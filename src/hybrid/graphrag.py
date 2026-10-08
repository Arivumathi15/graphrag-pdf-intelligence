import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(
    str(PROJECT_ROOT / "src" / "graph")
)

sys.path.append(
    str(PROJECT_ROOT / "src" / "vector")
)

sys.path.append(
    str(PROJECT_ROOT / "src" / "generation")
)


from neo4j_client import Neo4jClient
from entity_linker import EntityLinker
from query_analyzer import QueryAnalyzer
from graph_retriever import GraphRetriever
from graph_context import build_graph_context

from retriever import VectorRetriever

from llm import NvidiaLLM

from context_fusion import (
    build_vector_context,
    fuse_contexts
)

from graphrag_prompt import (
    build_graphrag_prompt
)


class GraphRAG:

    def __init__(
        self,
        top_k: int = 5
    ):

        self.top_k = top_k

        # Vector components
        self.vector_retriever = (
            VectorRetriever()
        )

        # Graph components
        self.neo4j_client = (
            Neo4jClient()
        )

        self.entity_linker = (
            EntityLinker(
                self.neo4j_client
            )
        )

        self.query_analyzer = (
            QueryAnalyzer()
        )

        self.graph_retriever = (
            GraphRetriever(
                self.neo4j_client
            )
        )

        # Generation component
        self.llm = NvidiaLLM()

    def answer(
        self,
        question: str
    ) -> dict:

        # --------------------------------
        # 1. Vector retrieval
        # --------------------------------

        vector_results = (
            self.vector_retriever.retrieve(
                question,
                k=self.top_k
            )
        )

        vector_context = (
            build_vector_context(
                vector_results
            )
        )

        # --------------------------------
        # 2. Entity linking
        # --------------------------------

        linked_entities = (
            self.entity_linker
            .find_entities_in_question(
                question
            )
        )

        # --------------------------------
        # 3. Graph retrieval
        # --------------------------------

        graph_results = []
        query_plan = None

        if linked_entities:

            query_plan = (
                self.query_analyzer.analyze(
                    question,
                    linked_entities
                )
            )

            graph_results = (
                self.graph_retriever
                .execute_plan(
                    start_entity=query_plan[
                        "start_entity"
                    ],
                    relationships=query_plan[
                        "relationships"
                    ]
                )
            )

        # --------------------------------
        # 4. Graph context
        # --------------------------------

        graph_context = (
            build_graph_context(
                graph_results
            )
        )

        # --------------------------------
        # 5. Context fusion
        # --------------------------------

        fused_context = (
            fuse_contexts(
                vector_context,
                graph_context
            )
        )

        # --------------------------------
        # 6. Build generation prompt
        # --------------------------------

        prompt = (
            build_graphrag_prompt(
                question,
                fused_context
            )
        )

        # --------------------------------
        # 7. Generate answer
        # --------------------------------

        answer = self.llm.generate(
            prompt,
            max_tokens=512
        )

        # --------------------------------
        # 8. Return useful debug info
        # --------------------------------

        return {
            "question": question,
            "answer": answer,
            "linked_entities": linked_entities,
            "query_plan": query_plan,
            "graph_results": graph_results,
            "vector_results": vector_results,
            "graph_context": graph_context,
            "vector_context": vector_context,
            "fused_context": fused_context
        }

    def close(self):

        self.neo4j_client.close()