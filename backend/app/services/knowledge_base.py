# backend/app/services/knowledge_base.py

import os
import json
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
# from langchain_postgres import PGVector  # optional for PostgreSQL later
from tqdm import tqdm


class InterviewKnowledgeBase:
    def __init__(self, persist_dir="backend/data/chroma_db", use_pgvector=False):
        """Knowledge base using HuggingFace embeddings and ChromaDB or pgvector."""
        self.persist_dir = persist_dir
        self.use_pgvector = use_pgvector
        self.vector_store = None

        # ---------- Load Embedding Model ----------
        cache_folder = Path("backend/data/models")
        cache_folder.mkdir(parents=True, exist_ok=True)

        print("🔧 Loading embedding model (all-MiniLM-L6-v2)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_folder=str(cache_folder),
            model_kwargs={'device': 'cpu'},  # change to 'cuda' if GPU available
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ Embedding model loaded and cached locally!")

    # ---------- Load JSON Questions ----------
    def load_questions(self):
        file_path = Path("backend/data/interview_qa.json")
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
            from langchain_postgres import PGVector
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
            self.vector_store = Chroma.from_texts(
                texts=texts,
                metadatas=metadatas,
                embedding=self.embeddings,
                persist_directory=self.persist_dir,
                collection_name="interview_questions"
            )
            print(f"✅ Stored in ChromaDB: {self.persist_dir}")

        return len(texts)

    # ---------- Search ----------
    def search(self, query: str, category: str = None, k: int = 3):
        """Search for similar questions in the knowledge base."""
        if not self.vector_store:
            if self.use_pgvector:
                from langchain_postgres import PGVector
                self.vector_store = PGVector(
                    connection_string=os.getenv("POSTGRES_URL"),
                    embedding_function=self.embeddings,
                    collection_name="interview_qa"
                )
            else:
                self.vector_store = Chroma(
                    persist_directory=self.persist_dir,
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
