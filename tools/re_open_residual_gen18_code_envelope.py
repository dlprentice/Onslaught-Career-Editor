#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Instrument Gen18 remaining OPEN residuals via static code envelopes.

Exports OPEN_DARK (255) and OPEN_EXECUTED (101) from Generation 18:

  1. OPEN_EXECUTED full-span STRICT try_envelope_at (len>=8) or tiny/relaxed
     code tails ending in ret/jmp → TERMINAL_BOUNDED_AMBIGUITY.
  2. OPEN_DARK multi-offset align-pad lead + strict/relaxed code tail
     → TERMINAL_BOUNDED_AMBIGUITY (static epilogue/orphan shape only).

Does **not** mutate Gen18/Gen17/Gen10. Does **not** invent names or
claim REBUILD_READY / CALL-entry beyond residual-row shape terminals.
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

SCHEMA = "bea.re.open-residual-gen18-code-envelope.v1"
PACK_SCHEMA = "bea.re.open-residual-gen18-code-envelope-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_CODE_ENVELOPE.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 255
EXPECTED_OPEN_EXECUTED = 101
EXPECTED_RESIDUALS = 6117

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN18 = Path(
    "local-lab/residual-terminal-generation18-table-align-executed-20260805-v1/"
    "generation-18-residual-terminal-table-align-executed"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen18-code-envelope-20260805-v1")

DEFAULT_FALSIFIER = (
    "PE byte change; failed re-decode envelope/tail; residual membership of a "
    "named function body; REBUILD_READY without contract proof"
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


def is_align_pad(blob: bytes, mass, inb) -> bool:
    return bool(blob) and (
        mass.is_pure_pad(blob) or inb.is_full_align_nop_run(blob)
    )


def classify_code_shape(
    blob: bytes, base: int, md, mass, inb
) -> dict[str, Any] | None:
    """Return shape recovery for a full residual subspan (no lead pad)."""
    if not blob or md is None:
        return None
    if is_align_pad(blob, mass, inb):
        return None

    # 1) strict mass envelope (requires len>=8 inside try_envelope_at)
    if len(blob) >= 8:
        env = mass.try_envelope_at(blob, base, md)
        if env:
            return {
                "lane": "STRICT_CODE_ENVELOPE",
                "shapeKind": "STATIC_CODE_DECODE_ENVELOPE",
                "frac": env.get("frac"),
                "non_pad": env.get("non_pad"),
                "first": env.get("first"),
                "last": env.get("last"),
                "note": env.get("note") or "strict_envelope",
            }

    # 2) relaxed / tiny: full linear decode, ends in control, high cover
    insns = list(md.disasm(blob, base))
    if not insns:
        return None
    covered = 0
    last_ct = False
    non_pad = 0
    first = insns[0].mnemonic
    last = insns[0].mnemonic
    for insn in insns:
        if covered + insn.size > len(blob):
            break
        covered += insn.size
        last_ct = insn.mnemonic in mass.CONTROL
        last = insn.mnemonic
        if insn.mnemonic not in {"int3", "nop"}:
            non_pad += 1
        if insn.mnemonic in ("ret", "retn"):
            rest = blob[covered:]
            pad = 0
            while pad < len(rest) and rest[pad] in (0x90, 0xCC) and pad < 16:
                pad += 1
            covered += pad
            if covered < len(blob) and is_align_pad(blob[covered:], mass, inb):
                covered = len(blob)
            break
    frac = covered / len(blob)
    need = 1 if len(blob) < 8 else 2
    if non_pad >= need and frac >= 0.90 and last_ct:
        return {
            "lane": "RELAXED_CODE_TAIL",
            "shapeKind": (
                "TINY_CODE_TAIL" if len(blob) < 8 else "RELAXED_CODE_DECODE_TAIL"
            ),
            "frac": round(frac, 4),
            "non_pad": non_pad,
            "first": first,
            "last": last,
            "note": f"relaxed non_pad={non_pad} frac={frac:.3f} size={len(blob)}",
        }
    return None


def recover_span(
    data: bytes, start: int, end: int, ib: int, secs, md, mass, inb
) -> dict[str, Any] | None:
    blob = span_bytes(data, start, end, ib, secs)
    if blob is None:
        return None
    n = len(blob)
    # offset 0
    c0 = classify_code_shape(blob, start, md, mass, inb)
    if c0:
        return {
            **c0,
            "offset": 0,
            "terms": [
                {
                    "startVa": f"0x{start:08x}",
                    "endVa": f"0x{end:08x}",
                    "bytes": n,
                    "kind": c0["shapeKind"],
                }
            ],
            "kinds": [c0["shapeKind"]],
            "peBytesSha256": hashlib.sha256(blob).hexdigest(),
        }
    max_off = min(16, max(0, n - 2))
    for off in range(1, max_off + 1):
        lead = blob[:off]
        sub = blob[off:]
        if not is_align_pad(lead, mass, inb):
            continue
        c = classify_code_shape(sub, start + off, md, mass, inb)
        if c is None:
            continue
        pad_kind = (
            "ALIGN_PAD_PREFIX"
            if mass.is_pure_pad(lead)
            else "MSVC_ALIGN_NOP_RUN"
        )
        return {
            **c,
            "lane": f"PAD_PLUS_{c['lane']}",
            "offset": off,
            "terms": [
                {
                    "startVa": f"0x{start:08x}",
                    "endVa": f"0x{start + off:08x}",
                    "bytes": off,
                    "kind": pad_kind,
                },
                {
                    "startVa": f"0x{start + off:08x}",
                    "endVa": f"0x{end:08x}",
                    "bytes": n - off,
                    "kind": c["shapeKind"],
                },
            ],
            "kinds": [pad_kind, c["shapeKind"]],
            "peBytesSha256": hashlib.sha256(blob).hexdigest(),
            "note": f"off={off} {c.get('note')}",
        }
    return None


def proposed_for(rec: dict[str, Any], source_state: str) -> dict[str, Any]:
    lane = rec["lane"]
    shape = "+".join(rec["kinds"])
    return {
        "classification": "CODE_CANDIDATE",
        "classificationVerdict": (
            "STATIC_FORMAL_ENVELOPE"
            if "STRICT" in lane
            else "STATIC_FORMAL_CODE_TAIL"
        ),
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
        "shapeKind": shape,
        "recoveryLane": lane,
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

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 18:
        raise SystemExit(f"expected Gen18, got {ready.get('generation')}")
    parent_advance = (ready.get("advance") or {}).get("kind")
    if parent_advance != "RESIDUAL_TERMINAL_OPEN_TABLE_ALIGN_EXECUTED":
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
            rec = recover_span(data, start, end, ib, secs, md, mass, inb)
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
                    }
                )
                lane_counts[f"STILL_OPEN_{source_state}"] += 1
                continue

            # PE recheck: re-run classify on code terms
            ok = True
            notes = [rec.get("note") or ""]
            for t in rec["terms"]:
                lo = int(t["startVa"], 16)
                hi = int(t["endVa"], 16)
                piece = span_bytes(data, lo, hi, ib, secs)
                if piece is None:
                    ok = False
                    notes.append(f"{t['kind']}:unmapped")
                    continue
                k = t["kind"]
                if k in {"ALIGN_PAD_PREFIX", "MSVC_ALIGN_NOP_RUN", "TINY_PAD_GAP"}:
                    if not is_align_pad(piece, mass, inb):
                        ok = False
                        notes.append(f"{k}:not_pad")
                else:
                    # code shape must reclassify
                    again = classify_code_shape(piece, lo, md, mass, inb)
                    if again is None:
                        ok = False
                        notes.append(f"{k}:reclassify_fail")
            if not ok:
                still.append(
                    {
                        "startVa": r["startVa"],
                        "endVa": r["endVa"],
                        "bytes": r.get("bytes"),
                        "source": source_state,
                        "lane": "STILL_OPEN",
                        "entityKey": r.get("entityKey") or "",
                        "questionIds": r.get("questionIds") or "",
                        "note": ";".join(notes),
                    }
                )
                lane_counts[f"STILL_OPEN_{source_state}"] += 1
                continue

            prop = proposed_for(rec, source_state)
            proofs.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": int(r.get("bytes") or (end - start)),
                    "kind": prop["shapeKind"],
                    "subspanKinds": "+".join(rec["kinds"]),
                    "composition": "+".join(rec["kinds"]),
                    "recoveryLane": prop["recoveryLane"],
                    "peBytesSha256": rec["peBytesSha256"],
                    "recheckNote": ";".join(notes),
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "sourceState": source_state,
                    "proposed": prop,
                    "shapeMeta": {
                        "frac": rec.get("frac"),
                        "non_pad": rec.get("non_pad"),
                        "first": rec.get("first"),
                        "last": rec.get("last"),
                        "offset": rec.get("offset"),
                    },
                }
            )
            recovery_rows.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "source": source_state,
                    "recoveryLane": prop["recoveryLane"],
                    "subspanKinds": "+".join(rec["kinds"]),
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
        if prop.get("contractState") == "REBUILD_READY":
            hard.append(f"rebuild {p['startVa']}")
        if p["sourceState"] == "OPEN_EXECUTED_RESIDUAL":
            # must remain observation EXECUTED in parent (checked at apply)
            pass

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
        "campaignGeneration": 18,
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
            f"Exported {EXPECTED_OPEN_DARK} OPEN_DARK + {EXPECTED_OPEN_EXECUTED} OPEN_EXECUTED from Gen18.",
            f"Code-envelope/tail proofs: {len(proofs)} (dark {n_dark} + executed {n_exec}).",
            f"Still open dark: {len(still_dark)}; still open executed: {len(still_exec)}.",
            "All proofs TERMINAL_BOUNDED_AMBIGUITY; question supersession required.",
            "No Gen18 ledger mutation; Gen19 apply is separate.",
        ],
        "non_claims": [
            "Does not invent function names or claim REBUILD_READY",
            "Static envelope/tail is residual-row shape only",
            "Does not prove full arguments/returns/callers",
            "Tiny code tails are epilogue/orphan shapes, not named entries",
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
        "campaignGeneration": 18,
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
            "Gen19 apply only if READY and proofs > 0",
            "Remaining OPEN_DARK: LARGE_MIXED / CODE_LIKE_PARTIAL mass",
            "Remaining OPEN_EXECUTED: non-envelope fragments",
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
            "subspanKinds",
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
        "schema": "bea.re.open-residual-gen18-code-envelope.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_255": summary["counts"]["n_open_dark_input"]
            == EXPECTED_OPEN_DARK,
            "open_executed_101": summary["counts"]["n_open_executed_input"]
            == EXPECTED_OPEN_EXECUTED,
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "only_bounded_ambiguity": all(
                p["proposed"]["terminalState"] == "TERMINAL_BOUNDED_AMBIGUITY"
                for p in pack["proofs"]
            ),
            "ready_or_empty": pack["status"] in {"READY_FOR_GENERATION", "EMPTY"},
            "no_gen19_apply": True,
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
            "Re-export OPEN_DARK/OPEN_EXECUTED from Gen18: 255/101",
            "Re-run build: proof set must match",
            "Gen18 residuals sha must equal ledger_sha_pre",
            "Any REBUILD_READY or invented name",
        ],
    }
    integrity["checks"]["gen18_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"][
        "gen18_residuals_unchanged"
    ]
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen18 OPEN residual code envelope / tail

Status: **MEASURED** / formal pack **{pack['status']}**
OPEN_DARK: **{EXPECTED_OPEN_DARK}** → proofs dark **{pack['n_dark_proofs']}**
OPEN_EXECUTED: **{EXPECTED_OPEN_EXECUTED}** → proofs exec **{pack['n_executed_proofs']}**
Total proofs: **{len(pack['proofs'])}**
Still open: dark **{len(result['still_dark'])}**, executed **{len(result['still_exec'])}**

## Non-claims
- Not Gen19 applied
- Not names / not REBUILD_READY
- Envelope/tail is residual-row shape only
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
    print("OPEN_RESIDUAL_GEN18_CODE_ENVELOPE_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN18)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN18)
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
        print("OPEN_RESIDUAL_GEN18_CODE_ENVELOPE_MEASURED")
        print(f"formal_pack_status={result['pack']['status']}")
        print(f"n_proofs={result['pack']['n_proofs']}")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
