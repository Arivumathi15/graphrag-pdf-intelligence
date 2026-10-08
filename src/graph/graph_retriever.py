class GraphRetriever:

    def __init__(self, neo4j_client):
        self.client = neo4j_client

    def retrieve_neighborhood(
        self,
        entity_name: str,
        max_hops: int = 4
    ) -> list[dict]:

        if max_hops < 1 or max_hops > 6:
            raise ValueError(
                "max_hops must be between 1 and 6"
            )

        query = f"""
        MATCH path =
            (start:Entity {{name: $entity_name}})
            -[*1..{max_hops}]->
            (end:Entity)

        RETURN path
        """

        paths = []

        with self.client.driver.session() as session:

            result = session.run(
                query,
                entity_name=entity_name
            )

            for record in result:

                path = record["path"]

                path_data = {
                    "nodes": [],
                    "relationships": []
                }

                for node in path.nodes:

                    path_data["nodes"].append({
                        "name": node.get("name"),
                        "type": node.get("type")
                    })

                for relationship in path.relationships:

                    path_data[
                        "relationships"
                    ].append({
                        "type": relationship.type,
                        "sources": relationship.get(
                            "sources",
                            []
                        ),
                        "chunk_ids": relationship.get(
                            "chunk_ids",
                            []
                        )
                    })

                paths.append(
                    path_data
                )

        return paths

    def execute_plan(
        self,
        start_entity: str,
        relationships: list[str]
    ) -> list[dict]:

        if not relationships:
            return []

        allowed_relationships = {
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

        # Validate relationship types
        for relationship in relationships:

            if relationship not in allowed_relationships:
                raise ValueError(
                    f"Unsupported relationship: "
                    f"{relationship}"
                )

        # -----------------------------------
        # 1. Build relationship pattern
        # -----------------------------------

        relationship_pattern = "".join(
            f"-[r{i + 1}:{relationship}]->"
            f"(n{i + 1}:Entity)"
            for i, relationship in enumerate(
                relationships
            )
        )

        # -----------------------------------
        # 2. Build RETURN items
        # -----------------------------------

        return_items = ["n0"]

        for i in range(len(relationships)):

            return_items.append(
                f"r{i + 1}"
            )

            return_items.append(
                f"n{i + 1}"
            )

        # -----------------------------------
        # 3. Build Cypher query
        # -----------------------------------

        query = f"""
        MATCH
            (n0:Entity {{name: $start_entity}})
            {relationship_pattern}

        RETURN
            {", ".join(return_items)}
        """

        results = []

        # -----------------------------------
        # 4. Execute query
        # -----------------------------------

        with self.client.driver.session() as session:

            records = session.run(
                query,
                start_entity=start_entity
            )

            for record in records:

                # ---------------------------
                # 5. Extract nodes
                # ---------------------------

                nodes = []

                for i in range(
                    len(relationships) + 1
                ):

                    node = record[f"n{i}"]

                    nodes.append({
                        "name": node.get("name"),
                        "type": node.get("type"),
                        "sources": node.get(
                            "sources",
                            []
                        ),
                        "chunk_ids": node.get(
                            "chunk_ids",
                            []
                        )
                    })

                # ---------------------------
                # 6. Extract relationships
                #    + provenance
                # ---------------------------

                steps = []

                for i, relationship_type in enumerate(
                    relationships
                ):

                    relationship = record[
                        f"r{i + 1}"
                    ]

                    steps.append({
                        "source": nodes[i]["name"],
                        "relationship": relationship_type,
                        "target": nodes[i + 1]["name"],

                        "sources": relationship.get(
                            "sources",
                            []
                        ),

                        "chunk_ids": relationship.get(
                            "chunk_ids",
                            []
                        )
                    })

                # ---------------------------
                # 7. Final result
                # ---------------------------

                results.append({
                    "start_entity": start_entity,
                    "nodes": nodes,
                    "steps": steps,
                    "answer_entity": nodes[-1]
                })

        return results