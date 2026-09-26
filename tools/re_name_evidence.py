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
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIMEN = ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
SOURCE = ROOT / "references/Onslaught"
IMAGE_BASE = 0x400000
MODEL_VERSION = 3   # 2: bare ds:0x memory operands are memory references; 3: strict RTTI census


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
    for h in census.hierarchies.values():
        class_bases.setdefault(plain(h.root_class),
                               [(plain(r.descriptor.class_name), r.descriptor.mdisp) for r in h.rows])
    slots: dict[int, list[int]] = defaultdict(list)
    for slot in sorted(census.slots, key=lambda x: (x.vtable_va, x.slot)):
        slots[slot.vtable_va].append(slot.function_va)
    vtables = [Vtable(va, plain(v.class_name), census.cols[v.col_va].offset, slots[va])
               for va, v in sorted(census.vtables.items())]
    return RttiModel(type_names, class_bases, vtables)


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


def load_functions(path: Path) -> list[Func]:
    out = []
    with path.open() as f:
        for r in csv.DictReader(f, delimiter="\t"):
            va = int(r["address"], 16)
            out.append(Func(va, r["name"], r["nameSource"], int(r["bodyMin"], 16), int(r["bodyMax"], 16),
                            r["signature"], r["callingConv"], r["commentPresent"] == "true", r["tags"],
                            r["isThunk"] == "true"))
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
        """Classes that introduce or override f: holders none of whose own bases also hold f
        at the same slot of the matching vtable."""
        holders = self.slots.get(f.va, [])
        classes = {k for k, _o, _i, _v in holders}
        minimal = set()
        for k in classes:
            if not any(self.is_ancestor(other, k) for other in classes if other != k):
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


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group().count("\n"), text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def index_source(root: Path = SOURCE) -> list[SourceFunc]:
    out = []
    for path in sorted(root.glob("*.cpp")):
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
            out.append(SourceFunc(key, path.name, text.count("\n", 0, m.start()) + 1, body, literals, calls))
    return out


def source_key_to_name(key: str) -> str:
    """'CGame::LoadLevel' -> 'CGame__LoadLevel'; '~CThing' destructors -> 'dtor'."""
    return key.replace("::~", "__dtor_").replace("::", "__").replace("~", "dtor_")


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
    c = sub.add_parser("facts")
    c.add_argument("--functions", type=Path, required=True)
    c.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
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
