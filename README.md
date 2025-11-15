# FluentWork Backend - MVP Deployment Guide

FastAPI backend for FluentWork - English speaking practice app for workplace 1:1 conversations.

## Quick Deploy to Railway

### Prerequisites
- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))
- OpenAI API key

### Deployment Steps

#### 1. Push to GitHub

```bash
cd fluentwork
git init
git add .
git commit -m "Initial commit - FluentWork MVP"
gh repo create fluentwork-backend --public --source=. --push
```

Or manually:
- Create new repo on GitHub
- Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/fluentwork-backend.git
git branch -M main
git push -u origin main
```

#### 2. Deploy to Railway

**Option A: Railway CLI (Fastest)**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set OPENAI_API_KEY=your_api_key_here
railway variables set MAX_SESSION_DURATION=300
railway variables set DEFAULT_COMPLEXITY=easy

# Deploy
railway up
```

**Option B: Railway Dashboard (Easiest)**
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `fluentwork-backend` repository
4. Railway auto-detects Python and deploys
5. Add environment variables:
   - Go to Variables tab
   - Add `OPENAI_API_KEY`
   - Add `MAX_SESSION_DURATION=300`
   - Add `DEFAULT_COMPLEXITY=easy`
6. Click "Deploy"

#### 3. Get Your API URL

After deployment completes:
- Railway provides a URL like: `https://fluentwork-backend-production.up.railway.app`
- Test it: Visit `https://YOUR_URL.railway.app/` (should see API info)
- API docs: `https://YOUR_URL.railway.app/docs`

#### 4. Connect Frontend

Update your frontend to use the Railway URL:
```javascript
const API_URL = "https://YOUR_URL.railway.app"
```

## Local Development

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run Locally
```bash
python main.py
# Or
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for API documentation.

### Test Without API Costs

In `main.py`, set:
```python
USE_MOCK_MODE = True  # Line 37
```

This uses hardcoded responses instead of OpenAI API.

## API Endpoints

- `POST /start-session` - Start practice session
- `POST /speech-to-text` - Convert audio to text
- `POST /get-manager-response` - Get AI response
- `POST /get-feedback` - Get session feedback
- `GET /user-progress` - View user stats
- `GET /` - Health check
- `GET /docs` - Interactive API docs

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `MAX_SESSION_DURATION` | Max session length (seconds) | 300 |
| `DEFAULT_COMPLEXITY` | Starting difficulty level | easy |

## Features

- 14 workplace scenarios (easy → medium → hard)
- Progressive difficulty based on sessions
- GPT-4 conversation management
- Whisper speech-to-text
- Performance feedback with ONE improvement tip
- Helpful phrases for CELTA-aligned learning
- In-memory storage (last 100 sessions)

## Architecture

```
fluentwork/
├── main.py                 # FastAPI app & endpoints
├── models.py              # Pydantic models
├── scenarios.py           # 14 workplace scenarios
├── conversation_engine.py # GPT-4 conversation logic
├── speech_handler.py      # Whisper integration
├── feedback_analyzer.py   # Performance analysis
├── requirements.txt       # Dependencies
├── railway.json          # Railway config
├── Procfile              # Process config
└── .env.example          # Environment template
```

## Monitoring

Railway provides:
- Real-time logs
- Resource usage metrics
- Deployment history
- Custom domains (optional)

## Troubleshooting

**Deployment fails:**
- Check Railway logs for errors
- Verify `requirements.txt` has all dependencies
- Ensure environment variables are set

**API errors:**
- Check `OPENAI_API_KEY` is valid
- Verify you have OpenAI API credits
- Check Railway logs for detailed errors

**Slow responses:**
- GPT-4 can take 2-5 seconds
- Whisper API takes 1-3 seconds
- Consider upgrading Railway plan for better performance

## Cost Estimates

**Railway (Free Tier):**
- $5 credit/month
- Enough for MVP testing (~500-1000 requests)

**OpenAI API:**
- Whisper: ~$0.006/minute of audio
- GPT-4: ~$0.03/conversation (estimate)
- 100 practice sessions ≈ $3-5

## Next Steps

1. Deploy backend to Railway
2. Connect frontend to Railway URL
3. Test end-to-end flow
4. Share with first users
5. Monitor Railway logs for errors

## Support

- Railway docs: [docs.railway.app](https://docs.railway.app)
- OpenAI docs: [platform.openai.com/docs](https://platform.openai.com/docs)
- Issues: Create GitHub issue

---

Built with FastAPI + OpenAI GPT-4 + Whisper
