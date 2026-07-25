"""Grade every function name by the strength of the evidence behind it.

The goal for this project's RE lane is "every name graded by its evidence", not
"every name replaced". A name like CUnitAI__SetStateTimestampCCToNow carries a
behavioural hypothesis that may well be right; overwriting it with CActor__vfunc_0
would trade a useful description for a correct prefix and lose the description.
So this emits a grade and the evidence, and leaves the names alone.

It also resolves the ownership problem that made grading unsafe before. A base
class's virtual methods appear in every derived class's vtable, so membership alone
attributes inherited methods to the wrong class. This walks the full MSVC RTTI
hierarchy -

    CompleteObjectLocator +16 -> RTTIClassHierarchyDescriptor
                                   +8  numBaseClasses
                                   +12 pBaseClassArray -> [RTTIBaseClassDescriptor]
                                                            +0 pTypeDescriptor

- to build each class's ancestor set, then attributes a shared function to the
  candidate class that is an ancestor of all the other candidates.

Grades, strongest first:
  RTTI_CONFIRMED   current prefix equals the resolved owning class
  RTTI_CONFLICT    RTTI resolves an owner and the current prefix disagrees
  RTTI_AMBIGUOUS   in several vtables and the hierarchy could not pick one owner
  BINARY_STRING    prefix appears verbatim as a string in the binary
  SOURCE_BACKED    prefix appears verbatim in the pinned reference source
  UNBACKED         no supporting evidence found (not disproven - a non-polymorphic
                   class emits no RTTI at all)
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
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--reference-source", type=Path)
    ap.add_argument("--out-tsv", type=Path)
    args = ap.parse_args(argv)

    data = args.binary.read_bytes()
    if hashlib.sha256(data).hexdigest() != PRISTINE_SHA256:
        print("REFUSED: not the pristine specimen.", file=sys.stderr)
        return 2

    pe = struct.unpack_from("<I", data, 0x3C)[0]
    optsz = struct.unpack_from("<H", data, pe + 20)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    imgbase = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    off = pe + 24 + optsz
    secs = []
    for i in range(nsec):
        b = data[off + i * 40: off + (i + 1) * 40]
        vsz, rva, rsz, rptr = struct.unpack_from("<IIII", b, 8)
        secs.append((b[0:8].rstrip(b"\0").decode(), imgbase + rva, vsz, rptr, rsz))
    text = next(s for s in secs if s[0] == ".text")
    TEXT_VA, TEXT_END = text[1], text[1] + text[2]

    def f2v(o):
        for _n, va, _vsz, rptr, rsz in secs:
            if rptr <= o < rptr + rsz:
                return va + (o - rptr)
        return None

    def v2f(va):
        for _n, base, vsz, rptr, rsz in secs:
            if base <= va < base + max(vsz, rsz):
                o = rptr + (va - base)
                return o if o + 4 <= len(data) else None
        return None

    def dw(va):
        o = v2f(va)
        return struct.unpack_from("<I", data, o)[0] if o is not None else None

    # --- RTTI ---------------------------------------------------------------
    type_desc = {}
    for m in re.finditer(rb"\.\?A[VU]([A-Za-z0-9_@?$]+)@@", data):
        nv = f2v(m.start())
        if nv is not None:
            type_desc[nv - 8] = m.group(1).decode()
    desc_set = set(type_desc)

    cols = {}
    for _n, base, _vsz, rptr, rsz in secs:
        blob = data[rptr:rptr + rsz]
        for i in range(0, len(blob) - 20, 4):
            if struct.unpack_from("<I", blob, i)[0] in (0, 1):
                ptd = struct.unpack_from("<I", blob, i + 12)[0]
                if ptd in desc_set:
                    cols[base + i] = (type_desc[ptd], struct.unpack_from("<I", blob, i + 16)[0])

    # class -> ancestor names, via the class hierarchy descriptor
    ancestors: dict[str, set[str]] = defaultdict(set)
    for _col_va, (cls, chd) in cols.items():
        if not chd:
            continue
        nbase = dw(chd + 8)
        parray = dw(chd + 12)
        if not nbase or not parray or nbase > 64:
            continue
        for k in range(nbase):
            bcd = dw(parray + 4 * k)
            if not bcd:
                continue
            ptd = dw(bcd)
            if ptd in desc_set:
                ancestors[cls].add(type_desc[ptd])

    vtables = {}
    col_set = set(cols)
    for _n, base, _vsz, rptr, rsz in secs:
        blob = data[rptr:rptr + rsz]
        for i in range(0, len(blob) - 4, 4):
            v = struct.unpack_from("<I", blob, i)[0]
            if v in col_set:
                vtables[base + i + 4] = cols[v][0]

    fn_classes = defaultdict(set)
    for vt, cls in vtables.items():
        o = v2f(vt)
        if o is None:
            continue
        slot = 0
        while o + 4 <= len(data):
            fn = struct.unpack_from("<I", data, o)[0]
            if not (TEXT_VA <= fn < TEXT_END):
                break
            if slot > 0 and (vt + slot * 4) in vtables:
                break
            fn_classes[fn].add(cls)
            slot += 1
            o += 4
            if slot > 512:
                break

    # resolve owner: the candidate that is an ancestor of every other candidate
    owner = {}
    ambiguous = 0
    for fn, cands in fn_classes.items():
        if len(cands) == 1:
            owner[fn] = next(iter(cands))
            continue
        picked = [c for c in cands if all(c in ancestors.get(d, set()) or c == d for d in cands)]
        if len(picked) == 1:
            owner[fn] = picked[0]
        else:
            ambiguous += 1

    # --- other evidence -----------------------------------------------------
    bin_strings = set()
    for m in re.finditer(rb"[ -~]{3,64}", data):
        bin_strings.add(m.group().decode("ascii"))
    # Declaration-aware, not substring. A bare "prefix in source_text" match counts
    # any incidental occurrence - a comment, a longer identifier that contains the
    # prefix, a string literal - and inflates this grade. Only accept a prefix that
    # the reference source actually DECLARES as a class or struct.
    src_types = set()
    if args.reference_source and args.reference_source.is_dir():
        decl = re.compile(r"(?:class|struct)\s+([A-Za-z_][A-Za-z0-9_]*)")
        for p in list(args.reference_source.glob("*.cpp")) + list(args.reference_source.glob("*.h")):
            try:
                src_types.update(decl.findall(p.read_text(encoding="utf-8", errors="ignore")))
            except OSError:
                pass

    # --- grade ---------------------------------------------------------------
    counts = defaultdict(int)
    rows = []
    with args.inventory.open(encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 2 or not p[0].startswith("0x"):
                continue
            va, name = int(p[0], 16), p[1]
            m = re.match(r"^([A-Za-z0-9_]+?)__", name)
            prefix = m.group(1) if m else ""
            # Ghidra's default FUN_/SUB_ names are the ABSENCE of a name, not a
            # competing claim. Scoring them as conflicts would inflate the conflict
            # count with functions nobody has named yet.
            unnamed = re.match(r"^(FUN|SUB|LAB|thunk_FUN)_[0-9a-fA-F]{6,}$", name) is not None
            if unnamed:
                grade = "UNNAMED_RTTI_OWNER" if va in owner else "UNNAMED"
                ev = f"default Ghidra name; owner={owner[va]}" if va in owner else "default Ghidra name"
            elif va in owner:
                grade = "RTTI_CONFIRMED" if prefix == owner[va] else "RTTI_CONFLICT"
                ev = f"vtable owner={owner[va]}"
            elif va in fn_classes:
                grade, ev = "RTTI_AMBIGUOUS", "in %d vtables, no single ancestor" % len(fn_classes[va])
            elif prefix and prefix in bin_strings:
                grade, ev = "BINARY_STRING", "prefix appears as a string in the binary"
            elif prefix and prefix in src_types:
                grade, ev = "SOURCE_BACKED", "reference source declares this class/struct"
            else:
                grade, ev = "UNBACKED", "no supporting evidence found"
            counts[grade] += 1
            rows.append((va, name, grade, ev))

    total = len(rows)
    print(f"classes with a hierarchy : {len(ancestors)}")
    print(f"functions reached by RTTI: {len(fn_classes)}   owner resolved: {len(owner)}   ambiguous: {ambiguous}")
    print(f"\nfunctions graded         : {total}")
    for g in ("RTTI_CONFIRMED", "RTTI_CONFLICT", "RTTI_AMBIGUOUS", "BINARY_STRING",
              "SOURCE_BACKED", "UNNAMED_RTTI_OWNER", "UNNAMED", "UNBACKED"):
        if counts[g]:
            print(f"  {g:<16} {counts[g]:>5}  ({100.0 * counts[g] / total:5.1f}%)")

    if args.out_tsv:
        args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
        with args.out_tsv.open("w", encoding="utf-8") as fh:
            fh.write("address\tname\tgrade\tevidence\n")
            for va, name, grade, ev in rows:
                fh.write(f"{va:#010x}\t{name}\t{grade}\t{ev}\n")
        print(f"\nledger: {args.out_tsv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
