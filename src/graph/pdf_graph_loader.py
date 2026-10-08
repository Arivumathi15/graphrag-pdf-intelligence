import json
import re
from pathlib import Path

from src.graph.neo4j_client import Neo4jClient


GRAPH_PATH = Path(
    "data/processed/pdf_resolved_graph.json"
)

DATASET_ID = "pdf_app"


def create_entity_key(name: str) -> str:
    """
    Create a stable unique key for each PDF entity.
    """

    normalized = name.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)

    return f"{DATASET_ID}::{normalized}"


def sanitize_relationship_type(
    relationship_type: str
) -> str:

    relationship_type = (
        relationship_type
        .strip()
        .upper()
    )

    relationship_type = re.sub(
        r"[^A-Z0-9_]",
        "_",
        relationship_type
    )

    return relationship_type


def main():

    print("=" * 70)
    print("PDF GRAPH -> NEO4J")
    print("=" * 70)

    # --------------------------------------------------
    # Load resolved graph JSON
    # --------------------------------------------------

    with GRAPH_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:

        graph = json.load(file)

    entities = graph.get(
        "entities",
        []
    )

    relationships = graph.get(
        "relationships",
        []
    )

    print(
        f"Entities to load: "
        f"{len(entities)}"
    )

    print(
        f"Relationships to load: "
        f"{len(relationships)}"
    )

    # --------------------------------------------------
    # Connect to Neo4j
    # --------------------------------------------------

    client = Neo4jClient()

    client.verify_connection()

    print(
        "\nNeo4j connection verified."
    )

    try:

        with client.driver.session() as session:

            # ------------------------------------------
            # Constraint for PDF graph
            # ------------------------------------------

            session.run(
                """
                CREATE CONSTRAINT pdf_entity_key_unique
                IF NOT EXISTS
                FOR (e:PdfEntity)
                REQUIRE e.entity_key IS UNIQUE
                """
            ).consume()

            print(
                "PdfEntity constraint ready."
            )

            # ------------------------------------------
            # Delete ONLY previous PDF application graph
            # ------------------------------------------

            result = session.run(
                """
                MATCH (
                    e:PdfEntity {
                        dataset_id: $dataset_id
                    }
                )

                DETACH DELETE e

                RETURN count(e) AS deleted
                """,
                dataset_id=DATASET_ID
            )

            record = result.single()

            deleted = (
                record["deleted"]
                if record
                else 0
            )

            print(
                f"Previous PDF entities deleted: "
                f"{deleted}"
            )

            # ------------------------------------------
            # Load entities
            # ------------------------------------------

            print(
                "\nLoading PDF entities..."
            )

            for index, entity in enumerate(
                entities,
                start=1
            ):

                name = entity.get(
                    "name",
                    ""
                ).strip()

                if not name:
                    continue

                entity_key = (
                    create_entity_key(name)
                )

                provenance = entity.get(
                    "provenance",
                    []
                )

                sources = sorted({
                    item.get("source")
                    for item in provenance
                    if item.get("source")
                })

                pages = sorted({
                    item.get("page")
                    for item in provenance
                    if item.get("page")
                    is not None
                })

                chunk_ids = sorted({
                    item.get("chunk_id")
                    for item in provenance
                    if item.get("chunk_id")
                })

                session.run(
                    """
                    MERGE (
                        e:PdfEntity {
                            entity_key: $entity_key
                        }
                    )

                    SET
                        e.name = $name,
                        e.type = $type,
                        e.dataset_id = $dataset_id,
                        e.aliases = $aliases,
                        e.sources = $sources,
                        e.pages = $pages,
                        e.chunk_ids = $chunk_ids
                    """,
                    entity_key=entity_key,
                    name=name,
                    type=entity.get(
                        "type",
                        "Other"
                    ),
                    dataset_id=DATASET_ID,
                    aliases=entity.get(
                        "aliases",
                        []
                    ),
                    sources=sources,
                    pages=pages,
                    chunk_ids=chunk_ids
                ).consume()

                if (
                    index % 50 == 0
                    or index == len(entities)
                ):
                    print(
                        f"  Loaded entities: "
                        f"{index}/{len(entities)}"
                    )

            # ------------------------------------------
            # Load relationships
            # ------------------------------------------

            print(
                "\nLoading PDF relationships..."
            )

            loaded_relationships = 0
            skipped_relationships = 0

            for index, relationship in enumerate(
                relationships,
                start=1
            ):

                source = relationship.get(
                    "source",
                    ""
                ).strip()

                target = relationship.get(
                    "target",
                    ""
                ).strip()

                relationship_name = (
                    relationship.get(
                        "relationship",
                        ""
                    )
                )

                if (
                    not source
                    or not target
                    or not relationship_name
                ):
                    skipped_relationships += 1
                    continue

                source_key = (
                    create_entity_key(source)
                )

                target_key = (
                    create_entity_key(target)
                )

                relation_type = (
                    sanitize_relationship_type(
                        relationship_name
                    )
                )

                if not relation_type:
                    skipped_relationships += 1
                    continue

                provenance = relationship.get(
                    "provenance",
                    []
                )

                sources = sorted({
                    item.get("source")
                    for item in provenance
                    if item.get("source")
                })

                pages = sorted({
                    item.get("page")
                    for item in provenance
                    if item.get("page")
                    is not None
                })

                chunk_ids = sorted({
                    item.get("chunk_id")
                    for item in provenance
                    if item.get("chunk_id")
                })

                # Relationship type cannot be supplied
                # as a normal Cypher parameter.
                # It has already been sanitized above.

                query = f"""
                MATCH
                    (
                        source:PdfEntity {{
                            entity_key: $source_key
                        }}
                    ),
                    (
                        target:PdfEntity {{
                            entity_key: $target_key
                        }}
                    )

                MERGE
                    (source)-[
                        r:{relation_type}
                    ]->(target)

                SET
                    r.dataset_id = $dataset_id,
                    r.sources = $sources,
                    r.pages = $pages,
                    r.chunk_ids = $chunk_ids
                """

                result = session.run(
                    query,
                    source_key=source_key,
                    target_key=target_key,
                    dataset_id=DATASET_ID,
                    sources=sources,
                    pages=pages,
                    chunk_ids=chunk_ids
                )

                summary = result.consume()

                # If source/target did not exist,
                # no relationship would be created.
                created = (
                    summary.counters
                    .relationships_created
                )

                if created > 0:
                    loaded_relationships += 1
                else:
                    # MERGE may also match an already
                    # existing relationship.
                    loaded_relationships += 1

                if (
                    index % 100 == 0
                    or index
                    == len(relationships)
                ):
                    print(
                        f"  Processed relationships: "
                        f"{index}/"
                        f"{len(relationships)}"
                    )

            # ------------------------------------------
            # Verification
            # ------------------------------------------

            entity_record = session.run(
                """
                MATCH (
                    e:PdfEntity {
                        dataset_id: $dataset_id
                    }
                )

                RETURN count(e) AS count
                """,
                dataset_id=DATASET_ID
            ).single()

            neo4j_entity_count = (
                entity_record["count"]
                if entity_record
                else 0
            )

            relationship_record = session.run(
                """
                MATCH
                    (
                        source:PdfEntity {
                            dataset_id:
                            $dataset_id
                        }
                    )
                    -[r]->
                    (
                        target:PdfEntity {
                            dataset_id:
                            $dataset_id
                        }
                    )

                WHERE
                    r.dataset_id =
                    $dataset_id

                RETURN count(r) AS count
                """,
                dataset_id=DATASET_ID
            ).single()

            neo4j_relationship_count = (
                relationship_record["count"]
                if relationship_record
                else 0
            )

            print(
                "\n" + "=" * 70
            )

            print(
                "NEO4J PDF GRAPH COMPLETE"
            )

            print(
                "=" * 70
            )

            print(
                f"Neo4j PDF entities: "
                f"{neo4j_entity_count}"
            )

            print(
                f"Neo4j PDF relationships: "
                f"{neo4j_relationship_count}"
            )

            print(
                f"Skipped relationships: "
                f"{skipped_relationships}"
            )

    finally:

        client.close()

        print(
            "\nNeo4j connection closed."
        )


if __name__ == "__main__":
    main()