from graphrag import GraphRAG


def main():

    question = (
        "What neural-network architecture is used "
        "by the product developed by the company "
        "acquired by Maya Chen's employer?"
    )

    rag = GraphRAG(
        top_k=5
    )

    try:

        result = rag.answer(
            question
        )

        print("\nQUESTION")
        print("=" * 70)
        print(
            result["question"]
        )

        print("\nLINKED ENTITIES")
        print("=" * 70)

        for entity in result[
            "linked_entities"
        ]:

            print(
                f"- {entity['name']} "
                f"({entity['type']})"
            )

        print("\nQUERY PLAN")
        print("=" * 70)
        print(
            result["query_plan"]
        )

        print("\nFINAL ANSWER")
        print("=" * 70)
        print(
            result["answer"]
        )

    finally:

        rag.close()


if __name__ == "__main__":
    main()