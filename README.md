# GraphRAG PDF Intelligence

Ask multi-hop questions across your PDFs and get answers grounded in both **vector search** and a **knowledge graph**.

Plain vector RAG retrieves passages that *look similar* to the question, so it struggles when the answer needs several facts chained together ("Who founded the company that acquired the lab where X worked?"). This project adds a Neo4j knowledge graph built from the documents, traverses it to follow those chains, and fuses the graph evidence with FAISS vector hits before the LLM answers. Every answer links back to its source document and page.

## Features

- **PDF ingestion** – text extraction (PyMuPDF), cleaning and chunking with per-page provenance.
- **Vector retrieval** – `sentence-transformers/all-MiniLM-L6-v2` embeddings in a FAISS index.
- **Parallel knowledge-graph extraction** – LLM entity/relationship extraction across a thread pool, resumable, with retries, token-budget escalation and recovery of truncated JSON.
- **Entity resolution** – duplicate entities are merged before loading into Neo4j.
- **Hybrid GraphRAG** – query analysis, entity linking, multi-hop graph traversal (up to 2 hops by default) and context fusion with vector results.
- **Explainable answers** – sources with page numbers, matched entities, graph reasoning paths and the raw vector evidence with similarity scores.
- **Baseline and evaluation harness** – a vector-only RAG baseline and a 30-question benchmark spanning 1 to 5 hops.
- **Streamlit UI** – a dark, dashboard-style interface for uploading PDFs and asking questions.

## How it works

```
                         ┌─► embeddings ─► FAISS index ──────────────┐
PDF ─► ingestion ─► chunks                                           ├─► context fusion ─► LLM ─► answer
                         └─► LLM extraction ─► entity resolution ─► Neo4j ─► graph traversal ┘
                              (parallel)
```

1. **Ingest** – PDFs are read page by page, cleaned and split into chunks (`data/processed/pdf_chunks.json`).
2. **Index** – chunks are embedded and stored in FAISS.
3. **Extract** – an LLM turns each chunk into entities and relationships. Chunks are processed in parallel and progress is saved after every chunk.
4. **Resolve and load** – entities are de-duplicated and loaded into Neo4j.
5. **Answer** – the question is analysed, linked to graph entities, and the graph is traversed for connected evidence. That evidence is combined with the top-K vector hits and passed to the LLM.

## Evaluation

The benchmark in `data/evaluation/` contains 30 questions over a synthetic corpus (`data/raw/`), grouped by the number of hops needed.

| Hops | Questions | Vector-only RAG | GraphRAG |
|------|-----------|-----------------|----------|
| 1    | 14        | 13              | 13       |
| 2    | 9         | 8               | 7        |
| 3    | 3         | 1               | 1        |
| 4    | 3         | 0               | 3        |
| 5    | 1         | 0               | 1        |
| **Total correct** | **30** | **22 (73%)** | **25 (83%)** |

GraphRAG matches the baseline on short questions and pulls ahead on long chains (4+ hops: 4/4 vs 0/4). The trade-off is latency: about 13 s per 1-hop question versus about 4 s for the baseline, rising to roughly 35–55 s on the longest chains. These are results from a single run on a small, synthetic set, so treat them as indicative rather than conclusive.

## Prerequisites

- Python 3.10 or newer
- A running [Neo4j](https://neo4j.com/) instance (AuraDB free tier or local Docker)
- An [NVIDIA API](https://build.nvidia.com/) key (used through the OpenAI-compatible endpoint with `openai/gpt-oss-20b`)

## Installation

```bash
git clone https://github.com/Arivumathi15/graphrag-pdf-intelligence.git
cd graphrag-pdf-intelligence

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
NVIDIA_API_KEY=your_nvidia_api_key
NEO4J_URI=neo4j+s://<your-instance>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# Optional
EXTRACTION_WORKERS=8
```

| Variable | Required | Description |
|----------|----------|-------------|
| `NVIDIA_API_KEY` | yes | API key for the LLM used in extraction and answering |
| `NEO4J_URI` | yes | Neo4j connection URI |
| `NEO4J_USERNAME` | yes | Neo4j user |
| `NEO4J_PASSWORD` | yes | Neo4j password |
| `EXTRACTION_WORKERS` | no | Parallel LLM calls during graph extraction (default `8`). Lower it if you see rate-limit errors, raise it if you have headroom. |

`.env` is git-ignored. Never commit credentials.

## Usage

### Run the app

```bash
streamlit run app.py
```

1. Upload one or more PDFs in the sidebar and click **Process documents**.
2. Wait for the four stages to finish (ingestion, vector index, graph extraction, Neo4j load).
3. Ask a question. The answer card shows the response; the tabs below show sources, graph reasoning paths and vector evidence.

Notes:

- The first start takes roughly 30 seconds while the embedding model and its dependencies load. A loading message is shown meanwhile.
- Processing a new upload **replaces** the previous documents and knowledge base.
- Adjust **Vector Top-K** in the sidebar to control how many chunks are retrieved before graph expansion.

### Run the pipeline stages manually

From the project root:

```bash
python -m src.ingestion.run_pdf_ingestion      # extract and chunk PDFs
python -m src.vector.build_pdf_index           # build the FAISS index
python -m src.extraction.batch_pdf_extract     # extract entities and relationships (parallel, resumable)
python -m src.graph.pdf_graph_loader           # load the graph into Neo4j
```

If extraction is interrupted, re-running `batch_pdf_extract` resumes from the chunks already saved in `data/processed/pdf_raw_extractions.json`. Chunks that failed are retried automatically.

### Run the evaluation

```bash
python src/evaluation/evaluate_baseline.py
python src/evaluation/evaluate_graphrag.py
```

Results are written to `data/evaluation/baseline_results.json` and `graphrag_results.json`.

## Project structure

```
app.py                  Streamlit application
.streamlit/config.toml  Dark theme configuration
src/
  ingestion/            PDF/text loading, cleaning, chunking
  vector/               Embeddings, FAISS store, retrievers, index builders
  extraction/           Prompts, parallel graph extraction, entity resolution, merging
  graph/                Neo4j client, loaders, query analysis, entity linking, retrievers
  hybrid/               GraphRAG pipelines and context fusion
  baseline/             Standard (vector-only) RAG
  generation/           LLM client, prompt builder, answer generator
  pipeline/             End-to-end PDF processing pipeline
  evaluation/           Metrics and baseline vs GraphRAG evaluation scripts
data/
  raw/                  Sample text corpus for the benchmark
  evaluation/           Questions, gold paths and results
  pdf_uploads/          Uploaded PDFs
  processed/            Generated artifacts (git-ignored)
tests/                  Unit tests
```

## Troubleshooting

| Symptom | Likely cause and fix |
|---------|----------------------|
| Blank dark page for about 30 s on first load | Models are still importing. Wait for the loading message to finish. |
| `NVIDIA_API_KEY not found in .env` | Create `.env` in the project root as shown above. |
| Neo4j connection error | Check that the instance is running and that `NEO4J_URI`, username and password are correct. |
| Many `[ERROR]` lines or a stall during extraction | The API is probably rate-limiting. Set `EXTRACTION_WORKERS=4` and re-run; progress is kept. |
| Fewer entities than expected on a re-run | The LLM is not fully deterministic, so counts vary slightly between runs. |
| `ConnectionResetError` traceback on Windows | A harmless asyncio message when a connection closes. It does not affect results. |

## Tech stack

Python · Streamlit · FAISS · sentence-transformers · Neo4j · PyMuPDF · NVIDIA API (OpenAI-compatible client)

## License

No license specified yet. Add a `LICENSE` file to clarify usage terms.
