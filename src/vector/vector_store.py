import json
from pathlib import Path

import faiss
import numpy as np


class VectorStore:

    def __init__(
        self,
        dimension: int
    ):
        self.dimension = dimension

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.metadata = []

    def add(
        self,
        embeddings: np.ndarray,
        chunks: list[dict]
    ):

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Number of embeddings must match "
                "number of chunks."
            )

        self.index.add(embeddings)

        self.metadata.extend(chunks)

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 3
    ) -> list[dict]:

        k = min(
            k,
            self.index.ntotal
        )

        scores, indices = self.index.search(
            query_embedding,
            k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            chunk = self.metadata[index].copy()

            chunk["score"] = float(score)

            results.append(chunk)

        return results

    def save(
        self,
        index_path: Path,
        metadata_path: Path
    ):

        index_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(index_path)
        )

        with metadata_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.metadata,
                file,
                indent=2,
                ensure_ascii=False
            )

    @classmethod
    def load(
        cls,
        index_path: Path,
        metadata_path: Path
    ):

        index = faiss.read_index(
            str(index_path)
        )

        store = cls(
            dimension=index.d
        )

        store.index = index

        with metadata_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            store.metadata = json.load(file)

        return store