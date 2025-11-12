from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()


# === STATE DEFINITIONS ===
@dataclass
class Message:
    role: str  # "interviewer", "user", "evaluator"
    content: str


@dataclass
class InterviewState:
    messages: List[Message]
    category: str
    question_count: int
    current_question: str
    current_question_id: str
    user_answer: str
    evaluation: str
    score: int


# === KNOWLEDGE BASE WITH CATEGORY-SPECIFIC QUESTIONS ===
class InterviewKnowledgeBase:
    def __init__(self):
        # Category-specific question banks
        self.questions = {
            "coding": [
                {
                    "id": "coding_q1",
                    "question": "Implement a function to reverse a singly linked list. Explain your approach and analyze the time/space complexity.",
                    "expert_answer": "Use three pointers (prev, curr, next). Iterate through list, reversing links. Time: O(n), Space: O(1).",
                },
                {
                    "id": "coding_q2",
                    "question": "Design an algorithm to find the longest substring without repeating characters. What data structure would you use?",
                    "expert_answer": "Use sliding window with HashSet. Track characters seen, expand/contract window. Time: O(n), Space: O(min(n,m)).",
                },
                {
                    "id": "coding_q3",
                    "question": "Explain how you would implement a LRU (Least Recently Used) cache with O(1) get and put operations.",
                    "expert_answer": "Use HashMap + Doubly Linked List. HashMap for O(1) access, DLL for O(1) eviction of LRU item.",
                },
            ],
            "system_design": [
                {
                    "id": "sysdesign_q1",
                    "question": "Design a URL shortening service like bit.ly. How would you handle billions of URLs and ensure high availability?",
                    "expert_answer": "Use base62 encoding, distributed key generation, CDN for redirects, database sharding, cache layer.",
                },
                {
                    "id": "sysdesign_q2",
                    "question": "How would you design Instagram's news feed? Focus on scalability and real-time updates.",
                    "expert_answer": "Fan-out on write for small followings, fan-out on read for celebrities. Use Redis cache, message queues, CDN.",
                },
                {
                    "id": "sysdesign_q3",
                    "question": "Design a distributed rate limiter that can handle millions of requests per second across multiple servers.",
                    "expert_answer": "Use Redis with sliding window counters, token bucket algorithm, consistent hashing for distribution.",
                },
            ],
            "behavioral": [
                {
                    "id": "behavioral_q1",
                    "question": "Tell me about a time when you had to work with a difficult team member. How did you handle the situation and what was the outcome?",
                    "expert_answer": "Use STAR method: Situation, Task, Action, Result. Focus on communication, empathy, problem-solving.",
                },
                {
                    "id": "behavioral_q2",
                    "question": "Describe a situation where you had to make a decision with incomplete information. What was your approach?",
                    "expert_answer": "Gather available data, assess risks, make informed decision, iterate based on feedback.",
                },
                {
                    "id": "behavioral_q3",
                    "question": "Tell me about a project you're most proud of. What challenges did you face and how did you overcome them?",
                    "expert_answer": "Highlight technical challenges, leadership, impact, lessons learned, measurable results.",
                },
            ],
        }

        self.question_index = {"coding": 0, "system_design": 0, "behavioral": 0}

    def search(self, query: str, category: str = "coding", k: int = 1):
        """Get category-specific questions"""
        # Normalize category name
        category = category.lower().replace(" ", "_")

        # Get questions for category
        category_questions = self.questions.get(category, self.questions["coding"])

        # Get next question in rotation
        idx = self.question_index.get(category, 0) % len(category_questions)
        self.question_index[category] = idx + 1

        # Return mock Result objects
        selected = category_questions[idx : idx + k]
        results = []
        for q in selected:
            result = type(
                "Result",
                (),
                {
                    "page_content": q["expert_answer"],
                    "metadata": {
                        "question": q["question"],
                        "id": q["id"],
                        "category": category,
                    },
                },
            )
            results.append(result)

        return results


# === MAIN GRAPH CLASS ===
class InterviewGraph:
    def __init__(self):
        self.kb = InterviewKnowledgeBase()
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.graph = self.build_graph()

    # === NODE 1: Start Interview ===
    def start_node(self, state: InterviewState):
        """Generate first question based on category"""
        category = state["category"]

        # Get category-specific question from knowledge base
        results = self.kb.search(f"{category} interview", category=category, k=1)

        question = (
            results[0].metadata["question"] if results else "Explain your approach."
        )
        q_id = results[0].metadata["id"] if results else f"{category}_q0"

        interviewer_msg = Message(role="interviewer", content=question)

        print(f"🎯 Starting {category} interview")
        print(f"📝 Question: {question[:100]}...")

        return {
            "current_question": question,
            "current_question_id": q_id,
            "question_count": 1,
            "messages": state["messages"] + [interviewer_msg],
        }

    # === NODE 2: Candidate Answers ===
    def candidate_answer_node(self, state: InterviewState):
        # In real app: wait for user input via API
        # For testing: look for last user message
        for msg in reversed(state["messages"]):
            if msg.role == "user":
                return {"user_answer": msg.content}

        # Fallback
        return {
            "user_answer": state.get("user_answer", "I need to think about this...")
        }

    # === NODE 3: Evaluate Answer ===
    def evaluate_node(self, state: InterviewState):
        """Evaluate answer using RAG with category context"""
        category = state["category"]

        # Get expert examples from knowledge base
        expert_results = self.kb.search(
            state["current_question"], category=category, k=2
        )
        expert_context = "\n\n".join([r.page_content for r in expert_results])

        # Category-specific evaluation criteria
        evaluation_focus = {
            "coding": "code quality, algorithm efficiency, time/space complexity, edge cases",
            "system_design": "scalability, reliability, trade-offs, component design, data flow",
            "behavioral": "STAR method (Situation, Task, Action, Result), specific examples, impact, lessons learned",
        }

        focus = evaluation_focus.get(category, "overall quality")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are an expert {category} interviewer. Evaluate the candidate's answer focusing on: {focus}

Provide your evaluation in this exact format:

Score: X/100

Strengths:
- [specific strength 1]
- [specific strength 2]

Weaknesses:
- [specific weakness 1]
- [specific weakness 2]

Improvement:
[one actionable suggestion]

Be constructive, specific, and reference the expert examples.""",
                ),
                (
                    "human",
                    """Question: {question}

Expert Examples:
{expert_context}

Candidate Answer:
{user_answer}

Evaluation:""",
                ),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "question": state["current_question"],
                "expert_context": expert_context,
                "user_answer": state["user_answer"],
            }
        )

        content = response.content if hasattr(response, "content") else str(response)

        # Extract score
        score = 70  # default
        for line in content.split("\n"):
            if "Score:" in line or "score:" in line.lower():
                try:
                    score_part = line.split(":")[1].strip().split("/")[0]
                    score = int("".join(filter(str.isdigit, score_part)))
                    break
                except:
                    pass

        evaluator_msg = Message(role="evaluator", content=content)

        print(f"⭐ Score: {score}/100")

        return {
            "evaluation": content,
            "score": score,
            "messages": state["messages"] + [evaluator_msg],
        }

    # === NODE 4: Generate Follow-up ===
    def followup_node(self, state: InterviewState):
        """Generate category-appropriate follow-up question"""
        category = state["category"]

        # Get next question from knowledge base instead of generating
        results = self.kb.search(f"{category} followup", category=category, k=1)

        if results and state["question_count"] < 3:
            new_question = results[0].metadata["question"]
            new_id = results[0].metadata["id"]
        else:
            # Fallback: generate with LLM
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        f"""You are an expert {category} interviewer. Generate ONE relevant follow-up question.

If score >= 70: Ask a deeper or optimization question
If score < 70: Ask a clarifying or foundational question

Keep it specific to {category} interviews.""",
                    ),
                    (
                        "human",
                        """Previous question: {question}
Answer score: {score}/100
Category: {category}

Generate one follow-up question:""",
                    ),
                ]
            )

            chain = prompt | self.llm
            response = chain.invoke(
                {
                    "question": state["current_question"],
                    "score": state["score"],
                    "category": category,
                }
            )

            content = (
                response.content if hasattr(response, "content") else str(response)
            )
            new_question = content.strip().strip("\"'").split("\n")[0]
            new_id = f"{state['current_question_id']}_followup"

        interviewer_msg = Message(role="interviewer", content=new_question)

        print(f"➡️  Next question: {new_question[:100]}...")

        return {
            "current_question": new_question,
            "current_question_id": new_id,
            "question_count": state["question_count"] + 1,
            "messages": state["messages"] + [interviewer_msg],
        }

    # === CONDITIONAL: Continue or End ===
    def should_continue(self, state: InterviewState):
        count = state.get("question_count", 0)
        result = "continue" if count < 3 else "end"
        print(f"🔄 Question {count}/3 - {result}")
        return result

    # === BUILD GRAPH ===
    def build_graph(self):
        workflow = StateGraph(InterviewState)

        # Nodes
        workflow.add_node("start", self.start_node)
        workflow.add_node("candidate_answer", self.candidate_answer_node)
        workflow.add_node("evaluate", self.evaluate_node)
        workflow.add_node("followup", self.followup_node)

        # Edges
        workflow.set_entry_point("start")
        workflow.add_edge("start", "candidate_answer")
        workflow.add_edge("candidate_answer", "evaluate")
        workflow.add_conditional_edges(
            "evaluate", self.should_continue, {"continue": "followup", "end": END}
        )
        workflow.add_edge("followup", "candidate_answer")

        return workflow.compile()


# === TEST SCRIPT ===
if __name__ == "__main__":
    load_dotenv()

    # Test all categories
    for test_category in ["coding", "system_design", "behavioral"]:
        print(f"\n{'=' * 60}")
        print(f"Testing {test_category.upper()} Interview")
        print(f"{'=' * 60}\n")

        graph = InterviewGraph()
        app = graph.graph

        initial_state = InterviewState(
            messages=[],
            category=test_category,
            question_count=0,
            current_question="",
            current_question_id="",
            user_answer="",
            evaluation="",
            score=0,
        )

        state = initial_state

        # Just test first question generation
        for output in app.stream(state):
            node = list(output.keys())[0]
            data = output[node]
            state = {**state, **data}

            if node == "start":
                print(f"✅ Generated {test_category} question successfully!")
                break
