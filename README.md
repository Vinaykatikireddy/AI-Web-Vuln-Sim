---
title: ai-web-vuln-sim
emoji: 🐠
colorFrom: yellow
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# AI-Powered Web Application Attack Simulation Platform

A full-stack educational cyber range that allows users to safely launch simulated attacks against intentionally vulnerable web applications.

## Project Structure

```
project/
├── backend/           # FastAPI Python backend (app/, templates/, pyproject.toml)
│   └── app/
│       ├── api/       # Routers: attack, auth, dashboard, lab, payload, report
│       ├── models/    # SQLAlchemy models
│       ├── schemas/   # Pydantic schemas
│       ├── core/      # Security, rate limiting
│       ├── services/  # Attack engine, lab manager, AI service, report generator
│       └── templates/reports/  # Jinja2 report templates
├── frontend/          # React/Vite/TypeScript frontend
├── labs/              # Vulnerable application containers (blog, ecommerce, file-upload, login)
├── docs/              # Documentation
├── scripts/           # DB seeding utilities
├── docker-compose.yml
├── Dockerfile         # Backend image (Hugging Face Spaces compatible)
└── supervisord.conf
```

## Getting Started

### Backend

1. Install Docker and Python 3.10+
2. Set environment variables:
   ```bash
   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   export DATABASE_URL=sqlite:///./app.db  # or a PostgreSQL URL
   ```
3. Run the backend:
   ```bash
   cd backend && pip install -r requirements.txt && uvicorn app.main:app --port 7860
   ```
   Or via Docker: `docker compose up --build` (backend on port 7860)

### Frontend

```bash
cd frontend && npm install && npm run dev
```

The frontend is also deployable to Vercel (`vercel.json` routes `/api/*` to the backend).

## Security Note

This platform is designed for educational purposes only. All attacks execute against isolated, intentionally vulnerable environments. Never use this platform to attack third-party systems.