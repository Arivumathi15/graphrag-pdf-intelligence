import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


sys.path.append(
    str(
        PROJECT_ROOT
        / "src"
        / "generation"
    )
)


from llm import NvidiaLLM
from extraction_prompt import build_extraction_prompt


class GraphExtractor:

    def __init__(self):

        self.llm = NvidiaLLM()

    def extract(
        self,
        chunk: dict
    ) -> dict:

        prompt = build_extraction_prompt(
            chunk["text"]
        )

        response = self.llm.generate(
            prompt,
            max_tokens=2048
        )

        try:

            graph_data = json.loads(
                response
            )

        except json.JSONDecodeError:

            raise ValueError(
                "NVIDIA returned invalid JSON:\n"
                + response
            )

        # Attach provenance
        graph_data["chunk_id"] = (
            chunk["chunk_id"]
        )

        graph_data["source"] = (
            chunk["source"]
        )

        return graph_data