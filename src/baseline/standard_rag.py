import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(
    str(PROJECT_ROOT / "src" / "vector")
)

sys.path.append(
    str(PROJECT_ROOT / "src" / "generation")
)


from retriever import VectorRetriever
from answer_generator import AnswerGenerator


class StandardRAG:

    def __init__(
        self,
        top_k: int = 5
    ):

        self.top_k = top_k

        self.retriever = VectorRetriever()

        self.generator = AnswerGenerator()

    def answer(
        self,
        question: str
    ) -> dict:

        retrieved_chunks = (
            self.retriever.retrieve(
                question,
                k=self.top_k
            )
        )

        generated_answer = (
            self.generator.generate(
                question,
                retrieved_chunks
            )
        )

        return {
            "question": question,
            "answer": generated_answer,
            "retrieved_chunks": retrieved_chunks
        }