"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.eggs import router as eggs_router
from app.api.companions import router as companions_router
from app.api.care import router as care_router
from app.api.training import router as training_router
from app.api.expeditions import router as expeditions_router
from app.api.expedition_actions import router as expedition_actions_router
from app.api.economy import router as economy_router
from app.api.admin import router as admin_router
from app.api.dialogue import router as dialogue_router
from app.api.lockdown import router as lockdown_router

app = FastAPI(
    title="TekTribe Trainer API",
    description="Backend API for the TekTribe Trainer PWA",
    version="0.1.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://napisnest.com",
        "https://www.napisnest.com",
        "https://tektribe-trainer.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler to ensure CORS headers on error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("Origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        },
    )


@app.get("/")
async def root():
    return {"message": "TekTribe Trainer API", "docs": "/docs"}

# Routers
app.include_router(auth_router, prefix="/api")
app.include_router(eggs_router, prefix="/api")
app.include_router(companions_router, prefix="/api")
app.include_router(care_router, prefix="/api")
app.include_router(training_router, prefix="/api")
app.include_router(expeditions_router, prefix="/api")
app.include_router(expedition_actions_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(economy_router, prefix="/api")
app.include_router(dialogue_router, prefix="/api")
app.include_router(lockdown_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check with Redis connectivity test."""
    redis_status = "ok"
    try:
        from app.core.config import settings
        import redis.asyncio as redis
        r = redis.from_url(settings.redis_url, decode_responses=True)
        await r.ping()
        await r.close()
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    return {"status": "ok", "version": "0.1.0", "redis": redis_status}
