from dataclasses import dataclass

from dataset_tools.candidates.parser import parse_candidate
from dataset_tools.evidence.preparation import PreparedEvidence
from dataset_tools.generator.prompt import build_single_fact_prompt
from dataset_tools.llm.client import LLMClient


@dataclass(frozen=True)
class GenerationRequest:
    """Inputs controlling one deterministic generation attempt."""

    fact_id: str
    max_tokens: int = 512


@dataclass(frozen=True)
class GenerationResult:
    """Raw and parsed output from one generation attempt."""

    prompt: str
    raw_output: str
    candidate: dict


class Generator:
    """Orchestrate one grounded candidate-generation attempt."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate(
        self,
        prepared: PreparedEvidence,
        request: GenerationRequest,
    ) -> GenerationResult:
        if request.max_tokens < 1:
            raise ValueError("max_tokens must be >= 1")

        facts_by_id = {
            fact.fact_id: fact
            for fact in prepared.cli_option_facts
        }

        fact_id = request.fact_id

        if fact_id not in facts_by_id:
            raise KeyError(
                "Requested fact_id is not present in prepared evidence: "
                f"{fact_id}"
            )

        fact = facts_by_id[fact_id]

        prompt = build_single_fact_prompt(fact)
        raw_output = self.llm_client.generate(
            prompt,
            request.max_tokens,
        )
        candidate = parse_candidate(raw_output)

        return GenerationResult(
            prompt=prompt,
            raw_output=raw_output,
            candidate=candidate,
        )
