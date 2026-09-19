from dataset_tools.llm.client import LLMClient


class MockLLMClient(LLMClient):
    """Deterministic LLM test double returning one valid candidate."""

    def __init__(
        self,
        response: str | None = None,
    ):
        self.response = response or (
            '{"instruction":"Use the documented option.",'
            '"context":null,'
            '"response":"HandBrakeCLI --preset Test"}'
        )
        self.calls: list[tuple[str, int]] = []

    def generate(
        self,
        prompt: str,
        max_tokens: int,
    ) -> str:
        self.calls.append((prompt, max_tokens))
        return self.response
