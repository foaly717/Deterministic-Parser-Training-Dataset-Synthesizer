#!/usr/bin/env python3

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

from dataset_tools.generator.prompt import build_candidate_prompt
from dataset_tools.generator.runner import validate_candidate_structure
from dataset_tools.parsers.cli_help import parse_cli_help
from dataset_tools.validators.command import validate_cli_command
from dataset_tools.validators.options import validate_cli_response


DEFAULT_ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
DEFAULT_HELP = Path("data/evidence/handbrakecli-help.txt")
DEFAULT_OUTPUT = Path("data/raw/livefire_20.jsonl")


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request_model(endpoint: str, prompt: str, model: str, max_tokens: int) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        data = json.loads(response.read())
    return data["choices"][0]["message"]["content"]


def parse_model_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--help-file", type=Path, default=DEFAULT_HELP)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args()

    facts = parse_cli_help(args.help_file)
    valid_options = {
        option
        for fact in facts
        for option in [fact.name, *fact.aliases]
    }
    tools = {fact.tool for fact in facts if fact.tool}

    if len(tools) != 1:
        raise ValueError(
            f"Expected exactly one documented tool, found: {sorted(tools)}"
        )

    expected_tool = next(iter(tools))
    sha256 = source_sha256(args.help_file)
    prompt = build_candidate_prompt(facts, sample_size=20)
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
                raw = request_model(args.endpoint, prompt, args.model, 1024)
                record["raw_response"] = raw
                parsed = parse_model_json(raw)
                record["parsed"] = parsed
            except Exception as exc:
                record["validation"] = f"JSON/request failure: {exc}"
                parse_rejections += 1
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                print(f"{attempt + 1:02d}: PARSE/REQUEST REJECTED — {exc}")
                continue

            items = parsed if isinstance(parsed, list) else [parsed]
            valid_items = 0

            for item in items:
                if not validate_candidate_structure(item):
                    structural_rejections += 1
                    continue

                valid_items += 1
                record["structurally_valid"] = True

                command_ok, command_message = validate_cli_command(
                    item["response"],
                    expected_tool,
                )

                if not command_ok:
                    command_rejections += 1
                    record["validation"] = command_message
                    continue

                record["command_valid"] = True

                option_ok, option_message = validate_cli_response(
                    item["response"],
                    valid_options,
                )

                if not option_ok:
                    option_rejections += 1
                    record["validation"] = option_message
                    continue

                accepted += 1
                record["status"] = "accepted"
                record["option_valid"] = True
                record["validation"] = option_message

            if valid_items == 0:
                structural_rejections += 1
                record["validation"] = "No structurally valid candidates."

            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(attempt + 1, record["status"].upper(), valid_items)

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
