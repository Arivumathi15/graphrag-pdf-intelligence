from neo4j_client import Neo4jClient
from entity_linker import EntityLinker
from query_analyzer import QueryAnalyzer
from graph_retriever import GraphRetriever
from graph_context import build_graph_context


def main():

    question = (
        "What neural-network architecture is used "
        "by the product developed by the company "
        "acquired by Maya Chen's employer?"
    )

    client = Neo4jClient()

    try:

        client.verify_connection()

        linker = EntityLinker(client)
        analyzer = QueryAnalyzer()
        retriever = GraphRetriever(client)

        # 1. Entity linking
        linked_entities = (
            linker.find_entities_in_question(
                question
            )
        )

        # 2. Query planning
        plan = analyzer.analyze(
            question,
            linked_entities
        )

        # 3. Graph retrieval
        graph_results = (
            retriever.execute_plan(
                start_entity=plan[
                    "start_entity"
                ],
                relationships=plan[
                    "relationships"
                ]
            )
        )

        # 4. Context construction
        graph_context = (
            build_graph_context(
                graph_results
            )
        )

        print("\nQUESTION")
        print("-" * 70)
        print(question)

        print("\nGRAPH CONTEXT")
        print("-" * 70)
        print(graph_context)

    finally:
        client.close()


if __name__ == "__main__":
    main()