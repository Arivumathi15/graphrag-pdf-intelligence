import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(
    str(PROJECT_ROOT / "src" / "generation")
)

from llm import NvidiaLLM


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


class QueryAnalyzer:

    def __init__(self):
        self.llm = NvidiaLLM()

    def build_prompt(
        self,
        question: str,
        linked_entities: list[dict]
    ) -> str:

        entity_names = [
            entity["name"]
            for entity in linked_entities
        ]

        allowed_relationships = sorted(
            ALLOWED_RELATIONSHIPS
        )

        return f"""
    You are a knowledge graph query planner.

    Your task is to convert the user's question into
    an ordered graph traversal plan.

    STARTING ENTITIES:
    {json.dumps(entity_names)}

    VALID RELATIONSHIP TYPES:
    {json.dumps(allowed_relationships)}

    USER QUESTION:
    {question}

    INSTRUCTIONS:

    1. Select exactly one start_entity from STARTING ENTITIES.

    2. Determine every graph relationship required to
    traverse from that entity toward the information
    requested by the question.

    3. relationships must contain only values from
    VALID RELATIONSHIP TYPES.

    4. Keep relationships in traversal order.

    5. The relationships array may contain one or more
    relationship types.

    6. Do not invent relationship names.

    7. Do not use placeholder values.

    8. Do not answer the user's question.

    9. Do not generate Cypher.

    10. Return only one JSON object.

    11. Do not include reasoning, analysis, explanations,
        markdown, or code fences.

    The JSON object must contain exactly two keys:

    "start_entity"
    "relationships"

    Return the final JSON object only.
    """.strip()

    def analyze(
        self,
        question: str,
        linked_entities: list[dict]
    ) -> dict:

        # -----------------------------------
        # 1. Make sure entity linking worked
        # -----------------------------------

        if not linked_entities:
            raise ValueError(
                "No linked entities available."
            )

        # -----------------------------------
        # 2. Build query-planning prompt
        # -----------------------------------

        prompt = self.build_prompt(
            question,
            linked_entities
        )

        # -----------------------------------
        # 3. First LLM attempt
        # -----------------------------------

        response = self.llm.generate(
            prompt,
            max_tokens=2048
        )

        try:

            plan = self._extract_json(
                response
            )

        except ValueError:

            print(
                "Warning: Could not extract "
                "query plan. Retrying..."
            )

            # -----------------------------------
            # 4. Retry with stronger instruction
            # -----------------------------------

            retry_prompt = f"""
    {prompt}

    IMPORTANT:
    Your previous response did not contain a usable JSON object.

    Return the final JSON object immediately.
    Do not explain your reasoning.
    Do not include analysis.
    Do not include markdown.
    Return only the JSON object.
    """.strip()

            response = self.llm.generate(
                retry_prompt,
                max_tokens=2048
            )

            try:

                plan = self._extract_json(
                    response
                )

            except ValueError as error:

                raise ValueError(
                    "Query planner failed to return "
                    "a valid JSON plan after retry.\n\n"
                    f"Response:\n{response}"
                ) from error

        # -----------------------------------
        # 5. Validate required fields
        # -----------------------------------

        if not isinstance(plan, dict):
            raise ValueError(
                "Query plan must be a JSON object."
            )

        if "start_entity" not in plan:
            raise ValueError(
                "Query plan is missing "
                "'start_entity'."
            )

        if "relationships" not in plan:
            raise ValueError(
                "Query plan is missing "
                "'relationships'."
            )

        relationships = plan[
            "relationships"
        ]

        if not isinstance(
            relationships,
            list
        ):
            raise ValueError(
                "'relationships' must be a list."
            )

        if not relationships:
            raise ValueError(
                "Query plan contains no relationships."
            )

        # -----------------------------------
        # 6. Validate relationship ontology
        # -----------------------------------

        for relationship in relationships:

            if relationship not in ALLOWED_RELATIONSHIPS:

                raise ValueError(
                    f"Invalid relationship "
                    f"in query plan: {relationship}"
                )

        # -----------------------------------
        # 7. Validate starting entity
        # -----------------------------------

        valid_entities = {
            entity["name"]
            for entity in linked_entities
        }

        if plan["start_entity"] not in valid_entities:

            raise ValueError(
                "Query planner selected an "
                "invalid starting entity: "
                f"{plan['start_entity']}"
            )

        # -----------------------------------
        # 8. Return validated plan
        # -----------------------------------

        return plan
    def _extract_json(self, response: str) -> dict:

        response = response.strip()

        # First try: response is already pure JSON
        try:
            return json.loads(response)

        except json.JSONDecodeError:
            pass

        # Second try:
        # Find a JSON object inside additional model text
        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "No complete JSON object found "
                "in model response."
            )

        json_text = response[
            start:end + 1
        ]

        try:
            return json.loads(json_text)

        except json.JSONDecodeError as error:
            raise ValueError(
                "JSON object was found but "
                "could not be parsed.\n\n"
                f"Extracted JSON:\n{json_text}"
            ) from error