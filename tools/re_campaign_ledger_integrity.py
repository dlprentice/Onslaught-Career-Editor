#!/usr/bin/env python3
"""Fail closed if Gen10 campaign ledgers lack falsifiers or treat UNSCORED as success."""
from __future__ import annotations
import csv
import sys
from pathlib import Path

def read_tsv(path: Path):
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/"
        "generation-10-ttd-call-context-observation-v2"
    )
    if not root.is_dir():
        print(f"FAIL missing campaign root {root}", file=sys.stderr)
        return 2
    funcs = read_tsv(root / "campaign-functions.tsv")
    res = read_tsv(root / "campaign-residuals.tsv")
    cons = read_tsv(root / "campaign-contracts.tsv")
    qs = read_tsv(root / "campaign-questions.tsv")
    errors = []
    if len(funcs) != 8124 or len(res) != 6117 or len(cons) != 14241 or len(qs) != 15241:
        errors.append(
            f"unexpected counts f={len(funcs)} r={len(res)} c={len(cons)} q={len(qs)}"
        )
    for label, rows in ("functions", funcs), ("residuals", res), ("contracts", cons), ("questions", qs):
        empty = sum(1 for r in rows if not (r.get("cheapestFalsifier") or "").strip())
        if empty:
            errors.append(f"{label}: {empty} rows missing cheapestFalsifier")
    open_cons = {c["entityKey"] for c in cons if (c.get("contractState") or "").upper() == "OPEN"}
    open_q = {q["entityKey"] for q in qs if (q.get("state") or "").upper() == "OPEN"}
    missing = open_cons - open_q
    if missing:
        errors.append(f"{len(missing)} OPEN contracts lack OPEN questions")
    unscored_success = [
        c for c in cons
        if (c.get("semanticGrade") or "").upper() == "UNSCORED"
        and (c.get("contractState") or "").upper() in {"CLOSED", "TERMINAL", "REBUILD_READY"}
    ]
    if unscored_success:
        errors.append(f"{len(unscored_success)} contracts treat UNSCORED as success")
    c2 = [c for c in cons if c.get("semanticGrade") == "C2_BOUNDED_RUNTIME"]
    if len(c2) != 4:
        errors.append(f"expected 4 C2 contracts, got {len(c2)}")
    rebuild_ready = [c for c in cons if c.get("rebuildState") == "REBUILD_READY"]
    if rebuild_ready:
        errors.append(f"unexpected REBUILD_READY count {len(rebuild_ready)}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print(
        "PASS campaign ledger integrity: "
        f"functions={len(funcs)} residuals={len(res)} contracts={len(cons)} "
        f"questions={len(qs)} C2={len(c2)} empty_falsifiers=0 open_contracts_without_question=0"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
