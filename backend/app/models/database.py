from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    JSON,
    Text,
    Boolean,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///D:/tech-interview-ai/backend/data/app.db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== MODELS ====================


class User(Base):
    """User model (optional for now, add later if needed)"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class InterviewSession(Base):
    """Stores interview session metadata"""

    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)  # Your custom session ID
    user_id = Column(Integer, nullable=True)  # FK to users (nullable for anonymous)

    # Interview details
    category = Column(String)  # "coding", "system_design", "behavioral"
    difficulty = Column(String, default="medium")

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Results
    total_questions = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)

    # Full conversation
    transcript = Column(JSON, nullable=True)  # List of messages

    # Status
    is_completed = Column(Boolean, default=False)


class QuestionResponse(Base):
    """Stores individual question responses"""

    __tablename__ = "question_responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True)  # FK to interview_sessions.id

    # Question details
    question_id = Column(String)  # e.g., "coding_001"
    question_text = Column(Text)
    question_number = Column(Integer)  # 1, 2, 3...

    # Answer details
    user_answer = Column(Text)

    # Evaluation
    evaluation = Column(Text)  # Full evaluation text
    score = Column(Integer)  # 0-100

    # Metadata
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class WeakArea(Base):
    """Tracks topics where user struggles"""

    __tablename__ = "weak_areas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)

    # Topic tracking
    category = Column(String)  # "coding", "system_design", etc.
    topic = Column(String)  # e.g., "linked lists", "rate limiting"

    # Statistics
    times_struggled = Column(Integer, default=1)
    average_score = Column(Float)
    last_seen = Column(DateTime, default=datetime.utcnow)


# ==================== CREATE TABLES ====================


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


# ==================== DEPENDENCY ====================


def get_db():
    """FastAPI dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Run this to create tables
if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
