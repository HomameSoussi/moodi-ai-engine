"""
MOODI Reflection API - Vercel Deployment
Main entrypoint for Vercel serverless functions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal
from openai import OpenAI
import json
import os

# Initialize FastAPI app
app = FastAPI(
    title="MOODI Reflection API",
    description="AI-powered mood reflection and micro-coaching",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt
SYSTEM_PROMPT = """You are **MOODI Reflection Engine**, an emotion-first micro-coach. 
Your job: transform a user's mood into a short, empathetic reflection + a tiny action.

Non-negotiables:
- **Max 60 words** for `reflection_text` (empathetic, human, specific to the mood, never generic).
- Give **one** tiny, doable suggestion in `action_suggestion` (max 20 words).
- Keep language and dialect = `user_locale` (support: ar, ar-darija, fr, en). If `user_locale` is `ar-darija`, reply in **Moroccan Darija** (Arabic script acceptable).
- Add a short `share_caption` users can post publicly (≤ 15 words, uplifting).
- For sound, give 1 `soundtrack_hint` (mood/genre; avoid trademarks where unsure).
- Add 3–6 `tags` capturing emotion nuance (e.g., ["calm","gratitude","evening","alone"]).
- **ALWAYS include `safety_flag`** in your response. Set it to "ok" for normal moods, or "elevate" if self-harm risk is detected.
- Output **valid JSON** matching the provided schema—no extra keys, no prose outside JSON.

Guardrails:
- No medical/clinical claims. If self-harm risk is present, set `safety_flag: "elevate"` and set `action_suggestion` to seeking help (culturally appropriate hotline/close person), no coaching beyond that.
- Never include PII. Never shame the user.
- If mood media is present, you may reference it generically (e.g., "in your photo", "in your voice note"); never describe people or private details.

Tone:
- Warm, brief, non-therapeutic. Use everyday language.

Required JSON fields: reflection_text, action_suggestion, share_caption, soundtrack_hint, tags, safety_flag"""


# ============================================================================
# Request/Response Models
# ============================================================================

class MoodPayload(BaseModel):
    """Mood submission payload"""
    mood_emoji: str = Field(..., description="Emoji representing the mood")
    mood_color: str = Field(..., description="Hex color code for the mood")
    intensity_0_10: int = Field(..., ge=0, le=10, description="Mood intensity from 0-10")
    context_text: Optional[str] = Field(None, description="Optional context or note")
    media_present: bool = Field(default=False, description="Whether media is attached")
    time_bucket: Literal["morning", "afternoon", "evening", "late-night"] = Field(..., description="Time of day")
    geo_hint: Optional[str] = Field(None, description="City or country hint")
    user_locale: Literal["ar", "ar-darija", "fr", "en"] = Field(..., description="User's language/locale")
    user_age_bucket: Literal["teen", "young-adult", "adult", "senior"] = Field(..., description="User's age group")


class ReflectionResponse(BaseModel):
    """AI-generated reflection response"""
    reflection_text: str = Field(..., max_length=360)
    action_suggestion: str = Field(..., max_length=120)
    share_caption: str = Field(..., max_length=90)
    soundtrack_hint: str
    tags: list[str] = Field(..., min_length=3, max_length=6)
    safety_flag: Literal["ok", "elevate"]


class NotificationRequest(BaseModel):
    """Notification generation request"""
    user_locale: Literal["ar", "ar-darija", "fr", "en"]
    theme: Literal["gentle_reminder", "streak_nudge", "evening_checkin", "milestone"]
    days_streak: int = Field(default=0, ge=0)


class NotificationResponse(BaseModel):
    """Notification copy response"""
    title: str = Field(..., max_length=80)
    body: str = Field(..., max_length=80)


class ReferralCaptionRequest(BaseModel):
    """Referral caption generation request"""
    user_locale: Literal["ar", "ar-darija", "fr", "en"]
    mood_emoji: str
    benefit: str = Field(default="Track your mood, get a tiny AI nudge")


class ReferralCaptionResponse(BaseModel):
    """Referral caption response"""
    caption: str = Field(..., max_length=72)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "MOODI Reflection API",
        "status": "healthy",
        "version": "1.0.0",
        "deployment": "Vercel"
    }


@app.post("/api/reflection", response_model=ReflectionResponse)
async def generate_reflection(payload: MoodPayload):
    """
    Generate AI reflection for a mood submission
    
    This is the primary endpoint that transforms user mood data into
    empathetic reflections with actionable suggestions.
    """
    try:
        # Build user prompt
        user_prompt = f"""You will receive a mood payload:

{payload.model_dump_json(indent=2)}

Return a single JSON object that fits the schema."""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Parse and return
        result = json.loads(response.choices[0].message.content)
        return ReflectionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notification", response_model=NotificationResponse)
async def generate_notification(request: NotificationRequest):
    """
    Generate push notification copy
    
    Creates ultra-short, empathetic notification text for mood reminders.
    """
    system_prompt = """You write ultra-short, empathetic push notifications and microcopies for mood journaling apps.
Rules: ≤ 80 characters, friendly, zero guilt. Match `user_locale`.
Output JSON: {"title": "...", "body": "..."} with both ≤ 80 chars."""
    
    user_prompt = f"""user_locale="{request.user_locale}"
theme="{request.theme}"
days_streak={request.days_streak}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        result = json.loads(response.choices[0].message.content)
        return NotificationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/referral-caption", response_model=ReferralCaptionResponse)
async def generate_referral_caption(request: ReferralCaptionRequest):
    """
    Generate social share caption for referrals
    
    Creates catchy, short captions for social media sharing.
    """
    system_prompt = """Write a catchy share caption for social. ≤ 12 words. Match locale.
Return JSON: {"caption":"..."} Only."""
    
    user_prompt = f"""user_locale="{request.user_locale}"
mood_emoji="{request.mood_emoji}"
benefit="{request.benefit}" """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.8,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        result = json.loads(response.choices[0].message.content)
        return ReferralCaptionResponse(caption=result.get("caption", "Check out MOODI!"))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
