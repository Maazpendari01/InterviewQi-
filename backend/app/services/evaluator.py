from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
import os


class EvaluationScore(BaseModel):
    """Structured evaluation output"""

    correctness: int = Field(
        description="Technical correctness (0-40 points)", ge=0, le=40
    )
    clarity: int = Field(description="Communication clarity (0-30 points)", ge=0, le=30)
    completeness: int = Field(
        description="Thoroughness and edge cases (0-30 points)", ge=0, le=30
    )
    total: int = Field(description="Total score (0-100 points)", ge=0, le=100)
    strengths: List[str] = Field(description="2-3 specific strengths in the answer")
    weaknesses: List[str] = Field(description="2-3 specific areas for improvement")
    improvement: str = Field(description="One specific, actionable suggestion")


class StructuredEvaluator:
    """Evaluates interview answers with structured Pydantic output"""

    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,  # Lower for consistency
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.parser = PydanticOutputParser(pydantic_object=EvaluationScore)

    def evaluate(
        self, question: str, user_answer: str, expert_context: str
    ) -> EvaluationScore:
        """
        Evaluate answer using structured rubric

        Args:
            question: The interview question
            user_answer: Candidate's response
            expert_context: Retrieved expert examples from RAG

        Returns:
            EvaluationScore with all fields populated
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert technical interviewer evaluating a candidate's answer.

Use this rubric:
- Correctness (0-40): Technical accuracy, sound reasoning, correct algorithms/concepts
- Clarity (0-30): How well explained, logical flow, appropriate terminology
- Completeness (0-30): Covers edge cases, discusses tradeoffs, considers alternatives

Be strict but fair. Most answers score 60-80. Only exceptional answers score 90+.

{format_instructions}""",
                ),
                (
                    "human",
                    """Question:
{question}

Expert Examples (for reference):
{expert_context}

Candidate's Answer:
{user_answer}

Provide detailed evaluation:""",
                ),
            ]
        )

        formatted_prompt = prompt.format_messages(
            format_instructions=self.parser.get_format_instructions(),
            question=question,
            expert_context=expert_context,
            user_answer=user_answer,
        )

        response = self.llm.invoke(formatted_prompt)

        try:
            evaluation = self.parser.parse(response.content)

            # Recalculate total to ensure consistency
            calculated_total = (
                evaluation.correctness + evaluation.clarity + evaluation.completeness
            )
            evaluation.total = calculated_total

            return evaluation

        except Exception as e:
            # Fallback if parsing fails
            print(f"⚠️ Parsing failed: {e}")
            return EvaluationScore(
                correctness=25,
                clarity=20,
                completeness=20,
                total=65,
                strengths=["Attempted to answer the question"],
                weaknesses=["Evaluation could not be fully parsed"],
                improvement="Please provide more detailed explanations",
            )

    def format_evaluation(self, evaluation: EvaluationScore) -> str:
        """Format evaluation for display"""
        return f"""Score: {evaluation.total}/100

Breakdown:
- Correctness: {evaluation.correctness}/40
- Clarity: {evaluation.clarity}/30
- Completeness: {evaluation.completeness}/30

Strengths:
{chr(10).join(f"✓ {s}" for s in evaluation.strengths)}

Weaknesses:
{chr(10).join(f"✗ {w}" for w in evaluation.weaknesses)}

Improvement:
→ {evaluation.improvement}
"""


# Test
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    evaluator = StructuredEvaluator()

    # Test evaluation
    question = "Design a function to reverse a linked list."
    user_answer = (
        "Use three pointers: prev, curr, next. Iterate through, reversing pointers."
    )
    expert = "Use three pointers (previous, current, next). Time O(n), Space O(1)."

    result = evaluator.evaluate(question, user_answer, expert)

    print("Testing Structured Evaluator:\n")
    print(evaluator.format_evaluation(result))
    print(f"\nPydantic model: {result}")
