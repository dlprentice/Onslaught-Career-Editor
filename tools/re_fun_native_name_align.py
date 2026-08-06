#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Plate: campaign-only FUN_* → nativeShippedName alignment.

Selects functions that still carry nameClass FUN (or FUN_* currentName) but
already have a non-empty nativeShippedName and live boundary promotion status
FUNCTION_PROMOTED_LIVE_BOUNDARY_ONLY (evidence that the address is a real
script/handler binding in the shipped registry + prior Ghidra boundary work).

Does **not** mutate Ghidra. Does **not** claim REBUILD_READY or full contracts.
Does **not** invent names beyond nativeShippedName.

Output plate for dual-role review before Gen34 apply.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "bea.re.fun-native-name-align.v1"
PACK_SCHEMA = "bea.re.fun-native-name-align-formal-pack.v1"
ADVANCE_KIND = "FUNCTION_NATIVE_NAME_ALIGN.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
ALLOWED_STATUS = {"FUNCTION_PROMOTED_LIVE_BOUNDARY_ONLY"}

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARENT = Path(
    "local-lab/residual-terminal-generation33-large-island-resolve-20260805-v1/"
    "generation-33-residual-terminal-large-island-resolve"
)
DEFAULT_OUT = Path("local-lab/fun-native-name-align-20260805-v1")

DEFAULT_FALSIFIER = (
    "Native shipped name does not bind this entryVa in registry/evidence; "
    "nameClass already NAMED; Ghidra live name contradicts without supersession; "
    "REBUILD_READY claim from name alone"
)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_tsv(path: Path) -> list[dict[str, str]]:
    rows = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        w = csv.DictWriter(
            handle,
            fieldnames=columns,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in columns})


def is_fun_identity(row: dict[str, str]) -> bool:
    name = str(row.get("currentName") or "")
    return row.get("nameClass") == "FUN" or name.startswith("FUN_")


def is_real_native_name(raw: str | None) -> bool:
    """Reject empty and ledger-stringified None from coverage join."""
    native = (raw or "").strip()
    if not native:
        return False
    if native.lower() in {"none", "null", "nil", "n/a", "-"}:
        return False
    return True


def select_proofs(functions: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    proofs: list[dict[str, Any]] = []
    still: list[dict[str, Any]] = []
    for row in functions:
        raw_native = row.get("nativeShippedName")
        native = (raw_native or "").strip()
        if not is_real_native_name(native):
            # Do not treat stringified "None" as a shipped name (ledger join artifact).
            continue
        status = (row.get("nativeRegistryStatus") or "").strip()
        if status.lower() in {"none", "null", ""}:
            status = ""
        if not is_fun_identity(row):
            still.append(
                {
                    "entryVa": row.get("entryVa"),
                    "currentName": row.get("currentName"),
                    "nativeShippedName": native,
                    "lane": "ALREADY_NAMED_OR_NON_FUN",
                    "nativeRegistryStatus": status,
                }
            )
            continue
        if status not in ALLOWED_STATUS:
            still.append(
                {
                    "entryVa": row.get("entryVa"),
                    "currentName": row.get("currentName"),
                    "nativeShippedName": native,
                    "lane": "STATUS_HELD",
                    "nativeRegistryStatus": status or "EMPTY",
                    "cheapestFalsifier": (
                        "Need FUNCTION_PROMOTED_LIVE_BOUNDARY_ONLY (or stronger "
                        "semantic live status) before campaign name align"
                    ),
                }
            )
            continue
        if native == (row.get("currentName") or "").strip():
            still.append(
                {
                    "entryVa": row.get("entryVa"),
                    "currentName": row.get("currentName"),
                    "nativeShippedName": native,
                    "lane": "ALREADY_ALIGNED",
                    "nativeRegistryStatus": status,
                }
            )
            continue
        proofs.append(
            {
                "entityKey": row.get("entityKey"),
                "entryVa": row.get("entryVa"),
                "oldName": row.get("currentName"),
                "newName": native,
                "nativeShippedName": native,
                "nativeRegistryStatus": status,
                "executionState": row.get("executionState"),
                "understoodTier": row.get("understoodTier"),
                "bodyBytes": row.get("bodyBytes"),
                "semanticGrade": row.get("semanticGrade"),
                "campaignState": row.get("campaignState"),
                "recoveryLane": "NATIVE_REGISTRY_BOUNDARY",
                "proposed": {
                    "currentName": native,
                    "nameClass": "NAMED",
                    "nativeRegistryStatus": status,
                    "evidenceAppend": "CAMPAIGN_NATIVE_NAME_ALIGNED",
                    "requiresQuestionSupersession": False,
                    "rebuildState": "NOT_READY",
                    "cheapestFalsifier": DEFAULT_FALSIFIER,
                    "nonClaims": [
                        "Not REBUILD_READY",
                        "Not full contract recovery",
                        "Not Ghidra live mutation",
                        "Name equals nativeShippedName only",
                    ],
                },
            }
        )
    return proofs, still


def build(*, campaign: Path, out_dir: Path) -> dict[str, Any]:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 33:
        raise SystemExit(f"expected Gen33 tip parent, got {ready.get('generation')}")
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    if len(functions) != 8124:
        raise SystemExit(f"functions {len(functions)}")
    proofs, still = select_proofs(functions)
    hard: list[str] = []
    seen_va: set[str] = set()
    seen_name: set[str] = set()
    for p in proofs:
        va = (p.get("entryVa") or "").lower()
        if not va:
            hard.append("missing entryVa")
        if va in seen_va:
            hard.append(f"dup va {va}")
        seen_va.add(va)
        nn = p.get("newName") or ""
        # allow duplicate native names only if different VAs (overloads) — flag only
        key = f"{nn}|{va}"
        if key in seen_name:
            hard.append(f"dup proof {key}")
        seen_name.add(key)
        if not p.get("entityKey"):
            hard.append(f"no entity {va}")
        if p["oldName"] == p["newName"]:
            hard.append(f"no-op {va}")

    status = (
        "READY_FOR_GENERATION"
        if proofs and not hard
        else "EMPTY"
        if not proofs and not hard
        else "BLOCKED"
    )
    pack = {
        "schema": PACK_SCHEMA,
        "status": status,
        "advance_kind_proposed": ADVANCE_KIND,
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 33,
        "n_functions_input": len(functions),
        "n_proofs": len(proofs),
        "n_still_held": len(still),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "recoveryLaneCounts": dict(Counter(p["recoveryLane"] for p in proofs)),
        "executionCounts": dict(Counter(p.get("executionState") or "?" for p in proofs)),
        "hold_generation_apply": True,
        "claims": [
            f"Selected {len(proofs)} FUN_* rows with real nativeShippedName and "
            "FUNCTION_PROMOTED_LIVE_BOUNDARY_ONLY for campaign name align.",
            "Aligns currentName/nameClass only; no Ghidra write; no REBUILD_READY.",
            (
                f"STATUS_HELD (real native, weak/other status): "
                f"{sum(1 for s in still if s.get('lane')=='STATUS_HELD')}."
            ),
            "Rejects empty/stringified None nativeShippedName (ledger join artifact).",
        ],
        "non_claims": [
            "Does not invent names beyond nativeShippedName",
            "Does not mutate Ghidra or pristine specimen",
            "Does not close OPEN contracts or claim full logic recovery",
            "Does not re-close residual police OFFSET_ENVELOPE holds",
            "Does not treat TSV literal 'None' as a shipped name",
        ],
        "proofs": proofs,
        "stillHeld": still,
    }
    summary = {
        "schema": SCHEMA,
        "status": "MEASURED",
        "plate": str(out_dir).replace("\\", "/"),
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 33,
        "formalPackStatus": status,
        "counts": {
            "n_proofs": len(proofs),
            "n_still_held": len(still),
            "executionCounts": pack["executionCounts"],
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "proofEntryVas": [p["entryVa"] for p in proofs],
        "parentFunctionsSha256": _sha(campaign / "campaign-functions.tsv"),
        "cheapestNext": [
            "Dual-role review then Gen34 apply (campaign-only)",
            "WEAK native rows need stronger registry/TTD before align",
            "COVERED FUN without native still need identity instruments",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "FORMAL-PACK.json").write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    cols = [
        "entryVa",
        "entityKey",
        "oldName",
        "newName",
        "nativeRegistryStatus",
        "executionState",
        "bodyBytes",
        "recoveryLane",
    ]
    _write_tsv(out_dir / "proofs.tsv", cols, proofs)
    _write_tsv(
        out_dir / "still-held.tsv",
        [
            "entryVa",
            "currentName",
            "nativeShippedName",
            "lane",
            "nativeRegistryStatus",
            "cheapestFalsifier",
        ],
        still,
    )
    (out_dir / "README.md").write_text(
        "# FUN native name align plate\n\n"
        f"Status: **{status}** · proofs: **{len(proofs)}**\n\n"
        "Campaign-only nameClass/currentName align from nativeShippedName.\n"
        "Gen34 apply held for dual-role review.\n",
        encoding="utf-8",
    )
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(
            {
                "formalPackSha256": _sha(out_dir / "FORMAL-PACK.json"),
                "parentFunctionsSha256": summary["parentFunctionsSha256"],
                "n_proofs": len(proofs),
                "status": status,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("FUN_NATIVE_NAME_ALIGN_MEASURED")
    print(f"formal_pack_status={status}")
    print(f"n_proofs={len(proofs)}")
    return summary


def verify(*, plate: Path) -> dict[str, Any]:
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    if pack.get("n_hard_mismatches", 1) != 0:
        raise SystemExit(f"hard: {pack.get('hardMismatches')}")
    if pack.get("status") not in {"READY_FOR_GENERATION", "EMPTY"}:
        raise SystemExit(f"status {pack.get('status')}")
    out = {
        "status": "VERIFIED",
        "formalPackStatus": pack.get("status"),
        "n_proofs": pack.get("n_proofs"),
        "lanes": pack.get("recoveryLaneCounts"),
    }
    print(json.dumps(out, indent=2))
    print("FUN_NATIVE_NAME_ALIGN_VERIFIED")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_PARENT)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    args = p.parse_args(argv)
    if args.cmd == "build":
        build(campaign=args.campaign, out_dir=args.out)
        return 0
    verify(plate=args.plate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
