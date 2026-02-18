# AI Career Transition Planner

Intelligent career transition planning powered by a hybrid AI meta-model. Upload your resume, discover matching roles, and chart multi-step career paths with personalized learning roadmaps.

## Architecture

```
┌─────────────────────────────────────────────┐
│                 Frontend                     │
│         Next.js 15 + shadcn/ui              │
│  Resume Upload → Career Explorer → Roadmap  │
└──────────────────┬──────────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────────┐
│                 Backend                      │
│              FastAPI (Python)                │
│                                              │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  │
│  │ Resume  │  │ Skill    │  │ Meta-Model│  │
│  │ Parser  │  │Extractor │  │  Scorer   │  │
│  │(PyMuPDF)│  │ (SpaCy)  │  │ (Hybrid)  │  │
│  └────┬────┘  └────┬─────┘  └─────┬─────┘  │
│       │            │              │          │
│  ┌────▼────────────▼──────────────▼─────┐   │
│  │         AI Provider Layer            │   │
│  │  Gemini 2.5 Flash (search grounding) │   │
│  │  Groq Llama 3.3 70B (fast fallback)  │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │      sentence-transformers           │   │
│  │      (all-MiniLM-L6-v2)             │   │
│  └──────────────────────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│              Database                        │
│        SQLite (MVP) / PostgreSQL             │
│  Users · Resumes · Skills · Roles · Matches │
│  Career Transitions · Transition Paths       │
└─────────────────────────────────────────────┘
```

## Features

### Resume Parsing & Skill Extraction
- PDF upload and text paste support
- Two-layer NLP extraction: SpaCy entity ruler + regex patterns
- 150+ skill patterns across technical, framework, tool, soft, domain, and certification categories

### Meta-Model Hybrid Scoring
The core engine combines multiple AI signal layers:

```
meta_score = w1 × embedding_similarity
           + w2 × skill_overlap
           + w3 × experience_match
           + w4 × llm_assessment
           + w5 × market_demand
```

Weights adjust dynamically per career mode (Growth, Stability, Pivot, Late-Career).

### Career GPS
- Dijkstra-based pathfinding through a career graph of 185 roles and 169 transitions
- Multi-step paths with difficulty scoring and timeline estimates
- Supports vertical promotions, lateral moves, career pivots, and stretch roles

### Skill Gap & Learning Roadmap
- Gap analysis between user skills and target role requirements
- Priority-based learning milestones
- Optional Gemini search-grounded resource recommendations

### Late-Career Mode
- Adjusted meta-model weights prioritizing stability and existing expertise
- Filters out entry-level roles for experienced professionals
- Recommends advisory, consulting, and leadership tracks

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React 19, Tailwind v4, shadcn/ui |
| Backend | FastAPI, Python 3.12 |
| Database | SQLite (MVP), PostgreSQL-ready |
| AI Primary | Google Gemini 2.5 Flash (search grounding) |
| AI Fallback | Groq (Llama 3.3 70B) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| NLP | SpaCy |
| PDF Parsing | PyMuPDF |
| Deployment | Docker, Vercel + Render |

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) Gemini API key and/or Groq API key

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
python -m spacy download en_core_web_sm

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Seed the database
python -m app.data.seed

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Compute Embeddings

After seeding roles, compute embeddings for matching:

```bash
curl -X POST http://localhost:8000/api/v1/career/embeddings \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

### Docker

```bash
docker compose up --build
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/resume/upload` | Upload PDF resume |
| POST | `/api/v1/resume/parse-text` | Parse pasted text |
| GET | `/api/v1/resume/{id}/skills` | Get extracted skills |
| GET | `/api/v1/roles` | List roles (filterable) |
| GET | `/api/v1/roles/{id}/transitions` | Get role transitions |
| POST | `/api/v1/career/match` | Run meta-model matching |
| POST | `/api/v1/career/transition-paths` | Find career paths |
| POST | `/api/v1/career/roadmap` | Generate learning roadmap |
| POST | `/api/v1/career/embeddings` | Compute role embeddings |

## Career Graph

- **185 roles** across 12 categories with Philippine job market context
- **169 career transitions** covering vertical, lateral, pivot, and stretch moves
- Salary ranges calibrated for the PH market (PHP & USD)

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── ai/              # Gemini + Groq provider abstraction
│   │   ├── api/v1/          # FastAPI routes
│   │   ├── data/            # Seed data (roles, transitions, skills taxonomy)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   └── services/        # Business logic (parser, extractor, meta-model, etc.)
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # React components (career, resume, layout, ui)
│   │   ├── lib/             # API client, utilities
│   │   └── types/           # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## License

MIT
