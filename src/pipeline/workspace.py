"""
Per-document workspaces.

Every processed PDF lives in its own folder so that documents can
coexist and be selected independently:

    data/workspaces/<doc_id>/
        pdf/<original name>.pdf
        chunks.json
        faiss.index
        faiss_metadata.json
        raw_extractions.json
        resolved_graph.json
        meta.json            <- written last; marks the workspace ready

The same ``doc_id`` is used as the Neo4j ``dataset_id``, which keeps
each document's graph separate from the others.
"""

import hashlib
import json
import os
import re
import shutil
from pathlib import Path


WORKSPACES_DIR = Path(
    os.getenv("WORKSPACES_DIR", "data/workspaces")
)

DOC_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")


def make_doc_id(filename: str, content: bytes) -> str:
    """
    Stable ID from the file name plus a content hash, so the same
    file is recognised again and different files never collide.
    """

    stem = re.sub(
        r"[^a-z0-9]+",
        "-",
        Path(filename).stem.lower(),
    ).strip("-")[:40] or "document"

    digest = hashlib.sha256(content).hexdigest()[:10]

    return f"{stem}-{digest}"


class Workspace:

    def __init__(self, doc_id: str):

        if not DOC_ID_PATTERN.match(doc_id):
            raise ValueError(f"Invalid document id: {doc_id!r}")

        self.doc_id = doc_id
        self.root = WORKSPACES_DIR / doc_id

    @property
    def pdf_dir(self) -> Path:
        return self.root / "pdf"

    @property
    def chunks_path(self) -> Path:
        return self.root / "chunks.json"

    @property
    def raw_path(self) -> Path:
        return self.root / "raw_extractions.json"

    @property
    def graph_path(self) -> Path:
        return self.root / "resolved_graph.json"

    @property
    def index_path(self) -> Path:
        return self.root / "faiss.index"

    @property
    def metadata_path(self) -> Path:
        return self.root / "faiss_metadata.json"

    @property
    def meta_path(self) -> Path:
        return self.root / "meta.json"

    def is_ready(self) -> bool:
        return self.meta_path.exists()

    def read_meta(self) -> dict:

        with self.meta_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def write_meta(self, meta: dict) -> None:

        with self.meta_path.open("w", encoding="utf-8") as file:
            json.dump(meta, file, indent=2, ensure_ascii=False)

    def remove(self) -> None:

        if self.root.exists():
            shutil.rmtree(self.root)


def get_workspace(doc_id: str):
    """Return the Workspace if it exists and is fully processed."""

    try:
        workspace = Workspace(doc_id)
    except ValueError:
        return None

    return workspace if workspace.is_ready() else None


def list_workspaces() -> list[Workspace]:
    """All fully processed documents, newest first."""

    if not WORKSPACES_DIR.exists():
        return []

    workspaces = []

    for folder in WORKSPACES_DIR.iterdir():

        if not folder.is_dir():
            continue

        workspace = get_workspace(folder.name)

        if workspace is not None:
            workspaces.append(workspace)

    workspaces.sort(
        key=lambda item: item.read_meta().get("created_at", ""),
        reverse=True,
    )

    return workspaces
