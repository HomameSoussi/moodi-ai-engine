# 🌟 MOODI AI Engine

> **AI-Powered Mood Journaling & Micro-Coaching Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4.1--mini-412991.svg)](https://openai.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

**MOODI** transforms user moods into empathetic reflections with actionable micro-coaching suggestions. Built with AI, gamification, and multilingual support for emotional wellness.

---

## ✨ Features

### 🤖 AI-Powered Reflections
- **Empathetic responses** in under 60 words
- **Actionable suggestions** for immediate mood improvement
- **Safety detection** with automatic escalation for at-risk users
- **Structured JSON output** for seamless integration

### 🌍 Multilingual Support
- **Arabic** (Modern Standard)
- **Moroccan Darija** (Authentic dialect with Arabic script)
- **French** (Natural, conversational)
- **English** (Warm and supportive)

### 🎮 Gamification System
- **Streak tracking** for consecutive daily posts
- **MoodCoins economy** with rewards and unlocks
- **Feature unlocks** at milestone achievements
- **Referral system** with viral loop mechanics

### 🔒 Safety & Security
- **Content moderation** with OpenAI safety checks
- **Safety flag detection** for self-harm risk
- **Row-level security** in Supabase database
- **Privacy-first** design with no PII storage

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Supabase account (for database)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/moodi-ai-engine.git
cd moodi-ai-engine

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your_openai_api_key_here"
```

### Run FastAPI Server

```bash
uvicorn fastapi_endpoint:app --reload --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

---

## 📡 API Endpoints

### 1. Generate Mood Reflection

**POST** `/api/reflection`

Transform a user's mood into an empathetic reflection with actionable suggestions.

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

### 2. Generate Notification

**POST** `/api/notification`

Create ultra-short push notification copy for mood reminders.

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

### 3. Generate Referral Caption

**POST** `/api/referral-caption`

Generate catchy social share captions for viral growth.

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

## 🗄️ Database Setup

### Supabase Schema

Execute `supabase_schema.sql` in your Supabase SQL Editor to create:

**Tables:**
- `users` - User profiles, streaks, and MoodCoins
- `moods` - Individual mood entries
- `mood_reflections` - AI-generated reflections
- `referrals` - Viral loop tracking
- `user_unlocks` - Feature unlock status
- `notifications` - Push notification queue

**Automatic Features:**
- ✅ Streak calculation triggers
- ✅ Coin reward automation
- ✅ Row-level security policies
- ✅ Referral reward system

---

## 🎮 Gamification Logic

### MoodCoins Economy

| Action | Reward | Frequency |
|--------|--------|-----------|
| Daily mood post | +5 coins | Once per day |
| 3-day streak bonus | +5 coins | Every 3 days |
| Referral accepted | +25 coins | Per referral |

### Feature Unlocks

| Feature | Cost | Description |
|---------|------|-------------|
| Custom Gradient | 50 coins | Personalized mood color themes |
| Voice Reflection | 120 coins | AI-generated voice responses |

---

## 🏗️ Architecture

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
└─────────────────────────────────────┘
```

---

## 📦 Project Structure

```
moodi-ai-engine/
├── moodi_reflection_api.py       # Core AI reflection engine
├── moodi_integration.py          # Complete workflow + gamification
├── fastapi_endpoint.py           # FastAPI REST API
├── nextjs_api_endpoint.ts        # Next.js API route (TypeScript)
├── supabase_schema.sql           # Database schema + triggers
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── LICENSE                       # MIT License
```

---

## 🧪 Testing

### Run Core Tests

```bash
# Test core reflection engine
python moodi_reflection_api.py

# Test complete integration workflow
python moodi_integration.py
```

### Test API Endpoints

```bash
# Start server
uvicorn fastapi_endpoint:app --reload

# Test reflection endpoint
curl -X POST http://localhost:8000/api/reflection \
  -H "Content-Type: application/json" \
  -d '{"mood_emoji":"😌","mood_color":"#7FD1AE","intensity_0_10":4,"context_text":"feeling calm","media_present":false,"time_bucket":"evening","user_locale":"en","user_age_bucket":"adult"}'
```

**Expected Result:** JSON response with reflection, action, caption, tags, and safety flag.

---

## 🚢 Deployment

### Option 1: Vercel (Next.js)

```bash
# Install dependencies
npm install openai

# Deploy
vercel deploy
```

### Option 2: Railway/Render (FastAPI)

```bash
# Start command
uvicorn fastapi_endpoint:app --host 0.0.0.0 --port $PORT
```

### Environment Variables

```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

## 📊 Test Results

**100% Test Pass Rate** ✅

- ✅ French responses: Natural and empathetic
- ✅ Moroccan Darija: Authentic dialect
- ✅ Streak calculation: Accurate
- ✅ Coin rewards: Correct
- ✅ Safety detection: Working
- ✅ API endpoints: All functional

See [TEST_RESULTS.md](./TEST_RESULTS.md) for detailed test reports.

---

## 🔐 Security

### Safety Features

1. **Content Moderation** - OpenAI Moderation API integration
2. **Safety Classification** - Secondary risk detection
3. **Escalation Logic** - Automatic flagging for at-risk users
4. **Row-Level Security** - Supabase RLS policies
5. **No PII Storage** - Privacy-first design

### Safety Flag Response

Every reflection includes a `safety_flag`:
- `"ok"` - Normal mood, coaching provided
- `"elevate"` - Risk detected, suggests seeking help

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-4.1-mini API
- **Supabase** for database and authentication
- **FastAPI** for the Python web framework
- **Next.js** for serverless API routes

---

## 📞 Support

For questions or support, please open an issue on GitHub.

---

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐️!

---

**Built with ❤️ for emotional wellness**
