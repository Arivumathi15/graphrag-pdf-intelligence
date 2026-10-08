import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

QUESTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "questions.json"
)

GOLD_PATHS_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "gold_paths.json"
)

GRAPH_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "resolved_graph.json"
)


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def traverse_step(
    current_entities,
    relationships,
    relationship_type,
    direction
):
    """
    Deterministically traverse one graph step.

    current_entities:
        Set of entity names currently reachable.

    direction:
        outgoing:
            current --REL--> target

        incoming:
            current <--REL-- source
    """

    next_entities = set()

    for current_entity in current_entities:

        for relation in relationships:

            rel_type = relation["type"]
            source = relation["source"]
            target = relation["target"]

            if rel_type != relationship_type:
                continue

            if direction == "outgoing":

                if source == current_entity:
                    next_entities.add(target)

            elif direction == "incoming":

                if target == current_entity:
                    next_entities.add(source)

            else:
                raise ValueError(
                    f"Unsupported direction: {direction}"
                )

    return next_entities


def validate_gold_path(
    start_entity,
    steps,
    relationships
):

    current_entities = {start_entity}

    trace = [
        sorted(current_entities)
    ]

    for step in steps:

        relationship = step["relationship"]
        direction = step["direction"]

        current_entities = traverse_step(
            current_entities=current_entities,
            relationships=relationships,
            relationship_type=relationship,
            direction=direction
        )

        trace.append(
            sorted(current_entities)
        )

        # Path became impossible
        if not current_entities:
            break

    return current_entities, trace


def main():

    print("=" * 70)
    print("GOLD PATH VALIDATION")
    print("=" * 70)

    questions = load_json(
        QUESTIONS_PATH
    )

    gold_paths = load_json(
        GOLD_PATHS_PATH
    )

    graph = load_json(
        GRAPH_PATH
    )

    relationships = graph.get(
        "relationships",
        []
    )

    entities = {
        entity["name"]
        for entity in graph.get(
            "entities",
            []
        )
    }

    passed = 0
    failed = 0

    results = []

    question_ids = {
        item["id"]
        for item in questions
    }

    # --------------------------------------------------
    # Check missing / extra gold paths
    # --------------------------------------------------

    gold_ids = set(
        gold_paths.keys()
    )

    missing_gold = (
        question_ids - gold_ids
    )

    extra_gold = (
        gold_ids - question_ids
    )

    if missing_gold:

        print(
            "\nMissing gold paths:"
        )

        for question_id in sorted(
            missing_gold
        ):
            print(
                f"  - {question_id}"
            )

    if extra_gold:

        print(
            "\nGold paths without questions:"
        )

        for question_id in sorted(
            extra_gold
        ):
            print(
                f"  - {question_id}"
            )

    # --------------------------------------------------
    # Validate each question
    # --------------------------------------------------

    for item in questions:

        question_id = item["id"]
        question = item["question"]
        expected_answer = item["answer"]

        print("\n" + "-" * 70)

        print(
            f"{question_id}: {question}"
        )

        gold = gold_paths.get(
            question_id
        )

        if gold is None:

            print(
                "❌ FAIL — no gold path"
            )

            failed += 1
            continue

        start_entity = gold.get(
            "start_entity"
        )

        steps = gold.get(
            "steps",
            []
        )

        # ----------------------------------------------
        # Start entity validation
        # ----------------------------------------------

        if start_entity not in entities:

            print(
                f"❌ FAIL — start entity "
                f"'{start_entity}' "
                "does not exist in KG"
            )

            failed += 1
            continue

        # ----------------------------------------------
        # Hop count consistency
        # ----------------------------------------------

        expected_hops = item["hops"]

        if len(steps) != expected_hops:

            print(
                "⚠️ HOP MISMATCH — "
                f"questions.json says "
                f"{expected_hops}, "
                f"gold path has "
                f"{len(steps)}"
            )

        # ----------------------------------------------
        # Traverse gold path
        # ----------------------------------------------

        try:

            final_entities, trace = (
                validate_gold_path(
                    start_entity,
                    steps,
                    relationships
                )
            )

        except Exception as exc:

            print(
                f"❌ FAIL — {exc}"
            )

            failed += 1
            continue

        # ----------------------------------------------
        # Validate expected answer
        # ----------------------------------------------

        success = (
            expected_answer
            in final_entities
        )

        if success:

            print(
                f"✅ PASS → "
                f"{expected_answer}"
            )

            passed += 1

        else:

            print(
                "❌ FAIL"
            )

            print(
                f"Expected: "
                f"{expected_answer}"
            )

            print(
                "Reached: "
                f"{sorted(final_entities)}"
            )

            print(
                "Trace:"
            )

            for index, state in enumerate(
                trace
            ):

                if index == 0:

                    print(
                        f"  START: {state}"
                    )

                else:

                    step = steps[
                        index - 1
                    ]

                    print(
                        f"  {step['direction']} "
                        f"{step['relationship']} "
                        f"→ {state}"
                    )

            failed += 1

        results.append(
            {
                "id": question_id,
                "expected_answer": (
                    expected_answer
                ),
                "start_entity": (
                    start_entity
                ),
                "steps": steps,
                "final_entities": sorted(
                    final_entities
                ),
                "passed": success
            }
        )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print("GOLD PATH SUMMARY")
    print("=" * 70)

    print(
        f"Questions: {len(questions)}"
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    if (
        failed == 0
        and not missing_gold
        and not extra_gold
    ):

        print(
            "\n✅ All gold paths are valid."
        )

    else:

        print(
            "\n❌ Gold benchmark requires "
            "corrections."
        )


if __name__ == "__main__":
    main()