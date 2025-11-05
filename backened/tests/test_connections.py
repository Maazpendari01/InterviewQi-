from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def test_groq():
    """Test Groq API connection"""
    try:
        # Use Llama 3 70B - it's FREE and powerful!
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        response = llm.invoke("Say 'Connected!' if you hear me")
        print(f"✅ Groq: {response.content}")
        print(f"   Model: llama3-70b-8192")
        print(f"   Speed: BLAZING FAST! 🚀")
        return True
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        print("   Get free key at: https://console.groq.com/keys")
        return False

if __name__ == "__main__":
    test_groq()
