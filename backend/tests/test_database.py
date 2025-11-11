from app.models.database import SessionLocal, InterviewSession, QuestionResponse
from datetime import datetime

def test_database_connection():
    """Test database is working"""
    db = SessionLocal()

    try:
        # Create test session
        test_session = InterviewSession(
            session_id="test_123",
            category="coding",
            difficulty="easy"
        )
        db.add(test_session)
        db.commit()
        db.refresh(test_session)

        print(f"✅ Created session with ID: {test_session.id}")

        # Query it back
        retrieved = db.query(InterviewSession).filter(
            InterviewSession.session_id == "test_123"
        ).first()

        assert retrieved is not None
        assert retrieved.category == "coding"
        print(f"✅ Retrieved session: {retrieved.session_id}")

        # Clean up
        db.delete(retrieved)
        db.commit()
        print("✅ Database test passed!")

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_database_connection()
