import json
from pathlib import Path

import faiss
import numpy as np

from src.vector.embeddings import EmbeddingModel


INDEX_PATH = Path("data/processed/pdf_faiss.index")
METADATA_PATH = Path("data/processed/pdf_faiss_metadata.json")


class PDFRetriever:

    def __init__(
        self,
        index_path=INDEX_PATH,
        metadata_path=METADATA_PATH,
        embedding_model=None,
    ):
        if not index_path.exists():
            raise FileNotFoundError(
                "PDF FAISS index not found. Run build_pdf_index first."
            )

        if not metadata_path.exists():
            raise FileNotFoundError(
                "PDF FAISS metadata not found."
            )

        self.index = faiss.read_index(str(index_path))

        with metadata_path.open("r", encoding="utf-8") as file:
            self.metadata = json.load(file)

        self.embedding_model = (
            embedding_model or EmbeddingModel()
        )

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:

        query_embedding = self.embedding_model.encode_documents([query])
        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index_id in zip(scores[0], indices[0]):

            if index_id == -1:
                continue

            chunk = self.metadata[index_id].copy()

            chunk["score"] = float(score)

            results.append(chunk)

        return results