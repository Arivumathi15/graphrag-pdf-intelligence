import json
import faiss
import numpy as np
from pathlib import Path

from src.vector.embeddings import EmbeddingModel


CHUNKS_PATH = Path("data/processed/pdf_chunks.json")
INDEX_PATH = Path("data/processed/pdf_faiss.index")
METADATA_PATH = Path("data/processed/pdf_faiss_metadata.json")


def build_pdf_index(
    chunks_path=CHUNKS_PATH,
    index_path=INDEX_PATH,
    metadata_path=METADATA_PATH,
    embedding_model=None,
):
    print("=" * 70)
    print("BUILDING PDF FAISS INDEX")
    print("=" * 70)

    if not chunks_path.exists():
        raise FileNotFoundError(
            f"{chunks_path} not found. Run PDF ingestion first."
        )

    with chunks_path.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    if not chunks:
        raise ValueError("No PDF chunks found.")

    print(f"Loaded chunks: {len(chunks)}")

    texts = [chunk["text"] for chunk in chunks]

    print("\nLoading embedding model...")
    embedding_model = embedding_model or EmbeddingModel()

    print("Generating embeddings...")
    embeddings = embedding_model.encode_documents(texts)

    embeddings = np.asarray(embeddings, dtype="float32")

    dimension = embeddings.shape[1]

    print(f"Embedding dimension: {dimension}")

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    index_path.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(index_path))

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("PDF FAISS INDEX CREATED")
    print("=" * 70)
    print(f"Vectors indexed: {index.ntotal}")
    print(f"FAISS index: {index_path}")
    print(f"Metadata: {metadata_path}")


if __name__ == "__main__":
    build_pdf_index()