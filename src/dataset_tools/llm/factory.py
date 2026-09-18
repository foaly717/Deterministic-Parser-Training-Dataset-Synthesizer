from dataset_tools.llm.client import OpenAICompatibleClient
from dataset_tools.llm.mock import MockLLMClient


def create_llm_client(
    provider: str,
    endpoint: str,
    model: str,
):
    if provider == "openai_compatible":
        return OpenAICompatibleClient(
            endpoint=endpoint,
            model=model,
        )

    if provider == "mock":
        return MockLLMClient()

    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )
