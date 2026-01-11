from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import time
import sqlite3
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

# ChromaDB setup (in-memory for cloud deployment like Render)
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="code_reviews")

# Retrieval setup for knowledge base
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
knowledge_vectorstore = Chroma(
    client=chroma_client,
    collection_name="knowledge_base",
    embedding_function=embeddings,
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

app = FastAPI(title="ReviewMate AI Backend", version="1.0.0")

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
    diff_id = f"diff_{hash(request.diff)}"
    try:
        collection.add(
            documents=[request.diff],
            metadatas=[{"pr_url": request.pr_url or "", "timestamp": str(time.time())}],
            ids=[diff_id]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store in vector DB: {str(e)}")

    # Store metadata in SQLite
    try:
        conn = sqlite3.connect("reviews.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (id, pr_url, status, timestamp) VALUES (?, ?, ?, ?)",
                       (diff_id, request.pr_url or "", "analyzed", time.time()))
        conn.commit()
        conn.close()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)