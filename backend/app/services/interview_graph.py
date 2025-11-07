from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from .interview_state import InterviewState, Message
from .knowledge_base import InterviewKnowledgeBase
import os

class InterviewGraph:
    def __init__(self):
        self.kb = InterviewKnowledgeBase()
        # Using Groq with llama3 or mixtral
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",  # or "mixtral-8x7b-32768"
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.graph = self.build_graph()

    def start_node(self, state: InterviewState):
        """Get first question"""
        results = self.kb.search(
            f"{state['category']} interview",
            category=state['category'],
            k=1
        )
        question = results[0].metadata['question'] if results else "Explain your approach."
        q_id = results[0].metadata['id'] if results else "fallback"

        return {
            "current_question": question,
            "current_question_id": q_id,
            "question_count": 1,
            "messages": [Message(role="interviewer", content=question)]
        }

    def evaluate_node(self, state: InterviewState):
        """Evaluate answer"""
        expert_results = self.kb.search(
            state['current_question'],
            category=state['category'],
            k=2
        )
        expert_context = "\n\n".join([r.page_content for r in expert_results])

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical interviewer. Evaluate the candidate's answer.

Provide your evaluation in this format:
Score: X/100

Strengths:
- [list specific strengths]

Weaknesses:
- [list specific weaknesses]

Improvement:
[one specific suggestion for improvement]

Be constructive and specific."""),
            ("human", """Question: {question}

Expert Examples:
{expert_context}

Candidate Answer:
{user_answer}

Evaluation:""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "question": state['current_question'],
            "expert_context": expert_context,
            "user_answer": state['user_answer']
        })

        # Parse score with better error handling
        score = 70  # default
        content = response.content if hasattr(response, 'content') else str(response)

        for line in content.split('\n'):
            if 'Score:' in line or 'score:' in line.lower():
                try:
                    # Extract number before /100
                    score_part = line.split(':')[1].split('/')[0]
                    score = int(''.join(filter(str.isdigit, score_part)))
                    break
                except:
                    pass

        return {
            "evaluation": content,
            "score": score,
            "messages": [Message(role="evaluator", content=content)]
        }

    def followup_node(self, state: InterviewState):
        """Generate follow-up"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical interviewer. Generate ONE relevant follow-up question based on the candidate's previous answer and score.

If score >= 70: Ask a deeper or related question
If score < 70: Ask a clarifying question or test a related concept

Keep the question concise and specific."""),
            ("human", """Previous question: {question}
Answer score: {score}/100

Generate one follow-up question:""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "question": state['current_question'],
            "score": state['score']
        })

        content = response.content if hasattr(response, 'content') else str(response)

        return {
            "current_question": content.strip(),
            "current_question_id": f"{state['current_question_id']}_followup",
            "question_count": state['question_count'] + 1,
            "messages": [Message(role="interviewer", content=content.strip())]
        }

    def should_continue(self, state: InterviewState):
        """Decide to continue or end"""
        return "continue" if state['question_count'] < 3 else "end"

    def build_graph(self):
        """Build workflow"""
        workflow = StateGraph(InterviewState)

        # Nodes
        workflow.add_node("start", self.start_node)
        workflow.add_node("evaluate", self.evaluate_node)
        workflow.add_node("followup", self.followup_node)

        # Edges
        workflow.set_entry_point("start")
        workflow.add_edge("start", "evaluate")
        workflow.add_conditional_edges(
            "evaluate",
            self.should_continue,
            {"continue": "followup", "end": END}
        )
        workflow.add_edge("followup", "evaluate")

        return workflow.compile()

# Test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    graph = InterviewGraph()
    state = InterviewState(
        messages=[],
        category="coding",
        question_count=0,
        current_question="",
        current_question_id="",
        user_answer="",
        evaluation="",
        score=0
    )

    # Test the start node
    result = graph.start_node(state)
    print(f"✅ Start node works!")
    print(f"Question: {result['current_question'][:100]}...")
