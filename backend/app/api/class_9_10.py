import os
from services import class_9_10
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from models.schemas import QueryRequest, QueryResponse, DocumentUploadResponse, DocumentListResponse


router = APIRouter()

@router.on_event('startup')
async def startup_event():
    try:
        await class_9_10.startup_event()
    except Exception as e:
        print(str(e))


@router.post('/query', response_model=QueryResponse)
async def query(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        return await class_9_10.query_documents(request=request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
