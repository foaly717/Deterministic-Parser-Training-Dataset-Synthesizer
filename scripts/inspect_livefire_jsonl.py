from pathlib import Path
import json

path = Path("data/raw/livefire_20.jsonl")
decoder = json.JSONDecoder()

for n, line in enumerate(path.read_text().splitlines(), 1):
    line = line.strip()
    if not line:
        continue

    pos = 0
    records_in_line = []

    while pos < len(line):
        while pos < len(line) and line[pos].isspace():
            pos += 1
        if pos >= len(line):
            break

        try:
            obj, end = decoder.raw_decode(line, pos)
            records_in_line.append(obj)
            pos = end
        except json.JSONDecodeError:
            print(
                f"[Line {n}] Unparseable tail starting at char {pos}: "
                f"{line[pos:pos+100]!r}"
            )
            break

    print(f"Line {n}: Parsed {len(records_in_line)} object(s).")
    for r in records_in_line:
        print(
            f"  Attempt: {r.get('attempt')} | "
            f"Status: {r.get('status')} | "
            f"Validation: {r.get('validation')}"
        )
