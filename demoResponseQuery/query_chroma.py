# scripts/query_chroma.py
import chromadb

# Define your query
query = "What are basic thing we need to care before buying property?"

# Connect to the persisted Chroma DB
client = chromadb.PersistentClient(path="vector_db/chroma_store")

# Load your collection
collection = client.get_collection(name="architect_knowledge")

# Perform semantic query
results = collection.query(
    query_texts=[query],
    n_results=3
)

# Print the top documents and metadata
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"\n📄 {meta['filename']}\n{doc}")
