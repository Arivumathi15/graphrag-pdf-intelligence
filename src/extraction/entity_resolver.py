import json
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/graph_extractions.json"
)

OUTPUT_FILE = Path(
    "data/processed/resolved_graph.json"
)


def entity_key(entity: dict) -> tuple:
    return (
        entity["name"].strip().lower(),
        entity["type"].strip().lower()
    )


def relationship_key(
    relationship: dict
) -> tuple:

    return (
        relationship["source"].strip().lower(),
        relationship["type"].strip().upper(),
        relationship["target"].strip().lower()
    )


def main():

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        extractions = json.load(file)

    # -------------------------
    # Resolve entities
    # -------------------------

    entities = {}

    for extraction in extractions:

        for entity in extraction["entities"]:

            key = entity_key(entity)

            if key not in entities:

                entities[key] = {
                    "name": entity["name"],
                    "type": entity["type"],
                    "sources": [],
                    "chunk_ids": []
                }

            if extraction["source"] not in entities[key]["sources"]:
                entities[key]["sources"].append(
                    extraction["source"]
                )

            if extraction["chunk_id"] not in entities[key]["chunk_ids"]:
                entities[key]["chunk_ids"].append(
                    extraction["chunk_id"]
                )

    # -------------------------
    # Resolve relationships
    # -------------------------

    relationships = {}

    for extraction in extractions:

        for relationship in extraction["relationships"]:

            key = relationship_key(
                relationship
            )

            if key not in relationships:

                relationships[key] = {
                    "source": relationship["source"],
                    "type": relationship["type"],
                    "target": relationship["target"],
                    "properties": relationship.get(
                        "properties",
                        {}
                    ),
                    "sources": [],
                    "chunk_ids": []
                }

            if extraction["source"] not in relationships[key]["sources"]:
                relationships[key]["sources"].append(
                    extraction["source"]
                )

            if extraction["chunk_id"] not in relationships[key]["chunk_ids"]:
                relationships[key]["chunk_ids"].append(
                    extraction["chunk_id"]
                )

    resolved_graph = {
        "entities": list(
            entities.values()
        ),
        "relationships": list(
            relationships.values()
        )
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            resolved_graph,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\nResolved entities: "
        f"{len(resolved_graph['entities'])}"
    )

    print(
        f"Resolved relationships: "
        f"{len(resolved_graph['relationships'])}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()