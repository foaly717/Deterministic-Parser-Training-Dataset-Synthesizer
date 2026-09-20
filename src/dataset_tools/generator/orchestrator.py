"""Generator orchestration with an explicit raw-generation boundary."""

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
class RawGenerationResult:
    """Exact rendered prompt and raw model response."""

    prompt: str
    raw_output: str


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

    def _prepare_prompt(
        self,
        prepared: PreparedEvidence,
        request: GenerationRequest,
    ) -> str:
        if request.max_tokens < 1:
            raise ValueError("max_tokens must be >= 1")

        facts_by_id = {
            fact.fact_id: fact
            for fact in prepared.cli_option_facts
        }

        if request.fact_id not in facts_by_id:
            raise KeyError(
                "Requested fact_id is not present in prepared evidence: "
                f"{request.fact_id}"
            )

        return build_single_fact_prompt(facts_by_id[request.fact_id])

    def generate_raw(
        self,
        prepared: PreparedEvidence,
        request: GenerationRequest,
    ) -> RawGenerationResult:
        """Execute exactly one model call without parsing its response."""
        prompt = self._prepare_prompt(prepared, request)
        raw_output = self.llm_client.generate(
            prompt,
            request.max_tokens,
        )
        return RawGenerationResult(
            prompt=prompt,
            raw_output=raw_output,
        )

    def generate(
        self,
        prepared: PreparedEvidence,
        request: GenerationRequest,
    ) -> GenerationResult:
        """Execute generation and parse the returned candidate exactly once."""
        raw_result = self.generate_raw(prepared, request)
        candidate = parse_candidate(raw_result.raw_output)

        return GenerationResult(
            prompt=raw_result.prompt,
            raw_output=raw_result.raw_output,
            candidate=candidate,
        )
