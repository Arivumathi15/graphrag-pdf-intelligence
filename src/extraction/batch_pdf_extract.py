import json
import os
import threading
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from pathlib import Path

from src.extraction.pdf_graph_extractor import PDFGraphExtractor
from src.extraction.pdf_graph_merger import merge_extractions


CHUNKS_PATH = Path("data/processed/pdf_chunks.json")

RAW_OUTPUT_PATH = Path(
    "data/processed/pdf_raw_extractions.json"
)

RESOLVED_OUTPUT_PATH = Path(
    "data/processed/pdf_resolved_graph.json"
)

# Parallel LLM calls; lower this if the API rate-limits you.
MAX_WORKERS = int(
    os.getenv("EXTRACTION_WORKERS", "8")
)


def save_json(path: Path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


def load_existing_results(path: Path = RAW_OUTPUT_PATH):

    if not path.exists():
        return []

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def main(
    chunks_path: Path = CHUNKS_PATH,
    raw_path: Path = RAW_OUTPUT_PATH,
    resolved_path: Path = RESOLVED_OUTPUT_PATH,
):

    print("=" * 70)
    print("PDF KNOWLEDGE GRAPH BATCH EXTRACTION")
    print("=" * 70)

    with chunks_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    print(f"Total chunks: {len(chunks)}")

    # Load previous progress if extraction was interrupted.
    extraction_results = load_existing_results(raw_path)

    completed_chunk_ids = {
        result["chunk_id"]
        for result in extraction_results
        if "chunk_id" in result
    }

    print(
        f"Previously completed: "
        f"{len(completed_chunk_ids)}"
    )

    pending = [
        chunk
        for chunk in chunks
        if chunk["chunk_id"] not in completed_chunk_ids
    ]

    # The LLM call is network-bound, so threads give a
    # near-linear speed-up. One extractor (and HTTP client)
    # is shared; the OpenAI client is thread-safe.
    extractor = PDFGraphExtractor()

    workers = max(
        1,
        min(MAX_WORKERS, len(pending))
    )

    print(
        f"Extracting {len(pending)} chunks "
        f"with {workers} parallel workers"
    )

    save_lock = threading.Lock()
    done = 0

    def extract_chunk(chunk):

        result = extractor.extract(chunk)

        # JSON parse failures come back as an "error" result;
        # raise so they are not marked complete and get
        # retried on the next run.
        if "error" in result:
            raise ValueError(result["error"])

        # Store chunk ID at result level
        # so we can resume later.
        result["chunk_id"] = chunk["chunk_id"]

        return result

    with ThreadPoolExecutor(
        max_workers=workers
    ) as executor:

        futures = {
            executor.submit(extract_chunk, chunk): chunk
            for chunk in pending
        }

        for future in as_completed(futures):

            chunk_id = futures[future]["chunk_id"]

            try:

                result = future.result()

            except Exception as error:

                # Continue instead of losing the whole batch.
                print(
                    f"[ERROR] {chunk_id}: {error}"
                )

                continue

            with save_lock:

                extraction_results.append(result)

                # Save after EVERY chunk so a crash
                # can resume from here.
                save_json(
                    raw_path,
                    extraction_results
                )

                done += 1

                print(
                    f"[{done}/{len(pending)}] {chunk_id} "
                    f"entities={len(result.get('entities', []))} "
                    f"relationships="
                    f"{len(result.get('relationships', []))}"
                )

    # Futures finish out of order; restore document order so
    # merging is deterministic.
    order = {
        chunk["chunk_id"]: index
        for index, chunk in enumerate(chunks)
    }

    extraction_results.sort(
        key=lambda result: order.get(
            result["chunk_id"],
            len(order)
        )
    )

    print("\nMerging extracted graph...")

    resolved_graph = merge_extractions(
        extraction_results
    )

    save_json(
        resolved_path,
        resolved_graph
    )

    print("\n" + "=" * 70)
    print("PDF GRAPH EXTRACTION COMPLETE")
    print("=" * 70)

    print(
        f"Processed chunks: "
        f"{len(extraction_results)}"
    )

    print(
        f"Resolved entities: "
        f"{len(resolved_graph['entities'])}"
    )

    print(
        f"Resolved relationships: "
        f"{len(resolved_graph['relationships'])}"
    )

    print(
        f"\nRaw extraction:\n"
        f"{raw_path}"
    )

    print(
        f"\nResolved graph:\n"
        f"{resolved_path}"
    )


if __name__ == "__main__":
    main()
