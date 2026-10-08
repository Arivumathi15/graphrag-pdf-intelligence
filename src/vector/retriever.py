from pathlib import Path

from embeddings import EmbeddingModel
from vector_store import VectorStore


INDEX_FILE = Path(
    "data/processed/faiss.index"
)

METADATA_FILE = Path(
    "data/processed/faiss_metadata.json"
)


class VectorRetriever:

    def __init__(self):

        self.embedding_model = (
            EmbeddingModel()
        )

        self.vector_store = (
            VectorStore.load(
                INDEX_FILE,
                METADATA_FILE
            )
        )

    def retrieve(
        self,
        query: str,
        k: int = 3
    ) -> list[dict]:

        query_embedding = (
            self.embedding_model.encode_query(
                query
            )
        )

        return self.vector_store.search(
            query_embedding,
            k=k
        )