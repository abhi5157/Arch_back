# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import os
# import chromadb
# from chromadb.config import Settings
# from sentence_transformers import SentenceTransformer
# from dotenv import load_dotenv
# from groq import Groq

# # Load .env
# load_dotenv()

# # Initialize FastAPI
# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load model and DB
# model = SentenceTransformer("all-MiniLM-L6-v2")
# chroma_client = chromadb.PersistentClient(path="vector_db/chroma_store")
# collection = chroma_client.get_collection(name="architect_knowledge")
# groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# # Chat memory to keep context (can be replaced by session-based memory)
# chat_history = []

# class ChatRequest(BaseModel):
#     message: str

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Chat API"}

# @app.post("/chat")
# async def chat(request: ChatRequest):
#     user_input = request.message

#     if not user_input:
#         return {"error": "Message field is required"}

#     # 1. Embed and retrieve from Chroma
#     query_vector = model.encode(user_input).tolist()
#     results = collection.query(query_embeddings=[query_vector], n_results=3)
#     context = "\n\n".join(results["documents"][0])

#     # 2. Build full chat prompt
#     messages = [
#         {
#             "role": "system", 
#             "content": '''
#             You are a helpful and intelligent assistant. Your task is to answer user queries using the provided context when available.
#             Instructions:
#             1. If the provided context contains enough information to answer the query, use only that context to respond.
#             2. If the context is missing or does not include sufficient information, you may answer based on your own knowledge.
#             3. Clearly prioritize accuracy and relevance.
#             4. If the context is not sufficient, do not fabricate information.
#             5. You are AI with information on architecture, engineering, and construction (AEC) topics,not other field if user ask about other field then just denied poliely
#             4. Do not invent or assume details that are not in the context unless no context is provided.
#             5. Be clear, concise, and professional in all responses.
#             *System Instructions*  
#             You are a helpful assistant. Follow these rules:  
#             1. **Context Priority**:  
#             - If context is provided, use it strictly.  
#             - If context is missing/insufficient, use your knowledge only on architecture property, civil engineering, and construction (AEC) nd basic greeting topics.  
#             2. **Formatting**:  
#             - Use `\n\n` for line breaks.  
#             - Wrap **small headings** in double asterisks (`**like this**`).  
#             - Wrap *large headings* in single asterisks (`*like this*`).  
#             3. **Style**:  

#                     '''}
#                           ]

#     for turn in chat_history[-8:]:
#         messages.append({"role": "user", "content": turn["user"]})
#         messages.append({"role": "assistant", "content": turn["bot"]})

#     prompt = f"""Use the following context to answer the user's question.\n\nContext:\n{context}\nQuestion: {user_input}"""
#     messages.append({"role": "user", "content": prompt})


#     # 3. Call Groq LLM
#     response = groq_client.chat.completions.create(
#         model="mistral-saba-24b",
#         messages=messages,
#         temperature=0.5,
#         max_tokens=1024,
#         top_p=1,
#         stream=False
#     )

#     bot_response = response.choices[0].message.content

#     # 4. Update memory
#     chat_history.append({"user": user_input, "bot": bot_response})

#     return {"response": bot_response}

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from groq import Groq
from typing import Dict, List
import uuid

# Load .env
load_dotenv()

# Global objects (initialized in lifespan)
model = None
chroma_client = None
collection = None
groq_client = None
sessions: Dict[str, List] = {}  # Session-based chat history

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources and clean up"""
    global model, chroma_client, collection, groq_client
    
    try:
        # Initialize model
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Initialize ChromaDB
        chroma_client = chromadb.PersistentClient(
            path="vector_db/chroma_store",
            settings=Settings(allow_reset=True)
        )
        collection = chroma_client.get_collection(name="architect_knowledge")
        
        # Initialize Groq client
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        yield
        
    except Exception as e:
        print(f"Initialization error: {str(e)}")
        raise
    finally:
        # Cleanup resources
        if chroma_client:
            chroma_client.reset()

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the Chat API"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message field is required")
        
        # Generate or validate session ID
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in sessions:
            sessions[session_id] = []
        
        # 1. Embed and retrieve from Chroma
        query_vector = model.encode(request.message).tolist()
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=3
        )
        context = "\n\n".join(results["documents"][0]) if results["documents"] else ""

        # 2. Build prompt with session history
        messages = [{
            "role": "system",
            "content": "..."  # (your system prompt here)
        }]

        for turn in sessions[session_id][-8:]:  # Keep last 4 exchanges
            messages.extend([
                {"role": "user", "content": turn["user"]},
                {"role": "assistant", "content": turn["bot"]}
            ])

        messages.append({
            "role": "user", 
            "content": f"Context:\n{context}\nQuestion: {request.message}"
        })

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
        
        # 4. Update session
        sessions[session_id].append({
            "user": request.message,
            "bot": bot_response
        })

        return {
            "response": bot_response,
            "session_id": session_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))