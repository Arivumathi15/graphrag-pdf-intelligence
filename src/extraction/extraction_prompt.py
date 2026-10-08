def build_extraction_prompt(text: str) -> str:

    return f"""
You are an information extraction system for a knowledge graph.

Extract entities and explicit relationships from the provided text.

ALLOWED ENTITY TYPES:
- Person
- Company
- Product
- Technology
- Project
- Location

ALLOWED RELATIONSHIP TYPES:
- WORKS_AT
- WORKED_AT
- ACQUIRED
- DEVELOPS
- USES
- PARTNERED_WITH
- CONTRIBUTES_TO
- HEADQUARTERED_IN
- OPERATES

RULES:

1. Extract only information explicitly supported by the text.
2. Do not use outside knowledge.
3. Do not invent relationships.
4. Use the most complete entity name available in the text.
5. Do not create dates or years as entities.
6. Store relevant dates or years as relationship properties.
7. Use only the allowed entity types.
8. Use only the allowed relationship types.
9. Return valid JSON only.
10. Do not include markdown or explanations.
11. Extract only specific named entities.
12. Do not create generic concepts such as "AI systems",
    "machine learning systems", "neural networks",
    "environmental applications", or "predictive modelling"
    as entities unless they are explicitly named technologies
    required by the schema.
13. A Product entity must be a specifically named product,
    platform, or system.
14. Extract technologies when they are explicitly stated as
    being used by a named product or system.

15. Normalize common technology variations to their canonical
    technology name when unambiguous.

    Examples:
    "transformer-based neural networks"
        → "Transformer"

    "transformer neural networks"
        → "Transformer"

    "recurrent neural networks"
        → "Recurrent Neural Network"

16. USES means the source entity uses the target technology.

17. USED_IN means the source technology is applied or adopted
    in the target field or application.

18. Do not substitute USES for USED_IN.

TEXT:

{text}

Return exactly this JSON structure:

{{
  "entities": [
    {{
      "name": "entity name",
      "type": "entity type"
    }}
  ],
  "relationships": [
    {{
      "source": "source entity name",
      "type": "relationship type",
      "target": "target entity name",
      "properties": {{}}
    }}
  ]
}}
""".strip()