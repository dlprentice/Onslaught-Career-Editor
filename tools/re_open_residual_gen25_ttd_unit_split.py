#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen25 OPEN_EXECUTED unit-split instrument (static PE + optional TTD join).

Exports the 4 OPEN_EXECUTED residuals from Generation 25 and classifies each
via cheap static unit-boundary proofs (TTD call-context is the authority for
naming/entry; this plate only closes residual *shape* when PE proves the
bytes are a miscut unit fragment):

  PREV_INSN_SPAN
    residual bytes lie strictly inside one instruction that starts before
    residual start (classic ret imm16 / lea SIB cut).

  JMP_OVER_FRAGMENT
    a short/near jmp immediately before residual lands at residual end
    (skipped alternate-path fragment).

  SWITCH_CASE_ENTRY
    residual start is a dword target of a nearby `jmp [reg*scale+table]`
    switch dispatch (table entry measured on pristine PE).

Terminal: TERMINAL_BOUNDED_AMBIGUITY only. Does not invent names.
Does not mutate Gen25. hold_generation_apply=True (no Gen26 apply here).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore

SCHEMA = "bea.re.open-residual-gen25-ttd-unit-split.v1"
PACK_SCHEMA = "bea.re.open-residual-gen25-ttd-unit-split-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_TTD_UNIT_SPLIT.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 99
EXPECTED_OPEN_EXECUTED = 4
EXPECTED_RESIDUALS = 6117
EXPECTED_EXEC_STARTS = {
    0x004AC6B0,
    0x004DA4BE,
    0x004DA89C,
    0x005772C7,
}

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN25 = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen25-ttd-unit-split-20260805-v1")
DEFAULT_COVERAGE_HINT = Path(
    "local-lab/console-callback-atomic14-post-campaign-20260803-v1/"
    "snapshot/ledger-gaps.tsv"
)

DEFAULT_FALSIFIER = (
    "PE re-decode: residual no longer interior of the pinned instruction / "
    "jmp-over target / switch table dword; TTD call-context proves a different "
    "unit membership; REBUILD_READY or named-entry claim without Gen10 authority"
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


def try_prev_insn_span(
    data: bytes, start: int, end: int, ib: int, secs, md, mass
) -> dict[str, Any] | None:
    """Residual fully interior to one instruction starting before start."""
    if end <= start:
        return None
    for lookback in range(1, 16):
        base = start - lookback
        win_end = max(end, start + 1) + 8
        blob = mass.span_bytes(data, base, win_end, ib, secs)
        if blob is None:
            continue
        for insn in md.disasm(blob, base):
            insn_lo = insn.address
            insn_hi = insn.address + insn.size
            if insn_lo >= end:
                break
            # instruction starts before residual and covers residual fully
            if insn_lo < start and insn_hi >= end:
                return {
                    "lane": "PREV_INSN_SPAN",
                    "shapeKind": f"PREV_INSN_SPAN/{insn.mnemonic}",
                    "insnStartVa": f"0x{insn_lo:08x}",
                    "insnEndVa": f"0x{insn_hi:08x}",
                    "mnemonic": insn.mnemonic,
                    "op_str": insn.op_str,
                    "insnBytesHex": insn.bytes.hex(),
                    "note": (
                        f"residual interior of {insn.mnemonic} "
                        f"0x{insn_lo:08x}-0x{insn_hi:08x}"
                    ),
                }
    return None


def try_jmp_over_fragment(
    data: bytes, start: int, end: int, ib: int, secs, md, mass
) -> dict[str, Any] | None:
    """Short/near jmp just before residual whose target is residual end (or after)."""
    if end <= start:
        return None
    for lookback in range(2, 16):
        base = start - lookback
        blob = mass.span_bytes(data, base, start + 1, ib, secs)
        if blob is None:
            continue
        for insn in md.disasm(blob, base):
            if insn.address + insn.size > start:
                break
            if insn.mnemonic != "jmp":
                continue
            # prefer unconditional short/near relative
            raw = insn.bytes
            target = None
            if len(raw) == 2 and raw[0] == 0xEB:
                rel = struct.unpack("b", raw[1:2])[0]
                target = insn.address + 2 + rel
            elif len(raw) == 5 and raw[0] == 0xE9:
                rel = struct.unpack("<i", raw[1:5])[0]
                target = insn.address + 5 + rel
            if target is None:
                continue
            if target >= end and insn.address + insn.size <= start:
                # residual fully skipped
                return {
                    "lane": "JMP_OVER_FRAGMENT",
                    "shapeKind": "JMP_OVER_FRAGMENT",
                    "jmpVa": f"0x{insn.address:08x}",
                    "jmpTargetVa": f"0x{target:08x}",
                    "jmpBytesHex": raw.hex(),
                    "note": (
                        f"jmp 0x{insn.address:08x} -> 0x{target:08x} skips "
                        f"0x{start:08x}-0x{end:08x}"
                    ),
                }
    return None


def try_switch_case_entry(
    data: bytes, start: int, end: int, ib: int, secs, md, mass
) -> dict[str, Any] | None:
    """Residual start is a dword in a nearby switch jump table."""
    if end <= start:
        return None
    # scan up to 32B before residual for jmp dword ptr [reg*4 + disp32]
    for lookback in range(6, 40):
        base = start - lookback
        blob = mass.span_bytes(data, base, start, ib, secs)
        if blob is None:
            continue
        for insn in md.disasm(blob, base):
            if insn.address + insn.size > start:
                break
            raw = insn.bytes
            # ff 24 xx disp32  or ff 24 9d disp32 patterns for jmp [reg*4+table]
            if len(raw) < 7 or raw[0] != 0xFF:
                continue
            if raw[1] not in (0x24, 0xA0, 0xA1, 0xA2, 0xA3):
                # also allow ff 24 /r with SIB
                pass
            # SIB form: FF /4 with modrm mem
            if raw[1] != 0x24:
                continue
            # FF 24 SIB disp32 — table at last 4 bytes
            if len(raw) < 7:
                continue
            table = struct.unpack_from("<I", raw, len(raw) - 4)[0]
            # read up to 16 dwords from table looking for start
            hits: list[str] = []
            for i in range(16):
                va = table + i * 4
                piece = mass.span_bytes(data, va, va + 4, ib, secs)
                if piece is None or len(piece) != 4:
                    break
                tgt = struct.unpack("<I", piece)[0]
                if tgt == start:
                    hits.append(f"0x{va:08x}")
            if hits:
                return {
                    "lane": "SWITCH_CASE_ENTRY",
                    "shapeKind": "SWITCH_CASE_ENTRY",
                    "dispatchVa": f"0x{insn.address:08x}",
                    "tableVa": f"0x{table:08x}",
                    "tableHitVas": hits,
                    "dispatchBytesHex": raw.hex(),
                    "note": (
                        f"switch jmp at 0x{insn.address:08x} table 0x{table:08x} "
                        f"contains residual start; hits={hits}"
                    ),
                }
    return None


def classify_executed_unit(
    data: bytes, start: int, end: int, ib: int, secs, md, mass
) -> dict[str, Any] | None:
    """First matching static unit-split lane."""
    for fn in (try_prev_insn_span, try_jmp_over_fragment, try_switch_case_entry):
        got = fn(data, start, end, ib, secs, md, mass)
        if got is not None:
            return got
    return None


def proposed_for(rec: dict[str, Any], row: dict[str, str]) -> dict[str, Any]:
    return {
        "classification": "CODE_CANDIDATE",
        "classificationVerdict": f"STATIC_UNIT_SPLIT/{rec['lane']}",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
        "shapeKind": rec["shapeKind"],
        "recoveryLane": rec["lane"],
        "requiresQuestionSupersession": True,
        "cheapestFalsifier": DEFAULT_FALSIFIER,
        "sourceState": "OPEN_EXECUTED_RESIDUAL",
        "prevFunc": row.get("prevFunc") or "",
        "nextFunc": row.get("nextFunc") or "",
    }


def load_coverage_hint(path: Path | None) -> dict[int, dict[str, str]]:
    if path is None or not path.is_file():
        return {}
    out: dict[int, dict[str, str]] = {}
    for r in _read_tsv(path):
        try:
            s = int(r.get("startVa") or r.get("start") or "0", 16)
        except ValueError:
            continue
        out[s] = r
    return out


def build(
    *,
    campaign: Path,
    specimen: Path,
    out_dir: Path,
    coverage_hint: Path | None = None,
) -> dict[str, Any]:
    if Cs is None:
        raise SystemExit("capstone required")
    mass = _load_mod(
        "re_open_dark_code_like_mass", ROOT / "tools" / "re_open_dark_code_like_mass.py"
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 25:
        raise SystemExit(f"expected Gen25, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != "RESIDUAL_TERMINAL_POLICE_REOPEN":
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
    exec_starts = {int(r["startVa"], 16) for r in executed}
    if exec_starts != EXPECTED_EXEC_STARTS:
        raise SystemExit(f"unexpected exec starts {sorted(hex(x) for x in exec_starts)}")

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
    _write_tsv(out_dir / "open-executed.tsv", export_cols, executed)

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = mass.pe_map(data)
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    cov = load_coverage_hint(coverage_hint or DEFAULT_COVERAGE_HINT)

    proofs: list[dict[str, Any]] = []
    still: list[dict[str, Any]] = []
    lane_counts: Counter = Counter()

    for r in executed:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        blob = mass.span_bytes(data, start, end, ib, secs)
        if blob is None:
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": end - start,
                    "lane": "UNMAPPED",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": "Unmapped PE span",
                }
            )
            lane_counts["UNMAPPED"] += 1
            continue
        rec = classify_executed_unit(data, start, end, ib, secs, md, mass)
        cov_row = cov.get(start) or {}
        if rec is None:
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": end - start,
                    "lane": "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "prevFunc": r.get("prevFunc") or cov_row.get("prevFunc") or "",
                    "nextFunc": r.get("nextFunc") or cov_row.get("nextFunc") or "",
                    "cheapestFalsifier": (
                        "No static unit-split (prev-insn / jmp-over / switch-case); "
                        "need elevated TTD call-context on residual start"
                    ),
                }
            )
            lane_counts["STILL_OPEN"] += 1
            continue
        prop = proposed_for(rec, r)
        # attach neighbor names from residual or coverage hint
        if not prop["prevFunc"] and cov_row.get("prevFunc"):
            prop["prevFunc"] = cov_row["prevFunc"]
        if not prop["nextFunc"] and cov_row.get("nextFunc"):
            prop["nextFunc"] = cov_row["nextFunc"]
        proofs.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": end - start,
                "kind": rec["shapeKind"],
                "subspanKinds": rec["shapeKind"],
                "recoveryLane": rec["lane"],
                "peBytesSha256": hashlib.sha256(blob).hexdigest(),
                "recheckNote": rec.get("note") or "",
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": "OPEN_EXECUTED_RESIDUAL",
                "detail": {
                    k: v
                    for k, v in rec.items()
                    if k not in {"lane", "shapeKind", "note"}
                },
                "coverageHint": {
                    "prevFunc": prop["prevFunc"],
                    "nextFunc": prop["nextFunc"],
                    "present": bool(cov_row),
                },
                "proposedTerminalState": prop["terminalState"],
                "proposed": prop,
            }
        )
        lane_counts[rec["lane"]] += 1

    hard: list[str] = []
    for p in proofs:
        if p["sourceState"] != "OPEN_EXECUTED_RESIDUAL":
            hard.append(f"non_exec {p['startVa']}")
        if not p.get("questionIds"):
            hard.append(f"no_qid {p['startVa']}")
        if p["proposedTerminalState"] != "TERMINAL_BOUNDED_AMBIGUITY":
            hard.append(f"bad_term {p['startVa']}")
        # re-check classification
        s = int(p["startVa"], 16)
        e = int(p["endVa"], 16)
        again = classify_executed_unit(data, s, e, ib, secs, md, mass)
        if again is None or again["lane"] != p["recoveryLane"]:
            hard.append(f"recheck_fail {p['startVa']}")

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
        "campaignGeneration": 25,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_proofs": len(proofs),
        "n_still_open_executed": len(still),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "recoveryLaneCounts": dict(Counter(p["recoveryLane"] for p in proofs)),
        "hold_generation_apply": True,
        "claims": [
            f"Exported {EXPECTED_OPEN_EXECUTED} OPEN_EXECUTED from Gen25.",
            f"Static unit-split proofs: {len(proofs)} ({dict(Counter(p['recoveryLane'] for p in proofs))}).",
            f"Still open executed: {len(still)}.",
            "Lanes are PE unit-boundary shape only (prev-insn / jmp-over / switch-case).",
            "Gen10 TTD remains authority for named CALL entry; this plate does not name.",
            "Gen26 apply withheld (hold_generation_apply).",
        ],
        "non_claims": [
            "Does not invent function names or REBUILD_READY",
            "Does not claim Gen10 call-context without a live TTD plate",
            "Neighbor prevFunc/nextFunc labels are ledger hints, not new identity",
            "Does not close OPEN_DARK",
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
        "campaignGeneration": 25,
        "formalPackStatus": pack["status"],
        "counts": {
            "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
            "formalPackProofs": len(proofs),
            "stillOpenExecuted": len(still),
            "laneCounts": dict(lane_counts),
            "recoveryLaneProofCounts": pack["recoveryLaneCounts"],
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Optional: apply unit-split proofs as Gen26 residual-terminal advance",
            "Elevated TTD call-context only if any residual remains STILL_OPEN",
            "Do not claim named entry from this static plate alone",
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
            "prevFunc",
            "nextFunc",
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
        ],
        proofs,
    )
    integrity = {
        "schema": "bea.re.open-residual-gen25-ttd-unit-split.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_executed_4": len(executed) == EXPECTED_OPEN_EXECUTED,
            "exec_starts_pinned": exec_starts == EXPECTED_EXEC_STARTS,
            "specimen_pristine": True,
            "empty_or_ready": pack["status"] in {"EMPTY", "READY_FOR_GENERATION"},
            "no_gen26_apply": True,
            "gen25_unmutated": True,
            "hold_generation_apply": True,
            "all_proofs_rechecked": len(hard) == 0,
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
    integrity["checks"]["gen25_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen25 OPEN_EXECUTED unit-split

Status: **MEASURED** / formal pack **{pack['status']}**  
Proofs: **{len(proofs)}** / 4 · still open: **{len(still)}**

Lanes: PREV_INSN_SPAN · JMP_OVER_FRAGMENT · SWITCH_CASE_ENTRY  
Gen26 apply: **held**. Gen10 TTD remains naming authority.
""",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("OPEN_RESIDUAL_GEN25_TTD_UNIT_SPLIT_MEASURED")
    print(f"formal_pack_status={pack['status']}")
    print(f"n_proofs={pack['n_proofs']}")
    return {"summary": summary, "pack": pack}


def verify_plate(
    plate: Path,
    campaign: Path,
    specimen: Path,
    coverage_hint: Path | None = None,
) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if summary["counts"]["n_open_executed_input"] != EXPECTED_OPEN_EXECUTED:
        raise SystemExit("open executed")
    for name, sha in (integrity.get("ledger_sha_pre") or {}).items():
        if _sha(campaign / name) != sha:
            raise SystemExit(f"ledger mutated {name}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen")
    if pack.get("status") not in {"EMPTY", "READY_FOR_GENERATION"}:
        raise SystemExit("pack status")
    if not pack.get("hold_generation_apply"):
        raise SystemExit("must hold generation apply")
    rebuilt = build(
        campaign=campaign,
        specimen=specimen,
        out_dir=plate / "_scratch",
        coverage_hint=coverage_hint,
    )
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
            },
            indent=2,
        )
    )
    print("OPEN_RESIDUAL_GEN25_TTD_UNIT_SPLIT_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Build unit-split plate for 4 OPEN_EXECUTED")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN25)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    b.add_argument("--coverage-hint", type=Path, default=DEFAULT_COVERAGE_HINT)
    v = sub.add_parser("verify", help="Verify plate vs Gen25")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN25)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    v.add_argument("--coverage-hint", type=Path, default=DEFAULT_COVERAGE_HINT)
    args = p.parse_args(argv)
    if args.cmd == "build":
        build(
            campaign=args.campaign,
            specimen=args.specimen,
            out_dir=args.out,
            coverage_hint=args.coverage_hint,
        )
        return 0
    if args.cmd == "verify":
        verify_plate(
            args.plate,
            args.campaign,
            args.specimen,
            coverage_hint=args.coverage_hint,
        )
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
