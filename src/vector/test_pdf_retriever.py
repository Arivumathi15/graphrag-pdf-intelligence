# from src.vector.pdf_retriever import PDFRetriever


# def main():

#     retriever = PDFRetriever()

#     query = "What is RAGChecker?"

#     print("=" * 70)
#     print("PDF RETRIEVAL TEST")
#     print("=" * 70)

#     print(f"\nQuestion: {query}")

#     results = retriever.retrieve(
#         query=query,
#         top_k=5
#     )

#     for rank, result in enumerate(results, start=1):

#         print("\n" + "-" * 70)

#         print(f"Rank: {rank}")
#         print(f"Score: {result['score']:.4f}")
#         print(f"Source: {result['source']}")
#         print(f"Page: {result['page']}")
#         print(f"Chunk ID: {result['chunk_id']}")

#         preview = result["text"][:500]

#         print(f"\nText:\n{preview}...")


# if __name__ == "__main__":
#     main()


from src.vector.pdf_retriever import PDFRetriever


def main():
    retriever = PDFRetriever()

    queries = [
        "What is RAGChecker?",
        "How does RAGChecker evaluate the retriever and generator?",
        "What problems with existing RAG evaluation does RAGChecker address?"
    ]

    for query in queries:

        print("\n" + "=" * 70)
        print(f"QUESTION: {query}")
        print("=" * 70)

        results = retriever.retrieve(
            query=query,
            top_k=5
        )

        for rank, result in enumerate(results, start=1):

            print(
                f"\n[{rank}] "
                f"Score: {result['score']:.4f} | "
                f"Page: {result['page']} | "
                f"Chunk: {result['chunk_id']}"
            )

            print(result["text"][:350])


if __name__ == "__main__":
    main()