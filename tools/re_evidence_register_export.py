#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dated export of the campaign register -> tracked EVIDENCE-REGISTER.tsv.

The per-entity register (campaign ledgers + frozen reducer) is the machine-
owned authority and stays under local-lab/. This exporter publishes a dated,
tracked one-row-per-entity view so that a fresh clone - or any reviewer who
is not the maintainer on this machine - can resolve where each function's
evidence lives, without importing the register itself. The header states the
export is stale the moment the next generation lands.

Usage:
    python tools/re_evidence_register_export.py \
        --campaign <tip campaign dir> --out reverse-engineering/EVIDENCE-REGISTER.tsv
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import re_campaign as campaign  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build(campaign_dir: Path) -> dict[str, object]:
    ready_path = campaign_dir / "campaign.ready.json"
    if not ready_path.is_file():
        raise SystemExit(f"campaign READY missing: {ready_path}")
    receipt = json.loads(ready_path.read_text(encoding="utf-8"))
    functions = campaign._campaign_rows_from_root(campaign_dir)["functions"]
    rows = []
    for fn in functions:
        rows.append(
            {
                "entryVa": fn.get("entryVa", ""),
                "name": fn.get("currentName", ""),
                "grade": fn.get("semanticGrade", ""),
                "resolution": fn.get("resolutionState", ""),
                "contractState": fn.get("campaignState", ""),
                "evidence": fn.get("evidenceStates", ""),
                "generation": receipt.get("generation", ""),
                "readySha256": hashlib.sha256(ready_path.read_bytes()).hexdigest(),
            }
        )
    rows.sort(key=lambda r: r["entryVa"])
    return {"rows": rows, "receipt": receipt}


def render(rows: list[dict[str, object]], generation: int, ready_sha: str, when: str) -> str:
    lines = [
        "# bea.re.evidence-register.v1",
        f"# generatedAtUtc: {when}",
        f"# generation: {generation}",
        f"# readySha256: {ready_sha}",
        "# DATED EXPORT of the machine-owned campaign register. The frozen",
        "# reducer and campaign.ready.json are authority; this file is a",
        "# convenience view and is STALE the moment the next generation lands.",
        "# Regenerate with tools/re_evidence_register_export.py.",
        "\t".join(
            ["entryVa", "name", "grade", "resolution", "contractState", "evidence", "generation", "readySha256"]
        ),
    ]
    for r in rows:
        lines.append(
            "\t".join(
                [
                    r["entryVa"],
                    r["name"].replace("\t", " "),
                    r["grade"],
                    r["resolution"],
                    r["contractState"],
                    r["evidence"].replace("\t", " "),
                    str(r["generation"]),
                    r["readySha256"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--campaign",
        type=Path,
        default=Path(
            "local-lab/function-c1-opaque-squad-spawn-helpers-batch-generation73-20260806-v1/"
            "generation-73-function-c1-opaque-squad-spawn-helpers-batch"
        ),
    )
    parser.add_argument(
        "--out", type=Path, default=Path("reverse-engineering/EVIDENCE-REGISTER.tsv")
    )
    args = parser.parse_args(argv)
    result = build(args.campaign)
    ready_sha = result["receipt"].get("readySha256", "") or hashlib.sha256(
        (args.campaign / "campaign.ready.json").read_bytes()
    ).hexdigest()
    generation = result["receipt"].get("generation", "")
    text = render(result["rows"], generation, ready_sha, utc_now())
    args.out.write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(result['rows'])} rows -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
