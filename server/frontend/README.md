# AI Camera Frontend (Vue 3 + Vite + TypeScript)

## Quickstart

```bash
cd frontend
npm install
cp .env.example .env # then edit API URL
npm run dev
```

## Environment

- `VITE_API_BASE_URL` — Backend API base URL (e.g., http://localhost:3000)

## Scripts

- `npm run dev` — Start dev server
- `npm run build` — Build for production
- `npm run preview` — Preview production build

## Structure

- `src/router` — Routes with auth guard
- `src/stores` — Pinia stores (JWT auth)
- `src/utils/api.ts` — Axios instance with token interceptor
- `src/views` — Basic views (Login, Dashboard)
