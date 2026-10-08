from llm import NvidiaLLM


def main():

    llm = NvidiaLLM()

    response = llm.generate(
        "What is a knowledge graph? "
        "Answer in one sentence."
    )

    print("\nNVIDIA RESPONSE")
    print(response)


if __name__ == "__main__":
    main()