import json
import sys
import time
from pathlib import Path


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(
    str(PROJECT_ROOT / "src" / "hybrid")
)

from graphrag import GraphRAG


QUESTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "questions.json"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "graphrag_results.json"
)


# --------------------------------------------------
# Simple answer normalization
# --------------------------------------------------

def normalize_answer(text: str) -> str:

    return (
        text
        .lower()
        .strip()
        .replace(".", "")
    )


def check_answer_correctness(
    expected: str,
    generated: str
) -> bool:

    return (
        normalize_answer(expected)
        in normalize_answer(generated)
    )


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

def main():

    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        questions = json.load(file)

    rag = GraphRAG(
        top_k=5
    )

    results = []

    try:

        for item in questions:

            question_id = item["id"]
            question = item["question"]
            expected_answer = item["answer"]
            hops = item["hops"]

            print("\n" + "=" * 70)
            print(
                f"{question_id} | "
                f"{hops}-hop"
            )
            print("=" * 70)

            print(
                f"Question: {question}"
            )

            # --------------------------------------
            # Measure complete GraphRAG latency
            # --------------------------------------

            start_time = time.perf_counter()

            try:

                result = rag.answer(
                    question
                )

                error = None

            except Exception as exc:

                result = None
                error = str(exc)

            latency = (
                time.perf_counter()
                - start_time
            )

            # --------------------------------------
            # Handle failure
            # --------------------------------------

            if result is None:

                evaluation_result = {
                    "id": question_id,
                    "question": question,
                    "hops": hops,
                    "expected_answer": expected_answer,
                    "generated_answer": None,
                    "correct": False,
                    "latency_seconds": round(
                        latency,
                        3
                    ),
                    "linked_entities": [],
                    "query_plan": None,
                    "graph_path_found": False,
                    "graph_evidence_sources": [],
                    "error": error
                }

                results.append(
                    evaluation_result
                )

                print(
                    f"ERROR: {error}"
                )

                continue

            # --------------------------------------
            # Answer correctness
            # --------------------------------------

            generated_answer = (
                result["answer"]
            )

            correct = (
                check_answer_correctness(
                    expected_answer,
                    generated_answer
                )
            )

            # --------------------------------------
            # Graph path
            # --------------------------------------

            graph_results = (
                result.get(
                    "graph_results",
                    []
                )
            )

            graph_path_found = bool(
                graph_results
            )

            # --------------------------------------
            # Collect graph evidence sources
            # --------------------------------------

            graph_sources = set()

            for graph_result in graph_results:

                for step in graph_result.get(
                    "steps",
                    []
                ):

                    for source in step.get(
                        "sources",
                        []
                    ):

                        graph_sources.add(
                            source
                        )

            # --------------------------------------
            # Store result
            # --------------------------------------

            evaluation_result = {
                "id": question_id,
                "question": question,
                "hops": hops,
                "expected_answer": expected_answer,
                "generated_answer": generated_answer,
                "correct": correct,
                "latency_seconds": round(
                    latency,
                    3
                ),
                "linked_entities": [
                    entity["name"]
                    for entity in result.get(
                        "linked_entities",
                        []
                    )
                ],
                "query_plan": result.get(
                    "query_plan"
                ),
                "graph_path_found": (
                    graph_path_found
                ),
                "graph_evidence_sources": sorted(
                    graph_sources
                ),
                "error": None
            }

            results.append(
                evaluation_result
            )

            # --------------------------------------
            # Terminal output
            # --------------------------------------

            print(
                f"Expected: {expected_answer}"
            )

            print(
                f"Generated: {generated_answer}"
            )

            print(
                f"Correct: {correct}"
            )

            print(
                f"Graph path found: "
                f"{graph_path_found}"
            )

            print(
                f"Latency: "
                f"{latency:.3f}s"
            )

            print(
                f"Plan: "
                f"{result.get('query_plan')}"
            )

        # ------------------------------------------
        # Save results
        # ------------------------------------------

        RESULTS_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            RESULTS_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                results,
                file,
                indent=2,
                ensure_ascii=False
            )

        # ------------------------------------------
        # Summary
        # ------------------------------------------

        total = len(results)

        correct_count = sum(
            result["correct"]
            for result in results
        )

        path_count = sum(
            result["graph_path_found"]
            for result in results
        )

        accuracy = (
            correct_count / total
            if total
            else 0
        )

        path_success_rate = (
            path_count / total
            if total
            else 0
        )

        print("\n" + "=" * 70)
        print("GRAPHRAG EVALUATION SUMMARY")
        print("=" * 70)

        print(
            f"Questions: {total}"
        )

        print(
            f"Correct: "
            f"{correct_count}/{total}"
        )

        print(
            f"Answer Accuracy: "
            f"{accuracy:.2%}"
        )

        print(
            f"Graph Path Success: "
            f"{path_success_rate:.2%}"
        )

        print(
            f"\nResults saved to:\n"
            f"{RESULTS_PATH}"
        )

    finally:

        rag.close()


if __name__ == "__main__":
    main()