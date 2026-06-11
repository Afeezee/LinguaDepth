# LinguaDepth 🌍

An adaptive English language learning platform for Nigerian university students.
Duolingo-inspired lessons, an ML proficiency classifier that directs the
curriculum, and an LLM tutor that grades written answers, validates spoken
answers, and powers a conversational practice chatbox.

## Architecture

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS v3 |
| Backend | Flask (Python 3.11) + SQLAlchemy |
| Database | SQLite (dev) — PostgreSQL-compatible schema |
| ML | scikit-learn Random Forest proficiency classifier |
| LLM | Groq API (`llama-4-scout-17b-16e-instruct`) |
| Speech | Browser Web Speech API (TTS + STT, Chrome/Edge) |
| Auth | JWT (24h expiry) |

The **ML engine** is the curriculum director: it extracts features from your
last 5 quiz sessions (average score, response time, error rate, score trend,
quiz count) and decides when to promote you between beginner, intermediate,
and advanced. The **LLM** is the tutor: it grades theory answers, validates
speech transcripts, and chats with you to practise conversation.

## Setup

Copy `.env.example` to `.env` and fill in your secrets (you need a
[Groq API key](https://console.groq.com) for question seeding and grading).

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed/seed_lessons.py     # seed the 35 lessons (creates the SQLite DB)
python seed/seed_questions.py   # generate + seed questions via LLM (needs GROQ_API_KEY)
flask run                       # runs on http://localhost:5000
```

No Groq key yet? Seed handwritten development questions instead:

```bash
python seed/seed_sample_questions.py   # objective questions only, no API needed
```

### Frontend

```bash
cd frontend
npm install
npm run dev                     # runs on http://localhost:5173
```

## Deploy on Railway

This repository is set up to deploy as a single Railway service:

- Railway installs Python dependencies from `backend/requirements.txt`
- Railway builds the React app in `frontend/`
- Flask serves the compiled frontend from `frontend/dist`
- Gunicorn binds to Railway's `$PORT`

Recommended Railway variables:

```bash
FLASK_ENV=production
SECRET_KEY=replace_me
JWT_SECRET_KEY=replace_me
GROQ_API_KEY=replace_me
DATABASE_URL=<Railway Postgres connection string>
```

Notes:

- Add a Railway Postgres service before first production run. SQLite on Railway is ephemeral.
- `CORS_ORIGINS` is only needed if you later split frontend and backend into separate services.
- After provisioning the database, seed lessons and starter questions against the production database.

### Train the ML model (after collecting pilot data)

```bash
cd backend
python ml/train.py
```

The classifier needs at least 10 users with 5+ completed sessions each.
Until `ml/model.pkl` exists, the classify endpoint safely returns
`{"should_promote": false, "reason": "model_not_trained"}`.

## How it works

1. **Register** → take a 10-question placement quiz → get assigned a level.
2. **Learn** → read short lessons (with text-to-speech), then take a
   5-question quiz mixing objective, theory, and oral questions.
3. **Get graded** → MCQs score instantly; written and spoken answers are
   graded by the LLM with one-line feedback.
4. **Practise speaking** → during oral questions, a speech chatbox holds a
   spoken conversation with you (STT in, TTS out).
5. **Level up** → after each quiz, the Random Forest classifier re-evaluates
   your proficiency. Promotion requires confidence > 0.75 and a positive
   score trend — celebrated with confetti. 🎉

## XP & Streaks

| Action | XP |
|---|---|
| Objective correct | +10 |
| Theory score ≥ 70 | +15 |
| Oral score ≥ 70 | +20 |
| Lesson completed | +50 |

Streaks increment on consecutive active days and reset after a missed day.

## Browser support

Speech recognition requires Chrome or Microsoft Edge. Other browsers get a
text-input fallback for oral questions and the chatbox.

## Admin

Grant admin access to an account:

```bash
cd backend
python seed/make_admin.py user@example.com           # grant
python seed/make_admin.py user@example.com --revoke  # revoke
```

Admins see a shield icon in the navbar linking to `/admin`, which provides:

- **Overview** — platform analytics: signups and quizzes per day (14 days),
  learner level distribution, hardest topics, activity stats.
- **Users** — search, change level, grant/revoke admin, delete accounts
  (self-demotion and self-deletion are blocked).
- **Export** — download any dataset as CSV: users, sessions, answers,
  questions, progress (`GET /api/admin/export/<dataset>`).

## API overview

```
POST /api/auth/register       POST /api/auth/login          GET  /api/auth/me
GET  /api/lessons/            GET  /api/lessons/:id         GET  /api/lessons/placement
POST /api/quiz/start          POST /api/quiz/answer         POST /api/quiz/complete
POST /api/quiz/placement/submit
GET  /api/dashboard/stats     GET  /api/dashboard/report
POST /api/ml/classify         POST /api/llm/chat
GET  /api/admin/users         PATCH/DELETE /api/admin/users/:id
GET  /api/admin/analytics     GET  /api/admin/export/:dataset
```

All protected routes need `Authorization: Bearer <token>`.
