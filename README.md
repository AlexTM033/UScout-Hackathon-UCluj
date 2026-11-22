# U-Scout AI — Football Scouting Platform

AI-powered football scouting dashboard built for **Universitatea Cluj**. Analyzes player performance from match data, generates tactical reports, and provides intelligent player search powered by Gemini AI.

## Features

- **P90 Normalized Scoring** — Position-specific performance ratings (0–100)
- **AI Scouting Assistant** — Natural language player queries via Gemini
- **Tactical DNA Analysis** — Evaluate player fit against club playing style
- **Integration Reports** — AI-driven accommodation & personality assessments
- **Transfermarkt Data** — Market values, images, and transfer history from local CSV datasets
- **Smart Search** — Diacritics-aware name matching with position, age, and price filters

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, SQLAlchemy, SQLite |
| Frontend | HTML, CSS, JavaScript (vanilla) |
| AI | Google Gemini API |
| Data | Transfermarkt CSV datasets, SofaScore match JSONs |

## Setup

### 1. Clone & Install

```bash
git clone <repo-url>
cd Hack1
pip install -r requirements.txt
```

### 2. Environment Variables

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey)) |
| `API_KEY` | Backend API authentication key (any secure string) |

### 3. Data Setup

This project requires two data directories (not included in the repo due to size):

- **`transfermarkt-datasets/`** — CSV files from [Transfermarkt Datasets](https://github.com/dcaribou/transfermarkt-datasets): `players.csv`, `player_valuations.csv`, `clubs.csv`, `appearances.csv`, etc.
- **`Date - meciuri/`** — Match-level player stats JSON files from SofaScore

### 4. Run

```bash
# Ingest data into SQLite (first run only)
# The server handles this automatically on startup

# Start the server
uvicorn main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000) to access the dashboard.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (no auth) |
| `POST` | `/api/v1/auth/login` | Admin login |
| `GET` | `/api/v1/scout/search` | Search & filter players |
| `GET` | `/api/v1/players/{id}` | Player details |
| `GET` | `/api/v1/players/{id}/stats` | Player statistics & radar |
| `GET` | `/api/v1/players/{id}/transfermarkt` | Transfermarkt data |
| `GET` | `/api/v1/players/{id}/tactical-dna` | Tactical DNA analysis |
| `GET` | `/api/v1/players/{id}/integration-report` | Integration report |
| `POST` | `/api/v1/scout/ai-search` | AI-powered natural language search |
| `POST` | `/api/v1/scout/assistant` | Scouting assistant chat |

All endpoints (except `/health` and `/api/v1/auth/login`) require `X-API-Key` header.

## Project Structure

```
├── main.py              # FastAPI app & routes
├── ai_engine.py         # Gemini AI integration (reports, tactical DNA)
├── nlp_scout.py         # Natural language scouting search
├── scoring.py           # Position-specific P90 scoring engine
├── ingestion.py         # Data ingestion & normalization pipeline
├── csv_lookup.py        # Transfermarkt CSV matcher (diacritics-aware)
├── database.py          # SQLAlchemy models & DB setup
├── models.py            # Pydantic response schemas
├── security.py          # API key authentication
├── scraper.py           # Market value scraper (legacy)
├── requirements.txt     # Python dependencies
└── main-frontend/       # Static frontend
    ├── index.html
    ├── app.js
    ├── style.css
    └── assets/
```

## License

Built for the U Cluj Hackathon 2026.
