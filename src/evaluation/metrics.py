import re
import unicodedata


def calculate_retrieval_recall(
    required_sources: list[str],
    retrieved_sources: list[str]
) -> float:
    """
    Calculate how many of the required source documents
    were successfully retrieved.

    Example:
        required  = ["people.txt", "aether_labs.txt"]
        retrieved = ["people.txt", "ecovision.txt"]

        recall = 1 / 2 = 0.5
    """

    required = set(required_sources)
    retrieved = set(retrieved_sources)

    if not required:
        return 0.0

    matched = required.intersection(retrieved)

    return len(matched) / len(required)


def normalize_answer(answer: str) -> str:
    """
    Normalize an answer before comparing it with the
    expected answer.

    Handles:
    - Unicode characters
    - Unicode/non-breaking spaces
    - Upper/lower case differences
    - Markdown bold formatting
    - Repeated whitespace
    - Common trailing punctuation
    """

    if not answer:
        return ""

    # Normalize Unicode representation
    answer = unicodedata.normalize("NFKC", answer)

    # Convert to lowercase
    answer = answer.lower()

    # Remove common Markdown formatting
    answer = answer.replace("**", "")
    answer = answer.replace("__", "")
    answer = answer.replace("`", "")

    # Normalize all whitespace including Unicode spaces
    answer = re.sub(r"\s+", " ", answer)

    # Remove leading/trailing whitespace
    answer = answer.strip()

    # Remove trailing punctuation
    answer = answer.rstrip(".,!?;:")

    return answer


def check_answer_correctness(
    expected_answer: str,
    generated_answer: str
) -> bool:
    """
    Check whether the expected answer is contained in
    the generated answer after normalization.

    This allows answers such as:

        Expected:
            "Aether Labs"

        Generated:
            "Maya Chen works at **Aether Labs**."

    to be considered correct.
    """

    expected = normalize_answer(expected_answer)
    generated = normalize_answer(generated_answer)

    if not expected or not generated:
        return False

    # Explicit insufficient-context responses are incorrect
    if generated == "insufficient_context":
        return False

    return expected in generated