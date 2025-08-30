import numpy as np
from flask import current_app
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    _model_instance = None

    def __init__(self):
        if EmbeddingService._model_instance is None:
            model_name = current_app.config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            EmbeddingService._model_instance = SentenceTransformer(model_name)
        self.model = EmbeddingService._model_instance

    def generate_character_embedding(self, quotes: list[str]) -> np.ndarray:
        """Create a character's embedding by averaging their quote embeddings."""
        if not quotes:
            return np.zeros(current_app.config.get("EMBEDDING_DIMENSION", 384))

        quote_embeddings = self.model.encode(quotes, convert_to_numpy=True)
        # np.mean returns a float64, which is compatible with pgvector
        return np.mean(quote_embeddings, axis=0)

    def generate_quote_embedding(self, quote: str) -> np.ndarray:
        """Generate an embedding for a single quote."""
        return self.model.encode([quote], convert_to_numpy=True)[0]
