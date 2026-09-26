#!/usr/bin/env python3
"""Byte-exact matching of a static library's object code in the pristine BEA.exe.

A static library (.lib) is an archive of COFF objects. Each function an object defines
becomes a pattern: its bytes, with every relocation field masked. A pattern that matches
at a game function's entry is a candidate.

Each relocation in a candidate implies an address for the symbol it names:
- DIR32: the stored value minus the object's addend;
- REL32: the displacement's target.

The implications from unique candidates are pooled, and every candidate is checked
against the pool. A reference into the candidate's own section must land inside the
matched bytes. Object data sections placed by the pool are verified the same way, and
their relocations add implications (a virtual table names its slots). Identical bodies
are told apart by what their relocations imply, then by the linker's layout, which
keeps each object's sections in order; bodies the linker folded into one carry every
alias that lands on them. Symbols that no pattern matched, such as the C runtime
functions D3DX calls, are placed by the references to them from matched code.

The tool reads only the specimen and the library, never Ghidra. Its output is private
evidence under local-data/: lib-matches.tsv (every decided entry), lib-placed.tsv
(symbols placed only by references), lib-pool.tsv (every implied address),
lib-proposals.tsv (names and evidence comments for a cohort) and a summary.

Usage:
  python tools/re_lib_match.py match --lib LIB --lib-sha256 PIN --out DIR --functions TSV
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import re
import struct
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

IMAGE_SCN_CNT_CODE = 0x20
IMAGE_SCN_LNK_COMDAT = 0x1000
IMAGE_SYM_CLASS_EXTERNAL = 2
IMAGE_SYM_CLASS_STATIC = 3
IMAGE_SYM_CLASS_LABEL = 6
IMAGE_SYM_CLASS_FUNCTION = 101
IMAGE_SYM_CLASS_WEAK_EXTERNAL = 105
IMAGE_SYM_DTYPE_FUNCTION = 0x20
REL_I386_DIR32, REL_I386_DIR32NB, REL_I386_SECTION, REL_I386_SECREL, REL_I386_REL32 = 0x06, 0x07, 0x0A, 0x0B, 0x14
_REL_WIDTH = {0x01: 2, 0x02: 2, 0x06: 4, 0x07: 4, 0x0A: 2, 0x0B: 4, 0x0D: 1, 0x14: 4}


# ---------------------------------------------------------------------------
# Archive and COFF parsing
# ---------------------------------------------------------------------------

def read_archive(data: bytes) -> list[tuple[str, bytes]]:
    """Members of an ar archive in the Microsoft layout (linker members and long names skipped)."""
    if data[:8] != b"!<arch>\n":
        raise ValueError("not an ar archive")
    out, longnames, off = [], b"", 8
    while off + 60 <= len(data):
        head = data[off:off + 60]
        if head[58:60] != b"`\n":
            raise ValueError(f"bad member header at {off}")
        name = head[:16].decode("latin-1").rstrip()
        size = int(head[48:58].decode("ascii").strip())
        body = data[off + 60:off + 60 + size]
        if name == "//":
            longnames = body
        elif name == "/" or name == "/SYM64/":
            pass
        elif name.startswith("/") and name[1:].isdigit():
            o = int(name[1:])
            end = min(i for i in (longnames.find(b"\0", o), longnames.find(b"/\n", o), len(longnames)) if i >= 0)
            out.append((longnames[o:end].decode("latin-1"), body))
        else:
            out.append((name.rstrip("/"), body))
        off += 60 + size + (size & 1)
    return out


@dataclass
class CoffSymbol:
    index: int
    name: str
    value: int
    section: int        # 1-based; 0 undefined, -1 absolute, -2 debug
    type: int
    storage: int
    aux: bytes


@dataclass
class CoffSection:
    index: int          # 1-based
    name: str
    chars: int
    data: bytes
    relocs: list[tuple[int, int, int]]      # (offset, symbol index, type)


@dataclass
class Coff:
    member: str
    sections: dict[int, CoffSection]
    symbols: dict[int, CoffSymbol]


def parse_coff(member: str, data: bytes) -> Coff | None:
    """An i386 COFF object; import objects, other machines and bigobj files return None."""
    if len(data) < 20:
        return None
    machine, nsec, _ts, psym, nsym, optsize, _ch = struct.unpack_from("<HHIIIHH", data, 0)
    if machine != 0x14C:
        return None
    strtab_off = psym + 18 * nsym
    strtab = data[strtab_off:]

    def sname(raw: bytes) -> str:
        if raw[:4] == b"\0\0\0\0":
            o = struct.unpack_from("<I", raw, 4)[0]
            return strtab[o:strtab.index(b"\0", o)].decode("latin-1")
        return raw.rstrip(b"\0").decode("latin-1")

    sections = {}
    base = 20 + optsize
    for i in range(nsec):
        raw = data[base + 40 * i:base + 40 * (i + 1)]
        name = raw[:8].rstrip(b"\0").decode("latin-1")
        if name.startswith("/") and name[1:].isdigit():
            o = int(name[1:])
            name = strtab[o:strtab.index(b"\0", o)].decode("latin-1")
        _vs, _va, rsize, rptr, prel, _pln, nrel, _nln, chars = struct.unpack_from("<IIIIIIHHI", raw, 8)
        body = data[rptr:rptr + rsize] if rptr else b"\0" * rsize
        relocs = [struct.unpack_from("<IIH", data, prel + 10 * k) for k in range(nrel)]
        sections[i + 1] = CoffSection(i + 1, name, chars, body, relocs)
    symbols = {}
    k = 0
    while k < nsym:
        raw = data[psym + 18 * k:psym + 18 * (k + 1)]
        value, secnum, typ, storage, naux = struct.unpack_from("<IhHBB", raw, 8)
        aux = data[psym + 18 * (k + 1):psym + 18 * (k + 1 + naux)]
        symbols[k] = CoffSymbol(k, sname(raw[:8]), value, secnum, typ, storage, aux)
        k += 1 + naux
    return Coff(member, sections, symbols)


@dataclass
class ObjFunc:
    member: str
    section: int
    start: int
    end: int
    symbol: str
    storage: int
    comdat: bool
    order: int = 0      # position of the section in the object (for layout checks)

    @property
    def key(self) -> tuple[str, int, int]:
        return (self.member, self.section, self.start)


def object_functions(coff: Coff) -> list[ObjFunc]:
    """Functions an object defines: symbols typed as functions in code sections (all named symbols
    at section offsets in hand-written code sections that carry no typed function)."""
    by_sec: dict[int, list[CoffSymbol]] = defaultdict(list)
    for s in coff.symbols.values():
        sec = coff.sections.get(s.section)
        if sec is None or not (sec.chars & IMAGE_SCN_CNT_CODE):
            continue
        if s.storage in (IMAGE_SYM_CLASS_EXTERNAL, IMAGE_SYM_CLASS_STATIC, IMAGE_SYM_CLASS_LABEL) and s.name != sec.name:
            by_sec[s.section].append(s)
    # MASM objects carry .bf records at each procedure's start and type their local labels as
    # functions too; there only the symbols at .bf values start functions.
    begins: dict[int, set[int]] = defaultdict(set)
    for s in coff.symbols.values():
        if s.storage == IMAGE_SYM_CLASS_FUNCTION and s.name == ".bf":
            begins[s.section].add(s.value)
    out = []
    for secnum, syms in by_sec.items():
        sec = coff.sections[secnum]
        typed = [s for s in syms if (s.type & 0x30) == IMAGE_SYM_DTYPE_FUNCTION]
        chosen = typed if typed else [s for s in syms if s.storage == IMAGE_SYM_CLASS_EXTERNAL]
        if begins.get(secnum):
            chosen = [s for s in chosen if s.value in begins[secnum]]
        first: dict[int, CoffSymbol] = {}
        for s in sorted(chosen, key=lambda s: (s.storage != IMAGE_SYM_CLASS_EXTERNAL, s.index)):
            first.setdefault(s.value, s)          # an external name wins over a local label
        chosen = sorted(first.values(), key=lambda s: s.value)
        for i, s in enumerate(chosen):
            end = chosen[i + 1].value if i + 1 < len(chosen) else len(sec.data)
            if end > s.value:
                out.append(ObjFunc(coff.member, secnum, s.value, end, s.name, s.storage,
                                   bool(sec.chars & IMAGE_SCN_LNK_COMDAT), secnum))
    return out


def masked_pattern(coff: Coff, fn: ObjFunc) -> tuple[bytes, bytes]:
    """(bytes, mask) for a function; mask byte 0 marks a relocated byte."""
    sec = coff.sections[fn.section]
    body = bytearray(sec.data[fn.start:fn.end])
    mask = bytearray(b"\xff" * len(body))
    for off, _sym, typ in sec.relocs:
        w = _REL_WIDTH.get(typ, 4)
        for b in range(off, off + w):
            if fn.start <= b < fn.end:
                mask[b - fn.start] = 0
                body[b - fn.start] = 0
    return bytes(body), bytes(mask)


def pattern_regex(body: bytes, mask: bytes) -> re.Pattern:
    parts = []
    for b, m in zip(body, mask):
        parts.append(b"." if m == 0 else re.escape(bytes([b])))
    return re.compile(b"".join(parts), re.DOTALL)


# ---------------------------------------------------------------------------
# Names
# ---------------------------------------------------------------------------

_CC = ("__cdecl", "__stdcall", "__thiscall", "__fastcall", "__clrcall", "__vectorcall", "__pascal")
_OP = re.compile(r"operator(?:\s*(?:new\[\]|delete\[\]|new|delete|->\*|->|<<=|>>=|<<|>>|<=|>=|==|!=|\+\+|--|\+=|-="
                 r"|\*=|/=|%=|&=|\|=|\^=|&&|\|\||\(\)|\[\]|[-+*/%^&|~!=<>,]))")
_OP_WORDS = {"new[]": "new_array", "delete[]": "delete_array", "new": "new", "delete": "delete", "->*": "arrow_star",
             "->": "arrow", "<<=": "shl_assign", ">>=": "shr_assign", "<<": "shl", ">>": "shr", "<=": "le", ">=": "ge",
             "==": "eq", "!=": "ne", "++": "inc", "--": "dec", "+=": "add_assign", "-=": "sub_assign",
             "*=": "mul_assign", "/=": "div_assign", "%=": "mod_assign", "&=": "and_assign", "|=": "or_assign",
             "^=": "xor_assign", "&&": "logical_and", "||": "logical_or", "()": "call", "[]": "index", "-": "sub",
             "+": "add", "*": "mul", "/": "div", "%": "mod", "^": "xor", "&": "and", "|": "or", "~": "bitnot",
             "!": "not", "=": "assign", "<": "lt", ">": "gt", ",": "comma"}


def demangle_all(symbols: list[str]) -> dict[str, str]:
    """Mangled MSVC symbols -> llvm-undname text (one batch call)."""
    mangled = sorted({s for s in symbols if s.startswith("?")})
    if not mangled:
        return {}
    out = subprocess.run(["llvm-undname"], input="\n".join(mangled) + "\n", capture_output=True, text=True).stdout
    result, lines, want = {}, out.split("\n"), set(mangled)
    for i, line in enumerate(lines[:-1]):
        if line in want and line not in result and not lines[i + 1].startswith("error:"):
            result[line] = lines[i + 1]
    return result


def _skip_special(text: str, i: int) -> int:
    """From a backtick, the index after the matching closing quote (the one followed by '(', '::' or the end)."""
    j = i + 1
    while j < len(text):
        if text[j] == "'" and (j + 1 == len(text) or text[j + 1] in "(:" or text.startswith("::", j + 1)):
            if j + 1 == len(text) or text[j + 1] != "'":
                return j + 1
        j += 1
    return len(text)


def qualified_name(demangled: str) -> str | None:
    """The qualified function name in llvm-undname output: from the calling convention (outside any
    template argument list) to the parameter list that opens at the same parenthesis depth."""
    text = demangled
    angle = paren = 0
    i, start, start_paren = 0, None, 0
    while i < len(text):
        if text.startswith("operator", i) and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] == "_")):
            m = _OP.match(text, i)
            i = m.end() if m else i + len("operator")
            continue
        c = text[i]
        if c == "`":
            i = _skip_special(text, i)
            continue
        if c == "<":
            angle += 1
        elif c == ">":
            angle -= 1
        elif c == "(":
            if start is not None and angle == 0 and paren == start_paren:
                return text[start:i].strip()
            paren += 1
        elif c == ")":
            paren -= 1
        elif angle == 0 and start is None:
            for cc in _CC:
                if text.startswith(cc + " ", i) and (i == 0 or text[i - 1] in " (*&"):
                    start, start_paren = i + len(cc) + 1, paren
                    i = start - 1
                    break
        i += 1
    return None


def split_scopes(q: str) -> list[str]:
    parts, depth, cur, i = [], 0, "", 0
    while i < len(q):
        if q[i] == "`":
            j = _skip_special(q, i)
            cur += q[i:j]
            i = j
            continue
        if q[i] == "<":
            depth += 1
        elif q[i] == ">":
            depth -= 1
        if depth == 0 and q.startswith("::", i):
            parts.append(cur)
            cur, i = "", i + 2
            continue
        cur += q[i]
        i += 1
    parts.append(cur)
    return parts


def _sanitize(text: str) -> str:
    text = re.sub(r"\b(?:class|struct|union|enum)\s+", "", text)
    text = text.replace("::", "\0").replace("*", "ptr").replace("&", "ref")
    text = re.sub(r"[^A-Za-z0-9_\0]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return re.sub(r"_*\0_*", "__", text)


def flat_name(symbol: str, demangled: dict[str, str]) -> str:
    """A Ghidra-legal flat name for a linker symbol: C symbols keep their decoration minus the stdcall
    suffix (the convention of the working project's Function ID names, such as _strlen); C++ symbols
    become their qualified name with '::' as '__', constructors as ctor and destructors as dtor."""
    if not symbol.startswith("?"):
        name = re.sub(r"@\d+$", "", symbol)
        name = name[1:] if name.startswith("@") else name
        return _legal(re.sub(r"[^A-Za-z0-9_]", "_", name))
    dem = demangled.get(symbol)
    q = qualified_name(dem) if dem else None
    if not q:
        q = _anonymous_template_name(symbol)
    if not q:
        return _legal(re.sub(r"[^A-Za-z0-9_]", "_", symbol).strip("_"))
    parts = split_scopes(q)
    out = []
    for n, p in enumerate(parts):
        last = n == len(parts) - 1
        cls = re.sub(r"<.*$", "", parts[n - 1]) if n else None
        if last and cls and p == cls:
            out.append("ctor")
        elif last and cls and p == "~" + cls:
            out.append("dtor")
        elif p.startswith("`"):
            inner = p[1:p.rfind("'")] if "'" in p else p[1:]
            inner = inner.replace("destructor", "dtor").replace("constructor", "ctor")
            out.append(_sanitize(inner))
        elif p.startswith("operator"):
            rest = p[len("operator"):].strip()
            out.append("operator_" + (_OP_WORDS.get(rest) or _sanitize(rest)))
        else:
            out.append(_sanitize(p))
    return _legal("__".join(x for x in out if x))


_MS_TYPES = {"C": "schar", "D": "char", "E": "uchar", "F": "short", "G": "ushort", "H": "int", "I": "uint",
             "J": "long", "K": "ulong", "M": "float", "N": "double", "_N": "bool"}


def _ms_number(text: str, i: int) -> tuple[str, int]:
    """An MSVC-encoded integer at text[i]: a digit n means n+1; A-P hex digits end with '@'; '?' negates."""
    neg = text[i] == "?"
    i += neg
    if text[i].isdigit():
        value, i = int(text[i]) + 1, i + 1
    else:
        j = text.index("@", i)
        value = int("".join("0123456789ABCDEF"[ord(c) - 65] for c in text[i:j]) or "0", 16)
        i = j + 1
    return ("m" if neg else "") + str(value), i


def _anonymous_template_name(symbol: str) -> str | None:
    """Function templates that MSVC 7 mangles with an empty template name (?Name@?$@args@scopes@@...),
    which llvm-undname rejects: Name_T_<args>, in the scopes that follow."""
    m = re.match(r"^\?([A-Za-z_]\w*)@\?\$@", symbol)
    if not m:
        return None
    i, args = m.end(), []
    while i < len(symbol) and symbol[i] != "@":
        if symbol.startswith("$0", i):
            value, i = _ms_number(symbol, i + 2)
            args.append(value)
        elif symbol.startswith("_N", i):
            args.append(_MS_TYPES["_N"]); i += 2
        elif symbol[i] in _MS_TYPES:
            args.append(_MS_TYPES[symbol[i]]); i += 1
        else:
            return None
    scopes = []
    i += 1
    while i < len(symbol) and symbol[i] != "@":
        j = symbol.index("@", i)
        scopes.append(symbol[i:j])
        i = j + 1
    return "::".join(list(reversed(scopes)) + [m.group(1) + "_T_" + "_".join(args)])


def _legal(name: str) -> str:
    if not name or not re.match(r"[A-Za-z_]", name[0]):
        name = "_" + name
    if len(name) > 191:
        name = name[:178] + "_" + hashlib.sha256(name.encode()).hexdigest()[:12]
    return name


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

@dataclass
class Library:
    path: Path
    sha256: str
    objects: dict[str, Coff]
    functions: list[ObjFunc]


def load_library(path: Path) -> Library:
    data = path.read_bytes()
    objects, functions = {}, []
    for member, body in read_archive(data):
        coff = parse_coff(member, body)
        if coff is None:
            continue
        if member in objects:
            member = f"{member}#{len(objects)}"
            coff.member = member
        objects[member] = coff
        functions.extend(object_functions(coff))
    return Library(path, hashlib.sha256(data).hexdigest(), objects, functions)


@dataclass
class Candidate:
    va: int
    fn: ObjFunc
    fixed: int                                      # unmasked bytes in the pattern
    implied: dict = field(default_factory=dict)     # symbol key -> address, from relocations
    own: dict = field(default_factory=dict)         # symbol key -> address, symbols inside the bytes
    conflicts: list = field(default_factory=list)   # self-inconsistent relocations


def symbol_key(coff: Coff, sym: CoffSymbol):
    """Global symbols are shared across objects; statics and section symbols belong to their object.
    A weak external with no definition of its own stands for its default symbol (MSVC emits a class's
    vector deleting destructor ??_E that way, as an alias of the scalar deleting destructor ??_G)."""
    if sym.storage == IMAGE_SYM_CLASS_WEAK_EXTERNAL and len(sym.aux) >= 4:
        default = coff.symbols.get(struct.unpack_from("<I", sym.aux, 0)[0])
        if default is not None and default is not sym:
            return symbol_key(coff, default)
    if sym.storage in (IMAGE_SYM_CLASS_EXTERNAL, IMAGE_SYM_CLASS_WEAK_EXTERNAL) and sym.name:
        return ("g", sym.name)
    sec = coff.sections.get(sym.section)
    if sec is not None and sym.name == sec.name:
        return ("s", coff.member, sym.section)
    return ("l", coff.member, sym.name, sym.section, sym.value)


def relocation_targets(coff: Coff, sec: CoffSection, lo: int, hi: int, base: int, read_u32, image_base: int):
    """(offset, symbol, implied target) for each relocation in [lo, hi) of a section placed at base."""
    for off, symidx, typ in sec.relocs:
        if not (lo <= off < hi):
            continue
        site = base + off
        game = read_u32(site)
        if game is None:
            continue
        addend = struct.unpack_from("<I", sec.data, off)[0]
        if typ == REL_I386_DIR32:
            target = (game - addend) & 0xFFFFFFFF
        elif typ == REL_I386_DIR32NB:
            target = (game + image_base - addend) & 0xFFFFFFFF
        elif typ == REL_I386_REL32:
            target = (game + site + 4 - addend) & 0xFFFFFFFF
        else:
            continue
        yield off, coff.symbols[symidx], target


def implications(coff: Coff, fn: ObjFunc, va: int, read_u32, image_base: int) -> tuple[dict, list]:
    """Addresses the matched bytes imply for the symbols the function's relocations name."""
    sec = coff.sections[fn.section]
    implied, conflicts = {}, []
    for _off, sym, target in relocation_targets(coff, sec, fn.start, fn.end, va - fn.start, read_u32, image_base):
        key = symbol_key(coff, sym)
        if sym.section == fn.section:
            # a reference into the function's own section must land where the object puts it
            own = (va - fn.start + sym.value) & 0xFFFFFFFF
            if own != target:
                conflicts.append((key, own, target))
        if key in implied and implied[key] != target:
            conflicts.append((key, implied[key], target))
        implied.setdefault(key, target)
    return implied, conflicts


def own_symbols(coff: Coff, fn: ObjFunc, va: int) -> dict:
    """The section symbol, the function's own symbol and every symbol inside the matched bytes."""
    out = {("s", coff.member, fn.section): va - fn.start}
    for s in coff.symbols.values():
        if s.storage in (IMAGE_SYM_CLASS_FUNCTION, 103):      # .bf/.lf/.ef and file records
            continue
        if s.section == fn.section and fn.start <= s.value < fn.end:
            out[symbol_key(coff, s)] = va + s.value - fn.start
    return out


class Resolver:
    """Decides each game entry's identity from byte matches, relocation implications, verified data
    sections and the linker's per-object section order."""

    def __init__(self, lib: Library, image, names: dict[str, str], lo: int, hi: int, starts: list[int]):
        self.lib, self.image, self.names, self.lo, self.hi = lib, image, names, lo, hi
        self.starts = sorted(starts)
        self.cands: dict[int, list[Candidate]] = {}
        self.decided: dict[int, dict] = {}
        self.votes: dict = defaultdict(Counter)
        self.pool: dict = {}
        self.contested: dict = {}
        self.data_done: set = set()
        self.data_checked: list = []
        self.nonstart_hits = 0
        self.decided_syms: dict[int, set[str]] = {}
        self.code_symbols = {f.symbol for f in lib.functions}

    def flat(self, c: Candidate) -> str:
        return flat_name(c.fn.symbol, self.names)

    def search(self) -> None:
        text = self.image.read(self.lo, self.hi - self.lo)
        start_set = set(self.starts)
        groups: dict[tuple[bytes, bytes], list[ObjFunc]] = defaultdict(list)
        for fn in self.lib.functions:
            body, mask = masked_pattern(self.lib.objects[fn.member], fn)
            if not any(mask):
                continue
            groups[(body, mask)].append(fn)
        for (body, mask), fns in groups.items():
            fixed = sum(1 for m in mask if m)
            if fixed < 4:
                # too little fixed code to search for; test it only at function entries
                for va in self.starts:
                    got = self.image.read(va, len(body))
                    if len(got) == len(body) and all(m == 0 or g == b for g, b, m in zip(got, body, mask)):
                        self._add(va, fns, fixed)
                continue
            rx = pattern_regex(body, mask)
            pos = 0
            while True:
                m = rx.search(text, pos)
                if not m:
                    break
                va = self.lo + m.start()
                if va in start_set:
                    self._add(va, fns, fixed)
                else:
                    self.nonstart_hits += 1
                pos = m.start() + 1

    def _add(self, va: int, fns: list[ObjFunc], fixed: int) -> None:
        row = self.cands.setdefault(va, [])
        for fn in fns:
            coff = self.lib.objects[fn.member]
            imp, conf = implications(coff, fn, va, self.image.u32, self.image.base)
            row.append(Candidate(va, fn, fixed, imp, own_symbols(coff, fn, va), conf))

    # -- pooling -------------------------------------------------------------

    def _vote(self, c: Candidate, local: bool) -> None:
        for k, v in list(c.implied.items()) + list(c.own.items()):
            if local or k[0] == "g":
                self.votes[k][v] += 1

    def _settle(self) -> None:
        self.pool.clear()
        self.contested.clear()
        for k, votes in self.votes.items():
            if len(votes) == 1:
                self.pool[k] = next(iter(votes))
            else:
                self.contested[k] = dict(votes)

    def _accept(self, va: int, how: str, cands: list[Candidate], **extra) -> None:
        self.decided[va] = {"how": how, "cands": cands, **extra}
        self.decided_syms[va] = {c.fn.symbol for c in cands} | set(extra.get("aliases", []))
        members = {c.fn.member for c in cands}
        for c in cands:
            self._vote(c, local=len(members) == 1)

    def _score(self, c: Candidate) -> tuple[int, int]:
        agree = sum(1 for k, v in c.implied.items() if self.pool.get(k) == v)
        clash = sum(1 for k, v in list(c.implied.items()) + list(c.own.items())
                    if k in self.pool and self.pool[k] != v)
        # a call into an entry already decided as a different function is a clash too
        clash += sum(1 for k, v in c.implied.items()
                     if k[0] == "g" and k[1] in self.code_symbols and v in self.decided_syms
                     and k[1] not in self.decided_syms[v])
        return agree, clash

    def _neighbours(self, va: int):
        single = sorted(v for v, d in self.decided.items() if len({c.fn.member for c in d["cands"]}) == 1)
        i = bisect.bisect_left(single, va)
        prev = self.decided[single[i - 1]]["cands"][0].fn if i > 0 else None
        j = bisect.bisect_right(single, va)
        nxt = self.decided[single[j]]["cands"][0].fn if j < len(single) else None
        return prev, nxt

    def _bracketed(self, c: Candidate, prev: ObjFunc | None, nxt: ObjFunc | None) -> bool:
        me = (c.fn.order, c.fn.start)
        return bool(prev and nxt and prev.member == nxt.member == c.fn.member
                    and (prev.order, prev.start) < me < (nxt.order, nxt.start))

    # -- data sections ---------------------------------------------------------

    def _section_base(self, coff: Coff, sec: CoffSection) -> int | None:
        k = ("s", coff.member, sec.index)
        if k in self.pool:
            return self.pool[k]
        for s in coff.symbols.values():
            if s.section == sec.index and s.name != sec.name:
                key = symbol_key(coff, s)
                if key in self.pool:
                    return (self.pool[key] - s.value) & 0xFFFFFFFF
        return None

    def data_pass(self) -> bool:
        """Verify object data sections at the addresses the pool gives them; their relocations then
        place what they point at (virtual tables name their slots)."""
        grew = False
        for member, coff in self.lib.objects.items():
            for sec in coff.sections.values():
                key = (member, sec.index)
                if key in self.data_done or sec.chars & IMAGE_SCN_CNT_CODE or not sec.relocs:
                    continue
                if sec.chars & 0x80:        # uninitialized data
                    continue
                base = self._section_base(coff, sec)
                if base is None:
                    continue
                self.data_done.add(key)
                got = self.image.read(base, len(sec.data))
                mask = bytearray(b"\xff" * len(sec.data))
                for off, _s, typ in sec.relocs:
                    for b in range(off, min(off + _REL_WIDTH.get(typ, 4), len(mask))):
                        mask[b] = 0
                same = len(got) == len(sec.data) and all(m == 0 or g == b for g, b, m in zip(got, sec.data, mask))
                self.data_checked.append((member, sec.index, sec.name, base, len(sec.data), same))
                if not same:
                    continue
                for _off, sym, target in relocation_targets(coff, sec, 0, len(sec.data), base, self.image.u32,
                                                            self.image.base):
                    self.votes[symbol_key(coff, sym)][target] += 1
                grew = True
        return grew

    # -- decisions -------------------------------------------------------------

    def run(self) -> None:
        self.search()
        # 1. entries whose clean candidates share one name and carry enough fixed code
        for va, row in self.cands.items():
            clean = [c for c in row if not c.conflicts]
            if clean and len({self.flat(c) for c in clean}) == 1 and max(c.fixed for c in clean) >= 16:
                self._accept(va, "unique", clean)
        self._settle()
        while True:
            changed = False
            at = defaultdict(list)
            for k, a in self.pool.items():
                if k[0] == "g" and k[1] in self.code_symbols:
                    at[a].append(k[1])
            for va, row in sorted(self.cands.items()):
                if va in self.decided:
                    continue
                clean = [c for c in row if not c.conflicts]
                scored = [(c, *self._score(c)) for c in clean]
                ok = [(c, a) for c, a, clash in scored if clash == 0]
                names = {self.flat(c) for c, _a in ok}
                prev, nxt = self._neighbours(va)
                placed = set(at.get(va, []))
                if len(names) == 1 and any(a > 0 for _c, a in ok):
                    self._accept(va, "relocations", [c for c, _a in ok])
                elif placed:
                    # the callers name this entry; several names mean identical bodies the linker folded
                    byte_ok = [c for c, _a in ok if c.fn.symbol in placed]
                    br = [c for c in byte_ok if self._bracketed(c, prev, nxt)]
                    kept = br[0].fn.symbol if len({c.fn.symbol for c in br}) == 1 else None
                    # a folded body is every alias at once; it is named after its shortest alias
                    best = min((sym for sym in placed if any(c.fn.symbol == sym for c in byte_ok)),
                               key=lambda sym: (len(flat_name(sym, self.names)), flat_name(sym, self.names)),
                               default=None)
                    pick = [c for c in byte_ok if c.fn.symbol == best]
                    if pick:
                        if len(placed) == 1:
                            self._accept(va, "called", pick)
                        else:
                            self._accept(va, "folded", pick, aliases=sorted(placed - {best}), kept=kept)
                    else:
                        self.decided[va] = {"how": "called-no-bytes", "cands": [], "symbols": sorted(placed)}
                else:
                    br = [c for c, _a in ok if self._bracketed(c, prev, nxt)]
                    if len({self.flat(c) for c in br}) == 1:
                        self._accept(va, "layout", br)
                    elif len(names) == 1 and ok and max(c.fixed for c, _a in ok) >= 8 and \
                            any(prev and prev.member == c.fn.member for c, _a in ok):
                        self._accept(va, "unique-short", [c for c, _a in ok])
                    else:
                        continue
                changed = True
            self._settle()
            if self.data_pass():
                self._settle()
                changed = True
            if not changed:
                break
        for va, row in self.cands.items():
            if va not in self.decided:
                self.decided[va] = {"how": "ambiguous", "cands": [c for c in row if not c.conflicts] or row}

    def _sym(self, c: Candidate) -> CoffSymbol:
        coff = self.lib.objects[c.fn.member]
        return next(s for s in coff.symbols.values()
                    if s.section == c.fn.section and s.value == c.fn.start and s.name == c.fn.symbol)

    def placed_symbols(self, entries: list[int] | None = None) -> dict:
        """Global symbols the pool places at a function entry (any entry in the program when given)
        that no pattern decided there."""
        out = {}
        start_set = set(entries if entries is not None else self.starts)
        for k, addr in self.pool.items():
            if k[0] != "g" or addr not in start_set:
                continue
            d = self.decided.get(addr)
            if d and d["how"] != "ambiguous":
                continue
            out[k[1]] = addr
        return out


def layout_violations(decided: dict[int, dict]) -> list[tuple[int, int, str]]:
    """Consecutive decided entries from one object whose section order runs backwards."""
    seq = sorted((va, d["cands"][0].fn) for va, d in decided.items()
                 if d["how"] not in ("ambiguous", "folded") and len({c.fn.member for c in d["cands"]}) == 1)
    out = []
    for (va0, f0), (va1, f1) in zip(seq, seq[1:]):
        if f0.member == f1.member and (f1.order, f1.start) < (f0.order, f0.start):
            out.append((va0, va1, f0.member))
    return out


# ---------------------------------------------------------------------------
# Proposals
# ---------------------------------------------------------------------------

AUDIT_DATE = "2026-09-26"
_HOW = {
    "unique": "No other function in the library has these bytes.",
    "relocations": "Other library functions share these bytes; only this one's relocation targets agree with the rest "
                   "of the match.",
    "layout": "Other library functions share these bytes; the linker keeps each object's sections in order, and only "
              "this one's section lies between those of its matched neighbours.",
    "unique-short": "No other library function with this much fixed code matches here, and its neighbours come from "
                    "the same object.",
}


def _equivalent(current: str, proposed: str) -> bool:
    norm = lambda t: re.sub(r"[`'_]", "", t.lower()).replace("constructor", "ctor").replace("destructor", "dtor")
    return norm(current) == norm(proposed)


def proposals(res: "Resolver", rows: dict[int, dict], names: dict[str, str], lib_label: str) -> list[dict]:
    """One proposal per program function the match names: the decided library entries, the function fragments
    Ghidra split off them, and the entries (library or game code) that the library code's own references place.
    Each proposal carries its evidence comment; names already equal to the proven one are left alone."""
    out = []
    pin = f"{lib_label} (SHA-256 {res.lib.sha256})"
    by_addr = defaultdict(list)
    for k, a in res.pool.items():
        if k[0] == "g" and a in rows and not k[1].startswith(("__imp_", "$", "??_C@")):
            by_addr[a].append(k[1])

    def votes(sym: str) -> int:
        return sum(res.votes[("g", sym)].values())

    def former(cur: dict) -> str:
        if cur.get("nameSource") == "DEFAULT":
            return ""
        return f" Former label: {cur['name']}."

    spans = []
    for va in sorted(res.decided):
        d = res.decided[va]
        if d["how"] in ("ambiguous", "called-no-bytes") or not d["cands"]:
            continue
        c = d["cands"][0]
        coff = res.lib.objects[c.fn.member]
        sec = coff.sections[c.fn.section]
        length = c.fn.end - c.fn.start
        nrel = sum(1 for off, _s, _t in sec.relocs if c.fn.start <= off < c.fn.end)
        agree = res._score(c)[0]
        sym = c.fn.symbol
        dem = names.get(sym, sym)
        new = flat_name(sym, names)
        spans.append((va, va + length, new))
        cur = rows.get(va)
        if cur is None:
            continue
        rel = (f" apart from its {nrel} relocation field{'s' if nrel != 1 else ''}, and every relocation resolves "
               f"consistently with the rest of the match ({agree} of them to addresses that other matches "
               f"confirm)") if nrel else " (it has no relocations)"
        if d["how"] == "folded":
            aliases = [flat_name(x, names) for x in d.get("aliases", [])]
            kept = f" The object section placed here is {flat_name(d['kept'], names)}'s." if d.get("kept") else ""
            how = (f"The linker folded identical bodies into this one: the library's references to "
                   f"{', '.join(aliases)} land here too, so it serves all of them.{kept}")
        elif d["how"] == "called":
            n = votes(sym)
            how = (f"Other library functions share these bytes; the library code's {n} reference{'s' if n != 1 else ''} "
                   f"to {sym} land{'' if n != 1 else 's'} here.")
        else:
            how = _HOW[d["how"]]
        text = (f"Linked library code: {dem}, from member {c.fn.member} of the static library {pin}. Proof: bytes "
                f"[{va:08x},{va + length:08x}) of the pristine executable equal the object code of {sym} byte for "
                f"byte{rel}. {how} Matched by tools/re_lib_match.py in the RE record audit ({AUDIT_DATE}).{former(cur)}")
        tags = ["library-code", "d3dx9-lib", "re-audit-20260926", "name-corrected-20260926"] + \
            (["linker-folded"] if d["how"] == "folded" else [])
        out.append({"address": va, "current": cur["name"], "source": cur["nameSource"], "proposed": new,
                    "how": d["how"], "comment": text, "tags": tags, "keepTags": False})
    # fragments: entries Ghidra split off inside a matched body
    for lo_, hi_, owner in spans:
        for va, cur in rows.items():
            if lo_ < va < hi_ and cur["nameSource"] != "ANALYSIS":
                text = (f"Part of {owner} ({lo_:08x}): that function's object code spans [{lo_:08x},{hi_:08x}) of the "
                        f"pristine executable (tools/re_lib_match.py, RE record audit {AUDIT_DATE}), so the saved "
                        f"function boundary here splits it; this entry is not a function of its own.{former(cur)}")
                out.append({"address": va, "current": cur["name"], "source": cur["nameSource"],
                            "proposed": f"{owner}_fragment_{va:08x}", "how": "fragment", "comment": text,
                            "tags": ["library-code", "d3dx9-lib", "re-audit-20260926", "name-corrected-20260926",
                                     "function-fragment"], "keepTags": False})
    # entries placed only by the library's own references
    decided = {r["address"] for r in out}
    for va in sorted(set(by_addr) - decided):
        cur = rows.get(va)
        d = res.decided.get(va)
        if cur is None or (d and d["how"] not in ("ambiguous", "called-no-bytes")):
            continue
        library = res.lo <= va < res.hi
        if not library and any(x in res.code_symbols for x in by_addr[va]):
            continue    # a library function folded with a program function: the program's name is its own question
        syms = sorted(by_addr[va], key=lambda x: (len(flat_name(x, names)), flat_name(x, names)))
        sym = syms[0]
        also = f" (also reached as {', '.join(syms[1:])})" if len(syms) > 1 else ""
        n = sum(votes(x) for x in syms)
        what = "Linked library function" if library else "The program's own definition of"
        where = "and every one of them lands here" if n != 1 else "and it lands here"
        text = (f"{what} {names.get(sym, sym)}{also}. Proof: the object code of the static library {pin} calls "
                f"or references {sym} at {n} site{'s' if n != 1 else ''} inside functions matched byte for byte "
                f"elsewhere in this executable, {where} (tools/re_lib_match.py, RE record audit "
                f"{AUDIT_DATE}).{former(cur)}")
        tags = (["library-code", "msvc-crt"] if library else sorted(t for t in cur.get("tags", "").split(",") if t)) + \
            ["re-audit-20260926", "name-corrected-20260926"]
        out.append({"address": va, "current": cur["name"], "source": cur["nameSource"],
                    "proposed": flat_name(sym, names), "how": "placed", "comment": text, "tags": tags,
                    "keepTags": not library})
    # leave names that already are the proven identity, and Ghidra's own funclet names
    out = [r for r in out if not _equivalent(r["current"], r["proposed"])
           and not re.match(r"^(Catch|Unwind|Catch_All)@", r["current"])]
    # uniqueness: a proposed name used twice, or held by a function this cohort does not rename, takes the address
    renamed = {r["address"] for r in out}
    held = {cur["name"]: va for va, cur in rows.items()}
    counts = Counter(r["proposed"] for r in out)
    for r in out:
        n = r["proposed"]
        if counts[n] > 1 or (n in held and held[n] != r["address"]):
            r["proposed"] = f"{n}_{r['address']:08x}"
    assert len({r["proposed"] for r in out}) == len(out)
    return sorted(out, key=lambda r: r["address"])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_starts(path: Path | None, lo: int, hi: int) -> tuple[list[int] | None, dict[int, dict]]:
    if path is None:
        return None, {}
    rows = {}
    with path.open() as f:
        for r in csv.DictReader(f, delimiter="\t"):
            va = int(r["address"], 16)
            if lo <= va < hi:
                rows[va] = r
    return sorted(rows), rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("match")
    m.add_argument("--lib", type=Path, required=True)
    m.add_argument("--lib-sha256", required=True, help="expected SHA-256 of the library (the pin)")
    m.add_argument("--out", type=Path, required=True)
    m.add_argument("--functions", type=Path, help="working-project function export (functions.tsv)")
    m.add_argument("--lo", type=lambda s: int(s, 16), default=0x0055D6A0)
    m.add_argument("--hi", type=lambda s: int(s, 16), default=0x005D0F10)
    args = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from re_name_evidence import Image
    image = Image()
    lib = load_library(args.lib)
    if lib.sha256 != args.lib_sha256:
        raise SystemExit(f"library hash {lib.sha256} is not the pinned {args.lib_sha256}")
    starts, rows = _load_starts(args.functions, args.lo, args.hi)
    _all_starts, all_rows = _load_starts(args.functions, 0, 1 << 32)
    names = demangle_all([f.symbol for f in lib.functions] +
                         [s.name for c in lib.objects.values() for s in c.symbols.values()])
    res = Resolver(lib, image, names, args.lo, args.hi, starts)
    res.run()
    args.out.mkdir(parents=True, exist_ok=True)
    placed = res.placed_symbols()
    by_addr = defaultdict(list)
    for k, a in res.pool.items():
        if k[0] == "g":
            by_addr[a].append(k[1])
    with (args.out / "lib-matches.tsv").open("w") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["address", "currentName", "how", "name", "symbol", "member", "section", "offset", "length",
                    "fixed", "relocations", "agree", "aliases", "alternatives", "keptSection"])
        for va in sorted(res.decided):
            d = res.decided[va]
            if not d["cands"]:
                w.writerow([f"0x{va:08x}", rows.get(va, {}).get("name", ""), d["how"], "", "", "", "", "", "", "",
                            "", "", "", ";".join(flat_name(x, names) for x in d.get("symbols", []))])
                continue
            c = d["cands"][0]
            alts = sorted({flat_name(x.fn.symbol, names) for x in d["cands"]})
            nrel = sum(1 for off, _s, _t in lib.objects[c.fn.member].sections[c.fn.section].relocs
                       if c.fn.start <= off < c.fn.end)
            agree = res._score(c)[0]
            aliases = sorted({flat_name(s, names) for s in list(by_addr.get(va, [])) + d.get("aliases", [])
                              if s not in {x.fn.symbol for x in d["cands"]} and not s.startswith("$")
                              and s in res.code_symbols})
            w.writerow([f"0x{va:08x}", rows.get(va, {}).get("name", ""), d["how"],
                        alts[0] if len(alts) == 1 and d["how"] != "ambiguous" else "", c.fn.symbol, c.fn.member,
                        c.fn.section, c.fn.start, c.fn.end - c.fn.start, c.fixed, nrel, agree, ";".join(aliases),
                        ";".join(alts) if len(alts) > 1 else "",
                        flat_name(d["kept"], names) if d.get("kept") else ""])
    with (args.out / "lib-placed.tsv").open("w") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["address", "currentName", "symbol", "name", "votes"])
        for sym, a in sorted(placed.items(), key=lambda x: x[1]):
            w.writerow([f"0x{a:08x}", rows.get(a, {}).get("name", ""), sym, flat_name(sym, names),
                        sum(res.votes[("g", sym)].values())])
    with (args.out / "lib-pool.tsv").open("w") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["key", "address", "votes"])
        for k in sorted(res.pool, key=lambda k: (res.pool[k], str(k))):
            w.writerow(["|".join(map(str, k)), f"0x{res.pool[k]:08x}", sum(res.votes[k].values())])
        for k, v in sorted(res.contested.items(), key=str):
            w.writerow(["|".join(map(str, k)), "CONTESTED " + ";".join(f"0x{a:08x}x{n}" for a, n in v.items()), ""])
    imports_ok = imports_bad = 0
    for k, a in res.pool.items():
        if k[0] == "g" and k[1].startswith("__imp_"):
            want = re.sub(r"@\d+$", "", k[1][len("__imp_"):]).lstrip("_")
            got = image.imports.get(a, "")
            if got.split("!")[-1] == want:
                imports_ok += 1
            else:
                imports_bad += 1
    props = proposals(res, all_rows, names, "DirectX 9.0 SDK d3dx9.lib")
    with (args.out / "lib-proposals.tsv").open("w") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["address", "source", "current", "proposed", "how", "tags", "keepTags", "comment"])
        for r in props:
            w.writerow([f"0x{r['address']:08x}", r["source"], r["current"], r["proposed"], r["how"],
                        ";".join(r["tags"]), str(r["keepTags"]).lower(), r["comment"]])
    viol = layout_violations(res.decided)
    summary = {"library": str(args.lib), "librarySha256": lib.sha256, "objects": len(lib.objects),
               "functions": len(lib.functions), "entriesMatched": len(res.decided),
               "how": Counter(d["how"] for d in res.decided.values()), "placedByCallers": len(placed),
               "proposals": Counter(r["how"] for r in props),
               "poolKeys": len(res.pool), "contestedKeys": len(res.contested),
               "dataSectionsChecked": len(res.data_checked),
               "dataSectionsMismatched": sum(1 for x in res.data_checked if not x[5]),
               "importSlotsAgree": imports_ok, "importSlotsDisagree": imports_bad,
               "nonEntryHits": res.nonstart_hits,
               "layoutViolations": [f"0x{a:08x}->0x{b:08x} {m}" for a, b, m in viol]}
    (args.out / "lib-match-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "layoutViolations"}, indent=2),
          "layout violations:", len(viol))
    return 0


if __name__ == "__main__":
    sys.exit(main())
