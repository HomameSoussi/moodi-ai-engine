# Vercel Deployment Guide for MOODI AI Engine

This guide will help you deploy the MOODI AI Engine to Vercel.

---

## 🚀 Quick Deploy

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/new
   - Sign in with your GitHub account

2. **Import Repository**
   - Click "Import Project"
   - Select `HomameSoussi/moodi-ai-engine` from your repositories
   - Click "Import"

3. **Configure Project**
   - **Framework Preset:** Select "Other" or "FastAPI"
   - **Root Directory:** Leave as `.` (root)
   - **Build Command:** Leave default (Vercel auto-detects)
   - **Output Directory:** Leave default

4. **Add Environment Variables**
   - Click "Environment Variables"
   - Add the following:
     ```
     Name: OPENAI_API_KEY
     Value: your_openai_api_key_here
     ```
   - Click "Add"

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (usually 1-2 minutes)
   - Your API will be live at `https://your-project-name.vercel.app`

---

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Navigate to project directory
cd moodi-ai-engine

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Select your account
# - Link to existing project? No
# - Project name? moodi-ai-engine (or your preferred name)
# - Directory? ./ (current directory)
# - Override settings? No

# Add environment variable
vercel env add OPENAI_API_KEY

# Deploy to production
vercel --prod
```

---

## 📡 API Endpoints

Once deployed, your API will be available at:

```
https://your-project-name.vercel.app
```

### Available Endpoints:

1. **Health Check**
   ```
   GET https://your-project-name.vercel.app/
   ```

2. **Generate Reflection**
   ```
   POST https://your-project-name.vercel.app/api/reflection
   ```

3. **Generate Notification**
   ```
   POST https://your-project-name.vercel.app/api/notification
   ```

4. **Generate Referral Caption**
   ```
   POST https://your-project-name.vercel.app/api/referral-caption
   ```

---

## 🧪 Testing Your Deployment

### Test Health Check

```bash
curl https://your-project-name.vercel.app/
```

**Expected Response:**
```json
{
  "service": "MOODI Reflection API",
  "status": "healthy",
  "version": "1.0.0",
  "deployment": "Vercel"
}
```

### Test Reflection Endpoint

```bash
curl -X POST https://your-project-name.vercel.app/api/reflection \
  -H "Content-Type: application/json" \
  -d '{
    "mood_emoji": "😌",
    "mood_color": "#7FD1AE",
    "intensity_0_10": 4,
    "context_text": "feeling calm and peaceful",
    "media_present": false,
    "time_bucket": "evening",
    "geo_hint": "New York",
    "user_locale": "en",
    "user_age_bucket": "adult"
  }'
```

**Expected Response:**
```json
{
  "reflection_text": "This calm evening moment is precious...",
  "action_suggestion": "Take three deep breaths...",
  "share_caption": "Finding peace in the evening calm.",
  "soundtrack_hint": "ambient, soft piano",
  "tags": ["calm", "evening", "peaceful", "relaxation"],
  "safety_flag": "ok"
}
```

---

## 🔧 Configuration Files

### `vercel.json`
Configures how Vercel builds and routes your application:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/main.py"
    }
  ]
}
```

### `api/main.py`
The main FastAPI application entrypoint that Vercel recognizes.

---

## 🌍 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-proj-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | None |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | None |

---

## 🔒 Security Best Practices

1. **Never commit API keys** - Use Vercel environment variables
2. **Use production keys** - Separate keys for dev/prod
3. **Enable CORS properly** - Configure allowed origins in production
4. **Monitor usage** - Set up OpenAI usage alerts
5. **Rate limiting** - Consider adding rate limiting middleware

---

## 📊 Monitoring & Logs

### View Deployment Logs

1. Go to Vercel Dashboard
2. Select your project
3. Click on "Deployments"
4. Click on a deployment to view logs

### View Runtime Logs

1. Go to your project in Vercel Dashboard
2. Click on "Logs" tab
3. View real-time function execution logs

---

## 🐛 Troubleshooting

### Issue: "No fastapi entrypoint found"

**Solution:** Make sure `api/main.py` exists and contains the FastAPI `app` instance.

### Issue: "Module not found"

**Solution:** Ensure all dependencies are listed in `requirements.txt`.

### Issue: "OpenAI API key not found"

**Solution:** 
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add `OPENAI_API_KEY` with your API key
3. Redeploy the project

### Issue: "Function timeout"

**Solution:** 
- Vercel has a 10-second timeout for Hobby plan, 60 seconds for Pro
- Consider upgrading if needed
- Optimize API calls

---

## 🔄 Continuous Deployment

Vercel automatically deploys when you push to GitHub:

1. **Push to main branch** → Production deployment
2. **Push to other branches** → Preview deployment
3. **Pull requests** → Automatic preview deployments

---

## 📈 Scaling

### Hobby Plan (Free)
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Serverless functions
- ⚠️ 10-second function timeout

### Pro Plan ($20/month)
- ✅ Everything in Hobby
- ✅ 1 TB bandwidth/month
- ✅ 60-second function timeout
- ✅ Advanced analytics
- ✅ Team collaboration

---

## 🔗 Useful Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Vercel Docs:** https://vercel.com/docs
- **FastAPI on Vercel:** https://vercel.com/docs/frameworks/backend/fastapi
- **Environment Variables:** https://vercel.com/docs/projects/environment-variables

---

## ✅ Deployment Checklist

- [ ] Repository synced to Vercel
- [ ] `OPENAI_API_KEY` environment variable added
- [ ] Deployment successful
- [ ] Health check endpoint working
- [ ] Reflection endpoint tested
- [ ] API documentation accessible
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up

---

## 🎉 Success!

Your MOODI AI Engine is now deployed on Vercel and ready to serve requests globally!

**Next Steps:**
1. Test all endpoints
2. Integrate with your mobile app
3. Set up monitoring and alerts
4. Configure custom domain (optional)

---

**Need Help?**
- Check Vercel documentation
- Open an issue on GitHub
- Contact Vercel support

---

**Built with ❤️ for emotional wellness**
