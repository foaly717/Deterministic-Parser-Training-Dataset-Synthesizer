#!/usr/bin/env python3

import argparse
import json
import re
import sys
import threading
import time
from pathlib import Path

from dataset_tools.config.settings import get_settings
from dataset_tools.llm import create_llm_client

from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.index import build_evidence_index
from dataset_tools.generator.planner import select_generation_fact
from dataset_tools.generator.prompt import build_single_fact_prompt
from dataset_tools.validators.pipeline import validate_candidate
from dataset_tools.validators.serialization import (
    serialize_validation_failure,
    serialize_validation_result,
)


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
    parser.add_argument("--help-file", type=Path, default=settings.help_file)
    parser.add_argument("--output", type=Path, default=settings.output)
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
    cli_option_facts = [
        fact for fact in document.facts
        if fact.category == "cli_option"
    ]

    tools = {fact.subject for fact in cli_option_facts if fact.subject}
    if len(tools) != 1:
        raise ValueError(
            f"Expected exactly one documented tool, found: {sorted(tools)}"
        )

    expected_tool = next(iter(tools))
    sha256 = document.source_sha256
    args.output.parent.mkdir(parents=True, exist_ok=True)

    accepted = 0
    structural_rejections = 0
    command_rejections = 0
    option_rejections = 0
    parse_rejections = 0

    tried_commands: list[tuple[int, str, str]] = []

    print()
    print("=== LIVE GENERATION ===")
    print(f"Model: {args.model}")
    print(f"Count: {args.count}")
    print()

    with args.output.open("w", encoding="utf-8") as handle:
        tried_header_printed = False

        for attempt in range(args.count):
            record = {
                "attempt": attempt + 1,
                "source_sha256": sha256,
                "generator_provider": args.provider,
                "generator_model": args.model,
                "raw_response": None,
                "parsed": None,
                "validation": None,
            }

            elapsed = 0.0
            command_display = "<no valid command>"

            try:
                fact = select_generation_fact(cli_option_facts, attempt)
                prompt = build_single_fact_prompt(fact)

                stop_timer = threading.Event()
                start_time = time.monotonic()

                def show_progress() -> None:
                    while not stop_timer.wait(1.0):
                        elapsed_now = time.monotonic() - start_time
                        sys.stdout.write(
                            f"\rCandidate: {attempt + 1:02d}/{args.count} | "
                            f"generating | elapsed: {elapsed_now:.1f}s"
                        )
                        sys.stdout.flush()

                sys.stdout.write(
                    f"Candidate: {attempt + 1:02d}/{args.count} | "
                    f"generating | elapsed: 0.0s"
                )
                sys.stdout.flush()

                timer_thread = threading.Thread(
                    target=show_progress,
                    daemon=True,
                )
                timer_thread.start()

                try:
                    raw = client.generate(prompt, 1024)
                finally:
                    stop_timer.set()
                    timer_thread.join()

                elapsed = time.monotonic() - start_time
                record["raw_response"] = raw
                parsed = parse_model_json(raw)
                record["parsed"] = parsed

            except Exception as exc:
                sys.stdout.write("\r")
                sys.stdout.flush()

                record["validation"] = serialize_validation_failure(
                    stage="parse",
                    reason_code="INVALID_JSON",
                    message=f"JSON/request failure: {exc}",
                )
                parse_rejections += 1

                handle.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

                tried_commands.append(
                    (
                        attempt + 1,
                        "REJECTED",
                        "<no valid command: JSON/request failure>",
                    )
                )

                print(
                    f"Candidate: {attempt + 1:02d}/{args.count} | "
                    f"complete | {elapsed:.1f}s | "
                    f"PARSE/REQUEST REJECTED — {exc}"
                )
                if not tried_header_printed:
                    print()
                    print("=== TRIED COMMANDS ===")
                    tried_header_printed = True

                print(
                    f"{attempt + 1:02d} REJECTED  | "
                    f"<no valid command: JSON/request failure>"
                )
                continue

            if not isinstance(parsed, dict):
                record["validation"] = serialize_validation_failure(
                    stage="parse",
                    reason_code="INVALID_JSON_SHAPE",
                    message="JSON output must be exactly one object.",
                )
                parse_rejections += 1

                handle.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

                tried_commands.append(
                    (
                        attempt + 1,
                        "REJECTED",
                        "<no valid command: invalid JSON shape>",
                    )
                )

                print(
                    f"Candidate: {attempt + 1:02d}/{args.count} | "
                    f"complete | {elapsed:.1f}s | "
                    f"JSON SHAPE REJECTED"
                )
                if not tried_header_printed:
                    print()
                    print("=== TRIED COMMANDS ===")
                    tried_header_printed = True

                print(
                    f"{attempt + 1:02d} REJECTED  | "
                    f"<no valid command: invalid JSON shape>"
                )
                continue

            result = validate_candidate(
                parsed,
                expected_tool,
                evidence_index,
            )

            record["validation"] = serialize_validation_result(
                result,
            )

            if isinstance(parsed.get("response"), str):
                command_display = parsed["response"].strip() or "<empty command>"

            if result.status != "accepted":
                if result.stage == "structure":
                    structural_rejections += 1
                elif result.stage == "command":
                    command_rejections += 1
                elif result.stage == "options":
                    option_rejections += 1

                status = "REJECTED"
            else:
                accepted += 1
                status = "ACCEPTED"

            handle.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

            tried_commands.append(
                (
                    attempt + 1,
                    status,
                    command_display,
                )
            )

            print(
                f"Candidate: {attempt + 1:02d}/{args.count} | "
                f"complete | {elapsed:.1f}s | {status}"
            )

            if not tried_header_printed:
                print()
                print("=== TRIED COMMANDS ===")
                tried_header_printed = True

            print(
                f"{attempt + 1:02d} {status:<10} | "
                f"{command_display}"
            )

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
