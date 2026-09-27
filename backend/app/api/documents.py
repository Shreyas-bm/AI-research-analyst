"""Document Upload and Vector Indexing Endpoints"""
import os
import uuid
import tempfile
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.database import crud
from backend.app.retrieval.parser import DocumentParser
from backend.app.retrieval.vector_store import ChromaVectorStore

router = APIRouter(prefix="/api/documents", tags=["Document Retrieval"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload PDF, Markdown, or text document, extract text chunks, and index into ChromaDB."""
    filename = file.filename or "uploaded_file.txt"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".md", ".markdown", ".txt", ".json"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {ext}. Allowed: .pdf, .md, .txt")

    doc_id = f"doc-{uuid.uuid4().hex[:8]}"

    # Save to temp file for parsing
    content_bytes = await file.read()
    file_size = len(content_bytes)

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_file.write(content_bytes)
        temp_path = temp_file.name

    try:
        parser = DocumentParser()
        chunks = parser.chunk_document(document_id=doc_id, filename=filename, file_path=temp_path)

        # Index in ChromaDB
        store = ChromaVectorStore()
        store.add_chunks(chunks)

        # Record in DB
        preview = chunks[0].content[:200] if chunks else ""
        doc_record = await crud.create_document_record(
            session=db,
            doc_id=doc_id,
            filename=filename,
            file_type=ext.lstrip("."),
            file_size_bytes=file_size,
            chunk_count=len(chunks),
            extracted_text_preview=preview
        )

        return {
            "document_id": doc_id,
            "filename": filename,
            "file_type": ext.lstrip("."),
            "file_size_bytes": file_size,
            "chunk_count": len(chunks),
            "preview": preview,
            "status": "indexed"
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("")
async def list_documents(db: AsyncSession = Depends(get_db)):
    """List all uploaded and indexed documents."""
    docs = await crud.list_documents(db)
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size_bytes": d.file_size_bytes,
            "chunk_count": d.chunk_count,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "preview": d.extracted_text_preview
        }
        for d in docs
    ]
