import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(
    str(PROJECT_ROOT / "src" / "graph")
)

sys.path.append(
    str(PROJECT_ROOT / "src" / "vector")
)


from neo4j_client import Neo4jClient
from entity_linker import EntityLinker
from query_analyzer import QueryAnalyzer
from graph_retriever import GraphRetriever
from graph_context import build_graph_context

from retriever import VectorRetriever

from context_fusion import (
    build_vector_context,
    fuse_contexts
)


def main():

    question = (
        "What neural-network architecture is used "
        "by the product developed by the company "
        "acquired by Maya Chen's employer?"
    )

    client = Neo4jClient()

    try:

        # --------------------------------
        # VECTOR RETRIEVAL
        # --------------------------------

        vector_retriever = VectorRetriever()

        vector_results = (
            vector_retriever.retrieve(
                question,
                k=5
            )
        )

        vector_context = (
            build_vector_context(
                vector_results
            )
        )

        # --------------------------------
        # GRAPH RETRIEVAL
        # --------------------------------

        linker = EntityLinker(client)
        analyzer = QueryAnalyzer()
        graph_retriever = GraphRetriever(
            client
        )

        linked_entities = (
            linker.find_entities_in_question(
                question
            )
        )

        plan = analyzer.analyze(
            question,
            linked_entities
        )

        graph_results = (
            graph_retriever.execute_plan(
                start_entity=plan[
                    "start_entity"
                ],
                relationships=plan[
                    "relationships"
                ]
            )
        )

        graph_context = (
            build_graph_context(
                graph_results
            )
        )

        # --------------------------------
        # CONTEXT FUSION
        # --------------------------------

        fused_context = (
            fuse_contexts(
                vector_context,
                graph_context
            )
        )

        print("\nQUESTION")
        print("=" * 70)
        print(question)

        print("\nFUSED CONTEXT")
        print("=" * 70)
        print(fused_context)

    finally:
        client.close()


if __name__ == "__main__":
    main()