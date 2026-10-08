import json
from pathlib import Path

from src.extraction.pdf_graph_extractor import (
    PDFGraphExtractor
)

from src.extraction.pdf_graph_merger import (
    merge_extractions
)


CHUNKS_PATH = Path(
    "data/processed/pdf_chunks.json"
)


def main():

    with CHUNKS_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    # Still only testing three chunks.
    test_chunks = chunks[:3]

    extractor = PDFGraphExtractor()

    extraction_results = []

    print("=" * 70)
    print("PDF ENTITY RESOLUTION TEST")
    print("=" * 70)

    for chunk in test_chunks:

        print(
            f"\nExtracting: "
            f"{chunk['chunk_id']}"
        )

        result = extractor.extract(chunk)

        extraction_results.append(result)

    print("\nMerging extracted graph...")

    graph = merge_extractions(
        extraction_results
    )

    print("\n" + "=" * 70)
    print("RESOLVED ENTITIES")
    print("=" * 70)

    for entity in graph["entities"]:

        print(
            f"\n{entity['name']} "
            f"[{entity['type']}]"
        )

        print(
            f"Aliases: {entity['aliases']}"
        )

        print(
            f"Evidence count: "
            f"{len(entity['provenance'])}"
        )

    print("\n" + "=" * 70)
    print("RESOLVED RELATIONSHIPS")
    print("=" * 70)

    for relationship in graph[
        "relationships"
    ]:

        print(
            f"{relationship['source']} "
            f"--{relationship['relationship']}--> "
            f"{relationship['target']} "
            f"[evidence: "
            f"{len(relationship['provenance'])}]"
        )

    print("\n" + "=" * 70)

    print(
        f"Total resolved entities: "
        f"{len(graph['entities'])}"
    )

    print(
        f"Total resolved relationships: "
        f"{len(graph['relationships'])}"
    )


if __name__ == "__main__":
    main()