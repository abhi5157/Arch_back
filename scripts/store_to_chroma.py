import os
import uuid
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Paths
CHUNK_DIR = "data/processed/clean_text"
CHROMA_DIR = "vector_db/chroma_store"

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(name="architect_knowledge")

def embed_all_chunks():
    total_count = 0

    for filename in os.listdir(CHUNK_DIR):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(CHUNK_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if not text:
            continue

        embedding = model.encode(text).tolist()

        collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[{"filename": filename}],
            ids=[str(uuid.uuid4())]
        )

        total_count += 1
        print(f"✅ Stored: {filename}")

    print(f"\n🔢 Total chunks embedded and stored: {total_count}")

if __name__ == "__main__":
    embed_all_chunks()
