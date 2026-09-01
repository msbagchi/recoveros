from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from backend.app.config import settings

from backend.app.api import (
    analytics,
    dashboard,
    opportunities,
    recovery_actions,
    recovery_trends,
    transactions,
)
from backend.app.api.recovery_operations import (
    router as recovery_operations_router,
)
from backend.app.api.merchants import (
    router as merchants_router,
)

app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-assisted revenue recovery "
        "platform for merchants."
    ),
    version="0.1.0",
)


# =========================================
# CORS
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://recoveros-tan.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# ROUTERS
# =========================================

app.include_router(
    dashboard.router
)

app.include_router(
    opportunities.router
)

app.include_router(
    transactions.router
)

app.include_router(
    analytics.router
)

app.include_router(
    recovery_trends.router
)

app.include_router(
    recovery_actions.router
)

app.include_router(
    recovery_operations_router
)
app.include_router(
    merchants_router
)

# =========================================
# ROOT
# =========================================

@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "message": (
            "Money shouldn't disappear silently."
        ),
        "version": "0.1.0",
    }


# =========================================
# HEALTH
# =========================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment":
            settings.app_env,
        "service":
            "recoveros-api",
    }