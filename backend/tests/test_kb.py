from app.services.knowledge_base import InterviewKnowledgeBase

def test_knowledge_base():
    print("Testing Knowledge Base...")
    kb = InterviewKnowledgeBase()
    
    # Test loading questions
    print("\nTesting question loading...")
    questions = kb.load_questions()
    print(f"Loaded {len(questions)} categories of questions")
    for category, items in questions.items():
        print(f"- {category}: {len(items)} questions")
    
    return questions

if __name__ == "__main__":
    test_knowledge_base()