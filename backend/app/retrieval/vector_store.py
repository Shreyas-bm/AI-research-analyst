"""Local ChromaDB Vector Store Manager"""
import os
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from typing import List, Optional, Dict, Any
from backend.app.config import settings
from backend.app.retrieval.embeddings import LocalEmbeddingService
from backend.app.retrieval.parser import DocumentChunk
from backend.app.schemas.evidence import EvidenceItem, SourceType, SourceMetadata

class CustomChromaEmbeddingFunction(EmbeddingFunction[Documents]):
    """Passes through embeddings to our LocalEmbeddingService."""
    def __init__(self, service: LocalEmbeddingService):
        self.service = service

    def __call__(self, input: Documents) -> Embeddings:
        return self.service.embed_documents(input)

    def name(self) -> str:
        return "custom_local_embedding_function"

    def get_config(self) -> Dict[str, Any]:
        return {"name": self.name()}

class ChromaVectorStore:
    def __init__(
        self,
        collection_name: str = "decisionlens_docs",
        persist_directory: Optional[str] = None,
        embedding_service: Optional[LocalEmbeddingService] = None
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIR
        self.embedder = embedding_service or LocalEmbeddingService()
        self.chroma_ef = CustomChromaEmbeddingFunction(self.embedder)

        # Initialize ChromaDB client
        if self.persist_directory and self.persist_directory != ":memory:":
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
        else:
            self.client = chromadb.EphemeralClient()

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.chroma_ef,
            metadata={"description": "DecisionLens Document Chunks"}
        )

    def add_chunks(self, chunks: List[DocumentChunk]):
        """Embed and index document chunks into ChromaDB."""
        if not chunks:
            return

        ids = [c.chunk_id for c in chunks]
        texts = [c.content for c in chunks]
        embeddings = self.embedder.embed_documents(texts)
        metadatas = [
            {
                "document_id": c.document_id,
                "filename": c.filename,
                "page_number": c.page_number or 1,
                "section": c.section or "General",
                "char_count": c.char_count
            }
            for c in chunks
        ]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[EvidenceItem]:
        """Perform semantic similarity search and return EvidenceItem list."""
        if self.collection.count() == 0:
            return []

        query_vec = self.embedder.embed_query(query_text)
        
        query_kwargs: Dict[str, Any] = {
            "query_embeddings": [query_vec],
            "n_results": min(top_k, max(1, self.collection.count())),
        }
        if where_filter:
            query_kwargs["where"] = where_filter

        results = self.collection.query(**query_kwargs)

        evidence_items: List[EvidenceItem] = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else [{}] * len(docs)
            distances = results.get("distances", [[0.0] * len(docs)])[0]

            for doc_text, meta, dist in zip(docs, metas, distances):
                score = max(0.0, min(1.0, 1.0 - (dist if dist is not None else 0.2)))
                filename = meta.get("filename", "Internal Document") if meta else "Internal Document"
                page = meta.get("page_number", 1) if meta else 1
                section = meta.get("section", "Section") if meta else "Section"
                doc_id = meta.get("document_id", "doc") if meta else "doc"

                evidence_items.append(EvidenceItem(
                    id=f"src-doc-{str(doc_id)[:6]}-{page}",
                    source_type=SourceType.DOCUMENT,
                    title=f"{filename} (p. {page} - {section})",
                    url=filename,
                    excerpt=doc_text,
                    metadata=SourceMetadata(
                        page_number=page,
                        section=section,
                        document_id=doc_id,
                        query_used=query_text
                    ),
                    credibility_score=0.95
                ))

        return evidence_items

    def count(self) -> int:
        return self.collection.count()
