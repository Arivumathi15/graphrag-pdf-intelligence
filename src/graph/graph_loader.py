import json
from pathlib import Path

from neo4j_client import Neo4jClient


GRAPH_FILE = Path(
    "data/processed/resolved_graph.json"
)


ALLOWED_RELATIONSHIPS = {
    "WORKS_AT",
    "WORKED_AT",
    "ACQUIRED",
    "DEVELOPS",
    "USES",
    "PARTNERED_WITH",
    "CONTRIBUTES_TO",
    "HEADQUARTERED_IN",
    "OPERATES",
    "USED_IN"
}


def load_entity(
    tx,
    entity: dict
):

    tx.run(
        """
        MERGE (e:Entity {name: $name})

        SET
            e.type = $type,
            e.sources = $sources,
            e.chunk_ids = $chunk_ids
        """,

        name=entity["name"],
        type=entity["type"],
        sources=entity["sources"],
        chunk_ids=entity["chunk_ids"]
    )


def load_relationship(
    tx,
    relationship: dict
):

    relationship_type = (
        relationship["type"]
    )

    if relationship_type not in ALLOWED_RELATIONSHIPS:
        raise ValueError(
            f"Unsupported relationship: "
            f"{relationship_type}"
        )

    query = f"""
    MATCH (source:Entity {{name: $source}})
    MATCH (target:Entity {{name: $target}})

    MERGE (source)-[r:{relationship_type}]->(target)

    SET
        r.sources = $sources,
        r.chunk_ids = $chunk_ids,
        r.properties_json = $properties_json
    """

    tx.run(
        query,
        source=relationship["source"],
        target=relationship["target"],
        sources=relationship["sources"],
        chunk_ids=relationship["chunk_ids"],
        properties_json=json.dumps(
            relationship.get(
                "properties",
                {}
            )
        )
    )


def main():

    with GRAPH_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        graph_data = json.load(file)

    client = Neo4jClient()

    try:

        client.verify_connection()

        print(
            "Connected to Neo4j."
        )

        with client.driver.session() as session:

            # Unique entity names
            session.run(
                """
                CREATE CONSTRAINT entity_name_unique
                IF NOT EXISTS
                FOR (e:Entity)
                REQUIRE e.name IS UNIQUE
                """
            )

            print(
                "\nLoading entities..."
            )

            for entity in graph_data["entities"]:

                session.execute_write(
                    load_entity,
                    entity
                )

            print(
                f"Loaded "
                f"{len(graph_data['entities'])} "
                f"entities."
            )

            print(
                "\nLoading relationships..."
            )

            for relationship in graph_data[
                "relationships"
            ]:

                session.execute_write(
                    load_relationship,
                    relationship
                )

            print(
                f"Loaded "
                f"{len(graph_data['relationships'])} "
                f"relationships."
            )

    finally:

        client.close()

    print(
        "\nKnowledge graph loading complete."
    )


if __name__ == "__main__":
    main()