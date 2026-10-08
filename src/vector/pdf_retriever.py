import json
from pathlib import Path

import faiss
import numpy as np

from src.vector.embeddings import EmbeddingModel


INDEX_PATH = Path("data/processed/pdf_faiss.index")
METADATA_PATH = Path("data/processed/pdf_faiss_metadata.json")


class PDFRetriever:

    def __init__(self):
        if not INDEX_PATH.exists():
            raise FileNotFoundError(
                "PDF FAISS index not found. Run build_pdf_index first."
            )

        if not METADATA_PATH.exists():
            raise FileNotFoundError(
                "PDF FAISS metadata not found."
            )

        self.index = faiss.read_index(str(INDEX_PATH))

        with METADATA_PATH.open("r", encoding="utf-8") as file:
            self.metadata = json.load(file)

        self.embedding_model = EmbeddingModel()

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