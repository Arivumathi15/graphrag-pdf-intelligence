from pathlib import Path
import pymupdf


def load_pdf_document(file_path: Path) -> list[dict]:
    """
    Extract text from a PDF page by page.

    Returns one document record per page so that
    page-level provenance can be preserved.
    """

    pages = []

    pdf = pymupdf.open(file_path)

    try:
        for page_index, page in enumerate(pdf):

            text = page.get_text("text")

            # Ignore completely empty pages
            if not text or not text.strip():
                continue

            pages.append(
                {
                    "document_id": file_path.stem,
                    "source": file_path.name,
                    "page": page_index + 1,
                    "text": text,
                }
            )

    finally:
        pdf.close()

    return pages


def load_pdf_documents(
    data_dir: Path
) -> list[dict]:
    """
    Load every PDF from a directory.

    Each returned item represents one PDF page.
    """

    documents = []

    pdf_files = sorted(data_dir.glob("*.pdf"))

    for file_path in pdf_files:

        print(
            f"Loading PDF: {file_path.name}"
        )

        pages = load_pdf_document(
            file_path
        )

        documents.extend(pages)

        print(
            f"  Extracted {len(pages)} text pages"
        )

    return documents