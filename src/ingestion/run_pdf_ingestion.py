import json
from pathlib import Path

from src.ingestion.pdf_loader import (
    load_pdf_documents
)
from src.ingestion.cleaner import clean_text
from src.ingestion.chunker import (
    chunk_pdf_page
)


RAW_PDF_DIR = Path(
    "data/pdf_uploads"
)

OUTPUT_PATH = Path(
    "data/processed/pdf_chunks.json"
)


def run_pdf_ingestion():
    """
    Load PDFs, clean extracted text,
    chunk pages and save the processed chunks.
    """

    print("=" * 70)
    print("PDF INGESTION")
    print("=" * 70)

    RAW_PDF_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    documents = load_pdf_documents(
        RAW_PDF_DIR
    )

    if not documents:
        print(
            "\nNo PDF documents found in:"
        )
        print(
            RAW_PDF_DIR.resolve()
        )
        return

    print(
        f"\nExtracted text pages: "
        f"{len(documents)}"
    )

    all_chunks = []

    for document in documents:

        cleaned_text = clean_text(
            document["text"]
        )

        if not cleaned_text:
            continue

        document["text"] = cleaned_text

        chunks = chunk_pdf_page(
            document,
            max_words=180,
            overlap_words=30
        )

        all_chunks.extend(
            chunks
        )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Generated chunks: "
        f"{len(all_chunks)}"
    )

    print(
        f"Saved to: "
        f"{OUTPUT_PATH}"
    )

    print("\nSample chunks:")

    for chunk in all_chunks[:3]:

        print("\n" + "-" * 70)

        print(
            f"Chunk ID: "
            f"{chunk['chunk_id']}"
        )

        print(
            f"Source: "
            f"{chunk['source']}"
        )

        print(
            f"Page: "
            f"{chunk['page']}"
        )

        print(
            f"Words: "
            f"{chunk['word_count']}"
        )

        preview = chunk["text"][:300]

        print(
            f"Text: {preview}..."
        )

    print(
        "\n✅ PDF ingestion completed."
    )


if __name__ == "__main__":
    run_pdf_ingestion()