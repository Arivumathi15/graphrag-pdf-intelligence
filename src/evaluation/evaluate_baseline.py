import sys
import json
import time
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


sys.path.append(
    str(
        PROJECT_ROOT
        / "src"
        / "baseline"
    )
)


from standard_rag import StandardRAG
from metrics import (
    calculate_retrieval_recall,
    check_answer_correctness
)


QUESTIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "questions.json"
)


RESULTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "baseline_results.json"
)


def main():

    with QUESTIONS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        questions = json.load(file)

    rag = StandardRAG(
        top_k=5
    )

    results = []

    print(
        f"\nEvaluating "
        f"{len(questions)} questions..."
    )

    for item in questions:

        print(
            f"\n{'=' * 60}"
        )

        print(
            f"{item['id']} "
            f"({item['hops']}-hop)"
        )

        print(
            item["question"]
        )

        start_time = time.perf_counter()

        rag_result = rag.answer(
            item["question"]
        )

        latency = (
            time.perf_counter()
            - start_time
        )

        retrieved_sources = [
            chunk["source"]
            for chunk
            in rag_result[
                "retrieved_chunks"
            ]
        ]

        retrieval_recall = (
            calculate_retrieval_recall(
                item["sources"],
                retrieved_sources
            )
        )

        answer_correct = (
            check_answer_correctness(
                item["answer"],
                rag_result["answer"]
            )
        )

        result = {
            "id": item["id"],
            "question": item["question"],
            "hops": item["hops"],

            "expected_answer":
                item["answer"],

            "generated_answer":
                rag_result["answer"],

            "required_sources":
                item["sources"],

            "retrieved_sources":
                retrieved_sources,

            "retrieval_recall":
                round(
                    retrieval_recall,
                    4
                ),

            "answer_correct":
                answer_correct,

            "latency_seconds":
                round(
                    latency,
                    3
                )
        }

        results.append(result)

        print(
            f"\nExpected: "
            f"{item['answer']}"
        )

        print(
            f"Generated: "
            f"{rag_result['answer']}"
        )

        print(
            f"Retrieval recall: "
            f"{retrieval_recall:.2%}"
        )

        print(
            f"Correct: "
            f"{answer_correct}"
        )

        print(
            f"Latency: "
            f"{latency:.2f}s"
        )

    with RESULTS_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\n{'=' * 60}"
    )

    print(
        f"Results saved to: "
        f"{RESULTS_FILE}"
    )


if __name__ == "__main__":
    main()