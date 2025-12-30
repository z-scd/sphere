import os
from services import notebook
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from models.schemas import QueryRequest, QueryResponse, DocumentUploadResponse, DocumentListResponse


router = APIRouter()

@router.on_event('startup')
async def startup_event():
    try:
        await notebook.startup_event()
    except Exception as e:
        print(str(e))


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload(
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

        return await notebook.upload_document(file=file)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/query', response_model=QueryResponse)
async def query(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        return await notebook.query_documents(request=request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/documents', response_model=DocumentListResponse)
async def list_document():
    try:
        return notebook.list_documents()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/documents/{filename}')
async def delete_documents(filename: str):
    """Delete a document and its embeddings"""
    try:
        return await notebook.delete_document(filename=file_name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/rebuild-index')
async def rebuild_index():
    """Rebuild the entire FAISS index from all the uploaded documents"""
    try:
        return notebook.rebuild_index()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
