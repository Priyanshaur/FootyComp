"""
FootIQ FastAPI Application Entry Point.

Run locally:
    uvicorn main:app --reload

Production (Render):
    uvicorn main:app --host 0.0.0.0 --port $PORT
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import players, teams, compare, predict

app = FastAPI(
    title="FootIQ API",
    description="Football analytics API — player comparison, team fit scoring, and AI match prediction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend origins
allowed_origins = [
    os.environ.get("FRONTEND_URL", "http://localhost:5173"),
    "https://footiq.vercel.app",  # update with your actual Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(players.router)
app.include_router(teams.router)
app.include_router(compare.router)
app.include_router(predict.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"status": "online", "service": "FootIQ API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check — also verifies env vars are set."""
    checks = {
        "supabase_url_set": bool(os.environ.get("SUPABASE_URL")),
        "supabase_key_set": bool(os.environ.get("SUPABASE_KEY")),
        "anthropic_key_set": bool(os.environ.get("ANTHROPIC_API_KEY")),
    }
    all_ok = all(checks.values())
    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
    }
