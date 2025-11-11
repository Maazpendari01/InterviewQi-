from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Optional, TypedDict
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# === STATE DEFINITIONS (Using TypedDict for LangGraph compatibility) ===
class Message(TypedDict):
    role: str  # "interviewer", "candidate", "evaluator", "user"
    content: str


class InterviewState(TypedDict):
    messages: List[Message]
    category: str
    question_count: int
    current_question: str
    current_question_id: str
    user_answer: str
    evaluation: str
    score: int
    repeat_count: int


# === KNOWLEDGE BASE MOCK ===
class InterviewKnowledgeBase:
    def search(self, query: str, category: str = "", k: int = 1):
        mock_results = [
            type(
                "Result",
                (),
                {
                    "page_content": "To reverse a linked list, use prev, curr, next pointers...",
                    "metadata": {
                        "question": "Design a function to reverse a linked list.",
                        "id": "q1",
                    },
                },
            ),
            type(
                "Result",
                (),
                {
                    "page_content": "For large lists, use chunking and disk storage...",
                    "metadata": {"question": "How to reverse a huge list?", "id": "q2"},
                },
            ),
        ]
        return mock_results[:k]


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

    # === HELPER METHOD ===
    def _get_message_attr(self, msg, attr):
        """Helper to get message attributes from either dict or Message object"""
        if isinstance(msg, dict):
            return msg.get(attr)
        return getattr(msg, attr, None)

    # === NODE 1: Start Interview ===
    def start_node(self, state: InterviewState):
        results = self.kb.search(f"{state['category']} interview", k=1)
        question = (
            results[0].metadata["question"] if results else "Explain your approach."
        )
        q_id = results[0].metadata["id"] if results else "q0"

        msg: Message = {"role": "interviewer", "content": question}
        return {
            "current_question": question,
            "current_question_id": q_id,
            "question_count": 1,
            "messages": state["messages"] + [msg],
            "repeat_count": 0,
        }

    # === NODE 2: Candidate Answers ===
    def candidate_answer_node(self, state: InterviewState):
        # Get last user message
        for msg in reversed(state["messages"]):
            if self._get_message_attr(msg, "role") == "user":
                content = self._get_message_attr(msg, "content")
                candidate_msg: Message = {"role": "candidate", "content": content}
                return {
                    "user_answer": content,
                    "messages": state["messages"] + [candidate_msg],
                }

        # Fallback
        fallback = "Use three pointers: prev, curr, next."
        candidate_msg: Message = {"role": "candidate", "content": fallback}
        return {
            "user_answer": fallback,
            "messages": state["messages"] + [candidate_msg],
        }

    # === NODE 3: Evaluate Answer (WITH REPEAT DETECTION) ===
    def evaluate_node(self, state: InterviewState):
        user_answer = state["user_answer"].strip().lower()
        past_answers = [
            self._get_message_attr(m, "content").strip().lower()
            for m in state["messages"]
            if self._get_message_attr(m, "role") == "candidate"
        ]

        # === REPEAT DETECTION ===
        if len(past_answers) > 1 and user_answer in past_answers[:-1]:
            repeat_count = state["repeat_count"] + 1
            content = (
                "Score: 30/100\n\n"
                "Weaknesses:\n"
                "- You repeated your previous answer verbatim.\n"
                "- This shows you are not listening to the question.\n"
                "- In a real interview, this would end the round.\n\n"
                "Improvement:\n"
                "Answer the *current* question directly. No copy-paste."
            )
            evaluator_msg: Message = {"role": "evaluator", "content": content}
            return {
                "evaluation": content,
                "score": 30,
                "repeat_count": repeat_count,
                "messages": state["messages"] + [evaluator_msg],
            }

        # === NORMAL EVALUATION ===
        expert_results = self.kb.search(state["current_question"], k=2)
        expert_context = "\n\n".join([r.page_content for r in expert_results])

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a strict technical interviewer.

If the candidate repeats a previous answer → give 30/100 and call it out.

Otherwise, evaluate normally.

Format:
Score: X/100

Strengths:
- ...

Weaknesses:
- ...

Improvement:
...""",
                ),
                (
                    "human",
                    """Question: {question}

Expert Examples:
{expert_context}

Previous Answers:
{previous}

Current Answer:
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
                "previous": "\n---\n".join(past_answers[:-1])
                if len(past_answers) > 1
                else "None",
                "user_answer": state["user_answer"],
            }
        )

        content = response.content if hasattr(response, "content") else str(response)
        score = 70
        for line in content.split("\n"):
            if "Score:" in line:
                try:
                    score = int("".join(filter(str.isdigit, line.split(":")[1])))
                    break
                except:
                    pass

        evaluator_msg: Message = {"role": "evaluator", "content": content}
        return {
            "evaluation": content,
            "score": score,
            "messages": state["messages"] + [evaluator_msg],
            "repeat_count": state["repeat_count"],
        }

    # === NODE 4: Generate Follow-up (ESCALATION + REPEAT AWARE) ===
    def followup_node(self, state: InterviewState):
        repeated = state["repeat_count"] > 0
        score = state["score"]

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Generate ONE follow-up question.

Rules:
- If repeated answer: Ask "Can you explain your answer in your own words?"
- If score < 60: Ask foundational
- If score 60–79: Ask clarification
- If score 80–89: Ask optimization
- If score >= 90: Ask system design twist

Be concise. No quotes.""",
                ),
                (
                    "human",
                    """Question: {question}
Score: {score}
Repeated: {repeated}

Next question:""",
                ),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "question": state["current_question"],
                "score": score,
                "repeated": "Yes" if repeated else "No",
            }
        )

        content = response.content.strip().strip("\"'").split("\n")[0]
        interviewer_msg: Message = {"role": "interviewer", "content": content}

        return {
            "current_question": content,
            "current_question_id": f"{state['current_question_id']}_f",
            "question_count": state["question_count"] + 1,
            "messages": state["messages"] + [interviewer_msg],
        }

    # === CONDITIONAL: Continue or End ===
    def should_continue(self, state: InterviewState):
        if state["repeat_count"] >= 2:
            return "end"
        return "continue" if state["question_count"] < 3 else "end"

    # === BUILD GRAPH ===
    def build_graph(self):
        workflow = StateGraph(InterviewState)

        workflow.add_node("start", self.start_node)
        workflow.add_node("candidate_answer", self.candidate_answer_node)
        workflow.add_node("evaluate", self.evaluate_node)
        workflow.add_node("followup", self.followup_node)

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
    graph = InterviewGraph()
    app = graph.graph

    initial_state: InterviewState = {
        "messages": [],
        "category": "coding",
        "question_count": 0,
        "current_question": "",
        "current_question_id": "",
        "user_answer": "",
        "evaluation": "",
        "score": 0,
        "repeat_count": 0,
    }

    config = {"configurable": {"thread_id": "test_123"}}
    state = initial_state

    print("Starting Interview...\n")
    for i in range(3):
        print(f"\n--- Question {i + 1} ---")
        for output in app.stream(state, config):
            node = list(output.keys())[0]
            data = output[node]
            if "messages" in data:
                last_msg = data["messages"][-1]
                role = (
                    last_msg.get("role")
                    if isinstance(last_msg, dict)
                    else last_msg.role
                )
                content = (
                    last_msg.get("content")
                    if isinstance(last_msg, dict)
                    else last_msg.content
                )
                print(f"[{role.upper()}]: {content}")
            state = {**state, **data}

        if i < 2:
            user_answer = input("\nYour answer: ") or "chunked streaming disk"
            user_msg: Message = {"role": "user", "content": user_answer}
            state["messages"].append(user_msg)
            print(f"[CANDIDATE]: {user_answer}\n")
