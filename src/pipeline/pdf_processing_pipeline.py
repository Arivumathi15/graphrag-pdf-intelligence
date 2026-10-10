import json
from datetime import datetime, timezone
from pathlib import Path

from src.ingestion.run_pdf_ingestion import (
    run_pdf_ingestion,
)
from src.vector.build_pdf_index import (
    build_pdf_index,
)
from src.extraction.batch_pdf_extract import (
    main as run_graph_extraction,
)
from src.graph.pdf_graph_loader import (
    main as load_graph_to_neo4j,
    delete_dataset,
)
from src.pipeline.workspace import (
    Workspace,
    get_workspace,
    list_workspaces,
    make_doc_id,
)


class PDFProcessingPipeline:
    """
    Processes each PDF into its own workspace so several
    documents can coexist. Nothing is deleted when a new
    document is added.
    """

    def __init__(self, embedding_model=None):

        # Optional shared model so the app loads it only once.
        self.embedding_model = embedding_model

    # --------------------------------------------------
    # Listing and statistics
    # --------------------------------------------------

    def list_documents(self) -> list[dict]:
        """Metadata for every processed document, newest first."""

        return [
            workspace.read_meta()
            for workspace in list_workspaces()
        ]

    def get_statistics(self, doc_id: str | None = None) -> dict:
        """
        Statistics for one document, or totals across all
        documents when doc_id is None.
        """

        stats = {
            "documents": 0,
            "pages": 0,
            "chunks": 0,
            "entities": 0,
            "relationships": 0,
        }

        if doc_id is not None:

            workspace = get_workspace(doc_id)

            documents = (
                [workspace.read_meta()]
                if workspace
                else []
            )

        else:

            documents = self.list_documents()

        for meta in documents:

            stats["documents"] += 1

            for key in (
                "pages",
                "chunks",
                "entities",
                "relationships",
            ):
                stats[key] += meta.get(key, 0)

        return stats

    # --------------------------------------------------
    # Processing
    # --------------------------------------------------

    def process_pdf(
        self,
        filename: str,
        content: bytes,
        progress=None,
    ):
        """
        Process one PDF into its own workspace.

        Returns (meta, created). If the same file was already
        processed, nothing is recomputed and created is False.
        """

        def report(message):
            if progress:
                progress(message)

        filename = Path(filename).name

        if Path(filename).suffix.lower() != ".pdf":
            raise ValueError(f"{filename} is not a PDF file.")

        doc_id = make_doc_id(filename, content)

        existing = get_workspace(doc_id)

        if existing is not None:
            return existing.read_meta(), False

        workspace = Workspace(doc_id)

        # A previous attempt may have been interrupted.
        workspace.remove()

        workspace.pdf_dir.mkdir(parents=True, exist_ok=True)

        (workspace.pdf_dir / filename).write_bytes(content)

        try:

            print("\n" + "=" * 70)
            print(f"PROCESSING: {filename}  ({doc_id})")
            print("=" * 70)

            report(f"Reading and chunking {filename}...")

            run_pdf_ingestion(
                pdf_dir=workspace.pdf_dir,
                output_path=workspace.chunks_path,
            )

            if not workspace.chunks_path.exists():
                raise ValueError(
                    "No extractable text was found. Scanned "
                    "(image-only) PDFs are not supported."
                )

            with workspace.chunks_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                chunks = json.load(file)

            if not chunks:
                raise ValueError(
                    "No extractable text was found. Scanned "
                    "(image-only) PDFs are not supported."
                )

            report("Building vector index...")

            build_pdf_index(
                chunks_path=workspace.chunks_path,
                index_path=workspace.index_path,
                metadata_path=workspace.metadata_path,
                embedding_model=self.embedding_model,
            )

            report("Extracting knowledge graph...")

            run_graph_extraction(
                chunks_path=workspace.chunks_path,
                raw_path=workspace.raw_path,
                resolved_path=workspace.graph_path,
            )

            if not workspace.graph_path.exists():
                raise RuntimeError(
                    "Graph extraction did not produce "
                    "a resolved graph."
                )

            report("Loading graph into Neo4j...")

            load_graph_to_neo4j(
                graph_path=workspace.graph_path,
                dataset_id=doc_id,
            )

            with workspace.graph_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                graph = json.load(file)

            meta = {
                "doc_id": doc_id,
                "name": filename,
                "pages": len(
                    {chunk["page"] for chunk in chunks}
                ),
                "chunks": len(chunks),
                "entities": len(graph.get("entities", [])),
                "relationships": len(
                    graph.get("relationships", [])
                ),
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

            # Written last: its presence marks the document ready.
            workspace.write_meta(meta)

            return meta, True

        except Exception:

            # Don't leave a half-built document behind.
            workspace.remove()

            try:
                delete_dataset(doc_id)
            except Exception:
                pass

            raise

    def process_uploaded_files(
        self,
        uploaded_files,
        progress=None,
    ) -> list[dict]:
        """
        Streamlit entry point. Returns one entry per file:
        {"meta": ..., "created": bool}.
        """

        if not uploaded_files:

            raise ValueError(
                "Please upload at least one PDF."
            )

        results = []

        for uploaded_file in uploaded_files:

            meta, created = self.process_pdf(
                filename=uploaded_file.name,
                content=bytes(uploaded_file.getbuffer()),
                progress=progress,
            )

            results.append(
                {"meta": meta, "created": created}
            )

        return results

    # --------------------------------------------------
    # Deletion
    # --------------------------------------------------

    def delete_document(self, doc_id: str) -> None:
        """Remove one document's files and its Neo4j graph."""

        workspace = get_workspace(doc_id)

        if workspace is None:
            return

        delete_dataset(doc_id)

        workspace.remove()
