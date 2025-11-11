from fastapi import FastAPI, Depends  # ✅ Added Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session  # ✅ Added Session
from sqlalchemy import text

from backend.app.routers import interview, analytics
from backend.app.models.database import get_db

app = FastAPI(
    title="AI Interview Platform",
    description="AI-powered technical interview with Groq API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(interview.router)
app.include_router(analytics.router)  # Add this


@app.get("/")
async def root():
    return {"message": "AI Interview Platform API", "docs": "/docs"}


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """Health check including database"""
    health_status = {"api": "healthy", "database": "unknown"}

    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"

    # Overall status
    all_healthy = all(v == "healthy" for v in health_status.values())
    health_status["status"] = "healthy" if all_healthy else "degraded"

    return health_status
