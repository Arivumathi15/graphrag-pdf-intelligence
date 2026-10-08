def build_rag_prompt(
    question: str,
    retrieved_chunks: list[dict]
) -> str:

    context_parts = []

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        context_parts.append(
            f"[Source {index}: {chunk['source']}]\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are answering questions using a retrieval-augmented
generation system.

Use ONLY the information contained in the provided context.

Do not use outside knowledge.
Do not guess missing relationships.

For multi-hop questions, every required relationship must be
supported by the provided context.

If the context does not contain enough information to reliably
derive the answer, respond exactly with:

INSUFFICIENT_CONTEXT

CONTEXT:

{context}

QUESTION:

{question}

Return only the concise final answer.
"""

    return prompt.strip()