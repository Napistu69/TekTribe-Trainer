# TekTribe Trainer

**Bond with the Past, Explore the Future.**

A browser-based Progressive Web App (PWA) that fuses virtual pet companionship, expedition-based exploration, deep breeding mechanics, and a sealed Web3 economy into a single living experience.

## Architecture

```
TekTribe-Trainer/
├── frontend/          React 18 + Vite + TypeScript PWA
├── backend/           Python 3.11 + FastAPI
└── shared/            Shared types and schemas
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Backend

```bash
cd backend
uv venv --python 3.11 .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Documentation

- [System Architecture v2.0](../TekTribe%20Trainer%20%E2%80%94%20System%20Architecture%20(v2.0))
- [Task Decomposition — Phase 1 MVP](../Hermes%20Task%20Decomposition%20%E2%80%94%20Phase%201%20MVP.md)

## License

All rights reserved.
