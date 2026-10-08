import json
from pathlib import Path

from loader import load_text_documents
from cleaner import clean_text
from chunker import chunk_document


RAW_DATA_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/processed/chunks.json")


def main():

    documents = load_text_documents(RAW_DATA_DIR)

    all_chunks = []

    print(f"Loaded {len(documents)} documents.")

    for document in documents:

        document["text"] = clean_text(
            document["text"]
        )

        chunks = chunk_document(
            document,
            max_words=200
        )

        all_chunks.extend(chunks)

        print(
            f"{document['source']}: "
            f"{len(chunks)} chunk(s)"
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()