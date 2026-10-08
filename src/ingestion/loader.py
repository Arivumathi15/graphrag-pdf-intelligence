from pathlib import Path #instead of manually writing windows paths, we can use pathlib to handle file paths in a more platform-independent way


def load_text_documents(data_dir: Path) -> list[dict]:
    """
    Load all .txt documents from the given directory.
    """

    documents = []

    for file_path in sorted(data_dir.glob("*.txt")):   #glob() is a method that returns all the files in the directory that match the given pattern, in this case, all .txt files. sorted() is used to sort the list of file paths in ascending order.

        text = file_path.read_text(
            encoding="utf-8"
        )

        document = {
            "document_id": file_path.stem,   #stem is a property of the Path object that returns the file name without the extension. For example, if the file name is "document1.txt", file_path.stem will return "document1".
            "source": file_path.name,
            "text": text,
        }

        documents.append(document)

    return documents