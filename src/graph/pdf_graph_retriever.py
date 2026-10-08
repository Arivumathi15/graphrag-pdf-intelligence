from src.graph.neo4j_client import Neo4jClient


DATASET_ID = "pdf_app"


class PDFGraphRetriever:

    def __init__(self):

        self.client = Neo4jClient()
        self.client.verify_connection()

    def close(self):
        self.client.close()

    def search_entities(
        self,
        query: str,
        limit: int = 10
    ):
        """
        Find candidate PDF entities using:
        - entity name
        - aliases
        """

        search_text = query.strip().lower()

        with self.client.driver.session() as session:

            result = session.run(
                """
                MATCH (
                    e:PdfEntity {
                        dataset_id: $dataset_id
                    }
                )

                WHERE
                    toLower(e.name)
                    CONTAINS $search_text

                    OR any(
                        alias IN e.aliases
                        WHERE
                            toLower(alias)
                            CONTAINS $search_text
                    )

                    OR any(
                        word IN split(
                            $search_text,
                            ' '
                        )
                        WHERE
                            size(word) > 3
                            AND (
                                toLower(e.name)
                                CONTAINS word

                                OR any(
                                    alias IN e.aliases
                                    WHERE
                                        toLower(alias)
                                        CONTAINS word
                                )
                            )
                    )

                RETURN
                    e.entity_key AS entity_key,
                    e.name AS name,
                    e.type AS type,
                    e.aliases AS aliases,
                    e.sources AS sources,
                    e.pages AS pages,
                    e.chunk_ids AS chunk_ids

                LIMIT $limit
                """,
                dataset_id=DATASET_ID,
                search_text=search_text,
                limit=limit
            )

            return [
                record.data()
                for record in result
            ]

    def get_neighborhood(
        self,
        entity_key: str,
        max_hops: int = 2,
        limit: int = 50
    ):
        """
        Retrieve paths around an entity.

        We allow both incoming and outgoing relationships
        because arbitrary PDFs may express facts in either
        direction.
        """

        if max_hops < 1:
            max_hops = 1

        # Keep path depth bounded.
        max_hops = min(
            max_hops,
            4
        )

        with self.client.driver.session() as session:

            # max_hops cannot be a normal Cypher parameter
            # inside *1..N, but it is an integer bounded above.

            query = f"""
            MATCH
                (
                    start:PdfEntity {{
                        entity_key: $entity_key,
                        dataset_id: $dataset_id
                    }}
                )

            MATCH path =
                (start)-[*1..{max_hops}]-(connected:PdfEntity)

            WHERE
                connected.dataset_id =
                $dataset_id

            RETURN
                path

            LIMIT $limit
            """

            result = session.run(
                query,
                entity_key=entity_key,
                dataset_id=DATASET_ID,
                limit=limit
            )

            paths = []

            for record in result:

                path = record["path"]

                nodes = []

                for node in path.nodes:

                    nodes.append({
                        "entity_key":
                            node.get(
                                "entity_key"
                            ),

                        "name":
                            node.get(
                                "name"
                            ),

                        "type":
                            node.get(
                                "type"
                            ),

                        "pages":
                            node.get(
                                "pages",
                                []
                            ),

                        "chunk_ids":
                            node.get(
                                "chunk_ids",
                                []
                            )
                    })

                relationships = []

                for relationship in (
                    path.relationships
                ):

                    relationships.append({
                        "type":
                            relationship.type,

                        "pages":
                            relationship.get(
                                "pages",
                                []
                            ),

                        "chunk_ids":
                            relationship.get(
                                "chunk_ids",
                                []
                            )
                    })

                paths.append({
                    "nodes": nodes,
                    "relationships":
                        relationships
                })

            return paths