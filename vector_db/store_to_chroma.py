# import os
# import json
# import chromadb

# # Paths
# EMBEDDING_FILE = "data/processed/embeddings_local.json"
# CHROMA_DB_DIR = "vector_db/chroma_store"
# COLLECTION_NAME = "architect_knowledge"

# # Initialize persistent Chroma client
# chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

# # Remove existing collection if it exists
# existing = chroma_client.list_collections()
# if any(col.name == COLLECTION_NAME for col in existing):
#     chroma_client.delete_collection(name=COLLECTION_NAME)

# # Create new collection
# collection = chroma_client.create_collection(name=COLLECTION_NAME)

# # Load embeddings
# with open(EMBEDDING_FILE, "r", encoding="utf-8") as f:
#     data = json.load(f)

# # Insert embeddings into Chroma
# for idx, item in enumerate(data):
#     collection.add(
#         documents=[item["text"]],
#         embeddings=[item["embedding"]],
#         ids=[f"doc_{idx}"],
#         metadatas=[{"filename": item["filename"]}]
#     )
#     print(f"✅ Stored: {item['filename']}")

# print(f"\n✅ Chroma DB stored at: {CHROMA_DB_DIR}")
import os
import uuid
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="vector_db/chroma_store")
collection = client.get_or_create_collection(name="architect_knowledge")

# ✅ Process both clean_text and property_chunks
chunk_dirs = ["data/processed/clean_text", "data/processed/property_chunks"]


def embed_all_chunks():
    total = 0
    for CHUNK_DIR in chunk_dirs:
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

            print(f"✅ Embedded: {filename}")
            total += 1
    print(f"\n🔢 Total embedded: {total}")

if __name__ == "__main__":
    embed_all_chunks()
