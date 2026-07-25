"""Recover class -> vtable -> virtual-method mappings from the binary's own RTTI.

BEA.exe carries 667 MSVC RTTI type descriptors holding real class names as the
original developers wrote them. Roughly 42% of the class prefixes currently in the
Ghidra database have no RTTI backing at all, which means a naming layer was partly
invented while real names sat unread in the same file.

RTTI is not just a string list. It is a structure chain, and following it converts
one class name into correct names for every virtual method of that class, with the
relationship proven by the binary's own layout rather than inferred from call
patterns:

    TypeDescriptor  (name string, preceded by vftable ptr + spare)
        ^
        | +12
    RTTICompleteObjectLocator
        ^
        | a dword somewhere equal to the COL address
    [vtable - 4]  ->  vtable  ->  consecutive .text pointers = virtual methods

Everything here is derived from bytes. Nothing is inferred from the existing
database, so the result is independent evidence rather than the analyser grading
its own homework.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path

PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--binary", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path)
    ap.add_argument("--inventory", type=Path, help="functions-all.tsv, to report overlap")
    args = ap.parse_args(argv)

    data = args.binary.read_bytes()
    if hashlib.sha256(data).hexdigest() != PRISTINE_SHA256:
        print("REFUSED: not the pristine specimen.", file=sys.stderr)
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
    text = next(s for s in secs if s[0] == ".text")
    TEXT_VA, TEXT_END = text[1], text[1] + text[2]

    def f2v(foff):
        for _n, va, vsz, rptr, rsz in secs:
            if rptr <= foff < rptr + rsz:
                return va + (foff - rptr)
        return None

    def v2f(va):
        for _n, base, vsz, rptr, rsz in secs:
            if base <= va < base + max(vsz, rsz):
                o = rptr + (va - base)
                return o if o < len(data) else None
        return None

    # --- 1. type descriptors ------------------------------------------------
    # TypeDescriptor = { void* pVFTable; void* spare; char name[]; }
    type_desc = {}   # descriptorVA -> class name
    for m in re.finditer(rb"\.\?A[VU]([A-Za-z0-9_@?$]+)@@", data):
        name_va = f2v(m.start())
        if name_va is None:
            continue
        type_desc[name_va - 8] = m.group(1).decode()
    print(f"type descriptors        : {len(type_desc)}")

    # --- 2. complete object locators ---------------------------------------
    # COL = { sig, offset, cdOffset, pTypeDescriptor, pClassDescriptor }
    col_to_class = {}
    desc_set = set(type_desc)
    for _n, base, vsz, rptr, rsz in secs:
        blob = data[rptr:rptr + rsz]
        for i in range(0, len(blob) - 20, 4):
            ptd = struct.unpack_from("<I", blob, i + 12)[0]
            if ptd in desc_set and struct.unpack_from("<I", blob, i)[0] in (0, 1):
                col_to_class[base + i] = type_desc[ptd]
    print(f"complete object locators: {len(col_to_class)}")

    # --- 3. vtables ---------------------------------------------------------
    vtables = {}   # vtableVA -> class name
    col_set = set(col_to_class)
    for _n, base, vsz, rptr, rsz in secs:
        blob = data[rptr:rptr + rsz]
        for i in range(0, len(blob) - 4, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if v in col_set:
                vtables[base + i + 4] = col_to_class[v]
    print(f"vtables located         : {len(vtables)}")

    # --- 4. virtual method slots -------------------------------------------
    rows = []
    per_class = defaultdict(list)
    for vt_va, cls in sorted(vtables.items()):
        foff = v2f(vt_va)
        if foff is None:
            continue
        slot = 0
        while True:
            if foff + 4 > len(data):
                break
            fn = struct.unpack_from("<I", data, foff)[0]
            if not (TEXT_VA <= fn < TEXT_END):
                break
            # a following vtable's COL pointer terminates this one
            if slot > 0 and (vt_va + slot * 4) in vtables:
                break
            rows.append((cls, vt_va, slot, fn))
            per_class[cls].append(fn)
            slot += 1
            foff += 4
            if slot > 512:
                break

    distinct_fns = {fn for _c, _v, _s, fn in rows}
    print(f"vtable slots resolved   : {len(rows)}")
    print(f"distinct functions named: {len(distinct_fns)}")
    print(f"classes with a vtable   : {len(per_class)}")

    if args.inventory:
        inv = {}
        with args.inventory.open(encoding="utf-8") as fh:
            next(fh, None)
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 2 and p[0].startswith("0x"):
                    inv[int(p[0], 16)] = p[1]
        known = sum(1 for fn in distinct_fns if fn in inv)
        agree = 0
        disagree = []
        for fn in distinct_fns:
            if fn not in inv:
                continue
            cur = inv[fn]
            classes = {c for c, _v, _s, g in rows if g == fn}
            if any(cur.startswith(c + "__") for c in classes):
                agree += 1
            else:
                disagree.append((fn, cur, sorted(classes)[:2]))
        print()
        print(f"of those, already in the inventory : {known}")
        print(f"  current name matches RTTI class  : {agree}")
        print(f"  current name DISAGREES with RTTI : {len(disagree)}")
        print(f"  not in inventory at all          : {len(distinct_fns) - known}")
        print("\nsample disagreements (RTTI is the stronger evidence):")
        for fn, cur, cls in disagree[:12]:
            print(f"  {fn:#010x}  now={cur[:44]:<44} rtti={cls}")

    if args.out_tsv:
        args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
        with args.out_tsv.open("w", encoding="utf-8") as fh:
            fh.write("class\tvtable_va\tslot\tfunction_va\n")
            for cls, vt, slot, fn in rows:
                fh.write(f"{cls}\t{vt:#010x}\t{slot}\t{fn:#010x}\n")
        print(f"\nmapping: {args.out_tsv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
