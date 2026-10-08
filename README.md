# GraphRAG PDF Intelligence

Ask questions about your PDFs and get grounded answers by combining **vector search** (FAISS) with a **knowledge graph** (Neo4j). Upload a PDF, and the app extracts entities and relationships, builds a graph, and answers multi-hop questions that plain RAG often misses.

## Features

- **PDF ingestion** – text extraction (PyMuPDF), cleaning, and chunking.
- **Vector retrieval** – `sentence-transformers/all-MiniLM-L6-v2` embeddings indexed in FAISS.
- **Knowledge graph extraction** – LLM-based entity/relation extraction, entity resolution, and loading into Neo4j.
- **Hybrid GraphRAG** – query analysis, entity linking, graph traversal, and context fusion with vector hits.
- **Baseline comparison** – a standard vector-only RAG pipeline plus an evaluation harness (1-hop and multi-hop questions).
- **Streamlit UI** – dark-themed app for uploading PDFs and chatting with them.

## Architecture

```
PDF ──► ingestion ──► chunks ──┬──► embeddings ──► FAISS index ─┐
                               │                                ├─► context fusion ─► LLM ─► answer
                               └──► LLM extraction ─► entity    │
                                    resolution ─► Neo4j ─► graph┘
                                                     retrieval
```

## Project structure

```
app.py                 Streamlit application
src/
  ingestion/           PDF/text loading, cleaning, chunking
  vector/              Embeddings, FAISS store, retrievers, index builders
  extraction/          Prompts, graph extraction, entity resolution, merging
  graph/               Neo4j client, loaders, query analysis, entity linking, retrievers
  hybrid/              GraphRAG pipelines and context fusion
  baseline/            Standard (vector-only) RAG
  generation/          LLM client, prompt builder, answer generator
  pipeline/            End-to-end PDF processing pipeline
  evaluation/          Metrics and baseline vs. GraphRAG evaluation scripts
data/
  raw/                 Sample text corpus for the benchmark
  evaluation/          Questions, gold paths, and results
  pdf_uploads/         Uploaded PDFs
tests/                 Unit tests
```

## Prerequisites

- Python 3.10+
- A running [Neo4j](https://neo4j.com/) instance (e.g. AuraDB free tier or local Docker)
- An [NVIDIA API](https://build.nvidia.com/) key (used via the OpenAI-compatible endpoint, model `openai/gpt-oss-20b`)

## Installation

```bash
git clone https://github.com/Arivumathi15/graphrag-pdf-intelligence.git
cd graphrag-pdf-intelligence

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
NVIDIA_API_KEY=your_nvidia_api_key
NEO4J_URI=neo4j+s://<your-instance>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

`.env` is git-ignored; never commit credentials.

## Usage

### Run the app

```bash
streamlit run app.py
```

Upload a PDF in the sidebar to trigger the processing pipeline (ingestion → index build → graph extraction → Neo4j load), then ask questions in the main view.

### Run pipeline stages manually

Run from the project root, using module syntax:

```bash
python -m src.ingestion.run_pdf_ingestion      # extract and chunk PDFs
python -m src.vector.build_pdf_index           # build the FAISS index
python -m src.extraction.batch_pdf_extract     # extract entities/relations
python -m src.graph.pdf_graph_loader           # load the graph into Neo4j
```

Intermediate artifacts are written to `data/processed/` (git-ignored).

### Evaluation

The benchmark under `data/evaluation/` compares standard RAG against GraphRAG on 1-hop and multi-hop questions over the sample corpus in `data/raw/`.

```bash
python src/evaluation/evaluate_baseline.py
python src/evaluation/evaluate_graphrag.py
```

Results are saved to `data/evaluation/baseline_results.json` and `graphrag_results.json`.

## Tech stack

Python · Streamlit · FAISS · sentence-transformers · Neo4j · PyMuPDF · NVIDIA API (OpenAI-compatible client)

## License

No license specified yet. Add a `LICENSE` file to clarify usage terms.
