import json
import urllib.request
from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int,
    ) -> str:
        raise NotImplementedError


class OpenAICompatibleClient(LLMClient):
    def __init__(
        self,
        endpoint: str,
        model: str,
    ):
        self.endpoint = endpoint
        self.model = model

    def generate(
        self,
        prompt: str,
        max_tokens: int,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0,
            "max_tokens": max_tokens,
        }

        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=180,
        ) as response:
            data = json.loads(response.read())

        return data["choices"][0]["message"]["content"]
