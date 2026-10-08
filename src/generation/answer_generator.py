from prompt_builder import build_rag_prompt
from llm import NvidiaLLM


class AnswerGenerator:

    def __init__(self):

        self.llm = NvidiaLLM()

    def generate(
        self,
        question: str,
        retrieved_chunks: list[dict]
    ) -> str:

        prompt = build_rag_prompt(
            question,
            retrieved_chunks
        )

        answer = self.llm.generate(
            prompt
        )

        return answer