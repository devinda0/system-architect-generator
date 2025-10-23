from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.health import router as healt_router
from app.api.user import router as user_router

app = FastAPI(
    title="System Architect Generator - API",
    version="0.1.0",
    description="Simple FastAPI app for the System Architect Generator project",
)

# Allow common CORS during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(healt_router, prefix="/api")
app.include_router(user_router, prefix="/api")

if __name__ == "__main__":
    # Run with: python main.py
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

