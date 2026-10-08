import json
from pathlib import Path

from embeddings import EmbeddingModel
from vector_store import VectorStore


CHUNKS_FILE = Path(
    "data/processed/chunks.json"
)

INDEX_FILE = Path(
    "data/processed/faiss.index"
)

METADATA_FILE = Path(
    "data/processed/faiss_metadata.json"
)


def main():

    with CHUNKS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    print(
        f"Loaded {len(chunks)} chunks."
    )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embedding_model = EmbeddingModel()

    embeddings = (
        embedding_model.encode_documents(
            texts
        )
    )

    print(
        f"Embedding shape: "
        f"{embeddings.shape}"
    )

    dimension = embeddings.shape[1]

    vector_store = VectorStore(
        dimension=dimension
    )

    vector_store.add(
        embeddings,
        chunks
    )

    vector_store.save(
        INDEX_FILE,
        METADATA_FILE
    )

    print(
        f"FAISS vectors: "
        f"{vector_store.index.ntotal}"
    )

    print(
        f"Saved index to: {INDEX_FILE}"
    )


if __name__ == "__main__":
    main()