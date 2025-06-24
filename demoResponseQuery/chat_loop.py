import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from groq import Groq

# Load .env
load_dotenv()

# Load model + DB
model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="vector_db/chroma_store")
collection = chroma_client.get_collection(name="architect_knowledge")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize chat memory
chat_history = []

print("🧠 Real Estate Architect Assistant (type 'exit' to quit)\n")

while True:
    user_input = input("👤 You: ")
    if user_input.strip().lower() in ['exit', 'quit']:
        print("👋 Goodbye!")
        break

    # 1. Embed and retrieve from Chroma
    query_vector = model.encode(user_input).tolist()
    results = collection.query(query_embeddings=[query_vector], n_results=3)
    context = "\n\n".join(results["documents"][0])

    # 2. Build full chat prompt
    messages = []
    
    # System prompt
    messages.append({
        "role": "system",
        "content": "You are a helpful real estate architect assistant. Use only the context provided to answer user queries. Be accurate, helpful, and detail-oriented."
    })

    # Add memory
    for turn in chat_history[-5:]:  # Limit to last 5 turns to stay under token limit
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["bot"]})

    # Add current turn
    prompt = f"""Use the following context to answer the user's question.

Context:
{context}
Question: {user_input}"""
    messages.append({"role": "user", "content": prompt})

    # 3. Call Groq LLM
    response = groq_client.chat.completions.create(
        model="mistral-saba-24b",
        messages=messages,
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stream=True
    )

    # 4. Stream response
    print("🤖 Assistant:", end=" ", flush=True)
    bot_response = ""
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            bot_response += delta
    print("\n" + "-" * 50)

    # 5. Update memory
    chat_history.append({"user": user_input, "bot": bot_response})
