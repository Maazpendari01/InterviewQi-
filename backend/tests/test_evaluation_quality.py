import pytest
from backend.app.services.evaluator import StructuredEvaluator
from backend.app.services.knowledge_base import InterviewKnowledgeBase


@pytest.fixture
def evaluator():
    return StructuredEvaluator()


@pytest.fixture
def knowledge_base():
    return InterviewKnowledgeBase()


def test_good_vs_bad_answer(evaluator, knowledge_base):
    """Good answers should score significantly higher than bad ones"""

    question = "Design a function to reverse a linked list."

    # Get expert context
    results = knowledge_base.search(question, category="coding", k=2)
    expert_context = "\n".join([r.page_content for r in results])

    # Good answer
    good_answer = """
    I would use an iterative approach with three pointers: previous, current, and next.

    Algorithm:
    1. Initialize prev = None, curr = head
    2. While curr is not None:
       - Save next node: next = curr.next
       - Reverse the link: curr.next = prev
       - Move forward: prev = curr, curr = next
    3. Return prev as new head

    Time complexity: O(n) - single pass through list
    Space complexity: O(1) - only using three pointers

    Edge cases: Empty list returns None, single node returns itself.
    """

    # Bad answer
    bad_answer = "Just loop through and reverse it."

    # Evaluate both
    good_eval = evaluator.evaluate(question, good_answer, expert_context)
    bad_eval = evaluator.evaluate(question, bad_answer, expert_context)

    print(f"\n✅ Good answer score: {good_eval.total}/100")
    print(f"❌ Bad answer score: {bad_eval.total}/100")

    # Good should score at least 25 points higher
    assert good_eval.total > bad_eval.total + 25, (
        f"Good answer ({good_eval.total}) should score significantly higher than bad ({bad_eval.total})"
    )

    # Good answer should score at least 70
    assert good_eval.total >= 70, (
        f"Good answer should score at least 70, got {good_eval.total}"
    )

    # Bad answer should score below 50
    assert bad_eval.total < 50, (
        f"Bad answer should score below 50, got {bad_eval.total}"
    )


def test_evaluation_consistency(evaluator, knowledge_base):
    """Same answer should get similar scores across multiple evaluations"""

    question = "Implement binary search."
    answer = """
    Binary search works on sorted arrays.
    Use two pointers: left=0, right=len-1.
    While left <= right:
    - Calculate mid = (left + right) // 2
    - If arr[mid] == target: return mid
    - If arr[mid] < target: left = mid + 1
    - Else: right = mid - 1
    Return -1 if not found.
    Time: O(log n), Space: O(1).
    """

    results = knowledge_base.search(question, category="coding", k=2)
    expert_context = "\n".join([r.page_content for r in results])

    # Run evaluation 3 times
    scores = []
    for i in range(3):
        eval_result = evaluator.evaluate(question, answer, expert_context)
        scores.append(eval_result.total)
        print(f"Run {i + 1}: {eval_result.total}/100")

    # Check variance
    max_score = max(scores)
    min_score = min(scores)
    variance = max_score - min_score

    print(f"\nScore variance: {variance} points")
    print(f"Scores: {scores}")

    # Variance should be less than 10 points
    assert variance < 10, (
        f"Variance too high: {variance} points (max: {max_score}, min: {min_score})"
    )


def test_structured_output_format(evaluator):
    """Verify Pydantic structure is always returned"""

    question = "What is time complexity?"
    answer = "O(n) means linear time."
    expert = "Time complexity measures algorithm efficiency."

    evaluation = evaluator.evaluate(question, answer, expert)

    # Check all required fields
    assert hasattr(evaluation, "correctness")
    assert hasattr(evaluation, "clarity")
    assert hasattr(evaluation, "completeness")
    assert hasattr(evaluation, "total")
    assert hasattr(evaluation, "strengths")
    assert hasattr(evaluation, "weaknesses")
    assert hasattr(evaluation, "improvement")

    # Check ranges
    assert 0 <= evaluation.correctness <= 40
    assert 0 <= evaluation.clarity <= 30
    assert 0 <= evaluation.completeness <= 30
    assert 0 <= evaluation.total <= 100

    # Check lists have items
    assert len(evaluation.strengths) > 0
    assert len(evaluation.weaknesses) > 0
    assert len(evaluation.improvement) > 0

    print("✅ All structure checks passed")


def test_score_distribution(evaluator, knowledge_base):
    """Test that scores are reasonably distributed"""

    test_cases = [
        (
            "Implement quicksort",
            "Sort using pivot and partition. O(n log n) average.",
            "good",
        ),
        ("Implement quicksort", "Use sorting.", "bad"),
        (
            "Explain recursion",
            "Function calls itself with base case to stop infinite recursion.",
            "medium",
        ),
    ]

    scores = []
    for question, answer, quality in test_cases:
        results = knowledge_base.search(question, category="coding", k=1)
        expert = results[0].page_content if results else "Expert answer"

        evaluation = evaluator.evaluate(question, answer, expert)
        scores.append((quality, evaluation.total))
        print(f"{quality.upper()}: {evaluation.total}/100")

    # Extract scores by quality
    good_scores = [s for q, s in scores if q == "good"]
    bad_scores = [s for q, s in scores if q == "bad"]

    if good_scores and bad_scores:
        assert min(good_scores) > max(bad_scores), (
            "Good answers should always score higher than bad answers"
        )

    print(f"✅ Score distribution looks reasonable")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
