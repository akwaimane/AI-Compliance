import os


def cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def frontend_dir() -> str | None:
    """Directory of the static frontend export, served at the site root if set."""
    path = os.environ.get("FRONTEND_DIR")
    return path if path and os.path.isdir(path) else None
