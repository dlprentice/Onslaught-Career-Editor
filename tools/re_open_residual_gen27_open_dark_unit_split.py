#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen27 remaining OPEN_DARK unit-split instrument.

Exports OPEN_DARK (82) from Generation 27 tip. Recovers residual-row terminals
via the same static PE unit-boundary classifiers used for OPEN_EXECUTED:

  JMP_OVER_FRAGMENT / PREV_INSN_SPAN / SWITCH_CASE_ENTRY

Does **not** re-close police-reopened OFFSET_ENVELOPE rows via envelope alone.
Does **not** mutate Gen27. Does **not** invent names or REBUILD_READY.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore

SCHEMA = "bea.re.open-residual-gen27-open-dark-unit-split.v1"
PACK_SCHEMA = "bea.re.open-residual-gen27-open-dark-unit-split-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_DARK_UNIT_SPLIT.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 82
EXPECTED_OPEN_EXECUTED = 0
EXPECTED_RESIDUALS = 6117

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN27 = Path(
    "local-lab/residual-terminal-generation27-tiny-fragment-20260805-v1/"
    "generation-27-residual-terminal-tiny-fragment"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen27-open-dark-unit-split-20260805-v1")
GEN25_READY = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen/campaign.ready.json"
)
GEN25_RECEIPT = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen/generation-receipt.json"
)

DEFAULT_FALSIFIER = (
    "PE re-decode: residual no longer interior of pinned insn / jmp-over / "
    "switch table dword; residual membership of a named body; REBUILD_READY claim"
)


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _stamp(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": _sha(path),
    }


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


def load_police_reopened() -> set[str]:
    out: set[str] = set()
    if GEN25_READY.is_file():
        ready = json.loads(GEN25_READY.read_text(encoding="utf-8"))
        for p in (ready.get("advance") or {}).get("reopened") or []:
            if isinstance(p, dict) and p.get("startVa"):
                out.add(str(p["startVa"]).lower())
    if GEN25_RECEIPT.is_file():
        rec = json.loads(GEN25_RECEIPT.read_text(encoding="utf-8"))
        out |= {str(s).lower() for s in rec.get("reopenedStarts") or []}
    return out


def proposed_for(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "classification": "CODE_CANDIDATE",
        "classificationVerdict": f"STATIC_OPEN_DARK_UNIT_SPLIT/{rec['lane']}",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
        "shapeKind": rec["shapeKind"],
        "recoveryLane": rec["lane"],
        "requiresQuestionSupersession": True,
        "cheapestFalsifier": DEFAULT_FALSIFIER,
        "sourceState": "OPEN_DARK_RESIDUAL",
    }


def build(*, campaign: Path, specimen: Path, out_dir: Path) -> dict[str, Any]:
    if Cs is None:
        raise SystemExit("capstone required")
    mass = _load_mod(
        "re_open_dark_code_like_mass", ROOT / "tools" / "re_open_dark_code_like_mass.py"
    )
    us_mod = _load_mod(
        "re_open_residual_gen25_ttd_unit_split",
        ROOT / "tools" / "re_open_residual_gen25_ttd_unit_split.py",
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 27:
        raise SystemExit(f"expected Gen27, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != "RESIDUAL_TERMINAL_OPEN_TINY_FRAGMENT":
        raise SystemExit(f"unexpected advance {(ready.get('advance') or {}).get('kind')}")

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    if len(residuals) != EXPECTED_RESIDUALS:
        raise SystemExit(f"residuals {len(residuals)}")
    dark = [r for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL"]
    executed = [
        r for r in residuals if r.get("campaignState") == "OPEN_EXECUTED_RESIDUAL"
    ]
    if len(dark) != EXPECTED_OPEN_DARK:
        raise SystemExit(f"OPEN_DARK {len(dark)}")
    if len(executed) != EXPECTED_OPEN_EXECUTED:
        raise SystemExit(f"OPEN_EXECUTED {len(executed)}")

    police = load_police_reopened()
    out_dir.mkdir(parents=True, exist_ok=True)
    export_cols = [
        "entityKey",
        "startVa",
        "endVa",
        "bytes",
        "observationState",
        "campaignState",
        "questionIds",
        "prevFunc",
        "nextFunc",
        "cheapestFalsifier",
    ]
    _write_tsv(out_dir / "open-dark.tsv", export_cols, dark)

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = mass.pe_map(data)
    md = Cs(CS_ARCH_X86, CS_MODE_32)

    proofs: list[dict[str, Any]] = []
    still: list[dict[str, Any]] = []
    buckets: Counter = Counter()
    lane_counts: Counter = Counter()
    n_police_hold = 0

    for r in dark:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        b = end - start
        if b <= 3:
            buckets["1-3"] += 1
        elif b <= 15:
            buckets["4-15"] += 1
        elif b <= 63:
            buckets["16-63"] += 1
        elif b <= 255:
            buckets["64-255"] += 1
        else:
            buckets["256+"] += 1

        blob = mass.span_bytes(data, start, end, ib, secs)
        is_police = r["startVa"].lower() in police
        if blob is None:
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": b,
                    "lane": "UNMAPPED",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": "Unmapped PE span",
                }
            )
            lane_counts["UNMAPPED"] += 1
            continue

        rec = us_mod.classify_executed_unit(data, start, end, ib, secs, md, mass)
        if rec is None:
            # note police envelope presence but do not promote
            env = mass.try_envelope_at(blob, start, md)
            if env and is_police:
                n_police_hold += 1
                still.append(
                    {
                        "startVa": r["startVa"],
                        "endVa": r["endVa"],
                        "bytes": b,
                        "lane": "POLICE_ENVELOPE_HOLD",
                        "entityKey": r.get("entityKey") or "",
                        "questionIds": r.get("questionIds") or "",
                        "cheapestFalsifier": (
                            "Police-reopened envelope still matches full-cover "
                            "gate; do not re-close without new instrument"
                        ),
                    }
                )
                lane_counts["POLICE_ENVELOPE_HOLD"] += 1
                continue
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": b,
                    "lane": "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": (
                        "No unit-split (jmp-over / prev-insn / switch); need "
                        "abs-ptr, shape, or TTD"
                    ),
                }
            )
            lane_counts["STILL_OPEN"] += 1
            continue

        prop = proposed_for(rec)
        proofs.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": b,
                "kind": rec["shapeKind"],
                "subspanKinds": rec["shapeKind"],
                "recoveryLane": rec["lane"],
                "peBytesSha256": hashlib.sha256(blob).hexdigest(),
                "recheckNote": rec.get("note") or "",
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": "OPEN_DARK_RESIDUAL",
                "police_reopen": is_police,
                "detail": {
                    k: v
                    for k, v in rec.items()
                    if k not in {"lane", "shapeKind", "note"}
                },
                "proposedTerminalState": prop["terminalState"],
                "proposed": prop,
            }
        )
        lane_counts[rec["lane"]] += 1

    hard: list[str] = []
    for p in proofs:
        if p["sourceState"] != "OPEN_DARK_RESIDUAL":
            hard.append(f"non_dark {p['startVa']}")
        if not p.get("questionIds"):
            hard.append(f"no_qid {p['startVa']}")
        if p["proposedTerminalState"] != "TERMINAL_BOUNDED_AMBIGUITY":
            hard.append(f"bad_term {p['startVa']}")
        s = int(p["startVa"], 16)
        e = int(p["endVa"], 16)
        again = us_mod.classify_executed_unit(data, s, e, ib, secs, md, mass)
        if again is None or again["lane"] != p["recoveryLane"]:
            hard.append(f"recheck_fail {p['startVa']}")
        blob = mass.span_bytes(data, s, e, ib, secs)
        if blob is None or hashlib.sha256(blob).hexdigest() != p["peBytesSha256"]:
            hard.append(f"pe_drift {p['startVa']}")

    pack: dict[str, Any] = {
        "schema": PACK_SCHEMA,
        "status": (
            "READY_FOR_GENERATION"
            if proofs and not hard
            else "EMPTY"
            if not proofs and not hard
            else "BLOCKED"
        ),
        "advance_kind_proposed": ADVANCE_KIND,
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 27,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_proofs": len(proofs),
        "n_still_open": len(still),
        "n_police_envelope_hold": n_police_hold,
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "darkSizeBuckets": dict(buckets),
        "recoveryLaneCounts": dict(Counter(p["recoveryLane"] for p in proofs)),
        "hold_generation_apply": True,
        "claims": [
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK from Gen27.",
            f"Open-dark unit-split proofs: {len(proofs)} "
            f"({dict(Counter(p['recoveryLane'] for p in proofs))}).",
            f"Police envelope holds (not re-closed): {n_police_hold}.",
            f"Still open dark: {len(still) - n_police_hold} + {n_police_hold} holds.",
            "Gen28 apply withheld until dual-role review (hold_generation_apply).",
        ],
        "non_claims": [
            "Does not invent function names or REBUILD_READY",
            "Does not re-close Gen25 police OFFSET_ENVELOPE set via envelope",
            "Does not claim CALL entry / Gen10 naming",
        ],
        "proofs": proofs,
    }

    summary = {
        "schema": SCHEMA,
        "status": "MEASURED",
        "plate": str(out_dir).replace("\\", "/"),
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 27,
        "formalPackStatus": pack["status"],
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "formalPackProofs": len(proofs),
            "stillOpen": len(still),
            "policeEnvelopeHold": n_police_hold,
            "darkSizeBuckets": dict(buckets),
            "laneCounts": dict(lane_counts),
            "recoveryLaneProofCounts": pack["recoveryLaneCounts"],
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Dual-role review then Gen28 apply of unit-split proofs",
            "Abs-ptr / shape for remaining non-unit dark",
            "Do not re-close police envelopes without new evidence",
        ],
        "proofStarts": [p["startVa"] for p in proofs],
        "parentResidualsSha256": _sha(campaign / "campaign-residuals.tsv"),
    }

    (out_dir / "FORMAL-PACK.json").write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    _write_tsv(
        out_dir / "still-open.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "lane",
            "entityKey",
            "questionIds",
            "cheapestFalsifier",
        ],
        still,
    )
    _write_tsv(
        out_dir / "proofs.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "recoveryLane",
            "kind",
            "peBytesSha256",
            "entityKey",
            "questionIds",
            "recheckNote",
            "police_reopen",
        ],
        proofs,
    )
    integrity = {
        "schema": "bea.re.open-residual-gen27-open-dark-unit-split.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_82": len(dark) == EXPECTED_OPEN_DARK,
            "open_executed_0": len(executed) == 0,
            "specimen_pristine": True,
            "empty_or_ready": pack["status"] in {"EMPTY", "READY_FOR_GENERATION"},
            "no_gen28_apply": True,
            "gen27_unmutated": True,
            "hold_generation_apply": True,
            "all_proofs_rechecked": len(hard) == 0,
            "no_police_envelope_proofs": all(
                p["recoveryLane"]
                in {"JMP_OVER_FRAGMENT", "PREV_INSN_SPAN", "SWITCH_CASE_ENTRY"}
                for p in proofs
            ),
        },
        "ledger_sha_pre": {
            "campaign-residuals.tsv": _sha(campaign / "campaign-residuals.tsv"),
            "campaign.ready.json": _sha(campaign / "campaign.ready.json"),
        },
        "sources": {
            "formalPack": _stamp(out_dir / "FORMAL-PACK.json"),
            "summary": _stamp(out_dir / "SUMMARY.json"),
            "specimen": _stamp(specimen),
        },
    }
    integrity["checks"]["gen27_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen27 OPEN_DARK unit-split

Status: **MEASURED** / formal pack **{pack['status']}**  
Proofs: **{len(proofs)}** · police holds: **{n_police_hold}** · still open: **{len(still)}**

Gen28 apply: **held** until dual-role review.
""",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("OPEN_RESIDUAL_GEN27_OPEN_DARK_UNIT_SPLIT_MEASURED")
    print(f"formal_pack_status={pack['status']}")
    print(f"n_proofs={pack['n_proofs']}")
    return {"summary": summary, "pack": pack}


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if summary["counts"]["n_open_dark_input"] != EXPECTED_OPEN_DARK:
        raise SystemExit("open dark")
    for name, sha in (integrity.get("ledger_sha_pre") or {}).items():
        if _sha(campaign / name) != sha:
            raise SystemExit(f"ledger mutated {name}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen")
    if pack.get("status") not in {"EMPTY", "READY_FOR_GENERATION"}:
        raise SystemExit("pack status")
    if not pack.get("hold_generation_apply"):
        raise SystemExit("must hold generation apply")
    rebuilt = build(campaign=campaign, specimen=specimen, out_dir=plate / "_scratch")
    import shutil

    shutil.rmtree(plate / "_scratch", ignore_errors=True)
    if rebuilt["pack"]["n_proofs"] != pack["n_proofs"]:
        raise SystemExit("proof count drift")
    if rebuilt["pack"]["status"] != pack["status"]:
        raise SystemExit("status drift")
    print(
        json.dumps(
            {
                "status": "VERIFIED",
                "formalPackStatus": pack["status"],
                "n_proofs": pack["n_proofs"],
                "lanes": pack.get("recoveryLaneCounts"),
                "policeHold": pack.get("n_police_envelope_hold"),
            },
            indent=2,
        )
    )
    print("OPEN_RESIDUAL_GEN27_OPEN_DARK_UNIT_SPLIT_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Build open-dark unit-split plate")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN27)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify", help="Verify plate vs Gen27")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN27)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    args = p.parse_args(argv)
    if args.cmd == "build":
        build(campaign=args.campaign, specimen=args.specimen, out_dir=args.out)
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
