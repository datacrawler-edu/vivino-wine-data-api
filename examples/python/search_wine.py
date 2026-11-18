"""Run the small Barolo search and print each confirmed vintage row."""

import json
from pathlib import Path

from client import collect


ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data" / "sample-input.json"


def main() -> None:
    run_input = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    _, run, summary, rows = collect(run_input)
    print("Run " + run.id + ": " + str(summary["status"]))
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
