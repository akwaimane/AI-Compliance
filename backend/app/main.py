from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.diagnostic import router as diagnostic_router
from .config import cors_origins, frontend_dir

app = FastAPI(
    title="AI Compliance & ISO 42001 Management Platform",
    version="0.1.0",
    description="Plateforme intégrée de conformité IA : AI Act & ISO/IEC 42001 (SMIA).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    expose_headers=["Content-Disposition"],
)

app.include_router(diagnostic_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# Mounted last so the API routes above take precedence.
if (static_dir := frontend_dir()) is not None:
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
