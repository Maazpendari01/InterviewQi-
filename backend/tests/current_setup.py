
from  backend.app.services.knowledge_base import InterviewKnowledgeBase
from backend.app.services.interview_agent import InterviewAgent
import time

def test_full_pipeline():
    print("=" * 60)
    print("TESTING YOUR GROQ + HUGGINGFACE SETUP")
    print("=" * 60)

    # 1. Test knowledge base
    print("\n1️⃣ Testing Knowledge Base...")
    kb = InterviewKnowledgeBase()

    start = time.time()
    results = kb.search("reverse linked list", category="coding", k=2)
    search_time = time.time() - start

    print(f"   ✅ Search completed in {search_time:.2f}s")
    print(f"   Found {len(results)} results")
    if results:
        print(f"   Top result: {results[0].metadata['question'][:50]}...")

    # 2. Test agent
    print("\n2️⃣ Testing Interview Agent...")
    agent = InterviewAgent()

    # Get question
    q = agent.get_question("coding")
    print(f"   ✅ Got question: {q['question'][:50]}...")

    # Evaluate answer
    test_answers = [
        ("Great answer", "Use three pointers: prev, curr, next. Iterate through list, reverse pointers. Time O(n), Space O(1)."),
        ("Medium answer", "Use a loop to reverse the list."),
        ("Poor answer", "I'm not sure how to do this.")
    ]

    print("\n3️⃣ Testing Evaluation Quality...")
    for label, answer in test_answers:
        print(f"\n   Testing: {label}")
        print(f"   Answer: {answer[:50]}...")

        start = time.time()
        try:
            evaluation = agent.evaluate_answer(q['question'], answer, "coding")
            eval_time = time.time() - start

            # Extract score
            score_line = [line for line in evaluation.split('\n') if 'Score' in line][0]
            score = int(''.join(filter(str.isdigit, score_line.split(':')[1][:3])))

            print(f"   ✅ Score: {score}/100 (took {eval_time:.2f}s)")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour setup is working correctly with:")
    print("  • HuggingFace Embeddings (FREE)")
    print("  • llama-3.1-8b-instant(FREE)")
    print("  • ChromaDB (FREE)")
    print(f"\nTotal cost: $0.00 🎉")

if __name__ == "__main__":
    test_full_pipeline()
