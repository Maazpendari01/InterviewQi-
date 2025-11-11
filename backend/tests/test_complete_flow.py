from fastapi.testclient import TestClient
from main import app
from app.models.database import SessionLocal, InterviewSession, QuestionResponse
import time

client = TestClient(app)


def cleanup_test_data():
    """Clean up test data"""
    db = SessionLocal()
    db.query(QuestionResponse).filter(
        QuestionResponse.question_id.like("test_%")
    ).delete(synchronize_session=False)
    db.query(InterviewSession).filter(
        InterviewSession.session_id.like("test_%")
    ).delete(synchronize_session=False)
    db.commit()
    db.close()


def test_complete_interview_flow():
    """Test full interview flow with database"""

    print("\n🧪 Testing Complete Interview Flow\n")

    # Clean up first
    cleanup_test_data()

    # Test 1: Start interview
    print("1️⃣ Starting interview...")
    start_response = client.post(
        "/api/interview/start", json={"category": "coding", "difficulty": "medium"}
    )
    assert start_response.status_code == 200
    data = start_response.json()
    session_id = data["session_id"]
    print(f"✅ Started: {session_id}")
    print(f"   First question: {data['question'][:50]}...")

    # Test 2: Submit answers (3 times)
    answers = [
        "I would use a hash map for O(n) time complexity...",
        "Three pointers: previous, current, next. Iterate...",
        "Binary search divides the array in half each time...",
    ]

    for i, answer in enumerate(answers, 1):
        print(f"\n{i + 1}️⃣ Submitting answer {i}...")
        answer_response = client.post(
            "/api/interview/answer", json={"session_id": session_id, "answer": answer}
        )
        assert answer_response.status_code == 200
        result = answer_response.json()
        print(f"✅ Score: {result['score']}/100")
        print(f"   Continue: {result['continue']}")

        if result["continue"]:
            print(f"   Next question: {result.get('next_question', '')[:50]}...")

        time.sleep(0.5)  # Brief pause

    # Test 3: Get summary
    print(f"\n4️⃣ Getting summary...")
    summary_response = client.get(f"/api/interview/{session_id}/summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    print(f"✅ Summary:")
    print(f"   Category: {summary['category']}")
    print(f"   Questions: {summary['total_questions']}")
    print(f"   Avg Score: {summary['average_score']}/100")
    print(f"   Completed: {summary['is_completed']}")

    # Test 4: Analytics
    print(f"\n5️⃣ Testing analytics...")
    stats_response = client.get("/api/analytics/stats")
    assert stats_response.status_code == 200
    stats = stats_response.json()
    print(f"✅ Platform Stats:")
    print(f"   Total sessions: {stats['total_sessions']}")
    print(f"   Completed: {stats['completed_sessions']}")
    print(f"   Avg score: {stats['average_score']}")

    # Test 5: Weak areas
    print(f"\n6️⃣ Testing weak areas...")
    weak_response = client.get("/api/analytics/weak-areas?threshold=70")
    assert weak_response.status_code == 200
    weak = weak_response.json()
    print(f"✅ Weak Areas (threshold 70):")
    for category, data in weak.get("weak_areas", {}).items():
        print(f"   {category}: {data['count']} struggles, avg {data['avg_score']}")

    # Test 6: Recent sessions
    print(f"\n7️⃣ Testing recent sessions...")
    recent_response = client.get("/api/interview/sessions/recent?limit=5")
    assert recent_response.status_code == 200
    recent = recent_response.json()
    print(f"✅ Recent Sessions: {recent['total']}")

    # Clean up
    cleanup_test_data()

    print("\n🎉 All tests passed!\n")


if __name__ == "__main__":
    try:
        test_complete_interview_flow()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
