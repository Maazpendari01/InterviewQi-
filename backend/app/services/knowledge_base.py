# backend/app/services/knowledge_base.py

import os
import json
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
# from langchain_community.vectorstores.pgvector import PGVector  # optional for PostgreSQL later
from tqdm import tqdm
import chromadb


class InterviewKnowledgeBase:
    def __init__(self, persist_dir="backend/data/chroma_db", use_pgvector=False):
        """Knowledge base using HuggingFace embeddings and ChromaDB or pgvector."""
        self.persist_dir = persist_dir
        self.use_pgvector = use_pgvector
        self.vector_store = None

        # ---------- Load Embedding Model ----------
        print("🚀 Initializing Interview Knowledge Base...")
        cache_folder = Path("backend/data/models")
        cache_folder.mkdir(parents=True, exist_ok=True)

        print("🔧 Loading embedding model (all-MiniLM-L6-v2)...")
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                cache_folder=str(cache_folder),
                model_kwargs={'device': 'cpu'},  # change to 'cuda' if GPU available
                encode_kwargs={'normalize_embeddings': True}
            )
            print("✅ Embedding model loaded and cached locally!")
            # Initialize vector store with questions
            try:
                self.ingest()
                print("✅ Questions loaded and embedded successfully!")
            except Exception as e:
                print(f"⚠️ Error loading questions: {str(e)}")
                raise
        except Exception as e:
            print(f"⚠️ Error loading embedding model: {str(e)}")
            raise

    # ---------- Load JSON Questions ----------
    def load_questions(self):
        # Resolve path from project root no matter where script runs
        base_dir = Path(__file__).resolve().parents[2]  # goes up from /app/services/ to /backend
        file_path = base_dir / "data" / "interview_qa.json"

        if not file_path.exists():
            raise FileNotFoundError(f"❌ interview_qa.json not found at {file_path.resolve()}")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # ---------- Ingest into Vector Store ----------
    def ingest(self):
        """Ingest questions into Chroma or pgvector with progress bar."""
        print("📚 Loading questions...")
        data = self.load_questions()
        texts, metadatas = [], []

        for category, questions in data.items():
            print(f"  Processing {category}...")
            for q in tqdm(questions, desc=f"  {category}"):
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
                texts.append(doc.strip())
                metadatas.append({
                    "id": q["id"],
                    "category": category,
                    "difficulty": q["difficulty"],
                    "question": q["question"]
                })

        print(f"📊 Embedding {len(texts)} documents (this may take 30–60s)...")

        # ---------- Create Vector Store ----------
        if self.use_pgvector:
            # PostgreSQL + pgvector (future production)
            from langchain_community.vectorstores.pgvector import PGVector
            from sqlalchemy import create_engine
            engine = create_engine(os.getenv("POSTGRES_URL"))
            self.vector_store = PGVector(
                connection_string=os.getenv("POSTGRES_URL"),
                embedding_function=self.embeddings,
                collection_name="interview_qa"
            )
            print("✅ Using PostgreSQL + pgvector as vector store.")
        else:
            # Local development (Chroma)
            try:
                client = chromadb.PersistentClient(path=self.persist_dir)
                collection = client.get_or_create_collection(name="interview_questions")

                self.vector_store = Chroma(
                    client=client,
                    collection_name="interview_questions",
                    embedding_function=self.embeddings,
                )

                # Add documents to collection
                self.vector_store.add_texts(
                    texts=texts,
                    metadatas=metadatas
                )
                print(f"✅ Stored in ChromaDB: {self.persist_dir}")
            except Exception as e:
                print(f"⚠️ Error with ChromaDB: {str(e)}")
                raise

        return len(texts)

    # ---------- Search ----------
    def search(self, query: str, category: str = None, k: int = 3):
        """Search for similar questions in the knowledge base."""
        if not self.vector_store:
            if self.use_pgvector:
                from langchain_community.vectorstores.pgvector import PGVector
                self.vector_store = PGVector(
                    connection_string=os.getenv("POSTGRES_URL", ""),  # Provide empty default
                    embedding_function=self.embeddings,
                    collection_name="interview_qa"
                )
            else:
                client = chromadb.PersistentClient(path=self.persist_dir)
                self.vector_store = Chroma(
                    client=client,
                    collection_name="interview_questions",
                    embedding_function=self.embeddings
                )

        filter_dict = {"category": category} if category else None
        results = self.vector_store.similarity_search(query, k=k, filter=filter_dict)
        return results


# ---------- Run Test ----------
if __name__ == "__main__":
    kb = InterviewKnowledgeBase()
    num_docs = kb.ingest()
    print(f"\n✅ Ingested {num_docs} documents")

    print("\n🔍 Testing search...")
    results = kb.search("reverse linked list", category="coding", k=1)
    for r in results:
        print(f"\n{r.page_content[:250]}...")
