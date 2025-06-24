from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from groq import Groq

# Load .env
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and DB
model = SentenceTransformer("paraphrase-MiniLM-L3-v2",device="cpu")
chroma_client = chromadb.PersistentClient(path="vector_db/chroma_store")
collection = chroma_client.get_collection(name="architect_knowledge")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Chat memory to keep context (can be replaced by session-based memory)
chat_history = []

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    user_input = request.message

    if not user_input:
        return {"error": "Message field is required"}

    # 1. Embed and retrieve from Chroma
    query_vector = model.encode(user_input).tolist()
    results = collection.query(query_embeddings=[query_vector], n_results=2)
    context = "\n\n".join(results["documents"][0])

    # 2. Build full chat prompt
    messages = [
        {"role": "system", "content": "You are a helpful real estate architect assistant. Use only the context provided to answer user queries. Be accurate, helpful, and detail-oriented."}
    ]

    for turn in chat_history[-3:]:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["bot"]})

    prompt = f"""Use the following context to answer the user's question.\n\nContext:\n{context}\nQuestion: {user_input}"""
    messages.append({"role": "user", "content": prompt})

    # 3. Call Groq LLM
    response = groq_client.chat.completions.create(
        model="mistral-saba-24b",
        messages=messages,
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stream=False
    )

    bot_response = response.choices[0].message.content

    # 4. Update memory
    chat_history.append({"user": user_input, "bot": bot_response})

    return {"response": bot_response}
