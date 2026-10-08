import re


class EntityLinker:

    def __init__(self, neo4j_client):
        self.client = neo4j_client

    def _normalize(self, text: str) -> str:

        text = text.lower().strip()

        # Remove common titles
        text = re.sub(
            r"\b(dr|mr|mrs|ms|prof)\.?\s+",
            "",
            text
        )

        # Remove unnecessary punctuation
        text = re.sub(
            r"[^\w\s]",
            "",
            text
        )

        # Normalize spaces
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def get_entities(self) -> list[dict]:

        query = """
        MATCH (e:Entity)
        RETURN
            e.name AS name,
            e.type AS type
        """

        with self.client.driver.session() as session:

            result = session.run(query)

            return [
                {
                    "name": record["name"],
                    "type": record["type"]
                }
                for record in result
            ]

    def find_entities_in_question(
        self,
        question: str
    ) -> list[dict]:

        entities = self.get_entities()

        normalized_question = self._normalize(
            question
        )

        matches = []

        for entity in entities:

            normalized_name = self._normalize(
                entity["name"]
            )

            if normalized_name in normalized_question:

                matches.append(
                    entity
                )

        return matches