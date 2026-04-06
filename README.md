# VinAI Lab Work Day 03: Calendar Booking Agent

## Preview

![UI Preview](report/preview/lab03-preview.png)

## Demo

[Demo video](https://drive.google.com/file/d/1thNdLr3Nf3GpkkeTPhZpbuhMGTpZXYc6/view?usp=sharing)

## Requirements

- Python 3.10+
- Node.js 18+
- Google Calendar OAuth token in `src/backend/token.json`

## Run Locally

### 1) Backend (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.backend.main:app --reload --port 8000
```

### 2) Frontend (Vite + React)

```bash
cd /Users/pdpa/Desktop/VinAI/VinAI-day03-calendar-booking-agent/src/frontend/calendar-invitation-bot-minimal
npm install
npm run dev
```

Then open the Vite URL shown in the terminal (usually `http://localhost:5173`).

## Notes

- The frontend calls `/api/chat` and proxies to the backend on port `8000`.
- If you change the backend port, update `src/frontend/calendar-invitation-bot-minimal/vite.config.js`.
