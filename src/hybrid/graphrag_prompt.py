def build_graphrag_prompt(
    question: str,
    fused_context: str
) -> str:

    return f"""
You are answering a question using retrieved evidence.

Use ONLY the supplied context.

The context contains two evidence types:

1. GRAPH FACTS
   Structured relationships retrieved from the knowledge graph.

2. VECTOR RETRIEVAL CONTEXT
   Semantically similar source-document chunks.

INSTRUCTIONS:

- Answer the user's question using only the supplied evidence.
- Follow the relationship chain required by the question.
- Graph facts represent structured relationships extracted from
  the source documents.
- Vector chunks may contain relevant information or distractors.
- Do not treat semantic similarity alone as proof of a relationship.
- Do not use outside knowledge.
- Do not invent missing relationships.
- The answer must be supported by the supplied context.
- If the supplied evidence is insufficient, return exactly:
  INSUFFICIENT_CONTEXT
- Keep the final answer concise.

QUESTION:
{question}

CONTEXT:
{fused_context}

FINAL ANSWER:
""".strip()