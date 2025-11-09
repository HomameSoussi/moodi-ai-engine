# MOODI Implementation Guide

## Complete AI-Powered Mood Journaling System

This guide provides everything you need to deploy the MOODI mood reflection engine with gamification, multilingual support, and safety features.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [API Endpoints](#api-endpoints)
5. [Database Setup](#database-setup)
6. [Gamification System](#gamification-system)
7. [Deployment Guide](#deployment-guide)
8. [Testing](#testing)
9. [Security & Safety](#security--safety)

---

## Overview

**MOODI** is an emotion-first micro-coaching platform that transforms user moods into empathetic reflections with actionable suggestions. The system supports:

- **Multilingual**: Arabic, Moroccan Darija, French, English
- **AI-Powered**: GPT-4.1-mini for natural, empathetic responses
- **Gamified**: MoodCoins, streaks, and unlockable features
- **Safe**: Built-in moderation and safety escalation
- **Scalable**: Ready for production deployment

---

## Architecture

```
┌─────────────┐
│   Client    │
│  (Mobile)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         API Layer                   │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  Reflection  │  │ Notification│ │
│  │   Endpoint   │  │  Generator  │ │
│  └──────┬───────┘  └──────┬──────┘ │
│         │                 │         │
│         ▼                 ▼         │
│  ┌──────────────────────────────┐  │
│  │   OpenAI GPT-4.1-mini        │  │
│  │   (Structured JSON Output)   │  │
│  └──────────────────────────────┘  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Supabase PostgreSQL            │
│  ┌────────┐  ┌──────────────────┐  │
│  │ Users  │  │ Moods & Reflect. │  │
│  └────────┘  └──────────────────┘  │
│  ┌────────┐  ┌──────────────────┐  │
│  │Referral│  │    Unlocks       │  │
│  └────────┘  └──────────────────┘  │
└─────────────────────────────────────┘
```

---

## Core Components

### 1. AI Reflection Engine (`moodi_reflection_api.py`)

The heart of MOODI - generates empathetic reflections from mood data.

**Key Features:**
- Max 60 words for reflection text
- Culturally appropriate responses
- Safety flag detection
- JSON schema validation

**Usage:**
```python
from moodi_reflection_api import generate_mood_reflection

payload = {
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

reflection = generate_mood_reflection(payload)
```

### 2. Integration Workflow (`moodi_integration.py`)

Complete end-to-end processing with gamification.

**Workflow Steps:**
1. Safety check (OpenAI Moderation)
2. AI reflection generation
3. Streak calculation
4. Coin rewards
5. Unlock checking

**Usage:**
```python
from moodi_integration import process_mood_submission

user_data = {
    "user_id": "uuid",
    "streak_days": 2,
    "moodcoins": 45,
    "last_mood_date": "2025-11-07",
    "locale": "fr"
}

result = process_mood_submission(mood_payload, user_data)
# Returns: reflection, coins_awarded, new_streak, unlocks, etc.
```

### 3. API Endpoints

Two implementations provided:

#### **FastAPI** (Python) - `fastapi_endpoint.py`
- Modern Python async framework
- Auto-generated OpenAPI docs
- Type-safe with Pydantic models

**Run:**
```bash
uvicorn fastapi_endpoint:app --reload --port 8000
```

**Docs:** http://localhost:8000/docs

#### **Next.js** (TypeScript) - `nextjs_api_endpoint.ts`
- Serverless-ready
- Vercel deployment optimized
- TypeScript type safety

**File location:** `/pages/api/moodi-reflection.ts`

---

## API Endpoints

### 1. POST `/api/reflection`

Generate AI reflection for a mood.

**Request:**
```json
{
  "mood_emoji": "😌",
  "mood_color": "#7FD1AE",
  "intensity_0_10": 4,
  "context_text": "petite promenade au bord de mer",
  "media_present": true,
  "time_bucket": "evening",
  "geo_hint": "Casablanca",
  "user_locale": "fr",
  "user_age_bucket": "adult"
}
```

**Response:**
```json
{
  "reflection_text": "Cette petite promenade au bord de la mer...",
  "action_suggestion": "Prends 3 grandes respirations profondes...",
  "share_caption": "Un moment de calme au bord de la mer.",
  "soundtrack_hint": "musique douce, ambient, nature",
  "tags": ["calme", "soirée", "mer", "promenade", "apaisement"],
  "safety_flag": "ok"
}
```

### 2. POST `/api/notification`

Generate push notification copy.

**Request:**
```json
{
  "user_locale": "fr",
  "theme": "streak_nudge",
  "days_streak": 5
}
```

**Response:**
```json
{
  "title": "Bravo pour ta série de 5 jours !",
  "body": "Continue à noter ton humeur, chaque jour compte."
}
```

### 3. POST `/api/referral-caption`

Generate social share caption.

**Request:**
```json
{
  "user_locale": "ar-darija",
  "mood_emoji": "😊",
  "benefit": "Track your mood, get a tiny AI nudge"
}
```

**Response:**
```json
{
  "caption": "تابع مزاجك وخلي AI يساعدك 😊"
}
```

---

## Database Setup

### Supabase Schema

Execute the SQL file `supabase_schema.sql` in your Supabase SQL Editor.

**Tables Created:**
- `users` - User profiles, streaks, coins
- `moods` - Mood entries
- `mood_reflections` - AI-generated reflections
- `referrals` - Viral loop tracking
- `user_unlocks` - Feature unlocks
- `notifications` - Push notification queue

**Automatic Triggers:**
- ✅ Streak calculation on mood insert
- ✅ Daily coin awards (5 coins)
- ✅ Streak bonus (5 coins every 3 days)
- ✅ Referral rewards (25 coins)

**Row Level Security (RLS):**
- ✅ Users can only access their own data
- ✅ Reflections tied to user's moods
- ✅ Secure by default

### Quick Setup

1. Create a Supabase project at https://supabase.com
2. Go to SQL Editor
3. Copy and paste `supabase_schema.sql`
4. Click "Run"
5. Done! ✨

---

## Gamification System

### MoodCoins Economy

| Action | Coins | Frequency |
|--------|-------|-----------|
| Daily mood post | +5 | Once per day |
| 3-day streak bonus | +5 | Every 3 days |
| Referral accepted | +25 | Per referral |

### Unlockable Features

| Feature | Cost | Description |
|---------|------|-------------|
| Custom Gradient | 50 coins | Personalized mood color themes |
| Voice Reflection | 120 coins | AI-generated voice responses |

### Streak Logic

- **Consecutive days**: Streak increments
- **Same day**: No change (one mood per day)
- **Missed day**: Streak resets to 1

**Implementation:**
```python
from moodi_integration import GamificationEngine

# Calculate streak
streak_change = GamificationEngine.calculate_streak(
    last_mood_date=date(2025, 11, 7),
    current_date=date(2025, 11, 8)
)

# Award coins
coins = GamificationEngine.award_daily_coins(user_data, is_new_day=True)
bonus = GamificationEngine.award_streak_bonus(new_streak=3, old_streak=2)

# Check unlocks
unlocks = GamificationEngine.check_unlocks(total_coins=55)
# Returns: ['custom_gradient']
```

---

## Deployment Guide

### Option 1: Vercel (Recommended for Next.js)

1. **Setup:**
   ```bash
   npm install openai
   ```

2. **Environment Variables:**
   ```env
   OPENAI_API_KEY=your_key_here
   ```

3. **Deploy:**
   ```bash
   vercel deploy
   ```

4. **API URL:**
   ```
   https://your-app.vercel.app/api/moodi-reflection
   ```

### Option 2: Railway/Render (FastAPI)

1. **Requirements:**
   ```txt
   fastapi
   uvicorn[standard]
   openai
   pydantic
   ```

2. **Start Command:**
   ```bash
   uvicorn fastapi_endpoint:app --host 0.0.0.0 --port $PORT
   ```

3. **Environment:**
   ```env
   OPENAI_API_KEY=your_key_here
   ```

### Option 3: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "fastapi_endpoint:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Testing

### Test Files Included

1. **`moodi_reflection_api.py`** - Run directly to test core reflection
2. **`moodi_integration.py`** - Run to test full workflow
3. **`fastapi_endpoint.py`** - Start server and use cURL/Postman

### Sample Test Cases

#### Test 1: French Calm Mood
```bash
curl -X POST http://localhost:8000/api/reflection \
  -H "Content-Type: application/json" \
  -d '{
    "mood_emoji":"😌",
    "mood_color":"#7FD1AE",
    "intensity_0_10":4,
    "context_text":"petite promenade au bord de mer",
    "media_present":true,
    "time_bucket":"evening",
    "geo_hint":"Casablanca",
    "user_locale":"fr",
    "user_age_bucket":"adult"
  }'
```

#### Test 2: Darija Stressed Mood
```bash
curl -X POST http://localhost:8000/api/reflection \
  -H "Content-Type: application/json" \
  -d '{
    "mood_emoji":"😣",
    "mood_color":"#F08A5D",
    "intensity_0_10":8,
    "context_text":"pressure dial lkhdma w deadlines",
    "media_present":false,
    "time_bucket":"late-night",
    "geo_hint":"Rabat",
    "user_locale":"ar-darija",
    "user_age_bucket":"young-adult"
  }'
```

### Expected Results

✅ **Validation passing**  
✅ **Correct language/dialect**  
✅ **Safety flag present**  
✅ **Character limits respected**  
✅ **3-6 tags returned**

---

## Security & Safety

### 1. Content Moderation

**OpenAI Moderation API** (optional, currently returns 404 but can be enabled):
```python
from moodi_integration import check_content_safety

result = check_content_safety("user text here")
if result["flagged"]:
    # Handle flagged content
```

### 2. Safety Classifier

Secondary check for self-harm detection:
```python
from moodi_integration import classify_safety_risk

flag = classify_safety_risk(context_text)
if flag == "elevate":
    # Escalate to human support
```

### 3. Safety Flag in Response

Every reflection includes `safety_flag`:
- `"ok"` - Normal mood, coaching provided
- `"elevate"` - Risk detected, action suggests seeking help

### 4. Row Level Security (RLS)

Supabase RLS policies ensure:
- Users only see their own data
- No cross-user data leakage
- Secure by default

### 5. Environment Variables

**Never commit:**
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

Use `.env` files and add to `.gitignore`.

---

## File Structure

```
moodi/
├── moodi_reflection_api.py       # Core AI reflection engine
├── moodi_integration.py          # Complete workflow + gamification
├── fastapi_endpoint.py           # FastAPI implementation
├── nextjs_api_endpoint.ts        # Next.js implementation
├── supabase_schema.sql           # Database schema + triggers
├── MOODI_IMPLEMENTATION_GUIDE.md # This file
└── requirements.txt              # Python dependencies
```

---

## Next Steps

1. ✅ **Deploy API** - Choose Vercel (Next.js) or Railway (FastAPI)
2. ✅ **Setup Supabase** - Run the SQL schema
3. ✅ **Configure Environment** - Add API keys
4. ✅ **Test Endpoints** - Use provided cURL commands
5. ✅ **Integrate Frontend** - Connect mobile app to API
6. ✅ **Monitor Safety** - Review safety_flag responses
7. ✅ **Scale** - Add caching, rate limiting as needed

---

## Support & Resources

- **OpenAI API Docs**: https://platform.openai.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js API Routes**: https://nextjs.org/docs/api-routes/introduction

---

## License

This implementation is provided as-is for the MOODI project. Customize and deploy as needed.

---

**Built with ❤️ for emotional wellness**
