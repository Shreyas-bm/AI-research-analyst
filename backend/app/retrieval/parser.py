"""Document Ingestion, Text Extraction, and Chunking Pipeline"""
import os
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    content: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    char_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentParser:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from file returning a list of page/section dicts:
        [{'text': str, 'page_number': int, 'section': str}]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext in [".md", ".markdown"]:
            return self._extract_markdown(file_path)
        elif ext in [".txt", ".log", ".json"]:
            return self._extract_text(file_path)
        else:
            return self._extract_text(file_path)

    def _extract_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        import fitz  # PyMuPDF
        pages = []
        doc = fitz.open(file_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text("text").strip()
            if text:
                pages.append({
                    "text": text,
                    "page_number": page_idx + 1,
                    "section": f"Page {page_idx + 1}"
                })
        doc.close()
        return pages

    def _extract_markdown(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        sections = []
        # Split by header (#, ##, ###)
        header_pattern = re.compile(r"^(#{1,3}\s+.+)$", re.MULTILINE)
        parts = header_pattern.split(content)

        current_header = "Introduction"
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if header_pattern.match(part):
                current_header = part.lstrip("#").strip()
            else:
                sections.append({
                    "text": part,
                    "page_number": 1,
                    "section": current_header
                })

        if not sections:
            sections.append({"text": content, "page_number": 1, "section": "Document"})
        return sections

    def _extract_text(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read().strip()
        return [{"text": content, "page_number": 1, "section": "Document"}]

    def chunk_document(self, document_id: str, filename: str, file_path: str) -> List[DocumentChunk]:
        """Parse file and split into overlapping chunks with rich metadata."""
        extracted_pages = self.extract_text_from_file(file_path)
        chunks: List[DocumentChunk] = []

        chunk_counter = 0
        for page_data in extracted_pages:
            text = page_data["text"]
            page_num = page_data["page_number"]
            section = page_data["section"]

            # Sliding window chunking
            start = 0
            text_len = len(text)

            while start < text_len:
                end = min(start + self.chunk_size, text_len)
                chunk_text = text[start:end].strip()

                if len(chunk_text) > 30:  # Ignore tiny noise chunks
                    chunk_counter += 1
                    chunks.append(DocumentChunk(
                        chunk_id=f"{document_id}_chk_{chunk_counter}",
                        document_id=document_id,
                        filename=filename,
                        content=chunk_text,
                        page_number=page_num,
                        section=section,
                        char_count=len(chunk_text),
                        metadata={
                            "document_id": document_id,
                            "filename": filename,
                            "page": page_num,
                            "section": section,
                            "offset_start": start,
                            "offset_end": end
                        }
                    ))

                if end >= text_len:
                    break
                start += (self.chunk_size - self.chunk_overlap)

        return chunks
