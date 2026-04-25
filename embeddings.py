import os
import numpy as np
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from .config import (
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    EMBEDDING_API_KEY,
    EMBEDDING_BASE_URL
)

class EmbeddingTool:
    def __init__(self):
        if EMBEDDING_PROVIDER == "siliconCloud":
            self.embeddings = OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
                api_key=EMBEDDING_API_KEY,
                base_url=EMBEDDING_BASE_URL
            )
        elif EMBEDDING_PROVIDER == "openai":
            self.embeddings = OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
                api_key=EMBEDDING_API_KEY
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {EMBEDDING_PROVIDER}")

    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text string."""
        if not text:
            return None
        # Replace newlines as recommended by OpenAI
        text = text.replace("\n", " ")
        try:
            vector = self.embeddings.embed_query(text)
            return np.array(vector, dtype=np.float32)
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None

    def get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Get embeddings for a batch of text strings."""
        if not texts:
            return []
        cleaned_texts = [t.replace("\n", " ") for t in texts]
        try:
            vectors = self.embeddings.embed_documents(cleaned_texts)
            return [np.array(v, dtype=np.float32) for v in vectors]
        except Exception as e:
            print(f"Error getting batch embeddings: {e}")
            return [None] * len(texts)

def calculate_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    if vec1 is None or vec2 is None:
        return 0.0
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)
