"""Test a proposed mapping of program functions onto a pinned source tree by call graph and return size.

A name taken from source is only as good as the structure that supports it. For each mapped function this checks:

- every call it makes into another mapped function is a call in the source, directly or through functions the
  compiler may have inlined: bodies in headers, definitions marked inline, names given with --inline, and any
  function defined in the caller's own file (VC6 /Ob2 inlines within a translation unit);
- which source calls between two mapped functions the program lacks (the compiler inlined them, or the source is a
  different version: a lead, not a failure);
- its return against the source's parameters for known scalar/pointer results: a non-static member (__thiscall)
  or __stdcall function pops its parameters with `ret N`. Unknown/aggregate result ABIs are withheld: a type name
  alone does not prove hidden-result storage. Static members/free __cdecl functions use caller cleanup.

Calls into bodies of at most --small bytes are reported apart, never as contradictions: the linker folds identical
small bodies, so such a target's saved name may be any one of its folded identities. So are implicit calls, which
source code makes without writing them: a constructor or destructor of a class the caller's source mentions (members,
bases, `new C`, locals), and the names given with --implicit (allocator entry points behind `new` and `delete`,
helpers behind operator overloads).

A contradiction means the mapping is wrong, or the source differs from the program there; either way it is
recorded, never smoothed over.

Usage:
  python tools/re_source_graph.py map-names --functions FUNCTIONS.tsv --source DIR --out MAP.tsv
      --report CANDIDATES.json
  python tools/re_source_graph.py check --mapping MAP.tsv --source DIR [--functions functions.tsv]
      [--pattern '*.cpp' --pattern '*.h'] [--inline NAME ...] [--out report.json]

MAP.tsv has the columns `address` and `source`: `Class::Method` or `Function`. An overload is `Class::Method/N`,
N being its parameter count.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import re_name_evidence as E  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = ROOT / "local-data/test-runs/re-audit-20260926/evidence/model.pickle"
_KEYWORDS = {"if", "for", "while", "switch", "return", "sizeof", "catch", "new", "delete"}


@dataclass
class Source:
    funcs: dict[str, list[E.SourceFunc]]              # short name -> definitions
    statics: set[tuple[str, str]]                     # (class, method) declared static
    inline: set[str]                                  # short names the compiler may have inlined
    calls: dict[str, set[str]] = field(default_factory=dict)   # key (with /N for overloads) -> short names called
    enum_types: set[str] = field(default_factory=set)


def short(key: str) -> str:
    return key.split("/")[0].split("::")[-1]


def params(args: str) -> list[str]:
    """Parameters as written, without default values; '' and 'void' mean none."""
    args = re.sub(r"=\s*[^,]+", "", args).strip()
    if args in ("", "void"):
        return []
    depth, cur, out = 0, "", []
    for ch in args:
        depth += (ch in "<(") - (ch in ">)")
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return out + [cur.strip()]


def param_bytes(p: str) -> int | None:
    """Stack bytes one parameter takes; None when a by-value aggregate makes it unknown."""
    t = re.sub(r"\b(const|volatile|register|struct|class|enum|unsigned|signed)\b", " ", p)
    if "*" in t or "&" in t:
        return 4
    # Header identity normalization removes whitespace between type words.
    # Do not let an unsigned prefix turn an eight-byte integer into four.
    if p.strip() in ('longlong', 'signedlonglong', 'unsignedlonglong',
                     'signed__int64', 'unsigned__int64', 'longdouble'):
        return 8
    if p.strip() in {sign+kind for sign in ('signed', 'unsigned')
                    for kind in ('char', 'short', 'shortint', 'int', 'long', 'longint')}:
        return 4
    words = t.split()
    base = words[0] if words else ""
    if base in ("double", "__int64") or "long long" in p:
        return 8
    if base in ("int", "short", "char", "bool", "float", "long", "WORD", "DWORD", "BYTE", "BOOL", "UINT", "size_t",
                "unsigned", "SINT", "UBYTE", "UWORD", "ULONG", "LONG", "WPARAM", "LPARAM", "HRESULT", "LRESULT",
                "INT_PTR", "UINT_PTR", "DWORD_PTR", "LONG_PTR", "WCHAR", "TCHAR") \
            or re.match(r"^(unsigned|signed)\b", p.strip()) or re.match(r"^(LP|H)[A-Z0-9]+$", base):
        return 4                                    # LPxxx pointers and Hxxx handles are 4 bytes
    return None


def index(root: Path, patterns: tuple[str, ...], extra_inline: set[str]) -> Source:
    defs = E.index_source(root, patterns)
    statics, inline, enum_types = set(), set(extra_inline), set()
    for path in sorted({p for pattern in patterns for p in root.glob(pattern)}):
        text = E.strip_comments(path.read_text(errors="replace"))
        enum_types.update(re.findall(r'\benum\s+(?:class\s+|struct\s+)?(\w+)\s*(?::[^;{}]+)?\{', text))
        for cm in re.finditer(r"\b(?:class|struct)\s+(\w+)(?:\s+final)?\s*(?::[^;{}()]*)?\{", text):
            depth, j = 1, cm.end()
            while j < len(text) and depth:
                depth += (text[j] == "{") - (text[j] == "}")
                j += 1
            body = text[cm.end():j - 1]
            for m in re.finditer(r"\bstatic\s+[^;(){}]*?\b(~?\w+)\s*\(", body):
                statics.add((cm.group(1), m.group(1)))
            # methods defined inside the class body are implicitly inline
            for m in re.finditer(r"(?:^|[;{}])\s*(?P<head>[\w:<>*&\s]*?)\b(?P<name>~?[A-Za-z_]\w*)\s*\((?P<args>[^;{}()]*)\)"
                                 r"\s*(?:const\s*)?(?::[^;{]*)?\{", body):
                if m.group("name") in _KEYWORDS:
                    continue
                depth, k = 1, m.end()
                while k < len(body) and depth:
                    depth += (body[k] == "{") - (body[k] == "}")
                    k += 1
                key = f"{cm.group(1)}::{m.group('name')}"
                method_body = body[m.end():k - 1]
                # Each definition position is distinct. Equal arguments/body
                # do not collapse const/nonconst overloads (or conditional
                # duplicate definitions) into a uniquely resolved identity.
                defs.append(E.SourceFunc(key, path.name, text.count("\n", 0, cm.end() + m.start()) + 1,
                                         method_body, [], [], 0, m.group("args"), "inline " + m.group("head")))
    funcs: dict[str, list[E.SourceFunc]] = defaultdict(list)
    for f in defs:
        funcs[short(f.key)].append(f)
        if f.file.endswith((".h", ".hpp", ".inl")) or re.search(r"\binline\b", f.head):
            inline.add(short(f.key))
    src = Source(funcs, statics, inline)
    src.enum_types = enum_types
    names = set(funcs)
    for name, fs in funcs.items():
        for f in fs:
            called = {c for c in re.findall(r"(?<!\w)(~?[A-Za-z_]\w*)\s*\(", f.body) if c not in _KEYWORDS}   # obj.f( and p->f( too
            # Equal-arity overloads cannot be resolved by this partial parser.
            # Preserve the union as possible calls; never silently select the
            # last definition. resolve() still withholds the ambiguous identity.
            key = f.key if len(fs) == 1 else f"{f.key}/{len(params(f.args))}"
            src.calls.setdefault(key, set()).update(called & names)
    return src


def resolve(src: Source, key: str) -> E.SourceFunc | None:
    """The definition a mapping key names ('Class::Method', 'Function' or 'Class::Method/N')."""
    base, _, n = key.partition("/")
    cands = [f for f in src.funcs.get(short(base), []) if f.key == base or not base.count("::")]
    if n:
        cands = [f for f in cands if len(params(f.args)) == int(n)]
    return cands[0] if len(cands) == 1 else None


def _keys(src: Source, name: str) -> list[str]:
    """The call-table keys of every definition with this short name."""
    fs = src.funcs.get(name, [])
    return [f.key if len(fs) == 1 else f"{f.key}/{len(params(f.args))}" for f in fs]


def _calls_of(src: Source, key: str) -> set[str]:
    if key in src.calls:
        return src.calls[key]
    return set().union(*[v for k, v in src.calls.items() if k.split("/")[0] == key])


def reach(src: Source, key: str, file: str | None = None) -> set[str]:
    """Short names a function calls, directly or through functions the compiler may have inlined: inline ones and,
    given the caller's file, every function defined in that file."""
    local = {n for n, fs in src.funcs.items() if file and any(f.file == file for f in fs)}
    seen: set[str] = set()
    todo = [key]
    while todo:
        for c in _calls_of(src, todo.pop()):
            if c not in seen:
                seen.add(c)
                if c in src.inline or c in local:
                    todo.extend(_keys(src, c))
    return seen


_STDCALL = re.compile(r"\b(__stdcall|CALLBACK|WINAPI|PASCAL|APIENTRY|STDMETHODCALLTYPE)\b")
_SCALAR_RET = re.compile(r"^(void|bool|BOOL|char|short|int|long|float|double|unsigned|signed|DWORD|WORD|BYTE|UINT|"
                         r"HRESULT|LRESULT|INT_PTR|LONG|ULONG|SINT|UBYTE|UWORD|WCHAR|size_t|__int64|HWND|HANDLE)\b")


def expected_pop(src: Source, f: E.SourceFunc) -> int | None:
    """Expected pop for known scalar/pointer results; aggregate/unknown ABI stays unresolved."""
    parts = f.key.split("::")
    member = len(parts) >= 2 and (parts[-2], parts[-1]) not in src.statics and not re.search(r"\bstatic\b", f.head)
    if not member and not _STDCALL.search(f.head):
        return 0
    sizes = [param_bytes(p) for p in params(f.args)]
    if None in sizes:
        return None
    ret = re.sub(r"\b(virtual|static|inline|const|__cdecl|__stdcall|__thiscall|__fastcall|__forceinline|CALLBACK|WINAPI|PASCAL|APIENTRY|STDMETHODCALLTYPE)\b", " ",
                 f.head).strip()
    constructor = parts[-1] == (parts[-2] if len(parts) >= 2 else None) or parts[-1].startswith('~')
    if not constructor and not ('*' in ret or '&' in ret or _SCALAR_RET.match(ret) or ret in src.enum_types):
        return None
    return sum(sizes)


def _implicit(src: Source, caller: E.SourceFunc, target: str, implicit: set[str]) -> bool:
    """Whether source code can reach this target without writing the call."""
    if short(target) in implicit:
        return True
    parts = target.split("/")[0].split("::")
    if len(parts) >= 2 and parts[-1] in (parts[-2], "~" + parts[-2]):     # a constructor or destructor
        cls = parts[-2]
        own = caller.key.split("::")[0] if "::" in caller.key else ""
        return bool(re.search(r"\b" + re.escape(cls) + r"\b", caller.body)) or cls == own
    return False


def check(mapping: dict[int, str], calls: dict[int, list[int]], rets: dict[int, set[int]], src: Source,
          sizes: dict[int, int] | None = None, small: int = 0, implicit: set[str] | None = None) -> dict:
    """mapping: address -> source key; calls: address -> call targets; rets: address -> bytes each ret pops;
    sizes: address -> body bytes (calls into bodies of at most `small` bytes are reported as folded candidates)."""
    sizes = sizes or {}
    implicit = implicit or set()
    by_short = defaultdict(set)
    for a, k in mapping.items():
        by_short[short(k)].add(a)
    rows, edges = [], 0
    for a, key in sorted(mapping.items()):
        f = resolve(src, key)
        row = {"address": f"0x{a:08x}", "source": key, "defined": bool(f), "contradictions": [], "absent": [],
               "smallTargets": [], "implicitTargets": [], "ret": sorted(rets.get(a, set()))}
        if f is None:
            row["contradictions"].append("not defined (once) in the source")
            rows.append(row)
            continue
        row["file"], row["line"] = f.file, f.line
        r = reach(src, key, f.file)
        made = set()
        for t in calls.get(a, []):
            if t in mapping and t != a:
                made.add(short(mapping[t]))
                if sizes.get(t, small + 1) <= small:
                    row["smallTargets"].append(f"0x{t:08x} {mapping[t]}")
                    continue
                if short(mapping[t]) not in r and _implicit(src, f, mapping[t], implicit):
                    row["implicitTargets"].append(f"0x{t:08x} {mapping[t]}")
                    continue
                edges += 1
                if short(mapping[t]) not in r:
                    row["contradictions"].append(f"calls 0x{t:08x} {mapping[t]}, which the source does not call")
        for g in sorted(r - src.inline):
            if g in by_short and g not in made and g != short(key):
                row["absent"].append(g)
        want = expected_pop(src, f)
        row["expectedPop"] = want
        if want is not None and rets.get(a) and rets[a] != {want}:
            row["contradictions"].append(f"returns popping {sorted(rets[a])} bytes; the source's parameters need {want}")
        rows.append(row)
    return {"mapped": len(mapping), "edgesChecked": edges,
            "contradicted": sum(1 for r in rows if r["contradictions"]), "rows": rows}


def program_facts(functions: Path, model: Path, addresses: set[int]):
    img, mdl = E.load_or_build(model)
    prog = E.Program(img, mdl, E.load_functions(functions))
    calls, rets, sizes = {}, {}, {}
    for a in addresses:
        f = prog.func_at(a)
        body = prog.body(f) if f else []
        calls[a] = [t for i in body for kind, t in E.insn_refs(i, img) if kind == "call"]
        rets[a] = {int(i.ops, 16) if i.ops else 0 for i in body if i.mnem == "ret"}
        sizes[a] = sum(i.size for i in body)
    return calls, rets, sizes


def source_digest(root: Path, patterns: tuple[str, ...]) -> str:
    """Pin the exact source inputs, including names; neither mtimes nor saved labels are authority."""
    files = sorted({p for pattern in patterns for p in root.glob(pattern)})
    records = [(p.relative_to(root).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
    return hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()


def input_pins(functions: Path, source: Path, patterns: tuple[str, ...]) -> dict:
    return {'functionsSha256': hashlib.sha256(functions.read_bytes()).hexdigest(),
            'sourceSha256': source_digest(source, patterns), 'sourcePatterns': list(patterns),
            'toolSha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__), Path(E.__file__)]}}


def map_names(functions: list[dict], src: Source) -> tuple[dict[int, str], list[dict]]:
    """Exact-spelling candidate map; ambiguity is retained, never resolved from an inherited ABI.

    A spelling match is a hypothesis for graph checks, not identity evidence.
    Overloads, duplicate definitions and multiple saved entries with the same
    source spelling are withheld even if their saved parameter counts differ.
    """
    defs = defaultdict(list)
    for group in src.funcs.values():
        for f in group:
            defs[E.source_key_to_name(f.key)].append(f)
    counts = defaultdict(int)
    seen = set()
    for r in functions:
        address = int(r['address'], 16)
        if address in seen:
            raise ValueError(f'duplicate function address {address:#x}')
        seen.add(address)
        counts[r['name']] += 1
    mapping, rows = {}, []
    for r in sorted(functions, key=lambda row: int(row['address'], 16)):
        address, name = int(r['address'], 16), r['name']
        candidates = defs.get(name, [])
        status = ('no-exact-source-definition' if not candidates else
                  'ambiguous-source-definition' if len(candidates) != 1 else
                  'ambiguous-saved-name' if counts[name] != 1 else 'candidate')
        if status == 'candidate':
            mapping[address] = candidates[0].key
        rows.append({'address': f'0x{address:08x}', 'name': name, 'status': status,
                     'candidates': [{'source': f.key, 'file': f.file, 'line': f.line,
                                     'parameters': f.args} for f in candidates]})
    return mapping, rows


def read_mapping(path: Path) -> dict[int, str]:
    result = {}
    with path.open() as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            address = int(row['address'], 16)
            if address in result or not row['source'].strip():
                raise ValueError(f'duplicate address or empty source in mapping: {address:#x}')
            result[address] = row['source']
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser('map-names', help='exact-spelling candidates, not verified identities')
    m.add_argument('--functions', type=Path, required=True)
    m.add_argument('--source', type=Path, required=True)
    m.add_argument('--pattern', action='append')
    m.add_argument('--out', type=Path, required=True, help='new mapping TSV; never overwrite evidence')
    m.add_argument('--report', type=Path, required=True, help='new candidate/ambiguity JSON')
    c = sub.add_parser("check")
    c.add_argument("--mapping", type=Path, required=True)
    c.add_argument("--source", type=Path, required=True)
    c.add_argument("--functions", type=Path, required=True, help="working-project function export (functions.tsv)")
    c.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="re_name_evidence model cache")
    c.add_argument("--pattern", action="append", help="source globs (default *.cpp and *.h)")
    c.add_argument("--inline", action="append", default=[], help="a function the compiler inlined")
    c.add_argument("--small", type=int, default=16, help="bodies of at most this many bytes may be folded")
    c.add_argument("--implicit", action="append", default=[], help="a name source code reaches without writing a call")
    c.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    patterns = tuple(args.pattern or ('*.cpp', '*.h'))
    src = index(args.source, patterns, set(getattr(args, 'inline', [])))
    inputs = input_pins(args.functions, args.source, patterns)
    if args.cmd == 'map-names':
        if args.out.resolve() == args.report.resolve() or args.out.exists() or args.report.exists():
            ap.error('mapping/report must be distinct new paths')
        with args.functions.open() as stream:
            mapping, rows = map_names(list(csv.DictReader(stream, delimiter='\t')), src)
        report = {'inputs': inputs, 'mappedCandidates': len(mapping), 'rows': rows,
                  'limits': 'Spelling-only candidate map; no retail identity or semantic verification. '
                            'Source parsing is partial; conditional branches/macros are not resolved. '
                            'Ambiguous definitions/overloads/saved names are withheld.'}
        with args.out.open('x') as stream:
            writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
            writer.writerow(['address', 'source'])
            writer.writerows((f'0x{a:08x}', key) for a, key in sorted(mapping.items()))
        with args.report.open('x') as stream:
            stream.write(json.dumps(report, indent=1)+'\n')
        print(f'{len(mapping)} candidates; {len(rows)-len(mapping)} withheld; no names verified')
        return 0
    mapping = read_mapping(args.mapping)
    calls, rets, sizes = program_facts(args.functions, args.model, set(mapping))
    report = check(mapping, calls, rets, src, sizes, args.small, set(args.implicit))
    report['inputs'] = inputs | {'mappingSha256': hashlib.sha256(args.mapping.read_bytes()).hexdigest()}
    if args.out:
        args.out.write_text(json.dumps(report, indent=1) + "\n")
    print(f"{report['mapped']} mapped; {report['edgesChecked']} call edges checked; "
          f"{report['contradicted']} functions contradicted")
    for r in report["rows"]:
        for x in r["contradictions"]:
            print(f"CONTRADICTION {r['address']} {r['source']}: {x}")
    return 1 if report["contradicted"] else 0


if __name__ == "__main__":
    sys.exit(main())
