import re

# we are doing conservative text cleaning to preserve paragraph boundaries. We are not removing punctuation or special characters, as they may be important for understanding the text. We are also not removing stop words, as they may be important for understanding the text. We are also not removing numbers, as they may be important for understanding the text. We are also not removing HTML tags, as they may be important for understanding the text. We are also not removing URLs, as they may be important for understanding the text. We are also not removing email addresses, as they may be important for understanding the text. We are also not removing phone numbers, as they may be important for understanding the text. We are also not removing dates, as they may be important for understanding the text. We are also not removing times, as they may be important for understanding the text. We are also not removing currency symbols, as they may be important for understanding the text. We are also not removing mathematical symbols, as they may be important for understanding the text. We are also not removing special characters, as they may be important for understanding the text. We are also not removing whitespace, as it may be important for understanding the text.


def clean_text(text: str) -> str:
    """
    Perform conservative text cleaning while preserving
    paragraph boundaries.
    """

    # Normalize Windows/Mac line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove unnecessary spaces/tabs inside lines
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces surrounding newline characters
    text = re.sub(r" *\n *", "\n", text)

    # More than two newlines becomes a paragraph break
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()