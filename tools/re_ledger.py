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
  RTTI_CONFIRMED       current prefix equals the resolved owning class
  RTTI_CONFLICT        RTTI resolves an owner and the current prefix disagrees
  RTTI_AMBIGUOUS       in several vtables and the hierarchy could not pick one owner
  OWNER_PREFIX_MISSING RTTI reaches this function but the name makes no class claim
  BINARY_STRING        prefix appears verbatim as a string in the binary
  SOURCE_BACKED        the pinned reference source DEFINES this class or struct
  UNNAMED_RTTI_OWNER   default Ghidra name, RTTI resolved an owner
  UNNAMED_RTTI_TARGET  default Ghidra name, in a vtable, owner unresolved
  UNNAMED              default Ghidra name, no RTTI observation
  UNBACKED             no supporting evidence found (not disproven - a
                       non-polymorphic class emits no RTTI at all)

With --partition-unbacked, UNBACKED is subdivided into seven mechanical cohorts.
See partition_unbacked() for the criteria. UNBACKED is one word for six materially
different situations and the headline percentage is not a naming-quality metric
until they are separated. The UNBACKED (total) parent line is printed either way,
deliberately: emitting only the seven children makes the headline read
"UNBACKED: 0", which would be quoted as if the naming had gained evidence. It has
not. Subdividing a bucket is not backing it.

FIXED 2026-07-25: SOURCE_BACKED previously reported 0. An editing pass had written
the word-boundary escape through a non-raw string, so a literal backspace byte
(0x08) sat at the head of the declaration pattern on disk and it matched nothing.
The byte is invisible when the file is read, which is why several passes of reading
the regex "confirmed" it was correct. `repr(decl.pattern)` showed it immediately.
Lesson worth keeping: to check what a pattern IS, print it - do not read it.

FIXED 2026-07-26: same failure family, found the same way - by executing the
artefact against the corpus rather than reading it. The replacement pattern
`\\b(?:class|struct)\\s+(\\w+)` was documented as "declaration-aware, not a
substring match". It is not: it also matches an ELABORATED TYPE SPECIFIER, so
`class CDXTexture *image;` - a pointer member in XBoxMemoryCard.h, with no
definition anywhere in the 106-file reference tree - "backed" 368 of the 1,009
SOURCE_BACKED rows (36.5%). The 1,009 rested on 71 distinct prefixes, not the 188
raw captures. Repairing it to require an actual DEFINITION moves 481 rows across
19 prefixes out of the grade (1,009 -> 528). It also recovers `IController`, which
the old pattern MISSED because a comment ending in the word "class" let `\\s+`
span the newline and consume the following `class` keyword as the captured token.
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

# --- reference-source class DEFINITION extraction ---------------------------
# See the module docstring for why this is definition-aware rather than
# declaration-aware. Print `repr()` of these, never read them.

# Comments and string/char literals are replaced by equal-length runs of spaces
# before any pattern is applied. This is not cosmetic: it is what stops a comment
# whose last word is "class" from letting `\s+` span the newline and swallow the
# next real `class` keyword as the captured token (the IController defect).
SRC_STRIP = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', re.S)

# Preprocessor conditional directives are blanked too, so that a class head split
# from its opening brace by an #ifdef arm still reads as a definition.
SRC_PP = re.compile(r"^[ \t]*#[ \t]*(?:if|ifdef|ifndef|else|elif|endif)\b[^\n]*", re.M)

# A DEFINITION: the class head must be followed by `{`, optionally through a base
# specifier introduced by a single `:`. The base-specifier character class
# deliberately excludes `*`, `&`, `(`, `)` and `;`, which is what rejects an
# elaborated type specifier such as `class CDXTexture *image` — a USE of the type,
# not a definition of it — and rejects `class CFoo;` forward declarations.
#
# `enum` is captured and then discarded: without it, `enum class EFoo { A };`
# would be collected as a class definition named EFoo. There is no `enum class` in
# the present reference tree (it is a C++11 form and this is a 2003 codebase), so
# this costs 0 tokens today - it is a live defect closed before it fires.
SRC_DEFN = re.compile(
    r"\b(?P<en>enum\s+)?(?:class|struct)\s+(?:__declspec\s*\([^)]*\)\s*)?"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:final\s*)?"
    r"(?:\{|:(?!:)[A-Za-z0-9_\s,:<>]*\{)", re.S)

# This tree also defines classes through macros (`DECLARE_THING_CLASS(CActor,
# CComplexThing)`, thing.h/actor.h). Those expansions are definitions and are
# collected; omitting them under-collects the grade.
SRC_MACRO = re.compile(r"\bDECLARE_[A-Z0-9_]*CLASS\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)")


def source_definitions(root: Path | None) -> set[str]:
    """Class/struct tokens the reference tree DEFINES, not merely mentions.

    A declaration is not evidence that this executable implements that class. The
    previous pattern, `\\b(?:class|struct)\\s+(\\w+)`, also matched an elaborated
    type specifier, so `class CDXTexture *image;` — a pointer member in an Xbox
    memory-card header, with no definition anywhere in the tree — "backed" 368
    function names. Only a definition counts now.
    """
    out: set[str] = set()
    if not root or not root.is_dir():
        return out
    # rglob, not glob: the previous non-recursive glob happened to be harmless for
    # this flat tree but silently drops every subdirectory of any other one.
    files = sorted(set(root.rglob("*.cpp")) | set(root.rglob("*.h"))
                   | set(root.rglob("*.hpp")) | set(root.rglob("*.cxx")))
    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        text = SRC_STRIP.sub(lambda m: " " * len(m.group()), text)
        text = SRC_PP.sub(lambda m: " " * len(m.group()), text)
        for m in SRC_DEFN.finditer(text):
            if not m.group("en"):
                out.add(m.group(2))
        out.update(SRC_MACRO.findall(text))
    return out


PARTITION_GRADES = ("COMPILER_EH_FUNCLET", "PE_IMPORT", "RESIDUAL_FREEFORM",
                    "VTABLE_VA_IN_BODY", "IMAGE_TYPE_TOKEN", "IMAGE_TYPE_SUBSTRING",
                    "INVENTED_PREFIX")


def import_slots(data: bytes, pe: int, imgbase: int, v2f) -> dict[int, str]:
    """IAT slot VA -> import name, walked from the PE import directory.

    Ordinal-only imports get `<dll>#ord<N>`; resolving those to a name is a human
    act and is not claimed here.
    """
    out: dict[int, str] = {}
    dd = pe + 24 + 96          # PE32 DataDirectory
    imp_rva = struct.unpack_from("<I", data, dd + 8)[0]   # entry 1 = import
    if not imp_rva:
        return out

    def cstr(rva: int) -> str:
        o = v2f(imgbase + rva)
        if o is None:
            return ""
        e = data.index(b"\0", o)
        return data[o:e].decode("latin-1")

    o = v2f(imgbase + imp_rva)
    if o is None:
        return out
    while True:
        oft, _ts, _fc, nm, ft = struct.unpack_from("<IIIII", data, o)
        if not (oft or ft):
            break
        dll = cstr(nm)
        names_rva, slot_rva = (oft or ft), ft
        no = v2f(imgbase + names_rva)
        if no is not None:
            k = 0
            while True:
                ent = struct.unpack_from("<I", data, no + 4 * k)[0]
                if not ent:
                    break
                if ent & 0x80000000:
                    label = f"{dll}#ord{ent & 0xFFFF}"
                else:
                    label = cstr(ent + 2)          # skip the 2-byte hint
                out[imgbase + slot_rva + 4 * k] = label
                k += 1
        o += 20
    return out


def partition_unbacked(rows, data, secs, v2f, vtables, bin_strings, desc_names,
                       imgbase, pe, verify_path):
    """Replace the single UNBACKED grade with seven mechanical cohorts.

    Every criterion is a byte test or a set membership; none is a judgement. The
    cohorts are applied in this order and are mutually exclusive, so they sum to
    the UNBACKED input count with no remainder:

      COMPILER_EH_FUNCLET  `Unwind@*`, size <= 64, 0 direct callers, exactly 1
                           absolute data reference. MSVC unwind funclets. These
                           are compiler output and can never carry a developer
                           name, so they must not be counted against naming.
      PE_IMPORT            body is `FF 25 <slot>` and the slot is in the import
                           directory. The import table is the strongest name
                           artefact in the file; grading it UNBACKED was absurd.
      RESIDUAL_FREEFORM    no `Prefix__` at all, and not one of the above.
      VTABLE_VA_IN_BODY    prefix IS an RTTI type descriptor in this image AND
                           the function's bytes contain that class's vtable VA as
                           an immediate. Evidence about THIS function's bytes -
                           and NOT a claim of ownership. See the warning below.
      IMAGE_TYPE_TOKEN     prefix IS an RTTI type descriptor in this image.
                           Licenses "this class exists in this build and the
                           prefix spells it" - NOT ownership of this function.
      IMAGE_TYPE_SUBSTRING prefix occurs as raw bytes somewhere in the image but
                           is not a type descriptor. Weak.
      INVENTED_PREFIX      prefix has no artefact of any kind: no type
                           descriptor, no byte occurrence in the whole image, no
                           reference-source definition. A name with nothing
                           behind it, and no bytes-only technique can ever back
                           it.

    VTABLE_VA_IN_BODY is the WEAK form of the vptr test: it accepts a vtable VA
    appearing anywhere in the body, not a store whose destination is proven to be
    entry ECX plus a known subobject offset. It over-collects for that reason and
    the cohort should be read as an upper bound.

    That is why it is NOT called VTABLE_STORE_OWN, which is what the proposal
    named it. `OWN` asserts ownership, and the test proves only that the class's
    vtable VA appears in these bytes - which is equally true of a constructor, a
    factory that builds an instance, and a member that seats a sibling subobject's
    vptr. Measured: 4 of the 176 rows are Create/Spawn-shaped
    (`CSpawnerData__CreateAndRegisterByName`). A grade must never claim more
    evidence than it has; the name now says exactly what was measured.
    """
    starts = sorted(va for va, _n, _g, _e in rows)
    sset = set(starts)

    extents: dict[int, int] = {}
    if verify_path:
        with verify_path.open(encoding="utf-8") as fh:
            ix = {n: i for i, n in enumerate(next(fh).rstrip("\n").split("\t"))}
            for line in fh:
                p = line.rstrip("\n").split("\t")
                try:
                    extents[int(p[ix["address"]], 16)] = int(p[ix["size"]])
                except (ValueError, KeyError, IndexError):
                    continue
    ends = {}
    for i, va in enumerate(starts):
        ends[va] = va + extents[va] if va in extents else (
            starts[i + 1] if i + 1 < len(starts) else va + 16)

    text = next(s for s in secs if s[0] == ".text")
    _n, tbase, tvs, trp, trs = text
    tend = tbase + tvs

    # direct callers, from a whole-.text E8/E9 rel32 sweep
    callers: dict[int, int] = defaultdict(int)
    for o in range(trs - 5):
        if data[trp + o] not in (0xE8, 0xE9):
            continue
        rel = struct.unpack_from("<i", data, trp + o + 1)[0]
        tgt = (tbase + o + 5 + rel) & 0xFFFFFFFF
        if tgt in sset:
            callers[tgt] += 1

    # absolute DWORD references to a function start, from .rdata and .data
    ptr_refs: dict[int, int] = defaultdict(int)
    for sname in (".rdata", ".data"):
        for s in secs:
            if s[0] != sname:
                continue
            _n2, _b2, _v2, rp2, rs2 = s
            for o in range(0, rs2 - 3, 4):
                v = struct.unpack_from("<I", data, rp2 + o)[0]
                if v in sset:
                    ptr_refs[v] += 1

    slots = import_slots(data, pe, imgbase, v2f)
    cls_vtables: dict[str, set[int]] = defaultdict(set)
    for vt, cls in vtables.items():
        cls_vtables[cls].add(vt)

    byte_seen: dict[str, bool] = {}
    out = []
    for va, name, grade, ev in rows:
        if grade != "UNBACKED":
            out.append((va, name, grade, ev))
            continue
        m = re.match(r"^([A-Za-z0-9_]+?)__", name)
        prefix = m.group(1) if m else ""
        size = ends[va] - va
        o = v2f(va)

        if (name.startswith("Unwind@") and size <= 64
                and callers.get(va, 0) == 0 and ptr_refs.get(va, 0) == 1):
            out.append((va, name, "COMPILER_EH_FUNCLET",
                        f"MSVC unwind funclet; {size}B, 0 callers, 1 data ref"))
            continue
        if (o is not None and data[o:o + 2] == b"\xff\x25"
                and struct.unpack_from("<I", data, o + 2)[0] in slots):
            slot = struct.unpack_from("<I", data, o + 2)[0]
            out.append((va, name, "PE_IMPORT",
                        f"FF 25 jmp [0x{slot:08x}]; import table says {slots[slot]}"))
            continue
        if not prefix:
            out.append((va, name, "RESIDUAL_FREEFORM", "no Prefix__ in name"))
            continue
        if prefix in desc_names:
            own = cls_vtables.get(prefix, set())
            hit = None
            if own and o is not None:
                end_o = o + max(size, 0)
                for i in range(o, min(end_o, len(data)) - 3):
                    v = struct.unpack_from("<I", data, i)[0]
                    if v in own:
                        hit = v
                        break
            if hit is not None:
                out.append((va, name, "VTABLE_VA_IN_BODY",
                            f"body contains {prefix} vtable VA 0x{hit:08x} "
                            f"(weak form: destination not sliced)"))
            else:
                out.append((va, name, "IMAGE_TYPE_TOKEN",
                            f"prefix is RTTI type descriptor .?AV{prefix}@@; "
                            f"ownership of this function NOT established"))
            continue
        if prefix not in byte_seen:
            byte_seen[prefix] = prefix.encode("ascii", "ignore") in data
        if byte_seen[prefix]:
            out.append((va, name, "IMAGE_TYPE_SUBSTRING",
                        "prefix occurs as raw bytes in the image, not as a type descriptor"))
        else:
            out.append((va, name, "INVENTED_PREFIX",
                        "prefix has no type descriptor, no byte occurrence in the "
                        "image, and no reference-source definition"))
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--binary", type=Path, required=True)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--reference-source", type=Path)
    ap.add_argument("--verify", type=Path,
                    help="re-verify.tsv, for MEASURED function extents. Without it "
                         "extents fall back to next-start, which over-states size "
                         "wherever padding follows.")
    ap.add_argument("--partition-unbacked", action="store_true",
                    help="split UNBACKED into its seven mechanical cohorts")
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
    src_types = source_definitions(args.reference_source)

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
                if va in owner:
                    grade, ev = "UNNAMED_RTTI_OWNER", f"default Ghidra name; owner={owner[va]}"
                elif va in fn_classes:
                    # Do not discard the RTTI observation just because nobody has
                    # named the function. Before this branch existed these rows
                    # graded plain UNNAMED and the vtable membership was lost.
                    grade = "UNNAMED_RTTI_TARGET"
                    ev = "default Ghidra name; in %d vtables, no single ancestor" % len(fn_classes[va])
                else:
                    grade, ev = "UNNAMED", "default Ghidra name"
            elif va in owner:
                # An absent prefix cannot disagree with RTTI. Grading a name that
                # makes no class claim as a CONFLICT counts a dispute that has only
                # one party.
                if not prefix:
                    grade, ev = "OWNER_PREFIX_MISSING", f"no Prefix__ in name; vtable owner={owner[va]}"
                else:
                    grade = "RTTI_CONFIRMED" if prefix == owner[va] else "RTTI_CONFLICT"
                    ev = f"vtable owner={owner[va]}"
            elif va in fn_classes:
                if not prefix:
                    grade = "OWNER_PREFIX_MISSING"
                    ev = "no Prefix__ in name; in %d vtables, no single ancestor" % len(fn_classes[va])
                else:
                    grade, ev = "RTTI_AMBIGUOUS", "in %d vtables, no single ancestor" % len(fn_classes[va])
            elif prefix and prefix in bin_strings:
                grade, ev = "BINARY_STRING", "prefix appears as a string in the binary"
            elif prefix and prefix in src_types:
                grade, ev = "SOURCE_BACKED", "reference source DEFINES this class/struct"
            else:
                grade, ev = "UNBACKED", "no supporting evidence found"
            rows.append((va, name, grade, ev))

    # --- partition UNBACKED --------------------------------------------------
    if args.partition_unbacked:
        rows = partition_unbacked(rows, data, secs, v2f, vtables, bin_strings,
                                  set(type_desc.values()), imgbase, pe, args.verify)
    for _va, _name, grade, _ev in rows:
        counts[grade] += 1

    total = len(rows)
    inv = {va for va, _n, _g, _e in rows}
    print(f"classes with a hierarchy : {len(ancestors)}")
    # Two numbers, because they are two different things and reporting only the
    # first over-states reach. fn_classes is keyed by any .text-range DWORD found
    # in a recovered vtable slot; only the subset that is an inventory function
    # START is ever graded.
    print(f"vtable slot targets in .text: {len(fn_classes)}   "
          f"of which inventory function starts: {len(fn_classes.keys() & inv)}   "
          f"not in inventory: {len(fn_classes.keys() - inv)}")
    print(f"owner resolved (any target): {len(owner)}   ambiguous: {ambiguous}")
    print(f"\nfunctions graded         : {total}")
    for g in ("RTTI_CONFIRMED", "RTTI_CONFLICT", "RTTI_AMBIGUOUS", "OWNER_PREFIX_MISSING",
              "BINARY_STRING", "SOURCE_BACKED", "UNNAMED_RTTI_OWNER", "UNNAMED_RTTI_TARGET",
              "UNNAMED"):
        if counts[g]:
            print(f"  {g:<20} {counts[g]:>5}  ({100.0 * counts[g] / total:5.1f}%)")
    # The parent line is printed whether or not the partition ran. Emitting only
    # the seven children makes UNBACKED read as 0, and a reader will quote that as
    # "the naming is now backed". Nothing here gained evidence; it was subdivided.
    ub = counts["UNBACKED"] + sum(counts[g] for g in PARTITION_GRADES)
    print(f"  {'UNBACKED (total)':<20} {ub:>5}  ({100.0 * ub / total:5.1f}%)")
    for g in PARTITION_GRADES:
        if counts[g]:
            print(f"    {g:<18} {counts[g]:>5}  ({100.0 * counts[g] / total:5.1f}%)")
    if args.partition_unbacked:
        namable = total - counts["COMPILER_EH_FUNCLET"]
        resid = counts["INVENTED_PREFIX"] + counts["IMAGE_TYPE_SUBSTRING"] + counts["RESIDUAL_FREEFORM"]
        print(f"\n  human-namable (total - EH funclets): {namable}")
        print(f"  residual with no image-local evidence: {resid}  "
              f"({100.0 * resid / namable:.1f}% of namable)")

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
