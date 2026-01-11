from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import time
import sqlite3
from functools import lru_cache
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from backend.agents import run_agent_workflow

# Load environment variables
load_dotenv()

app = FastAPI(title="ReviewMate AI Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ChromaDB setup (using default local embeddings - all-MiniLM-L6-v2, free)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="code_reviews")

# Retrieval setup for knowledge base
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
knowledge_vectorstore = Chroma(
    client=chroma_client,
    collection_name="knowledge_base",
    embedding_function=embeddings,
)
retriever = knowledge_vectorstore.as_retriever(search_kwargs={"k": 3})

# Groq LLM setup
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY not set in environment")
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=groq_api_key)

# RAG prompt and chain
prompt = ChatPromptTemplate.from_template("""
You are a code review assistant. Based on the following context about coding best practices:

{context}

Analyze this code diff and provide constructive feedback, suggestions for improvement, and any violations of best practices:

Diff: {diff}

Keep your response concise and actionable.
""")

rag_chain = (
    {"context": retriever, "diff": RunnablePassthrough()}
    | prompt
    | llm
)
# For future feedback loop, store agent outputs

# SQLite setup
def init_db():
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY,
            pr_url TEXT,
            status TEXT,
            timestamp REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class AnalyzeDiffRequest(BaseModel):
    diff: str  # Code diff content
    pr_url: Optional[str] = None  # Optional PR URL

class AnalyzeDiffResponse(BaseModel):
    message: str
    status: str

@app.post("/analyze-diff", response_model=AnalyzeDiffResponse)
async def analyze_diff(request: AnalyzeDiffRequest):
    """
    Endpoint to analyze a code diff.
    Stores diff in ChromaDB with basic embeddings.
    """
    if not request.diff.strip():
        raise HTTPException(status_code=400, detail="Diff content cannot be empty")

    # Store in ChromaDB
    diff_id = f"diff_{hash(request.diff)}_{int(time.time())}"  # Make unique with timestamp
    try:
        collection.add(
            documents=[request.diff],
            metadatas=[{"pr_url": request.pr_url or "", "timestamp": str(time.time())}],
            ids=[diff_id]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store in vector DB: {str(e)}")

    # Store metadata in SQLite with retry for lock
    try:
        conn = sqlite3.connect("reviews.db", timeout=10)  # Add timeout
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (id, pr_url, status, timestamp) VALUES (?, ?, ?, ?)",
                       (diff_id, request.pr_url or "", "analyzed", time.time()))
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            # Log and continue without failing
            print(f"Database locked, skipping metadata storage: {e}")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to store metadata: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store metadata: {str(e)}")

    # Generate AI suggestions using agent workflow
    try:
        suggestions = run_agent_workflow(request.diff)
        # Store agent outputs for feedback loop
        collection.add(
            documents=[suggestions],
            metadatas=[{"diff_id": diff_id, "type": "agent_feedback", "timestamp": str(time.time())}],
            ids=[f"feedback_{diff_id}"]
        )
    except Exception as e:
        suggestions = f"Agent workflow failed: {str(e)}"

    return AnalyzeDiffResponse(
        message=f"Diff analyzed. Suggestions: {suggestions}",
        status="success"
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/feedback")
async def submit_feedback(feedback: dict):
    """Accept feedback for model improvement"""
    # Simple logging; in production, store and use for fine-tuning
    print(f"Feedback received: {feedback}")
    return {"message": "Feedback submitted"}

@app.get("/metrics")
async def get_metrics():
    """Get basic metrics on reviews"""
    try:
        conn = sqlite3.connect("reviews.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reviews")
        count = cursor.fetchone()[0]
        conn.close()
        return {"total_reviews": count}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)