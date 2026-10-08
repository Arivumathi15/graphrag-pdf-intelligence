import json
import time
from pathlib import Path

from graph_extractor import GraphExtractor


CHUNKS_FILE = Path(
    "data/processed/chunks.json"
)

OUTPUT_FILE = Path(
    "data/processed/graph_extractions.json"
)


def main():

    with CHUNKS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    print(
        f"\nLoaded {len(chunks)} chunks."
    )

    extractor = GraphExtractor()

    results = []

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"\n[{index}/{len(chunks)}] "
            f"Extracting {chunk['chunk_id']}..."
        )

        start_time = time.perf_counter()

        try:

            graph_data = extractor.extract(
                chunk
            )

            elapsed = (
                time.perf_counter()
                - start_time
            )

            results.append(
                graph_data
            )

            print(
                f"Entities: "
                f"{len(graph_data['entities'])}"
            )

            print(
                f"Relationships: "
                f"{len(graph_data['relationships'])}"
            )

            print(
                f"Time: {elapsed:.2f}s"
            )

        except Exception as error:

            print(
                f"FAILED: {error}"
            )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)

    print(
        f"Successful extractions: "
        f"{len(results)}/{len(chunks)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()