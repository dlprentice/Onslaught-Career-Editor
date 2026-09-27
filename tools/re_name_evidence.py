#!/usr/bin/env python3
"""Byte-level evidence for every saved Ghidra function name in the pristine BEA.exe.

The RE record audit (PROGRAM.md, "RE record audit") treats every saved name as a
claim. This tool builds a whole-program model from the pristine specimen alone
(instructions, references, strings, imports, RTTI classes, vtables and bases) and
from the pinned GPL source, then records for each function what the bytes and the
source actually support. It never opens Ghidra and never writes the specimen; its
output is private evidence under local-data/.

Usage:
  python tools/re_name_evidence.py model  --out DIR          # build and cache the model
  python tools/re_name_evidence.py facts --functions TSV --out DIR     # counts of what the evidence supports
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import pickle
import re
import struct
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIMEN = ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
SOURCE = ROOT / "references/Onslaught"
IMAGE_BASE = 0x400000
MODEL_VERSION = 4   # 4: retain only proven fixed PMDs for subobject-offset composition


# ---------------------------------------------------------------------------
# PE image
# ---------------------------------------------------------------------------

@dataclass
class Section:
    name: str
    start: int          # virtual address
    size: int           # virtual size
    raw: bytes          # raw data (may be shorter than size)
    characteristics: int = 0

    def contains(self, va: int) -> bool:
        return self.start <= va < self.start + self.size


class Image:
    """Minimal PE reader over the pristine specimen (read-only)."""

    def __init__(self, path: Path = SPECIMEN, expected_sha256: str | None = SPECIMEN_SHA256):
        import pefile  # local import keeps the pure helpers importable without pefile
        self.data = path.read_bytes()
        digest = hashlib.sha256(self.data).hexdigest()
        if expected_sha256 and digest != expected_sha256:
            raise SystemExit(f"specimen hash {digest} is not the pristine {expected_sha256}")
        self.sha256 = digest
        pe = pefile.PE(data=self.data, fast_load=True)
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
        self.base = pe.OPTIONAL_HEADER.ImageBase
        self.entry = self.base + pe.OPTIONAL_HEADER.AddressOfEntryPoint
        self.sections = []
        for s in pe.sections:
            name = s.Name.rstrip(b"\0").decode("ascii", "replace")
            raw = self.data[s.PointerToRawData:s.PointerToRawData + s.SizeOfRawData]
            self.sections.append(Section(name, self.base + s.VirtualAddress,
                                         max(s.Misc_VirtualSize, len(raw)), raw, s.Characteristics))
        self.imports = {}  # IAT slot VA -> "DLL!name"
        for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
            dll = entry.dll.decode("ascii", "replace")
            for imp in entry.imports:
                name = imp.name.decode("ascii", "replace") if imp.name else f"ord{imp.ordinal}"
                self.imports[imp.address] = f"{dll}!{name}"
        self.text = next(s for s in self.sections if s.name == ".text")

    def section_of(self, va: int) -> Section | None:
        for s in self.sections:
            if s.contains(va):
                return s
        return None

    def read(self, va: int, n: int) -> bytes:
        s = self.section_of(va)
        if s is None:
            return b""
        off = va - s.start
        return s.raw[off:off + n]

    def u32(self, va: int) -> int | None:
        b = self.read(va, 4)
        return struct.unpack("<I", b)[0] if len(b) == 4 else None

    def cstring(self, va: int, limit: int = 512) -> str | None:
        b = self.read(va, limit)
        end = b.find(b"\0")
        if end <= 0:
            return None
        try:
            return b[:end].decode("latin-1")
        except UnicodeDecodeError:
            return None

    def is_code(self, va: int) -> bool:
        return self.text.contains(va)


# ---------------------------------------------------------------------------
# Disassembly and references
# ---------------------------------------------------------------------------

_OBJDUMP_LINE = re.compile(r"^\s*([0-9a-f]+):\t((?:[0-9a-f]{2} )+)\s*\t?(.*)$")
_HEX = re.compile(r"0x([0-9a-f]+)")
_DIRECT = re.compile(r"^0x[0-9a-f]+$")


@dataclass
class Insn:
    va: int
    size: int
    mnem: str
    ops: str


def disassemble(img: Image) -> list[Insn]:
    """Linear objdump disassembly of .text (Intel syntax), continuation lines merged."""
    sec = img.text
    with tempfile.NamedTemporaryFile(suffix=".bin") as tmp:
        tmp.write(sec.raw)
        tmp.flush()
        out = subprocess.run(
            ["objdump", "-D", "-b", "binary", "-m", "i386", "-M", "intel", "-w",
             f"--adjust-vma={sec.start:#x}", tmp.name],
            capture_output=True, text=True, check=True).stdout
    return [ins for ins, _raw in parse_objdump(out)]


def parse_objdump(out: str) -> list[tuple[Insn, bytes]]:
    """Parse GNU Intel rows, retaining raw bytes for bounded coverage checks."""
    insns: list[tuple[Insn, bytes]] = []
    for line in out.splitlines():
        m = _OBJDUMP_LINE.match(line)
        if not m:
            continue
        va = int(m.group(1), 16)
        raw = bytes.fromhex(m.group(2))
        size = len(raw)
        text = m.group(3).strip()
        if not text:
            continue
        parts = text.split(None, 1)
        mnem = parts[0]
        ops = parts[1] if len(parts) > 1 else ""
        # drop objdump's symbolic comments such as "# 0x..." or "<...>"
        ops = ops.split("#", 1)[0].strip()
        insns.append((Insn(va, size, mnem, ops), raw))
    return insns

def decode_entry_body(img: Image, fn: Func) -> list[Insn]:
    """Decode one complete exported body from its entry, never patch the model.

    Whole-image linear decoding may consume entry bytes as part of a preceding
    instruction. A local decode may repair coverage only; callers must still
    check control flow, ownership and ABI. Raw output is checked against every
    input byte, and undecodable/truncated rows are rejected.
    """
    size = fn.hi - fn.va + 1
    if (fn.lo != fn.va or getattr(fn, 'body_ranges', None) != 1
            or getattr(fn, 'declared_hi', None) != fn.hi
            or getattr(fn, 'body_bytes', None) != size or not 0 < size <= 1024 * 1024):
        raise ValueError('exact single-range exported extent required')
    sec = img.section_of(fn.va)
    if (sec is None or not sec.characteristics & 0x20000000
            or fn.hi >= sec.start + min(sec.size, len(sec.raw))):
        raise ValueError('complete body must have executable file-backed bytes')
    raw = img.read(fn.va, size)
    if len(raw) != size:
        raise ValueError('short selected-body read')
    with tempfile.NamedTemporaryFile(suffix='.bin') as tmp:
        tmp.write(raw)
        tmp.flush()
        out = subprocess.run(
            ['objdump', '-D', '-z', '-b', 'binary', '-m', 'i386', '-M', 'intel', '-w',
             f'--adjust-vma={fn.va:#x}', tmp.name],
            capture_output=True, text=True, check=True, timeout=30).stdout
    body = []
    cursor = fn.va
    for ins, decoded in parse_objdump(out):
        if (ins.va != cursor or not 1 <= ins.size <= 15
                or cursor + ins.size > fn.hi + 1
                or decoded != raw[cursor - fn.va:cursor - fn.va + ins.size]):
            raise ValueError('entry decode has a gap, overlap, overshoot or byte mismatch')
        if ins.mnem == '(bad)' or ins.mnem.startswith('.'):
            raise ValueError('invalid or data instruction in entry decode')
        body.append(ins)
        cursor += ins.size
    if cursor != fn.hi + 1:
        raise ValueError('entry decode does not cover the complete body')
    return body


def insn_refs(insn: Insn, img: Image) -> list[tuple[str, int]]:
    """References made by one instruction: ('call'|'jmp'|'jcc'|'imm'|'mem', target)."""
    refs = []
    mn = insn.mnem
    direct = _DIRECT.match(insn.ops) is not None
    if mn == "call" and direct:
        refs.append(("call", int(insn.ops, 16)))
        return refs
    if mn == "jmp" and direct:
        refs.append(("jmp", int(insn.ops, 16)))
        return refs
    if mn.startswith("j") and direct:
        refs.append(("jcc", int(insn.ops, 16)))
        return refs
    for m in _HEX.finditer(insn.ops):
        v = int(m.group(1), 16)
        if not (img.base <= v < img.base + 0x1000000):
            continue
        if img.section_of(v) is None:
            continue
        # memory operand (inside brackets, or objdump's bare segment form "ds:0x...") or immediate
        start = m.start()
        in_mem = (insn.ops.rfind("[", 0, start) > insn.ops.rfind("]", 0, start)
                  or insn.ops[max(0, start - 3):start] in ("ds:", "es:", "fs:", "gs:", "cs:", "ss:"))
        refs.append(("mem" if in_mem else "imm", v))
    return refs


# ---------------------------------------------------------------------------
# Strings
# ---------------------------------------------------------------------------

def scan_strings(img: Image, min_len: int = 4) -> dict[int, str]:
    """NUL-terminated printable ASCII strings in the data sections."""
    out = {}
    pat = re.compile(rb"[\x09\x0a\x0d\x20-\x7e]{%d,}\x00" % min_len)
    for s in img.sections:
        if s.name == ".text":
            continue
        for m in pat.finditer(s.raw):
            out[s.start + m.start()] = m.group()[:-1].decode("ascii")
    return out


# ---------------------------------------------------------------------------
# RTTI
# ---------------------------------------------------------------------------

@dataclass
class Vtable:
    va: int
    klass: str
    offset: int                      # subobject offset from the COL
    slots: list[int] = field(default_factory=list)


@dataclass
class RttiModel:
    type_names: dict[int, str]                 # type descriptor VA -> decorated name
    class_bases: dict[str, list[tuple[str, int]]]  # class -> [(base class, mdisp)] in CHD order (self first)
    vtables: list[Vtable]
    fixed_bases: dict[str, list[tuple[str, int]]] = field(default_factory=dict)


def demangle_type(name: str) -> str:
    """'.?AVCFoo@@' -> 'CFoo'; nested '.?AVInner@Outer@@' -> 'Outer::Inner'."""
    body = name[4:] if name.startswith((".?AV", ".?AU")) else name
    body = body.rstrip("@")
    parts = [p for p in body.split("@") if p]
    return "::".join(reversed(parts)) if parts else name


def scan_rtti(img: Image) -> RttiModel:
    """RTTI classes, bases (hierarchy order, self first, with mdisp) and vtables, from the strict census of
    tools/re_rtti_vtables.py, the repository's owner of RTTI recovery."""
    from re_rtti_vtables import parse_rtti
    census = parse_rtti(img.data)
    plain = lambda raw: demangle_type(".?AV" + raw + "@@")
    type_names = {va: plain(td.name) for va, td in census.type_descriptors.items()}
    class_bases: dict[str, list[tuple[str, int]]] = {}
    fixed_bases: dict[str, list[tuple[str, int]]] = {}
    for h in census.hierarchies.values():
        root = plain(h.root_class)
        class_bases.setdefault(root,
                               [(plain(r.descriptor.class_name), r.descriptor.mdisp) for r in h.rows])
        fixed = [(plain(r.descriptor.class_name), r.descriptor.mdisp) for r in h.rows
                 if r.descriptor.pdisp == -1 and r.descriptor.vdisp == 0 and r.descriptor.mdisp >= 0]
        if root in fixed_bases:
            fixed_bases[root] = [item for item in fixed_bases[root] if item in fixed]
        else:
            fixed_bases[root] = fixed
    slots: dict[int, list[int]] = defaultdict(list)
    for slot in sorted(census.slots, key=lambda x: (x.vtable_va, x.slot)):
        slots[slot.vtable_va].append(slot.function_va)
    vtables = [Vtable(va, plain(v.class_name), census.cols[v.col_va].offset, slots[va])
               for va, v in sorted(census.vtables.items())]
    return RttiModel(type_names, class_bases, vtables, fixed_bases)


@dataclass
class Model:
    version: int
    sha256: str
    entry: int
    imports: dict[int, str]
    insns: list[Insn]
    strings: dict[int, str]
    rtti: RttiModel
    refs_from: dict[int, list[tuple[str, int]]]   # insn va -> refs
    refs_to: dict[int, list[tuple[str, int]]]     # target -> [(kind, insn va)]
    data_ptrs_to: dict[int, list[int]]            # code target -> data words pointing at it

    def insn_index(self) -> list[int]:
        return [i.va for i in self.insns]


def build_model(img: Image) -> Model:
    insns = disassemble(img)
    refs_from: dict[int, list[tuple[str, int]]] = {}
    refs_to: dict[int, list[tuple[str, int]]] = defaultdict(list)
    for ins in insns:
        r = insn_refs(ins, img)
        if r:
            refs_from[ins.va] = r
            for kind, t in r:
                refs_to[t].append((kind, ins.va))
    strings = scan_strings(img)
    rtti = scan_rtti(img)
    data_ptrs_to: dict[int, list[int]] = defaultdict(list)
    for s in img.sections:
        if s.name == ".text":
            continue
        raw = s.raw
        for off in range(0, len(raw) - 4, 4):
            w = struct.unpack_from("<I", raw, off)[0]
            if img.is_code(w):
                data_ptrs_to[w].append(s.start + off)
    return Model(MODEL_VERSION, img.sha256, img.entry, dict(img.imports), insns, strings, rtti,
                 refs_from, dict(refs_to), dict(data_ptrs_to))


def load_or_build(cache: Path) -> tuple[Image, Model]:
    img = Image()
    if cache.exists():
        with cache.open("rb") as f:
            model = pickle.load(f)
        if model.version == MODEL_VERSION and model.sha256 == img.sha256:
            return img, model
    model = build_model(img)
    cache.parent.mkdir(parents=True, exist_ok=True)
    with cache.open("wb") as f:
        pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
    return img, model


# ---------------------------------------------------------------------------
# Functions and per-function facts
# ---------------------------------------------------------------------------

@dataclass
class Func:
    va: int
    name: str
    source: str            # Ghidra nameSource
    lo: int
    hi: int                # inclusive
    signature: str
    calling: str
    comment: bool
    tags: str
    thunk: bool
    body_ranges: int = 1
    body_bytes: int | None = None
    declared_hi: int | None = None


def load_functions(path: Path) -> list[Func]:
    out = []
    with path.open() as f:
        for r in csv.DictReader(f, delimiter="\t"):
            va = int(r["address"], 16)
            out.append(Func(va, r["name"], r["nameSource"], int(r["bodyMin"], 16), int(r["bodyMax"], 16),
                            r["signature"], r["callingConv"], r["commentPresent"] == "true", r["tags"],
                            r["isThunk"] == "true", int(r['bodyRanges']), int(r['bodyBytes']),
                            int(r['bodyMax'], 16)))
    out.sort(key=lambda x: x.va)
    # clip multi-range bounding boxes at the next function start
    for i, fn in enumerate(out):
        nxt = out[i + 1].va if i + 1 < len(out) else fn.hi + 1
        if fn.hi >= nxt:
            fn.hi = nxt - 1
    return out


class Program:
    """Model plus function table: who calls whom, which vtables hold what."""

    def __init__(self, img: Image, model: Model, funcs: list[Func]):
        self.img, self.model, self.funcs = img, model, funcs
        self.by_va = {f.va: f for f in funcs}
        self.starts = [f.va for f in funcs]
        self.insn_vas = [i.va for i in model.insns]
        # vtable membership: func va -> [(class, subobject offset, slot, vtable va)]
        self.slots: dict[int, list[tuple[str, int, int, int]]] = defaultdict(list)
        for vt in model.rtti.vtables:
            for i, t in enumerate(vt.slots):
                self.slots[t].append((vt.klass, vt.offset, i, vt.va))
        self.bases = model.rtti.class_bases
        self.fixed_bases = model.rtti.fixed_bases

    def func_at(self, va: int) -> Func | None:
        i = bisect.bisect_right(self.starts, va) - 1
        if i < 0:
            return None
        f = self.funcs[i]
        return f if f.lo <= va <= f.hi else None

    def body(self, f: Func) -> list[Insn]:
        i = bisect.bisect_left(self.insn_vas, f.va)
        out = []
        while i < len(self.model.insns) and self.model.insns[i].va <= f.hi:
            out.append(self.model.insns[i])
            i += 1
        return out

    def callers(self, f: Func) -> list[tuple[str, int, Func | None]]:
        return [(k, site, self.func_at(site)) for k, site in self.model.refs_to.get(f.va, [])
                if k in ("call", "jmp")]

    def strings_used(self, f: Func) -> list[tuple[int, str]]:
        out = []
        for ins in self.body(f):
            for _k, t in self.model.refs_from.get(ins.va, []):
                s = self.model.strings.get(t)
                if s is not None:
                    out.append((t, s))
        return out

    def is_ancestor(self, base: str, klass: str) -> bool:
        return any(b == base for b, _ in self.bases.get(klass, [])[1:])

    def defining_classes(self, f: Func) -> set[str]:
        """RTTI holders with a slot not inherited at the same subobject offset.

        A folded body may occupy several unrelated slots. Inheritance of one
        occurrence must not erase a new occurrence in the derived class. This
        identifies slot holders, not the semantic owner of every folded body.
        Negative/dynamic base offsets cannot establish this relationship.
        """
        holders = self.slots.get(f.va, [])
        minimal = set()
        for k, offset, slot, _table in holders:
            inherited = any(
                other != k and other_slot == slot
                and any(base == other and displacement >= 0
                        and displacement + other_offset == offset
                        for base, displacement in self.fixed_bases.get(k, []))
                for other, other_offset, other_slot, _other_table in holders)
            if not inherited:
                minimal.add(k)
        return minimal


def split_name(name: str) -> tuple[str | None, str]:
    """'CFoo__Bar_T3_00401000' -> ('CFoo', 'Bar_T3_00401000'); free names -> (None, name)."""
    if "__" in name and not name.startswith("__"):
        owner, method = name.split("__", 1)
        if owner and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", owner):
            return owner, method
    return None, name


# ---------------------------------------------------------------------------
# Small-function semantics
# ---------------------------------------------------------------------------

_PAD = {"nop", "int3", "xchg"}


def tiny_semantics(prog: "Program", f: Func, limit: int = 6,
                   *, instructions: list[Insn] | None = None) -> str | None:
    """Canonical description of a very small body, or None.

    Forms: noop:retN, const:V:retN, field:OFF:retN, this:retN, fconst:ADDR:retN,
    store:OFF:SRC:retN, thunk:TARGET, jmpimport:NAME."""
    selected = prog.body(f) if instructions is None else instructions
    body = [i for i in selected if i.mnem not in _PAD]
    if not body or len(body) > limit:
        return None
    last = body[-1]
    if last.mnem == "jmp":
        if len(body) == 1:
            m = re.match(r"^DWORD PTR ds:0x([0-9a-f]+)$", last.ops)
            if m and int(m.group(1), 16) in prog.model.imports:
                return "jmpimport:" + prog.model.imports[int(m.group(1), 16)].split("!", 1)[1]
            if _DIRECT.match(last.ops):
                return f"thunk:{int(last.ops, 16):08x}"
        return None
    if last.mnem != "ret":
        return None
    retn = int(last.ops, 16) if last.ops else 0
    rest = body[:-1]
    if not rest:
        return f"noop:ret{retn:x}"
    if len(rest) == 1:
        i = rest[0]
        if i.mnem == "xor" and i.ops == "eax,eax":
            return f"const:0:ret{retn:x}"
        if i.mnem == "or" and i.ops == "eax,0xffffffff":
            return f"const:-1:ret{retn:x}"
        m = re.match(r"^eax,0x([0-9a-f]+)$", i.ops)
        if i.mnem == "mov" and m:
            v = int(m.group(1), 16)
            return f"const:{v - (1 << 32) if v >= 1 << 31 else v}:ret{retn:x}"
        m = re.match(r"^eax,DWORD PTR \[ecx(?:\+0x([0-9a-f]+))?\]$", i.ops)
        if i.mnem == "mov" and m:
            return f"field:{int(m.group(1) or '0', 16):x}:ret{retn:x}"
        if i.mnem == "mov" and i.ops == "eax,ecx":
            return f"this:ret{retn:x}"
        m = re.match(r"^DWORD PTR ds:0x([0-9a-f]+)$", i.ops)
        if i.mnem == "fld" and m:
            return f"fconst:{int(m.group(1), 16):08x}:ret{retn:x}"
        m = re.match(r"^eax,DWORD PTR ds:0x([0-9a-f]+)$", i.ops)
        if i.mnem == "mov" and m:
            return f"global:{int(m.group(1), 16):08x}:ret{retn:x}"
    return None


_NAME_TINY = [
    (re.compile(r"(?i)Return(True|One|1)(?![0-9])"), lambda t: t.startswith("const:1:")),
    (re.compile(r"(?i)Return(False|Zero|0|Null)(?![0-9])"), lambda t: t.startswith("const:0:")),
    (re.compile(r"(?i)ReturnMinusOne|ReturnNegOne"), lambda t: t.startswith("const:-1:")),
    (re.compile(r"(?i)Return([2-9]|1[0-9])(?![0-9a-f])"), None),
    (re.compile(r"(?i)ReturnThis"), lambda t: t.startswith("this:")),
    (re.compile(r"(?i)NoOp"), lambda t: t.startswith("noop:")),
]


def check_tiny_name(method: str, tiny: str | None) -> str | None:
    """'agree' / 'disagree' when the name states a tiny body's behaviour, else None."""
    if tiny is None:
        return None
    m = re.search(r"(?i)ReturnField([0-9a-f]+)", method)
    if m:
        return "agree" if tiny.startswith(f"field:{int(m.group(1), 16):x}:") else "disagree"
    m = re.search(r"(?i)Return([2-9]|1[0-9])(?![0-9a-f])", method)
    if m:
        return "agree" if tiny.startswith(f"const:{int(m.group(1))}:") else "disagree"
    for pat, ok in _NAME_TINY:
        if ok is None:
            continue
        if pat.search(method):
            return "agree" if ok(tiny) else "disagree"
    m = re.search(r"(?i)Ret([0-9a-f]+)$", method)
    if m and tiny.startswith("noop:"):
        return "agree" if tiny == f"noop:ret{int(m.group(1), 16):x}" else "disagree"
    return None


# ---------------------------------------------------------------------------
# 'this' flow: which calls pass the caller's own object in ECX
# ---------------------------------------------------------------------------

_REG32 = ("eax", "ebx", "ecx", "edx", "esi", "edi", "ebp")


def this_calls(prog: "Program", f: Func) -> list[tuple[int, int, int]]:
    """Direct calls/tail jumps made with ECX = the caller's incoming ECX (+ offset).

    Linear, conservative tracking: a register holds THIS+k only after an explicit
    copy from a register known to hold it; any other write clears it; calls clobber
    eax, ecx and edx. Returns (site, target, offset)."""
    held: dict[str, int] = {"ecx": 0}
    out = []
    for ins in prog.body(f):
        mn, ops = ins.mnem, ins.ops
        if mn in ("call", "jmp") and _DIRECT.match(ops):
            if "ecx" in held:
                out.append((ins.va, int(ops, 16), held["ecx"]))
            if mn == "call":
                for r in ("eax", "ecx", "edx"):
                    held.pop(r, None)
            continue
        if mn == "call":
            for r in ("eax", "ecx", "edx"):
                held.pop(r, None)
            continue
        m = re.match(r"^(e[a-z]{2}),(e[a-z]{2})$", ops)
        if mn == "mov" and m and m.group(1) in _REG32 and m.group(2) in _REG32:
            dst, src = m.groups()
            if src in held:
                held[dst] = held[src]
            else:
                held.pop(dst, None)
            continue
        m = re.match(r"^(e[a-z]{2}),\[(e[a-z]{2})(?:\+0x([0-9a-f]+))?\]$", ops)
        if mn == "lea" and m and m.group(1) in _REG32:
            dst, src, k = m.group(1), m.group(2), int(m.group(3) or "0", 16)
            if src in held:
                held[dst] = held[src] + k
            else:
                held.pop(dst, None)
            continue
        # any other instruction writing a tracked register as its first operand
        first = ops.split(",", 1)[0].strip()
        if first in held and mn not in ("cmp", "test", "push"):
            held.pop(first, None)
        if mn == "pop" and ops in held:
            held.pop(ops, None)
        if mn in ("xchg",):
            for r in ops.split(","):
                held.pop(r.strip(), None)
    return out


def ancestors_or_self(prog: "Program", klass: str) -> set[str]:
    return {b for b, _ in prog.bases.get(klass, [])} | {klass}


# ---------------------------------------------------------------------------
# Pinned source index
# ---------------------------------------------------------------------------

_C_STRING = re.compile(r'"((?:[^"\\\n]|\\.)*)"')
# A definition at the start of a line: an optional return type ending in whitespace, '*' or '&', the qualified
# name (constructors and destructors have no return type), the parameters, an optional const and an optional
# constructor initializer list, then the body's brace.
_FUNC_DEF = re.compile(r"^(?P<head>(?:[A-Za-z_][^;{}()\n]*?[\s*&])?)(?P<qual>(?:[A-Za-z_]\w*::)*)(?P<name>~?[A-Za-z_]\w*)"
                       r"\s*\((?P<args>[^;{}]*)\)\s*(?:const\s*)?(?::[^;{]*)?\{", re.M)
_CALL_LIT = re.compile(r"(?P<callee>(?:[A-Za-z_]\w*(?:::|\.|->))*[A-Za-z_]\w*)\s*\(\s*(?P<pre>(?:[^();\"]|\([^();]*\))*?)\"(?P<lit>(?:[^\"\\\n]|\\.)*)\"")


def c_unescape(s: str) -> str:
    return (s.replace("\\\\", "\x00").replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
             .replace('\\"', '"').replace("\\'", "'").replace("\x00", "\\"))


@dataclass
class SourceFunc:
    key: str               # 'Class::Method' or 'Function'
    file: str
    line: int
    body: str
    literals: list[str]
    lit_calls: list[tuple[str, str, int]]   # (callee text, literal, argument index)
    end_line: int = 0      # line of the closing brace
    args: str = ""         # the parameter list as written
    head: str = ""         # what precedes the name: return type, 'static', 'inline', 'virtual'


_COMMENT_OR_LITERAL = re.compile(r"//[^\n]*|/\*.*?\*/|\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'", re.S)


def strip_comments(text: str) -> str:
    """Comments out, line numbers kept. One left-to-right pass, so a '//****' separator is a line comment (not the
    start of a block comment) and comment markers inside string or character literals stay literal."""
    def keep(m: re.Match) -> str:
        t = m.group()
        if t.startswith("//"):
            return ""
        if t.startswith("/*"):
            return "\n" * t.count("\n")
        return t
    return _COMMENT_OR_LITERAL.sub(keep, text)


def index_source(root: Path = SOURCE, patterns: tuple[str, ...] = ("*.cpp",)) -> list[SourceFunc]:
    out = []
    for path in sorted({p for pattern in patterns for p in root.glob(pattern)}):
        text = strip_comments(path.read_text(errors="replace"))
        for m in _FUNC_DEF.finditer(text):
            name = m.group("name")
            if name in ("if", "for", "while", "switch", "return", "sizeof", "catch"):
                continue
            head = m.group("head").strip()
            if head.startswith(("else", "return", "case", "#")):
                continue
            start = m.end()
            depth, j = 1, start
            while j < len(text) and depth:
                c = text[j]
                depth += (c == "{") - (c == "}")
                j += 1
            body = text[start:j - 1]
            key = (m.group("qual") or "") + name
            literals = [c_unescape(x) for x in _C_STRING.findall(body)]
            calls = []
            for cm in _CALL_LIT.finditer(body):
                argidx = cm.group("pre").count(",")
                calls.append((cm.group("callee"), c_unescape(cm.group("lit")), argidx))
            out.append(SourceFunc(key, path.name, text.count("\n", 0, m.start()) + 1, body, literals, calls,
                                  text.count("\n", 0, j - 1) + 1, m.group("args"), head))
    return out


def source_key_to_name(key: str) -> str:
    """'CGame::LoadLevel' -> 'CGame__LoadLevel'; constructors and destructors take the project's ctor/dtor
    ('CThing::CThing' -> 'CThing__ctor', 'CThing::~CThing' -> 'CThing__dtor')."""
    parts = key.split("::")
    if len(parts) >= 2 and parts[-1] == parts[-2]:
        parts[-1] = "ctor"
    elif len(parts) >= 2 and parts[-1] == "~" + parts[-2]:
        parts[-1] = "dtor"
    return "__".join(parts)


# ---------------------------------------------------------------------------
# Conservative header layouts; saved function names are never layout inputs
# ---------------------------------------------------------------------------

@dataclass
class HeaderMethod:
    owner: str
    name: str
    parameters: tuple[str, ...]
    qualifiers: str
    virtual: bool
    file: str
    line: int
    head: str
    body: str | None
    implicit: bool = False

    @property
    def identity(self):
        return ('~dtor' if self.name.startswith('~') else self.name,
                self.parameters, self.qualifiers)


@dataclass
class HeaderClass:
    name: str
    bases: list[str]
    methods: list[HeaderMethod]
    issues: list[str]
    file: str
    line: int


def _header_conditions(text: str, undefined: set[str]) -> tuple[str, list[tuple[int, int]]]:
    """Exclude explicit off branches; mark unknown branches instead of choosing one.

    This is not a preprocessor. Includes/macros are not expanded. A conventional
    outer include guard is admitted; other unresolved directives stay visible.
    Unknown data-only conditionals do not change the virtual method list.
    """
    guard = re.match(r'\s*#\s*ifndef\s+(\w+)\s*\n\s*#\s*define\s+\1\b', text)
    guard_name = guard.group(1) if guard else None
    known = {name: False for name in undefined}
    if guard_name:
        known[guard_name] = False
    stack, active, out, uncertain, pos = [], True, [], [], 0
    both = lambda a, b: False if a is False or b is False else None if a is None or b is None else True
    for line in text.splitlines(keepends=True):
        directive = re.match(r'\s*#\s*(\w+)\b(.*)', line)
        if directive:
            op, arg = directive.group(1), directive.group(2).strip()
            if op in ('if', 'ifdef', 'ifndef'):
                cond = None
                if op in ('ifdef', 'ifndef') and arg in known:
                    cond = known[arg] if op == 'ifdef' else not known[arg]
                elif op == 'if' and arg in ('0', '1'):
                    cond = arg == '1'
                stack.append((active, cond))
                active = both(active, cond)
            elif op in ('else', 'elif') and stack:
                parent, previous = stack[-1]
                cond = not previous if op == 'else' and previous is not None else None
                # After an elif we cannot select later alternatives confidently.
                stack[-1] = (parent, None if op == 'elif' else previous)
                active = both(parent, cond)
            elif op == 'endif' and stack:
                active, _ = stack.pop()
            elif op in ('define', 'undef') and active is not False:
                macro = re.match(r'\w+', arg)
                if macro:
                    if active is True:
                        known[macro.group()] = op == 'define'
                    else:
                        known.pop(macro.group(), None)
            out.append(''.join('\n' if c == '\n' else ' ' for c in line))
        elif active is False:
            out.append(''.join('\n' if c == '\n' else ' ' for c in line))
        else:
            out.append(line)
            if active is None:
                uncertain.append((pos, pos + len(line)))
        pos += len(line)
    return ''.join(out), uncertain


def _header_type(parameter: str) -> str | None:
    """Conservative type spelling; unsupported declarators remain unresolved."""
    parameter = parameter.split('=', 1)[0].strip()
    if any(c in parameter for c in '()[]') or '...' in parameter:
        return None
    m = re.search(r'\b[A-Za-z_]\w*$', parameter)
    if m:
        prefix = parameter[:m.start()].strip()
        qualifiers = {'const', 'volatile', 'signed', 'unsigned', 'long', 'short', 'struct', 'class', 'enum'}
        integer_words = {'signed', 'unsigned', 'long', 'short'}
        if prefix and not prefix.endswith('::') and (('*' in prefix or '&' in prefix)
                or any(word not in qualifiers for word in prefix.split())
                or (set(prefix.split()) <= integer_words and m.group() not in integer_words | {'int', 'char', '__int64'})):
            parameter = prefix
    parameter = re.sub(r'\b(class|struct|enum)\s+', '', parameter)
    if '*' not in parameter and '&' not in parameter:
        parameter = re.sub(r'\b(const|volatile)\b', '', parameter)
    return re.sub(r'\s+', '', parameter)


def header_classes(root: Path, undefined: set[str]) -> dict[str, HeaderClass]:
    """Partial declarations sufficient for unambiguous single-inheritance layouts.

    Missing bases/macros, unknown conditional methods, operators, templates and
    complex declarators withhold the affected layout. No saved name supplies a
    missing declaration. Method bodies are retained only as private witnesses.
    """
    import re_source_graph as G
    classes = {}
    headers = sorted(root.glob('*.h'))
    texts = {path: strip_comments(path.read_text(errors='replace')) for path in headers}
    macro_names = {name for text in texts.values()
                   for name in re.findall(r'^\s*#\s*define\s+(\w+)', text, re.M)}
    start_re = re.compile(r'\b(?:class|struct)\s+(?P<name>\w+)(?:\s+final)?\s*'
                          r'(?::(?P<bases>[^;{}()]*))?\{'
                          r'|\b(?P<macro>DECLARE_\w+)\s*\((?P<macroargs>[^()]+)\)')
    literal_re = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', re.S)
    for path in headers:
        text, uncertain = _header_conditions(texts[path], undefined)
        masked = literal_re.sub(lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), text)
        for cm in start_re.finditer(masked):
            macro = cm.group('macro')
            parts = [p.strip() for p in cm.group('macroargs').split(',')] if macro else []
            name = parts[0] if macro else cm.group('name')
            raw_bases = parts[1:] if macro else (cm.group('bases') or '').split(',')
            bases = [re.sub(r'\b(public|protected|private|virtual)\b', '', b).strip() for b in raw_bases if b.strip()]
            issues = [f'unexpanded class macro {macro}'] if macro else []
            if 'virtual' in (cm.group('bases') or '').split():
                issues.append('virtual inheritance')
            if len(bases) > 1:
                issues.append('multiple inheritance')
            if any('<' in b for b in bases) or '<' in masked[max(0, cm.start()-30):cm.start()].split(';')[-1]:
                issues.append('template context')
            if any(lo < cm.end() and hi > cm.start() for lo, hi in uncertain):
                issues.append('conditional class declaration')
            depth, end = 1, cm.end()
            while end < len(masked) and depth:
                depth += (masked[end] == '{') - (masked[end] == '}')
                end += 1
            if depth:
                issues.append('unterminated class')
            methods, cursor, i = [], cm.end(), cm.end()
            while i < end - 1:
                if masked[i] not in ';{':
                    i += 1
                    continue
                declaration_end = i
                declaration = masked[cursor:i].strip()
                declaration = re.sub(r'\b(public|protected|private)\s*:', '', declaration).strip()
                if re.search(r'\btemplate\s*<', declaration):
                    issues.append('member template declaration')
                body, after = None, i + 1
                if masked[i] == '{':
                    n = 1
                    while after < end and n:
                        n += (masked[after] == '{') - (masked[after] == '}')
                        after += 1
                    body = text[i+1:after-1]
                if re.match(re.escape(name)+r'\s*\(', declaration):
                    declaration = re.sub(r'\)\s*:(?!:).*$', ')', declaration, flags=re.S)
                method = re.fullmatch(r'(?P<head>[\w:\s*&<>]*?)(?<!\w)(?P<name>~?\w+)\s*'
                                      r'\((?P<args>[^()]*)\)\s*(?P<cv>(?:(?:const|volatile)\s*)*)'
                                      r'(?:override\s*|final\s*)*(?:=\s*0\s*)?', declaration)
                if method:
                    head, method_name = method.group('head').strip(), method.group('name')
                    params = tuple(_header_type(p) for p in G.params(method.group('args')))
                    if None in params:
                        issues.append(f'unsupported parameters for {method_name}')
                    elif not head and method_name not in (name, '~'+name):
                        issues.append(f'possible member macro {method_name}')
                    else:
                        if method_name in macro_names:
                            issues.append(f'unexpanded method-name macro {method_name}')
                        if any(lo < declaration_end and hi > cursor for lo, hi in uncertain):
                            issues.append(f'conditional method {method_name}')
                        name_site = re.search(re.escape(method_name)+r'\s*\(', masked[cursor:declaration_end])
                        methods.append(HeaderMethod(name, method_name, params,
                            ' '.join(method.group('cv').split()), 'virtual' in head.split(),
                            path.name, text.count('\n', 0, cursor+name_site.start())+1, head, body))
                elif 'virtual' in declaration.split() or '(' in declaration:
                    issues.append('unparsed method declaration: '+declaration[:100])
                elif re.match(r'(class|struct|enum)\b', declaration) and body is not None:
                    issues.append('nested type declaration')
                cursor, i = after, after
            item = HeaderClass(name, bases, methods, issues, path.name, text.count('\n', 0, cm.start())+1)
            if name in classes:
                classes[name].issues.append('multiple class definitions')
            else:
                classes[name] = item
    return classes


def header_layouts(classes: dict[str, HeaderClass]) -> tuple[dict[str, list[HeaderMethod]], dict[str, list[str]]]:
    layouts, issues, visiting = {}, {}, set()

    def build(name):
        if name in layouts or name in issues:
            return
        if name not in classes or name in visiting:
            issues[name] = ['missing base declaration' if name not in classes else 'inheritance cycle']
            return
        visiting.add(name)
        cls = classes[name]
        why = list(cls.issues)
        slots = []
        for base in cls.bases:
            build(base)
            if base in issues:
                why.append(f'unresolved base {base}')
            else:
                slots.extend(layouts[base])
        new, declared = [], set()
        for method in cls.methods:
            if method.name == cls.name:
                continue  # constructors cannot override a same-named base method
            if method.identity in declared:
                why.append(f'duplicate method {method.name}')
            declared.add(method.identity)
            match = next((i for i, old in enumerate(slots) if old.identity == method.identity), None)
            if match is not None:
                slots[match] = method
            elif method.virtual:
                new.append(method)
        # Do not assume a compiler-family overload permutation proves VC6's
        # exact order. The initial admitted families have no such new groups.
        if len({m.name for m in new}) != len(new):
            why.append('new virtual overload ordering requires byte witnesses')
        first_declaration = {}
        for position, method in enumerate(cls.methods):
            first_declaration.setdefault(method.name, position)
        if new != sorted(new, key=lambda m: first_declaration[m.name]):
            why.append('earlier nonvirtual/override declaration changes new virtual group order')
        slots.extend(new)
        if not any(m.name.startswith('~') for m in cls.methods):
            slots = [replace(m, owner=name, name='~'+name, implicit=True, file=cls.file, line=cls.line, body=None)
                     if m.name.startswith('~') else m for m in slots]
        if why:
            issues[name] = sorted(set(why))
        else:
            layouts[name] = slots
        visiting.remove(name)

    for name in classes:
        build(name)
    return layouts, issues


def align_header_vtables(prog: Program, classes: dict[str, HeaderClass]) -> dict:
    """Produce review candidates, never promotions or verified method identities."""
    layouts, unresolved = header_layouts(classes)
    primary = defaultdict(list)
    for table in prog.model.rtti.vtables:
        if table.offset == 0:
            primary[table.klass].append(table)
    rows, withheld, admission = [], [], {}

    def admit(name):
        if name in admission:
            return admission[name]
        if name not in layouts:
            admission[name] = unresolved.get(name, ['no parsed header'])
            return admission[name]
        tables = primary.get(name, [])
        layout = layouts[name]
        why = []
        if len(tables) != 1:
            why.append('missing or multiple primary tables')
        if any(len(t.slots) != len(layout) for t in tables):
            why.append(f'source has {len(layout)} slots; retail has {[len(t.slots) for t in tables]}')
        source_ancestors, todo = set(), list(classes[name].bases)
        while todo:
            base = todo.pop()
            if base not in source_ancestors:
                source_ancestors.add(base)
                todo.extend(classes[base].bases)
        retail_ancestors = {base for base, _ in prog.bases.get(name, []) if base != name}
        if source_ancestors != retail_ancestors:
            why.append('source and retail ancestor sets differ')
        retail_rows = prog.bases.get(name, [])
        expected_rows = {(name, 0)} | {(base, 0) for base in source_ancestors}
        if set(retail_rows) != expected_rows or len(retail_rows) != len(expected_rows):
            why.append('retail subobject offsets/multiplicity exceed the single primary chain')
        for base in classes[name].bases:
            if (base, 0) not in prog.fixed_bases.get(name, []):
                why.append(f'RTTI does not establish fixed primary base {base}')
            if admit(base):
                why.append(f'base layout not admitted: {base}')
        admission[name] = why
        return why

    for name, tables in sorted(primary.items()):
        why = admit(name)
        if why:
            withheld.append({'class': name, 'reasons': why})
            continue
        table = tables[0]
        for slot, (method, target) in enumerate(zip(layouts[name], table.slots)):
            row = {'class': name, 'table': f'0x{table.va:08x}', 'slot': slot,
                   'target': f'0x{target:08x}', 'source': method.owner+'::'+method.name,
                   'parameters': list(method.parameters), 'qualifiers': method.qualifiers,
                   'file': method.file, 'line': method.line, 'implicit': method.implicit,
                   'status': 'header-slot-candidate'}
            # Exact inheritance must preserve the address in this simple ABI
            # case. A mismatch is source drift or incomplete analysis, not a rename.
            if method.owner != name and len(primary.get(method.owner, [])) == 1:
                owner_table = primary[method.owner][0]
                if slot >= len(owner_table.slots) or owner_table.slots[slot] != target:
                    row['status'] = 'inherited-target-discrepancy'
            if target not in prog.by_va:
                row['status'] = 'missing-function-boundary'
            rows.append(row)
    return {'rows': rows, 'withheld': withheld,
            'limits': 'Header-slot candidates only. No saved name is an input. Partial parser, '
                      'single fixed primary inheritance, unresolved macros/conditionals/overload order withheld. '
                      'Matching counts do not prove source version or semantics; rederive byte witnesses before promotion.'}


def guarded_event_interface_witness(prog: Program, cls: HeaderClass, method: HeaderMethod,
                                    seed: Vtable, anchor: dict, source_root: Path | None) -> tuple[Vtable, int]:
    """One reviewed event-interface witness, without inventing the absent headers.

    The two queue callers transport the event pointer to a recipient's slot 0.
    Exact guarded transport is checked independently of supplied hashes. RTTI
    establishes a unique fixed primary path, allowing unrelated secondary bases.
    This proves an interface identity/stack footprint, not handler behavior or
    saved prototype types. EBP preservation across callbacks uses the x86 ABI.
    """
    witness = anchor['interfaceDispatch']
    if (source_root is None or method.name != 'HandleEvent' or method.parameters != ('CEvent*',)
            or not method.virtual or method.qualifiers or method.head.split() != ['virtual', 'void']
            or (anchor.get('sourceFile'), anchor.get('sourceLine')) != (method.file, method.line)
            or anchor['slot'] != 0 or seed.offset != 0
            or not witness.get('evidence') or not witness.get('receiverEvidence')):
        raise ValueError('guarded-event declaration or reviewed evidence mismatch')
    tables = prog.model.rtti.vtables
    chain = witness['primaryChain']
    if (len(chain) < 2 or len(set(chain)) != len(chain) or chain[0] != cls.name
            or chain[-1] != 'IListener' or not cls.bases or cls.bases[0] != chain[1]):
        raise ValueError('guarded-event primary source/RTTI path mismatch')
    selected, previous_length = [], None
    for index, name in enumerate(chain):
        raw, fixed = prog.bases.get(name, []), prog.fixed_bases.get(name, [])
        primary = [t for t in tables if t.klass == name and t.offset == 0]
        # Repeated ancestors, virtual PMDs and a different zero-offset path
        # cannot silently borrow a slot from this interface.
        if (raw != fixed or len({c for c, _ in raw}) != len(raw)
                or [c for c, offset in raw if offset == 0] != chain[index:]
                or any(offset < 0 for _, offset in raw) or len(primary) != 1
                or not primary[0].slots
                or previous_length is not None and len(primary[0].slots) > previous_length):
            raise ValueError('guarded-event primary ancestry is not unique and fixed')
        selected.append(primary[0]); previous_length = len(primary[0].slots)
    if (selected[0] != seed or len(selected[-1].slots) != 1
            or int(witness['table'], 16) != selected[-1].va or witness['class'] != 'IListener'):
        raise ValueError('guarded-event selected table mismatch')
    for base in cls.bases[1:]:
        matches = [offset for name, offset in prog.fixed_bases[cls.name] if name == base]
        if len(matches) != 1 or matches[0] <= 0:
            raise ValueError('guarded-event secondary source base is not separate')

    source = witness['source']
    if Path(source['file']).name != source['file']:
        raise ValueError('guarded-event source path is not bounded')
    path = source_root / source['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('guarded-event source hash mismatch')
    functions = [f for f in index_source(source_root, (source['file'],)) if f.key == source['function']]
    if len(functions) != 1:
        raise ValueError('guarded-event source caller is absent or ambiguous')
    lines = strip_comments(path.read_text(errors='replace')).splitlines()
    calls = source['calls']
    if len(calls) != 2 or len({r['line'] for r in calls}) != 2:
        raise ValueError('guarded-event needs two distinct source dispatches')
    for record in calls:
        line, receiver = record['line'], record['receiverLine']
        if (type(line) is not int or type(receiver) is not int
                or not functions[0].line <= receiver < line <= functions[0].end_line
                or re.sub(r'\s+', '', lines[line-1]) != 'to_call->HandleEvent(next_event);'
                or re.sub(r'\s+', '', lines[receiver-1]) != 'IListener*to_call=next_event->GetToCall();'):
            raise ValueError('guarded-event source call/receiver mismatch')
    if not witness.get('receiverSources'):
        raise ValueError('guarded-event receiver source witnesses missing')
    for record in witness['receiverSources']:
        if Path(record['file']).name != record['file'] or not record.get('evidence'):
            raise ValueError('guarded-event receiver source path/evidence missing')
        if hashlib.sha256((source_root/record['file']).read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('guarded-event receiver source hash mismatch')

    def span(record):
        start, size = int(record['address'], 16), record['bytes']
        if type(size) is not int or size <= 0:
            raise ValueError('guarded-event invalid byte span')
        raw = prog.img.read(start, size)
        if len(raw) != size or hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('guarded-event span hash mismatch')
        return start, start+size, raw

    start, end, _ = span(witness['caller'])
    fn = prog.by_va.get(start)
    if (fn is None or fn.lo != start or fn.hi+1 != end
            or getattr(fn, 'body_ranges', 1) != 1
            or getattr(fn, 'declared_hi', fn.hi) not in (None, fn.hi)
            or getattr(fn, 'body_bytes', end-start) not in (None, end-start)):
        raise ValueError('guarded-event caller boundary mismatch')
    body = prog.body(fn); cursor = start
    for ins in body:
        if ins.va != cursor or ins.size <= 0 or ins.mnem in ('(bad)', '.byte', '.word', '.long'):
            raise ValueError('guarded-event incomplete caller decoding')
        cursor += ins.size
    if cursor != end:
        raise ValueError('guarded-event caller decoding extent mismatch')
    windows = witness['windows']
    # Each shape includes the receiver load, reuse write, comparison and exact
    # skip-to-after-call branch, as well as the vptr load and event push.
    shapes = (bytes.fromhex('8b08 66896808 3bcd 7405 8b11 50 ff12'),
              bytes.fromhex('8b0a 66896a08 8b4624 40 3bcd 894624 7405 8b01 52 ff10'))
    if len(windows) != len(shapes):
        raise ValueError('guarded-event needs both queue transports')
    ranges = []
    starts = {i.va for i in body}
    for ins in body:
        if ins.mnem.startswith(('j', 'loop')):
            if not _DIRECT.fullmatch(ins.ops) or int(ins.ops,16) not in starts:
                raise ValueError('guarded-event unresolved or nonlocal branch target')
    for record, expected in zip(windows, shapes):
        lo, hi, raw = span(record)
        if raw != expected or not start <= lo < hi < end or lo not in starts or hi not in starts:
            raise ValueError('guarded-event transport shape mismatch')
        if ranges and lo < ranges[-1][1]:
            raise ValueError('guarded-event transports overlap or are out of order')
        ranges.append((lo, hi))
        for ins in body:
            if ins.mnem.startswith(('j', 'loop')) and _DIRECT.fullmatch(ins.ops):
                if lo < int(ins.ops, 16) < hi:
                    raise ValueError('guarded-event branch bypasses receiver transport')
    zero = int(witness['zeroRegisterAt'], 16)
    prefix = [i for i in body if i.va <= zero]
    if (not prefix or prefix[-1].va != zero or prefix[-1].mnem != 'xor'
            or prefix[-1].ops != 'ebp,ebp' or prog.img.read(zero, 2) != b'\x33\xed'
            or zero+2 > ranges[0][0]
            or any(i.mnem.startswith(('j', 'loop')) or i.mnem in ('call','ret') for i in prefix)):
        raise ValueError('guarded-event null-register initialization is not dominant')
    for ins in body:
        if not zero < ins.va < ranges[-1][1]:
            continue
        # A closed vocabulary avoids implicit/two-destination register writes
        # such as XADD's second operand or POPA's restored EBP. Calls preserve
        # EBP under the stated x86 ABI; this says nothing about exceptions.
        if ins.mnem not in {'mov','lea','shl','cmp','test','add','sub','inc','dec','xor',
                            'push','call','fld','fcomp','fnstsw','nop','je','jne','jmp','jle'}:
            raise ValueError('guarded-event unsupported null-register transport')
        if ((ins.ops.split(',')[0] in ('ebp','bp') and ins.mnem not in ('cmp','test','push'))
                or ins.mnem in ('enter','leave','popa','popad')):
            raise ValueError('guarded-event null-register clobber')
    literal = witness['callerLiteral']
    text = literal['text'].encode('ascii')+b'\0'; va = int(literal['address'],16)
    site = int(literal['site'],16)
    literal_ins = next((ins for ins in body if ins.va == site), None)
    if (prog.img.read(va,len(text)) != text or prog.img.data.count(text) != 1
            or literal['text'] not in functions[0].literals or not start <= site < site+5 <= end
            or literal_ins is None or literal_ins.size != 5 or literal_ins.mnem != 'push'
            or literal_ins.ops != hex(va)
            or prog.img.read(site,5) != b'\x68'+struct.pack('<I',va)):
        raise ValueError('guarded-event unique caller literal mismatch')
    return selected[-1], 4


def possible_interior_entry(prog: Program, start: int, end: int) -> bool:
    """Conservatively include raw pointers omitted by the instruction cache."""
    if not getattr(prog.img, 'sections', None):
        raise ValueError('interior-entry check needs the complete image sections')
    for target, refs in prog.model.refs_to.items():
        if start < target < end and any(kind in ('call', 'jmp', 'jcc', 'imm', 'mem')
                and not start <= site < end for kind, site in refs):
            return True
    if any(start < target < end for target in getattr(prog.model, 'data_ptrs_to', {})):
        return True
    return any(struct.pack('<I', target) in section.raw
               for target in range(start+1, end)
               for section in prog.img.sections)


def aggregate_copy_leaf(prog: Program, fn: Func, result_bytes: int) -> dict:
    """Recognize an entire straight-line member copy into a hidden result pointer.

    This proves a narrow normal-entry transport, not a source method identity or
    a global aggregate ABI. REP MOVSD assumes the normal clear direction flag.
    Valid result storage must not overlap the callee's saved stack/return words.
    Source and result spans must be valid, nonwrapping storage. Before-image
    semantics additionally require them not to overlap. Code must be unchanged.
    A separate source/caller witness
    must establish why this buffer is a return.
    Nothing here admits a RET-only stub, forwarder, arbitrary call or branch.
    """
    if type(result_bytes) is not int or not 4 <= result_bytes <= 256 or result_bytes % 4:
        raise ValueError('aggregate copy extent is not bounded DWORD storage')
    if (fn.lo != fn.va or fn.body_ranges != 1 or fn.declared_hi not in (None, fn.hi)
            or fn.body_bytes not in (None, fn.hi-fn.va+1)):
        raise ValueError('aggregate copy boundary is incomplete')
    if any(other.va != fn.va and other.lo <= fn.hi
           and (other.declared_hi or other.hi) >= fn.lo for other in prog.funcs):
        raise ValueError('aggregate copy has overlapping function ownership')
    if possible_interior_entry(prog, fn.va, fn.hi+1):
        raise ValueError('aggregate copy has a possible interior entry')
    body = decode_entry_body(prog.img, fn)
    pointer = lambda region, offset=0: ('pointer', region, offset)
    initial = {r: ('entry-register', r) for r in ('eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp')}
    regs = dict(initial, ecx=pointer('this'), esp=pointer('stack'))
    stack = {0: ('return-address',), 4: pointer('result')}
    owned_stack, writes, reads, pops, used_rep = set(), {}, set(), 0, False

    def member(offset):
        if not 0 <= offset <= 0x7ffffffc:
            raise ValueError('aggregate copy reads outside a forward member extent')
        reads.add(offset)
        return ('member-word', offset)

    def address(operand):
        match = re.fullmatch(r'\[(e(?:ax|bx|cx|dx|si|di|bp|sp))(?:([+-])0x([0-9a-f]+))?\]', operand)
        if not match or regs[match[1]][0] != 'pointer':
            raise ValueError('aggregate copy has an unproved address')
        value = regs[match[1]]
        offset = int(match[3] or '0', 16) * (-1 if match[2] == '-' else 1)
        return pointer(value[1], value[2] + offset)

    def read(operand):
        if operand in regs:
            return regs[operand]
        if re.fullmatch(r'0x[0-9a-f]+', operand):
            return ('constant', int(operand, 16))
        if operand.startswith('DWORD PTR '):
            _, region, offset = address(operand[10:])
            if region == 'stack' and offset in stack:
                return stack[offset]
            if region == 'this':
                return member(offset)
        raise ValueError('aggregate copy reads an unproved value')

    def store(destination, value):
        _, region, offset = destination
        if (region != 'result' or offset < 0 or offset % 4
                or offset >= result_bytes or offset in writes or value[0] != 'member-word'):
            raise ValueError('aggregate copy writes outside its exact result')
        writes[offset] = value[1]

    for index, ins in enumerate(body):
        if ins.mnem == 'ret':
            if index != len(body)-1 or ins.ops != '0x4':
                raise ValueError('aggregate copy has wrong return cleanup')
            pops += 1
        elif ins.mnem == 'mov':
            dest, sep, value = ins.ops.partition(',')
            if not sep:
                raise ValueError('aggregate copy has an invalid move')
            if dest in regs and dest != 'esp':
                regs[dest] = read(value)
            elif dest.startswith('DWORD PTR '):
                store(address(dest[10:]), read(value))
            else:
                raise ValueError('aggregate copy has an unsupported move')
        elif ins.mnem == 'lea':
            dest, sep, value = ins.ops.partition(',')
            if not sep or dest not in regs or dest == 'esp':
                raise ValueError('aggregate copy has an unsupported address load')
            regs[dest] = address(value)
        elif ins.mnem == 'add':
            dest, sep, value = ins.ops.partition(',')
            if (not sep or dest not in regs or dest == 'esp' or regs[dest][0] != 'pointer'
                    or not re.fullmatch(r'0x[0-9a-f]+', value)
                    or int(value, 16) > 0x7fffffff):
                raise ValueError('aggregate copy has unsupported pointer arithmetic')
            prior = regs[dest]
            regs[dest] = pointer(prior[1], prior[2]+int(value, 16))
        elif ins.mnem == 'push' and ins.ops in ('ebx', 'esi', 'edi', 'ebp'):
            offset = regs['esp'][2]-4
            stack[offset] = regs[ins.ops]
            owned_stack.add(offset)
            regs['esp'] = pointer('stack', offset)
        elif ins.mnem == 'pop' and ins.ops in ('ebx', 'esi', 'edi', 'ebp'):
            offset = regs['esp'][2]
            if offset not in owned_stack:
                raise ValueError('aggregate copy has unmatched register restoration')
            regs[ins.ops] = stack.pop(offset)
            owned_stack.remove(offset)
            regs['esp'] = pointer('stack', offset+4)
        elif ins.mnem == 'rep' and ins.ops == 'movs DWORD PTR es:[edi],DWORD PTR ds:[esi]':
            count, source, dest = regs['ecx'], regs['esi'], regs['edi']
            if (count[0] != 'constant' or not 1 <= count[1] <= 64
                    or source[:2] != ('pointer', 'this') or dest[:2] != ('pointer', 'result')):
                raise ValueError('aggregate copy has an unproved string transfer')
            for n in range(count[1]):
                store(pointer('result', dest[2]+4*n), member(source[2]+4*n))
            regs['esi'], regs['edi'] = pointer('this', source[2]+4*count[1]), pointer('result', dest[2]+4*count[1])
            regs['ecx'], used_rep = ('constant', 0), True
        else:
            raise ValueError('aggregate copy is not a supported complete leaf')
    if (pops != 1 or owned_stack or regs['esp'] != pointer('stack')
            or regs['eax'] != pointer('result')
            or any(regs[r] != initial[r] for r in ('ebx', 'esi', 'edi', 'ebp'))
            or set(writes) != set(range(0, result_bytes, 4))):
        raise ValueError('aggregate copy does not preserve its exact result/stack contract')
    first = writes[0]
    if (any(writes[n] != first+n for n in writes)
            or reads != set(range(first, first+result_bytes, 4))
            or not 0 <= first <= 0x80000000-result_bytes):
        raise ValueError('aggregate copy is not a contiguous member result')
    return {'address': f'0x{fn.va:08x}', 'bytes': fn.hi-fn.va+1,
            'bodySha256': hashlib.sha256(prog.img.read(fn.va, fn.hi-fn.va+1)).hexdigest(),
            'resultBytes': result_bytes, 'memberOffset': first, 'returnPop': 4,
            'eax': 'result destination', 'directionFlagClearRequired': used_rep}


def aggregate_interface_witness(prog: Program, cls: HeaderClass, method: HeaderMethod,
                                seed: Vtable, anchor: dict, source_root: Path | None) -> tuple[Vtable, int]:
    """Bind one reviewed source aggregate call to a concrete result-copy leaf.

    The receiver is a nonvolatile register loaded from the first stack argument.
    The call pushes an ESP-relative address, preserves that receiver in ECX and
    dispatches the selected slot. The reviewed caller must supply a valid result
    span. Its full frame lifetime and intervening callees' cleanup are not proved
    here. Valid objects must not alias the local stack; callees must obey the
    nonvolatile-register convention. These premises do not certify full caller/
    callee behavior or exception paths. This is a local interface witness only.
    """
    witness = anchor['interfaceDispatch']
    tables = {t.va: t for t in prog.model.rtti.vtables}
    base = tables.get(int(witness['table'], 16))
    if (base is None or base.klass != witness['class'] or base.offset != 0 or seed.offset != 0
            or cls.bases != [base.klass] or not method.virtual
            or prog.fixed_bases.get(cls.name) != [(cls.name, 0), (base.klass, 0)]
            or prog.bases.get(cls.name) != [(cls.name, 0), (base.klass, 0)]
            or len(seed.slots) != len(base.slots)):
        raise ValueError('aggregate interface is not a fixed direct primary base')
    if ((anchor.get('sourceFile'), anchor.get('sourceLine')) != (method.file, method.line)
            or method.parameters or not witness.get('evidence') or not witness.get('receiverEvidence')):
        raise ValueError('aggregate declaration/evidence does not match the zero-parameter interface')
    result_type = witness['resultType']
    if (not re.fullmatch(r'[A-Za-z_]\w*', result_type)
            or re.sub(r'\bvirtual\b', '', method.head).strip() != result_type):
        raise ValueError('aggregate return spelling disagrees with the declaration')
    import re_source_graph as G
    sf = SourceFunc(method.owner+'::'+method.name, method.file, method.line, '', [], [],
                    args='', head=method.head)
    if G.expected_pop(G.Source({}, set(), set()), sf) is not None or not witness.get('resultTypeEvidence'):
        raise ValueError('aggregate witness contradicts a scalar return or lacks reviewed type evidence')
    source = witness['source']
    if source_root is None or Path(source['file']).name != source['file']:
        raise ValueError('aggregate caller source is not a bounded file')
    path = source_root/source['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('aggregate caller source hash mismatch')
    functions = [f for f in index_source(source_root, (source['file'],)) if f.key == source['function']]
    line = source['line']
    if (len(functions) != 1 or type(line) is not int
            or not functions[0].line <= line <= functions[0].end_line):
        raise ValueError('aggregate source caller is absent or ambiguous')
    source_text = strip_comments(path.read_text(errors='replace'))
    active, conditional = _header_conditions(source_text, set())
    start_offset = sum(len(s) for s in source_text.splitlines(keepends=True)[:functions[0].line-1])
    end_offset = sum(len(s) for s in source_text.splitlines(keepends=True)[:functions[0].end_line])
    if (active[start_offset:end_offset] != source_text[start_offset:end_offset]
            or any(lo < end_offset and hi > start_offset for lo,hi in conditional)):
        raise ValueError('aggregate caller source contains unresolved conditions')
    actual = source_text.splitlines()[line-1].strip()
    pattern = re.escape(result_type) + r'\s+[A-Za-z_]\w*\s*=\s*([A-Za-z_]\w*)->' + re.escape(method.name) + r'\(\);'
    match = re.fullmatch(pattern, actual)
    if not match or actual != source['call']:
        raise ValueError('aggregate source call does not match its declaration')
    # This reviewed caller shape uses precisely one pointer argument. It is not
    # a rule permitting arbitrary expressions or inferred receiver ownership.
    if not re.fullmatch(re.escape(base.klass)+r'\s*\*\s*'+re.escape(match[1]), functions[0].args.strip()):
        raise ValueError('aggregate source receiver is not the unique interface pointer argument')

    def body(record):
        address, size = int(record['address'], 16), record['bytes']
        fn = prog.by_va.get(address)
        if (type(size) is not int or fn is None or size != fn.hi+1-address
                or fn.lo != address or fn.body_ranges != 1
                or fn.declared_hi not in (None, fn.hi) or fn.body_bytes not in (None, size)
                or any(other.va != fn.va and other.lo <= fn.hi
                       and (other.declared_hi or other.hi) >= fn.lo for other in prog.funcs)
                or hashlib.sha256(prog.img.read(address, size)).hexdigest() != record['sha256']):
            raise ValueError('aggregate witness body identity mismatch')
        return fn, decode_entry_body(prog.img, fn)

    caller, instructions = body(witness['caller'])
    receiver = witness['receiverRegister']
    if receiver not in ('ebx', 'esi', 'edi', 'ebp'):
        raise ValueError('aggregate receiver must survive intervening normal calls')
    load_va, start, call_va = (int(witness[k], 16) for k in ('receiverLoad', 'windowStart', 'callAddress'))
    by_va = {i.va: i for i in instructions}
    if not caller.va <= load_va < start <= call_va <= caller.hi or any(a not in by_va for a in (load_va, start, call_va)):
        raise ValueError('aggregate caller witness boundaries mismatch')
    protected_end = call_va+by_va[call_va].size
    # Only entry through this call establishes the witness. Later entries do
    # not bypass it unless a local transfer can return to the protected prefix.
    if (possible_interior_entry(prog, caller.va, protected_end)
            or any((i.mnem.startswith(('j','loop')) or i.mnem=='call')
                   and _DIRECT.fullmatch(i.ops) and caller.va < int(i.ops,16) < protected_end
                   or i.mnem.startswith(('j','loop')) and not _DIRECT.fullmatch(i.ops)
                   for i in instructions)):
        raise ValueError('aggregate caller has a possible interior entry')
    stack_offset = 0
    object_regs = {'ecx'}
    aliases = {part: full for full, parts in {
        'eax': ('eax','ax','ah','al'), 'ebx': ('ebx','bx','bh','bl'),
        'ecx': ('ecx','cx','ch','cl'), 'edx': ('edx','dx','dh','dl'),
        'esi': ('esi','si'), 'edi': ('edi','di'), 'ebp': ('ebp','bp'),
        'esp': ('esp','sp')}.items() for part in parts}
    for ins in instructions:
        if ins.va >= load_va:
            break
        dest, _, value = ins.ops.partition(',')
        if ins.mnem == 'mov' and dest in ('eax','ebx','ecx','edx','esi','edi','ebp'):
            if value in object_regs:
                object_regs.add(dest)
            else:
                object_regs.discard(dest)
        elif aliases.get(dest) in object_regs and ins.mnem not in ('push','cmp','test'):
            object_regs.discard(aliases[dest])
        if ins.mnem == 'push':
            if (prog.img.read(ins.va,1) == b'\x66'
                    or not (dest in ('eax','ebx','ecx','edx','esi','edi','ebp')
                            or re.fullmatch(r'0x[0-9a-f]+', dest))):
                raise ValueError('aggregate receiver prefix has an unsupported push width')
            stack_offset -= 4
        elif ins.mnem in ('add', 'sub') and re.fullmatch(r'esp,0x[0-9a-f]+', ins.ops):
            value = int(ins.ops.split(',')[1], 16)
            if value > 0x10000:
                raise ValueError('aggregate receiver prefix has unbounded stack adjustment')
            stack_offset += value if ins.mnem == 'add' else -value
        elif (ins.mnem in ('call', 'ret', 'pop') or ins.mnem.startswith(('j', 'loop'))
              or ins.mnem not in ('mov','lea','nop')
              or aliases.get(dest) == 'esp'):
            raise ValueError('aggregate receiver prefix has opaque stack/control flow')
        if ins.mnem == 'mov' and dest.startswith('DWORD PTR '):
            stored = re.fullmatch(r'DWORD PTR \[esp(?:\+0x([0-9a-f]+))?\]', dest)
            if stored:
                if not stack_offset <= stack_offset+int(stored[1] or '0',16) <= -4:
                    raise ValueError('aggregate receiver prefix overwrites entry stack data')
            elif dest != 'DWORD PTR fs:0x0':
                raise ValueError('aggregate receiver prefix has an unproved memory store')
        elif ins.mnem == 'mov' and dest not in aliases:
            raise ValueError('aggregate receiver prefix has an unsupported store width')
    loaded = re.fullmatch(re.escape(receiver)+r',DWORD PTR \[esp\+0x([0-9a-f]+)\]', by_va[load_va].ops)
    if by_va[load_va].mnem != 'mov' or not loaded or stack_offset+int(loaded[1],16) != 4:
        raise ValueError('aggregate receiver is not loaded from entry stack+4')
    object_regs.discard(receiver)
    for ins in instructions:
        if not load_va < ins.va < start:
            continue
        dest, _, value = ins.ops.partition(',')
        if (ins.mnem not in {'mov','lea','call','push','add','sub','cmp','test','nop',
                             'fld','fstp','fsub','fadd','fmul'}
                or aliases.get(dest) == receiver and ins.mnem not in ('cmp', 'test', 'push')):
            raise ValueError('aggregate receiver provenance is interrupted')
        if ins.mnem == 'call':
            object_regs.difference_update(('eax','ecx','edx'))
        elif aliases.get(dest) in object_regs and ins.mnem not in ('push','cmp','test'):
            if not (dest in object_regs and ins.mnem == 'add' and re.fullmatch(r'0x[0-9a-f]+', value)
                    and int(value, 16) < 0x10000):
                object_regs.discard(aliases[dest])
    facts = {receiver: 'receiver'}
    facts.update({r:'caller-object' for r in object_regs})
    registers = {'eax','ebx','ecx','edx','esi','edi','ebp'}
    pushed = []
    for ins in instructions:
        if not start <= ins.va < call_va:
            continue
        dest, _, value = ins.ops.partition(',')
        if ins.mnem == 'lea' and dest in registers and re.fullmatch(r'\[esp\+0x[0-9a-f]+\]', value):
            if not 0 < int(value[7:-1], 16) <= 0x10000-witness['resultBytes']:
                raise ValueError('aggregate result address is not a bounded positive stack displacement')
            facts[dest] = 'stack-relative-result-address'
        elif ins.mnem == 'mov' and dest in registers:
            load = re.fullmatch(r'DWORD PTR \[(e(?:ax|bx|cx|dx|si|di|bp))\]', value)
            facts[dest] = (facts.get(value) if value in registers else
                           'vptr' if load and facts.get(load[1]) == 'receiver' else None)
        elif ins.mnem == 'mov' and (store := re.fullmatch(r'DWORD PTR \[(e(?:bx|si|di|bp))\+0x([0-9a-f]+)\]', dest)) and value in registers:
            # Pinned constructor object stores do not change register/stack
            # transport under the stated valid-object/nonaliasing premise.
            if facts.get(store[1]) != 'caller-object' or int(store[2],16) >= 0x10000:
                raise ValueError('aggregate side store does not use the proven caller object')
        elif ins.mnem == 'push' and ins.ops in registers:
            pushed.append(facts.get(ins.ops))
        else:
            raise ValueError('aggregate argument window has unsupported transport')
    call = by_va[call_va]
    dispatch = re.fullmatch(r'DWORD PTR \[(e(?:ax|bx|cx|dx|si|di|bp))(?:\+0x([0-9a-f]+))?\]', call.ops)
    if (call.mnem != 'call' or not dispatch or facts.get(dispatch[1]) != 'vptr'
            or facts.get('ecx') != 'receiver' or int(dispatch[2] or '0',16) != anchor['slot']*4
            or pushed != ['stack-relative-result-address']):
        raise ValueError('aggregate call does not pass the witnessed destination/receiver/slot')
    leaf, _ = body(anchor['body'])
    proof = aggregate_copy_leaf(prog, leaf, witness['resultBytes'])
    if proof['memberOffset'] != witness['memberOffset']:
        raise ValueError('aggregate source member copy offset mismatch')
    return base, 4


def common_interface_witness(prog: Program, cls: HeaderClass, method: HeaderMethod,
                             seed: Vtable, anchor: dict, source_root: Path | None) -> tuple[Vtable, int]:
    """Bind a reviewed common-interface call to a surviving derived declaration.

    This intentionally supports only a direct, fixed, zero-offset base, equal
    table lengths and straight-line DWORD argument transport. Source/receiver
    correspondence still requires semantic review; pins and instruction checks
    prevent that reviewed witness from silently drifting. No missing header is
    invented, and parameter widths apply only to this witnessed interface.
    """
    import re_source_graph as G
    witness = anchor['interfaceDispatch']
    if witness.get('kind') == 'member-result-buffer':
        return aggregate_interface_witness(prog, cls, method, seed, anchor, source_root)
    if witness.get('kind') == 'guarded-event-primary-prefix':
        return guarded_event_interface_witness(prog, cls, method, seed, anchor, source_root)
    if witness.get('kind') not in (None, 'straight-line'):
        raise ValueError('unknown common-interface witness kind')
    tables = {t.va: t for t in prog.model.rtti.vtables}
    base = tables.get(int(witness['table'], 16))
    if (base is None or base.klass != witness['class'] or base.offset != 0 or seed.offset != 0
            or cls.bases != [base.klass] or not method.virtual
            or prog.bases.get(cls.name) != [(cls.name, 0), (base.klass, 0)]
            or prog.fixed_bases.get(cls.name) != [(cls.name, 0), (base.klass, 0)]
            or len(seed.slots) != len(base.slots)):
        raise ValueError('common-interface base is not a unique fixed direct interface')
    if (anchor.get('sourceFile'), anchor.get('sourceLine')) != (method.file, method.line):
        raise ValueError('common-interface declaration location mismatch')
    if not witness.get('evidence') or not witness.get('receiverEvidence'):
        raise ValueError('common-interface needs reviewed receiver and semantic evidence')

    source = witness['source']
    if source_root is None or Path(source['file']).name != source['file']:
        raise ValueError('common-interface needs a bounded pinned source file')
    path = source_root / source['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('common-interface source file hash mismatch')
    functions = [f for f in index_source(source_root, (source['file'],))
                 if f.key == source['function']]
    line = source['line']
    if (len(functions) != 1 or not isinstance(line, int) or isinstance(line, bool)
            or not functions[0].line <= line <= functions[0].end_line):
        raise ValueError('common-interface source caller is absent or ambiguous')
    actual = strip_comments(path.read_text(errors='replace')).splitlines()[line-1].strip()
    call = re.fullmatch(r'(?:[A-Za-z_]\w*\s*&=\s*)?[A-Za-z_]\w*(?:\[[^\]\n]+\])?->'
                        + re.escape(method.name) + r'\(([^()]*)\);', actual)
    if actual != source['call'] or not call or len(G.params(call[1])) != len(method.parameters):
        raise ValueError('common-interface source call does not match declaration')

    def pinned_span(record):
        address, size = int(record['address'], 16), record['bytes']
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ValueError('common-interface invalid byte span')
        raw = prog.img.read(address, size)
        if len(raw) != size or hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('common-interface byte span hash mismatch')
        return address, address + size

    caller_lo, caller_end = pinned_span(witness['caller'])
    fn = prog.by_va.get(caller_lo)
    if (fn is None or fn.lo != caller_lo or fn.hi+1 != caller_end
            or getattr(fn, 'body_ranges', 1) != 1
            or getattr(fn, 'declared_hi', fn.hi) not in (None, fn.hi)
            or getattr(fn, 'body_bytes', caller_end-caller_lo) not in (None, caller_end-caller_lo)):
        raise ValueError('common-interface caller boundary mismatch')
    start, end = pinned_span(witness['window'])
    if not caller_lo <= start < end <= caller_end:
        raise ValueError('common-interface dispatch window outside caller')
    body = [i for i in prog.body(fn) if start <= i.va < end]
    cursor = start
    for ins in body:
        if ins.va != cursor:
            raise ValueError('common-interface dispatch window decoding gap')
        cursor += ins.size
    if not body or cursor != end or body[-1].va != int(witness['callAddress'], 16):
        raise ValueError('common-interface dispatch window boundary mismatch')
    # Bind every auxiliary receiver witness too; its meaning is independently
    # reviewed, not inferred merely from a correct hash.
    if not witness.get('receiverSpans'):
        raise ValueError('common-interface receiver bindings are absent')
    for span in witness['receiverSpans']:
        pinned_span(span)

    receiver_load = int(witness['receiverLoad'], 16)
    facts, pushes, seen_receiver = {}, 0, False
    registers = {'eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp'}
    for ins in body[:-1]:
        if ins.mnem == 'mov':
            dest, sep, value = ins.ops.partition(',')
            if not sep or dest not in registers:
                raise ValueError('common-interface unsupported move')
            if ins.va == receiver_load:
                if not re.fullmatch(r'DWORD PTR \[[^\]]+\]', value):
                    raise ValueError('common-interface receiver is not a pointer load')
                facts[dest], seen_receiver = 'receiver', True
            elif value in registers:
                facts[dest] = facts.get(value)
            else:
                load = re.fullmatch(r'DWORD PTR \[(e(?:ax|bx|cx|dx|si|di|bp))\]', value)
                facts[dest] = 'vptr' if load and facts.get(load[1]) == 'receiver' else None
        elif ins.mnem == 'push' and (ins.ops in registers or _DIRECT.fullmatch(ins.ops)
                                     or re.fullmatch(r'DWORD PTR \[[^\]]+\]', ins.ops)):
            pushes += 1
        elif ins.mnem == 'add' and re.fullmatch(r'esp,0x[0-9a-f]+', ins.ops) and pushes == 0:
            # Some callers finish cleaning a preceding cdecl call before
            # setting up this interface; no current argument may be removed.
            pass
        else:
            raise ValueError('common-interface dispatch window is not supported straight-line transport')
    call_ins = body[-1]
    match = re.fullmatch(r'DWORD PTR \[(e(?:ax|bx|cx|dx|si|di|bp))(?:\+0x([0-9a-f]+))?\]', call_ins.ops)
    if (call_ins.mnem != 'call' or not match or not seen_receiver or facts.get('ecx') != 'receiver'
            or facts.get(match[1]) != 'vptr' or int(match[2] or '0', 16) != anchor['slot']*4):
        raise ValueError('common-interface call does not use the witnessed receiver and slot')
    widths = witness['parameterStackBytes']
    if (len(widths) != len(method.parameters) or any(type(n) is not int or n != 4 for n in widths)
            or pushes != len(widths)):
        raise ValueError('common-interface argument transport mismatch')
    for parameter, width in zip(method.parameters, widths):
        known = G.param_bytes(parameter)
        if known is not None and known != width:
            raise ValueError('common-interface width contradicts known source parameter')
    # Unknown parameter names can use these local byte witnesses; unknown or
    # aggregate return types cannot borrow a hidden-result ABI from them.
    sf = SourceFunc(method.owner+'::'+method.name, method.file, method.line, '', [], [],
                    args=', '.join('int' for _ in widths), head=method.head)
    expected = G.expected_pop(G.Source({}, set(), set()), sf)
    if method.name.startswith('~') or expected != sum(widths):
        raise ValueError('common-interface return ABI needs an independent witness')
    return base, expected



def ordered_interface_arguments(prog: Program, method: HeaderMethod, anchor: dict,
                                source_root: Path) -> dict:
    """Check ordered DWORD transport on one independently reviewed local path.

    Called after common_interface_witness's source/receiver/slot checks. Values
    are frozen when pushed, not read from registers at CALL. Source semantics
    and external register/stack bindings remain explicitly reviewed premises;
    this is neither whole-caller domination nor return-type certification.
    """
    import re_source_graph as G
    witness = anchor['interfaceDispatch']
    ordered = witness['orderedArguments']
    if witness.get('kind') not in (None, 'straight-line'):
        raise ValueError('ordered arguments require the straight-line interface route')
    if hashlib.sha256((source_root / method.file).read_bytes()).hexdigest() != ordered['headerSha256']:
        raise ValueError('ordered argument source header hash mismatch')
    source_call = witness['source']['call']
    call = re.search(r'->' + re.escape(method.name) + r'\(([^()]*)\);$', source_call)
    if not call:
        raise ValueError('ordered argument source call is unsupported')
    if '=' in call[1]:
        raise ValueError('ordered argument source assignments are unsupported')
    expressions = G.params(call[1])
    records = ordered['parameters']
    if len(records) != len(method.parameters) or not records:
        raise ValueError('ordered argument declaration arity mismatch')
    for index, (record, declared, expression) in enumerate(zip(records, method.parameters, expressions)):
        if (record['sourceType'] != declared or record['sourceArgument'] != expression.strip()
                or type(record['stackOffset']) is not int or record['stackOffset'] != 4 + index*4):
            raise ValueError('ordered argument source order/type or storage mismatch')
        width = G.param_bytes(declared)
        if width is not None and width != 4:
            raise ValueError('ordered argument is not one DWORD')

    caller = prog.by_va[int(witness['caller']['address'], 16)]
    complete = decode_entry_body(prog.img, caller)
    start = int(witness['window']['address'], 16)
    end = start + witness['window']['bytes']
    body = [ins for ins in complete if start <= ins.va < end]
    if (not body or body[0].va != start or body[-1].va + body[-1].size != end
            or body[-1].va != int(witness['callAddress'], 16) or body[-1].mnem != 'call'):
        raise ValueError('ordered argument window is not freshly decoded instruction-aligned code')
    if body != [ins for ins in prog.body(caller) if start <= ins.va < end]:
        raise ValueError('ordered argument fresh decode differs from the validated interface window')
    # A shared CALL may join separately prepared paths. Retain that limitation;
    # an entry inside the setup instead makes this bounded witness ambiguous.
    joins = set()
    references = getattr(prog.model, 'refs_to', {})
    targets = [(int(ins.ops, 16), ins.va) for ins in complete
               if (ins.mnem.startswith(('j', 'loop')) or ins.mnem == 'call')
               and _DIRECT.fullmatch(ins.ops)]
    targets += [(dest, site) for dest, refs in references.items()
                for kind, site in refs if kind in ('call', 'jmp', 'jcc')]
    for dest, site in targets:
        if start < dest < end:
            if dest == body[-1].va:
                joins.add(site)
            else:
                raise ValueError('ordered argument setup has a possible interior entry')

    registers = {'eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp'}
    facts = {reg: 'window.' + reg for reg in registers}
    stack_delta, pushes = 0, []

    def value(operand):
        if operand in facts:
            return facts[operand]
        if _DIRECT.fullmatch(operand):
            n = int(operand, 16)
            if n > 0xffffffff:
                raise ValueError('ordered argument constant exceeds DWORD')
            return f'constant32:0x{n:08x}'
        memory = re.fullmatch(r'DWORD PTR \[(e(?:ax|bx|cx|dx|si|di|bp|sp))'
                              r'(?:\+(e(?:ax|bx|cx|dx|si|di|bp))\*([1248]))?'
                              r'(?:\+(0x[0-9a-f]+))?\]', operand)
        if not memory:
            raise ValueError('ordered argument transport uses an unsupported operand')
        base, index, scale, offset = memory.groups()
        displacement = int(offset or '0', 16)
        if base == 'esp':
            if index:
                raise ValueError('ordered argument uses indexed stack addressing')
            relative = stack_delta + displacement
            if stack_delta < 0 and relative < 0 and relative + 4 > stack_delta:
                raise ValueError('ordered argument reloads memory overwritten by an outgoing push')
            return f'load32(window.esp{relative:+d})'
        address = facts[base]
        if index:
            address += f'+({facts[index]})*{scale}'
        if displacement:
            address += f'+0x{displacement:x}'
        return 'load32(' + address + ')'

    for ins in body[:-1]:
        raw = prog.img.read(ins.va, ins.size)
        if not raw or raw[0] in (0x66, 0x67):
            raise ValueError('ordered argument transport has an unsupported width prefix')
        if ins.mnem == 'mov':
            dest, sep, operand = ins.ops.partition(',')
            if not sep or dest not in registers:
                raise ValueError('ordered argument move is not a full register write')
            facts[dest] = value(operand)
        elif ins.mnem == 'push':
            captured = value(ins.ops)  # evaluate memory relative to pre-push ESP
            if raw[0] == 0x6a:
                signed = struct.unpack('b', raw[1:2])[0] & 0xffffffff
                if captured != f'constant32:0x{signed:08x}':
                    raise ValueError('ordered argument imm8 sign extension disagrees with bytes')
            pushes.append({'pushAddress': f'0x{ins.va:08x}', 'value': captured})
            stack_delta -= 4
        else:
            raise ValueError('ordered argument setup is not supported MOV/PUSH transport')
    if len(pushes) != len(records):
        raise ValueError('ordered argument push count mismatch')
    result = []
    for record, observed in zip(records, reversed(pushes)):
        if (int(record['pushAddress'], 16) != int(observed['pushAddress'], 16)
                or record['value'] != observed['value']):
            raise ValueError('ordered argument value or push site mismatch')
        result.append(dict(observed, stackOffset=record['stackOffset'], physicalBytes=4,
                           sourceType=record['sourceType'], sourceArgument=record['sourceArgument'],
                           typeLimit=('explicit source float; transport is its raw DWORD'
                                      if record['sourceType'] == 'float' else
                                      'DWORD transport only; typedef, signedness and pointee not inferred')))
    needed = set(re.findall(r'window\.(e(?:ax|bx|cx|dx|si|di|bp|sp))',
                            ' '.join(r['value'] for r in result)))
    bindings = ordered.get('externalBindings', [])
    if len({b['register'] for b in bindings}) != len(bindings) or {b['register'] for b in bindings} != needed:
        raise ValueError('ordered argument external bindings are absent, duplicate or unused')
    for binding in bindings:
        if not binding.get('meaning') or not binding.get('evidence') or not binding.get('spans'):
            raise ValueError('ordered argument external binding requires a reviewed byte premise')
        for span in binding['spans']:
            address, count = int(span['address'], 16), span['bytes']
            if type(count) is not int or count <= 0:
                raise ValueError('ordered argument external span size is invalid')
            raw = prog.img.read(address, count)
            if len(raw) != count or hashlib.sha256(raw).hexdigest() != span['sha256']:
                raise ValueError('ordered argument external span hash mismatch')
    return {'parameters': result, 'receiver': 'ECX', 'registerValuesAtCall': facts,
            'externalBindings': bindings, 'otherEntriesAtCall': [f'0x{a:08x}' for a in sorted(joins)],
            'scope': 'reviewed local path only; external bindings are independently reviewed premises',
            'limits': 'No whole-caller domination, hidden-result, return type/storage, runtime behavior '
                      'or missing source typedef certification. External object-memory bindings '
                      'presume no alias with outgoing stack writes.'}


def propagate_vtable_anchors(prog: Program, classes: dict[str, HeaderClass], document: dict,
                             source_root: Path | None = None) -> dict:
    """Propagate explicitly supplied source/byte witnesses through fixed RTTI ancestry.

    Anchors are research inputs requiring independent semantic review, not
    verified just because their hashes match. Every holder of a target is
    considered before calling it an unambiguous method candidate.
    """
    if document.get('specimenSha256') != prog.img.sha256:
        raise ValueError('anchor specimen identity mismatch')
    tables = {t.va: t for t in prog.model.rtti.vtables}
    layouts, _ = header_layouts(classes)
    anchors, seen = [], set()
    for anchor in document['anchors']:
        table = tables.get(int(anchor['table'], 16))
        slot = anchor['slot']
        if table is None or table.klass != anchor['class'] or table.offset != anchor['offset'] \
                or not isinstance(slot, int) or isinstance(slot, bool) or not 0 <= slot < len(table.slots):
            raise ValueError('anchor table/slot identity mismatch')
        if (table.va, slot) in seen:
            raise ValueError('duplicate anchor slot')
        seen.add((table.va, slot))
        target = int(anchor['target'], 16)
        if table.slots[slot] != target or prog.img.u32(table.va+4*slot) != target:
            raise ValueError('anchor target does not match specimen table word')
        body = anchor['body']
        if int(body['address'], 16) != target or not isinstance(body['bytes'], int) \
                or isinstance(body['bytes'], bool) or body['bytes'] <= 0:
            raise ValueError('anchor body range mismatch')
        raw = prog.img.read(target, body['bytes'])
        if len(raw) != body['bytes'] or hashlib.sha256(raw).hexdigest() != body['sha256']:
            raise ValueError('anchor body hash mismatch')
        cls = classes.get(anchor['class'])
        methods = [m for m in cls.methods if m.name == anchor['method']
                   and m.parameters == tuple(anchor['parameters'])
                   and m.qualifiers == anchor.get('qualifiers', '')] if cls else []
        if len(methods) != 1:
            raise ValueError('anchor source declaration is absent or ambiguous')
        method = methods[0]
        if method.name == cls.name or re.search(r'\btemplate\s*<', method.head):
            raise ValueError('constructor/template cannot establish a virtual anchor')
        if any(issue in ('multiple class definitions', 'conditional class declaration',
                         f'conditional method {method.name}', f'unexpanded method-name macro {method.name}')
               for issue in cls.issues):
            raise ValueError('anchor source declaration is conditional or multiply defined')
        if not method.virtual and method not in layouts.get(cls.name, []):
            raise ValueError('anchor method is not established virtual')
        if not method.virtual:
            todo, checked = list(cls.bases), set()
            while todo:
                base = todo.pop()
                if base in checked:
                    continue
                checked.add(base)
                if (base, 0) not in prog.fixed_bases.get(cls.name, []):
                    raise ValueError('inherited virtualness disagrees with retail RTTI ancestry')
                todo.extend(classes[base].bases)
        if not anchor.get('evidence'):
            raise ValueError('anchor needs an explicit semantic evidence explanation')
        if 'interfaceDispatch' in anchor:
            table, _ = common_interface_witness(prog, cls, method, table, anchor, source_root)
        anchors.append((anchor, table, method))
    mapped, gaps = defaultdict(list), []
    for anchor, seed, method in anchors:
        for table in tables.values():
            offsets = {0} if table.klass == seed.klass else {
                d for base, d in prog.fixed_bases.get(table.klass, []) if base == seed.klass and d >= 0}
            if not any(d+seed.offset == table.offset for d in offsets):
                continue
            slot = anchor['slot']
            if slot >= len(table.slots):
                gaps.append({'table': f'0x{table.va:08x}', 'class': table.klass, 'missingSlot': slot})
                continue
            target = table.slots[slot]
            if prog.img.u32(table.va+slot*4) != target:
                raise ValueError('descendant table word differs from specimen')
            mapped[target].append({'class': table.klass, 'offset': table.offset,
                'table': f'0x{table.va:08x}', 'slot': slot, 'method': method.name,
                'parameters': list(method.parameters), 'qualifiers': method.qualifiers,
                'anchorTable': anchor['table'], 'anchorSlot': anchor['slot']})
    rows = []
    for target, uses in sorted(mapped.items()):
        identities = {(u['method'], tuple(u['parameters']), u['qualifiers']) for u in uses}
        covered = {(u['class'], u['offset'], u['slot'], int(u['table'], 16)) for u in uses}
        uncovered = sorted(set(prog.slots.get(target, [])) - covered)
        status = ('missing-function-boundary' if target not in prog.by_va else
                  'conflicting-method-identities' if len(identities) != 1 else
                  'unmapped-vtable-aliases' if uncovered else 'anchored-method-candidate')
        rows.append({'target': f'0x{target:08x}', 'status': status, 'uses': uses,
                     'uncoveredHolders': uncovered,
                     'leastDerivedHolders': sorted(prog.defining_classes(prog.by_va[target]))
                        if target in prog.by_va else []})
    return {'rows': rows, 'gaps': gaps, 'anchorCount': len(anchors),
            'limits': 'Supplied anchors need semantic review. Fixed RTTI inheritance preserves slots, '
                      'not exclusive ownership of linker-folded bodies. All known holders are checked; '
                      'unmapped/conflicting aliases remain unresolved. No prototype or behavior is inferred.'}


def bounded_switch_targets(prog: Program, fn: Func, body: list[Insn]) -> dict:
    """Resolve only unsigned-guarded absolute x86 switch tables from pinned bytes.

    A short, contiguous CMP/JA sequence bounds the unchanged selector. An
    optional zeroed-register byte remap has a separately bounded footprint.
    No known entry may bypass the guard, including another table's entries.
    Tables must be file-backed, non-writable and outside saved code extents.
    This is static normal-flow evidence under the PE mapping and normal call
    contract, not proof against runtime patching, exception re-entry or a
    callee corrupting its return address. It supplies no method identity.
    """
    indirect = [(n, i) for n, i in enumerate(body)
                if i.mnem == 'jmp' and not _DIRECT.fullmatch(i.ops)]
    if not indirect:
        return {'tables': [], 'refusals': []}
    # Do not let a stale or differently seeded instruction cache invent a guard.
    if decode_entry_body(prog.img, fn) != body:
        raise ValueError('switch proof disagrees with fresh entry decoding')
    registers = ('eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp')
    low = {'eax': 'al', 'ebx': 'bl', 'ecx': 'cl', 'edx': 'dl'}
    aliases = {r: {r, r[1:]} | ({low[r], low[r][0]+'h'} if r in low else set())
               for r in registers}
    starts = {i.va for i in body}
    candidates, refusals = [], []

    def pin_data(address, count):
        if not 0 <= address < 2**32 or count <= 0 or address+count > 2**32:
            raise ValueError('switch table address span wraps the x86 address space')
        section = prog.img.section_of(address)
        raw = prog.img.read(address, count)
        if (section is None or section.characteristics & 0x80000000
                or not section.contains(address+count-1) or len(raw) != count):
            raise ValueError('switch table is truncated, unmapped or writable')
        if any(f.lo < address+count and (getattr(f, 'declared_hi', None) or f.hi) >= address
               for f in prog.funcs):
            raise ValueError('switch data overlaps an exported code extent')
        return raw, {'address': f'0x{address:08x}', 'bytes': count,
                     'sha256': hashlib.sha256(raw).hexdigest()}

    def preserves_guard(ins, selector):
        # These exact MOV/PUSH forms preserve flags and the selector. No
        # instructions are skipped between the JA and the optional remap.
        if ins.mnem == 'push':
            return ins.ops in registers or bool(_DIRECT.fullmatch(ins.ops))
        if ins.mnem != 'mov' or ',' not in ins.ops:
            return False
        dest, _ = ins.ops.split(',', 1)
        return (dest in registers and dest not in aliases[selector]
                or bool(re.fullmatch(r'DWORD PTR (?:\[[^\]]+\]|ds:0x[0-9a-f]+)', dest)))

    for n, jump in indirect:
        try:
            match = re.fullmatch(r'DWORD PTR \[(e(?:ax|bx|cx|dx|si|di|bp))\*4\+(0x[0-9a-f]+)\]', jump.ops)
            if not match:
                raise ValueError('unsupported switch jump operand')
            index, table_address = match[1], int(match[2], 16)
            selector, guard_index, remap_address = index, n-1, None
            if n >= 2 and body[n-1].mnem == 'mov':
                remap = re.fullmatch(r'([abcd]l),BYTE PTR \[(e(?:ax|bx|cx|dx|si|di|bp))\+(0x[0-9a-f]+)\]', body[n-1].ops)
                if remap:
                    selector, remap_address, guard_index = remap[2], int(remap[3], 16), n-3
                    if (low.get(index) != remap[1] or index == selector
                            or body[n-2].mnem != 'xor' or body[n-2].ops != f'{index},{index}'):
                        raise ValueError('switch byte index is not independently zero-extended')
            if guard_index < 1 or body[guard_index].mnem != 'ja' or not _DIRECT.fullmatch(body[guard_index].ops):
                raise ValueError('switch lacks an adjacent unsigned upper-bound branch')
            guard = body[guard_index]
            cmp_index = guard_index-1
            while (cmp_index >= 0 and guard_index-cmp_index <= 3
                   and preserves_guard(body[cmp_index], selector)):
                cmp_index -= 1
            compare = body[cmp_index] if cmp_index >= 0 else None
            if compare is None or guard_index-cmp_index > 3 or compare.mnem != 'cmp':
                raise ValueError('switch bound comparison or intervening instructions are unproved')
            bound = re.fullmatch(re.escape(selector)+r',(0x[0-9a-f]+)', compare.ops)
            if not bound or not 0 <= int(bound[1], 16) < (256 if remap_address is not None else 4096):
                raise ValueError('switch selector or bound is unsupported')
            count = int(bound[1], 16)+1
            selector_pin = None
            if remap_address is not None:
                remapped, selector_pin = pin_data(remap_address, count)
                table_count = max(remapped)+1
                selected = list(remapped)
            else:
                table_count = count
                selected = list(range(count))
            raw, table_pin = pin_data(table_address, table_count*4)
            words = list(struct.unpack('<'+'I'*table_count, raw))
            targets = [words[s] for s in selected]
            default = int(guard.ops, 16)
            if default not in starts or any(t not in starts for t in targets):
                raise ValueError('switch target is outside the body or inside an instruction')
            candidates.append({'jump': f'0x{jump.va:08x}', 'compare': f'0x{compare.va:08x}',
                               'guard': f'0x{guard.va:08x}', 'default': f'0x{default:08x}',
                               'selector': selector, 'selectorCount': count,
                               'table': table_pin, 'remap': selector_pin,
                               'targets': [f'0x{t:08x}' for t in targets],
                               'protectedStart': compare.va+1,
                               'protectedEnd': jump.va+jump.size})
        except (ValueError, IndexError) as error:
            refusals.append({'jump': f'0x{jump.va:08x}', 'reason': str(error)})

    # A local straight-line guard is sufficient only if no direct or table
    # edge enters after the CMP's exact entry, including an entry into that
    # instruction's interior bytes. Include every decoded local call and the
    # whole-image reference census, even sources outside this function.
    direct_targets = {int(i.ops, 16) for i in body
                      if (i.mnem.startswith(('j', 'loop')) or i.mnem == 'call')
                      and _DIRECT.fullmatch(i.ops)}
    table_targets = {int(t, 16) for row in candidates for t in row['targets']}
    admitted = []
    sections = getattr(prog.img, 'sections', None)
    if sections is None:
        raise ValueError('switch bypass check needs the complete pinned PE sections')
    for row in candidates:
        lo, hi = row.pop('protectedStart'), row.pop('protectedEnd')
        bypass = any(lo <= target < hi for target in direct_targets | table_targets)
        raw_entries = []
        for target in range(lo, hi):
            bypass |= any(kind in ('call', 'jmp', 'jcc', 'imm', 'mem')
                          for kind, _ in prog.model.refs_to.get(target, []))
            bypass |= bool(getattr(prog.model, 'data_ptrs_to', {}).get(target))
            # The generic model omits .text pointers, unaligned words and a
            # section's final word. Search the pinned bytes directly for this
            # small protected interval instead of trusting that incomplete
            # census. Any occurrence is conservative evidence to withhold;
            # it need not have been classified as data or executable code.
            word = struct.pack('<I', target)
            for section in sections:
                offset = section.raw.find(word)
                if offset >= 0:
                    raw_entries.append({'section': section.name, 'address': f'0x{section.start+offset:08x}',
                                        'value': f'0x{target:08x}'})
            bypass |= bool(raw_entries)
        if bypass:
            refusals.append({'jump': row['jump'], 'reason': 'possible entry bypasses the switch guard',
                             'rawWordCandidates': raw_entries})
        else:
            admitted.append(row)
    return {'tables': admitted, 'refusals': refusals,
            'bodySha256': hashlib.sha256(prog.img.read(fn.va, fn.hi-fn.va+1)).hexdigest()}


def typed_list_loop(prog: Program, fn: Func, witness: dict) -> dict:
    """Check one bounded intrusive-list dispatch, conditional on normal callee ABI.

    This recognizes the transport, not the source identity or callback effects.
    An explicit reviewer must bind the source method and the list's RTTI layout.
    The receiver is a nonvolatile register; callbacks must preserve it and must
    leave its node readable through the subsequent next-member load.
    """
    start, size = int(witness['address'], 16), witness['bytes']
    if type(size) is not int or not 0 < size <= 256 or not fn.va <= start < start+size <= fn.hi+1:
        raise ValueError('typed-list loop extent is invalid')
    raw = prog.img.read(start, size)
    if len(raw) != size or hashlib.sha256(raw).hexdigest() != witness['sha256']:
        raise ValueError('typed-list loop pin mismatch')
    full = decode_entry_body(prog.img, fn)
    body = [i for i in full if start <= i.va < start+size]
    if len(body) < 13 or body[0].va != start or body[-1].va+body[-1].size != start+size:
        raise ValueError('typed-list loop cuts an instruction')
    if possible_interior_entry(prog, start, start+size):
        raise ValueError('typed-list loop has a possible bypassing entry')
    outside = [i for i in full if not start <= i.va < start+size]
    if any((i.mnem.startswith(('j','loop')) or i.mnem == 'call')
           and _DIRECT.fullmatch(i.ops) and start < int(i.ops,16) < start+size for i in outside):
        raise ValueError('typed-list loop has a freshly decoded bypassing entry')
    indirect = [i for i in outside if i.mnem.startswith(('j','loop')) and not _DIRECT.fullmatch(i.ops)]
    if indirect:
        proven = bounded_switch_targets(prog, fn, full)
        covered = {int(t['jump'],16):t for t in proven['tables']}
        if any(i.va not in covered or any(start < int(t,16) < start+size
               for t in covered[i.va]['targets']) for i in indirect):
            raise ValueError('typed-list caller has an unresolved indirect entry')
    head = re.fullmatch(r'(ebx|esi|edi|ebp),DWORD PTR ds:0x([0-9a-f]+)', body[0].ops)
    if body[0].mnem != 'mov' or not head or int(head[2], 16) != int(witness['head'], 16):
        raise ValueError('typed-list head is not the selected global pointer')
    node = head[1]
    zero = witness.get('zeroRegister')
    if zero is not None:
        site = int(witness['zeroAddress'], 16)
        prefix = [i for i in full if i.va <= site]
        if (zero not in ('ebx', 'esi', 'edi', 'ebp') or zero == node or not prefix
                or prefix[-1].va != site or prefix[-1].mnem != 'xor'
                or prefix[-1].ops != zero+','+zero or site >= start
                or any(i.mnem not in ('push', 'mov', 'lea', 'nop') for i in prefix[:-1])
                or possible_interior_entry(prog, fn.va, start+1)):
            raise ValueError('typed-list zero register has no straight-entry witness')
        aliases = {'ebx': ('ebx', 'bx', 'bl', 'bh'), 'esi': ('esi', 'si'),
                   'edi': ('edi', 'di'), 'ebp': ('ebp', 'bp')}[zero]
        between = [i for i in full if site < i.va < start]
        if any((i.mnem not in ('mov', 'lea', 'add', 'sub', 'inc', 'dec', 'cmp', 'test', 'push', 'call')
                and not i.mnem.startswith('j'))
               or (i.ops.split(',')[0] in aliases and i.mnem not in ('cmp', 'test', 'push'))
               for i in between):
            raise ValueError('typed-list zero register was clobbered')
        starts = {i.va for i in full}
        if any(not _DIRECT.fullmatch(i.ops) or not site < int(i.ops,16) <= start
               or int(i.ops,16) not in starts for i in between if i.mnem.startswith('j')):
            raise ValueError('typed-list zero register prefix has an unresolved detour')
        for ins in full:
            if not (ins.mnem.startswith(('j','loop')) or ins.mnem == 'call'):
                continue
            if ins.mnem != 'call' and not _DIRECT.fullmatch(ins.ops):
                raise ValueError('typed-list zero register has an unresolved later entry')
            if (_DIRECT.fullmatch(ins.ops) and ins.va >= start+size
                    and fn.va < int(ins.ops,16) < start+size):
                raise ValueError('typed-list zero register has a later bypassing entry')
    def null_test(ins):
        return ((ins.mnem == 'test' and ins.ops == node+','+node)
                or (zero is not None and ins.mnem == 'cmp' and ins.ops == node+','+zero))
    j = 1
    if body[j].mnem == 'pop' and body[j].ops in ('ebx', 'esi', 'edi', 'ebp'):
        if body[j].ops in (node, zero):
            raise ValueError('typed-list head or zero register overwritten by pop')
        j += 1
    if (len(body) < j+9 or not null_test(body[j]) or body[j+1].mnem != 'je'
            or body[j+1].ops != hex(start+size)):
        raise ValueError('typed-list null guard mismatch')
    entry = body[j+2].va
    vptr = re.fullmatch(r'(eax|edx),DWORD PTR \['+node+r'\]', body[j+2].ops)
    call = body[j+4]
    slot = witness['slot']
    if (type(slot) is not int or not 1 <= slot <= 31 or body[j+2].mnem != 'mov' or not vptr
            or body[j+3].mnem != 'mov' or body[j+3].ops != 'ecx,'+node
            or call.mnem != 'call' or call.ops != f'DWORD PTR [{vptr[1]}+0x{slot*4:x}]'
            or call.va != int(witness['callAddress'], 16)):
        raise ValueError('typed-list receiver/vptr/slot transport mismatch')
    tail = body[j+5:]
    conditional = tail[0].mnem == 'mov' and re.fullmatch(r'al,ds:0x[0-9a-f]+', tail[0].ops)
    if conditional:
        tail = tail[1:]
    next_offset = witness['nextOffset']
    if (type(next_offset) is not int or not 4 <= next_offset <= 0x7c or next_offset % 4
            or tail[0].mnem != 'mov' or tail[0].ops != f'{node},DWORD PTR [{node}+0x{next_offset:x}]'):
        raise ValueError('typed-list next-member transport mismatch')
    tail = tail[1:]
    if conditional:
        low_zero = {'ebx': 'bl'}.get(zero)
        if (len(tail) != 8 or not ((tail[0].mnem == 'test' and tail[0].ops == 'al,al')
                or (low_zero and tail[0].mnem == 'cmp' and tail[0].ops == 'al,'+low_zero))
                or tail[1].mnem != 'je' or tail[1].ops != hex(tail[-2].va)):
            raise ValueError('typed-list ancillary-call guard mismatch')
        tail = tail[2:]
    if (len(tail) != 6 or tail[0].mnem != 'push' or not _DIRECT.fullmatch(tail[0].ops)
            or tail[1].mnem != 'push' or tail[1].ops not in ('0x0', zero)
            or tail[2].mnem != 'mov' or not re.fullmatch(r'ecx,0x[0-9a-f]+', tail[2].ops)
            or tail[3].mnem != 'call' or not _DIRECT.fullmatch(tail[3].ops)
            or not null_test(tail[4]) or tail[5].mnem != 'jne' or tail[5].ops != hex(entry)):
        raise ValueError('typed-list ancillary transport or backedge mismatch')
    return dict(head=witness['head'], slot=slot, nextOffset=next_offset,
                callAddress=witness['callAddress'], parameterStackBytes=0,
                ancillaryCall=tail[3].ops, conditionalAncillary=bool(conditional))


def typed_list_source_receiver(text: str, base: str, node: str, call: str, call_offset: int) -> None:
    """Admit the surviving standalone typed-list source shape, not arbitrary C++.

    Declaration, call and advancement must belong to the same simple loop.
    Qualified/template types, shadowed receivers, literals and conditional calls
    cannot lend an unrelated declaration or assignment to this witness.
    """
    if re.search(r'\b(?:u8|u|U|L)?R"', text):
        raise ValueError('typed-list source raw literals are unsupported')
    masked = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                    lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), text)
    name = re.escape(node)
    declaration = (r'(?:^|[;{}])\s*'+re.escape(base)+r'\s*\*\s*'+name+
                   r'\s*=\s*[A-Za-z_]\w*\s*;\s*while\s*\(\s*'+name+
                   r'\s*\)\s*\{(?P<loop>[^{}]*)\}')
    loops = list(re.finditer(declaration, masked))
    if len(loops) != 1 or not loops[0].start('loop') <= call_offset < loops[0].end('loop'):
        raise ValueError('typed-list source receiver declaration and call are not one bound loop')
    assignment = re.match(r'[A-Za-z_]\w*\s+([A-Za-z_]\w*)\s*=', call)
    if assignment and assignment[1] == node:
        raise ValueError('typed-list source result declaration shadows receiver')
    diagnostic = ''
    if assignment:
        result = re.escape(assignment[1])
        diagnostic = (r'(?:(?:if\s*\(\s*'+result+r'\s*!=\s*[A-Za-z_]\w*\s*\)\s*'+
                      name+r'\s*=\s*'+name+r'\s*;)|(?:ASSERT\s*\(\s*'+result+
                      r'\s*==\s*[A-Za-z_]\w*\s*\)\s*;))?')
    body = r'\s*'+re.escape(call)+r'\s*'+diagnostic+r'\s*'+name+r'\s*=\s*'+name+r'->mNext\s*;\s*'
    if not re.fullmatch(body, loops[0]['loop']):
        raise ValueError('typed-list source call and standalone next assignment shape mismatch')


def typed_list_witnesses(prog: Program, document: dict, source_root: Path | None) -> dict:
    """Validate reviewed typed-list seeds without manufacturing missing headers.

    The source/retail caller correspondence and receiver-layout evidence remain
    explicit review obligations. Complete-body and span pins preserve that
    reviewed evidence; hashes alone do not establish their semantic meaning.
    """
    if (source_root is None or document.get('kind') != 'typed-list-interface-v1'
            or document.get('specimenSha256') != prog.img.sha256
            or not document.get('receiverEvidence') or not document.get('sourceDivergences')):
        raise ValueError('typed-list identity or reviewed layout evidence absent')
    fresh = scan_rtti(prog.img)
    if fresh != prog.model.rtti:
        raise ValueError('typed-list cached RTTI differs from specimen')
    base, table_va = document['baseClass'], int(document['baseTable'], 16)
    tables = [t for t in fresh.vtables if t.va == table_va]
    if len(tables) != 1 or tables[0].klass != base or tables[0].offset != 0:
        raise ValueError('typed-list primary base table mismatch')
    def pinned_body(record):
        va, size = int(record['address'], 16), record['bytes']
        fn = prog.by_va.get(va)
        if (type(size) is not int or fn is None or fn.hi+1-va != size
                or hashlib.sha256(prog.img.read(va, size)).hexdigest() != record['sha256']):
            raise ValueError('typed-list complete body pin mismatch')
        if any(other.va != va and other.lo <= fn.hi
               and (other.declared_hi or other.hi) >= fn.lo for other in prog.funcs):
            raise ValueError('typed-list witness has overlapping function ownership')
        return fn, decode_entry_body(prog.img, fn)
    layout = document['layout']
    _, body = pinned_body(layout['body'])
    if (not layout.get('evidence') or body[0].mnem != 'mov'
            or body[0].ops != f'DWORD PTR [ecx],0x{table_va:x}'):
        raise ValueError('typed-list RTTI receiver binding mismatch')
    heads = {int(h, 16) for h in layout['heads']}
    if len(heads) != 2 or any(not any(i.mnem == 'mov' and i.ops == f'eax,ds:0x{h:x}' for i in body)
                             for h in heads):
        raise ValueError('typed-list layout does not reference both selected heads')
    offset = layout['nextOffset']
    if (type(offset) is not int or not 4 <= offset <= 0x7c or offset % 4
            or sum(i.mnem == 'mov' and i.ops == f'eax,DWORD PTR [eax+0x{offset:x}]' for i in body) != 2):
        raise ValueError('typed-list next-member layout binding mismatch')
    if not layout.get('supportBodies'):
        raise ValueError('typed-list independent registration/migration evidence absent')
    for record in layout['supportBodies']:
        if not record.get('evidence'):
            raise ValueError('typed-list supporting body needs a semantic explanation')
        pinned_body(record)
    result = {}
    for anchor in document['anchors']:
        slot = anchor['slot']
        key = (int(anchor['table'], 16), slot)
        if (key in result or key[0] != table_va or type(slot) is not int
                or not 0 < slot < len(tables[0].slots) or not anchor.get('callerIdentityEvidence')
                or not re.fullmatch(r'[A-Za-z_]\w*', anchor['method'])):
            raise ValueError('typed-list anchor or independent caller identity missing')
        source = anchor['source']
        if Path(source['file']).name != source['file']:
            raise ValueError('typed-list source filename is not bounded')
        path = source_root/source['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError('typed-list source pin mismatch')
        fs = [f for f in index_source(source_root, (source['file'],)) if f.key == source['function']]
        if (len(fs) != 1 or fs[0].key.split('::')[-1] != anchor['method']
                or type(source['line']) is not int or not fs[0].line <= source['line'] <= fs[0].end_line):
            raise ValueError('typed-list source caller is absent or ambiguous')
        text = strip_comments(path.read_text(errors='replace'))
        conditioned = text
        if source.get('platform') == 'PC':
            # The surviving PC implementation is enclosed by TARGET == PC.
            # Admit that one expression only for an actual i386 PE32 image;
            # this is not permission to choose arbitrary unknown branches.
            data = prog.img.data
            pe_offset = struct.unpack_from('<I', data, 0x3c)[0] if len(data) >= 0x40 else -1
            if (pe_offset < 0 or pe_offset+26 > len(data) or data[:2] != b'MZ'
                    or data[pe_offset:pe_offset+4] != b'PE\0\0'
                    or struct.unpack_from('<H', data, pe_offset+4)[0] != 0x14c
                    or struct.unpack_from('<H', data, pe_offset+24)[0] != 0x10b):
                raise ValueError('typed-list PC source selection needs an i386 PE32 image')
            conditioned = re.sub(r'(?m)^([ \t]*#[ \t]*if[ \t]+)TARGET[ \t]*==[ \t]*PC[ \t]*$',
                                 lambda m: (m[1]+'1').ljust(len(m[0])), text)
        elif source.get('platform') is not None:
            raise ValueError('typed-list source platform selection is unsupported')
        active, conditions = _header_conditions(conditioned, set())
        lo = sum(len(s) for s in text.splitlines(keepends=True)[:fs[0].line-1])
        hi = sum(len(s) for s in text.splitlines(keepends=True)[:fs[0].end_line])
        if active[lo:hi] != text[lo:hi] or any(a < hi and b > lo for a,b in conditions):
            raise ValueError('typed-list source caller contains unresolved conditions')
        actual = text.splitlines()[source['line']-1].strip()
        call = re.fullmatch(r'(?:[A-Za-z_]\w*\s+[A-Za-z_]\w*\s*=\s*)?([A-Za-z_]\w*)->'
                            + re.escape(anchor['method'])+r'\(\);', actual)
        if not call or actual != source['call']:
            raise ValueError('typed-list source call mismatch')
        node = call[1]
        line_text = text.splitlines()[source['line']-1]
        call_offset = (sum(len(s) for s in text.splitlines(keepends=True)[:source['line']-1])-lo
                       +len(line_text)-len(line_text.lstrip()))
        typed_list_source_receiver(text[lo:hi], base, node, actual, call_offset)
        fn, _ = pinned_body(anchor['caller'])
        if not anchor.get('identityBodies'):
            raise ValueError('typed-list independent caller distinctions absent')
        for record in anchor['identityBodies']:
            if not record.get('evidence'):
                raise ValueError('typed-list caller distinction needs reviewed evidence')
            pinned_body(record)
        loops = [typed_list_loop(prog, fn, w) for w in anchor['loops']]
        if (len(loops) != 2 or {int(w['head'],16) for w in loops} != heads
                or any(w['slot'] != slot or w['nextOffset'] != offset for w in loops)):
            raise ValueError('typed-list dispatches disagree with reviewed interface')
        result[key] = dict(pop=0, loops=loops)
    if not result:
        raise ValueError('typed-list witness has no anchors')
    return result


def typed_list_virtuals(prog: Program, document: dict, source_root: Path) -> dict:
    """Project reviewed list-dispatch identities through exact primary RTTI holders."""
    witnesses = typed_list_witnesses(prog, document, source_root)
    base, table_va = document['baseClass'], int(document['baseTable'], 16)
    mapped, gaps = defaultdict(list), []
    for table in prog.model.rtti.vtables:
        occurrences = [offset for name,offset in prog.bases.get(table.klass, []) if name == base]
        fixed = [offset for name,offset in prog.fixed_bases.get(table.klass, []) if name == base]
        if not occurrences:
            continue
        col = prog.img.u32(table.va-4)
        if (table.offset != 0 or occurrences != [0] or fixed != [0] or col is None
                or prog.img.u32(col) != 0 or prog.img.u32(col+4) != 0 or prog.img.u32(col+8) != 0):
            gaps.append(dict(table=hex(table.va), reason='not a unique fixed primary base'))
            continue
        for anchor in document['anchors']:
            slot = anchor['slot']
            if slot >= len(table.slots):
                gaps.append(dict(table=hex(table.va), missingSlot=slot))
                continue
            target = table.slots[slot]
            if prog.img.u32(table.va+4*slot) != target:
                raise ValueError('typed-list raw table word mismatch')
            mapped[target].append(dict(**{'class': table.klass}, offset=0, table=f'0x{table.va:08x}',
                slot=slot, method=anchor['method'], parameters=[], qualifiers='',
                anchorTable=f'0x{table_va:08x}', anchorSlot=slot))
    pointers = defaultdict(set)
    for section in prog.img.sections:
        if section.characteristics & 0x20000000:
            continue
        for offset in range(0, len(section.raw)-3, 4):
            word = struct.unpack_from('<I', section.raw, offset)[0]
            if word in mapped:
                pointers[word].add(section.start+offset)
    rows = []
    for target,uses in sorted(mapped.items()):
        covered = {(u['class'],u['offset'],u['slot'],int(u['table'],16)) for u in uses}
        uncovered = sorted(set(prog.slots.get(target, []))-covered)
        identities = {u['method'] for u in uses}
        cells = {int(u['table'],16)+4*u['slot'] for u in uses}
        status = ('conflicting-method-identities' if len(identities) != 1 else
                  'unmapped-vtable-aliases' if uncovered else
                  'extra-noncode-pointer-cells' if pointers[target] != cells else
                  'missing-function-boundary' if target not in prog.by_va else 'anchored-method-candidate')
        rows.append(dict(target=f'0x{target:08x}',status=status,uses=uses,uncoveredHolders=uncovered,
                         dataPointerCells=[f'0x{x:08x}' for x in sorted(pointers[target])],
                         leastDerivedHolders=sorted(prog.defining_classes(prog.by_va[target]))
                             if target in prog.by_va else []))
    propagated = dict(rows=rows,gaps=gaps)
    admission = vtable_abi_admission(prog, {}, document, propagated, source_root)
    return dict(propagated, admission=admission, proposals=vtable_name_proposals(prog,propagated,admission),
                witnesses={f'{table:08x}:{slot}':value for (table,slot),value in witnesses.items()},
                limits='Conditional on independently reviewed source/retail caller and list-layout correspondences. '
                       'Pins and loop transport checks do not by themselves prove those correspondences. '
                       'Aligned non-code pointers and all known RTTI holders are checked, not all computed pointers. '
                       'No source declaration, qualifiers, result type, callback lifetime or device-runtime acceptance. '
                       'Normal callee ABI and readable post-callback nodes are premises. Existing cohort gates still apply.')


def vtable_abi_admission(prog: Program, classes: dict[str, HeaderClass], document: dict, propagated: dict,
                         source_root: Path | None = None) -> dict:
    """Apply the same return/alias/boundary checks to every proposed method identity.

    This is the mechanical part of cohort admission. An independent review must
    establish the anchors' semantics once, and examine all flagged rows. A pass
    supports a method identity under those anchors, not full behavior or ABI types.
    """
    import re_source_graph as G
    anchor_by_slot = {(int(a['table'],16), a['slot']): a for a in document['anchors']}
    witnessed_pops = {}
    ordered_witnesses = {}
    tables = {t.va:t for t in prog.model.rtti.vtables}
    typed = (typed_list_witnesses(prog, document, source_root)
             if document.get('kind') == 'typed-list-interface-v1' else None)
    if typed is not None:
        witnessed_pops.update({key: value['pop'] for key,value in typed.items()})
    for key, a in anchor_by_slot.items():
        if 'interfaceDispatch' in a:
            cls = classes[a['class']]
            methods = [m for m in cls.methods if m.name == a['method']
                       and m.parameters == tuple(a['parameters']) and m.qualifiers == a.get('qualifiers', '')]
            if len(methods) != 1:
                raise ValueError('common-interface source declaration is absent or ambiguous')
            _, witnessed_pops[key] = common_interface_witness(prog, cls, methods[0], tables[key[0]], a, source_root)
            if 'orderedArguments' in a['interfaceDispatch']:
                ordered_witnesses[key] = ordered_interface_arguments(prog, methods[0], a, source_root)

    # Invocation-local only: reference caches must remain consistent with the
    # original whole-image instruction model, and later calls may use new bytes.
    entry_decodes = {}
    switch_proofs = {}

    def pops(va, seen=frozenset()):
        if va in seen or len(seen) >= 8 or va not in prog.by_va:
            return set(), {'unresolved tail target or cycle'}
        fn=prog.by_va[va]
        found, issues=set(), set()
        if (getattr(fn, 'body_ranges', 1) != 1
                or getattr(fn, 'declared_hi', fn.hi) not in (None, fn.hi)
                or getattr(fn, 'body_bytes', None) not in (None, fn.hi-fn.lo+1)
                or fn.lo != fn.va):
            return set(), {'noncontiguous or clipped function boundary'}
        if any(other.va != fn.va and other.lo <= fn.hi
               and (getattr(other, 'declared_hi', None) or other.hi) >= fn.lo
               for other in prog.funcs):
            return set(), {'overlapping exported function ownership'}
        body = prog.body(fn)
        cursor = fn.va
        covered = True
        for ins in body:
            covered &= ins.va == cursor and 1 <= ins.size <= 15
            cursor = ins.va + ins.size
        covered &= cursor == fn.hi + 1
        if not covered:
            if va not in entry_decodes:
                evidence = {'target': f'0x{va:08x}', 'source': 'entry-seeded GNU objdump',
                            'start': f'0x{va:08x}', 'endExclusive': f'0x{fn.hi+1:08x}'}
                try:
                    decoded = decode_entry_body(prog.img, fn)
                except (ValueError, OSError, subprocess.SubprocessError) as exc:
                    evidence.update(status='refused', reason=str(exc))
                    entry_decodes[va] = ([], evidence)
                else:
                    evidence.update(status='complete-byte-coverage', instructions=len(decoded),
                                    bytes=fn.hi-fn.va+1,
                                    bodySha256=hashlib.sha256(prog.img.read(fn.va, fn.hi-fn.va+1)).hexdigest())
                    entry_decodes[va] = (decoded, evidence)
            body, evidence = entry_decodes[va]
            if evidence['status'] != 'complete-byte-coverage':
                return set(), {'instruction decoding does not cover the exact function range',
                               'entry decoding refused: ' + evidence['reason']}
        if not body or body[-1].mnem not in ('ret', 'jmp'):
            issues.add('unresolved fallthrough beyond function range')
        if va not in switch_proofs:
            try:
                switch_proofs[va] = bounded_switch_targets(prog, fn, body)
            except (ValueError, OSError, subprocess.SubprocessError) as error:
                switch_proofs[va] = {'tables': [], 'refusals': [{'reason': str(error)}]}
        switches = {int(r['jump'], 16): r for r in switch_proofs[va]['tables']}
        starts = {ins.va for ins in body}
        for ins in body:
            if ins.mnem in ('(bad)', '.byte', '.word', '.long'):
                issues.add('invalid or data instruction decoding')
            if ins.mnem == 'xchg' and re.search(r'\b(?:esp|sp)\b', ins.ops):
                issues.add('opaque stack-pointer write')
            if ins.ops.split(',')[0] in ('esp', 'sp') and ins.mnem not in ('cmp', 'test', 'push'):
                if not (ins.mnem in ('add', 'sub') and re.fullmatch(r'esp,0x[0-9a-f]+', ins.ops)) \
                        and not (ins.mnem == 'mov' and ins.ops == 'esp,ebp'):
                    issues.add('opaque stack-pointer write')
            if ins.mnem == 'ret':
                found.add(int(ins.ops,16) if ins.ops else 0)
            elif ins.mnem.startswith(('j', 'loop')):
                if _DIRECT.fullmatch(ins.ops):
                    target=int(ins.ops,16)
                    if fn.lo <= target <= fn.hi:
                        if target not in starts:
                            issues.add('branch target is not a decoded instruction boundary')
                    else:
                        if ins.mnem == 'jmp':
                            # A backward branch can reach this tail after
                            # instructions later in address order. Inspect
                            # the whole source body, not a linear prefix.
                            if any(i.mnem in ('push', 'pop', 'pushf', 'popf', 'pusha', 'popa',
                                              'call', 'enter', 'leave')
                                   or re.search(r'\b(?:[er]?(?:sp|bp)|ss)\b', i.ops)
                                   for i in body):
                                issues.add('external tail prefix lacks a stack-neutral proof')
                            more, unknown=pops(target, seen|{va})
                            found.update(more); issues.update(unknown)
                        else:
                            issues.add('conditional branch outside current function range')
                else:
                    if ins.va not in switches:
                        issues.add('indirect tail target not proven')
        if not found:
            issues.add('no return cleanup established')
        return found, issues

    rows=[]
    for row in propagated['rows']:
        target=int(row['target'],16)
        issues=[] if row['status']=='anchored-method-candidate' else [row['status']]
        expected=set()
        for use in row['uses']:
            a=anchor_by_slot[(int(use['anchorTable'],16),use['anchorSlot'])]
            if typed is not None:
                expected.add(witnessed_pops[(int(a['table'],16),a['slot'])])
                continue
            method=next(m for m in classes[a['class']].methods if m.name==a['method']
                        and m.parameters==tuple(a['parameters']) and m.qualifiers==a.get('qualifiers',''))
            sf=SourceFunc(method.owner+'::'+method.name,method.file,method.line,'',[],[],
                          args=', '.join(method.parameters),head=method.head)
            n=witnessed_pops.get((int(a['table'],16),a['slot']))
            if n is None:
                n=G.expected_pop(G.Source({},set(),set()),sf)
            if method.name.startswith('~'):
                # An ordinary source destructor does not describe the compiler's
                # deleting entry (flag, optional deallocation, adjusted this).
                # Keep these out until a separately witnessed entry kind exists.
                issues.append('destructor entry kind needs an independent ABI witness')
            elif n is None:
                # A purecall/abort seed can end in RET without implementing the
                # interface. Its cleanup cannot prove an aggregate's hidden
                # result argument, even when descendants happen to agree.
                issues.append('source interface cleanup needs an independent ABI witness')
            else:
                expected.add(n)
        actual, unknown=pops(target)
        issues.extend(unknown)
        if len(expected)!=1 or actual!=expected:
            issues.append('return cleanup disagrees with anchor interface')
        fn=prog.by_va.get(target)
        # Use the same byte-checked entry decode for constant contradictions.
        # Reading the gapped cache again could conceal a decisive XOR/MOV.
        decoded = entry_decodes.get(target)
        tiny = (tiny_semantics(prog, fn, instructions=decoded[0] if decoded else None)
                if fn else None)
        # Only compare constant bodies for classes that actually declare this
        # implementation; never impose a base default on a derived override.
        for use in row['uses']:
            cls=classes.get(use['class'])
            if not cls: continue
            methods=[m for m in cls.methods if m.name==use['method']
                     and m.parameters==tuple(use['parameters']) and m.qualifiers==use['qualifiers']]
            if len(methods)!=1 or methods[0].body is None: continue
            match=re.fullmatch(r'\s*return\s+(TRUE|FALSE|true|false|NULL|0|1)\s*;\s*',methods[0].body)
            if match and tiny and tiny.startswith('const:'):
                want=1 if match.group(1) in ('TRUE','true','1') else 0
                if tiny.split(':')[1]!=str(want): issues.append('tiny constant contradicts source implementation')
        arguments = []
        for use in row['uses']:
            key = (int(use['anchorTable'], 16), use['anchorSlot'])
            if key in ordered_witnesses:
                arguments.append(ordered_witnesses[key])
        storage = None
        if arguments:
            layouts = {tuple((p['stackOffset'], p['physicalBytes'], p['sourceType'])
                             for p in witness['parameters']) for witness in arguments}
            if len(arguments) != len(row['uses']) or len(layouts) != 1:
                issues.append('ordered argument layouts conflict or leave a holder uncovered')
            elif not issues:
                storage = {'status': 'reviewed-local-transport-pass', 'receiver': 'ECX',
                           'parameters': arguments[0]['parameters'],
                           'returnTypeAndStorage': 'excluded; preserve independently',
                           'limits': 'Conditional on reviewed source and external-value bindings; '
                                     'not whole-caller or complete ABI certification.'}
        rows.append({'target':row['target'],'status':'mechanical-checks-pass' if not issues else 'withheld',
                     'expectedReturnPop':sorted(expected),'observedReturnPop':sorted(actual),
                     'argumentStorage':storage, 'flags':sorted(set(issues))})
    return {'rows':rows, 'orderedArgumentWitnesses': [dict(anchorTable=f'0x{k[0]:08x}', anchorSlot=k[1], **v)
                for k,v in sorted(ordered_witnesses.items())],
            'entryDecodings':[entry_decodes[k][1] for k in sorted(entry_decodes)],
            'switchProofs':[dict(target=f'0x{k:08x}', **switch_proofs[k]) for k in sorted(switch_proofs)
                            if switch_proofs[k]['tables'] or switch_proofs[k]['refusals']],
            'limits':'Conditional on independently rederived seed identities. '
            'Current function ranges, direct tails and admitted bounded switch tables are checked; other indirect '
            'tails and unresolved paths are withheld. Tables are separately pinned non-writable PE data; '
            'runtime patching and exception re-entry are not certified. No return/parameter type, stack-balance, '
            'callee behavior or runtime-behavior certification. '
            'Promotion additionally requires reviewed owners/names and the existing Ghidra gate.'}


def vtable_name_proposals(prog: Program, propagated: dict, admission: dict) -> dict:
    """Deterministic dispositions for one mechanically checked identity batch.

    Existing labels only decide whether a supported spelling can be retained;
    they never decide a method or an owner. A unique least-derived RTTI holder
    is a usable naming context, not proof against linker folding. Ambiguous
    owners and collisions stay outside the batch, including order-dependent
    collisions with another candidate's old name.
    """
    checked = {r['target']: r for r in admission['rows']}
    occupied = defaultdict(set)
    for fn in prog.funcs:
        occupied[fn.name].add(fn.va)
    rows = []
    for row in propagated['rows']:
        target = int(row['target'], 16)
        fn = prog.by_va.get(target)
        result = {'target': row['target'], 'currentName': fn.name if fn else None,
                  'proposedName': None, 'status': 'withheld', 'flags': []}
        check = checked.get(row['target'])
        if not check or check['status'] != 'mechanical-checks-pass':
            result['flags'] = check['flags'] if check else ['no mechanical admission']
        else:
            identities = {(u['method'], tuple(u['parameters']), u['qualifiers']) for u in row['uses']}
            if len(identities) != 1 or not fn:
                result['flags'] = ['identity or function is unresolved']
            else:
                method = next(iter(identities))[0]
                holders = {u['class'] for u in row['uses']}
                names = {c+'__'+method for c in holders}
                if fn.name in names:
                    result.update(proposedName=fn.name, status='keep')
                elif len(row['leastDerivedHolders']) == 1:
                    result.update(proposedName=row['leastDerivedHolders'][0]+'__'+method, status='rename')
                else:
                    result['flags'] = ['no unique RTTI naming owner']
        proposed = result['proposedName']
        if proposed and occupied[proposed] - {target}:
            result.update(status='withheld', flags=['proposed name already belongs to another function'])
        rows.append(result)
    proposed_targets = defaultdict(set)
    for row in rows:
        if row['status'] != 'withheld':
            proposed_targets[row['proposedName']].add(row['target'])
    for row in rows:
        if row['proposedName'] and len(proposed_targets[row['proposedName']]) > 1:
            row.update(status='withheld', flags=['multiple targets propose the same name'])
    return {'rows': rows, 'limits': 'Exact source method identity under reviewed anchors; RTTI holder '
            'names do not prove exclusive source ownership. No behavior or prototype changes. '
            'Keep and rename rows need the declared cohort preservation/review gate before publication.'}


# ---------------------------------------------------------------------------
# Caller-bound class-name getters
# ---------------------------------------------------------------------------

def class_name_getters(prog: Program, document: dict, source_root: Path) -> dict:
    """A reviewed source caller plus exact literal getters; no invented macro declaration.

    The absent DECLARE_* definitions cannot establish a header layout. This
    separate witness binds only _GetClassName at the observed primary slot.
    Initial literal contents may be writable; no runtime constness is inferred.
    Saved names are outputs/collision checks, never identity inputs.
    """
    if (document.get('specimenSha256') != prog.img.sha256
            or document.get('kind') != 'class-name-getter-v1'
            or not document.get('evidence') or not document.get('receiverEvidence')):
        raise ValueError('class-name witness identity or reviewed evidence missing')
    source = document['source']
    if Path(source['file']).name != source['file']:
        raise ValueError('class-name source path is not a bounded filename')
    path = source_root / source['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('class-name source hash mismatch')
    functions = [f for f in index_source(source_root, (source['file'],))
                 if f.key == source['function']]
    line = source['line']
    if (len(functions) != 1 or type(line) is not int
            or not functions[0].line <= line <= functions[0].end_line):
        raise ValueError('class-name source caller is absent or ambiguous')
    actual = strip_comments(path.read_text()).splitlines()[line-1].strip()
    match = re.fullmatch(r'strcpy\s*\(\s*\w+\s*,\s*(\w+)->ToRead\(\)->_GetClassName\(\)\s*\)\s*;', actual)
    if actual != source['call'] or not match:
        raise ValueError('class-name source string-copy call mismatch')
    base = document['baseClass']
    if not re.search(r'CActiveReader\s*<\s*'+re.escape(base)+r'\s*>\s*\*\s*'
                     +re.escape(match[1])+r'\s*=', functions[0].body):
        raise ValueError('class-name source receiver type is not established')

    def span(pin):
        start, size = int(pin['address'], 16), pin['bytes']
        if type(size) is not int or size <= 0:
            raise ValueError('class-name invalid span')
        raw = prog.img.read(start, size)
        if len(raw) != size or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise ValueError('class-name span hash mismatch')
        return start, start+size, raw

    start, end, _ = span(document['caller'])
    fn = prog.by_va.get(start)
    if (fn is None or fn.lo != start or fn.hi+1 != end or fn.body_ranges != 1
            or fn.declared_hi != end-1 or fn.body_bytes != end-start):
        raise ValueError('class-name caller boundary mismatch')
    ws, we, raw = span(document['window'])
    slot = document['slot']
    if (type(slot) is not int or not 0 <= slot <= 31 or not start <= ws < we <= end
            or int(document['callAddress'], 16) != ws+8 or len(raw) < 18
            or raw[:8] != bytes.fromhex('8b 0a 85 c9 74 28 8b 11')
            or raw[8:11] != bytes([0xff, 0x52, slot*4])
            or raw[11:18] != bytes.fromhex('8b f8 83 c9 ff 33 c0')
            or raw[18:] != bytes.fromhex('8d542420 f2ae f7d1 2bf9 8bc1 8bf7 8bfa '
                                         'c1e902 f3a5 8bc8 83e103 f3a4')
            or we != ws+46):
        raise ValueError('class-name receiver/slot/string-result window mismatch')
    literal = document['callerLiteral']
    text = literal['text'].encode('ascii')+b'\0'
    va, site = int(literal['address'], 16), int(literal['pushAddress'], 16)
    if (prog.img.read(va, len(text)) != text or prog.img.data.count(text) != 1
            or literal['text'] not in functions[0].literals
            or not start <= site < site+5 <= end
            or prog.img.read(site, 5) != b'\x68'+struct.pack('<I', va)):
        raise ValueError('class-name unique caller literal witness mismatch')

    # Re-run the existing strict RTTI parser against the specimen, not a cached
    # model's claim about class ownership. No new RTTI recovery implementation.
    fresh = scan_rtti(prog.img)
    if fresh != prog.model.rtti:
        raise ValueError('class-name cached RTTI differs from fresh specimen')
    seed = document['seed']
    seed_tables = [t for t in fresh.vtables if t.va == int(seed['table'],16)]
    if (len(seed_tables) != 1 or seed_tables[0].klass != base or seed_tables[0].offset != 0
            or len(seed_tables[0].slots) <= slot
            or seed_tables[0].slots[slot] != int(seed['target'],16)):
        raise ValueError('class-name seed table/slot mismatch')
    family = [t for t in fresh.vtables if t.offset == 0
              and (base, 0) in fresh.class_bases.get(t.klass, [])]
    pointers = defaultdict(list)
    for section in prog.img.sections:
        if section.characteristics & 0x20000000:
            continue
        for offset in range(0, len(section.raw)-3, 4):
            pointers[struct.unpack_from('<I', section.raw, offset)[0]].append(section.start+offset)
    rows, admission = [], []
    for table in sorted(family, key=lambda t: t.va):
        if len(table.slots) <= slot:
            continue
        target = table.slots[slot]
        flags, code = [], prog.img.read(target, 6)
        fn = prog.by_va.get(target)
        col = prog.img.u32(table.va-4)
        if (table.offset != 0 or col is None or prog.img.u32(col) != 0
                or prog.img.u32(col+4) != 0 or prog.img.u32(col+8) != 0
                or [offset for name, offset in fresh.class_bases[table.klass] if name == base] != [0]
                or [offset for name, offset in fresh.fixed_bases.get(table.klass, []) if name == base] != [0]):
            flags.append('not a unique fixed primary base with zero constructor displacement')
        if prog.img.u32(table.va+4*slot) != target:
            flags.append('raw vtable word differs')
        if (prog.slots.get(target) != [(table.klass,table.offset,slot,table.va)]
                or pointers.get(target) != [table.va+4*slot]):
            flags.append('shared target or extra non-code pointer requires separate proof')
        if (fn is None or fn.lo != target or fn.hi != target+5 or fn.declared_hi != target+5
                or fn.body_ranges != 1 or fn.body_bytes != 6 or fn.thunk):
            flags.append('not an exact six-byte non-thunk function')
        value = int.from_bytes(code[1:5], 'little') if len(code) == 6 else 0
        if len(code) != 6 or code[0] != 0xb8 or code[5] != 0xc3:
            flags.append('not an immediate-EAX/plain-RET getter')
        section = prog.img.section_of(value)
        expected = table.klass.encode('ascii')+b'\0'
        if (section is None or not section.characteristics & 0x40
                or not section.characteristics & 0x40000000 or section.characteristics & 0x20000000
                or value+len(expected) > section.start+len(section.raw)
                or prog.img.read(value,len(expected)) != expected):
            flags.append('class literal is not matching initialized non-executable data')
        use = {'class':table.klass,'offset':table.offset,'table':f'0x{table.va:08x}',
               'slot':slot,'method':'_GetClassName','parameters':[],'qualifiers':''}
        rows.append({'target':f'0x{target:08x}', 'status':'withheld' if flags else 'caller-method-candidate',
                     'uses':[use], 'uncoveredHolders':[u for u in prog.slots.get(target, [])
                         if u != (table.klass,table.offset,slot,table.va)],
                     'leastDerivedHolders':[table.klass],
                     'bodySha256':hashlib.sha256(code).hexdigest(), 'stringAddress':f'0x{value:08x}',
                     'stringSha256':hashlib.sha256(expected).hexdigest(),
                     'stringSection':section.name if section else None,
                     'stringCharacteristics':section.characteristics if section else None,
                     'stringWritable':bool(section and section.characteristics & 0x80000000),
                     'dataPointerCells':[f'0x{a:08x}' for a in pointers.get(target, [])]})
        admission.append({'target':f'0x{target:08x}',
                          'status':'withheld' if flags else 'mechanical-checks-pass', 'flags':flags,
                          'observedReturnPop':[0] if not flags else []})
    if not any(int(r['target'],16) == int(seed['target'],16)
               and r['status'] == 'caller-method-candidate' for r in rows):
        raise ValueError('class-name seed getter did not pass admission')
    propagated, admitted = {'rows':rows}, {'rows':admission}
    limits = ('Reviewed source-call identity only; missing macro/declaration/qualifiers and possible '
              'inlined forwarding are not resolved. Writable initial class literals do not establish '
              'runtime immutability. No prototype promotion. Only exact primary unshared getters '
              'are admitted; semantic witness review and cohort gates remain required.')
    proposals = vtable_name_proposals(prog,propagated,admitted)
    proposals['limits'] = limits
    return dict(propagated, admission=admitted, proposals=proposals, limits=limits)


# ---------------------------------------------------------------------------
# Compiler deleting entries
# ---------------------------------------------------------------------------

def scalar_delete_entry(raw: bytes, address: int, manager: int, free: int) -> int | None:
    """Recognize one unadjusted x86 deleting-entry shape; return its cleanup callee.

    This is an authored instruction pattern, not an identity oracle. The caller
    must independently bind the destructor slot, cleanup chain and allocator.
    No other compiler variant, adjusted receiver or vector delete is admitted.
    """
    pattern = (bytes.fromhex('56 8b f1 e8') + bytes(4)
               + bytes.fromhex('f6 44 24 08 01 74 0b 56 b9')
               + struct.pack('<I', manager) + b'\xe8' + bytes(4)
               + bytes.fromhex('8b c6 5e c2 04 00'))
    masked = set(range(4, 8)) | set(range(22, 26))
    if len(raw) != 32 or any(raw[i] != pattern[i] for i in range(32) if i not in masked):
        return None
    target = lambda offset: (address + offset + 4 + struct.unpack_from('<i', raw, offset)[0]) & 0xffffffff
    if target(22) != free:
        return None
    return target(4)


_CLEANUP_OPS = frozenset(('add', 'call', 'cmp', 'dec', 'imul', 'inc', 'je', 'jl', 'jle',
                          'jmp', 'jne', 'lea', 'mov', 'pop', 'push', 'ret', 'sub', 'test', 'xor'))


def _function_cfg(prog: Program, address: int):
    """Exact saved extent and explicit normal control flow; unknown edges refuse."""
    fn = prog.by_va.get(address)
    if (fn is None or fn.lo != address or fn.body_ranges != 1
            or fn.declared_hi != fn.hi or fn.body_bytes != fn.hi - address + 1):
        raise ValueError('missing, clipped or noncontiguous function boundary')
    body = prog.body(fn)
    cursor = address
    for ins in body:
        if ins.va != cursor or ins.size <= 0 or ins.mnem in ('(bad)', '.byte', '.word', '.long'):
            raise ValueError('incomplete or invalid instruction decoding')
        if ins.mnem not in _CLEANUP_OPS:
            raise ValueError('unsupported instruction in cleanup: ' + ins.mnem)
        if ins.ops.split(',')[0] in ('esp', 'sp') and ins.mnem not in ('cmp', 'test', 'push') \
                and not (ins.mnem in ('add', 'sub') and re.fullmatch(r'esp,0x[0-9a-f]+', ins.ops)) \
                and not (ins.mnem == 'mov' and ins.ops == 'esp,ebp'):
            raise ValueError('opaque cleanup stack-pointer write')
        cursor += ins.size
    if cursor != fn.hi + 1 or len(prog.img.read(address, fn.body_bytes)) != fn.body_bytes:
        raise ValueError('instruction/body extent mismatch')
    insns = {i.va: i for i in body}
    edges, exits = {}, {}
    for ins in body:
        after = ins.va + ins.size
        if ins.mnem == 'ret':
            if ins.ops not in ('', '0x0'):
                raise ValueError('non-deleting cleanup pops arguments')
            edges[ins.va] = []
            exits[ins.va] = ('ret', None)
        elif ins.mnem.startswith(('j', 'loop')):
            if not _DIRECT.fullmatch(ins.ops):
                raise ValueError('unresolved indirect control-flow edge')
            dest = int(ins.ops, 16)
            if dest not in insns:
                if ins.mnem != 'jmp' or fn.lo <= dest <= fn.hi:
                    raise ValueError('branch outside body or into an instruction')
                edges[ins.va] = []
                exits[ins.va] = ('tail', dest)
            else:
                edges[ins.va] = [dest] + ([] if ins.mnem == 'jmp' else [after])
        else:
            edges[ins.va] = [after]
        if any(t not in insns for t in edges[ins.va]):
            raise ValueError('unresolved fallthrough beyond body')
    reachable, todo = set(), [address]
    while todo:
        node = todo.pop()
        if node not in reachable:
            reachable.add(node)
            todo.extend(edges[node])
    exits = {a: v for a, v in exits.items() if a in reachable}
    if not exits:
        raise ValueError('no normal return path')
    return fn, insns, edges, exits, reachable


def _this_after(ins: Insn, before: frozenset[str]) -> frozenset[str]:
    """Original-this provenance under the x86 nonvolatile-register convention.

    Calls clobber EAX/ECX/EDX. This does not certify callee behavior or unwinding.
    Memory reloads and partial writes lose proof. Unknown opcodes clear all
    provenance here and are refused by _function_cfg, including implicit writes
    (RDTSCP, string and BCD operations) and two-destination operations such as XADD.
    """
    after = set(before)
    if ins.mnem not in _CLEANUP_OPS:
        return frozenset()
    operands = ins.ops.split(',')
    aliases = {part: reg for reg, parts in (
        ('eax', ('eax', 'ax', 'al', 'ah')), ('ecx', ('ecx', 'cx', 'cl', 'ch')),
        ('edx', ('edx', 'dx', 'dl', 'dh')), ('ebx', ('ebx', 'bx', 'bl', 'bh')),
        ('esi', ('esi', 'si')), ('edi', ('edi', 'di')), ('ebp', ('ebp', 'bp')))
        for part in parts}
    if ins.mnem == 'call':
        return frozenset(after - {'eax', 'ecx', 'edx'})
    if ins.mnem == 'imul' and len(operands) == 1:
        after -= {'eax', 'edx'}
    if ins.mnem not in ('cmp', 'test', 'push', 'jmp', 'ret') and not ins.mnem.startswith(('j', 'loop')):
        dest = aliases.get(operands[0])
        if dest:
            after.discard(dest)
            if ins.mnem == 'mov' and len(operands) == 2 and operands[0] == dest and operands[1] in before:
                after.add(dest)
    return frozenset(after)


def destructor_teardown_chain(prog: Program, address: int, base: int, seen=frozenset()) -> dict:
    """Require a reviewed base teardown on every explicit normal return path.

    The base's complete bytes are pinned by compiler_destructors(). Normal CFG
    dominance and original-this propagation cover internal backward blocks;
    frameless direct tails additionally need a stack-neutral prefix. Exceptions,
    arbitrary callees' preservation and full cleanup semantics stay outside proof.
    """
    if address in seen or len(seen) >= 8:
        raise ValueError('teardown chain cycle or depth limit')
    fn, insns, edges, exits, reachable = _function_cfg(prog, address)
    evidence = {'address': f'0x{address:08x}', 'bytes': fn.body_bytes,
                'sha256': hashlib.sha256(prog.img.read(address, fn.body_bytes)).hexdigest(), 'exits': []}
    if address == base:
        if any(kind != 'ret' for kind, _ in exits.values()):
            raise ValueError('reviewed base has an unresolved tail')
        evidence['reviewedBase'] = True
        return evidence
    incoming = {address: frozenset({'ecx'})}
    todo = [address]
    while todo:
        node = todo.pop()
        state = _this_after(insns[node], incoming[node])
        for dest in edges[node]:
            merged = state if dest not in incoming else incoming[dest] & state
            if dest not in incoming or merged != incoming[dest]:
                incoming[dest] = merged
                todo.append(dest)
    preds = {a: set() for a in reachable}
    for a in reachable:
        for b in edges[a]:
            preds[b].add(a)
    dominators = {a: ({a} if a == address else set(reachable)) for a in reachable}
    changed = True
    while changed:
        changed = False
        for a in sorted(reachable - {address}):
            new = {a} | set.intersection(*(dominators[p] for p in preds[a]))
            if new != dominators[a]:
                dominators[a] = new
                changed = True
    for site, (kind, target) in sorted(exits.items()):
        if kind == 'tail':
            if 'ecx' not in incoming[site] or any(
                i.mnem in ('push', 'pop', 'call', 'enter', 'leave', 'pushf', 'popf', 'pusha', 'popa',
                           'pushad', 'popad', 'pushfd', 'popfd')
                or re.search(r'\b(?:esp|sp|ebp|bp|ss)\b', i.ops) for i in insns.values()):
                raise ValueError('tail lacks unchanged-this and stack-neutral proof')
            chain = destructor_teardown_chain(prog, target, base, seen | {address})
            evidence['exits'].append({'site': f'0x{site:08x}', 'kind': 'tail', 'chain': chain})
            continue
        candidates = [a for a in dominators[site] if insns[a].mnem == 'call'
                      and _DIRECT.fullmatch(insns[a].ops) and 'ecx' in incoming[a]]
        for call in sorted(candidates, key=lambda a: len(dominators[a]), reverse=True):
            try:
                chain = destructor_teardown_chain(prog, int(insns[call].ops, 16), base, seen | {address})
            except ValueError:
                continue
            evidence['exits'].append({'site': f'0x{site:08x}', 'kind': 'ret',
                                     'dominatingCall': f'0x{call:08x}', 'chain': chain})
            break
        else:
            raise ValueError('return lacks a dominating original-this base teardown')
    return evidence


def compiler_destructors(prog: Program, document: dict) -> dict:
    """Admit one reviewed zero-offset destructor family, never from saved names.

    This separate route does not fabricate missing headers or relax source ABI
    admission. Its seed/allocator/witness pins require independent semantic review.
    """
    if document.get('specimenSha256') != prog.img.sha256 or not document.get('evidence'):
        raise ValueError('compiler-entry evidence/specimen pin missing or mismatched')
    seed = document['seed']
    tables = {t.va: t for t in prog.model.rtti.vtables}
    table = tables.get(int(seed['table'], 16)); slot = seed['slot']
    if (table is None or table.klass != seed['class'] or table.offset != 0
            or type(slot) is not int or not 0 <= slot < len(table.slots)):
        raise ValueError('compiler-entry seed table/class/slot mismatch')
    target, base = int(seed['target'], 16), int(document['teardown']['address'], 16)
    manager, free = int(document['manager'], 16), int(document['deallocator']['address'], 16)
    for pin in [seed['body'], document['teardown'], document['deallocator'], *document.get('witnesses', [])]:
        address, size = int(pin['address'], 16), pin['bytes']
        if type(size) is not int or size <= 0 or len(prog.img.read(address, size)) != size \
                or hashlib.sha256(prog.img.read(address, size)).hexdigest() != pin['sha256']:
            raise ValueError('compiler-entry witness body hash/range mismatch')
    if (int(seed['body']['address'], 16) != target or seed['body']['bytes'] != 32
            or table.slots[slot] != target or prog.img.u32(table.va + slot * 4) != target
            or scalar_delete_entry(prog.img.read(target, 32), target, manager, free) != base):
        raise ValueError('compiler-entry seed shape/target mismatch')
    seedfn = prog.by_va.get(target)
    if (seedfn is None or seedfn.lo != target or seedfn.hi != target + 31
            or seedfn.declared_hi != target + 31 or seedfn.body_ranges != 1 or seedfn.body_bytes != 32):
        raise ValueError('compiler-entry seed function boundary mismatch')
    if prog.by_va.get(base) is None or prog.by_va[base].body_bytes != document['teardown']['bytes']:
        raise ValueError('reviewed teardown boundary mismatch')
    destructor_teardown_chain(prog, base, base)
    mapped, excluded = defaultdict(list), []
    for vt in tables.values():
        bases = [offset for klass, offset in prog.bases.get(vt.klass, []) if klass == seed['class']]
        fixed = [offset for klass, offset in prog.fixed_bases.get(vt.klass, []) if klass == seed['class']]
        if vt.offset != 0 or bases != [0] or fixed != [0] or slot >= len(vt.slots):
            if bases:
                excluded.append({'table': f'0x{vt.va:08x}', 'class': vt.klass, 'offset': vt.offset,
                                 'baseOffsets': bases, 'fixedOffsets': fixed,
                                 'reason': 'secondary/repeated/dynamic ancestry or missing slot'})
            continue
        address = vt.slots[slot]
        if prog.img.u32(vt.va + slot * 4) != address:
            raise ValueError('descendant destructor slot word mismatch')
        mapped[address].append({'class': vt.klass, 'offset': 0, 'slot': slot,
                               'table': f'0x{vt.va:08x}', 'method': 'scalar_deleting_dtor',
                               'parameters': ['deleting_flag_word'], 'qualifiers': ''})
    rows, admission = [], []
    for address, uses in sorted(mapped.items()):
        fn = prog.by_va.get(address)
        owners = sorted(prog.defining_classes(fn)) if fn else []
        covered = {(u['class'], 0, slot, int(u['table'], 16)) for u in uses}
        unknown = sorted(set(prog.slots.get(address, [])) - covered)
        row = {'target': f'0x{address:08x}', 'uses': uses, 'leastDerivedHolders': owners,
               'uncoveredHolders': unknown, 'status': 'compiler-destructor-candidate'}
        issues = []
        if unknown: issues.append('unmapped destructor aliases')
        if len(owners) != 1: issues.append('no unique RTTI naming owner')
        if (fn is None or fn.va != fn.lo or fn.body_ranges != 1 or fn.body_bytes != 32
                or fn.declared_hi != fn.va + 31 or fn.hi != fn.va + 31):
            issues.append('not an exact unadjusted compiler-entry extent')
        else:
            cleanup = scalar_delete_entry(prog.img.read(address, 32), address, manager, free)
            if cleanup is None:
                issues.append('not the reviewed unadjusted compiler-entry shape')
            else:
                row['cleanupTarget'] = f'0x{cleanup:08x}'
                row['bodySha256'] = hashlib.sha256(prog.img.read(address, 32)).hexdigest()
                try:
                    row['teardownProof'] = destructor_teardown_chain(prog, cleanup, base)
                except ValueError as error:
                    issues.append(str(error))
        rows.append(row)
        admission.append({'target': row['target'], 'status': 'withheld' if issues else 'mechanical-checks-pass',
                          'flags': sorted(set(issues))})
    proposals = vtable_name_proposals(prog, {'rows': rows}, {'rows': admission})
    proposals['limits'] = ('Compiler-entry kind and nonexclusive RTTI naming context, not original source spelling '
                          'or complete cleanup semantics. All names are output comparisons only. '
                          'Independent review and the full Ghidra gate precede mutation.')
    return {'rows': rows, 'excludedTables': excluded, 'admission': {'rows': admission}, 'proposals': proposals,
            'limits': 'Normal explicit control flow only; x86 callee-preserved register convention assumed. '
                      'No exception, callee internals, full ABI or runtime certification. '
                      'Only the reviewed cleanup instruction set is supported. Other wrapper shapes, '
                      'secondary/repeated bases, aliases and collisions are withheld.'}


# ---------------------------------------------------------------------------
# Anchors from strings
# ---------------------------------------------------------------------------

def mkid_discriminator(raw: bytes) -> int | None:
    """Closed x86 construction of a four-byte initial-image tag, compared to EAX.

    The four signed-byte loads must address literal+3,+2,+1,+0. This proves
    the comparison, not that writable literals remain unchanged at runtime.
    """
    if len(raw) != 45:
        return None
    literal = struct.unpack_from('<I', raw, 34)[0]
    if literal > 0xfffffffc:
        return None
    expected = (b'\x0f\xbe\x0d' + struct.pack('<I', literal + 3)
                + b'\x0f\xbe\x15' + struct.pack('<I', literal + 2)
                + b'\xc1\xe1\x08\x03\xca\x0f\xbe\x15' + struct.pack('<I', literal + 1)
                + b'\xc1\xe1\x08\x03\xca\x0f\xbe\x15' + struct.pack('<I', literal)
                + b'\xc1\xe1\x08\x03\xca\x3b\xc1')
    return literal if raw == expected else None


def _tag_flow(body: list[Insn], producers: set[int]) -> tuple[dict, dict]:
    """Normal-flow facts: EAX is the tag, ESI is its reader, EBP is zero.

    Calls use the reviewed x86 nonvolatile-register convention. Unknown
    opcodes destroy all facts. Exception paths and indirect branches are not
    admitted. Each producer is separately checked for its receiver and body.
    """
    insns = {i.va: i for i in body}
    edges, parents = {}, defaultdict(set)
    for ins in body:
        after = ins.va + ins.size
        if ins.mnem == 'call' and (not _DIRECT.fullmatch(ins.ops)
                or body[0].va <= int(ins.ops, 16) < body[-1].va + body[-1].size):
            raise ValueError('tag caller has an indirect or intra-caller call')
        if ins.mnem == 'ret':
            dests = []
        elif ins.mnem.startswith(('j', 'loop')):
            if not _DIRECT.fullmatch(ins.ops):
                raise ValueError('tag caller has an indirect control-flow edge')
            dests = [int(ins.ops, 16)] + ([] if ins.mnem == 'jmp' else [after])
        else:
            dests = [after]
        if any(d not in insns for d in dests):
            raise ValueError('tag caller has an exterior or interior-instruction edge')
        edges[ins.va] = dests
        for dest in dests:
            parents[dest].add(ins.va)
    states = defaultdict(set)
    states[body[0].va].add((False, False, False))
    todo = [body[0].va]
    harmless = {'cmp', 'test', 'push', 'nop', 'ret'}
    written = {'mov', 'movsx', 'movzx', 'lea', 'pop', 'add', 'sub', 'and', 'or',
               'xor', 'shl', 'shr', 'sar', 'inc', 'dec', 'neg', 'not', 'imul'}
    aliases = ({x: 0 for x in ('eax', 'ax', 'al', 'ah')}
               | {x: 1 for x in ('esi', 'si')} | {x: 2 for x in ('ebp', 'bp')})
    while todo:
        address = todo.pop()
        ins = insns[address]
        ops = ins.ops.split(',')
        for state in list(states[address]):
            result = list(state)
            if ins.mnem == 'call':
                result[0] = address in producers
                if address in producers:
                    result[1] = True
            elif ins.mnem in written and not (ins.mnem == 'imul' and len(ops) == 1):
                if ops[0] in aliases:
                    result[aliases[ops[0]]] = False
                if ((ins.mnem == 'xor' and ops == ['ebp', 'ebp'])
                        or (ins.mnem == 'mov' and ops == ['ebp', '0x0'])):
                    result[2] = True
            elif ins.mnem not in harmless and not ins.mnem.startswith('j') and not ins.mnem.startswith('set'):
                result = [False, False, False]
            elif ins.mnem.startswith('set') and ops[0] in aliases:
                result[aliases[ops[0]]] = False
            for dest in edges[address]:
                branch = result.copy()
                previous = next(iter(parents[address])) if len(parents[address]) == 1 else None
                if (ins.mnem in ('je', 'jne') and previous is not None
                        and insns[previous].mnem == 'test' and insns[previous].ops == 'ebp,ebp'
                        and previous + insns[previous].size == address):
                    equal = dest == int(ins.ops, 16) if ins.mnem == 'je' else dest == address + ins.size
                    if equal:
                        branch[2] = True
                value = tuple(branch)
                if value not in states[dest]:
                    states[dest].add(value)
                    todo.append(dest)
    return states, edges


def tagged_call_witnesses(prog: Program, document: dict, source_root: Path) -> dict:
    """Check a reviewed caller's literal-selected calls without using saved names.

    Results bind initial-image tags, reader transport and direct targets. A
    source clause containing preprocessor directives is withheld instead of
    selecting a convenient platform branch. Class identity, complete callee
    semantics and exceptions require separate evidence; this tool never edits
    Ghidra or invents owners from call expressions.
    """
    if document.get('specimenSha256') != prog.img.sha256:
        raise ValueError('tag witness specimen pin mismatch')

    def function(pin):
        address = int(pin['address'], 16)
        fn = prog.by_va.get(address)
        if fn is None or fn.thunk:
            raise ValueError('tag witness requires a non-thunk function entry')
        body = decode_entry_body(prog.img, fn)
        raw = prog.img.read(address, fn.body_bytes)
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise ValueError('tag witness complete-body pin mismatch')
        return fn, body

    caller, body = function(document['caller'])
    for dest, references in prog.model.refs_to.items():
        if caller.va < dest <= caller.hi and any(
                kind in ('call', 'jmp', 'jcc') and not caller.va <= site <= caller.hi
                for kind, site in references):
            raise ValueError('saved instruction model enters the caller past its entry')
    source = document['source']
    path = source_root / source['file']
    if Path(source['file']).name != source['file'] or hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('tag witness source path/hash mismatch')
    defs = [f for f in index_source(source_root) if f.file == source['file'] and f.key == source['function']]
    if len(defs) != 1 or not document.get('identityEvidence'):
        raise ValueError('tag caller source identity is ambiguous or unreviewed')
    src = defs[0]
    source_text = strip_comments(path.read_text(errors='replace'))
    if source_text.count(src.body) != 1:
        raise ValueError('tag caller source body position is ambiguous')
    source_offset = source_text.index(src.body)
    active_text, conditional_ranges = _header_conditions(source_text, set())
    if not re.search(r'CChunkReader\s*&\s*c\s*=\s*\*reader\s*;', src.body):
        raise ValueError('source reader alias is not explicit')
    insns = {i.va: i for i in body}
    diagnostics = document['diagnostics']
    if not diagnostics:
        raise ValueError('tag caller has no independent diagnostic anchor')
    for row in diagnostics:
        literal, site = int(row['address'], 16), int(row['site'], 16)
        if (prog.img.cstring(literal) != row['text'] or row['text'] not in src.literals
                or site not in insns or (insns[site].mnem, insns[site].ops) != ('push', hex(literal))):
            raise ValueError('tag caller diagnostic anchor differs')
    producer, _ = function(document['producer'])
    sites = {int(v, 16) for v in document['producer']['calls']}
    actual = {i.va for i in body if i.mnem == 'call' and i.ops == hex(producer.va)}
    if not sites or sites != actual:
        raise ValueError('tag producer call census differs')
    for site in sites:
        before = insns.get(site - 2)
        if before is None or (before.mnem, before.ops, before.size) != ('mov', 'ecx,esi', 2):
            raise ValueError('tag producer receiver is not the selected reader')
    states, edges = _tag_flow(body, sites)
    for site in sites:
        if any(src != site - 2 and site in dests for src, dests in edges.items()):
            raise ValueError('tag producer call bypasses its receiver transport')
    rows, seen = [], set()
    for claim in document['calls']:
        tag = claim['tag']
        if tag in seen or not re.fullmatch('[A-Z0-9]{4}', tag):
            raise ValueError('duplicate or unsupported tag')
        seen.add(tag)
        start = int(claim['start'], 16)
        literal = mkid_discriminator(prog.img.read(start, 45))
        if (literal is None or prog.img.read(literal, 4) != tag.encode('ascii')
                or start not in insns or not states[start]
                or not all(t and r for t, r, _ in states[start])):
            raise ValueError('tag comparison or producer/reader provenance differs')
        branch = insns.get(start + 45)
        if branch is None or branch.mnem != 'jne' or not _DIRECT.fullmatch(branch.ops):
            raise ValueError('tag action is not guarded by equality')
        end = int(branch.ops, 16)
        block = [i for i in body if branch.va + branch.size <= i.va < end]
        target, target_body = function(claim['target'])
        if len(block) < 3 or block[-1].mnem != 'jmp' or not _DIRECT.fullmatch(block[-1].ops):
            raise ValueError('tag action lacks a direct common continuation')
        join = int(block[-1].ops, 16)
        if join not in insns or start <= join < end:
            raise ValueError('tag action rejoins inside its witness')
        calls = [i for i in block if i.mnem == 'call']
        if len(calls) != 1 or calls[0].ops != hex(target.va) or calls[0].va != int(claim['call'], 16):
            raise ValueError('tag action direct callee differs')
        call = calls[0]
        pushes, receiver = [], None
        for ins in block:
            if ins.va >= call.va:
                break
            if ins.mnem == 'push' and ins.ops in ('esi', '0x0', 'ebp'):
                if ins.ops == 'ebp' and not all(z for _, _, z in states[start]):
                    raise ValueError('tag argument register is not proven zero')
                pushes.append('reader' if ins.ops == 'esi' else 'zero')
            elif ins.mnem == 'mov' and re.fullmatch(r'ecx,0x[0-9a-f]+', ins.ops) and receiver is None:
                receiver = int(ins.ops.split(',')[1], 16)
            else:
                raise ValueError('unsupported or clobbering tag transport')
        arguments = list(reversed(pushes))
        if arguments.count('reader') != 1 or len(arguments) not in (1, 2):
            raise ValueError('tag consumer must receive the selected reader exactly once')
        if arguments != claim['arguments'] or receiver != (int(claim['receiver'], 16) if claim.get('receiver') else None):
            raise ValueError('tag reader/receiver/argument transport differs')
        after = [i for i in block if call.va < i.va < block[-1].va]
        cleanup = 0
        if after:
            if len(after) != 1 or (after[0].mnem, after[0].ops) != ('add', f'esp,0x{4*len(pushes):x}'):
                raise ValueError('unsupported post-call tag action')
            cleanup = 4 * len(pushes)
        # Observed RET instructions are not by themselves normal-path proof:
        # an unreachable RET may follow a tail jump or computed dispatch.
        returns = {int(i.ops, 16) if i.ops else 0 for i in target_body if i.mnem == 'ret'}
        if not returns or returns != {4 * len(pushes) - cleanup}:
            raise ValueError('tag callee observed RET immediates contradict transport')
        target_insns = {i.va: i for i in target_body}
        reached, pending, exterior, reached_returns = set(), [target.va], set(), set()
        indirect = False
        while pending:
            address = pending.pop()
            if address in reached:
                continue
            reached.add(address)
            ins = target_insns[address]
            if ins.mnem == 'ret':
                reached_returns.add(int(ins.ops, 16) if ins.ops else 0)
                continue
            if ins.mnem.startswith(('j', 'loop')):
                if not _DIRECT.fullmatch(ins.ops):
                    indirect = True
                    continue
                destinations = [int(ins.ops, 16)] + ([] if ins.mnem == 'jmp' else [address+ins.size])
            else:
                destinations = [address+ins.size]
            for dest in destinations:
                if dest in target_insns:
                    pending.append(dest)
                else:
                    exterior.add(dest)
        for origin, destinations in edges.items():
            if not start <= origin < end and any(start < dest < end for dest in destinations):
                raise ValueError('tag witness has an interior entry')
        for dest, references in prog.model.refs_to.items():
            if start < dest < end and any(kind in ('call', 'jmp', 'jcc') and not start <= site < end
                                          for kind, site in references):
                raise ValueError('saved instruction model has an exterior entry into tag witness')
        clauses = list(re.finditer(r'\bif\s*\(\s*tag\s*==\s*MKID\(\s*"'+tag+r'"\s*\)\s*\)\s*\{', src.body))
        expression, status = None, 'source-clause-withheld'
        if len(clauses) == 1:
            clause_start = source_offset + clauses[0].start()
            prefix_end = source_offset + clauses[0].end()
            outer_conditional = (active_text[clause_start:prefix_end] != source_text[clause_start:prefix_end]
                                 or any(lo < prefix_end and hi > clause_start for lo, hi in conditional_ranges))
            tail = src.body[clauses[0].end():]
            finish = tail.find('}')
            clause = tail[:finish].strip() if finish >= 0 else ''
            if (clause and not outer_conditional and '#' not in clause and '{' not in clause
                    and re.fullmatch(r'[\w:]+(?:(?:\.|->)\w+(?:\(\))?)*\(\s*&c\s*\)\s*;', clause)):
                expression = re.sub(r'\s+', '', clause)
                status = 'tag-call-and-source-clause'
        if claim.get('sourceCall') and expression != re.sub(r'\s+', '', claim['sourceCall']):
            raise ValueError('source call is absent, conditional or mismatched')
        rows.append(dict(tag=tag, literal=f'{literal:08x}', start=f'{start:08x}',
                         call=f'{call.va:08x}', target=f'{target.va:08x}',
                         arguments=arguments, receiver=receiver, observedReturnPop=sorted(returns),
                         reachableExplicitReturnPop=(sorted(reached_returns) if not indirect and not exterior else None),
                         indirectCalleeFlow=indirect, unresolvedCalleeTargets=[f'{a:08x}' for a in sorted(exterior)],
                         sourceCall=expression, status=status,
                         bodySha256=claim['target']['sha256']))
    return dict(rows=rows, limits='Initial image and explicit normal caller flow only; reviewed producer identity and nonvolatile-register ABI are premises. No owner/type inference, callee ESP-balance/exception/computed-flow proof, real asset loading or runtime immutability.')


def string_users(prog: "Program") -> dict[int, set[int]]:
    """Retail string VA -> functions whose bodies reference it."""
    users: dict[int, set[int]] = defaultdict(set)
    for a in prog.model.strings:
        for _k, site in prog.model.refs_to.get(a, []):
            f = prog.func_at(site)
            if f:
                users[a].add(f.va)
    return users


def next_call_after(prog: "Program", site: int, limit: int = 12) -> int | None:
    """Target of the first direct call within `limit` instructions after `site`."""
    i = bisect.bisect_left(prog.insn_vas, site)
    for ins in prog.model.insns[i + 1:i + 1 + limit]:
        if ins.mnem == "call":
            return int(ins.ops, 16) if _DIRECT.match(ins.ops) else None
        if ins.mnem in ("ret", "jmp"):
            return None
    return None


_MACRO_CALLEES = {"ToTCHAR", "ToWCHAR", "TEXT", "MKID", "TRACE", "SASSERT", "ASSERT", "CHECK_D3D_STATE", "_T", "L"}


def string_anchors(prog: "Program", src: list[SourceFunc]):
    """Return (body_anchors, callee_anchors).

    body_anchors: retail function va -> {source key} for literals unique to one source
    function and referenced by exactly one retail function.
    callee_anchors: retail callee va -> Counter of source callee texts, from source calls
    whose literal argument is pushed shortly before that retail call."""
    from collections import Counter
    by_text: dict[str, list[int]] = defaultdict(list)
    for a, t in prog.model.strings.items():
        by_text[t].append(a)
    users = string_users(prog)
    lit_owner: dict[str, set[str]] = defaultdict(set)
    for sf in src:
        for lit in sf.literals:
            lit_owner[lit].add(sf.key)
    body: dict[int, set[str]] = defaultdict(set)
    for lit, keys in lit_owner.items():
        if len(keys) != 1 or len(lit) < 6:
            continue
        addrs = by_text.get(lit, [])
        fs = set().union(*(users.get(a, set()) for a in addrs)) if addrs else set()
        if len(fs) == 1:
            body[next(iter(fs))].add(next(iter(keys)))
    callee: dict[int, Counter] = defaultdict(Counter)
    for sf in src:
        for text, lit, _argidx in sf.lit_calls:
            last = re.split(r"::|\.|->", text)[-1]
            if last in _MACRO_CALLEES or text in _MACRO_CALLEES or len(lit) < 4:
                continue
            for a in by_text.get(lit, []):
                for kind, site in prog.model.refs_to.get(a, []):
                    if kind != "imm":
                        continue
                    t = next_call_after(prog, site)
                    if t is not None:
                        callee[t][text] += 1
    return body, callee


def file_line_anchors(prog: "Program", src: list[SourceFunc]) -> dict[int, list[tuple[str, int, str | None]]]:
    """Retail function va -> [(source file, line, source function key or None)] from the debug allocation sites
    (`push LINE; push "C:\\dev\\ONSLAUGHT2\\File.cpp"; push TAG; push SIZE; call Alloc`). The file is proven; the
    line names the pinned source's function that spans it, which is a lead where the revisions drift. Header files
    carry inlined code and anchor nothing; the compiler's unwind funclets past LIB_HI are skipped."""
    index = {i.va: n for n, i in enumerate(prog.model.insns)}
    by_file: dict[str, list[SourceFunc]] = defaultdict(list)
    for sf in src:
        by_file[sf.file.lower()].append(sf)
    out: dict[int, list[tuple[str, int, str | None]]] = defaultdict(list)
    for a, text in prog.model.strings.items():
        m = re.search(r"([^\\/]+\.(?:cpp|c))$", text.strip(), re.I)
        if not m:
            continue
        for _kind, site in prog.model.refs_to.get(a, []):
            n = index.get(site)
            if not n or prog.model.insns[n - 1].mnem != "push":
                continue
            try:
                line = int(prog.model.insns[n - 1].ops, 16)
            except ValueError:
                continue
            f = prog.func_at(site)
            if f is None or not 0 < line < 100000 or f.va >= LIB_HI:
                continue
            key = next((sf.key for sf in by_file.get(m.group(1).lower(), []) if sf.line <= line <= sf.end_line), None)
            out[f.va].append((m.group(1), line, key))
    return out


def file_drift(anchors: dict[int, list], names: dict[int, str], src: list[SourceFunc], span: int = 400) -> dict:
    """Per source file, the line shift that puts the most anchored lines inside the source function each retail
    function's saved name names (the pinned revision's lines drift from the retail build's in some files)."""
    by_key = {sf.key: sf for sf in src}
    sites: dict[str, list[tuple[int, SourceFunc]]] = defaultdict(list)
    for va, lst in anchors.items():
        sf = by_key.get(names.get(va, "").replace("__", "::"))
        for file, line, _key in lst:
            if sf and sf.file.lower() == file.lower():
                sites[file.lower()].append((line, sf))
    out = {}
    for file, pairs in sites.items():
        best = max(range(-span, span + 1),
                   key=lambda d: (sum(1 for line, sf in pairs if sf.line <= line - d <= sf.end_line), -abs(d)))
        out[file] = best
    return out


_STRUCTURAL = re.compile(r"^FUN_|^Shared\w*VFunc__|VFunc_?\d*_[0-9a-f]{8}$|__Func_[0-9a-f]{8}$|_T3_[0-9a-f]{8}$|"
                         r"^\w+VFunc__")


def audit(prog: "Program", src: list[SourceFunc], graph: dict | None = None, calls=None) -> list[dict]:
    """One evidence row per user-defined game function name (library code excluded): what supports the name,
    what contradicts it, and a verdict. graph: re_source_graph.check() report over the same functions.
    verified: the name is a pinned-source definition and a line anchor (after its file's drift) or a string
      anchor names it. This is an automated evidence lead, not a completed semantic disposition;
    contradicted: an anchor names another function, its calls or return disagree with the source, its owner is
      not the class that defines it, or a tiny body contradicts the name;
    neutral: a structural placeholder (FUN_, SharedVFunc__, Class__VFunc_NN_addr, ...) that claims no identity;
    unsupported: nothing above supports it (a descriptive name, or a source name with no anchor).
    calls(key, file) -> short names the source function reaches, inlined helpers included (re_source_graph.reach):
    an anchor inside a function the named one calls is evidence for the name, since the build inlines them."""
    keys = {sf.key for sf in src}
    anchors = file_line_anchors(prog, src)
    names = {f.va: f.name for f in prog.funcs}
    drift = file_drift(anchors, names, src)
    by_file: dict[str, list[SourceFunc]] = defaultdict(list)
    for sf in src:
        by_file[sf.file.lower()].append(sf)
    body, _callee = string_anchors(prog, src)
    rows_g = {int(r["address"], 16): r for r in (graph or {}).get("rows", [])}
    out = []
    for f in prog.funcs:
        if f.source != "USER_DEFINED" or LIB_LO <= f.va < LIB_HI or f.va >= LIB_HI:
            continue
        owner, method = split_name(f.name)
        key = f.name.replace("__", "::")
        if key.endswith("::ctor") and owner:
            key = key[:-6] + "::" + owner.split("__")[-1]
        elif key.endswith("::dtor") and owner:
            key = key[:-6] + "::~" + owner.split("__")[-1]
        in_source = key in keys
        pro, con = [], []
        reach = calls(key, next((sf.file for sf in src if sf.key == key), None)) if (calls and in_source) else set()
        for file, line, _k in anchors.get(f.va, []):
            d = drift.get(file.lower(), 0)
            hit = next((sf.key for sf in by_file.get(file.lower(), []) if sf.line <= line - d <= sf.end_line), None)
            where = f"{file}:{line}" + (f" (drift {d:+d})" if d else "")
            if hit == key:
                pro.append(where)
            elif hit and hit.split("::")[-1] in reach:
                pro.append(f"{where} in {hit}, which it calls (inlined)")
            elif hit:
                con.append(f"{where} is in {hit}")
        for k in sorted(body.get(f.va, ())):
            if k == key:
                pro.append(f"string unique to {k}")
            elif k.split("::")[-1] in reach:
                pro.append(f"string unique to {k}, which it calls (inlined)")
            else:
                con.append(f"string unique to {k}")
        defs = prog.defining_classes(f)
        holders = {klass for klass, _offset, _slot, _table in prog.slots.get(f.va, [])}
        # A derived override can fold into its base's identical body. Pruning
        # inherited slots cannot distinguish that from simple inheritance and
        # must not contradict a saved owner that actually holds the body.
        if defs and owner and owner not in holders and not any(prog.is_ancestor(owner, d) for d in defs):
            con.append(f"vtables say it belongs to {'/'.join(sorted(defs))}")
        g = rows_g.get(f.va)
        # A manual mapping may test another identity at the same address.
        # Pins establish its inputs, not agreement with this saved name. A
        # /N overload selection is also withheld: the saved name chooses none.
        if g and g.get("source") == key:
            con.extend(g["contradictions"])
        tiny = check_tiny_name(method, tiny_semantics(prog, f))
        if tiny == "disagree":
            con.append("its tiny body contradicts the name")
        if _STRUCTURAL.search(f.name) and not in_source:
            verdict = "contradicted" if tiny == "disagree" else "neutral"
        elif con:
            verdict = "contradicted"
        # A compatible graph is not a unique method identity. In particular an
        # empty graph row plus a matching RTTI class proves no source method.
        elif in_source and pro:
            verdict = "verified"
        else:
            verdict = "unsupported"
        out.append({"address": f"0x{f.va:08x}", "name": f.name, "verdict": verdict, "inSource": in_source,
                    "definers": ";".join(sorted(defs)), "for": " | ".join(pro), "against": " | ".join(con)})
    return out


# ---------------------------------------------------------------------------
# Statically linked library code
# ---------------------------------------------------------------------------

# The game's last object file ends at CWaterRenderSystem (0x0055d5dc); the DLL import stubs follow
# (0x0055d5e0-0x0055d69f); linked library code runs from 0x0055d6a0 to the compiler's EH funclets
# (first Unwind@ at 0x005d0f10). Library identities come from tools/re_lib_match.py.
LIB_LO, LIB_HI = 0x0055D6A0, 0x005D0F10


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("model")
    m.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("audit", help="evidence and a verdict for every user-defined game function name")
    a.add_argument("--functions", type=Path, required=True)
    a.add_argument("--graph", type=Path, help="a re_source_graph.py report over the same export")
    a.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("facts")
    c.add_argument("--functions", type=Path, required=True)
    c.add_argument("--out", type=Path, required=True)
    v = sub.add_parser('vtables', help='header layouts and optional reviewed-anchor propagation; candidates only')
    v.add_argument('--functions', type=Path, required=True)
    v.add_argument('--source', type=Path, default=SOURCE)
    v.add_argument('--model', type=Path, required=True)
    v.add_argument('--undefine', action='append', default=[])
    v.add_argument('--anchors', type=Path)
    v.add_argument('--out', type=Path, required=True, help='new private JSON report')
    d = sub.add_parser('destructors', help='reviewed compiler-entry family with pinned teardown evidence')
    d.add_argument('--functions', type=Path, required=True)
    d.add_argument('--source', type=Path, default=SOURCE)
    d.add_argument('--model', type=Path, required=True)
    d.add_argument('--evidence', type=Path, required=True)
    d.add_argument('--out', type=Path, required=True, help='new private JSON report')
    n = sub.add_parser('class-names', help='reviewed caller and exact class-literal getter family')
    n.add_argument('--functions', type=Path, required=True)
    n.add_argument('--source', type=Path, default=SOURCE)
    n.add_argument('--model', type=Path, required=True)
    n.add_argument('--evidence', type=Path, required=True)
    n.add_argument('--out', type=Path, required=True, help='new private JSON report')
    t = sub.add_parser('tag-calls', help='reviewed literal-selected calls; no inferred class owners')
    t.add_argument('--functions', type=Path, required=True)
    t.add_argument('--source', type=Path, default=SOURCE)
    t.add_argument('--model', type=Path, required=True)
    t.add_argument('--evidence', type=Path, required=True)
    t.add_argument('--out', type=Path, required=True, help='new private JSON report')
    l = sub.add_parser('typed-lists', help='reviewed intrusive-list interface and fixed-primary RTTI family')
    l.add_argument('--functions', type=Path, required=True)
    l.add_argument('--source', type=Path, default=SOURCE)
    l.add_argument('--model', type=Path, required=True)
    l.add_argument('--evidence', type=Path, required=True)
    l.add_argument('--out', type=Path, required=True, help='new private JSON report')
    args = ap.parse_args(argv)
    if args.cmd == 'typed-lists':
        if args.out.exists():
            ap.error('typed-list report must be a new path')
        img, model = load_or_build(args.model)
        prog = Program(img, model, load_functions(args.functions))
        import re_source_graph as G
        pins = G.input_pins(args.functions, args.source, ('*.cpp', '*.h'))
        try:
            document = json.loads(args.evidence.read_text())
            if document.get('sourceSha256') != pins['sourceSha256']:
                raise ValueError('typed-list source content pin mismatch')
            report = typed_list_virtuals(prog, document, args.source)
        except (KeyError, TypeError, ValueError) as error:
            ap.error(str(error))
        report['inputs'] = dict(pins, specimenSha256=img.sha256,
                               evidenceSha256=hashlib.sha256(args.evidence.read_bytes()).hexdigest())
        with args.out.open('x') as stream:
            stream.write(json.dumps(report, indent=1)+'\n')
        from collections import Counter
        print('Typed-list proposals:', json.dumps(Counter(r['status'] for r in report['proposals']['rows']), sort_keys=True))
        return 0
    if args.cmd == 'tag-calls':
        if args.out.exists():
            ap.error('tag-call report must be a new path')
        img, model = load_or_build(args.model)
        prog = Program(img, model, load_functions(args.functions))
        import re_source_graph as G
        pins = G.input_pins(args.functions, args.source, ('*.cpp', '*.h'))
        try:
            document = json.loads(args.evidence.read_text())
            if document.get('sourceSha256') != pins['sourceSha256']:
                raise ValueError('tag-call source content pin mismatch')
            report = tagged_call_witnesses(prog, document, args.source)
        except (KeyError, TypeError, ValueError) as error:
            ap.error(str(error))
        report['inputs'] = dict(pins, specimenSha256=img.sha256,
                               evidenceSha256=hashlib.sha256(args.evidence.read_bytes()).hexdigest())
        with args.out.open('x') as stream:
            stream.write(json.dumps(report, indent=1)+'\n')
        from collections import Counter
        print('Tag-call witnesses:', json.dumps(Counter(r['status'] for r in report['rows']), sort_keys=True))
        return 0
    if args.cmd == 'class-names':
        if args.out.exists():
            ap.error('class-name report must be a new path')
        img, model = load_or_build(args.model)
        prog = Program(img, model, load_functions(args.functions))
        import re_source_graph as G
        pins = G.input_pins(args.functions, args.source, ('*.cpp', '*.h'))
        try:
            document = json.loads(args.evidence.read_text())
            if document.get('sourceSha256') != pins['sourceSha256']:
                raise ValueError('class-name source content pin mismatch')
            report = class_name_getters(prog, document, args.source)
        except (KeyError, TypeError, ValueError) as error:
            ap.error(str(error))
        report['inputs'] = dict(pins, specimenSha256=img.sha256,
                               evidenceSha256=hashlib.sha256(args.evidence.read_bytes()).hexdigest())
        with args.out.open('x') as stream:
            stream.write(json.dumps(report, indent=1)+'\n')
        from collections import Counter
        print('Class-name proposals:', json.dumps(Counter(r['status'] for r in report['proposals']['rows']), sort_keys=True))
        return 0
    if args.cmd == 'destructors':
        if args.out.exists():
            ap.error('compiler-entry report must be a new path')
        img, model = load_or_build(args.model)
        prog = Program(img, model, load_functions(args.functions))
        import re_source_graph as G
        pins = G.input_pins(args.functions, args.source, ('*.cpp', '*.h'))
        try:
            document = json.loads(args.evidence.read_text())
            if document.get('sourceSha256') != pins['sourceSha256']:
                raise ValueError('compiler-entry source content pin mismatch')
            report = compiler_destructors(prog, document)
        except (KeyError, TypeError, ValueError) as error:
            ap.error(str(error))
        report['inputs'] = dict(pins, specimenSha256=img.sha256,
                               evidenceSha256=hashlib.sha256(args.evidence.read_bytes()).hexdigest())
        with args.out.open('x') as stream:
            stream.write(json.dumps(report, indent=1) + '\n')
        from collections import Counter
        print('Compiler-entry proposals:', json.dumps(Counter(r['status'] for r in report['proposals']['rows']), sort_keys=True))
        return 0
    if args.cmd == 'vtables':
        if args.out.exists():
            ap.error('vtable report must be a new path')
        img, model = load_or_build(args.model)
        prog = Program(img, model, load_functions(args.functions))
        classes = header_classes(args.source, set(args.undefine))
        report = align_header_vtables(prog, classes)
        import re_source_graph as G
        report['inputs'] = G.input_pins(args.functions, args.source, ('*.cpp', '*.h'))
        report['inputs']['specimenSha256'] = img.sha256
        report['inputs']['undefinedMacros'] = sorted(set(args.undefine))
        if args.anchors:
            report['inputs']['anchorsSha256'] = hashlib.sha256(args.anchors.read_bytes()).hexdigest()
            try:
                anchors = json.loads(args.anchors.read_text())
                if anchors.get('sourceSha256') != report['inputs']['sourceSha256']:
                    raise ValueError('anchor source content pin mismatch')
                report['anchored'] = propagate_vtable_anchors(prog, classes, anchors, args.source)
                report['admission'] = vtable_abi_admission(prog, classes, anchors, report['anchored'], args.source)
                report['proposals'] = vtable_name_proposals(prog, report['anchored'], report['admission'])
            except (KeyError, TypeError, ValueError) as e:
                ap.error(str(e))
        with args.out.open('x') as stream:
            stream.write(json.dumps(report, indent=1)+'\n')
        print(f"{len({r['class'] for r in report['rows']})} complete header/table candidate classes; "
              f"{len(report['rows'])} slots; {len({r['target'] for r in report['rows']})} distinct targets; "
              f"{len(report['withheld'])} classes withheld")
        if 'anchored' in report:
            from collections import Counter
            print(json.dumps(Counter(r['status'] for r in report['anchored']['rows']), sort_keys=True))
            print('ABI admission:', json.dumps(Counter(r['status'] for r in report['admission']['rows']), sort_keys=True))
            print('Name proposals:', json.dumps(Counter(r['status'] for r in report['proposals']['rows']), sort_keys=True))
        return 0
    if args.cmd == "audit":
        img, model = load_or_build(args.out / "model.pickle")
        prog = Program(img, model, load_functions(args.functions))
        import re_source_graph as G
        gsrc = G.index(SOURCE, ("*.cpp", "*.h"), set())
        graph = json.loads(args.graph.read_text()) if args.graph else None
        if graph is not None:
            pins = graph.get('inputs', {})
            expected = G.input_pins(args.functions, SOURCE, ('*.cpp', '*.h'))
            if any(pins.get(key) != value for key, value in expected.items()):
                ap.error('graph inputs are stale or unpinned; regenerate with re_source_graph.py check')
        rows = audit(prog, index_source(SOURCE), graph,
                     lambda key, file: G.reach(gsrc, key, file))
        with (args.out / "name-audit.tsv").open("w") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        from collections import Counter
        print(json.dumps(Counter(r["verdict"] for r in rows), indent=2))
        return 0
    if args.cmd == "facts":
        img, model = load_or_build(args.out / "model.pickle")
        prog = Program(img, model, load_functions(args.functions))
        from collections import Counter
        cnt = Counter()
        for fn in prog.funcs:
            if fn.source != "USER_DEFINED":
                continue
            owner, method = split_name(fn.name)
            d = prog.defining_classes(fn)
            if d:
                cnt["virtual"] += 1
                if len(d) == 1:
                    cnt["virtual_single_definer"] += 1
                    if owner == next(iter(d)):
                        cnt["owner_matches_definer"] += 1
                    elif owner is None:
                        cnt["owner_absent"] += 1
                    else:
                        cnt["owner_differs"] += 1
                else:
                    cnt["virtual_multi_definer"] += 1
            else:
                cnt["nonvirtual"] += 1
            if prog.strings_used(fn):
                cnt["uses_strings"] += 1
        print(json.dumps(cnt, indent=2))
        return 0
    if args.cmd == "model":
        img, model = load_or_build(args.out / "model.pickle")
        summary = {
            "specimenSha256": model.sha256, "instructions": len(model.insns), "strings": len(model.strings),
            "imports": len(model.imports), "rttiClasses": len(model.rtti.class_bases),
            "vtables": len(model.rtti.vtables), "vtableSlots": sum(len(v.slots) for v in model.rtti.vtables),
        }
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    # Run under the module name so cached pickles resolve re_name_evidence.Model, not __main__.Model.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import re_name_evidence
    sys.exit(re_name_evidence.main())
