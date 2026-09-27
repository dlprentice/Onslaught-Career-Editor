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
  python tools/re_source_graph.py check-calls --witnesses CALLS.json --source DIR
      --functions FUNCTIONS.tsv --out REPORT.json

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
    """Parameters without defaults; nested groups and literals cannot split them.

    A top-level angle operator in a default expression is ambiguous without C++
    name lookup (comparison versus template). Refuse it instead of certifying
    an argument count; callers indexing source withhold that definition.
    """
    args = args.strip()
    if args in ("", "void"):
        return []
    masked = E.mask_source_literals(args)
    if masked is None:
        raise ValueError('incomplete parameter literal')
    depth, start, default, pos, out = 0, 0, None, 0, []
    while pos < len(masked):
        ch = masked[pos]
        if ch in '([{':
            end = E.source_delimiter_end(masked, pos)
            if end is None:
                raise ValueError('incomplete parameter group')
            pos = end
            continue
        if default is None:
            depth += (ch == '<') - (ch == '>')
            if depth < 0:
                raise ValueError('unmatched parameter angle bracket')
            if ch == '=' and depth == 0:
                default = pos
        elif ch in '<>' and not (ch == '>' and pos and masked[pos - 1] == '-'):
            raise ValueError('ambiguous angle operator in parameter default')
        if ch == ',' and depth == 0:
            out.append(args[start:default if default is not None else pos].strip())
            start, default = pos + 1, None
        pos += 1
    if depth:
        raise ValueError('unmatched parameter angle bracket')
    return out + [args[start:default].strip()]


def outer_type_text(declaration: str) -> str | None:
    """Ignore template arguments when classifying indirection of the type itself.

    Aggregate<T*> is a by-value aggregate, unlike Aggregate<T*>*. An unmatched
    template or a pointer-to-member needs independent ABI evidence.
    """
    depth, out = 0, []
    for char in declaration:
        if char == '<':
            depth += 1
        elif char == '>':
            depth -= 1
            if depth < 0:
                return None
        elif depth == 0:
            out.append(char)
    outer = ''.join(out)
    return None if depth or re.search(r'::\s*\*', outer) else outer


def param_bytes(p: str) -> int | None:
    """Stack bytes one parameter takes; None when a by-value aggregate makes it unknown."""
    t = re.sub(r"\b(const|volatile|register|struct|class|enum|unsigned|signed)\b", " ", p)
    outer = outer_type_text(t)
    if outer is None:
        return None
    if "*" in outer or "&" in outer:
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
        masked = E.mask_source_literals(text)
        if masked is None:
            continue
        enum_types.update(re.findall(r'\benum\s+(?:class\s+|struct\s+)?(\w+)\s*(?::[^;{}]+)?\{', masked))
        for cm in re.finditer(r"\b(?:class|struct)\s+(\w+)(?:\s+final)?\s*(?::[^;{}()]*)?\{", masked):
            j = E.source_delimiter_end(masked, cm.end() - 1)
            if j is None:
                continue
            body = text[cm.end():j - 1]
            body_mask = masked[cm.end():j - 1]
            for m in re.finditer(r"\bstatic\s+[^;(){}]*?\b(~?\w+)\s*\(", body_mask):
                statics.add((cm.group(1), m.group(1)))
            # methods defined inside the class body are implicitly inline
            covered_until = 0
            for m in re.finditer(r"(?:^|[;{}])\s*(?P<head>[\w:<>*&\s]*?)\b"
                                 r"(?P<name>operator\s*=(?=\s*\()|~?[A-Za-z_]\w*)\s*\(", body_mask):
                name = re.sub(r'\s+', '', m.group('name'))
                if name in _KEYWORDS or m.start('name') < covered_until:
                    continue
                spans = E.source_definition_parts(body_mask, m.end() - 1, name == cm.group(1))
                if spans is None:
                    continue
                args_end, init_start, init_end, opening, k = spans
                covered_until = k
                key = f"{cm.group(1)}::{name}"
                method_body = body[opening + 1:k - 1]
                # Each definition position is distinct. Equal arguments/body
                # do not collapse const/nonconst overloads (or conditional
                # duplicate definitions) into a uniquely resolved identity.
                defs.append(E.SourceFunc(key, path.name, text.count("\n", 0, cm.end() + m.start('name')) + 1,
                                         method_body, [], [], text.count('\n', 0, cm.end() + k - 1) + 1,
                                         body[m.end():args_end - 1], "inline " + re.sub(
                                             r'^\s*(?:(?:public|protected|private)\s*:\s*)+', '', m.group("head")),
                                         body[init_start:init_end]))
    funcs: dict[str, list[E.SourceFunc]] = defaultdict(list)
    unsupported_names = set()
    for f in defs:
        try:
            params(f.args)
        except ValueError:
            unsupported_names.add(short(f.key))
    for f in defs:
        # Dropping only the refused overload can make another one falsely
        # unique. Withhold this entire short-name family, including unqualified
        # resolution, until all its parameter lists can be distinguished.
        if short(f.key) in unsupported_names:
            continue
        funcs[short(f.key)].append(f)
        if f.file.endswith((".h", ".hpp", ".inl")) or re.search(r"\binline\b", f.head):
            inline.add(short(f.key))
    src = Source(funcs, statics, inline)
    src.enum_types = enum_types
    names = set(funcs)
    for name, fs in funcs.items():
        for f in fs:
            call_text = E.mask_source_literals(f.initializers + '\n' + f.body)
            called = {c for c in re.findall(r"(?<!\w)(~?[A-Za-z_]\w*)\s*\(", call_text or '')
                      if c not in _KEYWORDS}   # obj.f( and p->f( too; literals are not calls
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
    outer = outer_type_text(ret)
    if not constructor and (outer is None or not (
            '*' in outer or '&' in outer or (_SCALAR_RET.match(ret) and '<' not in ret)
            or ret in src.enum_types)):
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
    """Read complete entry-seeded bodies, not the whole-image linear decode.

    A preceding switch table can make that cache start inside a real function
    and silently omit its first call or corrupt its measured size. Exported
    boundaries remain claims: require exact, unambiguous ownership and let the
    byte-checked decoder reject inconsistent extents and undecodable/truncated
    bytes. This establishes
    local instruction facts, not whole-CFG reachability or source identity.
    """
    img, mdl = E.load_or_build(model)
    prog = E.Program(img, mdl, E.load_functions(functions))
    if len({f.va for f in prog.funcs}) != len(prog.funcs):
        raise ValueError('duplicate exported function entries')
    calls, rets, sizes = {}, {}, {}
    for a in sorted(addresses):
        f = prog.by_va.get(a)
        if f is None:
            raise ValueError(f'mapped address is not an exported function entry: {a:#x}')
        if any(other.va != a and other.lo <= f.hi
               and (other.declared_hi or other.hi) >= f.lo for other in prog.funcs):
            raise ValueError(f'mapped function has overlapping exported ownership: {a:#x}')
        body = E.decode_entry_body(img, f)
        calls[a] = [t for i in body for kind, t in E.insn_refs(i, img) if kind == "call"]
        rets[a] = {int(i.ops, 16) if i.ops else 0 for i in body if i.mnem == "ret"}
        sizes[a] = sum(i.size for i in body)
    return calls, rets, sizes


def source_digest(root: Path, patterns: tuple[str, ...]) -> str:
    """Pin the exact source inputs, including names; neither mtimes nor saved labels are authority."""
    files = sorted({p for pattern in patterns for p in root.glob(pattern)})
    records = [(p.relative_to(root).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
    return hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()


def direct_call_witnesses(prog: E.Program, source_root: Path, document: dict) -> dict:
    """Check exact direct source-call transports against independently reviewed premises.

    Unlike the broad graph, this admits no transitive/inlining substitute for
    the selected source statement or CALL. Complete caller/callee byte pins,
    source pins, ordered arguments and receiver must agree. Saved names are not
    read. Caller identity and meanings of external registers remain explicitly
    reviewed premises, not facts inferred from those strings. Results establish
    a selected local path, not full behavior, provenance of every call or ABI.
    """
    if document.get('specimenSha256') != prog.img.sha256:
        raise ValueError('direct-call specimen pin mismatch')
    if len({f.va for f in prog.funcs}) != len(prog.funcs):
        raise ValueError('direct-call duplicate function entries')
    src = index(source_root, ('*.cpp', '*.h'), set())
    decoded = {}
    conditions = document.get('sourceConditions', [])
    condition_keys = [(c['file'], c['line']) for c in conditions]
    if len(set(condition_keys)) != len(condition_keys):
        raise ValueError('direct-call source conditions are duplicated')
    used_conditions, selected_text = set(), {}
    headers = [E.strip_comments(p.read_text(errors='replace')) for p in source_root.glob('*.h')]

    def span_matches(span):
        count = span['bytes']
        if type(count) is not int or count <= 0:
            return False
        raw = prog.img.read(int(span['address'],16),count)
        return len(raw)==count and hashlib.sha256(raw).hexdigest()==span['sha256']

    def activity(name, text):
        if name not in selected_text:
            lines = text.splitlines(keepends=True)
            for condition in conditions:
                if condition['file'] != name:
                    continue
                line = condition['line']
                if (type(line) is not int or not 1<=line<=len(lines)
                        or type(condition['value']) is not bool
                        or lines[line-1].strip() != condition['directive']
                        or re.fullmatch(r'#\s*if\s+[A-Za-z_]\w*\s*==\s*[A-Za-z_]\w*',
                                        condition['directive']) is None
                        or hashlib.sha256((source_root/name).read_bytes()).hexdigest()!=condition['sha256']
                        or not condition.get('evidence') or not condition.get('spans')
                        or not all(span_matches(span) for span in condition['spans'])):
                    raise ValueError('direct-call source condition premise or pins differ')
                # Preserve every character offset. Only this exact named
                # comparison is selected, under the recorded review premise;
                # never override a literal #if 0 or expand arbitrary macros.
                old = lines[line-1]
                replacement = '#if '+str(int(condition['value']))
                lines[line-1] = replacement + ''.join('\n' if c=='\n' else ' ' for c in old[len(replacement):])
                used_conditions.add((name,line))
            selected_text[name] = E._header_conditions(''.join(lines), set())
        return selected_text[name]

    def function(pin):
        address = int(pin['address'], 16)
        fn = prog.by_va.get(address)
        if fn is None or fn.thunk:
            raise ValueError('direct-call requires a non-thunk function entry')
        if any(other.va != address and other.lo <= fn.hi
               and (other.declared_hi or other.hi) >= fn.lo for other in prog.funcs):
            raise ValueError('direct-call overlapping function ownership')
        if address not in decoded:
            decoded[address] = E.decode_entry_body(prog.img, fn)
        raw = prog.img.read(address, fn.body_bytes)
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise ValueError('direct-call complete-body pin mismatch')
        return fn, decoded[address]

    def source(pin):
        name = pin['file']
        if Path(name).name != name:
            raise ValueError('direct-call source must be one pinned file')
        path = source_root / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin['sha256']:
            raise ValueError('direct-call source hash mismatch')
        definition = resolve(src, pin['function'])
        if definition is None or definition.file != name or definition.line != pin['line']:
            raise ValueError('direct-call source identity is absent or ambiguous')
        text = E.strip_comments(path.read_text(errors='replace'))
        masked = E.mask_source_literals(text)
        if masked is None:
            raise ValueError('direct-call source literals are incomplete')
        headers_ = []
        for match in E._FUNC_DEF.finditer(masked):
            key = (match.group('qual') or '')+re.sub(r'\s+','',match.group('name'))
            if key != definition.key or text.count('\n',0,match.start())+1 != definition.line:
                continue
            parts = E.source_definition_parts(masked,match.end()-1,False)
            if parts:
                headers_.append((match.start(),parts[3]+1))
        if len(headers_) != 1:
            raise ValueError('direct-call source declaration span is ambiguous or unsupported')
        begin,end = headers_[0]
        active,uncertain = activity(name,text)
        if active[begin:end]!=text[begin:end] or any(a<end and b>begin for a,b in uncertain):
            raise ValueError('direct-call source definition has unresolved or inactive preprocessing')
        return definition, text

    rows, seen = [], set()
    for witness in document['calls']:
        caller, body = function(witness['caller'])
        target, target_body = function(witness['target'])
        caller_source, caller_text = source(witness['caller']['source'])
        target_source, target_text = source(witness['target']['source'])
        if not witness.get('identityEvidence') or not witness.get('sourceArgumentEvidence'):
            raise ValueError('direct-call identity/argument premises require independent review')
        call_address = int(witness['callAddress'], 16)
        if call_address in seen:
            raise ValueError('direct-call duplicate call site')
        seen.add(call_address)
        expression = witness['sourceCall']
        call = re.fullmatch(r'([A-Za-z_]\w*)(\.|->)([A-Za-z_]\w*)\(([^()]*)\);', expression)
        if not call or call[3] != short(target_source.key) or '=' in call[4]:
            raise ValueError('direct-call source statement does not select its target')
        masked_body = E.mask_source_literals(caller_source.body)
        occurrences = list(re.finditer(r'(?<![\w.:>])'+re.escape(expression), masked_body or ''))
        occurrences = [match for match in occurrences
                       if not (masked_body or '')[:match.start()].rstrip().endswith(('.', '->', '::'))]
        if masked_body is None or len(occurrences) != 1 or caller_text.count(caller_source.body) != 1:
            raise ValueError('direct-call source statement is absent, repeated or a literal')
        source_offset = caller_text.index(caller_source.body) + occurrences[0].start()
        active, uncertain = activity(caller_source.file,caller_text)
        if (active[source_offset:source_offset+len(expression)] != expression
                or any(a < source_offset+len(expression) and b > source_offset for a,b in uncertain)):
            raise ValueError('direct-call source statement has unresolved preprocessing')
        if caller_text.count('\n', 0, source_offset)+1 != witness['sourceLine']:
            raise ValueError('direct-call source statement line mismatch')
        macros = {match.group(1) for text in [caller_text,target_text,*headers]
                  for match in re.finditer(r'^\s*#\s*define\s+(\w+)\b',text,re.M)}
        identifiers = set(re.findall(r'\b[A-Za-z_]\w*\b',
            expression+' '+caller_source.key+' '+target_source.key+' '+target_source.head+' '+target_source.args))
        if macros & identifiers:
            raise ValueError('direct-call source uses a known macro without a bound expansion')
        declared = params(target_source.args)
        # These are expressions, not C++ parameter declarations: a member
        # arrow's '>' must not be parsed as a template delimiter. Keep this
        # route deliberately narrow; calls, casts, operators and comma groups
        # need a separately supported transport rather than token guessing.
        expressions = [part.strip() for part in call[4].split(',')] if call[4].strip() else []
        if any(not re.fullmatch(r'(?:[A-Za-z_]\w*(?:(?:->|\.)[A-Za-z_]\w*)*|-?(?:0x[0-9a-fA-F]+|[0-9]+))',
                                expression) for expression in expressions):
            raise ValueError('direct-call source argument expression is unsupported')
        records = witness['arguments']
        if len(declared) != len(expressions) or len(records) != len(declared):
            raise ValueError('direct-call source argument arity mismatch')
        parts = target_source.key.split('::')
        if (len(parts) < 2 or (parts[-2], parts[-1]) in src.statics
                or re.search(r'\bstatic\b', target_source.head)):
            raise ValueError('direct-call route requires a proven non-static source member')
        want = expected_pop(src, target_source)
        if want is None or want != 4*len(records):
            raise ValueError('direct-call source ABI is unresolved or not DWORD arguments')
        rets = {int(i.ops,16) if i.ops else 0 for i in target_body if i.mnem=='ret'}
        if rets != {want}:
            raise ValueError('direct-call callee return cleanup differs from source')
        start = int(witness['window']['address'],16)
        end = start + witness['window']['bytes']
        window = [i for i in body if start <= i.va < end]
        if (not window or window[0].va != start or window[-1].va+window[-1].size != end
                or window[-1].va != call_address
                or (window[-1].mnem,window[-1].ops) != ('call',hex(target.va))):
            raise ValueError('direct-call window or direct target is not instruction-aligned')
        raw = prog.img.read(start,end-start)
        if hashlib.sha256(raw).hexdigest() != witness['window']['sha256']:
            raise ValueError('direct-call window hash mismatch')
        entries = [(int(i.ops,16),i.va) for i in body
                   if (i.mnem.startswith(('j','loop')) or i.mnem=='call') and E._DIRECT.fullmatch(i.ops)]
        entries += [(dest,site) for dest,refs in getattr(prog.model,'refs_to',{}).items()
                    for kind,site in refs if kind in ('call','jmp','jcc')]
        if any(start < dest < end for dest,_ in entries):
            raise ValueError('direct-call setup has a possible interior entry')
        facts, pushes = E.local_dword_transport(prog.img, window[:-1])
        if len(pushes) != len(records) or witness['receiver'] != facts['ecx']:
            raise ValueError('direct-call receiver or push count mismatch')
        for index_,(record,observed,declaration,argument) in enumerate(zip(records,reversed(pushes),declared,expressions)):
            if (record['sourceParameter'] != declaration or record['sourceArgument'] != argument
                    or record['stackOffset'] != 4+4*index_
                    or record['value'] != observed['value']
                    or int(record['pushAddress'],16) != int(observed['pushAddress'],16)):
                raise ValueError('direct-call argument order, value or source binding mismatch')
        needed = set(re.findall(r'window\.(e(?:ax|bx|cx|dx|si|di|bp|sp))',
                               ' '.join([facts['ecx'], *(p['value'] for p in pushes)])))
        bindings = witness.get('externalBindings',[])
        if len({b['register'] for b in bindings}) != len(bindings) or {b['register'] for b in bindings} != needed:
            raise ValueError('direct-call external bindings are absent, duplicate or unused')
        for binding in bindings:
            if not binding.get('meaning') or not binding.get('evidence') or not binding.get('spans'):
                raise ValueError('direct-call external binding lacks a reviewed byte premise')
            for span in binding['spans']:
                if not span_matches(span):
                    raise ValueError('direct-call external span hash mismatch')
        rows.append({'caller':f'0x{caller.va:08x}','callAddress':f'0x{call_address:08x}',
                     'target':f'0x{target.va:08x}','sourceCaller':caller_source.key,
                     'sourceTarget':target_source.key,'sourceCall':expression,
                     'receiver':facts['ecx'],'arguments':records,'returnPop':want,
                     'identityEvidence':witness['identityEvidence'],
                     'sourceArgumentEvidence':witness['sourceArgumentEvidence'],
                     'externalBindings':bindings})
    if not rows:
        raise ValueError('direct-call witness set is empty')
    if used_conditions != set(condition_keys):
        raise ValueError('direct-call source condition premise is unused')
    return {'result':'PASS','checkedCalls':len(rows),'rows':rows,'sourceConditionPremises':conditions,
            'limits':'Selected local direct-CALL/receiver/ordered-argument agreement under the recorded '
                     'independently reviewed caller-identity and source-meaning premises. No saved-name, '
                     'transitive-call or file-order inference; no whole-caller domination, return-type/storage, '
                     'complete ABI, runtime, device or semantic-parity certification. Object-memory bindings '
                     'presume no alias with outgoing stack writes. Known macro uses in selected files/pinned '
                     'headers are withheld; unavailable include/macro environments are not reconstructed. '
                     'Explicit source-condition selections are reviewed premises, not recovered build flags. '
                     'Target source bodies can differ from retail; only selected interface/cleanup is compared here.'}


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
    w = sub.add_parser('check-calls', help='exact direct-call transport under independently reviewed premises')
    w.add_argument('--witnesses', type=Path, required=True)
    w.add_argument('--source', type=Path, required=True)
    w.add_argument('--functions', type=Path, required=True)
    w.add_argument('--model', type=Path, default=DEFAULT_MODEL)
    w.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(argv)
    patterns = tuple(getattr(args, 'pattern', None) or ('*.cpp', '*.h'))
    if args.cmd == 'check-calls':
        if args.out.exists():
            ap.error('call report must be a new path')
        img, model = E.load_or_build(args.model)
        prog = E.Program(img, model, E.load_functions(args.functions))
        document = json.loads(args.witnesses.read_text())
        if document.get('functionsSha256') != hashlib.sha256(args.functions.read_bytes()).hexdigest():
            ap.error('call witness function export pin mismatch')
        report = direct_call_witnesses(prog, args.source, document)
        report['inputs'] = input_pins(args.functions, args.source, patterns) | {
            'witnessesSha256': hashlib.sha256(args.witnesses.read_bytes()).hexdigest()}
        with args.out.open('x') as stream:
            stream.write(json.dumps(report, indent=2)+'\n')
        print(f"{report['checkedCalls']} exact direct-call transports checked; semantic premises remain explicit")
        return 0
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
