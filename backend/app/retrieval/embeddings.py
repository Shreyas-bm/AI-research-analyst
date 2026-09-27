"""Local Embeddings Service with deterministic vectorizer fallback"""
import hashlib
import math
from typing import List, Optional

class LocalEmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384, use_transformer: bool = False):
        self.model_name = model_name
        self.dimension = dimension
        self.use_transformer = use_transformer
        self._st_model = None

    def _get_st_model(self):
        if not self.use_transformer:
            return None
        if self._st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer(self.model_name)
            except Exception:
                self._st_model = False
        return self._st_model

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding vector for a single query text."""
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a list of document strings."""
        if self.use_transformer:
            st = self._get_st_model()
            if st and st is not False:
                try:
                    embeddings = st.encode(texts, normalize_embeddings=True)
                    return [e.tolist() for e in embeddings]
                except Exception:
                    pass
        
        # Deterministic fast fallback vectorizer (384 dimensions, normalized)
        results = []
        for text in texts:
            vec = [0.0] * self.dimension
            tokens = text.lower().split()
            if not tokens:
                tokens = ["empty"]
            for token in tokens:
                h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dimension
                val = ((h >> 8) % 1000) / 1000.0 - 0.5
                vec[idx] += val
            
            # L2 normalize
            norm = math.sqrt(sum(x * x for x in vec))
            if norm > 0:
                vec = [x / norm for x in vec]
            else:
                vec[0] = 1.0
            results.append(vec)
        return results

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two normalized vectors."""
        if len(vec_a) != len(vec_b):
            raise ValueError(f"Vector dimensions do not match: {len(vec_a)} vs {len(vec_b)}")
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a, b in zip(vec_a, vec_b)))
        norm_b = math.sqrt(sum(b * b for a, b in zip(vec_a, vec_b)))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)
