#!/usr/bin/env python3
"""Static analysis of retail HResultToString @ 0x005be628.

Extracts:
  - relative call sites into the body
  - equality-branch HRESULT → C-string pairs (cmp/je and fallthrough)
  - confirms ret 0x4 epilogue
  - classifies the post-body residual as switch auxiliary data prefix

Does not claim runtime reachability. Gen10 ledger is not mutated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

PRISTINE = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
ENTRY = 0x005BE628
# Inclusive end of last instruction byte before residual (ret 4 ends at 0x005c9c68)
BODY_END_EXCLUSIVE = 0x005C9C69
RET4_VA = 0x005C9C66


def pe_sections(data: bytes):
    e = struct.unpack_from("<I", data, 0x3C)[0]
    opt = e + 24
    ib = struct.unpack_from("<I", data, opt + 28)[0]
    ns = struct.unpack_from("<H", data, e + 6)[0]
    so = struct.unpack_from("<H", data, e + 20)[0]
    sec = e + 24 + so
    secs = []
    for i in range(ns):
        o = sec + i * 40
        name = data[o : o + 8].split(b"\0", 1)[0].decode("ascii", "replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", data, o + 8)
        secs.append((name, va, vs, rp, rs))
    return ib, secs


def va_to_off(va: int, ib: int, secs) -> int | None:
    rva = va - ib
    for _n, sva, vs, rp, rs in secs:
        if sva <= rva < sva + max(vs, rs):
            return rp + (rva - sva)
    return None


def read_cstr(data: bytes, va: int, ib: int, secs) -> str | None:
    o = va_to_off(va, ib, secs)
    if o is None:
        return None
    s = data[o : o + 120].split(b"\0", 1)[0]
    try:
        t = s.decode("ascii")
    except Exception:
        return None
    if not t or any(ord(c) < 32 or ord(c) > 126 for c in t):
        return None
    return t


def find_calls(data: bytes, ib: int, secs, target: int) -> list[int]:
    text = next(s for s in secs if s[0] == ".text")
    _n, sva, vs, rp, rs = text
    calls = []
    limit = rp + min(rs, vs) - 5
    for i in range(rp, limit):
        b = data[i]
        if b not in (0xE8, 0xE9):
            continue
        rel = struct.unpack_from("<i", data, i + 1)[0]
        src = ib + sva + (i - rp)
        if src + 5 + rel == target:
            calls.append(src)
    return calls


def extract_pairs(data: bytes, ib: int, secs) -> dict[int, dict]:
    body = data[va_to_off(ENTRY, ib, secs) : va_to_off(BODY_END_EXCLUSIVE, ib, secs)]
    pairs: dict[int, dict] = {}

    def mov_eax_at(va: int):
        off = va - ENTRY
        if off < 0 or off + 5 > len(body):
            return None
        if body[off] != 0xB8:
            return None
        return struct.unpack_from("<I", body, off + 1)[0]

    i = 0
    while i < len(body) - 12:
        if body[i] == 0x3D:
            imm = struct.unpack_from("<I", body, i + 1)[0]
            j = i + 5
            targets = []
            fall = None
            if j < len(body) and body[j] == 0x74:
                targets.append(ENTRY + j + 2 + struct.unpack_from("<b", body, j + 1)[0])
                fall = ENTRY + j + 2
            if j + 5 < len(body) and body[j : j + 2] == b"\x0f\x84":
                targets.append(ENTRY + j + 6 + struct.unpack_from("<i", body, j + 2)[0])
                fall = ENTRY + j + 6
            if j < len(body) and body[j] == 0x75:
                fall = ENTRY + j + 2
            if j + 5 < len(body) and body[j : j + 2] == b"\x0f\x85":
                fall = ENTRY + j + 6
            for tva in targets:
                sva = mov_eax_at(tva)
                if sva is None:
                    continue
                s = read_cstr(data, sva, ib, secs)
                if s:
                    pairs[imm] = {
                        "string": s,
                        "string_va": hex(sva),
                        "how": "je_target",
                        "cmp_va": hex(ENTRY + i),
                    }
            if fall is not None and imm not in pairs:
                sva = mov_eax_at(fall)
                if sva is not None:
                    s = read_cstr(data, sva, ib, secs)
                    if s:
                        pairs[imm] = {
                            "string": s,
                            "string_va": hex(sva),
                            "how": "fallthrough",
                            "cmp_va": hex(ENTRY + i),
                        }
        i += 1

    # mov ecx,imm / cmp eax,ecx / je
    i = 0
    while i < len(body) - 14:
        if body[i] == 0xB9 and body[i + 5 : i + 7] == b"\x3b\xc1":
            imm = struct.unpack_from("<I", body, i + 1)[0]
            j = i + 7
            targets = []
            if j < len(body) and body[j] == 0x74:
                targets.append(ENTRY + j + 2 + struct.unpack_from("<b", body, j + 1)[0])
            if j + 5 < len(body) and body[j : j + 2] == b"\x0f\x84":
                targets.append(ENTRY + j + 6 + struct.unpack_from("<i", body, j + 2)[0])
            for tva in targets:
                sva = mov_eax_at(tva)
                if sva is None:
                    continue
                s = read_cstr(data, sva, ib, secs)
                if s:
                    pairs[imm] = {
                        "string": s,
                        "string_va": hex(sva),
                        "how": "ecx_je",
                        "cmp_va": hex(ENTRY + i),
                    }
        i += 1
    return pairs


def post_body_table_prefix(data: bytes, ib: int, secs) -> dict:
    """Classify residual immediately after ret as code-address table prefix."""
    start = BODY_END_EXCLUSIVE
    # scan up to next 32k
    end = start + 0x7000
    o0 = va_to_off(start, ib, secs)
    o1 = va_to_off(end, ib, secs)
    blob = data[o0:o1]
    text_lo, text_hi = 0x401000, 0x5D8000
    hr_lo, hr_hi = ENTRY, BODY_END_EXCLUSIVE
    run = 0
    for i in range(0, len(blob) - 3, 4):
        v = struct.unpack_from("<I", blob, i)[0]
        if text_lo <= v < text_hi:
            run += 1
        else:
            break
    in_hr = 0
    for i in range(0, run * 4, 4):
        v = struct.unpack_from("<I", blob, i)[0]
        if hr_lo <= v < hr_hi:
            in_hr += 1
    return {
        "residual_start": hex(start),
        "pure_code_ptr_prefix_dwords": run,
        "pure_code_ptr_prefix_bytes": run * 4,
        "prefix_end": hex(start + run * 4),
        "prefix_ptrs_into_hresult_body": in_hr,
        "kind": "CODE_ADDRESS_TABLE_PREFIX" if run >= 8 and in_hr == run else "MIXED",
    }


def analyze(specimen: Path) -> dict:
    data = specimen.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != PRISTINE:
        raise SystemExit(f"specimen mismatch {sha}")
    ib, secs = pe_sections(data)
    calls = find_calls(data, ib, secs, ENTRY)
    pairs = extract_pairs(data, ib, secs)
    ret_bytes = data[va_to_off(RET4_VA, ib, secs) : va_to_off(RET4_VA, ib, secs) + 3]
    table = post_body_table_prefix(data, ib, secs)
    required = {
        0x88760868: "D3DERR_DEVICELOST",
        0x88760869: "D3DERR_DEVICENOTRESET",
        0x80004004: "E_ABORT",
    }
    checks = []
    for imm, name in required.items():
        got = pairs.get(imm, {}).get("string")
        checks.append({"hresult": hex(imm), "expected": name, "got": got, "ok": got == name})
    if not all(c["ok"] for c in checks):
        raise AssertionError(f"required pairs failed: {checks}")
    if ret_bytes != b"\xc2\x04\x00":
        raise AssertionError(f"ret 4 missing: {ret_bytes.hex()}")
    if len(calls) != 21:
        raise AssertionError(f"expected 21 call sites, got {len(calls)}")

    return {
        "schema": "bea.re.hresult-tostring-static.v1",
        "status": "PASS",
        "specimen_sha256": sha,
        "entry_va": hex(ENTRY),
        "body_end_exclusive": hex(BODY_END_EXCLUSIVE),
        "body_bytes": BODY_END_EXCLUSIVE - ENTRY,
        "ret4_va": hex(RET4_VA),
        "ret4_bytes": ret_bytes.hex(),
        "n_call_sites": len(calls),
        "call_sites": [hex(c) for c in sorted(calls)],
        "n_string_pairs": len(pairs),
        "required_pair_checks": checks,
        "post_body_table": table,
        "pairs": [
            {
                "hresult": hex(k),
                "hresult_u32": k,
                **v,
            }
            for k, v in sorted(pairs.items())
        ],
        "reachability": {
            "status": "DARK_IN_EXISTING_COVERAGE_CORPUS",
            "note": (
                "14 local-lab exec-coverage plates do not cover RVA 0x1be628; "
                "Gen10 observedBytes=0. Callers include PARTIAL OPEN_EXECUTED owners "
                "whose error branches into this body are unobserved."
            ),
        },
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)
    try:
        result = analyze(args.specimen)
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    summary = {k: v for k, v in result.items() if k != "pairs"}
    print(json.dumps(summary, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("HRESULT_TOSTRING_STATIC_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
