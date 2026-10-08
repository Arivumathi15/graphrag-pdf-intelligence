from html import escape

import streamlit as st


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="GraphRAG PDF Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Styles
# --------------------------------------------------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0B0F19;
    --surface: #121826;
    --surface-2: #171F31;
    --border: #232B3D;
    --text: #E6E9F2;
    --muted: #8B93A7;
    --accent: #7C83FF;
    --accent-2: #4FD1C5;
    --success: #34D399;
}

html, body, [class*="css"], .stMarkdown, .stTextInput input, button {
    font-family: 'Inter', sans-serif !important;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F1422 0%, #0B0F19 100%);
    border-right: 1px solid var(--border);
}
.sb-brand {
    display: flex; align-items: center; gap: .75rem;
    padding: .25rem 0 1.25rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.25rem;
}
.sb-logo {
    width: 38px; height: 38px; border-radius: 10px;
    display: grid; place-items: center; font-size: 1.15rem;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
}
.sb-title { font-weight: 700; font-size: 1rem; line-height: 1.1; }
.sb-sub { color: var(--muted); font-size: .75rem; }
.sb-label {
    text-transform: uppercase; letter-spacing: .08em;
    font-size: .7rem; font-weight: 600; color: var(--muted);
    margin: 1.25rem 0 .5rem 0;
}
[data-testid="stFileUploaderDropzone"] {
    background: var(--surface) !important;
    border: 1px dashed #34405A !important;
    border-radius: 12px !important;
}

/* ---------- Hero ---------- */
.hero {
    position: relative; overflow: hidden;
    padding: 2rem 2.25rem;
    border-radius: 18px;
    border: 1px solid var(--border);
    background:
        radial-gradient(900px 300px at 0% 0%, rgba(124,131,255,.18), transparent 60%),
        radial-gradient(700px 260px at 100% 100%, rgba(79,209,197,.12), transparent 60%),
        var(--surface);
    margin-bottom: 1.5rem;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: .4rem;
    font-size: .72rem; font-weight: 600; letter-spacing: .04em;
    color: var(--accent); background: rgba(124,131,255,.12);
    border: 1px solid rgba(124,131,255,.3);
    padding: .25rem .65rem; border-radius: 999px;
}
.hero h1 {
    font-size: 2.1rem !important; font-weight: 700 !important;
    letter-spacing: -.02em; margin: .75rem 0 .35rem 0 !important;
    padding: 0 !important;
}
.hero p { color: var(--muted); font-size: 1rem; margin: 0; max-width: 720px; }
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.dot.on { background: var(--success); box-shadow: 0 0 0 3px rgba(52,211,153,.2); }
.dot.off { background: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,.2); }

/* ---------- KPI cards ---------- */
.kpi-grid {
    display: grid; grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: .9rem; margin-bottom: 1.75rem;
}
@media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
.kpi {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 1rem 1.1rem;
    transition: border-color .2s, transform .2s;
}
.kpi:hover { border-color: #34405A; transform: translateY(-2px); }
.kpi-top { display: flex; justify-content: space-between; align-items: center; }
.kpi-label { color: var(--muted); font-size: .78rem; font-weight: 500; }
.kpi-icon { font-size: .95rem; opacity: .85; }
.kpi-value {
    font-size: 1.65rem; font-weight: 700; margin-top: .35rem;
    font-variant-numeric: tabular-nums; letter-spacing: -.01em;
}

/* ---------- Section headings ---------- */
.section-title {
    display: flex; align-items: center; gap: .6rem;
    font-size: 1.05rem; font-weight: 600; margin: .5rem 0 .75rem 0;
}
.section-title .bar {
    width: 4px; height: 18px; border-radius: 4px;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
}

/* ---------- Query box ---------- */
.st-key-query_card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 1.25rem 1.25rem .5rem 1.25rem;
}
.stTextInput input {
    background: var(--bg) !important; border-radius: 10px !important;
    padding: .8rem 1rem !important; font-size: .98rem !important;
}
.stButton button[kind="primary"], .stFormSubmitButton button {
    background: linear-gradient(135deg, var(--accent), #5B63F0) !important;
    border: none !important; font-weight: 600 !important;
    border-radius: 10px !important; padding: .6rem 1.2rem !important;
    box-shadow: 0 6px 20px -8px rgba(124,131,255,.6);
}
.stButton button[kind="primary"]:hover { filter: brightness(1.08); }

/* ---------- Answer ---------- */
.st-key-answer_card {
    background: linear-gradient(180deg, rgba(124,131,255,.06), transparent 40%), var(--surface);
    border: 1px solid var(--border); border-left: 3px solid var(--accent);
    border-radius: 14px; padding: 1.4rem 1.6rem;
}
.st-key-answer_card p, .st-key-answer_card li { line-height: 1.7; font-size: .98rem; }
.answer-head {
    display: flex; align-items: center; justify-content: space-between;
    color: var(--muted); font-size: .78rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: .08em; margin-bottom: .5rem;
}

/* ---------- Chips ---------- */
.chips { display: flex; flex-wrap: wrap; gap: .5rem; }
.chip {
    display: inline-flex; align-items: center; gap: .45rem;
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: 999px; padding: .35rem .8rem; font-size: .82rem;
}
.chip .pg {
    color: var(--accent-2); font-weight: 600;
    font-family: 'JetBrains Mono', monospace; font-size: .75rem;
}
.chip .tp { color: var(--muted); font-size: .72rem; }

/* ---------- Graph paths ---------- */
.path {
    display: flex; flex-wrap: wrap; align-items: center; gap: .4rem;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: .7rem .9rem; margin-bottom: .55rem;
}
.path .idx {
    color: var(--muted); font-family: 'JetBrains Mono', monospace;
    font-size: .72rem; margin-right: .35rem;
}
.node {
    background: rgba(124,131,255,.12); border: 1px solid rgba(124,131,255,.35);
    color: #C7CAFF; border-radius: 8px; padding: .2rem .55rem;
    font-size: .82rem; font-weight: 500;
}
.rel {
    color: var(--accent-2); font-family: 'JetBrains Mono', monospace;
    font-size: .68rem; letter-spacing: .02em;
}

/* ---------- Evidence ---------- */
.ev {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem 1.15rem; margin-bottom: .75rem;
}
.ev-head {
    display: flex; justify-content: space-between; align-items: center;
    gap: 1rem; margin-bottom: .6rem;
}
.ev-src { font-weight: 600; font-size: .88rem; }
.ev-src span { color: var(--muted); font-weight: 400; }
.score { display: flex; align-items: center; gap: .5rem; min-width: 160px; }
.score-track {
    flex: 1; height: 6px; background: var(--border);
    border-radius: 999px; overflow: hidden;
}
.score-fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }
.score-num { font-family: 'JetBrains Mono', monospace; font-size: .75rem; color: var(--muted); }
.ev-text { color: #C5CAD8; font-size: .88rem; line-height: 1.65; white-space: pre-wrap; }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: .25rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { padding: .6rem 1rem; font-weight: 500; }

/* ---------- Empty state ---------- */
.empty {
    text-align: center; padding: 3.5rem 1rem;
    border: 1px dashed #34405A; border-radius: 16px; background: var(--surface);
}
.empty .ico { font-size: 2.2rem; }
.empty h3 { margin: .75rem 0 .35rem 0 !important; font-weight: 600 !important; }
.empty p { color: var(--muted); margin: 0; }

.footer {
    margin-top: 3rem; padding-top: 1.25rem; border-top: 1px solid var(--border);
    display: flex; flex-wrap: wrap; gap: .5rem; justify-content: center;
}
.footer .chip { color: var(--muted); font-size: .75rem; }
.muted { color: var(--muted); font-size: .88rem; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

@st.cache_resource
def get_pipeline():
    # Heavy imports (torch, sentence-transformers, Neo4j) are
    # deferred so the page can render before they finish.
    from src.pipeline.pdf_processing_pipeline import (
        PDFProcessingPipeline,
    )

    return PDFProcessingPipeline()


@st.cache_resource
def get_graphrag():
    from src.hybrid.pdf_graphrag import PDFGraphRAG

    return PDFGraphRAG()


def html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def section_title(text):
    html(
        f'<div class="section-title"><span class="bar"></span>'
        f"{escape(text)}</div>"
    )


def render_graph_path(index, path):
    nodes = path["nodes"]
    relationships = path["relationships"]

    parts = [f'<span class="idx">{index:02d}</span>']

    for position, node in enumerate(nodes):
        parts.append(
            f'<span class="node">'
            f'{escape(str(node.get("name", "Unknown")))}</span>'
        )

        if position < len(relationships):
            relation = relationships[position].get(
                "type", "RELATED_TO"
            )
            parts.append(
                f'<span class="rel">— {escape(str(relation))} →</span>'
            )

    html(f'<div class="path">{"".join(parts)}</div>')


def render_evidence(index, chunk):
    score = float(chunk["score"])
    width = max(0.0, min(score, 1.0)) * 100

    html(
        f"""
        <div class="ev">
            <div class="ev-head">
                <div class="ev-src">#{index} · {escape(str(chunk['source']))}
                    <span>· page {escape(str(chunk['page']))}</span></div>
                <div class="score">
                    <div class="score-track">
                        <div class="score-fill" style="width:{width:.0f}%"></div>
                    </div>
                    <span class="score-num">{score:.3f}</span>
                </div>
            </div>
            <div class="ev-text">{escape(str(chunk['text']))}</div>
        </div>
        """
    )


# --------------------------------------------------
# Data
# --------------------------------------------------

with st.spinner(
    "Loading models and connecting to the knowledge base "
    "(first start takes ~30s)..."
):
    pipeline = get_pipeline()

stats = pipeline.get_statistics()

has_knowledge_base = stats["chunks"] > 0


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    html(
        """
        <div class="sb-brand">
            <div class="sb-logo">🧠</div>
            <div>
                <div class="sb-title">GraphRAG</div>
                <div class="sb-sub">PDF Intelligence Console</div>
            </div>
        </div>
        """
    )

    html('<div class="sb-label">Knowledge sources</div>')

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    process_button = st.button(
        "Process documents",
        type="primary",
        icon=":material/bolt:",
        use_container_width=True,
    )

    html('<div class="sb-label">Retrieval settings</div>')

    top_k = st.slider(
        "Vector Top-K",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of vector chunks retrieved before graph expansion.",
    )


# --------------------------------------------------
# Hero
# --------------------------------------------------

status_dot = "on" if has_knowledge_base else "off"
status_text = (
    "Knowledge base ready"
    if has_knowledge_base
    else "Awaiting documents"
)

html(
    f"""
    <div class="hero">
        <span class="hero-badge">
            <span class="dot {status_dot}"></span>{status_text}
        </span>
        <h1>GraphRAG PDF Intelligence</h1>
        <p>Ask multi-hop questions across your documents. Answers combine
        dense vector retrieval with knowledge-graph reasoning, with every
        claim traced back to its source page.</p>
    </div>
    """
)


# --------------------------------------------------
# Knowledge base statistics
# --------------------------------------------------

kpis = [
    ("Documents", "📄", stats["documents"]),
    ("Pages", "📑", stats["pages"]),
    ("Chunks", "🧩", stats["chunks"]),
    ("Entities", "🔵", stats["entities"]),
    ("Relationships", "🔗", stats["relationships"]),
]

html(
    '<div class="kpi-grid">'
    + "".join(
        f'<div class="kpi"><div class="kpi-top">'
        f'<span class="kpi-label">{label}</span>'
        f'<span class="kpi-icon">{icon}</span></div>'
        f'<div class="kpi-value">{value:,}</div></div>'
        for label, icon, value in kpis
    )
    + "</div>"
)


# --------------------------------------------------
# Process uploaded documents
# --------------------------------------------------

if process_button:

    if not uploaded_files:

        st.toast(
            "Please upload at least one PDF.",
            icon=":material/warning:",
        )

    else:

        try:

            with st.status(
                "Processing documents...",
                expanded=True,
            ) as status:

                st.write("Reading and chunking PDFs...")
                st.write("Building vector index...")
                st.write("Extracting knowledge graph...")
                st.write("Loading graph into Neo4j...")

                pipeline.process_uploaded_files(
                    uploaded_files
                )

                status.update(
                    label="Documents processed successfully",
                    state="complete",
                    expanded=False,
                )

            # GraphRAG contains FAISS + graph state,
            # so clear the cached instance after rebuilding.
            get_graphrag.clear()

            st.session_state.pop("result", None)

            st.rerun()

        except Exception as error:

            st.error(
                f"Document processing failed: {error}",
                icon=":material/error:",
            )


# --------------------------------------------------
# Empty state
# --------------------------------------------------

if not has_knowledge_base:

    html(
        """
        <div class="empty">
            <div class="ico">📂</div>
            <h3>No documents indexed yet</h3>
            <p>Upload PDFs from the sidebar and click
            <b>Process documents</b> to build your knowledge base.</p>
        </div>
        """
    )

    st.stop()


# --------------------------------------------------
# Question answering
# --------------------------------------------------

section_title("Ask your documents")

with st.container(key="query_card"):

    with st.form("ask_form", border=False):

        input_col, button_col = st.columns(
            [6, 1],
            vertical_alignment="bottom",
        )

        with input_col:
            question = st.text_input(
                "Question",
                placeholder=(
                    "e.g. How does RAGChecker evaluate "
                    "the retriever and generator?"
                ),
                label_visibility="collapsed",
            )

        with button_col:
            ask_button = st.form_submit_button(
                "Ask",
                icon=":material/arrow_forward:",
                use_container_width=True,
            )


if ask_button:

    if not question.strip():

        st.toast(
            "Please enter a question.",
            icon=":material/warning:",
        )

    else:

        try:

            with st.spinner(
                "Searching vector and graph knowledge..."
            ):

                graphrag = get_graphrag()

                st.session_state["result"] = graphrag.answer(
                    question=question,
                    top_k=top_k,
                )

        except Exception as error:

            st.error(
                f"GraphRAG failed: {error}",
                icon=":material/error:",
            )


result = st.session_state.get("result")

if result:

    st.write("")

    # ------------------------------------------
    # Answer
    # ------------------------------------------

    with st.container(key="answer_card"):

        html(
            f'<div class="answer-head"><span>Answer</span>'
            f'<span>{len(result["sources"])} sources · '
            f'{len(result["graph_paths"])} graph paths</span></div>'
        )

        st.markdown(result["answer"])

    st.write("")

    # ------------------------------------------
    # Details tabs
    # ------------------------------------------

    sources_tab, graph_tab, evidence_tab = st.tabs(
        [
            f":material/description: Sources ({len(result['sources'])})",
            f":material/hub: Graph reasoning ({len(result['graph_paths'])})",
            f":material/manage_search: Vector evidence ({len(result['vector_results'])})",
        ]
    )

    with sources_tab:

        if result["sources"]:

            html(
                '<div class="chips">'
                + "".join(
                    f'<span class="chip">📄 {escape(str(source["source"]))}'
                    f'<span class="pg">p.{escape(str(source["page"]))}</span></span>'
                    for source in result["sources"]
                )
                + "</div>"
            )

        else:

            html('<p class="muted">No source information available.</p>')

    with graph_tab:

        if result["matched_entities"]:

            html('<div class="sb-label">Matched entities</div>')

            html(
                '<div class="chips">'
                + "".join(
                    f'<span class="chip">{escape(str(entity["name"]))}'
                    f'<span class="tp">{escape(str(entity["type"]))}</span></span>'
                    for entity in result["matched_entities"]
                )
                + "</div>"
            )

        html('<div class="sb-label">Reasoning paths</div>')

        if result["graph_paths"]:

            for index, path in enumerate(
                result["graph_paths"][:12],
                start=1,
            ):
                render_graph_path(index, path)

        else:

            html('<p class="muted">No graph paths retrieved.</p>')

    with evidence_tab:

        for index, chunk in enumerate(
            result["vector_results"],
            start=1,
        ):
            render_evidence(index, chunk)


# --------------------------------------------------
# Footer
# --------------------------------------------------

html(
    '<div class="footer">'
    + "".join(
        f'<span class="chip">{name}</span>'
        for name in [
            "Hybrid GraphRAG",
            "FAISS",
            "Neo4j",
            "Sentence Transformers",
            "NVIDIA NIM",
        ]
    )
    + "</div>"
)
