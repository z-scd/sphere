import os
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
from utils.custom_errors import ExtractionException, EmptyInputException
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


# Ensure data directories exist
# os.makedirs("data/documents/CLASS_9_10", exist_ok=True)
os.makedirs("data/faiss_index/CLASS_9_10", exist_ok=True)


index_path = "data/faiss_index/CLASS_9_10/index.faiss"
metadata_path = "data/faiss_index/CLASS_9_10/metadata.pkl"


# Initialize services
document_processor = DocumentProcessor()
vector_store = VectorStore(index_path=index_path, metadata_path=metadata_path)
llm_service = LLMService()


async def startup_event():
    """Initialize services on startup"""
    vector_store.load_index()

    # Check if we have documents but no index, then rebuild
    docs_dir = "data/documents/books/CLASS_9_10"
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
        docs_dir = "data/documents/books/CLASS_9_10"
        files = [
            f for f in os.listdir(docs_dir) if os.path.isfile(os.path.join(docs_dir, f))
        ]

        if not files:
            return
        print(files)
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


async def query_documents(request: QueryRequest):
    """
    Query the RAG system with a medical question
    """
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