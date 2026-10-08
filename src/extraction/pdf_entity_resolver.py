import re
import unicodedata


# Conservative aliases for common RAG concepts.
# We can expand this later based on real PDFs.
ENTITY_ALIASES = {
    "ragchecker": "RAGCHECKER",

    "rag system": "RAG System",
    "rag systems": "RAG System",

    "retrieval module": "Retriever",
    "retrieval component": "Retriever",
    "retriever": "Retriever",

    "generation module": "Generator",
    "generation component": "Generator",
    "generator": "Generator",

    "retrieval-augmented generation": "Retrieval-Augmented Generation",
    "retrieval augmented generation": "Retrieval-Augmented Generation",
}


def normalize_for_matching(name: str) -> str:
    """
    Normalize an entity name only for comparison/matching.
    """

    if not name:
        return ""

    name = unicodedata.normalize("NFKC", name)

    name = name.strip().lower()

    # Collapse repeated whitespace.
    name = re.sub(r"\s+", " ", name)

    # Remove trailing punctuation.
    name = name.rstrip(".,;:!?")

    return name


def resolve_entity_name(name: str) -> str:
    """
    Convert known variants to one canonical entity name.
    Unknown entities retain their original name.
    """

    normalized = normalize_for_matching(name)

    if normalized in ENTITY_ALIASES:
        return ENTITY_ALIASES[normalized]

    return name.strip()