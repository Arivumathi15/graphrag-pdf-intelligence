from src.graph.pdf_graph_retriever import (
    PDFGraphRetriever
)


def print_path(path, number):

    print(
        f"\nPATH {number}"
    )

    nodes = path["nodes"]
    relationships = (
        path["relationships"]
    )

    for index, node in enumerate(nodes):

        print(
            node["name"],
            end=""
        )

        if index < len(relationships):

            relation = relationships[
                index
            ]

            print(
                f" --{relation['type']}--> ",
                end=""
            )

    print()

    pages = set()

    for node in nodes:
        pages.update(
            node.get(
                "pages",
                []
            )
        )

    print(
        f"Pages: "
        f"{sorted(pages)}"
    )


def main():

    retriever = PDFGraphRetriever()

    try:

        query = "RAGCHECKER"

        print("=" * 70)
        print("PDF GRAPH RETRIEVAL TEST")
        print("=" * 70)

        print(
            f"\nEntity search: {query}"
        )

        entities = (
            retriever.search_entities(
                query=query,
                limit=5
            )
        )

        for entity in entities:

            print(
                f"\n{entity['name']} "
                f"[{entity['type']}]"
            )

            print(
                f"Pages: "
                f"{entity['pages']}"
            )

            print(
                f"Aliases: "
                f"{entity['aliases']}"
            )

        if not entities:

            print(
                "\nNo matching entities."
            )

            return

        start_entity = entities[0]

        print(
            "\n" + "=" * 70
        )

        print(
            f"GRAPH NEIGHBORHOOD: "
            f"{start_entity['name']}"
        )

        print("=" * 70)

        paths = (
            retriever.get_neighborhood(
                entity_key=start_entity[
                    "entity_key"
                ],
                max_hops=2,
                limit=20
            )
        )

        for index, path in enumerate(
            paths,
            start=1
        ):

            print_path(
                path,
                index
            )

        print(
            f"\nTotal paths returned: "
            f"{len(paths)}"
        )

    finally:

        retriever.close()


if __name__ == "__main__":
    main()