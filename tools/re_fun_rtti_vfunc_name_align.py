#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Plate: COVERED FUN_* named from strict RTTI vtable slots.

Parent: Gen35. Joins campaign FUN (COVERED, no real nativeShippedName) to
local-lab RTTI strict vtables.tsv (class, slot, function_va).

Naming policy (conservative):
  - Single class ownership for dominant slot -> Class__VFunc_{slot}, nameClass NAMED
  - Multi-class ownership -> VFuncSlot_{slot:02d}_{entryVa8}, nameClass VFUNC_SLOT
    (matches existing campaign VFuncSlot_* pattern; avoids wrong most-derived guess)
  - Skip if >8 owning classes (shared stub soup) or bodyBytes < 4

Does not invent free-form names. No Ghidra. No REBUILD_READY.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "bea.re.fun-rtti-vfunc-name-align.v1"
PACK_SCHEMA = "bea.re.fun-rtti-vfunc-name-align-formal-pack.v1"
ADVANCE_KIND = "FUNCTION_RTTI_VFUNC_NAME_ALIGN.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARENT = Path(
    "local-lab/function-weak-native-name-align-generation35-20260805-v1/"
    "generation-35-function-weak-native-name-align"
)
DEFAULT_VTABLES = Path(
    "local-lab/rtti-strict-census-2026-08-03/strict-census-v1-ready/vtables.tsv"
)
DEFAULT_OUT = Path("local-lab/fun-rtti-vfunc-name-align-20260805-v1")

DEFAULT_FALSIFIER = (
    "RTTI strict vtable slot no longer maps function_va; multi-class shared stub "
    "misnamed as exclusive; REBUILD_READY claim; Ghidra mutation"
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
    return native.lower() not in {"none", "null", "nil", "n/a", "-"}


def is_fun_identity(row: dict[str, str]) -> bool:
    name = str(row.get("currentName") or "")
    return row.get("nameClass") == "FUN" or name.startswith("FUN_")


def va8(entry_va: str) -> str:
    return entry_va.lower().replace("0x", "").zfill(8)


def propose_name(owners: list[tuple[str, int]], entry_va: str) -> tuple[str, str, str]:
    """Return (newName, nameClass, lane)."""
    slot_counts: Counter[int] = Counter(s for _, s in owners)
    dominant_slot = sorted(slot_counts.items(), key=lambda x: (-x[1], x[0]))[0][0]
    classes = sorted({c for c, s in owners if s == dominant_slot})
    if not classes:
        classes = sorted({c for c, _ in owners})
    if len(classes) == 1:
        return (
            f"{classes[0]}__VFunc_{dominant_slot}",
            "NAMED",
            "RTTI_VFUNC_EXCLUSIVE",
        )
    if len(classes) > 8:
        return ("", "", "SKIP_SHARED_SOUP")
    # multi-class: address-suffixed VFuncSlot pattern already used in campaign
    return (
        f"VFuncSlot_{dominant_slot:02d}_{va8(entry_va)}",
        "VFUNC_SLOT",
        "RTTI_VFUNC_SHARED_SLOT",
    )


def select_proofs(
    functions: list[dict[str, str]], vtables: list[dict[str, str]]
) -> tuple[list[dict], list[dict]]:
    by_va = {f["entryVa"].lower(): f for f in functions}
    owners: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for r in vtables:
        fva = (r.get("function_va") or "").lower()
        cls = (r.get("class") or "").strip()
        if not fva or not cls:
            continue
        try:
            slot = int(r.get("slot") or -1)
        except ValueError:
            continue
        if slot < 0:
            continue
        f = by_va.get(fva)
        if not f:
            continue
        if not is_fun_identity(f):
            continue
        if f.get("executionState") != "COVERED":
            continue
        if is_real_native_name(f.get("nativeShippedName")):
            continue
        try:
            body = int(f.get("bodyBytes") or 0)
        except ValueError:
            body = 0
        if body < 4:
            continue
        owners[fva].append((cls, slot))

    proofs: list[dict[str, Any]] = []
    still: list[dict[str, Any]] = []
    for fva, own in sorted(owners.items()):
        f = by_va[fva]
        new_name, name_class, lane = propose_name(own, f["entryVa"])
        if lane == "SKIP_SHARED_SOUP" or not new_name:
            still.append(
                {
                    "entryVa": f.get("entryVa"),
                    "currentName": f.get("currentName"),
                    "lane": "SKIP_SHARED_SOUP",
                    "n_classes": str(len({c for c, _ in own})),
                }
            )
            continue
        if new_name == (f.get("currentName") or ""):
            still.append(
                {
                    "entryVa": f.get("entryVa"),
                    "lane": "ALREADY_ALIGNED",
                    "currentName": f.get("currentName"),
                }
            )
            continue
        classes = sorted({c for c, _ in own})
        slots = sorted({s for _, s in own})
        proofs.append(
            {
                "entityKey": f.get("entityKey"),
                "entryVa": f.get("entryVa"),
                "oldName": f.get("currentName"),
                "newName": new_name,
                "nameClass": name_class,
                "recoveryLane": lane,
                "executionState": f.get("executionState"),
                "bodyBytes": f.get("bodyBytes"),
                "rttiClasses": ";".join(classes),
                "rttiSlots": ";".join(str(s) for s in slots),
                "n_owner_rows": len(own),
                "proposed": {
                    "currentName": new_name,
                    "nameClass": name_class,
                    "evidenceAppend": "CAMPAIGN_RTTI_VFUNC_NAME_ALIGNED",
                    "rebuildState": "NOT_READY",
                    "cheapestFalsifier": DEFAULT_FALSIFIER,
                    "nonClaims": [
                        "Not REBUILD_READY",
                        "Not full contract recovery",
                        "Not Ghidra live mutation",
                        "Multi-class uses VFuncSlot_XX_addr form only",
                    ],
                },
            }
        )
    return proofs, still


def build(*, campaign: Path, vtables_path: Path, out_dir: Path) -> dict[str, Any]:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 35:
        raise SystemExit(f"expected Gen35 parent, got {ready.get('generation')}")
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    if len(functions) != 8124:
        raise SystemExit(f"functions {len(functions)}")
    vtables = _read_tsv(vtables_path)
    proofs, still = select_proofs(functions, vtables)
    hard: list[str] = []
    seen: set[str] = set()
    seen_names: set[str] = set()
    for p in proofs:
        va = (p.get("entryVa") or "").lower()
        if va in seen:
            hard.append(f"dup va {va}")
        seen.add(va)
        nn = p.get("newName") or ""
        if nn in seen_names:
            hard.append(f"dup name {nn}")
        seen_names.add(nn)
        if not p.get("entityKey"):
            hard.append(f"no ek {va}")
        if p["oldName"] == p["newName"]:
            hard.append(f"noop {va}")

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
        "rttiVtables": {
            "path": str(vtables_path).replace("\\", "/"),
            "sha256": _sha(vtables_path),
            "n_rows": len(vtables),
        },
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 35,
        "n_functions_input": len(functions),
        "n_proofs": len(proofs),
        "n_still_held": len(still),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "recoveryLaneCounts": dict(Counter(p["recoveryLane"] for p in proofs)),
        "hold_generation_apply": True,
        "claims": [
            f"Selected {len(proofs)} COVERED FUN_* with strict RTTI vtable ownership.",
            "Exclusive class -> Class__VFunc_N; multi-class -> VFuncSlot_XX_addr.",
            "No Ghidra; no REBUILD_READY; no residual police touch.",
        ],
        "non_claims": [
            "Does not invent free-form names",
            "Does not claim method semantics beyond vtable slot identity",
            "Does not mutate Ghidra or pristine specimen",
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
        "campaignGeneration": 35,
        "formalPackStatus": status,
        "counts": {
            "n_proofs": len(proofs),
            "n_still_held": len(still),
            "lanes": pack["recoveryLaneCounts"],
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "proofEntryVas": [p["entryVa"] for p in proofs],
        "parentFunctionsSha256": _sha(campaign / "campaign-functions.tsv"),
        "cheapestNext": [
            "Dual-role review then Gen36 apply",
            "Police OPEN_DARK instrument; remaining COVERED FUN without RTTI",
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
            "nameClass",
            "recoveryLane",
            "bodyBytes",
            "rttiClasses",
            "rttiSlots",
        ],
        proofs,
    )
    _write_tsv(
        out_dir / "still-held.tsv",
        ["entryVa", "currentName", "lane", "n_classes"],
        still,
    )
    (out_dir / "README.md").write_text(
        f"# RTTI vfunc name align\n\nStatus **{status}** proofs **{len(proofs)}**\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("FUN_RTTI_VFUNC_NAME_ALIGN_MEASURED")
    print(f"formal_pack_status={status} n_proofs={len(proofs)}")
    return summary


def verify(*, plate: Path) -> dict[str, Any]:
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    if pack.get("n_hard_mismatches", 1) != 0:
        raise SystemExit(f"hard {pack.get('hardMismatches')}")
    if pack.get("status") not in {"READY_FOR_GENERATION", "EMPTY"}:
        raise SystemExit(f"status {pack.get('status')}")
    out = {
        "status": "VERIFIED",
        "formalPackStatus": pack.get("status"),
        "n_proofs": pack.get("n_proofs"),
        "lanes": pack.get("recoveryLaneCounts"),
    }
    print(json.dumps(out, indent=2))
    print("FUN_RTTI_VFUNC_NAME_ALIGN_VERIFIED")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_PARENT)
    b.add_argument("--vtables", type=Path, default=DEFAULT_VTABLES)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    args = p.parse_args(argv)
    if args.cmd == "build":
        build(campaign=args.campaign, vtables_path=args.vtables, out_dir=args.out)
        return 0
    verify(plate=args.plate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
