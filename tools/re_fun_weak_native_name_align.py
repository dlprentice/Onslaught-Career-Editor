#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Plate: campaign FUN_* WEAK native names corroborated by script-native-table-144.

Parent tip: Gen34. Selects remaining FUN rows with nativeRegistryStatus=WEAK
and real nativeShippedName only when MissionScript descriptor table
(local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv) binds
handler VA + shippedName at the documented table base/stride.

Does not invent names. Does not mutate Ghidra. Does not claim REBUILD_READY.
Rejects stringified None natives (same gate as Gen34).
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

SCHEMA = "bea.re.fun-weak-native-name-align.v1"
PACK_SCHEMA = "bea.re.fun-weak-native-name-align-formal-pack.v1"
ADVANCE_KIND = "FUNCTION_WEAK_NATIVE_NAME_ALIGN.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
TABLE_PATH = Path(
    "local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv"
)
EXPECTED_TABLE_ROWS = 144
TABLE_BASE = 0x0064CE20
TABLE_STRIDE = 0x40

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARENT = Path(
    "local-lab/function-native-name-align-generation34-20260805-v1/"
    "generation-34-function-native-name-align"
)
DEFAULT_OUT = Path("local-lab/fun-weak-native-name-align-20260805-v1")

DEFAULT_FALSIFIER = (
    "script-native-table-144 handler/shippedName mismatch; status not WEAK; "
    "native stringified None; REBUILD_READY claim; Ghidra live mutation"
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


def is_real_native_name(raw: str | None) -> bool:
    native = (raw or "").strip()
    if not native:
        return False
    if native.lower() in {"none", "null", "nil", "n/a", "-"}:
        return False
    return True


def is_fun_identity(row: dict[str, str]) -> bool:
    name = str(row.get("currentName") or "")
    return row.get("nameClass") == "FUN" or name.startswith("FUN_")


def load_script_table(path: Path) -> dict[str, dict[str, str]]:
    """Map handler VA lower -> table row; verify structural record VAs."""
    rows = _read_tsv(path)
    if len(rows) != EXPECTED_TABLE_ROWS:
        raise SystemExit(f"table rows {len(rows)} != {EXPECTED_TABLE_ROWS}")
    by_handler: dict[str, dict[str, str]] = {}
    for row in rows:
        idx = int(row["index"])
        record = int(row["record"], 16)
        expected = TABLE_BASE + idx * TABLE_STRIDE
        if record != expected:
            raise SystemExit(f"record VA mismatch index {idx}: {row['record']}")
        handler = (row.get("handler") or "").lower()
        if not handler.startswith("0x"):
            raise SystemExit(f"bad handler {row}")
        if handler in by_handler:
            raise SystemExit(f"dup handler {handler}")
        by_handler[handler] = row
    return by_handler


def select_proofs(
    functions: list[dict[str, str]], table: dict[str, dict[str, str]]
) -> tuple[list[dict], list[dict]]:
    proofs: list[dict[str, Any]] = []
    still: list[dict[str, Any]] = []
    for row in functions:
        if not is_fun_identity(row):
            continue
        native = (row.get("nativeShippedName") or "").strip()
        if not is_real_native_name(native):
            continue
        status = (row.get("nativeRegistryStatus") or "").strip()
        if status != "WEAK":
            continue
        va = (row.get("entryVa") or "").lower()
        trow = table.get(va)
        if trow is None:
            still.append(
                {
                    "entryVa": row.get("entryVa"),
                    "currentName": row.get("currentName"),
                    "nativeShippedName": native,
                    "lane": "NOT_IN_SCRIPT_TABLE",
                    "cheapestFalsifier": "handler VA absent from script-native-table-144",
                }
            )
            continue
        shipped = (trow.get("shippedName") or "").strip()
        if shipped != native:
            still.append(
                {
                    "entryVa": row.get("entryVa"),
                    "currentName": row.get("currentName"),
                    "nativeShippedName": native,
                    "lane": "TABLE_NAME_MISMATCH",
                    "tableShippedName": shipped,
                    "cheapestFalsifier": "table shippedName != campaign nativeShippedName",
                }
            )
            continue
        # Table status column is a 2026-07-28 Ghidra snapshot grade; WEAK means
        # handler still FUN_* in that snapshot — required corroboration for this plate.
        if (trow.get("status") or "").strip() != "WEAK":
            still.append(
                {
                    "entryVa": row.get("entryVa"),
                    "lane": "TABLE_STATUS_NOT_WEAK",
                    "tableStatus": trow.get("status"),
                    "nativeShippedName": native,
                }
            )
            continue
        if native == (row.get("currentName") or "").strip():
            still.append(
                {
                    "entryVa": row.get("entryVa"),
                    "lane": "ALREADY_ALIGNED",
                    "nativeShippedName": native,
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
                "semanticGrade": row.get("semanticGrade"),
                "bodyBytes": row.get("bodyBytes"),
                "tableIndex": trow.get("index"),
                "tableRecord": trow.get("record"),
                "tableStatus": trow.get("status"),
                "recoveryLane": "WEAK_SCRIPT_TABLE_BIND",
                "proposed": {
                    "currentName": native,
                    "nameClass": "NAMED",
                    "evidenceAppend": "CAMPAIGN_WEAK_NATIVE_NAME_ALIGNED_SCRIPT_TABLE_144",
                    "rebuildState": "NOT_READY",
                    "cheapestFalsifier": DEFAULT_FALSIFIER,
                    "nonClaims": [
                        "Not REBUILD_READY",
                        "Not Ghidra live mutation",
                        "WEAK registry status retained",
                        "Name equals nativeShippedName corroborated by table only",
                    ],
                },
            }
        )
    return proofs, still


def build(*, campaign: Path, table_path: Path, out_dir: Path) -> dict[str, Any]:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 34:
        raise SystemExit(f"expected Gen34 parent, got {ready.get('generation')}")
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    if len(functions) != 8124:
        raise SystemExit(f"functions {len(functions)}")
    table = load_script_table(table_path)
    proofs, still = select_proofs(functions, table)
    hard: list[str] = []
    seen: set[str] = set()
    for p in proofs:
        va = (p.get("entryVa") or "").lower()
        if va in seen:
            hard.append(f"dup {va}")
        seen.add(va)
        if not p.get("entityKey"):
            hard.append(f"no ek {va}")
        if p["oldName"] == p["newName"]:
            hard.append(f"noop {va}")
        if not is_real_native_name(p.get("newName")):
            hard.append(f"bad newName {va}")

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
        "scriptNativeTable": {
            "path": str(table_path).replace("\\", "/"),
            "sha256": _sha(table_path),
            "n_rows": EXPECTED_TABLE_ROWS,
            "base": hex(TABLE_BASE),
            "stride": hex(TABLE_STRIDE),
        },
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 34,
        "n_functions_input": len(functions),
        "n_proofs": len(proofs),
        "n_still_held": len(still),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "recoveryLaneCounts": dict(Counter(p["recoveryLane"] for p in proofs)),
        "executionCounts": dict(Counter(p.get("executionState") or "?" for p in proofs)),
        "hold_generation_apply": True,
        "claims": [
            f"Selected {len(proofs)} WEAK FUN_* with real native + script-table-144 bind.",
            "Campaign name align only; WEAK status retained; no Ghidra; no REBUILD_READY.",
            "Rejects stringified None natives.",
        ],
        "non_claims": [
            "Does not invent names beyond table/campaign native",
            "Does not mutate Ghidra or pristine specimen",
            "Does not close contracts or claim full logic recovery",
            "Does not re-close residual police OFFSET_ENVELOPE",
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
        "campaignGeneration": 34,
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
            "Dual-role review then Gen35 apply",
            "COVERED FUN without native need identity instruments",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "FORMAL-PACK.json").write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    _write_tsv(
        out_dir / "proofs.tsv",
        [
            "entryVa",
            "entityKey",
            "oldName",
            "newName",
            "executionState",
            "semanticGrade",
            "tableIndex",
            "recoveryLane",
        ],
        proofs,
    )
    _write_tsv(
        out_dir / "still-held.tsv",
        ["entryVa", "currentName", "nativeShippedName", "lane", "cheapestFalsifier"],
        still,
    )
    (out_dir / "README.md").write_text(
        "# WEAK FUN native name align (script-table-144)\n\n"
        f"Status: **{status}** · proofs: **{len(proofs)}**\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("FUN_WEAK_NATIVE_NAME_ALIGN_MEASURED")
    print(f"formal_pack_status={status} n_proofs={len(proofs)}")
    return summary


def verify(*, plate: Path) -> dict[str, Any]:
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    if pack.get("n_hard_mismatches", 1) != 0:
        raise SystemExit(f"hard {pack.get('hardMismatches')}")
    if pack.get("status") not in {"READY_FOR_GENERATION", "EMPTY"}:
        raise SystemExit(f"status {pack.get('status')}")
    for p in pack.get("proofs") or []:
        if not is_real_native_name(p.get("newName")):
            raise SystemExit(f"bad name {p.get('entryVa')}")
    out = {
        "status": "VERIFIED",
        "formalPackStatus": pack.get("status"),
        "n_proofs": pack.get("n_proofs"),
    }
    print(json.dumps(out, indent=2))
    print("FUN_WEAK_NATIVE_NAME_ALIGN_VERIFIED")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_PARENT)
    b.add_argument("--table", type=Path, default=TABLE_PATH)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    args = p.parse_args(argv)
    if args.cmd == "build":
        build(campaign=args.campaign, table_path=args.table, out_dir=args.out)
        return 0
    verify(plate=args.plate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
