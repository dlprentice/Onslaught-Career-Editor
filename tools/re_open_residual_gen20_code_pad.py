#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Instrument Gen20 remaining OPEN residuals: code pack + trailing pad / soft multi.

Exports OPEN_DARK (171) and OPEN_EXECUTED (5) from Generation 20.

Recovery lanes (residual-row TERMINAL_BOUNDED_AMBIGUITY only):

  ENVELOPE_PLUS_PAD / MULTI_UNIT_PLUS_PAD
    optional MSVC/pure pad lead + hard code envelope or multi-unit pack
    (n_code>=2, units end ret/retn/jmp) + optional trailing pad.

  SOFT_MULTI_UNIT_EXECUTED
    OPEN_EXECUTED only: sequential units with first ending ret/jmp and
    later units ending any control (call/je/…), full residual cover,
    n_code>=2, >=1 ret. Captures ret+trailing-thunk packs that hard
    multi-unit rejects.

Does **not** mutate Gen20/Gen19/Gen10. Does **not** invent names or
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

SCHEMA = "bea.re.open-residual-gen20-code-pad.v1"
PACK_SCHEMA = "bea.re.open-residual-gen20-code-pad-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_CODE_PAD.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 171
EXPECTED_OPEN_EXECUTED = 5
EXPECTED_RESIDUALS = 6117

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN20 = Path(
    "local-lab/residual-terminal-generation20-multi-unit-20260805-v1/"
    "generation-20-residual-terminal-multi-unit"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen20-code-pad-20260805-v1")

DEFAULT_FALSIFIER = (
    "PE byte change; pad strip + re-decode fails envelope/multi-unit; soft "
    "multi-unit loses ret-first unit; residual membership of a named body; "
    "REBUILD_READY claim"
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


def is_pad(blob: bytes, mass, inb) -> bool:
    return bool(blob) and (
        mass.is_pure_pad(blob) or inb.is_full_align_nop_run(blob)
    )


def pad_kind(blob: bytes, mass, inb) -> str:
    if mass.is_pure_pad(blob):
        return "TINY_PAD_GAP" if len(blob) <= 8 else "ALIGN_PAD_PREFIX"
    return "MSVC_ALIGN_NOP_RUN"


def multi_soft_executed(blob: bytes, base: int, md, mass) -> dict[str, Any] | None:
    """Soft multi-unit for EXECUTED: first unit ret/jmp; later any control."""
    if not blob or len(blob) < 6 or md is None:
        return None
    control = mass.CONTROL
    units: list[dict[str, Any]] = []
    pos = 0
    total_np = 0
    n_ret = 0
    while pos < len(blob):
        while pos < len(blob) and blob[pos] in (0x90, 0xCC):
            pos += 1
        if pos >= len(blob):
            break
        unit_start = pos
        insns = list(md.disasm(blob[pos:], base + pos))
        if not insns:
            return None
        covered = 0
        last_m = ""
        non_pad = 0
        for insn in insns:
            if covered + insn.size > len(blob) - pos:
                break
            covered += insn.size
            last_m = insn.mnemonic
            if insn.mnemonic not in {"int3", "nop"}:
                non_pad += 1
            if insn.mnemonic in {"ret", "retn"}:
                n_ret += 1
            if insn.mnemonic in {"ret", "retn", "jmp"}:
                break
            if units and insn.mnemonic in control:
                break
        if non_pad < 1 or covered == 0 or last_m not in control:
            return None
        if not units and last_m not in {"ret", "retn", "jmp"}:
            return None
        total_np += non_pad
        units.append(
            {
                "kind": "CODE",
                "lo": unit_start,
                "hi": unit_start + covered,
                "last": last_m,
                "non_pad": non_pad,
            }
        )
        pos = unit_start + covered
    if pos != len(blob):
        return None
    if len(units) < 2 or n_ret < 1 or total_np < 3:
        return None
    return {
        "lane": "SOFT_MULTI_UNIT_EXECUTED",
        "shapeKind": f"SOFT_MULTI_UNIT_EXECUTED_x{len(units)}",
        "units": units,
        "n_code": len(units),
        "n_ret": n_ret,
        "total_non_pad": total_np,
    }


def recover_hard_code_pad(
    blob: bytes, base: int, md, mass, inb, mu_mod, env_mod
) -> dict[str, Any] | None:
    """Lead pad + hard multi-unit/envelope head + trail pad."""
    if not blob or len(blob) < 6:
        return None
    if is_pad(blob, mass, inb):
        return None
    n = len(blob)
    for lead in range(0, min(16, n - 4) + 1):
        if lead and not is_pad(blob[:lead], mass, inb):
            continue
        body = blob[lead:]
        max_tr = min(128, max(0, len(body) - 3))
        for trail in range(0, max_tr + 1):
            if trail and not is_pad(body[-trail:], mass, inb):
                continue
            head = body[:-trail] if trail else body
            if len(head) < 3:
                continue
            # require some pad when head alone would already be closed by Gen19/18
            # — still allow trail/lead 0 if head recovers (edge: prior miss)
            mpack = mu_mod.multi_unit_pack(head, base + lead, md, mass)
            if mpack is not None:
                return {
                    "lane": "MULTI_UNIT_PLUS_PAD",
                    "shapeKind": f"MULTI_UNIT_PLUS_PAD_x{mpack['n_code']}",
                    "lead": lead,
                    "trail": trail,
                    "head": len(head),
                    "n_code": mpack["n_code"],
                    "units": mpack.get("units"),
                    "note": f"lead={lead} trail={trail} n_code={mpack['n_code']}",
                }
            cshape = env_mod.classify_code_shape(head, base + lead, md, mass, inb)
            if cshape is not None:
                return {
                    "lane": "ENVELOPE_PLUS_PAD",
                    "shapeKind": f"ENVELOPE_PLUS_PAD/{cshape.get('shapeKind') or cshape.get('lane')}",
                    "lead": lead,
                    "trail": trail,
                    "head": len(head),
                    "envelopeLane": cshape.get("lane"),
                    "note": f"lead={lead} trail={trail} {cshape.get('note') or cshape.get('lane')}",
                }
    return None


def proposed_for(rec: dict[str, Any], source_state: str) -> dict[str, Any]:
    return {
        "classification": "CODE_CANDIDATE",
        "classificationVerdict": (
            "STATIC_SOFT_MULTI_UNIT"
            if rec["lane"] == "SOFT_MULTI_UNIT_EXECUTED"
            else "STATIC_CODE_PLUS_PAD"
        ),
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
    inb = _load_mod(
        "re_open_dark_still_open_inbound",
        ROOT / "tools" / "re_open_dark_still_open_inbound.py",
    )
    mu_mod = _load_mod(
        "re_open_residual_gen19_multi_unit",
        ROOT / "tools" / "re_open_residual_gen19_multi_unit.py",
    )
    env_mod = _load_mod(
        "re_open_residual_gen18_code_envelope",
        ROOT / "tools" / "re_open_residual_gen18_code_envelope.py",
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 20:
        raise SystemExit(f"expected Gen20, got {ready.get('generation')}")
    parent_advance = (ready.get("advance") or {}).get("kind")
    if parent_advance != "RESIDUAL_TERMINAL_OPEN_MULTI_UNIT":
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

    def emit_proof(r: dict, source_state: str, rec: dict) -> None:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        blob = span_bytes(data, start, end, ib, secs)
        assert blob is not None
        prop = proposed_for(rec, source_state)
        pe_sha = hashlib.sha256(blob).hexdigest()
        proofs.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": int(r.get("bytes") or (end - start)),
                "kind": prop["shapeKind"],
                "subspanKinds": prop["shapeKind"],
                "composition": rec.get("note")
                or f"lane={rec['lane']} n_code={rec.get('n_code')}",
                "recoveryLane": prop["recoveryLane"],
                "peBytesSha256": pe_sha,
                "recheckNote": rec.get("note") or rec["lane"],
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": source_state,
                "nCodeUnits": rec.get("n_code") or "",
                "leadPad": rec.get("lead", 0),
                "trailPad": rec.get("trail", 0),
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
                "nCodeUnits": rec.get("n_code") or "",
                "leadPad": rec.get("lead", 0),
                "trailPad": rec.get("trail", 0),
                "proposedTerminalState": prop["terminalState"],
                "entityKey": r.get("entityKey") or "",
            }
        )
        lane_counts[prop["recoveryLane"]] += 1

    for r in dark:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        blob = span_bytes(data, start, end, ib, secs)
        if blob is None:
            raise SystemExit(f"unmapped {r['startVa']}")
        rec = recover_hard_code_pad(blob, start, md, mass, inb, mu_mod, env_mod)
        if rec is None:
            still_dark.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "source": "OPEN_DARK_RESIDUAL",
                    "lane": "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": (
                        "High false-decode / no ret-terminated unit cover; need "
                        "LARGE_MIXED upgrade, inbound xref, or TTD coverage join"
                    ),
                }
            )
            lane_counts["STILL_OPEN_OPEN_DARK_RESIDUAL"] += 1
            continue
        # recheck
        again = recover_hard_code_pad(blob, start, md, mass, inb, mu_mod, env_mod)
        if again is None or again["lane"] != rec["lane"]:
            still_dark.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "source": "OPEN_DARK_RESIDUAL",
                    "lane": "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "note": "recheck_fail",
                }
            )
            lane_counts["STILL_OPEN_OPEN_DARK_RESIDUAL"] += 1
            continue
        emit_proof(r, "OPEN_DARK_RESIDUAL", rec)

    for r in executed:
        if r.get("observationState") != "EXECUTED":
            raise SystemExit(f"exec not EXECUTED {r['startVa']}")
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        blob = span_bytes(data, start, end, ib, secs)
        if blob is None:
            raise SystemExit(f"unmapped {r['startVa']}")
        rec = recover_hard_code_pad(blob, start, md, mass, inb, mu_mod, env_mod)
        if rec is None:
            rec = multi_soft_executed(blob, start, md, mass)
            if rec is not None:
                rec["note"] = (
                    f"soft n_code={rec['n_code']} ends="
                    f"{[u['last'] for u in rec['units']]}"
                )
                rec["lead"] = 0
                rec["trail"] = 0
        if rec is None:
            still_exec.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "source": "OPEN_EXECUTED_RESIDUAL",
                    "lane": "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": (
                        "Body fragment / non-ret tail under EXECUTED; need unit "
                        "split via TTD call-context or inbound ownership"
                    ),
                }
            )
            lane_counts["STILL_OPEN_OPEN_EXECUTED_RESIDUAL"] += 1
            continue
        # recheck
        if rec["lane"] == "SOFT_MULTI_UNIT_EXECUTED":
            again = multi_soft_executed(blob, start, md, mass)
            if again is None or again["n_code"] != rec["n_code"]:
                still_exec.append(
                    {
                        "startVa": r["startVa"],
                        "endVa": r["endVa"],
                        "bytes": r.get("bytes"),
                        "source": "OPEN_EXECUTED_RESIDUAL",
                        "lane": "STILL_OPEN",
                        "entityKey": r.get("entityKey") or "",
                        "questionIds": r.get("questionIds") or "",
                        "note": "soft_recheck_fail",
                    }
                )
                lane_counts["STILL_OPEN_OPEN_EXECUTED_RESIDUAL"] += 1
                continue
        else:
            again = recover_hard_code_pad(blob, start, md, mass, inb, mu_mod, env_mod)
            if again is None or again["lane"] != rec["lane"]:
                still_exec.append(
                    {
                        "startVa": r["startVa"],
                        "endVa": r["endVa"],
                        "bytes": r.get("bytes"),
                        "source": "OPEN_EXECUTED_RESIDUAL",
                        "lane": "STILL_OPEN",
                        "entityKey": r.get("entityKey") or "",
                        "questionIds": r.get("questionIds") or "",
                        "note": "recheck_fail",
                    }
                )
                lane_counts["STILL_OPEN_OPEN_EXECUTED_RESIDUAL"] += 1
                continue
        emit_proof(r, "OPEN_EXECUTED_RESIDUAL", rec)

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
        if prop.get("contractState") == "REBUILD_READY":
            hard.append(f"rebuild {p['startVa']}")
        if p["sourceState"] == "OPEN_EXECUTED_RESIDUAL" and p[
            "recoveryLane"
        ] == "SOFT_MULTI_UNIT_EXECUTED":
            if int(p.get("nCodeUnits") or 0) < 2:
                hard.append(f"soft_units {p['startVa']}")

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
        "campaignGeneration": 20,
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
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK + {EXPECTED_OPEN_EXECUTED} OPEN_EXECUTED from Gen20.",
            f"Code+pad / soft-multi proofs: {len(proofs)} (dark {n_dark} + executed {n_exec}).",
            f"Still open dark: {len(still_dark)}; still open executed: {len(still_exec)}.",
            "All proofs TERMINAL_BOUNDED_AMBIGUITY; question supersession required.",
            "No Gen20 ledger mutation; Gen21 apply is separate.",
        ],
        "non_claims": [
            "Does not invent function names or claim REBUILD_READY",
            "Trailing pad is PE shape only",
            "SOFT_MULTI_UNIT_EXECUTED is residual-row shape under EXECUTED only",
            "Does not prove per-unit ownership or full contracts",
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
        "campaignGeneration": 20,
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
            "Gen21 apply only if READY and proofs > 0",
            "Remaining OPEN_DARK: high false-decode CODE_LIKE without ret units",
            "Remaining OPEN_EXECUTED: 1-2B noise / mid-body fragments",
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
        "leadPad",
        "trailPad",
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
                    "nCodeUnits": p.get("nCodeUnits", ""),
                    "leadPad": p.get("leadPad", 0),
                    "trailPad": p.get("trailPad", 0),
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
            "leadPad",
            "trailPad",
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
        "schema": "bea.re.open-residual-gen20-code-pad.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_171": summary["counts"]["n_open_dark_input"]
            == EXPECTED_OPEN_DARK,
            "open_executed_5": summary["counts"]["n_open_executed_input"]
            == EXPECTED_OPEN_EXECUTED,
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "only_bounded_ambiguity": all(
                p["proposed"]["terminalState"] == "TERMINAL_BOUNDED_AMBIGUITY"
                for p in pack["proofs"]
            ),
            "ready_or_empty": pack["status"] in {"READY_FOR_GENERATION", "EMPTY"},
            "no_gen21_apply": True,
            "soft_multi_only_executed": all(
                p["sourceState"] == "OPEN_EXECUTED_RESIDUAL"
                for p in pack["proofs"]
                if p["recoveryLane"] == "SOFT_MULTI_UNIT_EXECUTED"
            ),
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
            "Re-export OPEN_DARK/OPEN_EXECUTED from Gen20: 171/5",
            "Re-run build: proof set must match",
            "Gen20 residuals sha must equal ledger_sha_pre",
            "SOFT_MULTI_UNIT on OPEN_DARK",
        ],
    }
    integrity["checks"]["gen20_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"][
        "gen20_residuals_unchanged"
    ]
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen20 OPEN residual code+pad / soft multi-unit

Status: **MEASURED** / formal pack **{pack['status']}**
OPEN_DARK: **{EXPECTED_OPEN_DARK}** → proofs dark **{pack['n_dark_proofs']}**
OPEN_EXECUTED: **{EXPECTED_OPEN_EXECUTED}** → proofs exec **{pack['n_executed_proofs']}**
Total proofs: **{len(pack['proofs'])}**
Still open: dark **{len(result['still_dark'])}**, executed **{len(result['still_exec'])}**

## Non-claims
- Not Gen21 applied
- Not names / not REBUILD_READY
- Soft multi-unit is EXECUTED-only residual shape
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
        if p["recoveryLane"] == "SOFT_MULTI_UNIT_EXECUTED":
            if p["sourceState"] != "OPEN_EXECUTED_RESIDUAL":
                raise SystemExit(f"soft on dark {p['startVa']}")
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
    print("OPEN_RESIDUAL_GEN20_CODE_PAD_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN20)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN20)
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
        print("OPEN_RESIDUAL_GEN20_CODE_PAD_MEASURED")
        print(f"formal_pack_status={result['pack']['status']}")
        print(f"n_proofs={result['pack']['n_proofs']}")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
