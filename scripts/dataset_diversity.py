#!/usr/bin/env python3

import json
from collections import Counter
from pathlib import Path

INPUT = Path("data/raw/livefire_20.jsonl")

def main() -> int:
    instructions = Counter()
    responses = Counter()
    options = Counter()
    total = 0

    with INPUT.open(encoding="utf-8") as handle:
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
