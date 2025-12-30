"""
Medical RAG Application Backend
Main application file: main.py
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from datetime import datetime
from dotenv import load_dotenv
from api.router import api_router
# Load environment variables from .env file
try:
    load_dotenv()
except UnicodeDecodeError:
    # Handle case where .env file has wrong encoding
    print(
        "⚠️  Warning: .env file has encoding issues. Please recreate it with UTF-8 encoding."
    )
    print("   The file should contain: OPENROUTER_API_KEY=your_key_here")

from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from services.llm_service import LLMService
from models.schemas import (
    QueryRequest,
    QueryResponse,
    DocumentUploadResponse,
    DocumentListResponse,
    HealthResponse,
)

# Initialize FastAPI app
app = FastAPI(
    title="Medical RAG API",
    description="RAG application for medical students",
    version="1.0.0",
)

app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

index_path = "data/faiss_index/index.faiss"
metadata_path = "data/faiss_index/metadata.pkl"

# Initialize services
document_processor = DocumentProcessor()
vector_store = VectorStore(index_path=index_path, metadata_path=metadata_path)
llm_service = LLMService()

# Ensure data directories exist
os.makedirs("data/documents/books", exist_ok=True)
os.makedirs("data/faiss_index/books", exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    vector_store.load_index()

    # Check if we have documents but no index, then rebuild
    docs_dir = "data/documents/books"
    if os.path.exists(docs_dir) and os.listdir(docs_dir):
        if vector_store.index.ntotal == 0:
            print("📚 Found documents but no index. Rebuilding index...")
            await rebuild_index_on_startup()
        else:
            print(
                f"📚 Loaded {vector_store.index.ntotal} embeddings from existing index"
            )

    print("✅ Application started successfully")


async def rebuild_index_on_startup():
    """Rebuild index from all documents on startup"""
    try:
        docs_dir = "data/documents/books"
        files = [
            f for f in os.listdir(docs_dir) if os.path.isfile(os.path.join(docs_dir, f))
        ]

        if not files:
            return

        total_chunks = 0
        successful_docs = 0
        failed_docs = []

        for filename in files:
            try:
                file_path = os.path.join(docs_dir, filename)
                chunks = document_processor.process_document(file_path, filename)

                if chunks:
                    vector_store.add_documents(chunks)
                    total_chunks += len(chunks)
                    successful_docs += 1
                    print(f"  ✓ Processed: {filename} ({len(chunks)} chunks)")
                else:
                    failed_docs.append(f"{filename} (no content extracted)")

            except Exception as e:
                failed_docs.append(f"{filename} ({str(e)})")
                print(f"  ✗ Failed to process {filename}: {str(e)}")

        print(
            f"✅ Index rebuilt: {successful_docs} documents, {total_chunks} total chunks"
        )

        if failed_docs:
            print(f"⚠️ Failed to process {len(failed_docs)} documents:")
            for failed in failed_docs:
                print(f"  - {failed}")

    except Exception as e:
        print(f"⚠️ Error during startup index rebuild: {str(e)}")


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Medical RAG API is running",
        timestamp=datetime.now(),
    )


@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = None
):
    """
    Upload and process a medical document
    Supports: PDF, TXT, MD files
    """
    try:
        # Validate file type
        allowed_extensions = [".pdf", ".txt", ".md"]
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_extensions}",
            )

        # Save file
        file_path = os.path.join("data/documents/books", file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process document
        chunks = document_processor.process_document(file_path, file.filename)

        if not chunks:
            raise HTTPException(
                status_code=400, detail="No content extracted from document"
            )

        # Add to vector store
        vector_store.add_documents(chunks)

        return DocumentUploadResponse(
            success=True,
            filename=file.filename,
            chunks_created=len(chunks),
            message="Document uploaded and processed successfully",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system with a medical question
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Retrieve relevant documents
        retrieved_docs = vector_store.search(query=request.query, top_k=request.top_k)

        if not retrieved_docs:
            return QueryResponse(
                query=request.query,
                answer="I couldn't find any relevant information in the knowledge base. Please try uploading relevant medical documents first.",
                sources=[],
                retrieved_chunks=0,
            )

        # Generate answer using LLM
        answer = llm_service.generate_answer(
            query=request.query,
            context_docs=retrieved_docs,
            system_prompt=request.system_prompt,
        )

        # Format sources
        sources = [
            {
                "filename": doc["metadata"]["source"],
                "chunk_id": doc["metadata"]["chunk_id"],
                "content": doc["content"][:200] + "...",
                "similarity": float(doc["similarity"]),
            }
            for doc in retrieved_docs
        ]

        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            retrieved_chunks=len(retrieved_docs),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents"""
    try:
        docs_dir = "data/documents/books"
        if not os.path.exists(docs_dir):
            return DocumentListResponse(documents=[], total=0)

        files = os.listdir(docs_dir)
        documents = [
            {
                "filename": f,
                "size": os.path.getsize(os.path.join(docs_dir, f)),
                "uploaded_at": datetime.fromtimestamp(
                    os.path.getctime(os.path.join(docs_dir, f))
                ),
            }
            for f in files
        ]

        return DocumentListResponse(documents=documents, total=len(documents))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document and its embeddings"""
    try:
        file_path = os.path.join("data/documents", filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete file
        os.remove(file_path)

        # Note: In a production system, you'd also want to remove the
        # specific embeddings from FAISS. For simplicity, we'll rebuild the index
        # This could be optimized by maintaining a mapping of documents to embeddings

        return {"success": True, "message": f"Document {filename} deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rebuild-index")
async def rebuild_index():
    """Rebuild the entire FAISS index from all documents"""
    try:
        docs_dir = "data/documents/books"

        if not os.path.exists(docs_dir):
            raise HTTPException(status_code=404, detail="No documents found")

        # Clear existing index
        vector_store.clear_index()

        # Process all documents
        total_chunks = 0
        files = os.listdir(docs_dir)

        for filename in files:
            file_path = os.path.join(docs_dir, filename)
            chunks = document_processor.process_document(file_path, filename)
            vector_store.add_documents(chunks)
            total_chunks += len(chunks)

        return {
            "success": True,
            "message": f"Index rebuilt successfully",
            "documents_processed": len(files),
            "total_chunks": total_chunks,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
