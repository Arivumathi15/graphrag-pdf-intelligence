from src.pipeline.pdf_processing_pipeline import (
    PDFProcessingPipeline,
)


def main():

    pipeline = PDFProcessingPipeline()

    stats = pipeline.get_statistics()

    print("=" * 70)
    print("PDF PROCESSING PIPELINE TEST")
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


if __name__ == "__main__":
    main()