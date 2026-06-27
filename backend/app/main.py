from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi
import os
from dotenv import load_dotenv
from pathlib import Path

from app.api import auth, users, jobs, filters, applications, dashboard
from app.database.core import engine, Base

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Hunter API",
    description="AI-Powered Job Hunter Platform - Backend API",
    version="1.0.0"
)

def get_cors_origins():
    configured_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    development_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    return sorted(set(configured_origins + development_origins))


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(filters.router)
app.include_router(applications.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Job Hunter API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Job Hunter API",
        version="1.0.0",
        description="AI-Powered Job Hunter Platform - REST API",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENV", "development") == "development"
    )
