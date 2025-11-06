from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings  # FREE embeddings!
import json

class InterviewKnowledgeBase:
    def __init__(self, persist_dir="backend/data/chroma_db"):
        self.persist_dir = persist_dir
        # Use FREE HuggingFace embeddings instead of paid OpenAI
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None

    def load_questions(self):  # ← This needs to be indented
        from pathlib import Path

        # Get path relative to this script file
        script_dir = Path(__file__).parent  # .../app/services/
        json_file = script_dir.parent.parent / 'data' / 'interview_qa.json'

        # Debugging
        print(f"Looking for file at: {json_file.absolute()}")

        if not json_file.exists():
            raise FileNotFoundError(f"Cannot find interview_qa.json at {json_file.absolute()}")

        with open(json_file, 'r') as f:
            return json.load(f)

    def ingest(self):  # ← This also needs to be indented at the same level
        """Ingest all questions into vector DB"""
        print("📚 Loading questions...")
        data = self.load_questions()

        texts = []
        metadatas = []

        for category, questions in data.items():
            for q in questions:
                # Create document
                doc = f"""
Question: {q['question']}
Category: {category}
Difficulty: {q['difficulty']}

Expert Approach:
{q['expert_approach']}

Key Points:
{chr(10).join(f"- {p}" for p in q['key_points'])}

Common Mistakes:
{chr(10).join(f"- {m}" for m in q['common_mistakes'])}

Follow-ups:
{chr(10).join(f"- {f}" for f in q['follow_ups'])}
"""
                texts.append(doc)
                metadatas.append({
                    "id": q['id'],
                    "category": category,
                    "difficulty": q['difficulty'],
                    "question": q['question']
                })

        print(f"📊 Embedding {len(texts)} documents (using FREE HuggingFace embeddings)...")

        # Create vector store
        self.vector_store = Chroma.from_texts(
            texts=texts,
            metadatas=metadatas,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )

        print(f"✅ Done! Stored in {self.persist_dir}")
        return len(texts)

    def search(self, query: str, category: str = None, k: int = 3):
        """Search for relevant questions"""
        if not self.vector_store:
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )

        filter_dict = {"category": category} if category else None
        results = self.vector_store.similarity_search(
            query, k=k, filter=filter_dict
        )
        return results


# Test
if __name__ == "__main__":
    kb = InterviewKnowledgeBase()
    num_docs = kb.ingest()
    print(f"\n✅ Ingested {num_docs} documents")

    # Test search
    print("\n🔍 Testing search...")
    results = kb.search("reverse linked list", category="coding", k=1)
    for r in results:
        print(f"\n{r.page_content[:200]}...")
