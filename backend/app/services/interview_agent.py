# backend/app/services/interview_agent.py

import os
from langchain_community.chat_models import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from .knowledge_base import InterviewKnowledgeBase
from dotenv import load_dotenv

load_dotenv()


class InterviewAgent:
    def __init__(self):
        """Agent uses Groq + local embeddings for RAG evaluation."""
        self.kb = InterviewKnowledgeBase()
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3,
            max_tokens=1024
        )

    # ---------- Get Question ----------
    def get_question(self, category: str = "coding"):
        """Retrieve one question from the knowledge base."""
        results = self.kb.search(f"{category} interview question", category=category, k=1)
        if results:
            return {
                "question": results[0].metadata["question"],
                "id": results[0].metadata["id"],
                "category": category,
            }
        else:
            # fallback if no question found
            return {
                "question": "Describe your problem-solving approach.",
                "id": "fallback",
                "category": category,
            }

    # ---------- Evaluate Answer ----------
    def evaluate_answer(self, question: str, user_answer: str, category: str):
        """Use Groq LLaMA 3.1-8B model to evaluate user answers."""
        expert_results = self.kb.search(question, category=category, k=2)
        expert_context = "\n\n".join([r.page_content for r in expert_results])

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert technical interviewer. "
             "Evaluate the candidate's answer against expert examples. "
             "Provide a score (0–100), strengths, weaknesses, and one improvement suggestion. "
             "Be constructive and concise."),
            ("human",
             "Question: {question}\n\n"
             "Expert Examples:\n{expert_context}\n\n"
             "Candidate Answer:\n{user_answer}\n\n"
             "Evaluation:")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "question": question,
            "expert_context": expert_context,
            "user_answer": user_answer
        })

        return response.content.strip()
