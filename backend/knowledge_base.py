from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

# ChromaDB setup for knowledge base (in-memory)
chroma_client = chromadb.Client()
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(
    client=chroma_client,
    collection_name="knowledge_base",
    embedding_function=embeddings,
)

# Sample coding standards and best practices
knowledge_docs = [
    Document(
        page_content="Clean Code Principle: Functions should be small and do one thing. A function should not exceed 20 lines.",
        metadata={"source": "Clean Code", "topic": "functions"}
    ),
    Document(
        page_content="SOLID Principle: Single Responsibility - A class should have only one reason to change.",
        metadata={"source": "SOLID", "topic": "classes"}
    ),
    Document(
        page_content="Error Handling: Use try-except blocks and avoid bare except clauses. Log errors appropriately.",
        metadata={"source": "Best Practices", "topic": "error_handling"}
    ),
    Document(
        page_content="Code Review: Check for TODO comments as technical debt. Ensure variables are meaningfully named.",
        metadata={"source": "Code Review Guidelines", "topic": "naming"}
    ),
    Document(
        page_content="Security: Avoid hardcoding secrets. Use environment variables for API keys and sensitive data.",
        metadata={"source": "OWASP", "topic": "security"}
    ),
    Document(
        page_content="Performance: Avoid nested loops where possible. Use efficient data structures like sets for lookups.",
        metadata={"source": "Performance Best Practices", "topic": "performance"}
    ),
]

def build_knowledge_base():
    """Add knowledge documents to ChromaDB if not already present."""
    if vectorstore._collection.count() == 0:  # Check if empty
        vectorstore.add_documents(knowledge_docs)
        print("Knowledge base populated with sample coding standards.")
    else:
        print("Knowledge base already exists.")

if __name__ == "__main__":
    build_knowledge_base()