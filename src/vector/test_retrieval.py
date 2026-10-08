from retriever import VectorRetriever


def main():

    retriever = VectorRetriever()

    question = (
    "What neural-network architecture is used "
    "by the product developed by the company "
    "acquired by Maya Chen's employer?"
)

    results = retriever.retrieve(
        question,
        k=5
    )

    print()
    print("QUESTION")
    print(question)

    print()
    print("TOP RESULTS")

    for rank, result in enumerate(
        results,
        start=1
    ):

        print()
        print(
            f"{rank}. "
            f"{result['source']}"
        )

        print(
            f"Score: "
            f"{result['score']:.4f}"
        )

        print(
            result["text"]
        )


if __name__ == "__main__":
    main()