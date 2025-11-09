# MOODI AI Engine v1.0.0 🎉

## Production-Ready Release

We're excited to announce the first production-ready release of **MOODI AI Engine** - an AI-powered mood journaling and micro-coaching platform designed for emotional wellness.

---

## 🌟 What's New

### Core Features

**AI-Powered Reflections**
Transform user moods into empathetic, actionable reflections in under 60 words. Powered by OpenAI's GPT-4.1-mini with structured JSON outputs.

**Multilingual Support**
- ✅ Arabic (Modern Standard)
- ✅ Moroccan Darija (Authentic dialect with Arabic script)
- ✅ French (Natural, conversational)
- ✅ English (Warm and supportive)

**Gamification System**
- Streak tracking for consecutive daily posts
- MoodCoins economy with automatic rewards
- Feature unlocks at milestone achievements
- Referral system with viral loop mechanics

**Safety & Security**
- Content moderation with OpenAI safety checks
- Automatic safety flag detection for at-risk users
- Row-level security in Supabase database
- Privacy-first design with no PII storage

---

## 📦 What's Included

### API Implementations
- **FastAPI Backend** (`fastapi_endpoint.py`) - Python REST API with auto-generated docs
- **Next.js API Route** (`nextjs_api_endpoint.ts`) - Serverless TypeScript implementation

### Core Components
- **Reflection Engine** (`moodi_reflection_api.py`) - Core AI mood processing
- **Integration Workflow** (`moodi_integration.py`) - Complete pipeline with gamification

### Database
- **Supabase Schema** (`supabase_schema.sql`) - 6 tables with automatic triggers
- Streak calculation automation
- Coin reward distribution
- Row-level security policies

### Documentation
- Comprehensive README with quick start guide
- API endpoint documentation
- Deployment instructions
- Test results and validation reports

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/HomameSoussi/moodi-ai-engine.git
cd moodi-ai-engine

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY="your_key_here"

# Run FastAPI server
uvicorn fastapi_endpoint:app --reload --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

---

## 📡 API Endpoints

### 1. POST `/api/reflection`
Generate empathetic mood reflections with actionable suggestions.

### 2. POST `/api/notification`
Create ultra-short push notification copy for mood reminders.

### 3. POST `/api/referral-caption`
Generate catchy social share captions for viral growth.

See the [README](https://github.com/HomameSoussi/moodi-ai-engine#-api-endpoints) for detailed endpoint documentation.

---

## 🧪 Test Results

**100% Test Pass Rate** ✅

- ✅ 8 tests run, 8 passed, 0 failed
- ✅ French responses: Natural and empathetic
- ✅ Moroccan Darija: Authentic dialect validated
- ✅ Streak calculation: Accurate (2→3 days, bonus triggered)
- ✅ Coin rewards: Correct (5 daily + 5 bonus = 10 total)
- ✅ Unlock triggered: Custom gradient at 55 coins
- ✅ All API endpoints functional
- ✅ Safety detection operational

See [TEST_RESULTS.md](https://github.com/HomameSoussi/moodi-ai-engine/blob/main/TEST_RESULTS.md) for detailed test reports.

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

## 🚢 Deployment

### Recommended Platforms

**Vercel** (Next.js)
```bash
vercel deploy
```

**Railway/Render** (FastAPI)
```bash
uvicorn fastapi_endpoint:app --host 0.0.0.0 --port $PORT
```

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

## 📊 Architecture

```
Client (Mobile) → API Layer → OpenAI GPT-4.1-mini → Supabase PostgreSQL
```

The system follows a clean, scalable architecture with clear separation of concerns:
- API layer handles requests and responses
- OpenAI processes mood data and generates reflections
- Supabase manages data persistence and triggers

---

## 🔐 Security Features

1. **Content Moderation** - OpenAI Moderation API integration
2. **Safety Classification** - Secondary risk detection
3. **Escalation Logic** - Automatic flagging for at-risk users
4. **Row-Level Security** - Supabase RLS policies
5. **No PII Storage** - Privacy-first design

Every reflection includes a `safety_flag`:
- `"ok"` - Normal mood, coaching provided
- `"elevate"` - Risk detected, suggests seeking help

---

## 📝 Known Issues

- OpenAI Moderation API currently returns 404 (fallback safety classifier is active and functional)

---

## 🗺️ Roadmap

### Planned Features
- Voice reflection generation
- Advanced analytics dashboard
- Mobile SDK for iOS and Android
- Real-time mood tracking
- Community features
- Advanced safety monitoring

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/HomameSoussi/moodi-ai-engine/blob/main/LICENSE) file for details.

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

## 🌟 Star the Project

If you find this project helpful, please consider giving it a ⭐️!

---

**Built with ❤️ for emotional wellness**

[View on GitHub](https://github.com/HomameSoussi/moodi-ai-engine) | [Documentation](https://github.com/HomameSoussi/moodi-ai-engine/blob/main/MOODI_IMPLEMENTATION_GUIDE.md) | [Test Results](https://github.com/HomameSoussi/moodi-ai-engine/blob/main/TEST_RESULTS.md)
