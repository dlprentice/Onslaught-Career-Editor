"""Classify the .text bytes that belong to no Ghidra function as code vs data.

re_verify.py established that the 6,411-function inventory covers 79.8% of .text,
leaving 284,815 non-padding bytes in 4,356 runs owned by nothing. That is the gap
between "a complete pass over the function list" and "a complete pass over the
binary".

Not all of it is missing code. `.text` in an MSVC binary also holds pointer tables,
switch jump tables and alignment padding, all of which correctly belong to no
function. Creating functions on those would manufacture exactly the false positives
the earlier campaign stopped to avoid.

This tool separates them using evidence derived from the binary alone:

  PAD          every byte is 0xCC / 0x90 / 0x00
  PTR_TABLE    dwords overwhelmingly resolve into .text (a jump or function table)
  CODE         a real entry reference (CALL/JMP/stored pointer) or a textbook MSVC
               prologue at a 16-byte-aligned start, plus a clean instruction decode
  DATA         decodes badly and has no entry evidence
  UNKNOWN      decodes acceptably but nothing points at it - never auto-created

Only CODE is a creation candidate, and even then alignment is required, because an
unaligned "entry" is far more likely to be a branch into the middle of an existing
body, and creating a function there splits a real function in half.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

import capstone

PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"

PROLOGUES = (
    b"\x55\x8b\xec",       # push ebp; mov ebp,esp
    b"\x8b\xff",           # mov edi,edi  (hotpatch pad)
    b"\x83\xec",           # sub esp,imm8
    b"\x81\xec",           # sub esp,imm32
    b"\x53\x8b",           # push ebx; mov ...
    b"\x56\x8b",           # push esi; mov ...
    b"\x57\x8b",           # push edi; mov ...
    b"\x55\x8d",           # push ebp; lea ...
    b"\x8b\x44\x24",       # mov eax,[esp+n]   cdecl arg read
    b"\x8b\x4c\x24",       # mov ecx,[esp+n]
    b"\x8a\x44\x24",       # mov al,[esp+n]
    b"\xa1",               # mov eax,[imm32]
    b"\xc7\x05",           # mov [imm32],imm32
    b"\xd9\x05",           # fld [imm32]
    b"\x6a",               # push imm8
)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--binary", type=Path, required=True)
    ap.add_argument("--exports", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path)
    ap.add_argument("--out-candidates", type=Path, help="aligned CODE starts, one hex VA per line")
    ap.add_argument("--min-run", type=int, default=8)
    args = ap.parse_args(argv)

    data = args.binary.read_bytes()
    if hashlib.sha256(data).hexdigest() != PRISTINE_SHA256:
        print("REFUSED: not the pristine specimen the Ghidra DB was built from.", file=sys.stderr)
        return 2

    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    optsz = struct.unpack_from("<H", data, pe + 20)[0]
    imgbase = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    off = pe + 24 + optsz
    secs = []
    for i in range(nsec):
        b = data[off + i * 40: off + (i + 1) * 40]
        name = b[0:8].rstrip(b"\0").decode()
        vsz, rva, rsz, rptr = struct.unpack_from("<IIII", b, 8)
        secs.append((name, imgbase + rva, vsz, rptr, rsz))
    tname, TEXT_VA, TEXT_VSZ, TEXT_RPTR, TEXT_RSZ = next(s for s in secs if s[0] == ".text")[0:1] + \
        next(s for s in secs if s[0] == ".text")[1:]
    TEXT_END = TEXT_VA + TEXT_VSZ

    def f(va: int) -> int:
        return TEXT_RPTR + (va - TEXT_VA)

    # --- coverage bitmap from the exports --------------------------------
    covered = bytearray(TEXT_VSZ)
    for tsv in sorted(args.exports.glob("W*/instructions.tsv")):
        with tsv.open(encoding="utf-8") as fh:
            header = next(fh, "").rstrip("\n").split("\t")
            i_ia, i_by = header.index("instruction_addr"), header.index("bytes")
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) <= max(i_ia, i_by):
                    continue
                a = int(p[i_ia], 16) - TEXT_VA
                n = len(bytes.fromhex(p[i_by].replace(" ", "")))
                if 0 <= a < TEXT_VSZ:
                    covered[a:a + n] = b"\x01" * min(n, TEXT_VSZ - a)

    # --- entry-reference signals -----------------------------------------
    text_bytes = data[TEXT_RPTR:TEXT_RPTR + TEXT_RSZ]
    call_t, jmp_t = defaultdict(int), defaultdict(int)
    for i in range(len(text_bytes) - 5):
        op = text_bytes[i]
        if op in (0xE8, 0xE9):
            rel = struct.unpack_from("<i", text_bytes, i + 1)[0]
            tgt = TEXT_VA + i + 5 + rel
            if TEXT_VA <= tgt < TEXT_END:
                (call_t if op == 0xE8 else jmp_t)[tgt] += 1
    ptr_ref = defaultdict(int)
    for _n, _va, _vsz, rptr, rsz in secs:
        blob = data[rptr:rptr + rsz]
        for i in range(0, len(blob) - 4, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if TEXT_VA <= v < TEXT_END:
                ptr_ref[v] += 1

    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

    # --- runs -------------------------------------------------------------
    runs = []
    start = None
    for i in range(TEXT_VSZ):
        if not covered[i]:
            if start is None:
                start = i
        elif start is not None:
            runs.append((start, i))
            start = None
    if start is not None:
        runs.append((start, TEXT_VSZ))

    results, candidates = [], []
    counts = defaultdict(int)
    byte_counts = defaultdict(int)
    for lo, hi in runs:
        length = hi - lo
        if length < args.min_run:
            continue
        va = TEXT_VA + lo
        blob = data[f(va):f(va) + length]

        if all(b in (0xCC, 0x90, 0x00) for b in blob):
            cls, why = "PAD", "all alignment filler"
        else:
            dwords = [struct.unpack_from("<I", blob, i)[0] for i in range(0, len(blob) - 3, 4)]
            inside = sum(1 for v in dwords if TEXT_VA <= v < TEXT_END)
            if dwords and inside / len(dwords) >= 0.75:
                cls, why = "PTR_TABLE", f"{inside}/{len(dwords)} dwords resolve into .text"
            else:
                # skip leading filler, then judge the first real byte
                k = 0
                while k < len(blob) and blob[k] in (0xCC, 0x90):
                    k += 1
                entry = va + k
                body = blob[k:]
                decoded = list(md.disasm(bytes(body[:180]), entry))
                n_ok = len(decoded)
                pro = any(bytes(body).startswith(pfx) for pfx in PROLOGUES)
                refs = call_t.get(entry, 0) + jmp_t.get(entry, 0) + ptr_ref.get(entry, 0)
                aligned = entry % 16 == 0
                if n_ok >= 4 and (refs > 0 or (pro and aligned)):
                    cls = "CODE"
                    why = f"refs={refs} prologue={pro} aligned={aligned} insns={n_ok}"
                    if aligned:
                        candidates.append(entry)
                elif n_ok >= 4:
                    cls, why = "UNKNOWN", f"decodes ({n_ok}) but nothing references it"
                else:
                    cls, why = "DATA", f"poor decode ({n_ok} insns)"

        counts[cls] += 1
        byte_counts[cls] += length
        results.append({"va": f"{va:#010x}", "len": length, "class": cls, "why": why})

    total_runs = sum(counts.values())
    total_bytes = sum(byte_counts.values())
    print(f"runs >= {args.min_run} bytes : {total_runs}   ({total_bytes} bytes)")
    for k in sorted(counts, key=lambda x: -byte_counts[x]):
        print(f"  {k:<10} {counts[k]:>5} runs  {byte_counts[k]:>8} bytes"
              f"  ({100.0 * byte_counts[k] / total_bytes:5.1f}%)")
    print(f"\naligned CODE starts (creation candidates): {len(candidates)}")

    if args.out_tsv:
        args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
        with args.out_tsv.open("w", encoding="utf-8") as fh:
            fh.write("va\tlen\tclass\twhy\n")
            for r in results:
                fh.write(f"{r['va']}\t{r['len']}\t{r['class']}\t{r['why']}\n")
        print(f"detail: {args.out_tsv}")

    if args.out_candidates:
        args.out_candidates.parent.mkdir(parents=True, exist_ok=True)
        args.out_candidates.write_text(
            "\n".join(f"{a:#010x}" for a in sorted(candidates)) + "\n", encoding="utf-8")
        print(f"candidates: {args.out_candidates}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
