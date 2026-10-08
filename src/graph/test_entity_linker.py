from neo4j_client import Neo4jClient
from entity_linker import EntityLinker


def main():

    client = Neo4jClient()

    try:

        client.verify_connection()

        linker = EntityLinker(
            client
        )

        questions = [
            "Where does Maya Chen work?",

            (
                "What product is developed by the "
                "company acquired by Maya Chen's employer?"
            ),

            (
                "What neural-network architecture is "
                "used by the product developed by the "
                "company acquired by Maya Chen's employer?"
            ),

            "What project does Leon Walker contribute to?"
        ]

        for question in questions:

            matches = (
                linker.find_entities_in_question(
                    question
                )
            )

            print("\n" + "=" * 70)

            print(
                f"QUESTION:\n{question}"
            )

            print(
                "\nLINKED ENTITIES:"
            )

            if not matches:
                print("No entities found.")

            for entity in matches:

                print(
                    f"- {entity['name']} "
                    f"({entity['type']})"
                )

    finally:

        client.close()


if __name__ == "__main__":
    main()