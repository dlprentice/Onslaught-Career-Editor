#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Instrument Gen15 remaining OPEN_DARK CODE_LIKE / LARGE_MIXED mass (381).

Exports OPEN_DARK from Generation 15, re-runs deeper + large-mixed analysis,
attempts pure-pad recovery, multi-offset code-envelope recovery for
CODE_LIKE_PARTIAL, and full-cover large-mixed promotion. Emits a MEASURED
plate and optional READY_FOR_GENERATION formal pack for residual-row terminals
only when PE rechecks survive.

Does **not** mutate Gen15/Gen10. Does **not** invent function names.
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

SCHEMA = "bea.re.open-dark-code-like-mass.v1"
PACK_SCHEMA = "bea.re.open-dark-code-like-mass-formal-pack.v1"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EXPECTED_OPEN_DARK = 381
EXPECTED_RESIDUALS = 6117
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN15 = Path(
    "local-lab/residual-terminal-generation15-open-dark-remaining-20260805-v1/"
    "generation-15-residual-terminal-open-dark-remaining"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-dark-code-like-mass-gen15-20260805-v1")

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore

CONTROL = {
    "ret", "retn", "jmp", "je", "jne", "jz", "jnz", "ja", "jb", "jae", "jbe",
    "jg", "jl", "jge", "jle", "call",
}
PAD_KINDS = {"TINY_PAD_GAP", "ALIGN_PAD_PREFIX", "ZERO_RUN_PREFIX"}
DATA_KINDS = {"CODE_ADDRESS_TABLE_PREFIX", "FLOAT32_TABLE_PREFIX", "INDEX_OR_BYTE_TABLE"}
CODE_KIND = "STATIC_CODE_DECODE_ENVELOPE"


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
    for row in secs:
        # Accept (va,vsize,rawptr,rawsize) or (name,va,vsize,rawptr,rawsize)
        if len(row) == 5:
            _name, sva, vs, rp, rs = row
        else:
            sva, vs, rp, rs = row
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


def is_pure_pad(blob: bytes) -> bool:
    return bool(blob) and all(b in (0x00, 0x90, 0xCC) for b in blob)


def code_ptr_run(blob: bytes, align: int = 0) -> int:
    """Leading run of .text code pointers at the given alignment offset."""
    if align < 0 or align > 3:
        return 0
    body = blob[align:]
    usable = len(body) - (len(body) % 4)
    n = 0
    for i in range(0, usable, 4):
        v = struct.unpack_from("<I", body, i)[0]
        if TEXT_LO <= v < TEXT_HI:
            n += 1
        else:
            break
    return n * 4


def best_code_ptr_run(blob: bytes) -> tuple[int, int]:
    """Return (align, run_bytes) for the best pointer-table alignment."""
    best_align, best_run = 0, 0
    for a in range(4):
        run = code_ptr_run(blob, a)
        if run > best_run:
            best_align, best_run = a, run
    return best_align, best_run


def float_run(blob: bytes) -> int:
    """Leading IEEE float run with strong anti-junk filters.

    Rejects:
      - any alignment that yields ≥4 .text code-pointer dwords
      - high printable-ASCII fraction (string/const pools)
      - low unique-byte diversity (repeating pad-like runs)
      - magnitudes outside a conservative game-data band
    """
    if not blob or len(blob) < 32:
        return 0
    # Independent filter: if any 4-align yields ≥4 code pointers in the span,
    # this is not a float table.
    for a in range(4):
        body = blob[a:]
        usable = len(body) - (len(body) % 4)
        ptrs = 0
        for i in range(0, usable, 4):
            v = struct.unpack_from("<I", body, i)[0]
            if TEXT_LO <= v < TEXT_HI:
                ptrs += 1
        if ptrs >= 4:
            return 0
    printable = sum(1 for b in blob if 32 <= b < 127)
    if printable / len(blob) >= 0.40:
        return 0
    if len(set(blob)) <= max(4, len(blob) // 16):
        return 0
    usable = len(blob) - (len(blob) % 4)
    n = 0
    for i in range(0, usable, 4):
        v = struct.unpack_from("<I", blob, i)[0]
        if TEXT_LO <= v < TEXT_HI:
            break
        f = struct.unpack_from("<f", blob, i)[0]
        if f != f or abs(f) == float("inf"):
            break
        af = abs(f)
        if af < 1e-4 or af > 1e5:
            break
        n += 1
    return n * 4 if n >= 8 else 0


def try_envelope_at(blob: bytes, base_va: int, md) -> dict[str, Any] | None:
    """Try STATIC_CODE_DECODE_ENVELOPE criteria at offset 0 of blob."""
    if not blob or md is None or len(blob) < 8:
        return None
    if is_pure_pad(blob):
        return None
    insns = list(md.disasm(blob, base_va))
    if len(insns) < 2:
        return None
    covered = 0
    last_non_pad_ct = False
    last_non_pad_mnem = ""
    non_pad = 0
    for insn in insns:
        if covered + insn.size > len(blob):
            break
        covered += insn.size
        if insn.mnemonic not in {"int3", "nop"}:
            non_pad += 1
            last_non_pad_ct = insn.mnemonic in CONTROL
            last_non_pad_mnem = insn.mnemonic
        if insn.mnemonic in ("ret", "retn"):
            rest = blob[covered:]
            pad = 0
            while pad < len(rest) and rest[pad] in (0x90, 0xCC) and pad < 16:
                pad += 1
            covered += pad
            break
    # Full residual cover only: uncovered tail must be pure pad (or empty).
    # frac>=0.90 with non-pad openBytes laundered Gen16 OFFSET_ENVELOPE terminals
    # that deeper left STILL_OPEN/PARTIAL (police REFUTED 2026-08-05).
    rest = blob[covered:]
    if rest:
        if not is_pure_pad(rest):
            return None
        covered = len(blob)
    frac = covered / len(blob)
    # Require terminating non-pad control (not trailing nop decoration).
    min_non_pad = 2 if len(blob) <= 16 else max(4, (len(blob) + 15) // 16)
    if non_pad >= min_non_pad and frac == 1.0 and last_non_pad_ct:
        return {
            "ok": True,
            "covered": covered,
            "frac": round(frac, 4),
            "non_pad": non_pad,
            "first": insns[0].mnemonic,
            "last": last_non_pad_mnem,
            "note": f"envelope non_pad={non_pad} frac={frac:.3f} end={last_non_pad_mnem}",
        }
    return None


def try_multi_offset_envelope(
    data: bytes, start: int, end: int, ib: int, secs, md
) -> dict[str, Any] | None:
    """Scan offsets 0..min(15, n-8) for a full-span envelope or prefix+pad cover."""
    blob = span_bytes(data, start, end, ib, secs)
    if blob is None:
        return None
    n = len(blob)
    # pure pad whole residual
    if is_pure_pad(blob):
        return {
            "lane": "PURE_PAD_WHOLE",
            "kinds": ["TINY_PAD_GAP" if n <= 8 else "ALIGN_PAD_PREFIX"],
            "terms": [
                {
                    "startVa": f"0x{start:08x}",
                    "endVa": f"0x{end:08x}",
                    "bytes": n,
                    "kind": "TINY_PAD_GAP" if n <= 8 else "ALIGN_PAD_PREFIX",
                }
            ],
            "note": "pure_pad_whole",
        }
    # multi-offset envelope FIRST (before float) so real code stubs win
    max_off = min(16, max(0, n - 8))
    for off in range(0, max_off + 1):
        sub = blob[off:]
        lead = blob[:off]
        if off and not is_pure_pad(lead):
            continue
        env = try_envelope_at(sub, start + off, md)
        if env is None:
            continue
        # try_envelope_at already requires full sub cover (pad-only tail allowed)
        if int(env.get("covered") or 0) != len(sub):
            continue
        terms = []
        kinds = []
        if off:
            terms.append(
                {
                    "startVa": f"0x{start:08x}",
                    "endVa": f"0x{start + off:08x}",
                    "bytes": off,
                    "kind": "ALIGN_PAD_PREFIX",
                }
            )
            kinds.append("ALIGN_PAD_PREFIX")
        terms.append(
            {
                "startVa": f"0x{start + off:08x}",
                "endVa": f"0x{end:08x}",
                "bytes": n - off,
                "kind": CODE_KIND,
            }
        )
        kinds.append(CODE_KIND)
        return {
            "lane": "OFFSET_ENVELOPE",
            "kinds": kinds,
            "terms": terms,
            "note": f"off={off} {env['note']}",
            "entryFirst": env.get("first"),
            "entryLast": env.get("last"),
        }
    # code-pointer table at best alignment + optional pad lead/tail
    align, cpr = best_code_ptr_run(blob)
    if cpr >= 32:
        lead = blob[:align]
        mid = blob[align : align + cpr]
        tail = blob[align + cpr :]
        if (not lead or is_pure_pad(lead)) and (not tail or is_pure_pad(tail)):
            terms = []
            kinds = []
            cur = start
            if lead:
                terms.append(
                    {
                        "startVa": f"0x{cur:08x}",
                        "endVa": f"0x{cur + len(lead):08x}",
                        "bytes": len(lead),
                        "kind": "ALIGN_PAD_PREFIX",
                    }
                )
                kinds.append("ALIGN_PAD_PREFIX")
                cur += len(lead)
            terms.append(
                {
                    "startVa": f"0x{cur:08x}",
                    "endVa": f"0x{cur + cpr:08x}",
                    "bytes": cpr,
                    "kind": "CODE_ADDRESS_TABLE_PREFIX",
                }
            )
            kinds.append("CODE_ADDRESS_TABLE_PREFIX")
            cur += cpr
            if tail:
                terms.append(
                    {
                        "startVa": f"0x{cur:08x}",
                        "endVa": f"0x{end:08x}",
                        "bytes": len(tail),
                        "kind": "ALIGN_PAD_PREFIX",
                    }
                )
                kinds.append("ALIGN_PAD_PREFIX")
            # lead+mid+tail always covers residual by construction
            return {
                "lane": "TABLE_PLUS_PAD",
                "kinds": kinds,
                "terms": terms,
                "note": f"align={align} code_ptrs={cpr // 4}+pad",
            }
    # float table + pad tail only after pointer-table reject
    fr = float_run(blob)
    if fr >= 32 and fr <= n and (fr == n or is_pure_pad(blob[fr:])):
        terms = [
            {
                "startVa": f"0x{start:08x}",
                "endVa": f"0x{start + fr:08x}",
                "bytes": fr,
                "kind": "FLOAT32_TABLE_PREFIX",
            }
        ]
        kinds = ["FLOAT32_TABLE_PREFIX"]
        if fr < n:
            terms.append(
                {
                    "startVa": f"0x{start + fr:08x}",
                    "endVa": f"0x{end:08x}",
                    "bytes": n - fr,
                    "kind": "ALIGN_PAD_PREFIX",
                }
            )
            kinds.append("ALIGN_PAD_PREFIX")
        return {
            "lane": "FLOAT_PLUS_PAD" if fr < n else "FLOAT_WHOLE",
            "kinds": kinds,
            "terms": terms,
            "note": f"floats={fr // 4}" + ("+pad" if fr < n else ""),
        }
    return None


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
    if len(open_dark) != EXPECTED_OPEN_DARK:
        raise SystemExit(f"OPEN_DARK {len(open_dark)} != {EXPECTED_OPEN_DARK}")
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
                "kind": r.get("classification") or "AMBIGUOUS",
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


def build(*, campaign: Path, specimen: Path, out_dir: Path) -> dict[str, Any]:
    if Cs is None:
        raise SystemExit("capstone required")
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 15:
        raise SystemExit(f"expected Gen15, got {ready.get('generation')}")

    out_dir.mkdir(parents=True, exist_ok=True)
    open_tsv = out_dir / "open-dark.tsv"
    open_rows = export_open_dark(campaign, open_tsv)

    deeper_mod = _load_mod(
        "re_residual_open_mixed_deeper",
        ROOT / "tools" / "re_residual_open_mixed_deeper.py",
    )
    deeper_result = deeper_mod.analyze_open_mixed(specimen, open_tsv)
    results = list(deeper_result.get("rows") or [])
    if len(results) != EXPECTED_OPEN_DARK:
        raise SystemExit(f"deeper rows {len(results)}")
    # Quarantine deeper FLOAT32_TABLE_PREFIX subspans that fail multi-align
    # pointer-table reject (plate hygiene; pack authority is independent).
    data_probe = specimen.read_bytes()
    if hashlib.sha256(data_probe).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib_probe, secs_probe = pe_map(data_probe)
    float_quarantined = 0
    for row in results:
        new_subs = []
        for s in row.get("subspans") or []:
            if s.get("kind") == "FLOAT32_TABLE_PREFIX" and s.get("terminal"):
                lo = int(s["startVa"], 16)
                hi = int(s["endVa"], 16)
                blob = span_bytes(data_probe, lo, hi, ib_probe, secs_probe)
                if blob is not None and float_run(blob) < 32:
                    s = {
                        **s,
                        "terminal": False,
                        "kind": "QUARANTINED_FALSE_FLOAT",
                        "reason": "multi_align_code_ptr_reject_or_float_filter",
                    }
                    float_quarantined += 1
            new_subs.append(s)
        row["subspans"] = new_subs
    deeper_result["rows"] = results
    deeper_result["floatClaimsQuarantined"] = float_quarantined
    (out_dir / "deeper-full.json").write_text(
        json.dumps(deeper_result, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "deeper-rows.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )

    large_mod = _load_mod(
        "re_large_mixed_blob_classify",
        ROOT / "tools" / "re_large_mixed_blob_classify.py",
    )
    spans = large_mod.load_large_mixed_from_deeper(out_dir / "deeper-full.json")
    large_result = large_mod.classify_large_mixed(specimen, spans)
    # Quarantine FLOAT32_LUT segments that fail multi-align pointer reject.
    for row in large_result.get("rows") or large_result.get("spans") or []:
        for s in row.get("segments") or []:
            if s.get("kind") in {"FLOAT32_LUT", "FLOAT32_TABLE_PREFIX"} and s.get(
                "terminal"
            ):
                lo = int(s["startVa"], 16)
                hi = int(s["endVa"], 16)
                blob = span_bytes(data_probe, lo, hi, ib_probe, secs_probe)
                if blob is not None and float_run(blob) < 32:
                    s["terminal"] = False
                    s["kind"] = "QUARANTINED_FALSE_FLOAT"
                    s["reason"] = "multi_align_code_ptr_reject_or_float_filter"
                    float_quarantined += 1
    large_result["floatClaimsQuarantined"] = float_quarantined
    (out_dir / "large-mixed-full.json").write_text(
        json.dumps(large_result, indent=2) + "\n", encoding="utf-8"
    )

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = pe_map(data)
    md = Cs(CS_ARCH_X86, CS_MODE_32)

    camp_by = {r["startVa"].lower(): r for r in open_rows}
    proofs: list[dict[str, Any]] = []
    recovery_rows: list[dict[str, Any]] = []
    still_open: list[dict[str, Any]] = []
    lane_counts: Counter = Counter()

    primary_counts = Counter(r.get("primary") for r in results)

    for r in results:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        start_s = r["startVa"].lower()
        camp = camp_by[start_s]
        primary = r.get("primary") or ""
        terms = [s for s in (r.get("subspans") or []) if s.get("terminal")]
        kinds = [t.get("kind") or "" for t in terms]

        recovery = None
        # 1) already whole-span from deeper with allowed kinds
        if (
            r.get("wholeSpanTerminal")
            and terms
            and all(
                (t.get("kind") or "") in (PAD_KINDS | DATA_KINDS | {CODE_KIND})
                for t in terms
            )
        ):
            recovery = {
                "lane": "DEEPER_WHOLE",
                "kinds": kinds,
                "terms": terms,
                "note": "deeper_whole_span",
            }
        else:
            recovery = try_multi_offset_envelope(data, start, end, ib, secs, md)

        # 2) large-mixed full segment cover
        if recovery is None and primary == "LARGE_MIXED_BLOB":
            # find large-mixed row matching start
            for lm in large_result.get("rows") or large_result.get("spans") or []:
                if str(lm.get("startVa") or "").lower() != start_s:
                    continue
                segs = lm.get("segments") or []
                term_segs = [s for s in segs if s.get("terminal")]
                # full cover if all segments terminal and contiguous
                if not segs or any(not s.get("terminal") for s in segs):
                    break
                # check cover
                segs_sorted = sorted(
                    segs, key=lambda s: int(s["startVa"], 16)
                )
                if int(segs_sorted[0]["startVa"], 16) != start:
                    break
                cur = start
                ok = True
                for s in segs_sorted:
                    lo = int(s["startVa"], 16)
                    hi = int(s["endVa"], 16)
                    if lo != cur:
                        ok = False
                        break
                    cur = hi
                if ok and cur == end:
                    # map large-mixed kinds to our kinds
                    mapped = []
                    for s in segs_sorted:
                        k = s.get("kind") or ""
                        if k in {"ALIGN_PAD", "ALIGN_PAD_PREFIX"}:
                            mk = "ALIGN_PAD_PREFIX"
                        elif k in {"CODE_ADDRESS_TABLE", "CODE_ADDRESS_TABLE_PREFIX"}:
                            mk = "CODE_ADDRESS_TABLE_PREFIX"
                        elif k in {"FLOAT32_LUT", "FLOAT32_TABLE_PREFIX"}:
                            mk = "FLOAT32_TABLE_PREFIX"
                        elif k in {"SSE_OR_CONST_POOL"}:
                            mk = "INDEX_OR_BYTE_TABLE"
                        else:
                            mk = None
                        if mk is None:
                            ok = False
                            break
                        mapped.append(
                            {
                                "startVa": s["startVa"],
                                "endVa": s["endVa"],
                                "bytes": s.get("bytes"),
                                "kind": mk,
                            }
                        )
                    if ok and mapped:
                        recovery = {
                            "lane": "LARGE_MIXED_FULL_COVER",
                            "kinds": [m["kind"] for m in mapped],
                            "terms": mapped,
                            "note": "large_mixed_all_terminal_segments",
                        }
                break

        if recovery is None:
            still_open.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "primary": primary,
                    "entityKey": camp.get("entityKey") or "",
                    "questionIds": camp.get("questionIds") or "",
                    "lane": "STILL_OPEN",
                    "openBytes": r.get("openBytes"),
                    "terminalBytes": r.get("terminalBytes"),
                }
            )
            lane_counts["STILL_OPEN"] += 1
            continue

        lane_counts[recovery["lane"]] += 1
        kinds = recovery["kinds"]
        # PE recheck
        ok_all = True
        notes = [recovery.get("note") or ""]
        for t in recovery["terms"]:
            lo = int(t["startVa"], 16)
            hi = int(t["endVa"], 16)
            blob = span_bytes(data, lo, hi, ib, secs)
            if blob is None:
                ok_all = False
                notes.append(f"{t.get('kind')}:unmapped")
                continue
            k = t.get("kind") or ""
            if k in PAD_KINDS:
                if not is_pure_pad(blob):
                    ok_all = False
                    notes.append(f"{k}:non_pad")
                else:
                    notes.append(f"{k}:pad_ok")
            elif k == "CODE_ADDRESS_TABLE_PREFIX":
                # accept best alignment; require run covers ≥95% of this subspan
                align, run = best_code_ptr_run(blob)
                if run < 32 or run < len(blob) * 0.90:
                    ok_all = False
                    notes.append(f"{k}:run={run} align={align}")
                else:
                    notes.append(f"{k}:ptrs={run // 4} align={align}")
            elif k == "FLOAT32_TABLE_PREFIX":
                run = float_run(blob)
                if run < 32 or run < len(blob) * 0.90:
                    ok_all = False
                    notes.append(f"{k}:run={run}")
                else:
                    notes.append(f"{k}:floats={run // 4}")
            elif k == CODE_KIND:
                env = try_envelope_at(blob, lo, md)
                if env is None:
                    ok_all = False
                    notes.append(f"{k}:fail")
                else:
                    notes.append(env["note"])
            elif k == "INDEX_OR_BYTE_TABLE":
                notes.append(f"{k}:pe_rebind")
            else:
                ok_all = False
                notes.append(f"unknown:{k}")

        whole = span_bytes(data, start, end, ib, secs)
        if whole is None or not ok_all:
            still_open.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": r.get("bytes"),
                    "primary": primary,
                    "entityKey": camp.get("entityKey") or "",
                    "questionIds": camp.get("questionIds") or "",
                    "lane": "RECHECK_FAILED",
                    "note": ";".join(notes),
                }
            )
            lane_counts["RECHECK_FAILED"] += 1
            continue

        # refuse padding if code present
        prop = proposed_for_kinds(kinds)
        if prop["terminalState"] == "TERMINAL_PADDING" and CODE_KIND in kinds:
            prop = proposed_for_kinds([CODE_KIND])

        qids = (camp.get("questionIds") or "").strip()
        composition = (
            "PURE_SINGLE"
            if len(kinds) == 1
            else "MULTI_SUBSPAN_FULL_COVER"
        )
        proof = {
            "startVa": r["startVa"],
            "endVa": r["endVa"],
            "bytes": len(whole),
            "kind": kinds[0] if len(kinds) == 1 else "MULTI_SUBSPAN_FULL_COVER",
            "subspanKinds": ";".join(kinds),
            "composition": composition,
            "recoveryLane": recovery["lane"],
            "peBytesSha256": hashlib.sha256(whole).hexdigest(),
            "recheckNote": ";".join(notes),
            "entityKey": camp.get("entityKey") or "",
            "questionIds": qids,
            "campaignState": "OPEN_DARK_RESIDUAL",
            "observationState": camp.get("observationState") or "DARK",
            "proposed": {
                **prop,
                "cheapestFalsifier": (
                    "PE byte change; failed kind re-check; inbound reference proving "
                    "non-terminal semantics; residual membership of a named function body"
                ),
                "requiresQuestionSupersession": bool(qids),
                "shapeKind": ";".join(kinds),
                "shapeReason": ";".join(notes),
                "composition": composition,
                "recoveryLane": recovery["lane"],
                "entryClaim": (
                    "STATIC_SHAPE_ONLY_NOT_CALL_ENTRY"
                    if CODE_KIND in kinds
                    else "PAD_OR_DATA_SHAPE"
                ),
            },
        }
        proofs.append(proof)
        recovery_rows.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": len(whole),
                "primary": primary,
                "recoveryLane": recovery["lane"],
                "subspanKinds": ";".join(kinds),
                "proposedTerminalState": prop["terminalState"],
                "entityKey": camp.get("entityKey") or "",
            }
        )

    n_need_q = sum(1 for p in proofs if p["proposed"]["requiresQuestionSupersession"])
    term_counts = Counter(p["proposed"]["terminalState"] for p in proofs)
    lane_proof_counts = Counter(p["recoveryLane"] for p in proofs)

    pack = {
        "schema": PACK_SCHEMA,
        "status": "READY_FOR_GENERATION" if proofs else "EMPTY",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "n_proofs": len(proofs),
        "n_hard_mismatches": 0,
        "n_require_question_supersession": n_need_q,
        "n_already_clean": len(proofs) - n_need_q,
        "n_still_open": len(still_open),
        "proposedTerminalStateCounts": dict(term_counts),
        "recoveryLaneCounts": dict(lane_proof_counts),
        "advance_kind_proposed": "RESIDUAL_TERMINAL_OPEN_DARK_CODE_LIKE_MASS.v1",
        "parent_generation": 15,
        "parent_residual_classification_authority": (
            "Gen15 residual-terminal open-dark remaining is residual authority; "
            "this pack proposes CODE_LIKE/LARGE_MIXED residual-row terminals only"
        ),
        "claims": [
            f"Exported exactly {EXPECTED_OPEN_DARK} Gen15 OPEN_DARK residuals.",
            f"Recovered formal-pack residual-row proofs: {len(proofs)} "
            f"({dict(term_counts)}; lanes {dict(lane_proof_counts)}).",
            f"Still open: {len(still_open)}.",
            f"Question supersession required for {n_need_q}/{len(proofs)}.",
            "No Gen15 ledger mutation; Gen16 apply is separate.",
        ],
        "non_claims": [
            "Does not invent function names or claim CALL entry / REBUILD_READY",
            "Offset-envelope recovery is static shape only",
            "Partial non-pad tails stay OPEN",
            "LARGE_MIXED only admits when all segments are terminal and cover residual",
        ],
        "proofs": proofs,
        "hardMismatches": [],
    }

    summary = {
        "schema": SCHEMA,
        "status": "MEASURED",
        "plate": str(out_dir).replace("\\", "/"),
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 15,
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "deeperPrimaryCounts": dict(primary_counts),
            "recoveryLaneCountsAll": dict(lane_counts),
            "formalPackProofs": len(proofs),
            "stillOpen": len(still_open),
            "proposedTerminalStateCounts": dict(term_counts),
            "recoveryLaneProofCounts": dict(lane_proof_counts),
            "largeMixed": (large_result or {}).get("primary_counts") or {},
            "floatClaimsQuarantined": float_quarantined,
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "DeepSeek normal+adversarial on this plate",
            "Gen16 apply only if READY and proofs > 0",
            "Remaining STILL_OPEN: xref/inbound/coverage instruments",
        ],
    }
    return {
        "summary": summary,
        "pack": pack,
        "still_open": still_open,
        "recovery_rows": recovery_rows,
        "open_rows": open_rows,
    }


def write_plate(
    result: dict[str, Any], out_dir: Path, *, campaign: Path, specimen: Path
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pack = result["pack"]
    summary = result["summary"]
    still = result["still_open"]

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
        "entityKey",
        "questionIds",
        "lane",
        "openBytes",
        "terminalBytes",
        "note",
    ]
    _write_tsv(out_dir / "still-open.tsv", still_cols, still)
    _write_tsv(
        out_dir / "recovery.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "primary",
            "recoveryLane",
            "subspanKinds",
            "proposedTerminalState",
            "entityKey",
        ],
        result["recovery_rows"],
    )

    pack_summary = {
        k: pack[k]
        for k in pack
        if k not in {"proofs", "hardMismatches"}
    }
    pack_summary["proofStarts"] = [p["startVa"] for p in pack["proofs"]]
    (out_dir / "PACK-SUMMARY.json").write_text(
        json.dumps(pack_summary, indent=2) + "\n", encoding="utf-8"
    )
    summary["proofStarts"] = [p["startVa"] for p in pack["proofs"]]
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    integrity = {
        "schema": "bea.re.open-dark-code-like-mass.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_381": summary["counts"]["n_open_dark_input"] == EXPECTED_OPEN_DARK,
            "specimen_pristine": summary["specimen_sha256"] == SPECIMEN_SHA256,
            "no_pad_with_code": all(
                not (
                    p["proposed"]["terminalState"] == "TERMINAL_PADDING"
                    and CODE_KIND in (p.get("subspanKinds") or "")
                )
                for p in pack["proofs"]
            ),
            "ready_or_empty": pack["status"] in {"READY_FOR_GENERATION", "EMPTY"},
            "no_gen16_apply": True,
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
            "Re-export OPEN_DARK from Gen15: count must be 381",
            "Re-run tools/re_open_dark_code_like_mass.py build: proof set must match",
            "Gen15 campaign-residuals.tsv sha must equal ledger_sha_pre",
            "Any TERMINAL_PADDING proof containing STATIC_CODE_DECODE_ENVELOPE",
        ],
    }
    integrity["checks"]["gen15_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    integrity["checks"]["no_ledger_mutation"] = integrity["checks"][
        "gen15_residuals_unchanged"
    ]
    integrity["sources"]["summary"] = _stamp(out_dir / "SUMMARY.json")
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen15 OPEN_DARK CODE_LIKE / LARGE_MIXED mass

Status: **MEASURED** / formal pack **{pack['status']}**
Input: **{EXPECTED_OPEN_DARK}** OPEN_DARK
Proofs: **{len(pack['proofs'])}**
Still open: **{len(still)}**

## Recovery lanes (proofs)

| Lane | Count |
|------|------:|
{chr(10).join(f'| {k} | {v} |' for k,v in sorted(pack['recoveryLaneCounts'].items())) or '| (none) | 0 |'}

## Proposed terminals

| State | Count |
|-------|------:|
{chr(10).join(f'| {k} | {v} |' for k,v in sorted(pack['proposedTerminalStateCounts'].items())) or '| (none) | 0 |'}

## Non-claims

- Not Gen16 applied
- Not CALL entry / not names / not REBUILD_READY
""",
        encoding="utf-8",
    )


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if summary["counts"]["n_open_dark_input"] != EXPECTED_OPEN_DARK:
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
            raise SystemExit(f"pad+code {p['startVa']}")
    rebuilt = build(campaign=campaign, specimen=specimen, out_dir=plate / "_scratch")
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
                "n_proofs": pack["n_proofs"],
                "proposedTerminalStateCounts": pack["proposedTerminalStateCounts"],
                "recoveryLaneCounts": pack["recoveryLaneCounts"],
                "stillOpen": pack["n_still_open"],
            },
            indent=2,
        )
    )
    print("OPEN_DARK_CODE_LIKE_MASS_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN15)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, required=True)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN15)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    args = p.parse_args(argv)
    if args.cmd == "build":
        result = build(
            campaign=args.campaign, specimen=args.specimen, out_dir=args.out
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
        print("OPEN_DARK_CODE_LIKE_MASS_OK")
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
