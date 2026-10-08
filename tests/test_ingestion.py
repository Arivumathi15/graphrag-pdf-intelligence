import json
from pathlib import Path


CHUNKS_FILE = Path("data/processed/chunks.json")


def test_chunks_exist():

    assert CHUNKS_FILE.exists()

    with CHUNKS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    assert len(chunks) > 0


def test_required_fields():

    with CHUNKS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    required_fields = {
        "chunk_id",
        "document_id",
        "source",
        "chunk_index",
        "text",
        "word_count",
    }

    for chunk in chunks:

        assert required_fields.issubset(
            chunk.keys()
        )


def test_unique_chunk_ids():

    with CHUNKS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    chunk_ids = [
        chunk["chunk_id"]
        for chunk in chunks
    ]

    assert len(chunk_ids) == len(set(chunk_ids))