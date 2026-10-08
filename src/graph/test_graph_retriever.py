from neo4j_client import Neo4jClient
from entity_linker import EntityLinker
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

        retriever = GraphRetriever(
            client
        )

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

        if not linked_entities:
            print(
                "No starting entity found."
            )
            return

        start_entity = (
            linked_entities[0]["name"]
        )

        paths = (
            retriever.retrieve_neighborhood(
                start_entity,
                max_hops=4
            )
        )

        print("\nGRAPH PATHS")
        print("-" * 70)

        for index, path in enumerate(
            paths,
            start=1
        ):

            print(f"\nPATH {index}")

            nodes = path["nodes"]
            relationships = (
                path["relationships"]
            )

            for i, relationship in enumerate(
                relationships
            ):

                print(
                    f"{nodes[i]['name']} "
                    f"-[{relationship['type']}]-> "
                    f"{nodes[i + 1]['name']}"
                )

    finally:

        client.close()


if __name__ == "__main__":
    main()