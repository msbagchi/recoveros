import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from backend.app.config import settings
from backend.app.db.init_db import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield

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
from backend.app.api.promises import (
    router as promises_router,
)
from backend.app.api.batch_recovery import (
    router as batch_recovery_router,
)
from backend.app.api.escalations import (
    router as escalations_router,
)
from backend.app.api.checkout_abandonment import (
    router as checkout_abandonment_router,
)
from backend.app.api.subscription_recovery import (
    router as subscription_recovery_router,
)
from backend.app.api.mandate_retry import (
    router as mandate_retry_router,
)
from backend.app.api.b2b_receivables import (
    router as b2b_receivables_router,
)

app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-assisted revenue recovery "
        "platform for merchants."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# =========================================
# CORS
# =========================================

_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,https://recoveros-tan.vercel.app",
)
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
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
app.include_router(
    promises_router
)
app.include_router(
    batch_recovery_router
)
app.include_router(
    escalations_router
)
app.include_router(
    checkout_abandonment_router
)
app.include_router(
    subscription_recovery_router
)
app.include_router(
    mandate_retry_router
)
app.include_router(
    b2b_receivables_router
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