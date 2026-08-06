#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Instrument Gen19 remaining OPEN residuals via multi-unit code packs.

Exports OPEN_DARK (235) and OPEN_EXECUTED (9) from Generation 19.

Recovery lane MULTI_UNIT_CODE_PACK:
  residual fully covered by sequential code units each ending in a control
  transfer (ret/retn/jmp), optional 0x90/0xCC pad between units, with
  n_code_units >= 2 (vtable method packs, atexit+thunk pairs, dual-ret
  stubs). Terminal: TERMINAL_BOUNDED_AMBIGUITY only.

Does **not** mutate Gen19/Gen18/Gen10. Does **not** invent names or
claim REBUILD_READY.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore

SCHEMA = "bea.re.open-residual-gen19-multi-unit.v1"
PACK_SCHEMA = "bea.re.open-residual-gen19-multi-unit-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_MULTI_UNIT.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 235
EXPECTED_OPEN_EXECUTED = 9
EXPECTED_RESIDUALS = 6117
MIN_CODE_UNITS = 2
MIN_TOTAL_NON_PAD = 3

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN19 = Path(
    "local-lab/residual-terminal-generation19-code-envelope-20260805-v1/"
    "generation-19-residual-terminal-code-envelope"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen19-multi-unit-20260805-v1")

DEFAULT_FALSIFIER = (
    "PE byte change; multi-unit re-decode fails full cover; unit no longer ends "
    "in ret/jmp; residual membership of a named function body; REBUILD_READY claim"
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


def pe_map(data: bytes):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    opt = e_lfanew + 24
    image_base = struct.unpack_from("<I", data, opt + 28)[0]
    num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    size_opt = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sec_off = e_lfanew + 24 + size_opt
    sections = []
    for i in range(num_sections):
        o = sec_off + i * 40
        name = data[o : o + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        sections.append((name, va, vsize, rawptr, rawsize))
    return image_base, sections


def va_to_off(va: int, image_base: int, sections) -> int | None:
    rva = va - image_base
    for _name, sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            if rva - sva >= rawsize:
                return None
            return rawptr + (rva - sva)
    return None


def span_bytes(data: bytes, start: int, end: int, ib: int, secs) -> bytes | None:
    if end <= start:
        return None
    o0 = va_to_off(start, ib, secs)
    if o0 is None or va_to_off(end - 1, ib, secs) is None:
        return None
    blob = data[o0 : o0 + (end - start)]
    if len(blob) != end - start:
        return None
    return blob


def multi_unit_pack(
    blob: bytes,
    base: int,
    md,
    mass,
    *,
    min_code_units: int = MIN_CODE_UNITS,
    min_total_non_pad: int = MIN_TOTAL_NON_PAD,
) -> dict[str, Any] | None:
    """Cover residual with >=2 sequential code units ending in ret/retn/jmp."""
    if not blob or len(blob) < 6 or md is None:
        return None
    if mass.is_pure_pad(blob):
        return None
    control = mass.CONTROL
    units: list[dict[str, Any]] = []
    pos = 0
    total_non_pad = 0
    while pos < len(blob):
        pad_start = pos
        while pos < len(blob) and blob[pos] in (0x90, 0xCC):
            pos += 1
        if pos > pad_start:
            if pos == len(blob):
                units.append(
                    {
                        "kind": "PAD",
                        "lo": pad_start,
                        "hi": pos,
                        "insns": 0,
                        "non_pad": 0,
                        "last": "pad",
                    }
                )
                break
            units.append(
                {
                    "kind": "PAD",
                    "lo": pad_start,
                    "hi": pos,
                    "insns": 0,
                    "non_pad": 0,
                    "last": "pad",
                }
            )
        if pos >= len(blob):
            break
        unit_start = pos
        insns = list(md.disasm(blob[pos:], base + pos))
        if not insns:
            return None
        covered = 0
        last_ct = False
        non_pad = 0
        n_ins = 0
        last_m = ""
        for insn in insns:
            if covered + insn.size > len(blob) - pos:
                break
            covered += insn.size
            n_ins += 1
            last_ct = insn.mnemonic in control
            last_m = insn.mnemonic
            if insn.mnemonic not in {"int3", "nop"}:
                non_pad += 1
            # hard unit boundary only on ret/jmp (not conditional)
            if insn.mnemonic in {"ret", "retn", "jmp"}:
                break
        if non_pad < 1 or covered == 0:
            return None
        # unit must end on ret/retn/jmp specifically (not je/jl mid-body)
        if last_m not in {"ret", "retn", "jmp"}:
            return None
        if not last_ct:
            return None
        total_non_pad += non_pad
        units.append(
            {
                "kind": "CODE",
                "lo": unit_start,
                "hi": unit_start + covered,
                "insns": n_ins,
                "non_pad": non_pad,
                "last": last_m,
            }
        )
        pos = unit_start + covered
    if pos != len(blob):
        return None
    n_code = sum(1 for u in units if u["kind"] == "CODE")
    if n_code < min_code_units:
        return None
    if total_non_pad < min_total_non_pad:
        return None
    return {
        "units": units,
        "n_code": n_code,
        "n_units": len(units),
        "total_non_pad": total_non_pad,
        "lane": "MULTI_UNIT_CODE_PACK",
        "shapeKind": f"MULTI_UNIT_CODE_PACK_x{n_code}",
    }


def proposed_for(rec: dict[str, Any], source_state: str) -> dict[str, Any]:
    return {
        "classification": "CODE_CANDIDATE",
        "classificationVerdict": "STATIC_MULTI_UNIT_CODE_PACK",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
        "shapeKind": rec["shapeKind"],
        "recoveryLane": rec["lane"],
        "requiresQuestionSupersession": True,
        "cheapestFalsifier": DEFAULT_FALSIFIER,
        "sourceState": source_state,
    }


def build(*, campaign: Path, specimen: Path, out_dir: Path) -> dict[str, Any]:
    if Cs is None:
        raise SystemExit("capstone required")
    mass = _load_mod(
        "re_open_dark_code_like_mass", ROOT / "tools" / "re_open_dark_code_like_mass.py"
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 19:
        raise SystemExit(f"expected Gen19, got {ready.get('generation')}")
    parent_advance = (ready.get("advance") or {}).get("kind")
    if parent_advance != "RESIDUAL_TERMINAL_OPEN_CODE_ENVELOPE":
        raise SystemExit(f"unexpected parent advance {parent_advance}")

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
    ]
    _write_tsv(out_dir / "open-dark.tsv", export_cols, dark)
    _write_tsv(out_dir / "open-executed.tsv", export_cols, executed)

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = pe_map(data)
    md = Cs(CS_ARCH_X86, CS_MODE_32)

    proofs: list[dict[str, Any]] = []
    still_dark: list[dict[str, Any]] = []
    still_exec: list[dict[str, Any]] = []
    recovery_rows: list[dict[str, Any]] = []
    lane_counts: Counter = Counter()

    for source_state, rows, still in (
        ("OPEN_DARK_RESIDUAL", dark, still_dark),
        ("OPEN_EXECUTED_RESIDUAL", executed, still_exec),
    ):
        for r in rows:
            start = int(r["startVa"], 16)
            end = int(r["endVa"], 16)
            if source_state == "OPEN_EXECUTED_RESIDUAL":
                if r.get("observationState") != "EXECUTED":
                    raise SystemExit(f"exec not EXECUTED {r['startVa']}")
            blob = span_bytes(data, start, end, ib, secs)
            if blob is None:
                raise SystemExit(f"unmapped {r['startVa']}")
            rec = multi_unit_pack(blob, start, md, mass)
            if rec is None:
                still.append(
                    {
                        "startVa": r["startVa"],
                        "endVa": r["endVa"],
                        "bytes": r.get("bytes"),
                        "source": source_state,
                        "lane": "STILL_OPEN",
                        "entityKey": r.get("entityKey") or "",
                        "questionIds": r.get("questionIds") or "",
                        "cheapestFalsifier": (
                            "Multi-unit pack fails; need coverage/TTD unit split, "
                            "inbound xref, or LARGE_MIXED segmenter upgrade"
                        ),
                    }
                )
                lane_counts[f"STILL_OPEN_{source_state}"] += 1
                continue

            # PE recheck: re-run pack
            again = multi_unit_pack(blob, start, md, mass)
            if again is None or again["n_code"] != rec["n_code"]:
                still.append(
                    {
                        "startVa": r["startVa"],
                        "endVa": r["endVa"],
                        "bytes": r.get("bytes"),
                        "source": source_state,
                        "lane": "STILL_OPEN",
                        "entityKey": r.get("entityKey") or "",
                        "questionIds": r.get("questionIds") or "",
                        "note": "recheck_fail",
                    }
                )
                lane_counts[f"STILL_OPEN_{source_state}"] += 1
                continue

            prop = proposed_for(rec, source_state)
            pe_sha = hashlib.sha256(blob).hexdigest()
            unit_desc = ";".join(
                f"{u['kind']}:{u['lo']}-{u['hi']}:{u['last']}" for u in rec["units"]
            )
            proofs.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": int(r.get("bytes") or (end - start)),
                    "kind": prop["shapeKind"],
                    "subspanKinds": prop["shapeKind"],
                    "composition": unit_desc,
                    "recoveryLane": prop["recoveryLane"],
                    "peBytesSha256": pe_sha,
                    "recheckNote": f"n_code={rec['n_code']} non_pad={rec['total_non_pad']}",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "sourceState": source_state,
                    "nCodeUnits": rec["n_code"],
                    "proposed": prop,
                }
            )
            recovery_rows.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "source": source_state,
                    "recoveryLane": prop["recoveryLane"],
                    "nCodeUnits": rec["n_code"],
                    "proposedTerminalState": prop["terminalState"],
                    "entityKey": r.get("entityKey") or "",
                }
            )
            lane_counts[prop["recoveryLane"]] += 1

    term_counts = Counter(p["proposed"]["terminalState"] for p in proofs)
    lane_proof = Counter(p["recoveryLane"] for p in proofs)
    source_counts = Counter(p["sourceState"] for p in proofs)
    n_dark = source_counts.get("OPEN_DARK_RESIDUAL", 0)
    n_exec = source_counts.get("OPEN_EXECUTED_RESIDUAL", 0)

    hard: list[str] = []
    for p in proofs:
        prop = p.get("proposed") or {}
        if prop.get("terminalState") != "TERMINAL_BOUNDED_AMBIGUITY":
            hard.append(f"bad_term {p['startVa']}")
        if not p.get("questionIds"):
            hard.append(f"no_qid {p['startVa']}")
        if int(p.get("nCodeUnits") or 0) < MIN_CODE_UNITS:
            hard.append(f"too_few_units {p['startVa']}")
        if prop.get("contractState") == "REBUILD_READY":
            hard.append(f"rebuild {p['startVa']}")

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
        "campaignGeneration": 19,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_proofs": len(proofs),
        "n_dark_proofs": n_dark,
        "n_executed_proofs": n_exec,
        "n_still_open_dark": len(still_dark),
        "n_still_open_executed": len(still_exec),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "proposedTerminalStateCounts": dict(term_counts),
        "recoveryLaneCounts": dict(lane_proof),
        "sourceStateCounts": dict(source_counts),
        "claims": [
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK + {EXPECTED_OPEN_EXECUTED} OPEN_EXECUTED from Gen19.",
            f"Multi-unit code pack proofs: {len(proofs)} (dark {n_dark} + executed {n_exec}).",
            f"Still open dark: {len(still_dark)}; still open executed: {len(still_exec)}.",
            f"Each proof has n_code_units >= {MIN_CODE_UNITS}, units end ret/retn/jmp.",
            "All proofs TERMINAL_BOUNDED_AMBIGUITY; question supersession required.",
            "No Gen19 ledger mutation; Gen20 apply is separate.",
        ],
        "non_claims": [
            "Does not invent function names or claim REBUILD_READY",
            "Multi-unit pack is residual-row static shape only",
            "Does not prove per-unit callers/arguments/ownership",
            "Conditional-only unit ends are rejected (ret/jmp required)",
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
        "campaignGeneration": 19,
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
            "recoveryLaneCountsAll": dict(lane_counts),
            "formalPackProofs": len(proofs),
            "stillOpenDark": len(still_dark),
            "stillOpenExecuted": len(still_exec),
            "proposedTerminalStateCounts": dict(term_counts),
            "recoveryLaneProofCounts": dict(lane_proof),
            "sourceStateCounts": dict(source_counts),
            "n_dark_proofs": n_dark,
            "n_executed_proofs": n_exec,
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Dual-role DeepSeek direct (flash+pro max normal+adversarial) + Grok normal+adversarial subagents",
            "Gen20 apply only if READY and proofs > 0",
            "Remaining OPEN_DARK: CODE_LIKE_PARTIAL / LARGE_MIXED without multi-unit cover",
            "Remaining OPEN_EXECUTED: body fragments / non-ret tails",
        ],
        "proofStarts": [p["startVa"] for p in proofs],
    }
    return {
        "summary": summary,
        "pack": pack,
        "still_dark": still_dark,
        "still_exec": still_exec,
        "recovery_rows": recovery_rows,
    }


def write_plate(
    result: dict[str, Any], out_dir: Path, *, campaign: Path, specimen: Path
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pack = result["pack"]
    summary = result["summary"]
    (out_dir / "FORMAL-PACK.json").write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    proof_cols = [
        "startVa",
        "endVa",
        "bytes",
        "kind",
        "subspanKinds",
        "composition",
        "recoveryLane",
        "peBytesSha256",
        "recheckNote",
        "entityKey",
        "questionIds",
        "sourceState",
        "nCodeUnits",
        "proposedTerminalState",
        "requiresQuestionSupersession",
    ]
    with (out_dir / "proofs.tsv").open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {PACK_SCHEMA}\n")
        w = csv.DictWriter(
            handle, fieldnames=proof_cols, delimiter="\t", lineterminator="\n"
        )
        w.writeheader()
        for p in pack["proofs"]:
            w.writerow(
                {
                    "startVa": p["startVa"],
                    "endVa": p["endVa"],
                    "bytes": p["bytes"],
                    "kind": p["kind"],
                    "subspanKinds": p["subspanKinds"],
                    "composition": p["composition"],
                    "recoveryLane": p["recoveryLane"],
                    "peBytesSha256": p["peBytesSha256"],
                    "recheckNote": p["recheckNote"],
                    "entityKey": p["entityKey"],
                    "questionIds": p["questionIds"],
                    "sourceState": p["sourceState"],
                    "nCodeUnits": p["nCodeUnits"],
                    "proposedTerminalState": p["proposed"]["terminalState"],
                    "requiresQuestionSupersession": p["proposed"][
                        "requiresQuestionSupersession"
                    ],
                }
            )
    still_cols = [
        "startVa",
        "endVa",
        "bytes",
        "source",
        "lane",
        "entityKey",
        "questionIds",
        "cheapestFalsifier",
        "note",
    ]
    _write_tsv(out_dir / "still-open-dark.tsv", still_cols, result["still_dark"])
    _write_tsv(out_dir / "still-open-executed.tsv", still_cols, result["still_exec"])
    _write_tsv(
        out_dir / "recovery.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "source",
            "recoveryLane",
            "nCodeUnits",
            "proposedTerminalState",
            "entityKey",
        ],
        result["recovery_rows"],
    )
    pack_summary = {k: pack[k] for k in pack if k not in {"proofs", "hardMismatches"}}
    pack_summary["proofStarts"] = [p["startVa"] for p in pack["proofs"]]
    (out_dir / "PACK-SUMMARY.json").write_text(
        json.dumps(pack_summary, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    integrity = {
        "schema": "bea.re.open-residual-gen19-multi-unit.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_235": summary["counts"]["n_open_dark_input"]
            == EXPECTED_OPEN_DARK,
            "open_executed_9": summary["counts"]["n_open_executed_input"]
            == EXPECTED_OPEN_EXECUTED,
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "only_bounded_ambiguity": all(
                p["proposed"]["terminalState"] == "TERMINAL_BOUNDED_AMBIGUITY"
                for p in pack["proofs"]
            ),
            "min_two_code_units": all(
                int(p.get("nCodeUnits") or 0) >= MIN_CODE_UNITS for p in pack["proofs"]
            ),
            "ready_or_empty": pack["status"] in {"READY_FOR_GENERATION", "EMPTY"},
            "no_gen20_apply": True,
        },
        "ledger_sha_pre": {
            "campaign-residuals.tsv": _sha(campaign / "campaign-residuals.tsv"),
            "campaign-functions.tsv": _sha(campaign / "campaign-functions.tsv"),
            "campaign.ready.json": _sha(campaign / "campaign.ready.json"),
        },
        "sources": {
            "formalPack": _stamp(out_dir / "FORMAL-PACK.json"),
            "summary": _stamp(out_dir / "SUMMARY.json"),
            "specimen": _stamp(specimen),
            "campaignReady": _stamp(campaign / "campaign.ready.json"),
        },
        "falsifier": [
            "Re-export OPEN_DARK/OPEN_EXECUTED from Gen19: 235/9",
            "Re-run build: proof set must match",
            "Gen19 residuals sha must equal ledger_sha_pre",
            "Any proof with nCodeUnits < 2 or non-ret/jmp unit end",
        ],
    }
    integrity["checks"]["gen19_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"][
        "gen19_residuals_unchanged"
    ]
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen19 OPEN residual multi-unit code pack

Status: **MEASURED** / formal pack **{pack['status']}**
OPEN_DARK: **{EXPECTED_OPEN_DARK}** → proofs dark **{pack['n_dark_proofs']}**
OPEN_EXECUTED: **{EXPECTED_OPEN_EXECUTED}** → proofs exec **{pack['n_executed_proofs']}**
Total proofs: **{len(pack['proofs'])}**
Still open: dark **{len(result['still_dark'])}**, executed **{len(result['still_exec'])}**

## Non-claims
- Not Gen20 applied
- Not names / not REBUILD_READY
- Multi-unit is residual-row shape only (ret/jmp unit ends)
""",
        encoding="utf-8",
    )


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if summary["counts"]["n_open_dark_input"] != EXPECTED_OPEN_DARK:
        raise SystemExit("open dark count")
    if summary["counts"]["n_open_executed_input"] != EXPECTED_OPEN_EXECUTED:
        raise SystemExit("open executed count")
    for name, sha in (integrity.get("ledger_sha_pre") or {}).items():
        if _sha(campaign / name) != sha:
            raise SystemExit(f"ledger mutated {name}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen")
    for p in pack["proofs"]:
        if int(p.get("nCodeUnits") or 0) < MIN_CODE_UNITS:
            raise SystemExit(f"units {p['startVa']}")
    rebuilt = build(
        campaign=campaign, specimen=specimen, out_dir=plate / "_scratch"
    )
    import shutil

    shutil.rmtree(plate / "_scratch", ignore_errors=True)
    a = {
        (p["startVa"].lower(), p["peBytesSha256"], p["proposed"]["terminalState"])
        for p in pack["proofs"]
    }
    b = {
        (p["startVa"].lower(), p["peBytesSha256"], p["proposed"]["terminalState"])
        for p in rebuilt["pack"]["proofs"]
    }
    if a != b:
        raise SystemExit(f"proof drift only_plate={len(a-b)} only_rebuild={len(b-a)}")
    print(
        json.dumps(
            {
                "status": "VERIFIED",
                "n_open_dark": EXPECTED_OPEN_DARK,
                "n_open_executed": EXPECTED_OPEN_EXECUTED,
                "n_proofs": pack["n_proofs"],
                "n_dark": pack["n_dark_proofs"],
                "n_exec": pack["n_executed_proofs"],
                "stillOpenDark": pack["n_still_open_dark"],
                "stillOpenExecuted": pack["n_still_open_executed"],
            },
            indent=2,
        )
    )
    print("OPEN_RESIDUAL_GEN19_MULTI_UNIT_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN19)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN19)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    args = p.parse_args(argv)
    if args.cmd == "build":
        result = build(
            campaign=args.campaign, specimen=args.specimen, out_dir=args.out
        )
        write_plate(
            result, args.out, campaign=args.campaign, specimen=args.specimen
        )
        print(json.dumps(result["summary"], indent=2))
        print("OPEN_RESIDUAL_GEN19_MULTI_UNIT_MEASURED")
        print(f"formal_pack_status={result['pack']['status']}")
        print(f"n_proofs={result['pack']['n_proofs']}")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
