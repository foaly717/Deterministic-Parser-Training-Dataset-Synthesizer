from dataset_tools.llm.client import LLMClient


class MockLLMClient(LLMClient):
    def generate(
        self,
        prompt: str,
        max_tokens: int,
    ) -> str:
        return '{"command": "fake"}'
