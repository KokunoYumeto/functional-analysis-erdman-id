#!/usr/bin/env python3
"""Apply the adjudicated whole-edition spelling for Indonesian self-adjoint."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_COUNTS = {
    ROOT / "source" / "id-ID" / "Gelfand_Naimark-id.tex": 7,
    ROOT / "source" / "id-ID" / "no_identity-id.tex": 18,
    ROOT / "qa" / "ch12_translation_part_a.tex": 7,
    ROOT / "qa" / "ch12_translation_part_b.tex": 11,
    ROOT / "provenance" / "CH11_TERMINOLOGY_DECISIONS.md": 2,
    ROOT / "provenance" / "CH12_TERMINOLOGY_PLAN.md": 2,
    ROOT / "qa" / "CH11_INDONESIAN_TERMINOLOGY_EXTERNAL_QA.md": 3,
}
TERMINOLOGY = ROOT / "backend" / "terminology.jsonl"


def main() -> None:
    for path, expected in TEXT_COUNTS.items():
        data = path.read_bytes()
        if b"\r" in data or data.startswith(b"\xef\xbb\xbf"):
            raise SystemExit(f"unexpected encoding/line endings: {path}")
        text = data.decode("utf-8")
        count = text.count("swadjoin")
        if count != expected:
            raise SystemExit(f"unexpected swadjoin count in {path}: {count} != {expected}")
        path.write_text(text.replace("swadjoin", "swaadjoin"), encoding="utf-8", newline="\n")

    lines = TERMINOLOGY.read_text(encoding="utf-8").splitlines()
    changed = 0
    output: list[str] = []
    for line in lines:
        record = json.loads(line)
        if record.get("id") == "TERM-SELF-ADJOINT":
            if record.get("preferred") != "swadjoin" or record.get("variants") != ["adjoin-diri"]:
                raise SystemExit("TERM-SELF-ADJOINT baseline differs")
            record["preferred"] = "swaadjoin"
            record["variants"] = ["swadjoin", "adjoin-diri"]
            changed += 1
        output.append(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
    if changed != 1:
        raise SystemExit(f"TERM-SELF-ADJOINT match count differs: {changed}")
    TERMINOLOGY.write_text("\n".join(output) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
