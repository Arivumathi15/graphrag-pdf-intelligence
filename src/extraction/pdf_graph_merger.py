from src.extraction.pdf_entity_resolver import (
    resolve_entity_name
)


def merge_extractions(
    extraction_results: list[dict]
) -> dict:

    entity_map = {}
    relationship_map = {}

    for result in extraction_results:

        # -------------------------
        # Entities
        # -------------------------

        for entity in result.get("entities", []):

            original_name = entity.get("name", "").strip()

            if not original_name:
                continue

            canonical_name = resolve_entity_name(
                original_name
            )

            entity_type = entity.get(
                "type",
                "Other"
            )

            provenance = entity.get(
                "provenance",
                {}
            )

            key = canonical_name.lower()

            if key not in entity_map:

                entity_map[key] = {
                    "name": canonical_name,
                    "type": entity_type,
                    "aliases": set(),
                    "provenance": []
                }

            # Preserve original LLM name as alias.
            entity_map[key]["aliases"].add(
                original_name
            )

            if (
                provenance
                and provenance
                not in entity_map[key]["provenance"]
            ):
                entity_map[key]["provenance"].append(
                    provenance
                )

        # -------------------------
        # Relationships
        # -------------------------

        for relationship in result.get(
            "relationships",
            []
        ):

            source = resolve_entity_name(
                relationship.get(
                    "source",
                    ""
                )
            )

            target = resolve_entity_name(
                relationship.get(
                    "target",
                    ""
                )
            )

            relation_type = relationship.get(
                "relationship",
                ""
            ).strip().upper()

            if not source or not target or not relation_type:
                continue

            provenance = relationship.get(
                "provenance",
                {}
            )

            key = (
                source.lower(),
                relation_type,
                target.lower()
            )

            if key not in relationship_map:

                relationship_map[key] = {
                    "source": source,
                    "relationship": relation_type,
                    "target": target,
                    "provenance": []
                }

            if (
                provenance
                and provenance
                not in relationship_map[key]["provenance"]
            ):
                relationship_map[key][
                    "provenance"
                ].append(provenance)

    # Convert sets so graph can later be serialized as JSON.
    entities = []

    for entity in entity_map.values():

        entity["aliases"] = sorted(
            entity["aliases"]
        )

        entities.append(entity)

    relationships = list(
        relationship_map.values()
    )

    return {
        "entities": entities,
        "relationships": relationships
    }