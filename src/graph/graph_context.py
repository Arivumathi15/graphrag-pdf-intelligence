def build_graph_context(
    graph_results: list[dict]
) -> str:

    if not graph_results:
        return "No graph facts were retrieved."

    lines = [
        "GRAPH FACTS:"
    ]

    fact_number = 1

    for result in graph_results:

        for step in result["steps"]:

            source = step["source"]
            relationship = step["relationship"]
            target = step["target"]

            lines.append(
                f"\n{fact_number}. "
                f"{source} "
                f"--{relationship}--> "
                f"{target}"
            )

            sources = step.get(
                "sources",
                []
            )

            chunk_ids = step.get(
                "chunk_ids",
                []
            )

            evidence = []

            for source_name, chunk_id in zip(
                sources,
                chunk_ids
            ):
                evidence.append(
                    f"{source_name} [{chunk_id}]"
                )

            if evidence:
                lines.append(
                    "   Evidence: "
                    + ", ".join(evidence)
                )

            fact_number += 1

    return "\n".join(lines)