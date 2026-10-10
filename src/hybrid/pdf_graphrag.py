import json
from pathlib import Path

from src.vector.pdf_retriever import PDFRetriever
from src.graph.pdf_graph_retriever import PDFGraphRetriever
from src.generation.llm import NvidiaLLM


CHUNKS_PATH = Path(
    "data/processed/pdf_chunks.json"
)


class PDFGraphRAG:

    def __init__(
        self,
        workspace=None,
        embedding_model=None,
    ):

        # A workspace scopes every store to one document.
        # Without one, fall back to the legacy single-corpus paths.
        if workspace is not None:

            chunks_path = workspace.chunks_path

            self.vector_retriever = PDFRetriever(
                index_path=workspace.index_path,
                metadata_path=workspace.metadata_path,
                embedding_model=embedding_model,
            )

            self.graph_retriever = PDFGraphRetriever(
                dataset_id=workspace.doc_id
            )

        else:

            chunks_path = CHUNKS_PATH

            self.vector_retriever = PDFRetriever(
                embedding_model=embedding_model
            )

            self.graph_retriever = (
                PDFGraphRetriever()
            )

        self.llm = NvidiaLLM()

        with chunks_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            chunks = json.load(file)

        self.chunk_map = {
            chunk["chunk_id"]: chunk
            for chunk in chunks
        }

    def close(self):

        self.graph_retriever.close()

    # --------------------------------------------------
    # Graph retrieval
    # --------------------------------------------------

    def retrieve_graph(
        self,
        question: str,
        max_entities: int = 3,
        max_hops: int = 2,
        max_paths_per_entity: int = 8
    ):

        entities = (
            self.graph_retriever
            .search_entities(
                query=question,
                limit=max_entities
            )
        )

        graph_paths = []

        seen_paths = set()

        for entity in entities:

            paths = (
                self.graph_retriever
                .get_neighborhood(
                    entity_key=entity[
                        "entity_key"
                    ],
                    max_hops=max_hops,
                    limit=max_paths_per_entity
                )
            )

            for path in paths:

                signature = self._path_signature(
                    path
                )

                if signature in seen_paths:
                    continue

                seen_paths.add(signature)

                graph_paths.append(path)

        return entities, graph_paths

    # --------------------------------------------------
    # Path helpers
    # --------------------------------------------------

    def _path_signature(self, path):

        node_names = tuple(
            node.get("name", "")
            for node in path["nodes"]
        )

        relationship_types = tuple(
            relationship.get(
                "type",
                ""
            )
            for relationship
            in path["relationships"]
        )

        return (
            node_names,
            relationship_types
        )

    def format_graph_path(self, path):

        nodes = path["nodes"]

        relationships = (
            path["relationships"]
        )

        parts = []

        for index, node in enumerate(nodes):

            parts.append(
                node.get(
                    "name",
                    "Unknown"
                )
            )

            if index < len(
                relationships
            ):

                relation = (
                    relationships[index]
                    .get(
                        "type",
                        "RELATED_TO"
                    )
                )

                parts.append(
                    f"--{relation}--"
                )

        return " ".join(parts)

    # --------------------------------------------------
    # Collect graph evidence chunks
    # --------------------------------------------------

    def graph_evidence_chunks(
        self,
        graph_paths,
        max_chunks: int = 8
    ):

        chunk_ids = []

        for path in graph_paths:

            for node in path["nodes"]:

                for chunk_id in node.get(
                    "chunk_ids",
                    []
                ):

                    if (
                        chunk_id
                        not in chunk_ids
                    ):
                        chunk_ids.append(
                            chunk_id
                        )

        chunks = []

        for chunk_id in chunk_ids:

            chunk = self.chunk_map.get(
                chunk_id
            )

            if chunk:
                chunks.append(chunk)

            if len(chunks) >= max_chunks:
                break

        return chunks

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    def build_prompt(
        self,
        question,
        vector_results,
        graph_paths,
        graph_chunks
    ):

        vector_context = []

        for result in vector_results:

            vector_context.append(
                f"""
SOURCE: {result['source']}
PAGE: {result['page']}
CHUNK: {result['chunk_id']}

{result['text']}
"""
            )

        graph_context = []

        for index, path in enumerate(
            graph_paths[:12],
            start=1
        ):

            graph_context.append(
                f"{index}. "
                f"{self.format_graph_path(path)}"
            )

        graph_evidence = []

        for chunk in graph_chunks:

            graph_evidence.append(
                f"""
SOURCE: {chunk['source']}
PAGE: {chunk['page']}
CHUNK: {chunk['chunk_id']}

{chunk['text']}
"""
            )

        return f"""
You are answering a question using evidence extracted
from uploaded documents.

Use ONLY the supplied evidence.

You are given two complementary sources of context:

1. VECTOR EVIDENCE
Semantic chunks retrieved directly from the documents.

2. KNOWLEDGE GRAPH PATHS
Structured relationships extracted from the documents.

Knowledge graph paths help identify relationships and
multi-hop connections, but graph extraction may contain
noise.

The original document chunks are the authoritative
evidence.

Do not state a graph relationship as fact unless it is
supported by the supplied document evidence.

If the available evidence does not support an answer,
respond exactly:

INSUFFICIENT_CONTEXT


QUESTION:

{question}


=========================
VECTOR EVIDENCE
=========================

{''.join(vector_context)}


=========================
KNOWLEDGE GRAPH PATHS
=========================

{chr(10).join(graph_context)}


=========================
GRAPH-SOURCED DOCUMENT EVIDENCE
=========================

{''.join(graph_evidence)}


=========================
ANSWER INSTRUCTIONS
=========================

Answer the question clearly and concisely.

When possible:
- explain relationships across multiple pieces of evidence
- use the graph paths to connect related concepts
- rely on document text for factual claims
- do not use outside knowledge
- do not invent missing information

Do not mention internal retrieval implementation unless
the question asks about it.

Answer:
"""

    # --------------------------------------------------
    # Main GraphRAG pipeline
    # --------------------------------------------------

    def answer(
        self,
        question: str,
        top_k: int = 5
    ):

        # 1. Vector retrieval

        vector_results = (
            self.vector_retriever.retrieve(
                question,
                top_k=top_k
            )
        )

        # 2. Graph retrieval

        entities, graph_paths = (
            self.retrieve_graph(
                question
            )
        )

        # 3. Retrieve original chunks associated
        #    with graph entities.

        graph_chunks = (
            self.graph_evidence_chunks(
                graph_paths
            )
        )

        # 4. Build fused prompt

        prompt = self.build_prompt(
            question=question,
            vector_results=vector_results,
            graph_paths=graph_paths,
            graph_chunks=graph_chunks
        )

        # 5. Generate answer

        answer = self.llm.generate(
            prompt=prompt,
            max_tokens=1500
        )

        # 6. Build source list

        sources = {}

        all_chunks = (
            vector_results
            + graph_chunks
        )

        for chunk in all_chunks:

            key = (
                chunk["source"],
                chunk["page"]
            )

            sources[key] = {
                "source":
                    chunk["source"],

                "page":
                    chunk["page"]
            }

        return {
            "question": question,
            "answer": answer,
            "matched_entities": entities,
            "graph_paths": graph_paths,
            "vector_results": vector_results,
            "graph_evidence": graph_chunks,
            "sources": list(
                sources.values()
            )
        }