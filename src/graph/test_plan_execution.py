import json

from neo4j_client import Neo4jClient
from entity_linker import EntityLinker
from query_analyzer import QueryAnalyzer
from graph_retriever import GraphRetriever


def main():

    question = (
        "What neural-network architecture is used "
        "by the product developed by the company "
        "acquired by Maya Chen's employer?"
    )

    client = Neo4jClient()

    try:

        client.verify_connection()

        linker = EntityLinker(
            client
        )

        analyzer = QueryAnalyzer()

        retriever = GraphRetriever(
            client
        )

        # 1. Entity linking

        linked_entities = (
            linker.find_entities_in_question(
                question
            )
        )

        # 2. Query analysis

        plan = analyzer.analyze(
            question,
            linked_entities
        )

        # 3. Graph execution

        results = retriever.execute_plan(
            start_entity=plan[
                "start_entity"
            ],
            relationships=plan[
                "relationships"
            ]
        )

        print("\nQUESTION")
        print("-" * 70)
        print(question)

        print("\nQUERY PLAN")
        print("-" * 70)
        print(
            json.dumps(
                plan,
                indent=2
            )
        )

        print("\nGRAPH RESULTS")
        print("-" * 70)

        if not results:
            print(
                "No matching graph path found."
            )
            return

        for result in results:

            for step in result["steps"]:

                print(
                    f"\n{step['source']} "
                    f"-[{step['relationship']}]-> "
                    f"{step['target']}"
                )

                print(
                    "Sources:",
                    step["sources"]
                )

                print(
                    "Chunks:",
                    step["chunk_ids"]
                )

            print(
                "\nANSWER ENTITY:"
            )

            print(
                result[
                    "answer_entity"
                ]["name"]
            )

    finally:

        client.close()


if __name__ == "__main__":
    main()