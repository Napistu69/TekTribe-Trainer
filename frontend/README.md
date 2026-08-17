# TekTribe Trainer — Frontend

React 18 + Vite + TypeScript PWA for the TekTribe Trainer game.

## Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_CLIENT_ID` | Immutable Passport Client ID from Hub |
| `VITE_API_URL` | Backend FastAPI URL (default: http://localhost:8000) |

## Scripts

- `npm run dev` — Start Vite dev server (port 5173)
- `npm run build` — TypeScript check + production build
- `npm run preview` — Preview production build
- `npm run lint` — ESLint check
- `npm run test` — Jest unit tests
