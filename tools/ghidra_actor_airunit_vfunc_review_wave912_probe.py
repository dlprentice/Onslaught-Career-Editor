#!/usr/bin/env python3
"""Validate Wave912 actor/air-unit vfunc review and CActor::StickToGround correction evidence."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave912-actor-airunit-vfunc-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_actor_airunit_vfunc_review_wave912_2026-05-27.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
ACTOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Actor.cpp" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str] | None:
    want = addr.lower().replace("0x", "")
    for row in rows:
        got = (row.get("address") or row.get("target_addr") or "").lower().replace("0x", "")
        if got == want:
            return row
    return None


def token(text: str, value: str) -> bool:
    return "".join(value.lower().split()) in "".join(text.lower().split())


def build_report() -> dict[str, object]:
    failures: list[str] = []
    post_metadata = read_tsv(BASE / "post_metadata.tsv")
    post_tags = read_tsv(BASE / "post_tags.tsv")
    post_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")

    actor = row_by_addr(post_metadata, "0x00402030")
    if actor is None:
        failures.append("missing post metadata for 0x00402030")
    else:
        checks = {
            "name": actor.get("name") == "CActor__StickToGround",
            "signature": actor.get("signature") == "void __thiscall CActor__StickToGround(void * this)",
            "comment_source": token(actor.get("comment", ""), "CActor::StickToGround"),
            "comment_oldpos": token(actor.get("comment", ""), "mOldPos=mPos"),
        }
        for name, ok in checks.items():
            if not ok:
                failures.append(f"actor metadata check failed: {name}")

    tag_row = row_by_addr(post_tags, "0x00402030")
    if tag_row is None:
        failures.append("missing post tags for 0x00402030")
    else:
        for required in ("actor-sticktoground-wave912", "wave912-readback-verified", "source-backed-name", "name-corrected"):
            if required not in tag_row.get("tags", ""):
                failures.append(f"missing tag {required}")

    decomp_row = row_by_addr(post_index, "0x00402030")
    if decomp_row is None or decomp_row.get("name") != "CActor__StickToGround" or decomp_row.get("status") != "OK":
        failures.append("post decompile index does not confirm CActor__StickToGround")

    instr_text = "\n".join("\t".join(row.values()) for row in instructions)
    for required in ("CALL\t0x004f3c50", "LEA\tEAX, [ESI + 0x1c]", "ADD\tESI, 0x8c", "RET"):
        if required not in instr_text:
            failures.append(f"instruction token missing: {required}")

    final_dry = read_text(BASE / "apply_final_dry.log")
    final_dry_compact = " ".join(final_dry.split())
    if "SKIP: 0x00402030 CActor__StickToGround" not in final_dry_compact:
        failures.append("final dry-run did not skip corrected target")
    if "missing=0 bad=0" not in final_dry_compact:
        failures.append("final dry-run summary missing clean status")

    queue = json.loads(read_text(QUEUE_JSON) or "{}")
    if queue.get("status") != "PASS":
        failures.append("queue json is not PASS")
    signals = queue.get("qualitySignals", {})
    for key in ("commentlessFunctionCount", "undefinedSignatureCount", "paramSignatureCount"):
        if signals.get(key) != 0:
            failures.append(f"queue signal not zero: {key}")

    docs = {
        "public_note": read_text(PUBLIC_NOTE),
        "campaign": read_text(CAMPAIGN),
        "actor_doc": read_text(ACTOR_DOC),
        "unit_doc": read_text(UNIT_DOC),
    }
    for path_name, text in docs.items():
        for required in ("Wave912", "CActor__StickToGround"):
            if required not in text:
                failures.append(f"{path_name} missing {required}")

    return {
        "schema": "ghidra-actor-airunit-vfunc-review-wave912.v1",
        "status": "PASS" if not failures else "FAIL",
        "target": "0x00402030 CActor__StickToGround",
        "reviewedTargets": 6,
        "mutatedTargets": 1,
        "failures": failures,
        "inputs": {
            "base": str(BASE.relative_to(ROOT)),
            "publicNote": str(PUBLIC_NOTE.relative_to(ROOT)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave912-actor-airunit-vfunc-review.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave912 actor/air-unit vfunc review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    if report["failures"]:
        for failure in report["failures"]:
            print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
