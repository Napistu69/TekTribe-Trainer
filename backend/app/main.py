"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.eggs import router as eggs_router
from app.api.companions import router as companions_router
from app.api.care import router as care_router

app = FastAPI(
    title="TekTribe Trainer API",
    description="Backend API for the TekTribe Trainer PWA",
    version="0.1.0",
)

# CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api")
app.include_router(eggs_router, prefix="/api")
app.include_router(companions_router, prefix="/api")
app.include_router(care_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
