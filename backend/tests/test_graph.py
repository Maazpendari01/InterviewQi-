from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def test_groq():
    """Test Groq API connection"""
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )
        response = llm.invoke("Say 'Connected!' if you hear me")
        content = response.content if hasattr(response, 'content') else str(response)
        print(f"✅ Groq: {content}")
        return True
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return False

if __name__ == "__main__":
    test_groq()
