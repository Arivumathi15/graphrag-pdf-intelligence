import json
from pathlib import Path

from src.extraction.pdf_graph_extractor import PDFGraphExtractor


CHUNKS_PATH = Path("data/processed/pdf_chunks.json")


def main():

    with CHUNKS_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    # Test only a few chunks first.
    test_chunks = chunks[:3]

    extractor = PDFGraphExtractor()

    print("=" * 70)
    print("PDF KNOWLEDGE GRAPH EXTRACTION TEST")
    print("=" * 70)

    for chunk in test_chunks:

        print("\n" + "=" * 70)
        print(f"Chunk: {chunk['chunk_id']}")
        print(f"Page: {chunk['page']}")
        print("=" * 70)

        result = extractor.extract(chunk)

        print("\nENTITIES")

        for entity in result.get("entities", []):
            print(
                f"  {entity['name']} "
                f"[{entity['type']}]"
            )

        print("\nRELATIONSHIPS")

        for relationship in result.get(
            "relationships",
            []
        ):
            print(
                f"  {relationship['source']}"
                f" --{relationship['relationship']}--> "
                f"{relationship['target']}"
            )

        print("\nPROVENANCE")

        relationships = result.get("relationships", [])

        if relationships:
            print(
                relationships[0]["provenance"]
            )


if __name__ == "__main__":
    main()