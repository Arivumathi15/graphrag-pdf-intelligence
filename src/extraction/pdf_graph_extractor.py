import json

from src.generation.llm import NvidiaLLM
from src.extraction.pdf_extraction_prompt import (
    PDF_EXTRACTION_SYSTEM_PROMPT
)


# Escalating output budgets used on retry.
TOKEN_BUDGETS = (3000, 6000, 8000)


def parse_json_response(response: str, repair: bool = True):
    """Return (parsed_dict, None) or (None, error).

    Strips Markdown fences and, if the reply was truncated,
    recovers every complete entry before the cut-off.
    """

    cleaned = response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned), None
    except json.JSONDecodeError as error:
        first_error = error

    if not repair:
        return None, first_error

    # Truncated output: cut back to the last complete object
    # and close the open array/object.
    positions = [
        index
        for index, char in enumerate(cleaned)
        if char == "}"
    ]

    for position in reversed(positions[-200:]):

        for suffix in ("]}", "}", ""):

            try:

                repaired = json.loads(
                    cleaned[: position + 1] + suffix
                )

            except json.JSONDecodeError:
                continue

            if isinstance(repaired, dict):
                return repaired, None

    return None, first_error


class PDFGraphExtractor:

    def __init__(self):
        self.llm = NvidiaLLM()

    def extract(self, chunk: dict) -> dict:

        prompt = f"""
{PDF_EXTRACTION_SYSTEM_PROMPT}

DOCUMENT INFORMATION:
Document: {chunk['source']}
Page: {chunk['page']}
Chunk ID: {chunk['chunk_id']}

DOCUMENT TEXT:
{chunk['text']}

Extract the knowledge graph information from the document text above.

Return ONLY the JSON object.
"""

        # Retry with a larger token budget: the model shares
        # max_tokens with its reasoning, so long answers can be
        # cut off mid-JSON.
        result = None
        last_error = None
        response = ""

        for attempt, max_tokens in enumerate(TOKEN_BUDGETS):

            is_last = attempt == len(TOKEN_BUDGETS) - 1

            try:

                response = self.llm.generate(
                    prompt=prompt,
                    max_tokens=max_tokens
                )

            except Exception as error:

                last_error = error
                continue

            # Only salvage a truncated reply on the final attempt.
            result, last_error = parse_json_response(
                response,
                repair=is_last
            )

            if result is not None:
                break

        if result is None:

            print(
                f"JSON parsing failed for "
                f"{chunk['chunk_id']}: {last_error}"
            )

            return {
                "entities": [],
                "relationships": [],
                "error": str(last_error)
            }

        # Make sure expected fields exist.
        result.setdefault("entities", [])
        result.setdefault("relationships", [])

        provenance = {
            "document_id": chunk["document_id"],
            "source": chunk["source"],
            "page": chunk["page"],
            "chunk_id": chunk["chunk_id"]
        }

        # Add provenance to entities.
        for entity in result["entities"]:
            entity["provenance"] = provenance.copy()

        # Add provenance to relationships.
        for relationship in result["relationships"]:
            relationship["provenance"] = provenance.copy()

        return result