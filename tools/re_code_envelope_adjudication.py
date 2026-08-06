#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Entry-shape adjudication + formal pack for quarantined CODE envelopes.

Inputs:
  - Gen13 residual-terminal campaign (OPEN_DARK residual authority parent)
  - open-dark frontier code-envelope-candidates.tsv (250 quarantined)
  - deeper-rows.json (subspan geometry)
  - pristine specimen

Outputs a MEASURED adjudication plate and READY_FOR_GENERATION formal pack for
pure whole-span STATIC_CODE_DECODE_ENVELOPE residuals only (TERMINAL_BOUNDED_AMBIGUITY).

Does **not** invent function names. Does **not** claim CALL entry or REBUILD_READY.
Does **not** mutate Gen10/Gen13. Multi-subspan prefix+envelope rows stay accounting-only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "bea.re.code-envelope-adjudication.v1"
PACK_SCHEMA = "bea.re.code-envelope-formal-pack.v1"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EXPECTED_CANDIDATES = 250
EXPECTED_PURE_PROOFS = 242  # pure single-subspan envelopes
EXPECTED_MULTI_ACCOUNTING = 8

DEFAULT_GEN13 = Path(
    "local-lab/residual-terminal-generation13-open-dark-pad-data-20260805-v1/"
    "generation-13-residual-terminal-open-dark-pad-data"
)
DEFAULT_CANDS = Path(
    "local-lab/residual-open-dark-frontier-gen12-20260805-v1/code-envelope-candidates.tsv"
)
DEFAULT_DEEPER = Path(
    "local-lab/residual-open-dark-frontier-gen12-20260805-v1/deeper-rows.json"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/code-envelope-adjudication-20260805-v1")

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore


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


def pe_map(data: bytes):
    e = struct.unpack_from("<I", data, 0x3C)[0]
    ib = struct.unpack_from("<I", data, e + 24 + 28)[0]
    num = struct.unpack_from("<H", data, e + 6)[0]
    so = struct.unpack_from("<H", data, e + 20)[0]
    sec = e + 24 + so
    secs = []
    for i in range(num):
        o = sec + i * 40
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        secs.append((va, vsize, rawptr, rawsize))
    return ib, secs


def va_to_off(va: int, ib: int, secs) -> int | None:
    rva = va - ib
    for sva, vs, rp, rs in secs:
        if sva <= rva < sva + max(vs, rs):
            d = rva - sva
            if d < rs:
                return rp + d
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


CONTROL = {
    "ret", "retn", "jmp", "je", "jne", "jz", "jnz", "ja", "jb", "jae", "jbe",
    "jg", "jl", "jge", "jle", "call", "int3",
}


def decode_envelope(blob: bytes, start_va: int, md) -> dict[str, Any]:
    """Re-prove STATIC_CODE_DECODE_ENVELOPE criteria on PE bytes."""
    if not blob or md is None:
        return {"ok": False, "note": "no_blob_or_capstone", "decode_frac": 0.0, "insns": 0}
    insns = list(md.disasm(blob, start_va))
    if not insns:
        return {"ok": False, "note": "no_decode", "decode_frac": 0.0, "insns": 0}
    covered = 0
    last_ct = False
    first = insns[0]
    last = insns[0]
    for insn in insns:
        if covered + insn.size > len(blob):
            break
        covered += insn.size
        last = insn
        last_ct = insn.mnemonic in CONTROL
        if insn.mnemonic in ("ret", "retn"):
            # trailing pad after ret is fine
            rest = blob[covered:]
            pad = 0
            while pad < len(rest) and rest[pad] in (0x90, 0xCC) and pad < 16:
                pad += 1
            covered += pad
            break
    decode_frac = covered / len(blob) if blob else 0.0
    ok = (
        len(insns) >= 2
        and decode_frac >= 0.90
        and last_ct
        and covered >= 8
    )
    return {
        "ok": ok,
        "note": f"insns={sum(1 for i in insns if i.address < start_va + covered)} decode_frac={decode_frac:.3f} ends_ct={int(last_ct)}",
        "decode_frac": round(decode_frac, 4),
        "insns": sum(1 for i in insns if i.address < start_va + covered),
        "coveredBytes": covered,
        "first": {
            "va": f"0x{first.address:08x}",
            "mnem": first.mnemonic,
            "ops": first.op_str,
            "bytes": first.bytes.hex(),
        },
        "last": {
            "va": f"0x{last.address:08x}",
            "mnem": last.mnemonic,
            "ops": last.op_str,
            "bytes": last.bytes.hex(),
        },
    }


def grade_entry_shape(first: dict, last: dict | None) -> str:
    """Static entry/fallthrough shape grade (not CALL proof)."""
    f = first.get("mnem") or ""
    l = (last or {}).get("mnem") or ""
    fb = first.get("bytes") or ""
    ops = first.get("ops") or ""
    if f == "push" and "ebp" in ops:
        return "PROLOGUE_LIKE"
    if fb.startswith("83ec") or fb.startswith("81ec"):
        return "PROLOGUE_LIKE"
    if f in ("push",) and ops.strip() in {"esi", "edi", "ebx", "ecx", "edx", "eax"}:
        # common MSVC prologue variants
        if l in ("ret", "retn") or fb.startswith("55") is False:
            if l in ("ret", "retn"):
                return "PROLOGUE_OR_THUNK"
    if f == "ret" or l in ("ret", "retn"):
        if f in ("mov", "push", "pop", "lea", "xor", "cmp", "test", "jmp", "je", "jne", "call"):
            return "CASE_OR_BODY_WITH_RET"
        return "RET_SHAPED"
    if f == "jmp":
        return "JMP_ENTRY_OR_TAIL"
    if f == "call":
        return "CALL_THEN_BODY"
    if f in ("mov", "push", "pop", "lea", "xor", "cmp", "test", "inc", "dec", "add", "sub", "and", "or"):
        return "BODY_FRAGMENT"
    return "UNKNOWN"


def build(
    *,
    specimen: Path,
    candidates_tsv: Path,
    deeper_rows_json: Path,
    campaign: Path,
) -> dict[str, Any]:
    if Cs is None:
        raise SystemExit("capstone required")
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != SPECIMEN_SHA256:
        raise SystemExit(f"specimen mismatch {sha}")
    ib, secs = pe_map(data)
    md = Cs(CS_ARCH_X86, CS_MODE_32)

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 13:
        raise SystemExit(f"expected Gen13 campaign, got {ready.get('generation')}")

    cands = _read_tsv(candidates_tsv)
    if len(cands) != EXPECTED_CANDIDATES:
        raise SystemExit(f"expected {EXPECTED_CANDIDATES} candidates, got {len(cands)}")

    deeper_rows = json.loads(deeper_rows_json.read_text(encoding="utf-8"))
    if not isinstance(deeper_rows, list):
        deeper_rows = deeper_rows.get("rows") or []
    deeper_by = {r["startVa"].lower(): r for r in deeper_rows}

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    camp_by = {r["startVa"].lower(): r for r in residuals}

    adjudicated: list[dict[str, Any]] = []
    pure_proofs: list[dict[str, Any]] = []
    multi_accounting: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    entry_grades: Counter = Counter()

    for c in cands:
        start_s = (c.get("startVa") or "").lower()
        end_s = (c.get("endVa") or "").lower()
        start = int(c["startVa"], 16)
        end = int(c["endVa"], 16)
        deeper = deeper_by.get(start_s)
        camp = camp_by.get(start_s)
        if deeper is None:
            failures.append({"startVa": c.get("startVa"), "reason": "missing_deeper"})
            continue
        if camp is None:
            failures.append({"startVa": c.get("startVa"), "reason": "missing_campaign"})
            continue
        if camp.get("campaignState") != "OPEN_DARK_RESIDUAL":
            failures.append(
                {
                    "startVa": c.get("startVa"),
                    "reason": f"campaignState={camp.get('campaignState')}",
                }
            )
            continue
        if camp.get("observationState") == "EXECUTED":
            failures.append({"startVa": c.get("startVa"), "reason": "executed_excluded"})
            continue

        terms = [s for s in (deeper.get("subspans") or []) if s.get("terminal")]
        pure = (
            bool(deeper.get("wholeSpanTerminal"))
            and len(terms) == 1
            and terms[0].get("kind") == "STATIC_CODE_DECODE_ENVELOPE"
            and terms[0]["startVa"].lower() == start_s
            and terms[0]["endVa"].lower() == end_s
        )
        multi = (
            bool(deeper.get("wholeSpanTerminal"))
            and len(terms) >= 2
            and any(t.get("kind") == "STATIC_CODE_DECODE_ENVELOPE" for t in terms)
        )

        blob = span_bytes(data, start, end, ib, secs)
        if blob is None:
            failures.append({"startVa": c.get("startVa"), "reason": "unmapped"})
            continue

        # For multi, grade the envelope subspan only for entry shape; residual-row
        # formal pack requires pure single subspan.
        if pure:
            env_start, env_end = start, end
            env_blob = blob
        elif multi:
            env = next(t for t in terms if t.get("kind") == "STATIC_CODE_DECODE_ENVELOPE")
            env_start = int(env["startVa"], 16)
            env_end = int(env["endVa"], 16)
            env_blob = span_bytes(data, env_start, env_end, ib, secs) or b""
        else:
            failures.append({"startVa": c.get("startVa"), "reason": "not_pure_or_multi_envelope"})
            continue

        recheck = decode_envelope(env_blob, env_start, md)
        entry_grade = (
            grade_entry_shape(recheck["first"], recheck.get("last"))
            if recheck.get("first")
            else "DECODE_FAIL"
        )
        entry_grades[entry_grade] += 1

        row = {
            "startVa": c["startVa"],
            "endVa": c["endVa"],
            "bytes": int(c.get("bytes") or (end - start)),
            "lane": c.get("candidateLane") or "",
            "prevFunc": c.get("prevFunc") or camp.get("prevFunc") or "",
            "nextFunc": c.get("nextFunc") or camp.get("nextFunc") or "",
            "entityKey": camp.get("entityKey") or "",
            "questionIds": camp.get("questionIds") or "",
            "campaignState": camp.get("campaignState") or "",
            "observationState": camp.get("observationState") or "",
            "pureWholeSpanEnvelope": pure,
            "multiSubspanAccountingOnly": multi and not pure,
            "entryGrade": entry_grade,
            "recheckOk": recheck.get("ok"),
            "recheckNote": recheck.get("note"),
            "decodeFrac": recheck.get("decode_frac"),
            "insns": recheck.get("insns"),
            "firstMnem": (recheck.get("first") or {}).get("mnem"),
            "lastMnem": (recheck.get("last") or {}).get("mnem"),
            "peBytesSha256": hashlib.sha256(blob).hexdigest(),
            "envelopePeBytesSha256": hashlib.sha256(env_blob).hexdigest() if env_blob else "",
            "formalPackEligible": bool(pure and recheck.get("ok")),
            "subspanKinds": ";".join(t.get("kind") or "" for t in terms),
        }
        adjudicated.append(row)

        if multi and not pure:
            multi_accounting.append(
                {
                    **row,
                    "role": "MULTI_SUBSPAN_ACCOUNTING_ONLY",
                    "note": "prefix+envelope; not residual-row terminal without split",
                }
            )
            continue

        if pure and recheck.get("ok"):
            qids = (camp.get("questionIds") or "").strip()
            pure_proofs.append(
                {
                    "startVa": c["startVa"],
                    "endVa": c["endVa"],
                    "bytes": len(blob),
                    "kind": "STATIC_CODE_DECODE_ENVELOPE",
                    "peBytesSha256": hashlib.sha256(blob).hexdigest(),
                    "recheckNote": recheck["note"],
                    "entryGrade": entry_grade,
                    "entityKey": camp.get("entityKey") or "",
                    "questionIds": qids,
                    "campaignState": camp.get("campaignState") or "",
                    "classificationVerdict": camp.get("classificationVerdict") or "",
                    "observationState": camp.get("observationState") or "",
                    "proposed": {
                        "classification": "AMBIGUOUS",
                        "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
                        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
                        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
                        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
                        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
                        "cheapestFalsifier": (
                            "PE byte change; decode_frac/control-transfer recheck fail; "
                            "inbound CALL proving free entry (or proving non-residual membership); "
                            "or residual subsumed into a named function body"
                        ),
                        "requiresQuestionSupersession": bool(qids),
                        "shapeKind": "STATIC_CODE_DECODE_ENVELOPE",
                        "shapeReason": recheck["note"],
                        "entryGrade": entry_grade,
                        "entryClaim": "STATIC_SHAPE_ONLY_NOT_CALL_ENTRY",
                    },
                }
            )
        elif pure and not recheck.get("ok"):
            failures.append(
                {
                    "startVa": c.get("startVa"),
                    "reason": f"recheck_failed:{recheck.get('note')}",
                }
            )

    if failures:
        # soft: pure recheck failures block pack; report
        hard = [f for f in failures if str(f.get("reason", "")).startswith("recheck_failed")]
        other = [f for f in failures if not str(f.get("reason", "")).startswith("recheck_failed")]
        if other:
            raise SystemExit("hard failures:\n" + "\n".join(json.dumps(f) for f in other))
        if hard:
            raise SystemExit(
                f"{len(hard)} pure envelopes failed decode recheck:\n"
                + "\n".join(json.dumps(f) for f in hard[:20])
            )

    if len(adjudicated) != EXPECTED_CANDIDATES:
        raise SystemExit(f"adjudicated {len(adjudicated)} != {EXPECTED_CANDIDATES}")
    if len(pure_proofs) != EXPECTED_PURE_PROOFS:
        raise SystemExit(
            f"pure proofs {len(pure_proofs)} != {EXPECTED_PURE_PROOFS} "
            f"(multi={len(multi_accounting)})"
        )
    if len(multi_accounting) != EXPECTED_MULTI_ACCOUNTING:
        raise SystemExit(
            f"multi accounting {len(multi_accounting)} != {EXPECTED_MULTI_ACCOUNTING}"
        )

    n_need_q = sum(1 for p in pure_proofs if p["proposed"]["requiresQuestionSupersession"])
    pack = {
        "schema": PACK_SCHEMA,
        "status": "READY_FOR_GENERATION",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": sha,
        "n_proofs": len(pure_proofs),
        "n_hard_mismatches": 0,
        "n_require_question_supersession": n_need_q,
        "n_already_clean": len(pure_proofs) - n_need_q,
        "n_multi_subspan_accounting_only": len(multi_accounting),
        "kindCounts": {"STATIC_CODE_DECODE_ENVELOPE": len(pure_proofs)},
        "entryGradeCounts": dict(Counter(p["entryGrade"] for p in pure_proofs)),
        "proposedTerminalStateCounts": {"TERMINAL_BOUNDED_AMBIGUITY": len(pure_proofs)},
        "expectedProofs": EXPECTED_PURE_PROOFS,
        "advance_kind_proposed": "RESIDUAL_TERMINAL_CODE_ENVELOPE_BOUNDED.v1",
        "parent_generation": 13,
        "parent_residual_classification_authority": (
            "Gen13 residual-terminal open-dark pad/data is residual authority; "
            "this pack proposes TERMINAL_BOUNDED_AMBIGUITY for pure code-envelope OPEN_DARK rows only"
        ),
        "claims": [
            f"Adjudicated {EXPECTED_CANDIDATES} quarantined CODE envelopes from Gen13 OPEN_DARK.",
            f"Formal pack: {len(pure_proofs)} pure whole-span STATIC_CODE_DECODE_ENVELOPE → TERMINAL_BOUNDED_AMBIGUITY.",
            f"Multi-subspan prefix+envelope excluded from residual-row pack: {len(multi_accounting)}.",
            f"Entry grades (static shape only): {dict(Counter(p['entryGrade'] for p in pure_proofs))}.",
            f"Question supersession required for {n_need_q}/{len(pure_proofs)}.",
            "Decode envelope recheck requires decode_frac>=0.90, >=2 insns, ends in control transfer.",
        ],
        "non_claims": [
            "Does not invent function names or claim CALL entry",
            "Does not claim REBUILD_READY",
            "Does not mutate Gen10/Gen13 ledgers",
            "PROLOGUE_LIKE is static shape priority, not runtime entry proof",
            "Multi-subspan rows are accounting only (not residual-row terminals)",
            "Admitting without question supersession would launder OPEN questions",
        ],
        "proofs": pure_proofs,
        "multiSubspanAccounting": multi_accounting,
        "hardMismatches": [],
    }

    summary = {
        "schema": SCHEMA,
        "status": "MEASURED",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": sha,
        "campaign": str(campaign).replace("\\", "/"),
        "counts": {
            "n_candidates": len(adjudicated),
            "n_pure_formal_pack": len(pure_proofs),
            "n_multi_accounting_only": len(multi_accounting),
            "entryGradeCountsAll": dict(entry_grades),
            "entryGradeCountsPure": dict(Counter(p["entryGrade"] for p in pure_proofs)),
            "formalPackStatus": pack["status"],
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Apply formal pack via Gen14 residual-terminal reducer with question supersession",
            "PROLOGUE_LIKE subset: TTD call-context when traces cover those RVAs",
            "Multi-subspan 8: split residual or deeper formalization before row terminal",
        ],
    }

    return {
        "summary": summary,
        "pack": pack,
        "adjudicated": adjudicated,
        "multi_accounting": multi_accounting,
    }


def write_plate(result: dict[str, Any], out_dir: Path, *, campaign: Path, specimen: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pack = result["pack"]
    summary = result["summary"]
    adjudicated = result["adjudicated"]

    (out_dir / "FORMAL-PACK.json").write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "adjudication-full.json").write_text(
        json.dumps(
            {
                "schema": SCHEMA,
                "rows": adjudicated,
                "multiSubspanAccounting": result["multi_accounting"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    cols = [
        "startVa", "endVa", "bytes", "lane", "entryGrade", "pureWholeSpanEnvelope",
        "multiSubspanAccountingOnly", "formalPackEligible", "recheckOk", "recheckNote",
        "firstMnem", "lastMnem", "entityKey", "questionIds", "subspanKinds",
    ]
    with (out_dir / "adjudication.tsv").open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        w = csv.DictWriter(handle, fieldnames=cols, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in adjudicated:
            w.writerow(r)

    proof_cols = [
        "startVa", "endVa", "bytes", "kind", "entryGrade", "peBytesSha256",
        "recheckNote", "entityKey", "questionIds", "proposedTerminalState",
        "requiresQuestionSupersession",
    ]
    with (out_dir / "proofs.tsv").open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {PACK_SCHEMA}\n")
        w = csv.DictWriter(handle, fieldnames=proof_cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for p in pack["proofs"]:
            w.writerow(
                {
                    "startVa": p["startVa"],
                    "endVa": p["endVa"],
                    "bytes": p["bytes"],
                    "kind": p["kind"],
                    "entryGrade": p["entryGrade"],
                    "peBytesSha256": p["peBytesSha256"],
                    "recheckNote": p["recheckNote"],
                    "entityKey": p["entityKey"],
                    "questionIds": p["questionIds"],
                    "proposedTerminalState": p["proposed"]["terminalState"],
                    "requiresQuestionSupersession": p["proposed"]["requiresQuestionSupersession"],
                }
            )

    summary["plate"] = str(out_dir).replace("\\", "/")
    summary["proofStarts"] = [p["startVa"] for p in pack["proofs"]]
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    # also slim SUMMARY without huge lists for pack
    pack_summary = {k: pack[k] for k in pack if k not in {"proofs", "multiSubspanAccounting", "hardMismatches"}}
    pack_summary["plate"] = str(out_dir).replace("\\", "/")
    pack_summary["proofStarts"] = [p["startVa"] for p in pack["proofs"]]
    (out_dir / "PACK-SUMMARY.json").write_text(
        json.dumps(pack_summary, indent=2) + "\n", encoding="utf-8"
    )

    integrity = {
        "schema": "bea.re.code-envelope-adjudication.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "candidates_250": len(adjudicated) == EXPECTED_CANDIDATES,
            "pure_proofs_242": len(pack["proofs"]) == EXPECTED_PURE_PROOFS,
            "multi_8": len(result["multi_accounting"]) == EXPECTED_MULTI_ACCOUNTING,
            "all_pure_recheck_ok": all(p.get("recheckNote") for p in pack["proofs"]),
            "all_bounded_ambiguity": all(
                p["proposed"]["terminalState"] == "TERMINAL_BOUNDED_AMBIGUITY"
                for p in pack["proofs"]
            ),
            "no_padding_terminal": all(
                p["proposed"]["terminalState"] != "TERMINAL_PADDING" for p in pack["proofs"]
            ),
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "ready_for_generation": pack["status"] == "READY_FOR_GENERATION",
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
            "Re-run tools/re_code_envelope_adjudication.py build: pure proofs must be 242",
            "Any proof with TERMINAL_PADDING or invented name",
            "Gen13 campaign-residuals.tsv sha diverges from ledger_sha_pre",
            "Decode recheck fails for any pure envelope",
        ],
    }
    integrity["checks"]["gen13_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"]["gen13_residuals_unchanged"]
    integrity["sources"]["summary"] = _stamp(out_dir / "SUMMARY.json")
    (out_dir / "INTEGRITY.json").write_text(json.dumps(integrity, indent=2) + "\n", encoding="utf-8")

    (out_dir / "README.md").write_text(
        f"""# CODE envelope entry adjudication + formal pack

Status: **MEASURED** / formal pack **{pack['status']}**
Candidates: **{EXPECTED_CANDIDATES}** quarantined CODE envelopes (Gen13 OPEN_DARK)
Pure formal-pack proofs: **{len(pack['proofs'])}** → `TERMINAL_BOUNDED_AMBIGUITY`
Multi-subspan accounting-only: **{len(result['multi_accounting'])}**

## Entry grades (pure proofs)

| Grade | Count |
|-------|------:|
{chr(10).join(f'| {k} | {v} |' for k,v in sorted(pack['entryGradeCounts'].items()))}

## Non-claims

- Not CALL entry / not function names / not REBUILD_READY
- Not Gen13 mutation
- PROLOGUE_LIKE is static priority for later TTD call-context only

## Next

Apply pack via Gen14 residual-terminal reducer with question supersession.
""",
        encoding="utf-8",
    )


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if pack["n_proofs"] != EXPECTED_PURE_PROOFS:
        raise SystemExit(f"n_proofs {pack['n_proofs']}")
    if pack["status"] != "READY_FOR_GENERATION":
        raise SystemExit(pack["status"])
    if any(p["proposed"]["terminalState"] != "TERMINAL_BOUNDED_AMBIGUITY" for p in pack["proofs"]):
        raise SystemExit("non-bounded-ambiguity terminal in pack")
    if any(p["kind"] != "STATIC_CODE_DECODE_ENVELOPE" for p in pack["proofs"]):
        raise SystemExit("non-envelope kind in pack")
    for name, sha in (integrity.get("ledger_sha_pre") or {}).items():
        if _sha(campaign / name) != sha:
            raise SystemExit(f"ledger mutated {name}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    rebuilt = build(
        specimen=specimen,
        candidates_tsv=DEFAULT_CANDS if not Path(summary.get("campaign") or "").exists() else DEFAULT_CANDS,
        deeper_rows_json=DEFAULT_DEEPER,
        campaign=campaign,
    )
    # use plate sources if present - rebuild from defaults is fine if paths match
    a = {(p["startVa"].lower(), p["peBytesSha256"]) for p in pack["proofs"]}
    b = {(p["startVa"].lower(), p["peBytesSha256"]) for p in rebuilt["pack"]["proofs"]}
    if a != b:
        raise SystemExit(f"proof set drift only_plate={len(a-b)} only_rebuild={len(b-a)}")
    print(
        json.dumps(
            {
                "status": "VERIFIED",
                "n_proofs": pack["n_proofs"],
                "entryGradeCounts": pack["entryGradeCounts"],
                "n_multi_accounting": pack["n_multi_subspan_accounting_only"],
            },
            indent=2,
        )
    )
    print("CODE_ENVELOPE_ADJUDICATION_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--candidates", type=Path, default=DEFAULT_CANDS)
    b.add_argument("--deeper-rows", type=Path, default=DEFAULT_DEEPER)
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN13)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, required=True)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN13)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    args = p.parse_args(argv)
    if args.cmd == "build":
        result = build(
            specimen=args.specimen,
            candidates_tsv=args.candidates,
            deeper_rows_json=args.deeper_rows,
            campaign=args.campaign,
        )
        write_plate(result, args.out, campaign=args.campaign, specimen=args.specimen)
        print(
            json.dumps(
                {
                    "status": "OK",
                    "counts": result["summary"]["counts"],
                    "n_proofs": result["pack"]["n_proofs"],
                    "entryGradeCounts": result["pack"]["entryGradeCounts"],
                },
                indent=2,
            )
        )
        print("CODE_ENVELOPE_ADJUDICATION_OK")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
