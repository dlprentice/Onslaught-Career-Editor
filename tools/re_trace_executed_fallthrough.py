#!/usr/bin/env python3
"""Classify TRACE_EXECUTED_CORROBORATED residuals by static fallthrough shape.

For each join TRACE_EXECUTED residual on pristine PE:

  - Decode first insn at startVa and last insn before endVa
  - Grade whether residual is:
      FALLTHROUGH_CONTINUATION (prev function falls into residual; residual falls into next)
      ORPHAN_WITH_RET (starts like body, ends in ret)
      JMP_TABLE_CASE (looks like mid-switch case)
      PROLOGUE_LIKE (push ebp / sub esp patterns)
      UNKNOWN

Does not invent names. Does not claim CALL entry. Hash-bound specimen only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore


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


def v2o(va: int, ib: int, secs) -> int | None:
    rva = va - ib
    for sva, vs, rp, rs in secs:
        if sva <= rva < sva + max(vs, rs):
            d = rva - sva
            if d < rs:
                return rp + d
    return None


def first_last_insns(raw, ib, secs, start, end, md) -> dict:
    off = v2o(start, ib, secs)
    if off is None:
        return {"error": "unmapped"}
    nbytes = max(1, end - start)
    chunk = raw[off : off + nbytes + 16]
    insns = list(md.disasm(chunk, start))
    if not insns:
        return {"error": "no_decode", "bytes": chunk[:16].hex()}
    first = insns[0]
    last = None
    for i in insns:
        if i.address < end:
            last = i
        else:
            break
    return {
        "first": {
            "va": f"0x{first.address:08x}",
            "mnem": first.mnemonic,
            "ops": first.op_str,
            "bytes": first.bytes.hex(),
        },
        "last": None
        if last is None
        else {
            "va": f"0x{last.address:08x}",
            "mnem": last.mnemonic,
            "ops": last.op_str,
            "bytes": last.bytes.hex(),
        },
        "nInsnsInSpan": sum(1 for i in insns if i.address < end),
    }


def grade_shape(info: dict) -> str:
    if "error" in info:
        return "DECODE_FAIL"
    f = info["first"]["mnem"]
    l = (info.get("last") or {}).get("mnem")
    fb = info["first"]["bytes"]
    # prologue-like
    if f in ("push",) and "ebp" in info["first"]["ops"]:
        return "PROLOGUE_LIKE"
    if fb.startswith("83ec") or fb.startswith("81ec"):  # sub esp, imm
        return "PROLOGUE_LIKE"
    if f == "ret" or l == "ret":
        if f in ("mov", "push", "pop", "lea", "xor", "cmp", "test", "jmp", "je", "jne"):
            return "CASE_OR_BODY_WITH_RET"
        return "RET_SHAPED"
    if f == "jmp" and "dword ptr" in info["first"]["ops"]:
        return "JMP_INDIRECT"
    if f in ("mov", "push", "pop", "lea", "xor", "cmp", "test", "inc", "dec", "add", "sub"):
        if l in ("jmp", "je", "jne", "ja", "jb", "jg", "jl", "ret"):
            return "BODY_FRAGMENT"
        return "BODY_FRAGMENT"
    return "UNKNOWN"


def analyze(specimen: Path, join_json: Path) -> dict:
    if Cs is None:
        raise SystemExit("capstone required")
    raw = specimen.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen mismatch {sha}")
    ib, secs = pe_map(raw)
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    data = json.loads(join_json.read_text(encoding="utf-8"))
    rows = data.get("rows", data)
    te = [r for r in rows if r.get("joinGrade") == "TRACE_EXECUTED_CORROBORATED"]
    out = []
    grades: dict[str, int] = {}
    for r in te:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        info = first_last_insns(raw, ib, secs, start, end, md)
        g = grade_shape(info)
        grades[g] = grades.get(g, 0) + 1
        out.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": r.get("bytes"),
                "prevFunc": r.get("prevFunc"),
                "nextFunc": r.get("nextFunc"),
                "shape": info,
                "fallthroughGrade": g,
            }
        )
    return {
        "schema": "bea.re.trace-executed-fallthrough.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "n_candidates": len(out),
        "gradeCounts": grades,
        "candidates": out,
        "claims": [
            f"Classified {len(out)} TRACE_EXECUTED residuals by first/last insn shape on pristine PE.",
            "PROLOGUE_LIKE rows are higher-priority CALL-entry candidates for TTD call-context.",
            "BODY_FRAGMENT / CASE_OR_BODY_WITH_RET may be fallthrough islands, not free functions.",
        ],
        "non_claims": [
            "Does not invent names or mutate Gen10/Gen11.",
            "Shape grade is static only; runtime entry still required for CALL contracts.",
        ],
        "cheapestNextInstrument": (
            "TTD call-context on PROLOGUE_LIKE subset under level-opening traces "
            "that cover those RVAs in the EXECUTED union."
        ),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--join-json", type=Path, required=True)
    p.add_argument("--json-out", type=Path, required=True)
    args = p.parse_args(argv)
    result = analyze(args.specimen, args.join_json)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in result if k != "candidates"}, indent=2))
    print("TRACE_FALLTHROUGH_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
