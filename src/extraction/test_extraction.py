import json
from pathlib import Path

from graph_extractor import GraphExtractor


CHUNKS_FILE = Path(
    "data/processed/chunks.json"
)


def main():

    with CHUNKS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    target_chunk = next(
        chunk
        for chunk in chunks
        if chunk["chunk_id"]
        == "aether_labs_000"
    )

    print("\nINPUT CHUNK")
    print("-" * 60)
    print(
        target_chunk["text"]
    )

    extractor = GraphExtractor()

    result = extractor.extract(
        target_chunk
    )

    print("\nEXTRACTED GRAPH")
    print("-" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()