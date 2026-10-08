import json

from neo4j_client import Neo4jClient
from entity_linker import EntityLinker
from query_analyzer import QueryAnalyzer


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

        linked_entities = (
            linker.find_entities_in_question(
                question
            )
        )

        print("\nQUESTION")
        print("-" * 70)
        print(question)

        print("\nLINKED ENTITIES")
        print("-" * 70)

        for entity in linked_entities:
            print(
                f"{entity['name']} "
                f"({entity['type']})"
            )

        plan = analyzer.analyze(
            question,
            linked_entities
        )

        print("\nQUERY PLAN")
        print("-" * 70)

        print(
            json.dumps(
                plan,
                indent=2
            )
        )

    finally:
        client.close()


if __name__ == "__main__":
    main()