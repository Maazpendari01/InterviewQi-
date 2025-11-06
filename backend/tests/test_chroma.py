import chromadb

def test_chroma():
    """Test ChromaDB"""
    try:
        client = chromadb.Client()
        collection = client.create_collection(name="test")
        collection.add(
            documents=["Test document"],
            ids=["doc1"]
        )
        results = collection.query(
            query_texts=["test"],
            n_results=1
        )
        print(f"✅ Chroma: {results['documents']}")
        return True
    except Exception as e:
        print(f"❌ Chroma Error: {e}")
        return False

if __name__ == "__main__":
    test_chroma()
