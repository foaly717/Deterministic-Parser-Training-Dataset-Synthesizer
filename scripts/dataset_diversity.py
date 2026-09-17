#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    instructions = Counter()
    responses = Counter()
    options = Counter()
    total = 0

    with args.input.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            parsed = record.get("parsed")
            if not isinstance(parsed, dict):
                continue
            total += 1
            instructions[parsed["instruction"]] += 1
            responses[parsed["response"]] += 1
            for token in parsed["response"].split():
                if token.startswith("-"):
                    options[token] += 1

    print("=== DATASET DIVERSITY REPORT ===")
    print(f"Accepted records: {total}")
    print(f"Unique instructions: {len(instructions)}")
    print(f"Unique responses: {len(responses)}")
    print(f"Unique options: {len(options)}")
    print()
    print("Top options:")
    for option, count in options.most_common(20):
        print(f"  {option}: {count}")

    duplicates = sum(v - 1 for v in responses.values() if v > 1)
    print()
    print(f"Duplicate responses: {duplicates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
