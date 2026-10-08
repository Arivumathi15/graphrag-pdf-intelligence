from standard_rag import StandardRAG


def main():

    rag = StandardRAG(
        top_k=5
    )

    question = (
        "What neural-network architecture is used "
        "by the product developed by the company "
        "acquired by Maya Chen's employer?"
    )

    result = rag.answer(
        question
    )

    print("\nQUESTION")
    print(result["question"])

    print("\nRETRIEVED SOURCES")

    for chunk in result["retrieved_chunks"]:

        print(
            f"- {chunk['source']} "
            f"({chunk['score']:.4f})"
        )

    print("\nNVIDIA ANSWER")
    print(result["answer"])


if __name__ == "__main__":
    main()