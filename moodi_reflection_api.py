"""
MOODI Reflection Engine API
Core AI endpoint for mood reflection generation
"""

import json
import os
from openai import OpenAI

# Initialize OpenAI client (API key already configured in environment)
client = OpenAI()

# System prompt for the Mood Reflection Engine
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

# JSON Schema for response validation
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "reflection_text": {"type": "string", "maxLength": 360},
        "action_suggestion": {"type": "string", "maxLength": 120},
        "share_caption": {"type": "string", "maxLength": 90},
        "soundtrack_hint": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}, "minItems": 3, "maxItems": 6},
        "safety_flag": {"type": "string", "enum": ["ok", "elevate"]}
    },
    "required": ["reflection_text", "action_suggestion", "share_caption", "soundtrack_hint", "tags", "safety_flag"],
    "additionalProperties": False
}


def generate_mood_reflection(mood_payload: dict) -> dict:
    """
    Generate AI reflection for a given mood payload
    
    Args:
        mood_payload: Dictionary containing mood data with keys:
            - mood_emoji
            - mood_color
            - intensity_0_10
            - context_text (optional)
            - media_present
            - time_bucket
            - geo_hint
            - user_locale
            - user_age_bucket
    
    Returns:
        Dictionary with reflection_text, action_suggestion, share_caption, 
        soundtrack_hint, tags, and safety_flag
    """
    
    # Build user prompt with the mood payload
    user_prompt = f"""You will receive a mood payload:

{json.dumps(mood_payload, indent=2, ensure_ascii=False)}

Return a single JSON object that fits the schema."""
    
    try:
        # Call OpenAI API with structured output
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Parse the JSON response
        result = json.loads(response.choices[0].message.content)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error generating mood reflection: {str(e)}")


def validate_response(response: dict) -> tuple[bool, list]:
    """
    Validate response against schema requirements
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    required_fields = ["reflection_text", "action_suggestion", "share_caption", 
                      "soundtrack_hint", "tags", "safety_flag"]
    for field in required_fields:
        if field not in response:
            errors.append(f"Missing required field: {field}")
    
    # Validate field constraints
    if "reflection_text" in response and len(response["reflection_text"]) > 360:
        errors.append(f"reflection_text too long: {len(response['reflection_text'])} chars (max 360)")
    
    if "action_suggestion" in response and len(response["action_suggestion"]) > 120:
        errors.append(f"action_suggestion too long: {len(response['action_suggestion'])} chars (max 120)")
    
    if "share_caption" in response and len(response["share_caption"]) > 90:
        errors.append(f"share_caption too long: {len(response['share_caption'])} chars (max 90)")
    
    if "tags" in response:
        if not isinstance(response["tags"], list):
            errors.append("tags must be an array")
        elif len(response["tags"]) < 3 or len(response["tags"]) > 6:
            errors.append(f"tags must have 3-6 items, got {len(response['tags'])}")
    
    if "safety_flag" in response and response["safety_flag"] not in ["ok", "elevate"]:
        errors.append(f"safety_flag must be 'ok' or 'elevate', got '{response['safety_flag']}'")
    
    return (len(errors) == 0, errors)


if __name__ == "__main__":
    # Sample test payloads from the specification
    
    print("=" * 80)
    print("MOODI Reflection Engine - API Test")
    print("=" * 80)
    print()
    
    # Test 1: Calm, evening, French
    print("Test 1: Calm mood (French, evening)")
    print("-" * 80)
    
    test_payload_1 = {
        "mood_emoji": "😌",
        "mood_color": "#7FD1AE",
        "intensity_0_10": 4,
        "context_text": "petite promenade au bord de mer",
        "media_present": True,
        "time_bucket": "evening",
        "geo_hint": "Casablanca",
        "user_locale": "fr",
        "user_age_bucket": "adult"
    }
    
    print(f"Input: {json.dumps(test_payload_1, indent=2, ensure_ascii=False)}")
    print()
    
    result_1 = generate_mood_reflection(test_payload_1)
    print(f"Output: {json.dumps(result_1, indent=2, ensure_ascii=False)}")
    print()
    
    is_valid, errors = validate_response(result_1)
    print(f"Validation: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    print()
    
    # Test 2: Stressed, Darija
    print("=" * 80)
    print("Test 2: Stressed mood (Moroccan Darija, late-night)")
    print("-" * 80)
    
    test_payload_2 = {
        "mood_emoji": "😣",
        "mood_color": "#F08A5D",
        "intensity_0_10": 8,
        "context_text": "pressure dial lkhdma w deadlines",
        "media_present": False,
        "time_bucket": "late-night",
        "geo_hint": "Rabat",
        "user_locale": "ar-darija",
        "user_age_bucket": "young-adult"
    }
    
    print(f"Input: {json.dumps(test_payload_2, indent=2, ensure_ascii=False)}")
    print()
    
    result_2 = generate_mood_reflection(test_payload_2)
    print(f"Output: {json.dumps(result_2, indent=2, ensure_ascii=False)}")
    print()
    
    is_valid, errors = validate_response(result_2)
    print(f"Validation: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    print()
    
    print("=" * 80)
    print("Testing complete!")
    print("=" * 80)
