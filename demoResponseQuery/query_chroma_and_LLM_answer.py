# scripts/query_chroma_and_answer.py

import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Initialize Chroma + embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="vector_db/chroma_store")
collection = client.get_collection(name="architect_knowledge")

# Initialize Groq SDK
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Input from user
query = input("🔍 Ask your question: ")

# Encode query and search Chroma
query_vector = model.encode(query).tolist()
results = collection.query(query_embeddings=[query_vector], n_results=3)

# Prepare prompt with context
top_chunks = results["documents"][0]
context = "\n\n".join(top_chunks)

prompt = f"""You are an expert real estate architect assistant.

Use only the following information to answer the question helpfully and accurately.

Context:
{context}

Question: {query}

Answer:"""

# Use Groq to generate answer
completion = groq_client.chat.completions.create(
    model=os.getenv("GROQ_MODEL"),  # or any other accepted model model="mistral-saba-24b"
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=1024,
    top_p=1,
    stream=True
)

# Print streamed response
print("\n🧠 AI Answer:\n")
for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
