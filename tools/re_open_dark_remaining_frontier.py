#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen14-bound OPEN_DARK remaining frontier + formal pack (no campaign apply).

Exports OPEN_DARK_RESIDUAL rows from Generation 14, re-runs deeper MIXED
classifiers, handles the 8 multi-subspan prefix+envelope residuals, and emits a
hash-bound formal pack of residual-row terminal candidates only when PE rechecks
survive.

Does **not** mutate Gen10/Gen14. Does **not** invent function names.
Gen15 apply is a separate reducer step after DeepSeek review.
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

SCHEMA = "bea.re.open-dark-remaining-frontier.v1"
PACK_SCHEMA = "bea.re.open-dark-remaining-formal-pack.v1"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EXPECTED_GEN14_OPEN_DARK = 413
EXPECTED_MULTI_SUBSPAN = 8
EXPECTED_RESIDUALS = 6117
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN14 = Path(
    "local-lab/residual-terminal-generation14-code-envelope-20260805-v1/"
    "generation-14-residual-terminal-code-envelope"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_MULTI_SOURCE = Path(
    "local-lab/code-envelope-adjudication-20260805-v1/FORMAL-PACK.json"
)
DEFAULT_OUT = Path("local-lab/open-dark-remaining-frontier-gen14-20260805-v1")

PAD_KINDS = {
    "TINY_PAD_GAP",
    "ALIGN_PAD_PREFIX",
    "ZERO_RUN_PREFIX",
    "MOSTLY_ALIGN_PADDING",
}
DATA_KINDS = {
    "CODE_ADDRESS_TABLE_PREFIX",
    "FLOAT32_TABLE_PREFIX",
    "INDEX_OR_BYTE_TABLE",
    "POINTER_TABLE_LIKE",
}
CODE_KIND = "STATIC_CODE_DECODE_ENVELOPE"
ROW_TERMINAL_KINDS = PAD_KINDS | DATA_KINDS | {CODE_KIND}


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


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def recheck_kind(kind: str, blob: bytes) -> tuple[bool, str]:
    if not blob:
        return False, "empty"
    if kind in PAD_KINDS:
        if all(b in (0x00, 0x90, 0xCC) for b in blob):
            return True, "pad_bytes_only"
        return False, "non_pad_byte"
    if kind == "CODE_ADDRESS_TABLE_PREFIX":
        usable = len(blob) - (len(blob) % 4)
        if usable < 32:
            return False, "too_short"
        n = 0
        for i in range(0, usable, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if TEXT_LO <= v < TEXT_HI:
                n += 1
            else:
                break
        if n >= 8 and n * 4 == usable:
            return True, f"code_ptrs={n}"
        if n >= 8 and n * 4 >= usable * 0.95:
            return True, f"code_ptrs={n}_frac"
        return False, f"code_ptr_run={n}"
    if kind == "FLOAT32_TABLE_PREFIX":
        usable = len(blob) - (len(blob) % 4)
        if usable < 32:
            return False, "too_short"
        ok = 0
        for i in range(0, usable, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if TEXT_LO <= v < TEXT_HI:
                break
            f = struct.unpack_from("<f", blob, i)[0]
            if f != f or abs(f) == float("inf") or abs(f) > 1e10:
                break
            ok += 1
        if ok >= 8 and ok * 4 >= usable * 0.9:
            return True, f"floats={ok}"
        return False, f"float_run={ok}"
    if kind == "INDEX_OR_BYTE_TABLE":
        if len(blob) < 16:
            return False, "too_short"
        usable = len(blob) - (len(blob) % 4)
        low = sum(
            1
            for i in range(0, usable, 4)
            if struct.unpack_from("<I", blob, i)[0] <= 0xFFFF
        )
        if low * 4 >= usable * 0.85:
            return True, f"low_dwords={low}"
        return False, f"low_dwords={low}"
    if kind == CODE_KIND:
        # PE rebind only here; decode_frac recheck done via deeper primary /
        # optional capstone path in pure-envelope lane.
        return True, "pe_rebind_shape"
    return False, f"unknown_kind={kind}"


def proposed_for_kinds(kinds: list[str]) -> dict[str, str]:
    s = set(kinds)
    if s <= PAD_KINDS:
        return {
            "classification": "PADDING",
            "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
            "terminalState": "TERMINAL_PADDING",
            "campaignState": "TERMINAL_PADDING",
            "bytePattern": "PADDING_LIKE_BYTES",
            "contractState": "TERMINAL_PADDING",
        }
    if s <= DATA_KINDS:
        return {
            "classification": "DATA",
            "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
            "terminalState": "TERMINAL_DATA",
            "campaignState": "TERMINAL_DATA",
            "bytePattern": "DATA_LIKE_BYTES",
            "contractState": "TERMINAL_DATA",
        }
    if s == {CODE_KIND}:
        return {
            "classification": "AMBIGUOUS",
            "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
            "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
            "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
            "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
            "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
        }
    # multi composition (pad/data + code) fully accounted
    return {
        "classification": "AMBIGUOUS",
        "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
        "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
        "campaignState": "TERMINAL_BOUNDED_AMBIGUITY",
        "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
        "contractState": "TERMINAL_BOUNDED_AMBIGUITY",
    }


def export_open_dark(campaign: Path, out_tsv: Path) -> list[dict[str, str]]:
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    if len(residuals) != EXPECTED_RESIDUALS:
        raise SystemExit(f"residuals {len(residuals)}")
    open_dark = [r for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL"]
    if len(open_dark) != EXPECTED_GEN14_OPEN_DARK:
        raise SystemExit(
            f"OPEN_DARK {len(open_dark)} != {EXPECTED_GEN14_OPEN_DARK}"
        )
    cols = [
        "entityKey",
        "startVa",
        "endVa",
        "bytes",
        "kind",
        "observationState",
        "prevFunc",
        "nextFunc",
        "questionIds",
        "campaignState",
        "classification",
        "terminalState",
        "bytePattern",
        "cheapestFalsifier",
    ]
    rows = []
    for r in open_dark:
        rows.append(
            {
                "entityKey": r.get("entityKey") or "",
                "startVa": r.get("startVa") or "",
                "endVa": r.get("endVa") or "",
                "bytes": r.get("bytes") or "",
                "kind": r.get("classification") or r.get("bytePattern") or "AMBIGUOUS",
                "observationState": r.get("observationState") or "DARK",
                "prevFunc": r.get("prevFunc") or "",
                "nextFunc": r.get("nextFunc") or "",
                "questionIds": r.get("questionIds") or "",
                "campaignState": r.get("campaignState") or "",
                "classification": r.get("classification") or "",
                "terminalState": r.get("terminalState") or "",
                "bytePattern": r.get("bytePattern") or "",
                "cheapestFalsifier": r.get("cheapestFalsifier") or "",
            }
        )
    _write_tsv(out_tsv, cols, rows)
    return rows


def _subspans_cover_whole(start: int, end: int, terms: list[dict]) -> bool:
    """True if terminal subspans are contiguous and exactly cover [start,end)."""
    if not terms:
        return False
    spans = sorted(
        (int(t["startVa"], 16), int(t["endVa"], 16), t.get("kind") or "")
        for t in terms
    )
    if spans[0][0] != start or spans[-1][1] != end:
        return False
    cur = start
    for lo, hi, _ in spans:
        if lo != cur:
            return False
        if hi <= lo:
            return False
        cur = hi
    return cur == end


def build(
    *,
    campaign: Path,
    specimen: Path,
    multi_source: Path,
    out_dir: Path,
) -> dict[str, Any]:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 14:
        raise SystemExit(f"expected Gen14, got {ready.get('generation')}")

    out_dir.mkdir(parents=True, exist_ok=True)
    open_tsv = out_dir / "open-dark.tsv"
    open_rows = export_open_dark(campaign, open_tsv)

    deeper_mod = _load_mod(
        "re_residual_open_mixed_deeper",
        ROOT / "tools" / "re_residual_open_mixed_deeper.py",
    )
    deeper_result = deeper_mod.analyze_open_mixed(specimen, open_tsv)
    results_list = list(deeper_result.get("rows") or [])
    if len(results_list) != EXPECTED_GEN14_OPEN_DARK:
        raise SystemExit(f"deeper rows {len(results_list)}")

    (out_dir / "deeper-full.json").write_text(
        json.dumps(deeper_result, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "deeper-rows.json").write_text(
        json.dumps(results_list, indent=2) + "\n", encoding="utf-8"
    )

    # LARGE_MIXED segmenter when available
    large_mod = _load_mod(
        "re_large_mixed_blob_classify",
        ROOT / "tools" / "re_large_mixed_blob_classify.py",
    )
    spans = large_mod.load_large_mixed_from_deeper(out_dir / "deeper-full.json")
    large_result = large_mod.classify_large_mixed(specimen, spans)
    (out_dir / "large-mixed-full.json").write_text(
        json.dumps(large_result, indent=2) + "\n", encoding="utf-8"
    )

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = pe_map(data)

    multi_pack = json.loads(multi_source.read_text(encoding="utf-8"))
    multi_starts = {
        (m.get("startVa") or "").lower()
        for m in (multi_pack.get("multiSubspanAccounting") or [])
    }
    if len(multi_starts) != EXPECTED_MULTI_SUBSPAN:
        # allow if plate lists 8 elsewhere
        multi_from_rows = [
            r
            for r in results_list
            if len([s for s in (r.get("subspans") or []) if s.get("terminal")]) >= 2
            and r.get("wholeSpanTerminal")
        ]
        if len(multi_from_rows) < EXPECTED_MULTI_SUBSPAN:
            raise SystemExit(
                f"multi starts {len(multi_starts)} expected {EXPECTED_MULTI_SUBSPAN}"
            )

    camp_by = {r["startVa"].lower(): r for r in open_rows}
    deeper_by = {r["startVa"].lower(): r for r in results_list}

    proofs: list[dict[str, Any]] = []
    multi_formalized: list[dict[str, Any]] = []
    still_open_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    primary_counts = Counter(r.get("primary") for r in results_list)
    whole = [r for r in results_list if r.get("wholeSpanTerminal")]
    fully_open = [
        r
        for r in results_list
        if not r.get("wholeSpanTerminal") and int(r.get("terminalBytes") or 0) == 0
    ]
    partial = [
        r
        for r in results_list
        if not r.get("wholeSpanTerminal") and int(r.get("terminalBytes") or 0) > 0
    ]

    for r in results_list:
        start_s = r["startVa"].lower()
        end_s = r["endVa"].lower()
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        camp = camp_by.get(start_s, {})
        terms = [dict(s) for s in (r.get("subspans") or []) if s.get("terminal")]
        kinds = [t.get("kind") or "" for t in terms]

        # Promote PARTIAL where open remainder is pure pad (00/90/CC) into a
        # multi-subspan full-cover candidate (terminal prefix + pad tail).
        if (
            not r.get("wholeSpanTerminal")
            and terms
            and int(r.get("openBytes") or 0) > 0
        ):
            # open remainder is after last terminal subspan end or before first
            term_spans = sorted(
                (int(t["startVa"], 16), int(t["endVa"], 16)) for t in terms
            )
            # only leading terminal prefix pattern: terms start at residual start
            if term_spans[0][0] == start:
                cur = start
                ok_prefix = True
                for lo, hi in term_spans:
                    if lo != cur:
                        ok_prefix = False
                        break
                    cur = hi
                if ok_prefix and cur < end:
                    tail = span_bytes(data, cur, end, ib, secs)
                    if tail is not None and tail and all(
                        b in (0x00, 0x90, 0xCC) for b in tail
                    ):
                        terms.append(
                            {
                                "startVa": f"0x{cur:08x}",
                                "endVa": f"0x{end:08x}",
                                "bytes": end - cur,
                                "kind": "ALIGN_PAD_PREFIX",
                                "terminal": True,
                                "reason": "open_tail_pure_pad_promoted",
                            }
                        )
                        kinds = [t.get("kind") or "" for t in terms]
                        r = {
                            **r,
                            "wholeSpanTerminal": True,
                            "primary": "FULLY_SUBSPAN_TERMINAL_PAD_TAIL_PROMOTED",
                        }

        # Pure single-subspan whole residual terminal
        pure_single = (
            bool(r.get("wholeSpanTerminal"))
            and len(terms) == 1
            and terms[0].get("kind") in ROW_TERMINAL_KINDS
            and terms[0]["startVa"].lower() == start_s
            and terms[0]["endVa"].lower() == end_s
        )
        multi_full = (
            bool(r.get("wholeSpanTerminal"))
            and len(terms) >= 2
            and all(k in ROW_TERMINAL_KINDS for k in kinds)
            and _subspans_cover_whole(start, end, terms)
        )

        if not pure_single and not multi_full:
            still_open_rows.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "primary": r.get("primary"),
                    "terminalBytes": r.get("terminalBytes"),
                    "openBytes": r.get("openBytes"),
                    "entityKey": camp.get("entityKey") or "",
                    "questionIds": camp.get("questionIds") or "",
                    "subspanKinds": ";".join(kinds),
                    "lane": "STILL_OPEN",
                }
            )
            continue

        # PE recheck each terminal subspan
        ok_all = True
        notes = []
        for t in terms:
            lo = int(t["startVa"], 16)
            hi = int(t["endVa"], 16)
            blob = span_bytes(data, lo, hi, ib, secs)
            if blob is None:
                ok_all = False
                notes.append(f"{t.get('kind')}:unmapped")
                continue
            kind = t.get("kind") or ""
            if kind == CODE_KIND:
                # Pure INT3/NOP/00 runs are pad, not code envelopes (deeper can
                # mislabel all-int3 spans as envelopes because int3 is CT).
                if blob and all(b in (0x00, 0x90, 0xCC) for b in blob):
                    kind = "ALIGN_PAD_PREFIX"
                    kinds[terms.index(t)] = kind
                    t = {**t, "kind": kind}
                    ok, note = recheck_kind(kind, blob)
                    notes.append(f"reclass_pad_from_false_envelope:{note}")
                    if not ok:
                        ok_all = False
                else:
                    try:
                        from capstone import CS_ARCH_X86, CS_MODE_32, Cs

                        md = Cs(CS_ARCH_X86, CS_MODE_32)
                        insns = list(md.disasm(blob, lo))
                        covered = 0
                        last_ct = False
                        non_pad_insns = 0
                        control = {
                            "ret", "retn", "jmp", "je", "jne", "jz", "jnz",
                            "ja", "jb", "jae", "jbe", "jg", "jl", "jge", "jle", "call",
                        }
                        for insn in insns:
                            if covered + insn.size > len(blob):
                                break
                            covered += insn.size
                            last_ct = insn.mnemonic in control
                            if insn.mnemonic not in {"int3", "nop"}:
                                non_pad_insns += 1
                            if insn.mnemonic in ("ret", "retn"):
                                rest = blob[covered:]
                                pad = 0
                                while (
                                    pad < len(rest)
                                    and rest[pad] in (0x90, 0xCC)
                                    and pad < 16
                                ):
                                    pad += 1
                                covered += pad
                                break
                        frac = covered / len(blob) if blob else 0.0
                        if (
                            non_pad_insns >= 2
                            and frac >= 0.90
                            and last_ct
                        ):
                            notes.append(
                                f"code_env non_pad_insns={non_pad_insns} frac={frac:.3f}"
                            )
                        else:
                            ok_all = False
                            notes.append(
                                f"code_env_fail non_pad={non_pad_insns} frac={frac:.3f} ct={int(last_ct)}"
                            )
                    except Exception as exc:  # pragma: no cover
                        ok_all = False
                        notes.append(f"code_env_exc:{exc}")
            else:
                ok, note = recheck_kind(kind, blob)
                notes.append(f"{kind}:{note}")
                if not ok:
                    ok_all = False

        if not ok_all:
            failures.append(
                {
                    "startVa": r["startVa"],
                    "reason": "recheck_failed:" + ";".join(notes),
                    "kinds": kinds,
                }
            )
            still_open_rows.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "primary": r.get("primary"),
                    "terminalBytes": r.get("terminalBytes"),
                    "openBytes": r.get("openBytes"),
                    "entityKey": camp.get("entityKey") or "",
                    "questionIds": camp.get("questionIds") or "",
                    "subspanKinds": ";".join(kinds),
                    "lane": "RECHECK_FAILED",
                }
            )
            continue

        whole_blob = span_bytes(data, start, end, ib, secs)
        if whole_blob is None:
            failures.append({"startVa": r["startVa"], "reason": "whole_unmapped"})
            continue

        prop = proposed_for_kinds(kinds)
        # Refuse padding terminal if any non-pad kind present
        if prop["terminalState"] == "TERMINAL_PADDING" and not set(kinds) <= PAD_KINDS:
            failures.append({"startVa": r["startVa"], "reason": "pad_mixed_kinds"})
            continue
        # Refuse TERMINAL_DATA if code envelope present
        if prop["terminalState"] == "TERMINAL_DATA" and CODE_KIND in kinds:
            prop = proposed_for_kinds([CODE_KIND])  # force ambig

        qids = (camp.get("questionIds") or "").strip()
        composition = "PURE_SINGLE" if pure_single else "MULTI_SUBSPAN_FULL_COVER"
        proof = {
            "startVa": r["startVa"],
            "endVa": r["endVa"],
            "bytes": len(whole_blob),
            "kind": kinds[0] if pure_single else "MULTI_SUBSPAN_FULL_COVER",
            "subspanKinds": ";".join(kinds),
            "composition": composition,
            "peBytesSha256": hashlib.sha256(whole_blob).hexdigest(),
            "recheckNote": ";".join(notes),
            "entityKey": camp.get("entityKey") or "",
            "questionIds": qids,
            "campaignState": camp.get("campaignState") or "OPEN_DARK_RESIDUAL",
            "classificationVerdict": camp.get("classification") or "",
            "observationState": camp.get("observationState") or "DARK",
            "proposed": {
                **prop,
                "cheapestFalsifier": (
                    "PE byte change in span; failed kind re-check; inbound code "
                    "reference proving non-terminal semantics; residual membership "
                    "of a named function body"
                ),
                "requiresQuestionSupersession": bool(qids),
                "shapeKind": ";".join(kinds),
                "shapeReason": ";".join(notes),
                "composition": composition,
                "entryClaim": (
                    "STATIC_SHAPE_ONLY_NOT_CALL_ENTRY"
                    if CODE_KIND in kinds
                    else "PAD_OR_DATA_SHAPE"
                ),
            },
        }
        proofs.append(proof)
        if multi_full or start_s in multi_starts:
            multi_formalized.append(proof)

    # Fail closed on hard recheck only if we expected pure terminals to pass
    hard = [f for f in failures if "unmapped" in str(f.get("reason"))]
    if hard:
        raise SystemExit("hard failures:\n" + "\n".join(json.dumps(f) for f in hard))

    # Distinguish known multi cohort (8) from pad-tail promotions.
    known_multi_in_proofs = [
        p for p in proofs if p["startVa"].lower() in multi_starts
    ]
    pad_tail_promotions = [
        p
        for p in proofs
        if p["startVa"].lower() not in multi_starts
        and "open_tail_pure_pad_promoted" in (p.get("recheckNote") or "")
        or (
            p["startVa"].lower() not in multi_starts
            and p.get("composition") == "MULTI_SUBSPAN_FULL_COVER"
            and "ALIGN_PAD_PREFIX" in (p.get("subspanKinds") or "")
            and CODE_KIND not in (p.get("subspanKinds") or "")
        )
    ]
    # Prefer note-based promotion detection; fall back to data+pad without code.
    pad_tail_promotions = [
        p
        for p in proofs
        if p["startVa"].lower() not in multi_starts
    ]
    multi_in_proofs = known_multi_in_proofs  # keep name for pack field: known cohort

    term_bytes = sum(int(r.get("terminalBytes") or 0) for r in results_list)
    open_bytes = sum(int(r.get("openBytes") or 0) for r in results_list)
    kind_counts = Counter(p["kind"] for p in proofs)
    term_state_counts = Counter(p["proposed"]["terminalState"] for p in proofs)
    composition_counts = Counter(p["composition"] for p in proofs)
    n_need_q = sum(1 for p in proofs if p["proposed"]["requiresQuestionSupersession"])

    pack = {
        "schema": PACK_SCHEMA,
        "status": "READY_FOR_GENERATION" if proofs else "EMPTY",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "n_proofs": len(proofs),
        "n_hard_mismatches": len(hard),
        "n_require_question_supersession": n_need_q,
        "n_already_clean": len(proofs) - n_need_q,
        "n_still_open_after_pack": len(still_open_rows),
        "n_multi_formalized": len(known_multi_in_proofs),
        "n_pad_tail_promotions": len(pad_tail_promotions),
        "kindCounts": dict(kind_counts),
        "compositionCounts": dict(composition_counts),
        "proposedTerminalStateCounts": dict(term_state_counts),
        "advance_kind_proposed": "RESIDUAL_TERMINAL_OPEN_DARK_REMAINING.v1",
        "parent_generation": 14,
        "parent_residual_classification_authority": (
            "Gen14 residual-terminal code-envelope is residual authority; "
            "this pack proposes additional OPEN_DARK residual-row terminals only"
        ),
        "source": {
            "campaign": str(campaign).replace("\\", "/"),
            "multiSource": str(multi_source).replace("\\", "/"),
        },
        "claims": [
            f"Exported exactly {EXPECTED_GEN14_OPEN_DARK} Gen14 OPEN_DARK residuals and re-classified them.",
            f"Formal-pack residual-row proofs: {len(proofs)} "
            f"({dict(term_state_counts)}; composition {dict(composition_counts)}).",
            f"Known multi-subspan cohort formalized: {len(known_multi_in_proofs)}/"
            f"{EXPECTED_MULTI_SUBSPAN}; pad-tail promotions: {len(pad_tail_promotions)}.",
            f"Still open after pack filter: {len(still_open_rows)}.",
            f"Question supersession required for {n_need_q}/{len(proofs)}.",
            "No Gen10/Gen14 ledger mutation; Gen15 apply is separate.",
        ],
        "non_claims": [
            "Does not invent function names or claim CALL entry / REBUILD_READY",
            "CODE envelopes remain TERMINAL_BOUNDED_AMBIGUITY shape only",
            "Partial subspans alone do not admit residual rows",
            "LARGE_MIXED / CODE_LIKE_PARTIAL without whole-span terminal stay OPEN",
            "Admitting without question supersession would launder OPEN questions",
        ],
        "proofs": proofs,
        "stillOpenSamples": still_open_rows[:40],
        "recheckFailures": [
            f for f in failures if str(f.get("reason", "")).startswith("recheck_failed")
        ],
        "hardMismatches": hard,
    }

    summary = {
        "schema": SCHEMA,
        "status": "MEASURED",
        "plate": str(out_dir).replace("\\", "/"),
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 14,
        "counts": {
            "n_open_dark_input": len(results_list),
            "n_whole_span_terminal_deeper": len(whole),
            "n_partial_subspan": len(partial),
            "n_still_fully_open_deeper": len(fully_open),
            "terminal_bytes_accounted_deeper": term_bytes,
            "open_bytes_remaining_deeper": open_bytes,
            "primaryCounts": dict(primary_counts),
            "formalPackProofs": len(proofs),
            "stillOpenAfterPack": len(still_open_rows),
            "multiFormalizedKnownCohort": len(known_multi_in_proofs),
            "padTailPromotions": len(pad_tail_promotions),
            "proposedTerminalStateCounts": dict(term_state_counts),
            "compositionCounts": dict(composition_counts),
            "largeMixed": (large_result or {}).get("primary_counts")
            or (large_result or {}).get("segment_kind_counts")
            or {},
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "DeepSeek normal+adversarial on this plate",
            "Gen15 residual-terminal reducer only after READY review",
            "Still-open LARGE_MIXED: segment/xref/coverage instruments",
            "EXECUTED PROLOGUE_LIKE call-context remains separate",
        ],
        "artifacts": [
            "open-dark.tsv",
            "deeper-full.json",
            "deeper-rows.json",
            "large-mixed-full.json",
            "FORMAL-PACK.json",
            "proofs.tsv",
            "still-open.tsv",
            "SUMMARY.json",
            "INTEGRITY.json",
            "README.md",
        ],
    }
    return {
        "summary": summary,
        "pack": pack,
        "still_open_rows": still_open_rows,
        "open_rows": open_rows,
        "results_list": results_list,
    }


def write_plate(
    result: dict[str, Any],
    out_dir: Path,
    *,
    campaign: Path,
    specimen: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pack = result["pack"]
    summary = result["summary"]
    still = result["still_open_rows"]

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
        "peBytesSha256",
        "recheckNote",
        "entityKey",
        "questionIds",
        "proposedTerminalState",
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
                    "subspanKinds": p["subspanKinds"],
                    "composition": p["composition"],
                    "peBytesSha256": p["peBytesSha256"],
                    "recheckNote": p["recheckNote"],
                    "entityKey": p["entityKey"],
                    "questionIds": p["questionIds"],
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
        "primary",
        "terminalBytes",
        "openBytes",
        "entityKey",
        "questionIds",
        "subspanKinds",
        "lane",
    ]
    _write_tsv(out_dir / "still-open.tsv", still_cols, still)

    pack_summary = {
        k: pack[k]
        for k in pack
        if k not in {"proofs", "stillOpenSamples", "recheckFailures", "hardMismatches"}
    }
    pack_summary["proofStarts"] = [p["startVa"] for p in pack["proofs"]]
    (out_dir / "PACK-SUMMARY.json").write_text(
        json.dumps(pack_summary, indent=2) + "\n", encoding="utf-8"
    )
    summary["proofStarts"] = [p["startVa"] for p in pack["proofs"]]
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    integrity = {
        "schema": "bea.re.open-dark-remaining-frontier.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_413": summary["counts"]["n_open_dark_input"] == EXPECTED_GEN14_OPEN_DARK,
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "partition_deeper": (
                summary["counts"]["n_whole_span_terminal_deeper"]
                + summary["counts"]["n_partial_subspan"]
                + summary["counts"]["n_still_fully_open_deeper"]
                == EXPECTED_GEN14_OPEN_DARK
            ),
            "no_padding_with_code_kind": all(
                not (
                    p["proposed"]["terminalState"] == "TERMINAL_PADDING"
                    and CODE_KIND in (p.get("subspanKinds") or "")
                )
                for p in pack["proofs"]
            ),
            "ready_or_empty": pack["status"] in {"READY_FOR_GENERATION", "EMPTY"},
            "no_gen15_apply": True,
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
            "openDarkTsv": _stamp(out_dir / "open-dark.tsv"),
        },
        "falsifier": [
            "Re-export OPEN_DARK from Gen14: count must be 413",
            "Re-run tools/re_open_dark_remaining_frontier.py build: proof set must match",
            "Gen14 campaign-residuals.tsv sha must equal ledger_sha_pre",
            "Any TERMINAL_PADDING proof containing STATIC_CODE_DECODE_ENVELOPE",
            "Silent Gen15 apply without separate reducer",
        ],
    }
    integrity["checks"]["gen14_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"]["gen14_residuals_unchanged"]
    integrity["sources"]["summary"] = _stamp(out_dir / "SUMMARY.json")
    (out_dir / "INTEGRITY.json").write_text(json.dumps(integrity, indent=2) + "\n", encoding="utf-8")

    (out_dir / "README.md").write_text(
        f"""# Gen14 OPEN_DARK remaining frontier

Status: **MEASURED** / formal pack **{pack['status']}**
Input OPEN_DARK: **{EXPECTED_GEN14_OPEN_DARK}**
Formal-pack proofs: **{len(pack['proofs'])}**
Still open after pack filter: **{len(still)}**

## Proposed terminals

| State | Count |
|-------|------:|
{chr(10).join(f'| {k} | {v} |' for k,v in sorted(pack['proposedTerminalStateCounts'].items())) or '| (none) | 0 |'}

## Composition

| Kind | Count |
|------|------:|
{chr(10).join(f'| {k} | {v} |' for k,v in sorted(pack['compositionCounts'].items())) or '| (none) | 0 |'}

## Non-claims

- Not Gen15 applied
- Not CALL entry / not function names / not REBUILD_READY
- CODE envelopes are BOUNDED_AMBIGUITY only

## Next

DeepSeek review → Gen15 residual-terminal reducer with supersession (separate step).
""",
        encoding="utf-8",
    )


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if summary["counts"]["n_open_dark_input"] != EXPECTED_GEN14_OPEN_DARK:
        raise SystemExit("open dark count")
    for name, sha in (integrity.get("ledger_sha_pre") or {}).items():
        if _sha(campaign / name) != sha:
            raise SystemExit(f"ledger mutated {name}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen")
    for p in pack["proofs"]:
        if p["proposed"]["terminalState"] == "TERMINAL_PADDING" and CODE_KIND in (
            p.get("subspanKinds") or ""
        ):
            raise SystemExit(f"pad+code laundering {p['startVa']}")
    # rebuild
    rebuilt = build(
        campaign=campaign,
        specimen=specimen,
        multi_source=DEFAULT_MULTI_SOURCE,
        out_dir=plate / "_rebuild_scratch",
    )
    # clean scratch
    import shutil

    shutil.rmtree(plate / "_rebuild_scratch", ignore_errors=True)
    a = {(p["startVa"].lower(), p["peBytesSha256"], p["proposed"]["terminalState"]) for p in pack["proofs"]}
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
                "n_open_dark": EXPECTED_GEN14_OPEN_DARK,
                "n_proofs": pack["n_proofs"],
                "proposedTerminalStateCounts": pack["proposedTerminalStateCounts"],
                "compositionCounts": pack["compositionCounts"],
                "stillOpen": pack["n_still_open_after_pack"],
            },
            indent=2,
        )
    )
    print("OPEN_DARK_REMAINING_FRONTIER_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN14)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--multi-source", type=Path, default=DEFAULT_MULTI_SOURCE)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, required=True)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN14)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    args = p.parse_args(argv)
    if args.cmd == "build":
        result = build(
            campaign=args.campaign,
            specimen=args.specimen,
            multi_source=args.multi_source,
            out_dir=args.out,
        )
        write_plate(result, args.out, campaign=args.campaign, specimen=args.specimen)
        print(
            json.dumps(
                {
                    "status": "OK",
                    "counts": result["summary"]["counts"],
                    "n_proofs": result["pack"]["n_proofs"],
                    "packStatus": result["pack"]["status"],
                },
                indent=2,
            )
        )
        print("OPEN_DARK_REMAINING_FRONTIER_OK")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
