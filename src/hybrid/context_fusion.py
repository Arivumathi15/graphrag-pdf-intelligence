def build_vector_context(
    retrieved_chunks: list[dict]
) -> str:

    if not retrieved_chunks:
        return "No vector context was retrieved."

    lines = [
        "VECTOR RETRIEVAL CONTEXT:"
    ]

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        source = chunk.get(
            "source",
            "unknown"
        )

        chunk_id = chunk.get(
            "chunk_id",
            "unknown"
        )

        text = chunk.get(
            "text",
            ""
        )

        lines.append(
            f"\n[{index}] "
            f"Source: {source}"
        )

        lines.append(
            f"Chunk: {chunk_id}"
        )

        lines.append(text)

    return "\n".join(lines)


def fuse_contexts(
    vector_context: str,
    graph_context: str
) -> str:

    return f"""
{graph_context}

==================================================

{vector_context}
""".strip()