import json
import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

QUESTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "questions.json"
)

GRAPH_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "resolved_graph.json"
)

RAW_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)


def main():

    print("=" * 70)
    print("BENCHMARK VALIDATION")
    print("=" * 70)

    errors = []
    warnings = []

    # --------------------------------------------------
    # Load benchmark
    # --------------------------------------------------

    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        questions = json.load(file)

    # --------------------------------------------------
    # Load resolved knowledge graph
    # --------------------------------------------------

    with open(
        GRAPH_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        graph = json.load(file)

    print(
        f"\nQuestions loaded: {len(questions)}"
    )

    # --------------------------------------------------
    # 1. Required fields
    # --------------------------------------------------

    required_fields = {
        "id",
        "question",
        "answer",
        "hops",
        "category",
        "sources"
    }

    for index, item in enumerate(
        questions,
        start=1
    ):

        missing = (
            required_fields
            - set(item.keys())
        )

        if missing:

            errors.append(
                f"Question #{index} "
                f"is missing fields: "
                f"{sorted(missing)}"
            )

    # --------------------------------------------------
    # 2. Duplicate IDs
    # --------------------------------------------------

    ids = [
        item.get("id")
        for item in questions
    ]

    duplicate_ids = [
        question_id
        for question_id, count
        in Counter(ids).items()
        if count > 1
    ]

    if duplicate_ids:

        errors.append(
            "Duplicate question IDs: "
            f"{duplicate_ids}"
        )

    # --------------------------------------------------
    # 3. Empty questions / answers
    # --------------------------------------------------

    for item in questions:

        question_id = item.get(
            "id",
            "UNKNOWN"
        )

        if not str(
            item.get("question", "")
        ).strip():

            errors.append(
                f"{question_id}: "
                "question is empty."
            )

        if not str(
            item.get("answer", "")
        ).strip():

            errors.append(
                f"{question_id}: "
                "answer is empty."
            )

    # --------------------------------------------------
    # 4. Validate hop values
    # --------------------------------------------------

    for item in questions:

        question_id = item.get(
            "id",
            "UNKNOWN"
        )

        hops = item.get("hops")

        if (
            not isinstance(hops, int)
            or hops < 1
        ):

            errors.append(
                f"{question_id}: "
                f"invalid hops value: {hops}"
            )

    # --------------------------------------------------
    # 5. Validate source files
    # --------------------------------------------------

    raw_sources = {
        path.name
        for path in RAW_DATA_DIR.glob(
            "*.txt"
        )
    }

    for item in questions:

        question_id = item.get(
            "id",
            "UNKNOWN"
        )

        for source in item.get(
            "sources",
            []
        ):

            if source not in raw_sources:

                errors.append(
                    f"{question_id}: "
                    f"source does not exist: "
                    f"{source}"
                )

    # --------------------------------------------------
    # 6. Collect KG entity names
    # --------------------------------------------------

    entity_names = {
        entity["name"]
        for entity in graph.get(
            "entities",
            []
        )
    }

    # --------------------------------------------------
    # 7. Expected answer exists in KG
    # --------------------------------------------------

    for item in questions:

        question_id = item.get(
            "id",
            "UNKNOWN"
        )

        expected_answer = item.get(
            "answer"
        )

        if (
            expected_answer
            not in entity_names
        ):

            warnings.append(
                f"{question_id}: "
                f"expected answer "
                f"'{expected_answer}' "
                "is not an entity in the KG."
            )

    # --------------------------------------------------
    # 8. Source list should not be empty
    # --------------------------------------------------

    for item in questions:

        question_id = item.get(
            "id",
            "UNKNOWN"
        )

        sources = item.get(
            "sources",
            []
        )

        if not sources:

            warnings.append(
                f"{question_id}: "
                "no evaluation sources listed."
            )

    # --------------------------------------------------
    # 9. Distribution statistics
    # --------------------------------------------------

    hop_distribution = Counter(
        item.get("hops")
        for item in questions
    )

    category_distribution = Counter(
        item.get("category")
        for item in questions
    )

    print("\nHOP DISTRIBUTION")
    print("-" * 70)

    for hops in sorted(
        hop_distribution
    ):

        print(
            f"{hops}-hop: "
            f"{hop_distribution[hops]}"
        )

    print("\nCATEGORY DISTRIBUTION")
    print("-" * 70)

    for category, count in sorted(
        category_distribution.items()
    ):

        print(
            f"{category}: {count}"
        )

    # --------------------------------------------------
    # 10. Graph statistics
    # --------------------------------------------------

    print("\nKNOWLEDGE GRAPH")
    print("-" * 70)

    print(
        f"Entities: "
        f"{len(graph.get('entities', []))}"
    )

    print(
        f"Relationships: "
        f"{len(graph.get('relationships', []))}"
    )

    # --------------------------------------------------
    # Final report
    # --------------------------------------------------

    print("\nVALIDATION RESULT")
    print("=" * 70)

    if errors:

        print(
            f"❌ {len(errors)} error(s)"
        )

        for error in errors:

            print(
                f"  ERROR: {error}"
            )

    else:

        print(
            "✅ No structural errors found."
        )

    if warnings:

        print(
            f"\n⚠️ {len(warnings)} "
            "warning(s)"
        )

        for warning in warnings:

            print(
                f"  WARNING: {warning}"
            )

    else:

        print(
            "✅ No warnings found."
        )

    # --------------------------------------------------
    # Exit code
    # --------------------------------------------------

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()