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
            self.sections.append(Section(name, self.base + s.VirtualAddress, max(s.Misc_VirtualSize, len(raw)), raw))
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
    insns: list[Insn] = []
    for line in out.splitlines():
        m = _OBJDUMP_LINE.match(line)
        if not m:
            continue
        va = int(m.group(1), 16)
        size = len(m.group(2).split())
        text = m.group(3).strip()
        if not text:
            continue
        parts = text.split(None, 1)
        mnem = parts[0]
        ops = parts[1] if len(parts) > 1 else ""
        # drop objdump's symbolic comments such as "# 0x..." or "<...>"
        ops = ops.split("#", 1)[0].strip()
        insns.append(Insn(va, size, mnem, ops))
    return insns


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


def tiny_semantics(prog: "Program", f: Func, limit: int = 6) -> str | None:
    """Canonical description of a very small body, or None.

    Forms: noop:retN, const:V:retN, field:OFF:retN, this:retN, fconst:ADDR:retN,
    store:OFF:SRC:retN, thunk:TARGET, jmpimport:NAME."""
    body = [i for i in prog.body(f) if i.mnem not in _PAD]
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


def propagate_vtable_anchors(prog: Program, classes: dict[str, HeaderClass], document: dict) -> dict:
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
        anchors.append((anchor, table, methods[0]))
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


def vtable_abi_admission(prog: Program, classes: dict[str, HeaderClass], document: dict, propagated: dict) -> dict:
    """Apply the same return/alias/boundary checks to every proposed method identity.

    This is the mechanical part of cohort admission. An independent review must
    establish the anchors' semantics once, and examine all flagged rows. A pass
    supports a method identity under those anchors, not full behavior or ABI types.
    """
    import re_source_graph as G
    anchor_by_slot = {(int(a['table'],16), a['slot']): a for a in document['anchors']}

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
        body = prog.body(fn)
        cursor = fn.va
        for ins in body:
            if ins.va != cursor:
                issues.add('instruction decoding does not cover the exact function range')
            cursor = ins.va + ins.size
        if cursor != fn.hi+1:
            issues.add('instruction decoding does not cover the exact function range')
        if not body or body[-1].mnem not in ('ret', 'jmp'):
            issues.add('unresolved fallthrough beyond function range')
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
            method=next(m for m in classes[a['class']].methods if m.name==a['method']
                        and m.parameters==tuple(a['parameters']) and m.qualifiers==a.get('qualifiers',''))
            sf=SourceFunc(method.owner+'::'+method.name,method.file,method.line,'',[],[],
                          args=', '.join(method.parameters),head=method.head)
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
        tiny=tiny_semantics(prog,fn) if fn else None
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
        rows.append({'target':row['target'],'status':'mechanical-checks-pass' if not issues else 'withheld',
                     'expectedReturnPop':sorted(expected),'observedReturnPop':sorted(actual),
                     'flags':sorted(set(issues))})
    return {'rows':rows,'limits':'Conditional on independently rederived seed identities. '
            'Current function ranges and direct tail paths are checked; indirect tails and other unresolved '
            'paths are withheld. No return/parameter type or runtime-behavior certification. '
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
    args = ap.parse_args(argv)
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
                report['anchored'] = propagate_vtable_anchors(prog, classes, anchors)
                report['admission'] = vtable_abi_admission(prog, classes, anchors, report['anchored'])
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
