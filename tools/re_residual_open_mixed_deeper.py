#!/usr/bin/env python3
"""Deeper static analysis of still-open MIXED residuals (post base classifier).

Takes the 720 DARK open rows (CODE_LIKE_OPEN + UNRESOLVED_MIXED) and applies
finer, conservative structure detectors. Can mark *subspans* terminal without
claiming the whole residual row is closed.

Terminal subspan kinds (shape only):
  - CODE_ADDRESS_TABLE_PREFIX: run of .text code pointers (≥8 dwords)
  - FLOAT32_TABLE: aligned IEEE-754 float runs (finite, non-trivial density)
  - TINY_PAD_GAP: 1–8 B of only NOP/INT3/00 between neighbors
  - ZERO_RUN_PREFIX / ALIGN_PAD_PREFIX: leading pad only (subspan)

Non-terminal refinements:
  - LARGE_MIXED_BLOB: size≥256 with reported substructure
  - CODE_LIKE_PARTIAL: decode without envelope (kept open)
  - INDEX_OR_BYTE_TABLE: dense low-byte / small-int dwords
  - UNRESOLVED_TAIL: remainder after a terminal prefix

Does not invent function names. Does not mutate Gen10.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
TEXT_LO = 0x401000
TEXT_HI = 0x5D8000  # BEA .text-ish upper (image-relative preferred base)


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
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        sections.append((va, vsize, rawptr, rawsize))
    return image_base, sections


def va_to_off(va: int, image_base: int, sections) -> int | None:
    rva = va - image_base
    for sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            return rawptr + (rva - sva)
    return None


def code_ptr_run_bytes(blob: bytes) -> int:
    """Length in bytes of leading aligned dwords that are .text code pointers."""
    usable = len(blob) - (len(blob) % 4)
    run = 0
    for i in range(0, usable, 4):
        v = struct.unpack_from("<I", blob, i)[0]
        if TEXT_LO <= v < TEXT_HI:
            run += 1
        else:
            break
    return run * 4


def float32_run_bytes(blob: bytes, min_run: int = 8) -> int:
    """Leading aligned *plausible* float32 LUT run length (bytes), 0 if short.

    Rejects denormals, NaN/Inf, code pointers, and extreme magnitudes so that
    packed index/junk (e.g. 00 01 02 03 …) is not mistaken for a float table.
    """
    usable = len(blob) - (len(blob) % 4)
    run = 0
    for i in range(0, usable, 4):
        bits = struct.unpack_from("<I", blob, i)[0]
        if bits == 0:
            if run == 0:
                return 0
            break
        exp = (bits >> 23) & 0xFF
        if exp == 0 or exp == 0xFF:  # zero/denormal or nan/inf
            break
        if TEXT_LO <= bits < TEXT_HI:
            break
        f = struct.unpack_from("<f", blob, i)[0]
        af = abs(f)
        if af < 1e-6 or af > 1e6:
            break
        run += 1
    if run >= min_run:
        return run * 4
    return 0


def pad_prefix_bytes(blob: bytes) -> int:
    n = 0
    for b in blob:
        if b in (0x00, 0x90, 0xCC):
            n += 1
        else:
            break
    return n


def is_tiny_pad_gap(blob: bytes) -> bool:
    return 1 <= len(blob) <= 8 and all(b in (0x00, 0x90, 0xCC) for b in blob)


def low_byte_table_score(blob: bytes) -> float:
    """Fraction of dwords with high 3 bytes zero (index-like)."""
    usable = len(blob) - (len(blob) % 4)
    if usable < 16:
        return 0.0
    hits = 0
    dwords = usable // 4
    for i in range(0, usable, 4):
        v = struct.unpack_from("<I", blob, i)[0]
        if v <= 0xFFFF:
            hits += 1
    return hits / dwords


def try_capstone():
    try:
        import capstone  # type: ignore

        return capstone
    except Exception:
        return None


def decode_frac(blob: bytes, cs_mod) -> tuple[float, int, bool]:
    if not blob or cs_mod is None:
        return 0.0, 0, False
    md = cs_mod.Cs(cs_mod.CS_ARCH_X86, cs_mod.CS_MODE_32)
    offset = 0
    count = 0
    last_ct = False
    control = {
        "ret",
        "retn",
        "jmp",
        "je",
        "jne",
        "jz",
        "jnz",
        "ja",
        "jb",
        "jae",
        "jbe",
        "jg",
        "jl",
        "jge",
        "jle",
        "call",
        "int3",
    }
    while offset < len(blob) and count < 256:
        insns = list(md.disasm(blob[offset : offset + 16], 0))
        if not insns:
            break
        insn = insns[0]
        if insn.size <= 0:
            break
        offset += insn.size
        count += 1
        last_ct = insn.mnemonic in control
        if insn.mnemonic in ("ret", "retn"):
            break
    return (offset / len(blob) if blob else 0.0), count, last_ct


def analyze_span(
    start_va: int,
    blob: bytes,
    base_kind: str,
    prev_func: str,
    next_func: str,
    cs_mod,
) -> dict:
    n = len(blob)
    subspans: list[dict] = []
    terminal_bytes = 0

    if is_tiny_pad_gap(blob):
        subspans.append(
            {
                "startVa": fmt_va(start_va),
                "endVa": fmt_va(start_va + n),
                "bytes": n,
                "kind": "TINY_PAD_GAP",
                "terminal": True,
                "reason": "1-8B only 00/90/CC between neighbors",
            }
        )
        terminal_bytes = n
        return _pack(
            start_va,
            n,
            base_kind,
            prev_func,
            next_func,
            subspans,
            terminal_bytes,
            "TINY_PAD_GAP",
        )

    # Leading pad prefix (subspan only)
    pad_n = pad_prefix_bytes(blob)
    if pad_n >= 4 and pad_n < n:
        subspans.append(
            {
                "startVa": fmt_va(start_va),
                "endVa": fmt_va(start_va + pad_n),
                "bytes": pad_n,
                "kind": "ALIGN_PAD_PREFIX",
                "terminal": True,
                "reason": f"leading_pad={pad_n}",
            }
        )
        terminal_bytes += pad_n
        rest_off = pad_n
    else:
        rest_off = 0

    rest = blob[rest_off:]
    rest_va = start_va + rest_off

    # Code address table prefix on remainder
    cptr = code_ptr_run_bytes(rest)
    if cptr >= 32:  # ≥8 dwords
        subspans.append(
            {
                "startVa": fmt_va(rest_va),
                "endVa": fmt_va(rest_va + cptr),
                "bytes": cptr,
                "kind": "CODE_ADDRESS_TABLE_PREFIX",
                "terminal": True,
                "reason": f"code_ptrs={cptr // 4} dwords into .text",
            }
        )
        terminal_bytes += cptr
        rest_off2 = rest_off + cptr
        rest2 = blob[rest_off2:]
        rest_va2 = start_va + rest_off2
    else:
        rest_off2 = rest_off
        rest2 = rest
        rest_va2 = rest_va

    # Float table on remaining
    frun = float32_run_bytes(rest2, min_run=8)
    if frun >= 32:
        subspans.append(
            {
                "startVa": fmt_va(rest_va2),
                "endVa": fmt_va(rest_va2 + frun),
                "bytes": frun,
                "kind": "FLOAT32_TABLE_PREFIX",
                "terminal": True,
                "reason": f"float32_run={frun // 4}",
            }
        )
        terminal_bytes += frun
        rest_off3 = rest_off2 + frun
        rest3 = blob[rest_off3:]
        rest_va3 = start_va + rest_off3
    else:
        rest_off3 = rest_off2
        rest3 = rest2
        rest_va3 = rest_va2

    # Index/byte table signal on remaining (non-terminal unless very pure)
    idx = low_byte_table_score(rest3) if len(rest3) >= 16 else 0.0
    if idx >= 0.85 and len(rest3) >= 16:
        subspans.append(
            {
                "startVa": fmt_va(rest_va3),
                "endVa": fmt_va(rest_va3 + len(rest3)),
                "bytes": len(rest3),
                "kind": "INDEX_OR_BYTE_TABLE",
                "terminal": True,
                "reason": f"low_dword_frac={idx:.3f}",
            }
        )
        terminal_bytes += len(rest3)
        rest3 = b""
        rest_va3 = start_va + n

    # Code-like remainder
    if rest3:
        df, ic, ends_ct = decode_frac(rest3, cs_mod)
        if (
            cs_mod is not None
            and ic >= 2
            and df >= 0.90
            and ends_ct
            and len(rest3) >= 8
        ):
            # Only promote full remainder as code envelope when it is not a
            # short junk tail after a data prefix (avoid false whole-span close).
            if rest_off3 == 0 or len(rest3) >= 16:
                subspans.append(
                    {
                        "startVa": fmt_va(rest_va3),
                        "endVa": fmt_va(rest_va3 + len(rest3)),
                        "bytes": len(rest3),
                        "kind": "STATIC_CODE_DECODE_ENVELOPE",
                        "terminal": True,
                        "reason": f"insns={ic} decode_frac={df:.3f}",
                    }
                )
                terminal_bytes += len(rest3)
                rest3 = b""
            else:
                subspans.append(
                    {
                        "startVa": fmt_va(rest_va3),
                        "endVa": fmt_va(rest_va3 + len(rest3)),
                        "bytes": len(rest3),
                        "kind": "UNRESOLVED_TAIL",
                        "terminal": False,
                        "reason": f"short_tail_after_prefix decode_frac={df:.3f}",
                    }
                )
        elif len(rest3) > 0:
            kind_tail = (
                "CODE_LIKE_PARTIAL"
                if df >= 0.5 and ic >= 2
                else ("LARGE_MIXED_BLOB" if len(rest3) >= 256 else "UNRESOLVED_TAIL")
            )
            subspans.append(
                {
                    "startVa": fmt_va(rest_va3),
                    "endVa": fmt_va(rest_va3 + len(rest3)),
                    "bytes": len(rest3),
                    "kind": kind_tail,
                    "terminal": False,
                    "reason": f"decode_frac={df:.3f} insns={ic} idx={idx:.3f}",
                }
            )

    primary = "STILL_OPEN"
    if terminal_bytes >= n and n > 0:
        primary = "FULLY_SUBSPAN_TERMINAL"
    elif terminal_bytes > 0:
        primary = "PARTIAL_SUBSPAN_TERMINAL"
    elif any(s["kind"] == "LARGE_MIXED_BLOB" for s in subspans):
        primary = "LARGE_MIXED_BLOB"
    elif any(s["kind"] == "CODE_LIKE_PARTIAL" for s in subspans):
        primary = "CODE_LIKE_PARTIAL"

    return _pack(
        start_va, n, base_kind, prev_func, next_func, subspans, terminal_bytes, primary
    )


def fmt_va(va: int) -> str:
    """Zero-padded 32-bit hex VA for stable joins with campaign TSVs."""
    return f"0x{va:08x}"


def _pack(
    start_va, n, base_kind, prev_func, next_func, subspans, terminal_bytes, primary
):
    return {
        "startVa": fmt_va(start_va),
        "endVa": fmt_va(start_va + n),
        "bytes": n,
        "baseKind": base_kind,
        "prevFunc": prev_func,
        "nextFunc": next_func,
        "primary": primary,
        "terminalBytes": terminal_bytes,
        "openBytes": max(0, n - terminal_bytes),
        "wholeSpanTerminal": terminal_bytes >= n and n > 0,
        "subspans": subspans,
    }


def read_still_open_tsv(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_i = next(i for i, line in enumerate(lines) if line and not line.startswith("#"))
    cols = lines[header_i].split("\t")
    rows = []
    for line in lines[header_i + 1 :]:
        if not line.strip():
            continue
        parts = line.split("\t")
        rows.append({cols[j]: parts[j] if j < len(cols) else "" for j in range(len(cols))})
    return rows


def analyze_open_mixed(specimen: Path, still_open_tsv: Path) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen sha256 mismatch: {sha}")
    image_base, sections = pe_map(data)
    cs_mod = try_capstone()
    open_rows = read_still_open_tsv(still_open_tsv)
    results = []
    for r in open_rows:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        o0 = va_to_off(start, image_base, sections)
        o1 = va_to_off(end, image_base, sections)
        if o0 is None or o1 is None or o1 < o0:
            results.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": end - start,
                    "baseKind": r.get("kind", ""),
                    "primary": "UNMAPPED",
                    "terminalBytes": 0,
                    "openBytes": end - start,
                    "wholeSpanTerminal": False,
                    "subspans": [],
                    "prevFunc": r.get("prevFunc", ""),
                    "nextFunc": r.get("nextFunc", ""),
                }
            )
            continue
        blob = data[o0:o1]
        results.append(
            analyze_span(
                start,
                blob,
                r.get("kind", ""),
                r.get("prevFunc", ""),
                r.get("nextFunc", ""),
                cs_mod,
            )
        )

    primary_counts = Counter(x["primary"] for x in results)
    sub_counts: Counter = Counter()
    term_sub = 0
    for x in results:
        for s in x.get("subspans") or []:
            sub_counts[s["kind"]] += 1
            if s.get("terminal"):
                term_sub += 1
    whole_term = sum(1 for x in results if x.get("wholeSpanTerminal"))
    partial = sum(1 for x in results if x.get("primary") == "PARTIAL_SUBSPAN_TERMINAL")
    open_bytes_total = sum(x.get("openBytes", 0) for x in results)
    term_bytes_total = sum(x.get("terminalBytes", 0) for x in results)
    # Pin the HResult residual
    hresult_row = next(
        (x for x in results if x["startVa"].lower() == "0x005c9c69"), None
    )
    return {
        "schema": "bea.re.residual-open-mixed-deeper.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "n_open_input": len(results),
        "n_whole_span_terminal": whole_term,
        "n_partial_subspan_terminal": partial,
        "n_still_fully_open": sum(
            1
            for x in results
            if not x.get("wholeSpanTerminal") and x.get("terminalBytes", 0) == 0
        ),
        "terminal_bytes_accounted": term_bytes_total,
        "open_bytes_remaining": open_bytes_total,
        "primary_counts": dict(primary_counts),
        "subspan_kind_counts": dict(sub_counts),
        "terminal_subspan_count": term_sub,
        "capstone": bool(cs_mod),
        "hresult_post_body_residual": hresult_row,
        "rows": results,
        "note": (
            "Subspan terminals are shape/accounting only; Gen10 residual rows "
            "are not re-sliced or mutated. EXECUTED open-boundary (108) not in "
            "still-open.tsv input."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--still-open-tsv", type=Path, required=True)
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    result = analyze_open_mixed(args.specimen, args.still_open_tsv)
    summary = {k: v for k, v in result.items() if k != "rows"}
    # shrink hresult row subspans for summary print
    print(json.dumps(summary, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        if args.summary_only:
            args.json_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        else:
            args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("RESIDUAL_OPEN_MIXED_DEEPER_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
