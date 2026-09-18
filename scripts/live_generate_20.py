#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path

from dataset_tools.config.settings import get_settings
from dataset_tools.llm import create_llm_client

from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.index import build_evidence_index
from dataset_tools.generator.planner import select_generation_fact
from dataset_tools.generator.prompt import build_single_fact_prompt
from dataset_tools.validators.pipeline import validate_candidate



DEFAULT_HELP = Path("data/evidence/handbrakecli-help.txt")
DEFAULT_OUTPUT = Path("data/raw/livefire_20.jsonl")


def parse_model_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    settings = get_settings()

    parser.add_argument("--provider", default=settings.provider)
    parser.add_argument("--model", default=settings.model)
    parser.add_argument("--endpoint", default=settings.endpoint)
    parser.add_argument("--help-file", type=Path, default=DEFAULT_HELP)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args()

    client = create_llm_client(
        provider=args.provider,
        endpoint=args.endpoint,
        model=args.model,
    )

    document = load_evidence(args.help_file)
    evidence_index = build_evidence_index(document)

    # Restrict to cli_option facts for both tool detection and generation —
    # the constraint fact's subject is an option name (e.g. "--preset"), not
    # a tool name, and would corrupt the tool-uniqueness check below if included.
    cli_option_facts = [fact for fact in document.facts if fact.category == "cli_option"]

    tools = {fact.subject for fact in cli_option_facts if fact.subject}
    if len(tools) != 1:
        raise ValueError(f"Expected exactly one documented tool, found: {sorted(tools)}")

    expected_tool = next(iter(tools))
    sha256 = document.source.sha256
    args.output.parent.mkdir(parents=True, exist_ok=True)

    accepted = 0
    structural_rejections = 0
    command_rejections = 0
    option_rejections = 0
    parse_rejections = 0

    with args.output.open("w", encoding="utf-8") as handle:
        for attempt in range(args.count):
            record = {
                "attempt": attempt + 1,
                "source_sha256": sha256,
                "generator_provider": args.provider,
                "generator_model": args.model,
                "raw_response": None,
                "parsed": None,
                "structurally_valid": False,
                "command_valid": False,
                "option_valid": False,
                "status": "rejected",
                "validation": None,
            }

            try:
                fact = select_generation_fact(cli_option_facts, attempt)
                prompt = build_single_fact_prompt(fact)
                raw = client.generate(prompt, 1024)
                record["raw_response"] = raw
                parsed = parse_model_json(raw)
                record["parsed"] = parsed
            except Exception as exc:
                record["validation"] = f"JSON/request failure: {exc}"
                parse_rejections += 1
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                print(f"{attempt + 1:02d}: PARSE/REQUEST REJECTED — {exc}")
                continue

            if not isinstance(parsed, dict):
                record["validation"] = "JSON output must be exactly one object."
                parse_rejections += 1
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                print(f"{attempt + 1:02d}: JSON SHAPE REJECTED")
                continue

            result = validate_candidate(parsed, expected_tool, evidence_index)

            record["validation"] = result.validation_logs

            if result.stage != "structure":
                record["structurally_valid"] = True

            if result.status != "accepted":
                if result.stage == "structure":
                    structural_rejections += 1
                elif result.stage == "command":
                    command_rejections += 1
                elif result.stage == "options":
                    option_rejections += 1
            else:
                accepted += 1
                record["status"] = "accepted"
                record["command_valid"] = True
                record["option_valid"] = True

            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(attempt + 1, record["status"].upper())

    print()
    print("=== LIVEFIRE SUMMARY ===")
    print(f"Attempts:              {args.count}")
    print(f"Accepted:              {accepted}")
    print(f"Parse/request rejects: {parse_rejections}")
    print(f"Structural rejects:    {structural_rejections}")
    print(f"Command rejects:       {command_rejections}")
    print(f"Option rejects:        {option_rejections}")
    print(f"Report:                {args.output}")
    print(f"Evidence SHA-256:      {sha256}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
