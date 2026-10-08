import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class NvidiaLLM:

    def __init__(
        self,
        model_name: str = "openai/gpt-oss-20b"
    ):

        api_key = os.getenv("NVIDIA_API_KEY")

        if not api_key:
            raise ValueError(
                "NVIDIA_API_KEY not found in .env"
            )

        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            # Parallel extraction can hit rate limits (429);
            # the SDK retries with exponential backoff.
            max_retries=6,
            timeout=120,
        )

        self.model_name = model_name

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model_name,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.1,
            top_p=1,
            max_tokens=max_tokens,
            stream=False
        )

        message = response.choices[0].message

        # Normal final response
        if message.content:
            return message.content.strip()

        # Helpful debugging if NVIDIA returns no final content
        reasoning = getattr(
            message,
            "reasoning_content",
            None
        )

        if reasoning:
            raise ValueError(
                "NVIDIA returned reasoning but no final answer. "
                "The model may have used the token budget for reasoning.\n\n"
                f"Reasoning output:\n{reasoning}"
            )

        raise ValueError(
            "NVIDIA returned an empty response.\n"
            f"Full message: {message}"
        )