from src.hybrid.pdf_graphrag import PDFGraphRAG


def format_path(graphrag, path):
    return graphrag.format_graph_path(path)


def main():

    question = (
        "How does RAGChecker evaluate "
        "the retriever and generator?"
    )

    print("=" * 70)
    print("PDF GRAPHRAG END-TO-END TEST")
    print("=" * 70)

    print(f"\nQUESTION:\n{question}")

    graphrag = PDFGraphRAG()

    try:

        result = graphrag.answer(
            question=question,
            top_k=5
        )

        # ------------------------------------------------
        # Final answer
        # ------------------------------------------------

        print("\n" + "=" * 70)
        print("ANSWER")
        print("=" * 70)

        print(result["answer"])

        # ------------------------------------------------
        # Matched graph entities
        # ------------------------------------------------

        print("\n" + "=" * 70)
        print("MATCHED GRAPH ENTITIES")
        print("=" * 70)

        if result["matched_entities"]:

            for entity in result[
                "matched_entities"
            ]:

                print(
                    f"- {entity['name']} "
                    f"[{entity['type']}]"
                )

        else:
            print("No graph entities matched.")

        # ------------------------------------------------
        # Graph reasoning paths
        # ------------------------------------------------

        print("\n" + "=" * 70)
        print("GRAPH PATHS")
        print("=" * 70)

        if result["graph_paths"]:

            for index, path in enumerate(
                result["graph_paths"][:10],
                start=1
            ):

                print(
                    f"{index}. "
                    f"{format_path(graphrag, path)}"
                )

        else:
            print("No graph paths retrieved.")

        # ------------------------------------------------
        # Vector evidence
        # ------------------------------------------------

        print("\n" + "=" * 70)
        print("TOP VECTOR EVIDENCE")
        print("=" * 70)

        for index, chunk in enumerate(
            result["vector_results"],
            start=1
        ):

            print(
                f"\n[{index}] "
                f"{chunk['source']} "
                f"- Page {chunk['page']}"
            )

            print(
                f"Similarity: "
                f"{chunk['score']:.4f}"
            )

            preview = (
                chunk["text"][:350]
                .replace("\n", " ")
            )

            print(preview)

        # ------------------------------------------------
        # Sources
        # ------------------------------------------------

        print("\n" + "=" * 70)
        print("SOURCES")
        print("=" * 70)

        for source in result["sources"]:

            print(
                f"- {source['source']} "
                f"(Page {source['page']})"
            )

    finally:

        graphrag.close()


if __name__ == "__main__":
    main()