def split_into_paragraphs(text: str) -> list[str]:
    """
    Split cleaned text using blank lines as paragraph boundaries.
    """

    return [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]


def chunk_document(
    document: dict,
    max_words: int = 200
) -> list[dict]:
    """
    Create paragraph-aware chunks while trying to preserve
    semantic relationships.
    """

    paragraphs = split_into_paragraphs(document["text"])

    chunks = []
    current_paragraphs = []
    current_word_count = 0

    for paragraph in paragraphs:

        paragraph_word_count = len(paragraph.split())

        if (
            current_paragraphs
            and current_word_count + paragraph_word_count > max_words
        ):
            chunk_text = "\n\n".join(current_paragraphs)

            chunks.append({
                "chunk_id": (
                    f"{document['document_id']}_"
                    f"{len(chunks):03d}"
                ),
                "document_id": document["document_id"],
                "source": document["source"],
                "chunk_index": len(chunks),
                "text": chunk_text,
                "word_count": current_word_count,
            })

            current_paragraphs = []
            current_word_count = 0

        current_paragraphs.append(paragraph)
        current_word_count += paragraph_word_count

    # Save the final chunk
    if current_paragraphs:

        chunk_text = "\n\n".join(current_paragraphs)

        chunks.append({
            "chunk_id": (
                f"{document['document_id']}_"
                f"{len(chunks):03d}"
            ),
            "document_id": document["document_id"],
            "source": document["source"],
            "chunk_index": len(chunks),
            "text": chunk_text,
            "word_count": current_word_count,
        })

    return chunks


import re


def split_into_sentences(text: str) -> list[str]:
    """
    Lightweight sentence splitter used for PDF text.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def chunk_pdf_page(
    document: dict,
    max_words: int = 180,
    overlap_words: int = 30
) -> list[dict]:
    """
    Split one PDF page into sentence-aware chunks.

    Preserves:
    - document_id
    - source filename
    - page number
    - chunk index
    """

    sentences = split_into_sentences(
        document["text"]
    )

    chunks = []

    current_words = []

    for sentence in sentences:

        sentence_words = sentence.split()

        # If adding this sentence exceeds the limit,
        # save the current chunk first.
        if (
            current_words
            and len(current_words)
            + len(sentence_words)
            > max_words
        ):

            chunk_text = " ".join(
                current_words
            )

            chunk_index = len(chunks)

            chunks.append(
                {
                    "chunk_id": (
                        f"{document['document_id']}"
                        f"_p{document['page']:03d}"
                        f"_c{chunk_index:03d}"
                    ),
                    "document_id": document[
                        "document_id"
                    ],
                    "source": document[
                        "source"
                    ],
                    "page": document[
                        "page"
                    ],
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "word_count": len(
                        current_words
                    ),
                }
            )

            # Keep a small overlap from the
            # previous chunk.
            current_words = current_words[
                -overlap_words:
            ]

        current_words.extend(
            sentence_words
        )

    # Save final chunk
    if current_words:

        chunk_index = len(chunks)

        chunks.append(
            {
                "chunk_id": (
                    f"{document['document_id']}"
                    f"_p{document['page']:03d}"
                    f"_c{chunk_index:03d}"
                ),
                "document_id": document[
                    "document_id"
                ],
                "source": document[
                    "source"
                ],
                "page": document[
                    "page"
                ],
                "chunk_index": chunk_index,
                "text": " ".join(
                    current_words
                ),
                "word_count": len(
                    current_words
                ),
            }
        )

    return chunks