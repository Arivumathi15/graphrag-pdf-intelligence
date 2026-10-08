import json
import faiss
import numpy as np
from pathlib import Path

from src.vector.embeddings import EmbeddingModel


CHUNKS_PATH = Path("data/processed/pdf_chunks.json")
INDEX_PATH = Path("data/processed/pdf_faiss.index")
METADATA_PATH = Path("data/processed/pdf_faiss_metadata.json")


def build_pdf_index():
    print("=" * 70)
    print("BUILDING PDF FAISS INDEX")
    print("=" * 70)

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"{CHUNKS_PATH} not found. Run PDF ingestion first."
        )

    with CHUNKS_PATH.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    if not chunks:
        raise ValueError("No PDF chunks found.")

    print(f"Loaded chunks: {len(chunks)}")

    texts = [chunk["text"] for chunk in chunks]

    print("\nLoading embedding model...")
    embedding_model = EmbeddingModel()

    print("Generating embeddings...")
    embeddings = embedding_model.encode_documents(texts)

    embeddings = np.asarray(embeddings, dtype="float32")

    dimension = embeddings.shape[1]

    print(f"Embedding dimension: {dimension}")

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(INDEX_PATH))

    with METADATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("PDF FAISS INDEX CREATED")
    print("=" * 70)
    print(f"Vectors indexed: {index.ntotal}")
    print(f"FAISS index: {INDEX_PATH}")
    print(f"Metadata: {METADATA_PATH}")


if __name__ == "__main__":
    build_pdf_index()