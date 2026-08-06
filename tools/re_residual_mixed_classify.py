#!/usr/bin/env python3
"""Classify Gen10 MIXED_OR_CODE_LIKE residual spans from a pristine PE.

Terminal grades (conservative shape terminals only):
  - MOSTLY_ALIGN_PADDING: high pad fraction, small span
  - POINTER_TABLE_LIKE: aligned image-pointer dwords
  - ASCII_LIKE: high printable density
  - STATIC_CODE_DECODE_ENVELOPE: capstone covers most of span ending in
    control-transfer (ret/jmp/jcc/call) — shape terminal, not entry proof

Non-terminal:
  - EXECUTED_CODE_SPAN_OPEN_BOUNDARY: observationState=EXECUTED but campaign
    keeps OPEN_CODE_BOUNDARY (execution ≠ contract/boundary terminal)
  - CODE_LIKE_OPEN / UNRESOLVED_MIXED

Does not invent function names or mutate campaign ledgers.
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


def read_residual_rows(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_i = next(i for i, line in enumerate(lines) if line and not line.startswith("#"))
    cols = lines[header_i].split("\t")
    rows: list[dict[str, str]] = []
    for line in lines[header_i + 1 :]:
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        rows.append({cols[j]: parts[j] if j < len(parts) else "" for j in range(len(cols))})
    return rows


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


def try_capstone():
    try:
        import capstone  # type: ignore

        return capstone
    except Exception:
        return None


def decode_x86_length(blob: bytes, cs_mod) -> tuple[int, int, bool]:
    if not blob or cs_mod is None:
        return 0, 0, False
    md = cs_mod.Cs(cs_mod.CS_ARCH_X86, cs_mod.CS_MODE_32)
    offset = 0
    count = 0
    last_is_ct = False
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
    while offset < len(blob):
        if blob[offset] in (0x90, 0xCC) and count == 0:
            offset += 1
            continue
        insns = list(md.disasm(blob[offset : offset + 16], 0))
        if not insns:
            break
        insn = insns[0]
        if insn.size <= 0:
            break
        offset += insn.size
        count += 1
        last_is_ct = insn.mnemonic in control
        if insn.mnemonic in ("ret", "retn"):
            rest = blob[offset:]
            if all(b in (0x90, 0xCC, 0x00) for b in rest):
                return offset + len(rest), count, True
            return offset, count, True
        if count > 512:
            break
    return offset, count, last_is_ct


def classify_blob(blob: bytes, observation_state: str, image_base: int, image_end: int, cs_mod) -> dict:
    n = len(blob)
    if n == 0:
        return {"kind": "EMPTY", "terminal": False, "reason": "empty_span"}

    nop = sum(1 for b in blob if b == 0x90)
    cc = sum(1 for b in blob if b == 0xCC)
    zero = sum(1 for b in blob if b == 0x00)
    pad_frac = (nop + cc + zero) / n
    print_frac = sum(1 for b in blob if 32 <= b < 127) / n
    dwords = max(1, n // 4)
    ptrs = 0
    for i in range(0, n - 3, 4):
        val = struct.unpack_from("<I", blob, i)[0]
        if image_base <= val < image_end:
            ptrs += 1
    ptr_frac = ptrs / dwords
    decoded_len, insn_count, ends_ct = decode_x86_length(blob, cs_mod)
    decode_frac = decoded_len / n

    base = {
        "pad_frac": round(pad_frac, 4),
        "ptr_frac": round(ptr_frac, 4),
        "print_frac": round(print_frac, 4),
        "decode_frac": round(decode_frac, 4),
        "insn_count": insn_count,
        "ends_control_transfer": ends_ct,
    }

    if observation_state == "EXECUTED":
        # Campaign intentionally keeps these OPEN_CODE_BOUNDARY: bytes ran, but
        # entry/contract is not proved. Do not promote to terminal here.
        return {
            "kind": "EXECUTED_CODE_SPAN_OPEN_BOUNDARY",
            "terminal": False,
            "reason": "observationState=EXECUTED_but_open_code_boundary",
            **base,
        }
    if pad_frac >= 0.85 and n <= 64:
        return {
            "kind": "MOSTLY_ALIGN_PADDING",
            "terminal": True,
            "reason": f"pad_frac={pad_frac:.3f}",
            **base,
        }
    if n >= 8 and n % 4 == 0 and ptr_frac >= 0.75 and decode_frac < 0.25:
        return {
            "kind": "POINTER_TABLE_LIKE",
            "terminal": True,
            "reason": f"ptr_frac={ptr_frac:.3f}",
            **base,
        }
    # Pure prefix of .text code pointers (switch/jump tables after functions).
    if n >= 16:
        usable = n - (n % 4)
        text_lo, text_hi = 0x401000, 0x5D8000
        run = 0
        for i in range(0, usable, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if text_lo <= v < text_hi:
                run += 1
            else:
                break
        if run >= 8 and (run * 4) >= max(16, int(0.9 * usable)) and decode_frac < 0.2:
            return {
                "kind": "CODE_ADDRESS_TABLE",
                "terminal": True,
                "reason": f"prefix_code_ptrs={run} dwords",
                **base,
            }
    if n >= 8 and print_frac >= 0.85 and ptr_frac < 0.2 and decode_frac < 0.3:
        return {
            "kind": "ASCII_LIKE",
            "terminal": True,
            "reason": f"print_frac={print_frac:.3f}",
            **base,
        }
    if (
        cs_mod is not None
        and insn_count >= 2
        and decode_frac >= 0.90
        and ends_ct
        and pad_frac < 0.5
    ):
        return {
            "kind": "STATIC_CODE_DECODE_ENVELOPE",
            "terminal": True,
            "reason": f"insns={insn_count} decode_frac={decode_frac:.3f} ends_ct",
            **base,
        }
    if cs_mod is not None and insn_count >= 3 and decode_frac >= 0.6:
        return {
            "kind": "CODE_LIKE_OPEN",
            "terminal": False,
            "reason": f"partial/full decode without terminal envelope insns={insn_count}",
            **base,
        }
    return {
        "kind": "UNRESOLVED_MIXED",
        "terminal": False,
        "reason": "no terminal static pattern",
        **base,
    }


def classify_mixed(specimen: Path, residuals_tsv: Path) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen sha256 mismatch: {sha}")
    image_base, sections = pe_map(data)
    image_end = image_base + max(sva + max(vs, rs) for sva, vs, _rp, rs in sections)
    cs_mod = try_capstone()
    rows = [
        r
        for r in read_residual_rows(residuals_tsv)
        if r.get("bytePattern") == "MIXED_OR_CODE_LIKE_BYTES"
    ]
    results = []
    for r in rows:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        o0 = va_to_off(start, image_base, sections)
        o1 = va_to_off(end, image_base, sections)
        if o0 is None or o1 is None or o1 < o0:
            grade = {"kind": "UNMAPPED", "terminal": False, "reason": "va_unmapped"}
            blob = b""
        else:
            blob = data[o0:o1]
            grade = classify_blob(blob, r["observationState"], image_base, image_end, cs_mod)
        results.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": r["bytes"],
                "observationState": r["observationState"],
                "prevFunc": r.get("prevFunc", ""),
                "nextFunc": r.get("nextFunc", ""),
                "questionIds": r.get("questionIds", ""),
                **grade,
            }
        )
    counts = Counter(x["kind"] for x in results)
    terminal = sum(1 for x in results if x.get("terminal"))
    return {
        "schema": "bea.re.residual-mixed-static.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "n_total": len(results),
        "n_terminal": terminal,
        "n_open": len(results) - terminal,
        "counts": dict(counts),
        "capstone": bool(cs_mod),
        "rows": results,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--residuals-tsv", type=Path, required=True)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)
    result = classify_mixed(args.specimen, args.residuals_tsv)
    summary = {k: v for k, v in result.items() if k != "rows"}
    print(json.dumps(summary, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("RESIDUAL_MIXED_CLASSIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
