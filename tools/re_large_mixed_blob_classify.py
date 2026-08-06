#!/usr/bin/env python3
"""Segment and classify LARGE_MIXED_BLOB residual subspans (JPEG/math frontier).

Consumes either:
  - deeper-plate full.json rows, extracting LARGE_MIXED_BLOB subspans, or
  - an explicit TSV of startVa/endVa spans.

Emits sub-segments with conservative kinds. Pure data tables may be shape-terminal;
code fragments stay OPEN (no invented function names / entry claims).

Does not mutate Gen10.
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
TEXT_HI = 0x5D8000


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


def fmt_va(va: int) -> str:
    return f"0x{va:08x}"


def try_capstone():
    try:
        import capstone  # type: ignore

        return capstone
    except Exception:
        return None


def code_ptr_run(blob: bytes, min_dwords: int = 4) -> int:
    usable = len(blob) - (len(blob) % 4)
    run = 0
    for i in range(0, usable, 4):
        v = struct.unpack_from("<I", blob, i)[0]
        if TEXT_LO <= v < TEXT_HI:
            run += 1
        else:
            break
    return run * 4 if run >= min_dwords else 0


def pad_run(blob: bytes) -> int:
    n = 0
    for b in blob:
        if b in (0x00, 0x90, 0xCC):
            n += 1
        else:
            break
    return n if n >= 4 else 0


def float32_lut_run(blob: bytes, min_run: int = 8) -> int:
    usable = len(blob) - (len(blob) % 4)
    run = 0
    for i in range(0, usable, 4):
        bits = struct.unpack_from("<I", blob, i)[0]
        if bits == 0:
            if run == 0:
                return 0
            break
        exp = (bits >> 23) & 0xFF
        if exp == 0 or exp == 0xFF:
            break
        if TEXT_LO <= bits < TEXT_HI:
            break
        f = struct.unpack_from("<f", blob, i)[0]
        af = abs(f)
        if af < 1e-6 or af > 1e6:
            break
        run += 1
    return run * 4 if run >= min_run else 0


def int16_quant_like_run(blob: bytes) -> int:
    """JPEG-ish: ≥64 consecutive int16 with abs values mostly in 1..255."""
    if len(blob) < 128:
        return 0
    # scan aligned int16 runs of at least 64 entries
    best = 0
    for align in (0, 1):
        if len(blob) < align + 128:
            continue
        i = align
        run = 0
        while i + 2 <= len(blob):
            v = struct.unpack_from("<h", blob, i)[0]
            if 0 <= abs(v) <= 255:
                run += 1
                i += 2
            else:
                if run >= 64:
                    best = max(best, run * 2)
                run = 0
                i += 2
        if run >= 64:
            best = max(best, run * 2)
    return best if best >= 128 else 0


def sse_const_pool_run(blob: bytes) -> int:
    """16-byte aligned repeating masks / small-int XMM constants."""
    if len(blob) < 32:
        return 0
    # prefer 16-byte chunks with low unique-byte diversity or known shuffle patterns
    run = 0
    for i in range(0, len(blob) - 15, 16):
        chunk = blob[i : i + 16]
        uniq = len(set(chunk))
        # shuffle masks often 0..15 permutation; broadcast constants few unique bytes
        if uniq <= 8 or (uniq <= 16 and max(chunk) <= 15 and min(chunk) >= 0):
            # reject pure pad
            if all(b in (0, 0x90, 0xCC) for b in chunk):
                break
            run += 16
        else:
            break
    return run if run >= 32 else 0


def code_fragment_run(blob: bytes, cs_mod, max_bytes: int = 4096) -> tuple[int, int, bool]:
    """Longest leading capstone decode; return (bytes, insn_count, ends_ct)."""
    if not blob or cs_mod is None:
        return 0, 0, False
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
    limit = min(len(blob), max_bytes)
    # Typical x86 function/thunk starts (conservative; not a name claim).
    ok_start = blob[0] in {
        0x55,
        0x53,
        0x56,
        0x57,
        0x51,
        0x52,
        0x50,
        0x8B,
        0x89,
        0x83,
        0x81,
        0x0F,
        0xDB,
        0xD9,
        0xDD,
        0x9C,
        0x60,
        0x33,
        0x31,
        0x85,
        0x3B,
        0x68,
        0x6A,
        0xB8,
        0xE8,
        0xE9,
        0xEB,
        0x8D,
        0x64,
        0xF2,
        0xF3,
        0x66,
        0xC6,
        0xC7,
        0xA1,
        0xA3,
        0xFF,
        0x8B,
    }
    while offset < limit and count < 512:
        # Stop at zero-run data islands (not NOP — NOPs are normal in code).
        if offset + 8 <= limit and all(blob[offset + k] == 0x00 for k in range(8)):
            break
        if offset + 4 <= limit and all(blob[offset + k] == 0xCC for k in range(4)):
            break
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
            pad = 0
            while offset + pad < limit and blob[offset + pad] in (0x90, 0xCC) and pad < 16:
                pad += 1
            offset += pad
            # Always require a plausible code start byte — random tables
            # contain incidental 0xC3 (ret) after garbage "instructions".
            if ok_start and count >= 4:
                return offset, count, True
            return 0, 0, False
    # Accept jmp-ended fragment only with plausible start and length
    if last_ct and ok_start and count >= 6 and offset >= 16:
        return offset, count, True
    return 0, 0, False


def segment_blob(start_va: int, blob: bytes, cs_mod) -> list[dict]:
    """Greedy left-to-right segmentation of one LARGE_MIXED span."""
    segs: list[dict] = []
    pos = 0
    n = len(blob)
    while pos < n:
        rest = blob[pos:]
        va = start_va + pos

        # 1) pad
        pr = pad_run(rest)
        if pr:
            segs.append(_seg(va, pr, "ALIGN_PAD", True, f"pad={pr}"))
            pos += pr
            continue

        # 2) code pointer table
        cpr = code_ptr_run(rest, min_dwords=4)
        if cpr:
            segs.append(
                _seg(
                    va,
                    cpr,
                    "CODE_ADDRESS_TABLE",
                    True,
                    f"code_ptrs={cpr // 4}",
                )
            )
            pos += cpr
            continue

        # 3) float LUT
        fr = float32_lut_run(rest, min_run=8)
        if fr:
            segs.append(_seg(va, fr, "FLOAT32_LUT", True, f"floats={fr // 4}"))
            pos += fr
            continue

        # 4) SSE/const pool
        sr = sse_const_pool_run(rest)
        if sr:
            segs.append(_seg(va, sr, "SSE_OR_CONST_POOL", True, f"bytes={sr}"))
            pos += sr
            continue

        # 5) int16 quant-like
        qr = int16_quant_like_run(rest)
        if qr >= 128 and qr <= len(rest):
            # only if leading portion matches; measure actual leading run
            lead = 0
            for i in range(0, len(rest) - 1, 2):
                v = struct.unpack_from("<h", rest, i)[0]
                if 0 <= abs(v) <= 255:
                    lead += 2
                else:
                    break
            if lead >= 128:
                segs.append(
                    _seg(va, lead, "INT16_QUANT_LIKE", True, f"int16s={lead // 2}")
                )
                pos += lead
                continue

        # 6) code fragment
        cr, ic, ends = code_fragment_run(rest, cs_mod)
        if cr >= 16:
            segs.append(
                _seg(
                    va,
                    cr,
                    "OPEN_CODE_FRAGMENT",
                    False,  # never terminal-close as named function
                    f"insns={ic} ends_ct={int(ends)}",
                )
            )
            pos += cr
            continue

        # 7) unknown byte — advance to next 4-byte boundary pattern or +1
        # consume until next recognizable pattern (cap 64B unknown island)
        advance = 1
        for step in range(4, min(65, len(rest) + 1), 4):
            trial = rest[step:]
            if (
                pad_run(trial)
                or code_ptr_run(trial, 4)
                or float32_lut_run(trial, 8)
                or (code_fragment_run(trial, cs_mod)[0] >= 16)
            ):
                advance = step
                break
        else:
            advance = min(64, len(rest)) if len(rest) >= 64 else len(rest)
        segs.append(
            _seg(va, advance, "UNRESOLVED_BYTES", False, f"island={advance}")
        )
        pos += advance

    return segs


def _seg(va: int, nbytes: int, kind: str, terminal: bool, reason: str) -> dict:
    return {
        "startVa": fmt_va(va),
        "endVa": fmt_va(va + nbytes),
        "bytes": nbytes,
        "kind": kind,
        "terminal": terminal,
        "reason": reason,
    }


def load_large_mixed_from_deeper(full_json: Path) -> list[dict]:
    data = json.loads(full_json.read_text(encoding="utf-8"))
    rows = data.get("rows") or []
    out = []
    for r in rows:
        for s in r.get("subspans") or []:
            if s.get("kind") == "LARGE_MIXED_BLOB" and int(s.get("bytes") or 0) >= 256:
                out.append(
                    {
                        "startVa": s["startVa"],
                        "endVa": s["endVa"],
                        "bytes": int(s["bytes"]),
                        "prevFunc": r.get("prevFunc", ""),
                        "nextFunc": r.get("nextFunc", ""),
                        "parentStart": r.get("startVa", ""),
                        "parentEnd": r.get("endVa", ""),
                    }
                )
    # de-dupe by startVa
    seen = set()
    uniq = []
    for x in out:
        if x["startVa"] in seen:
            continue
        seen.add(x["startVa"])
        uniq.append(x)
    return uniq


def classify_large_mixed(specimen: Path, spans: list[dict]) -> dict:
    raw = specimen.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen sha256 mismatch: {sha}")
    image_base, sections = pe_map(raw)
    cs_mod = try_capstone()
    results = []
    for sp in spans:
        start = int(sp["startVa"], 16)
        end = int(sp["endVa"], 16)
        o0 = va_to_off(start, image_base, sections)
        o1 = va_to_off(end, image_base, sections)
        if o0 is None or o1 is None or o1 < o0:
            results.append(
                {
                    **sp,
                    "primary": "UNMAPPED",
                    "terminalBytes": 0,
                    "openBytes": end - start,
                    "segments": [],
                }
            )
            continue
        blob = raw[o0:o1]
        segs = segment_blob(start, blob, cs_mod)
        term_b = sum(s["bytes"] for s in segs if s.get("terminal"))
        open_b = sum(s["bytes"] for s in segs if not s.get("terminal"))
        kind_c = Counter(s["kind"] for s in segs)
        primary = "FULLY_DATA_TERMINAL" if open_b == 0 and term_b > 0 else (
            "PARTIAL_DATA_TERMINAL" if term_b > 0 else "STILL_OPEN_MIXED"
        )
        if open_b > 0 and any(s["kind"] == "OPEN_CODE_FRAGMENT" for s in segs):
            if term_b > 0:
                primary = "CODE_AND_DATA_MIXED"
            else:
                primary = "OPEN_CODE_DOMINATED"
        results.append(
            {
                "startVa": fmt_va(start),
                "endVa": fmt_va(end),
                "bytes": len(blob),
                "prevFunc": sp.get("prevFunc", ""),
                "nextFunc": sp.get("nextFunc", ""),
                "parentStart": sp.get("parentStart", ""),
                "parentEnd": sp.get("parentEnd", ""),
                "primary": primary,
                "terminalBytes": term_b,
                "openBytes": open_b,
                "segmentKinds": dict(kind_c),
                "segments": segs,
            }
        )

    seg_counts: Counter = Counter()
    term_seg = 0
    for r in results:
        for s in r.get("segments") or []:
            seg_counts[s["kind"]] += 1
            if s.get("terminal"):
                term_seg += 1
    return {
        "schema": "bea.re.large-mixed-blob-classify.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "n_spans": len(results),
        "terminal_bytes_accounted": sum(r["terminalBytes"] for r in results),
        "open_bytes_remaining": sum(r["openBytes"] for r in results),
        "primary_counts": dict(Counter(r["primary"] for r in results)),
        "segment_kind_counts": dict(seg_counts),
        "terminal_segment_count": term_seg,
        "capstone": bool(cs_mod),
        "rows": results,
        "note": (
            "OPEN_CODE_FRAGMENT is non-terminal (no entry/name). "
            "Data table kinds are shape terminals only. Gen10 not mutated."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument(
        "--deeper-full-json",
        type=Path,
        help="deeper plate full.json to extract LARGE_MIXED_BLOB subspans",
    )
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--summary-only", action="store_true")
    p.add_argument("--min-bytes", type=int, default=256)
    args = p.parse_args(argv)
    if not args.deeper_full_json:
        raise SystemExit("--deeper-full-json required")
    spans = load_large_mixed_from_deeper(args.deeper_full_json)
    spans = [s for s in spans if s["bytes"] >= args.min_bytes]
    result = classify_large_mixed(args.specimen, spans)
    summary = {k: v for k, v in result.items() if k != "rows"}
    print(json.dumps(summary, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = summary if args.summary_only else result
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("LARGE_MIXED_BLOB_CLASSIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
