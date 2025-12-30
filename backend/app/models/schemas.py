"""
Pydantic models for request/response validation
File: models/schemas.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for querying the RAG system"""

    query: str = Field(..., description="The medical question or query")
    top_k: int = Field(
        default=5, ge=1, le=20, description="Number of documents to retrieve"
    )
    system_prompt: Optional[str] = Field(
        default=None, description="Custom system prompt for the LLM"
    )


class SourceDocument(BaseModel):
    """Source document information"""

    filename: str
    chunk_id: int
    content: str
    similarity: float


class QueryResponse(BaseModel):
    """Response model for query results"""

    query: str
    answer: str
    sources: List[Dict[str, Any]]
    retrieved_chunks: int


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""

    success: bool
    filename: str
    chunks_created: int
    message: str


class DocumentInfo(BaseModel):
    """Information about an uploaded document"""

    filename: str
    size: int
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    """Response model for listing documents"""

    documents: List[Dict[str, Any]]
    total: int


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    message: str
    timestamp: datetime
