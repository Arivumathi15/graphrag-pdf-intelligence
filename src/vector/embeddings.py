from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingModel:

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        print(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(
            model_name
        )

    def encode_documents(
        self,
        texts: list[str]
    ) -> np.ndarray:

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True, 
            show_progress_bar=True
        )

        return embeddings.astype("float32")

    def encode_query(
        self,
        query: str
    ) -> np.ndarray:

        embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.astype("float32")