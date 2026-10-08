import json
import shutil
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
)


PDF_UPLOAD_DIR = Path(
    "data/pdf_uploads"
)

CHUNKS_PATH = Path(
    "data/processed/pdf_chunks.json"
)

RAW_EXTRACTIONS_PATH = Path(
    "data/processed/pdf_raw_extractions.json"
)

RESOLVED_GRAPH_PATH = Path(
    "data/processed/pdf_resolved_graph.json"
)

FAISS_INDEX_PATH = Path(
    "data/processed/pdf_faiss.index"
)

FAISS_METADATA_PATH = Path(
    "data/processed/pdf_faiss_metadata.json"
)


class PDFProcessingPipeline:

    def __init__(self):

        PDF_UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    # --------------------------------------------------
    # Clean previous application data
    # --------------------------------------------------

    def clear_previous_data(
        self,
        clear_uploaded_pdfs: bool = False,
    ):

        generated_files = [
            CHUNKS_PATH,
            RAW_EXTRACTIONS_PATH,
            RESOLVED_GRAPH_PATH,
            FAISS_INDEX_PATH,
            FAISS_METADATA_PATH,
        ]

        for path in generated_files:

            if path.exists():

                path.unlink()

                print(
                    f"Removed: {path}"
                )

        if clear_uploaded_pdfs:

            for pdf_path in (
                PDF_UPLOAD_DIR.glob("*.pdf")
            ):

                pdf_path.unlink()

                print(
                    f"Removed PDF: "
                    f"{pdf_path.name}"
                )

    # --------------------------------------------------
    # Save uploaded files
    # --------------------------------------------------

    def save_uploaded_files(
        self,
        uploaded_files,
    ):

        PDF_UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        saved_files = []

        for uploaded_file in uploaded_files:

            filename = Path(
                uploaded_file.name
            ).name

            if (
                Path(filename)
                .suffix
                .lower()
                != ".pdf"
            ):
                continue

            destination = (
                PDF_UPLOAD_DIR
                / filename
            )

            with destination.open(
                "wb"
            ) as file:

                file.write(
                    uploaded_file.getbuffer()
                )

            saved_files.append(
                destination
            )

        return saved_files

    # --------------------------------------------------
    # Read processing statistics
    # --------------------------------------------------

    def get_statistics(self):

        stats = {
            "documents": 0,
            "pages": 0,
            "chunks": 0,
            "entities": 0,
            "relationships": 0,
        }

        # PDFs

        stats["documents"] = len(
            list(
                PDF_UPLOAD_DIR.glob(
                    "*.pdf"
                )
            )
        )

        # Chunks + pages

        if CHUNKS_PATH.exists():

            with CHUNKS_PATH.open(
                "r",
                encoding="utf-8",
            ) as file:

                chunks = json.load(file)

            stats["chunks"] = len(
                chunks
            )

            unique_pages = {
                (
                    chunk.get("source"),
                    chunk.get("page"),
                )
                for chunk in chunks
            }

            stats["pages"] = len(
                unique_pages
            )

        # Graph

        if RESOLVED_GRAPH_PATH.exists():

            with RESOLVED_GRAPH_PATH.open(
                "r",
                encoding="utf-8",
            ) as file:

                graph = json.load(file)

            stats["entities"] = len(
                graph.get(
                    "entities",
                    [],
                )
            )

            stats["relationships"] = len(
                graph.get(
                    "relationships",
                    [],
                )
            )

        return stats

    # --------------------------------------------------
    # Main processing pipeline
    # --------------------------------------------------

    def process_existing_pdfs(self):

        pdf_files = list(
            PDF_UPLOAD_DIR.glob(
                "*.pdf"
            )
        )

        if not pdf_files:

            raise ValueError(
                "No PDF files found in "
                "data/pdf_uploads."
            )

        print("\n" + "=" * 70)
        print("PDF GRAPHRAG PROCESSING PIPELINE")
        print("=" * 70)

        print(
            f"\nDocuments: "
            f"{len(pdf_files)}"
        )

        # Important:
        # remove generated application artifacts
        # before processing a new document batch.

        self.clear_previous_data(
            clear_uploaded_pdfs=False
        )

        # ----------------------------------------------
        # Stage 1
        # PDF -> cleaned chunks
        # ----------------------------------------------

        print("\n[1/4] PDF INGESTION")

        run_pdf_ingestion()

        if not CHUNKS_PATH.exists():

            raise RuntimeError(
                "PDF ingestion did not "
                "produce pdf_chunks.json."
            )

        # ----------------------------------------------
        # Stage 2
        # Chunks -> FAISS
        # ----------------------------------------------

        print("\n[2/4] VECTOR INDEX")

        build_pdf_index()

        # ----------------------------------------------
        # Stage 3
        # Chunks -> KG extraction
        # ----------------------------------------------

        print(
            "\n[3/4] KNOWLEDGE GRAPH "
            "EXTRACTION"
        )

        run_graph_extraction()

        if not RESOLVED_GRAPH_PATH.exists():

            raise RuntimeError(
                "Graph extraction did not "
                "produce a resolved graph."
            )

        # ----------------------------------------------
        # Stage 4
        # Resolved graph -> Neo4j
        # ----------------------------------------------

        print("\n[4/4] NEO4J GRAPH LOAD")

        load_graph_to_neo4j()

        stats = self.get_statistics()

        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)

        print(
            f"Documents: "
            f"{stats['documents']}"
        )

        print(
            f"Pages: "
            f"{stats['pages']}"
        )

        print(
            f"Chunks: "
            f"{stats['chunks']}"
        )

        print(
            f"Entities: "
            f"{stats['entities']}"
        )

        print(
            f"Relationships: "
            f"{stats['relationships']}"
        )

        return stats

    # --------------------------------------------------
    # Streamlit entry point
    # --------------------------------------------------

    def process_uploaded_files(
        self,
        uploaded_files,
    ):

        if not uploaded_files:

            raise ValueError(
                "Please upload at least "
                "one PDF."
            )

        # Remove previous uploaded PDFs and
        # generated application artifacts.

        self.clear_previous_data(
            clear_uploaded_pdfs=True
        )

        saved_files = (
            self.save_uploaded_files(
                uploaded_files
            )
        )

        if not saved_files:

            raise ValueError(
                "No valid PDF files "
                "were uploaded."
            )

        return (
            self.process_existing_pdfs()
        )