from sqlalchemy.orm import Session
from backend.app.models.database import SessionLocal, InterviewSession, QuestionResponse
from backend.app.services.db_service import DatabaseService
from datetime import datetime
import uuid


def test_db_service():
    """Test database service operations"""
    db = SessionLocal()
    service = DatabaseService(db)

    # Generate unique session ID for this test run
    unique_session_id = f"test_service_{uuid.uuid4().hex[:8]}"
    print(f"Using session_id: {unique_session_id}")

    try:
        # Test 1: Create session
        print("\nTest 1: Create session...")
        session = service.create_session(
            session_id=unique_session_id,
            category="coding",
            difficulty="medium"
        )
        assert session.id is not None
        print(f"Created session ID: {session.id}")

        # Test 2: Save response
        print("\nTest 2: Save response...")
        response = service.save_response(
            session_db_id=session.id,
            question_id="coding_001",
            question_text="Reverse a linked list",
            question_number=1,
            user_answer="Use three pointers...",
            evaluation="Good answer! Score: 85/100",
            score=85,
            category="coding"
        )
        assert response.id is not None
        print(f"Saved response ID: {response.id}")

        # Test 3: Get session
        print("\nTest 3: Get session...")
        retrieved = service.get_session(unique_session_id)
        assert retrieved is not None
        assert retrieved.category == "coding"
        print(f"Retrieved session: {retrieved.session_id}")

        # Test 4: Complete session
        print("\nTest 4: Complete session...")
        completed = service.complete_session(
            unique_session_id,
            transcript=[{"role": "interviewer", "content": "Question"}]
        )
        assert completed.is_completed is True
        assert completed.average_score == 85
        print(f"Completed session, avg score: {completed.average_score}")

        # Test 5: Analytics
        print("\nTest 5: Analytics...")
        total = service.get_total_sessions()
        print(f"Total sessions: {total}")

        avg_score = service.get_average_score()
        print(f"Average score: {avg_score}")

        print("\nAll tests passed!")

    except Exception as e:
        print(f"\nTest failed: {e}")
        raise  # Re-raise to see full traceback
    finally:
        # === CRITICAL: Always clean up, even on failure ===
        try:
            print("\nCleaning up test data...")
            db.query(QuestionResponse).delete()
            db.query(InterviewSession).filter(
                InterviewSession.session_id.like("test_service_%")
            ).delete(synchronize_session=False)
            db.commit()
            print("Cleanup complete.")
        except Exception as cleanup_error:
            print(f"Cleanup failed: {cleanup_error}")
            db.rollback()
        finally:
            db.close()


if __name__ == "__main__":
    test_db_service()
