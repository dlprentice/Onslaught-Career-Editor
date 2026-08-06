#!/usr/bin/env python3
"""Probe authoring tool -- turn an intent into a spliced BEA level archive.

    "make the engine do X on a schedule"  ->  a .aya the engine will load,
                                              plus a manifest that says exactly
                                              what was changed and why,
                                              plus a poison twin that should die.

WHY IT IS SHAPED LIKE THIS
--------------------------
A silent mis-write is this project's expensive failure mode: it does not look
like a bug, it looks like *engine behaviour*. So every write here is
content-anchored -- the caller states the bytes it expects to find and the tool
refuses on mismatch. There is no API path that takes a bare offset. The
container spec's own quoted offset was once wrong by 26 bytes; an anchor turns
that into a refusal instead of a desynchronised symbol table read as "the engine
rejects edits".

The grammar and the container codec are imported from `local-lab/`, not copied,
so there is one definition of each. See `bea_lab.py`.

Authority for every field: `local-lab/SCRIPT-FORMAT-SPEC-2026-08-02.md`,
read from the pristine specimen `BEA.exe.original.backup`
sha256 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750.
Section references below (`spec Sx.y`) point into that document.

WHAT IT CAN AUTHOR
------------------
  set-constant     retarget a compiled constant (the proven case: a Pause
                   duration).  Same length for int/float/bool; a string of a
                   different length needs --allow-length-change.
  set-script-trace set the first serialized script trailer dword, which retail
                   reads into CScriptObjectCode+0x60 and compares exactly with
                   1 after each executed instruction. Same length, anchored.
  retarget-call    point a CALL at a different native of the same arity and
                   return discipline, so a probe can invoke something we want to
                   observe.  Same length, always.
  poison-opcode    the proven poison: an opcode outside 0x00..0x1a makes
                   SpawnFromOpcode return NULL into an unchecked array ->
                   0xC0000005 (measured twice at ~13 s).
  poison-datatype  an unknown type tag makes CreateFromType consume nothing and
                   desynchronise the rest of the object.
  null-control     corrupt the 10-byte `end_script` sentinel.  The engine reads
                   and discards it (spec S3.2) so this predicts NO behaviour
                   change -- it is the arm that distinguishes "the engine ignored
                   our edit" from "we edited the wrong file".
  splice-script    append a whole donor script object to the table.  Nothing
                   inside an object is an offset (spec S7.1), so this is pure
                   concatenation plus a scriptCount bump.  Length-changing;
                   statically verified, never executed.
  replace-script   replace one script record in place with a deliberately tiny
                   straight-line program emitted from specimen-derived native
                   signatures.  Script name and table ordinal are preserved.
  raw              escape hatch.  Still requires expected bytes.

WHAT IT CANNOT AUTHOR, DELIBERATELY
-----------------------------------
  * type tags 5 and 6 (spec S9.4 -- never exercised by shipped data, widths come
    from the factory only).  Refused rather than guessed.
  * inserting a script anywhere but the end of the table.  Whether world "things"
    reference scripts by index is not established, so no existing script is ever
    renumbered.
  * compiling .msl.  The executable has the VM and no compiler. replace-script
    emits only straight-line let/call recipes; it is not a source compiler.
  * branches, jumps, arithmetic, nested expressions, or arbitrary opcodes.
    The bounded emitter uses only six corpus-observed operations and will not
    invent control flow.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

import bea_lab
import mission_script_emitter as mse

TOOL_VERSION = "1.1.0"
SPEC = "local-lab/SCRIPT-FORMAT-SPEC-2026-08-02.md"
SPECIMEN_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"

OP_CALL = 0x18
VALID_OPCODES = frozenset(range(0x00, 0x1B))  # spec S3.4
SENTINEL = b"end_script"
BLOCK = 1_048_576  # container block inflated size (all but the last)
WORLD_TAGS = (b"RLWD", b"BSWD")

# Type tags the tool will write a value for. 0 has no value bytes; 5 and 6 are
# never exercised by shipped data (spec S9.4) so we refuse rather than guess.
WRITABLE_TAGS = {1: "int", 2: "float", 3: "string", 4: "bool"}


# --------------------------------------------------------------------------- #
# errors
# --------------------------------------------------------------------------- #
class ProbeError(Exception):
    """Base for every refusal. The CLI turns these into exit code 2."""


class AnchorMismatch(ProbeError):
    """The bytes at the target offset are not the bytes the caller expected."""


class IntentError(ProbeError):
    """The intent cannot be expressed against this archive."""


class FramingError(ProbeError):
    """The archive did not parse, before or after the edit."""


class LengthChangeRefused(ProbeError):
    """A length-changing edit was required but not authorised."""


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def hx(b: bytes) -> str:
    return b.hex(" ")


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- #
# the edit primitives -- both carry the bytes they expect to displace
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Edit:
    """A same-length, content-anchored write into the inflated payload."""

    offset: int
    expect: bytes
    new: bytes
    kind: str
    description: str
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.expect) != len(self.new):
            raise ProbeError(
                f"Edit is not same-length ({len(self.expect)} -> {len(self.new)}); "
                "use a Splice for length-changing writes"
            )
        if not self.expect:
            raise ProbeError("Edit with empty expected bytes is not an anchor")

    @property
    def end(self) -> int:
        return self.offset + len(self.expect)

    def to_manifest(self, world_base: int | None = None) -> dict:
        d = {
            "kind": self.kind,
            "offset": self.offset,
            "length": len(self.expect),
            "expect_hex": hx(self.expect),
            "new_hex": hx(self.new),
            "description": self.description,
        }
        if world_base is not None:
            d["payload_offset"] = self.offset - world_base
        d.update(self.meta)
        return d


@dataclass(frozen=True)
class Splice:
    """A length-changing, content-anchored write.

    `expect_remove` are the exact bytes being removed at `offset` (empty for a
    pure insertion) and `expect_anchor` are the bytes that must be found starting
    at `offset` regardless -- so a pure insertion still has to name what it is
    inserting in front of.
    """

    offset: int
    expect_remove: bytes
    expect_anchor: bytes
    insert: bytes
    kind: str
    description: str
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.expect_anchor:
            raise ProbeError("Splice with no anchor bytes is a bare offset; refused")
        if self.expect_remove and not self.expect_anchor.startswith(self.expect_remove[: len(self.expect_anchor)]):
            # expect_remove and expect_anchor must agree on their overlap
            n = min(len(self.expect_remove), len(self.expect_anchor))
            if self.expect_remove[:n] != self.expect_anchor[:n]:
                raise ProbeError("Splice expect_remove and expect_anchor disagree")

    @property
    def delta(self) -> int:
        return len(self.insert) - len(self.expect_remove)

    def to_manifest(self, world_base: int | None = None) -> dict:
        d = {
            "kind": self.kind,
            "offset": self.offset,
            "removed": len(self.expect_remove),
            "inserted": len(self.insert),
            "delta": self.delta,
            "expect_remove_hex": hx(self.expect_remove),
            "expect_anchor_hex": hx(self.expect_anchor[:32]),
            "insert_sha256": sha256(self.insert),
            "description": self.description,
        }
        if len(self.insert) <= 64:
            d["insert_hex"] = hx(self.insert)
        if world_base is not None:
            d["payload_offset"] = self.offset - world_base
        d.update(self.meta)
        return d


def verify_anchor(buf: bytes, offset: int, expect: bytes, what: str) -> None:
    """The refusal. Nothing in this module writes without going through here."""
    if offset < 0 or offset + len(expect) > len(buf):
        raise AnchorMismatch(
            f"{what}: range [{offset},{offset + len(expect)}) is outside the "
            f"{len(buf)}-byte payload"
        )
    have = buf[offset : offset + len(expect)]
    if have != expect:
        raise AnchorMismatch(
            f"{what}: anchor mismatch at {offset}\n"
            f"    expected {hx(expect)}\n"
            f"    found    {hx(have)}\n"
            "  REFUSED. The archive is not the one this edit was computed against, "
            "or the offset is wrong. Re-derive from a parse; never trust a quoted offset."
        )


def apply_edits(buf: bytes, edits: list[Edit], splice: Splice | None = None) -> bytes:
    """Verify every anchor, refuse on overlap, then write. Order-independent."""
    ordered = sorted(edits, key=lambda e: e.offset)
    for a, b in zip(ordered, ordered[1:]):
        if b.offset < a.end:
            raise ProbeError(
                f"edits overlap: {a.kind}@[{a.offset},{a.end}) and "
                f"{b.kind}@[{b.offset},{b.end})"
            )
    for e in ordered:
        verify_anchor(buf, e.offset, e.expect, f"{e.kind} ({e.description})")
    out = bytearray(buf)
    for e in ordered:
        out[e.offset : e.end] = e.new
    if splice is not None:
        verify_anchor(bytes(out), splice.offset, splice.expect_anchor,
                      f"{splice.kind} ({splice.description})")
        if splice.expect_remove:
            verify_anchor(bytes(out), splice.offset, splice.expect_remove,
                          f"{splice.kind} removal ({splice.description})")
        if ordered and ordered[-1].end > splice.offset:
            # a same-length edit inside the removed/inserted region would be
            # silently discarded
            for e in ordered:
                if e.offset < splice.offset + len(splice.expect_remove) and e.end > splice.offset:
                    raise ProbeError(
                        f"edit {e.kind}@{e.offset} lies inside the splice region; refused"
                    )
        out[splice.offset : splice.offset + len(splice.expect_remove)] = splice.insert
    return bytes(out)


# --------------------------------------------------------------------------- #
# container + chunk model
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ChunkNode:
    tag: bytes
    hdr_off: int   # offset of the 4-byte tag
    size_off: int  # offset of the u32 size field
    body: int
    end: int


def chunk_chain(data: bytes, base: int, end: int):
    pos = base
    while pos + 8 <= end:
        tag = data[pos : pos + 4]
        (size,) = struct.unpack_from("<I", data, pos + 4)
        body = pos + 8
        if body + size > end:
            raise FramingError(f"chunk {tag!r} at {pos} overruns {end}")
        yield ChunkNode(tag, pos, pos + 4, body, body + size)
        pos = body + size
    if pos != end:
        raise FramingError(f"chunk chain ended at {pos}, expected {end}")


def find_chunk_path(data: bytes, *tags: bytes) -> list[ChunkNode]:
    """Return the node chain for e.g. (WRES, WRLD, RLWD), or raise."""
    out: list[ChunkNode] = []
    base, end = 0, len(data)
    for t in tags:
        for node in chunk_chain(data, base, end):
            if node.tag == t:
                out.append(node)
                base, end = node.body, node.end
                break
        else:
            raise FramingError(f"chunk {t!r} not found in [{base},{end})")
    return out


class World:
    """One RLWD / BSWD world chunk, parsed to the script table."""

    def __init__(self, inflated: bytes, chain: list[ChunkNode], parse_mod):
        self.chain = chain
        self.node = chain[-1]
        self.tag = self.node.tag.decode()
        self.base = self.node.body
        self.end = self.node.end
        self.payload = inflated[self.base : self.end]
        try:
            self.parsed = parse_mod.parse_world(self.payload)
        except Exception as exc:  # noqa: BLE001 - parser raises its own types
            raise FramingError(f"{self.tag}: {type(exc).__name__}: {exc}") from exc
        self.scripts = self.parsed["table"]["scripts"]
        self.by_name = {s["name"]: s for s in self.scripts}
        self.count_off = self.base + self.parsed["table"]["count_off"]

    @property
    def script_count(self) -> int:
        return self.parsed["table"]["count"]

    def script(self, name: str) -> dict:
        s = self.by_name.get(name)
        if s is None:
            near = ", ".join(sorted(self.by_name)[:12])
            raise IntentError(
                f"{self.tag} has no script named {name!r}. Present: {near}"
                f"{' ...' if len(self.by_name) > 12 else ''}"
            )
        return s

    def abs(self, payload_off: int) -> int:
        return self.base + payload_off

    def sentinels_ok(self) -> tuple[int, int]:
        good = sum(1 for s in self.scripts if s["sentinel"] == SENTINEL)
        return good, len(self.scripts)


class Archive:
    """An inflated .aya plus its world chunks. Read-only."""

    def __init__(self, path: str | os.PathLike, lab=None):
        self.path = str(Path(path).resolve())
        self.lab_root, self._aya, self._sp, self._ba = bea_lab.load(lab)
        raw, inflated, blocks = self._aya.read_aya(self.path)
        self.raw = raw
        self.inflated = inflated
        self.blocks = blocks  # [(compressed, inflated), ...]
        self.block_sizes = [b[1] for b in blocks]
        self.file_sha = sha256(raw)
        self.inflated_sha = sha256(inflated)
        self.worlds: dict[str, World] = {}
        for tag in WORLD_TAGS:
            try:
                chain = find_chunk_path(inflated, b"WRES", b"WRLD", tag)
            except FramingError:
                continue
            self.worlds[tag.decode()] = World(inflated, chain, self._sp)

    def world(self, tag: str = "RLWD") -> World:
        w = self.worlds.get(tag)
        if w is None:
            raise IntentError(
                f"{Path(self.path).name} has no {tag} world chunk "
                f"(has: {', '.join(self.worlds) or 'none'})"
            )
        return w

    def blocks_regular(self) -> bool:
        """Every block inflates to exactly BLOCK except the last."""
        if not self.block_sizes:
            return False
        return all(n == BLOCK for n in self.block_sizes[:-1]) and 0 < self.block_sizes[-1] <= BLOCK


def reblock(total: int) -> list[int]:
    """Block sizes for a payload of `total` bytes, preserving the shipped rule."""
    if total <= 0:
        raise ProbeError("empty payload")
    full, rem = divmod(total, BLOCK)
    sizes = [BLOCK] * full
    if rem:
        sizes.append(rem)
    return sizes


# --------------------------------------------------------------------------- #
# natives: the descriptor table and the corpus-observed call profile
# --------------------------------------------------------------------------- #
def load_natives(lab_root: Path) -> dict[int, str]:
    p = Path(lab_root) / "msl" / "natives.json"
    if not p.is_file():
        raise ProbeError(f"native descriptor table not found at {p}")
    tbl = json.load(open(p, encoding="utf-8"))
    nat = {t["i"]: t["name"] for t in tbl}
    nat[0] = nat.get(0) or "FollowWaypoint"  # slot 0 is statically initialised
    return {k: v for k, v in nat.items() if v}


def decode_call(operand: int) -> tuple[int, int, int]:
    """spec S3.4: bits 0..7 native index, 8..15 argc, 16..31 return-expected."""
    u = operand & 0xFFFFFFFF
    return u & 0xFF, (u >> 8) & 0xFF, (u >> 16) & 0xFFFF


def encode_call(index: int, argc: int, ret_hi: int) -> int:
    if not 0 <= index <= 0xFF:
        raise IntentError(f"native index {index} does not fit the 8-bit field")
    if not 0 <= argc <= 0xFF:
        raise IntentError(f"argc {argc} does not fit the 8-bit field")
    if not 0 <= ret_hi <= 0xFFFF:
        raise IntentError(f"return word {ret_hi} does not fit the 16-bit field")
    v = (ret_hi << 16) | (argc << 8) | index
    return struct.unpack("<i", struct.pack("<I", v))[0]


def build_call_profile(corpus_dir: str | os.PathLike, lab=None) -> dict:
    """Observed (argc, return) per native over every archive in `corpus_dir`.

    All 9,236 shipped CALLs give each native exactly one profile, which is what
    makes `retarget-call` checkable: a retarget that changes arity or return
    discipline would unbalance the VM stack, and we can refuse it rather than
    discover it as a crash.
    """
    _root, _aya, sp, ba = bea_lab.load(lab)
    nat = load_natives(_root)
    prof: dict[str, dict] = {}
    archives = sorted(Path(corpus_dir).glob("*_res_PC.aya"))
    if not archives:
        raise ProbeError(f"no *_res_PC.aya under {corpus_dir}")
    scanned = 0
    for p in archives:
        inf = ba.inflate_aya(str(p))
        for tag in WORLD_TAGS:
            try:
                chain = find_chunk_path(inf, b"WRES", b"WRLD", tag)
            except FramingError:
                continue
            parsed = sp.parse_world(inf[chain[-1].body : chain[-1].end])
            scanned += 1
            for s in parsed["table"]["scripts"]:
                for op, arg in s["instructions"]:
                    if op != OP_CALL:
                        continue
                    idx, argc, hi = decode_call(arg)
                    name = nat.get(idx)
                    if not name:
                        continue
                    e = prof.setdefault(name, {"index": idx, "profiles": {}, "calls": 0})
                    e["calls"] += 1
                    key = f"{argc}/{1 if hi else 0}"
                    e["profiles"][key] = e["profiles"].get(key, 0) + 1
    return {
        "generated_utc": _now(),
        "corpus": str(Path(corpus_dir).resolve()),
        "archives": len(archives),
        "world_chunks": scanned,
        "natives_in_table": len(nat),
        "natives_called": len(prof),
        "by_name": prof,
    }


def get_profile(corpus_dir: str | os.PathLike | None, cache: str | os.PathLike | None,
                lab=None) -> dict:
    if cache and Path(cache).is_file():
        return json.load(open(cache, encoding="utf-8"))
    if not corpus_dir:
        raise ProbeError(
            "no native call profile: pass --corpus <Resources dir> (or --profile-cache "
            "pointing at a built one). retarget-call cannot be checked without it."
        )
    prof = build_call_profile(corpus_dir, lab=lab)
    if cache:
        Path(cache).parent.mkdir(parents=True, exist_ok=True)
        json.dump(prof, open(cache, "w", encoding="utf-8"), indent=1)
    return prof


# --------------------------------------------------------------------------- #
# intent -> edits
# --------------------------------------------------------------------------- #
def _symbol(script: dict, sel) -> dict:
    syms = script["symtab"]["symbols"]
    if isinstance(sel, int) or (isinstance(sel, str) and sel.lstrip("#").isdigit()):
        i = int(str(sel).lstrip("#"))
        if not 0 <= i < len(syms):
            raise IntentError(f"{script['name']}: symbol index {i} out of range 0..{len(syms) - 1}")
        return syms[i]
    matches = [s for s in syms if s["name"] == sel or s["name"] == f"const {sel}"]
    if not matches:
        names = ", ".join(s["name"] for s in syms)
        raise IntentError(f"{script['name']}: no symbol {sel!r}. Symbols: {names}")
    if len(matches) > 1:
        raise IntentError(
            f"{script['name']}: symbol {sel!r} is ambiguous "
            f"(indices {[m['index'] for m in matches]}); select by #index"
        )
    return matches[0]


def _encode_value(tag: int, value) -> bytes:
    if tag == 1:
        return struct.pack("<i", int(value))
    if tag == 2:
        return struct.pack("<f", float(value))
    if tag == 4:
        if isinstance(value, str):
            v = value.strip().lower()
            if v in ("true", "1", "yes"):
                value = 1
            elif v in ("false", "0", "no"):
                value = 0
            else:
                raise IntentError(f"cannot read {value!r} as a bool")
        return struct.pack("<i", 1 if int(value) else 0)
    if tag == 3:
        if not isinstance(value, str):
            raise IntentError("a string symbol needs a string value")
        return value.encode("latin-1")
    raise IntentError(f"internal: no encoder for tag {tag}")


def intent_set_constant(world: World, spec: dict):
    """Retarget a compiled constant. The proven case is a Pause duration."""
    script = world.script(spec["script"])
    sym = _symbol(script, spec["symbol"])
    tag = sym["type"]
    if tag == 0:
        raise IntentError(
            f"{script['name']}.{sym['name']} has type tag 0 -- no value bytes in the "
            "stream (spec S3.5). There is nothing to retarget."
        )
    if tag not in WRITABLE_TAGS:
        raise IntentError(
            f"{script['name']}.{sym['name']} has type tag {tag}. Tags 5 and 6 are never "
            f"exercised by shipped data (spec S9.4); their widths come from the factory "
            "only. REFUSED rather than guessed."
        )
    new = _encode_value(tag, spec["value"])
    val_off = world.abs(sym["value_off"])
    if tag == 3:
        # read_value records value_off at the LENGTH PREFIX and value_len as the
        # character count -- they do not describe the same span. Handle explicitly.
        chars_off = val_off + 4
        old_chars = world.payload[sym["value_off"] + 4 : sym["value_off"] + 4 + sym["value_len"]]
        old_prefix = world.payload[sym["value_off"] : sym["value_off"] + 4]
        if len(new) == len(old_chars):
            return [Edit(chars_off, old_chars, new, "set-constant",
                         f"{script['name']} symbol #{sym['index']} {sym['name']!r} (string) "
                         f"{old_chars.decode('latin-1')!r} -> {spec['value']!r}",
                         {"script": script["name"], "symbol": sym["name"],
                          "symbol_index": sym["index"], "type_tag": tag})], None
        splice = Splice(
            val_off,
            old_prefix + old_chars,
            old_prefix + old_chars,
            struct.pack("<i", len(new)) + new,
            "set-constant-resize",
            f"{script['name']} symbol #{sym['index']} {sym['name']!r} (string) "
            f"{old_chars.decode('latin-1')!r} -> {spec['value']!r} "
            f"({len(old_chars)} -> {len(new)} chars, string32 prefix rewritten)",
            {"script": script["name"], "symbol": sym["name"],
             "symbol_index": sym["index"], "type_tag": tag},
        )
        return [], splice

    old = world.payload[sym["value_off"] : sym["value_off"] + sym["value_len"]]
    if len(old) != len(new):
        raise IntentError(f"internal: tag {tag} width {len(old)} vs encoded {len(new)}")
    return [Edit(val_off, old, new, "set-constant",
                 f"{script['name']} symbol #{sym['index']} {sym['name']!r} "
                 f"({WRITABLE_TAGS[tag]}) {sym['value']!r} -> {spec['value']!r}"
                 + (f"  [{spec['why']}]" if spec.get("why") else ""),
                 {"script": script["name"], "symbol": sym["name"],
                  "symbol_index": sym["index"], "type_tag": tag,
                  "old_value": sym["value"], "new_value": spec["value"]})], None


def _instruction(script: dict, i: int) -> tuple[int, int, int]:
    if not 0 <= i < script["instr_count"]:
        raise IntentError(
            f"{script['name']}: instruction {i} out of range 0..{script['instr_count'] - 1}"
        )
    op, arg = script["instructions"][i]
    return op, arg, script["instr_off"] + i * 8


def intent_retarget_call(world: World, spec: dict, natives: dict[int, str], profile: dict):
    """Point a CALL at a different native of the same arity and return discipline."""
    script = world.script(spec["script"])
    i = int(spec["instruction"])
    op, arg, ioff = _instruction(script, i)
    if op != OP_CALL:
        raise IntentError(
            f"{script['name']} instruction {i} is opcode {op:#04x}, not CALL ({OP_CALL:#04x}). "
            "Nothing to retarget."
        )
    old_idx, argc, hi = decode_call(arg)
    old_name = natives.get(old_idx, f"<{old_idx}>")

    want = spec["native"]
    by_name = {v: k for k, v in natives.items()}
    if isinstance(want, int) or str(want).isdigit():
        new_idx = int(want)
        new_name = natives.get(new_idx)
        if new_name is None:
            raise IntentError(f"native slot {new_idx} is unnamed in the descriptor table")
    else:
        new_idx = by_name.get(want)
        if new_idx is None:
            raise IntentError(
                f"no native named {want!r} in the 144-slot descriptor table. "
                f"Try `probe_author.py natives`."
            )
        new_name = want

    if new_idx == old_idx:
        raise IntentError(f"{script['name']} instruction {i} already calls {new_name}")

    # The guard that matters: arity and return discipline must match, or the VM
    # stack unbalances. Every one of the 9,236 shipped CALLs gives its native a
    # single (argc, return) profile, so this is checkable evidence, not a hunch.
    if not spec.get("allow_unprofiled"):
        entry = profile.get("by_name", {}).get(new_name)
        if entry is None:
            raise IntentError(
                f"{new_name} is in the descriptor table but is never called by any shipped "
                f"script, so its arity and return discipline are unobserved. REFUSED. "
                f"Pass allow_unprofiled to override -- and expect to need a poison arm."
            )
        want_key = f"{argc}/{1 if hi else 0}"
        if want_key not in entry["profiles"]:
            obs = ", ".join(f"{k} x{v}" for k, v in sorted(entry["profiles"].items()))
            raise IntentError(
                f"arity/return mismatch: {old_name} is called here as argc={argc}, "
                f"returns={'yes' if hi else 'no'}; {new_name} is only ever observed as "
                f"[{obs}] over {entry['calls']} shipped calls. REFUSED -- retargeting "
                "across arities unbalances the VM stack."
            )

    new_arg = encode_call(new_idx, argc, hi)
    old_bytes = struct.pack("<ii", op, arg)
    new_bytes = struct.pack("<ii", op, new_arg)
    symnames = {s["name"] for s in script["symtab"]["symbols"]}
    return [Edit(
        world.abs(ioff), old_bytes, new_bytes, "retarget-call",
        f"{script['name']} instruction {i}: CALL {old_name} -> CALL {new_name} "
        f"(argc={argc}, {'returns a value' if hi else 'void'}; operand "
        f"{arg & 0xFFFFFFFF:#010x} -> {new_arg & 0xFFFFFFFF:#010x})"
        + (f"  [{spec['why']}]" if spec.get("why") else ""),
        {"script": script["name"], "instruction": i,
         "old_native": old_name, "new_native": new_name,
         "old_native_index": old_idx, "new_native_index": new_idx,
         "argc": argc, "returns_value": bool(hi),
         # Not a requirement -- ExecuteCall resolves the index directly and never
         # consults the symbol table. Recorded because all 9,236 shipped calls
         # satisfy it, so a divergence is worth seeing in the manifest.
         "new_native_named_in_symtab": new_name in symnames},
    )], None


def intent_poison_opcode(world: World, spec: dict):
    """The proven poison. spec S3.4 / S8.7: an opcode outside 0x00..0x1a makes
    SpawnFromOpcode print `FATAL ERROR: uknown instruction` and return NULL into
    an array the caller does not check -> the measured 0xC0000005."""
    script = world.script(spec["script"])
    i = int(spec["instruction"])
    op, arg, ioff = _instruction(script, i)
    bad = int(spec.get("opcode", 0x7F))
    if bad in VALID_OPCODES:
        raise IntentError(
            f"poison opcode {bad:#04x} is INSIDE the accepted range 0x00..0x1a, so "
            "SpawnFromOpcode would accept it and the arm would not die. That is not a "
            "poison -- it is an untested edit. REFUSED."
        )
    if not 0 <= bad <= 0xFFFFFFFF:
        raise IntentError("poison opcode does not fit a dword")
    old = struct.pack("<i", op)
    new = struct.pack("<I", bad)
    return [Edit(world.abs(ioff), old, new, "poison-opcode",
                 f"POISON: {script['name']} instruction {i} opcode {op:#04x} -> {bad:#04x} "
                 "(outside 0x00..0x1a; SpawnFromOpcode returns NULL -> expected 0xC0000005)",
                 {"script": script["name"], "instruction": i,
                  "old_opcode": op, "new_opcode": bad,
                  "expected_outcome": "crash 0xC0000005 during level load"})], None


def intent_poison_datatype(world: World, spec: dict):
    """spec S3.5: an unknown type tag makes CreateFromType consume NOTHING,
    desynchronising every field after it."""
    script = world.script(spec["script"])
    sym = _symbol(script, spec["symbol"])
    bad = int(spec.get("tag", 9))
    if bad in (0, 1, 2, 3, 4, 5, 6):
        raise IntentError(
            f"type tag {bad} is accepted by CreateFromType, so the arm would not die. REFUSED."
        )
    # the tag dword sits immediately before the value
    if sym["type"] == 3:
        tag_off = sym["value_off"] - 4
    else:
        tag_off = sym["value_off"] - 4
    old = world.payload[tag_off : tag_off + 4]
    if struct.unpack("<i", old)[0] != sym["type"]:
        raise IntentError(
            f"internal: type tag for {sym['name']} does not sit at value_off-4 "
            f"(found {hx(old)} for tag {sym['type']})"
        )
    return [Edit(world.abs(tag_off), old, struct.pack("<i", bad), "poison-datatype",
                 f"POISON: {script['name']} symbol #{sym['index']} {sym['name']!r} type tag "
                 f"{sym['type']} -> {bad} (unknown to CreateFromType; consumes nothing, "
                 "desynchronises the rest of the object)",
                 {"script": script["name"], "symbol": sym["name"],
                  "symbol_index": sym["index"], "old_tag": sym["type"], "new_tag": bad,
                  "expected_outcome": "FATAL ERROR: unknown data type, then desync"})], None


def intent_null_control(world: World, spec: dict):
    """Corrupt the sentinel. spec S3.2: the engine reads and discards it and the
    literal does not occur in the executable, so this predicts NO behaviour
    change. It is the arm that separates `the engine ignored our edit` from
    `we edited a file the engine never opened`."""
    script = world.script(spec["script"])
    off = script["sentinel_off"]
    old = world.payload[off : off + 10]
    if old != SENTINEL:
        raise AnchorMismatch(f"{script['name']}: sentinel is {old!r}, not {SENTINEL!r}")
    new = spec.get("bytes")
    new = new.encode("latin-1") if isinstance(new, str) else (new or b"XXXXXXXXXX")
    if len(new) != 10:
        raise IntentError("sentinel replacement must be exactly 10 bytes")
    return [Edit(world.abs(off), old, new, "null-control",
                 f"NULL CONTROL: {script['name']} sentinel {SENTINEL.decode()!r} -> "
                 f"{new.decode('latin-1')!r} (engine reads and discards it; predicts NO "
                 "behaviour change)",
                 {"script": script["name"],
                  "expected_outcome": "no observable change; arm must behave as the probe"})], None


def intent_raw(world: World, spec: dict):
    """Escape hatch. Still content-anchored -- there is no bare-offset path."""
    off = int(spec["offset"])
    expect = bytes.fromhex(spec["expect"]) if isinstance(spec["expect"], str) else spec["expect"]
    new = bytes.fromhex(spec["new"]) if isinstance(spec["new"], str) else spec["new"]
    return [Edit(off, expect, new, "raw",
                 spec.get("why") or f"raw {len(expect)}-byte write at {off}")], None


def intent_set_script_trace(world: World, spec: dict):
    """Set the serialized per-script VM trace mode without a bare offset.

    The retail constructor reads object trailer dword A into
    CScriptObjectCode+0x60. CScriptObjectCode__Run compares it exactly with 1
    before emitting the post-instruction trace line. Values 0 and 2 are useful
    controls; 1 is the only enabling value.
    """
    unknown = set(spec) - {"op", "script", "value", "why"}
    missing = {"script"} - set(spec)
    if unknown or missing:
        raise IntentError(
            f"set-script-trace schema mismatch: unknown={sorted(unknown)}, "
            f"missing={sorted(missing)}"
        )
    value = spec.get("value", 1)
    if type(value) is not int or value not in {0, 1, 2}:
        raise IntentError(
            "set-script-trace.value must be integer 0, 1, or 2; retail enables "
            "the trace only for exact value 1"
        )
    script = world.script(spec["script"])
    if len(script.get("trailer", [])) != 2:
        raise FramingError(f"{script['name']}: expected exactly two object trailer dwords")
    trailer_off = script["end"] - 8
    old = world.payload[trailer_off:trailer_off + 4]
    expected = struct.pack("<i", script["trailer"][0])
    if old != expected:
        raise AnchorMismatch(
            f"{script['name']}: trailerA parser value {script['trailer'][0]} does not "
            f"match bytes {hx(old)}"
        )
    new = struct.pack("<i", value)
    if new == old:
        raise IntentError(
            f"{script['name']}: trailerA is already {value}; identity trace edit refused"
        )
    ordinal = world.scripts.index(script)
    expected_outcome = (
        "post-instruction VM trace lines when the separately enabled file logger is writable"
        if value == 1
        else "no VM trace lines; exact-comparison control"
    )
    return [Edit(
        world.abs(trailer_off), old, new, "set-script-trace",
        spec.get("why")
        or f"{script['name']} trailerA {script['trailer'][0]} -> {value} "
           f"(CScriptObjectCode+0x60; exact value 1 enables post-instruction trace)",
        {
            "script": script["name"],
            "scriptOrdinal": ordinal,
            "objectField": "CScriptObjectCode+0x60",
            "serializedField": "trailerA",
            "oldValue": script["trailer"][0],
            "newValue": value,
            "expectedOutcome": expected_outcome,
        },
    )], None


def intent_splice_script(world: World, spec: dict, lab=None):
    """Append a whole compiled object to the script table.

    spec S7.1: there is no size or offset field anywhere inside an object, and
    its only indices (instruction, symbol) are local to it -- so this is pure
    concatenation plus a scriptCount bump. Appending at the END never renumbers
    an existing script, which matters because whether world `things` reference
    scripts by index is NOT established.
    """
    donor_path = spec.get("donor_archive")
    donor_arch = world if donor_path is None else None
    if donor_path is not None:
        donor_arch = Archive(donor_path, lab=lab).world(spec.get("donor_world", "RLWD"))
    donor = donor_arch.script(spec["donor_script"])
    blob = donor_arch.payload[donor["record_start"] : donor["record_end"]]
    if not blob.endswith(SENTINEL):
        raise FramingError("donor record does not end on its sentinel")

    as_name = spec.get("as_name")
    if as_name:
        old_name = donor["name"].encode("latin-1")
        new_name = as_name.encode("latin-1")
        head = struct.pack("<i", len(old_name)) + old_name
        if not blob.startswith(head):
            raise FramingError("donor record does not start with its own string32 name")
        blob = struct.pack("<i", len(new_name)) + new_name + blob[len(head) :]

    if world.by_name.get(as_name or donor["name"]):
        raise IntentError(
            f"{world.tag} already has a script named {as_name or donor['name']!r}; "
            "pass as_name to rename the copy"
        )

    tail = world.scripts[-1]
    ins_at = world.abs(tail["record_end"])
    anchor = world.payload[tail["record_end"] - 10 : tail["record_end"]]
    if anchor != SENTINEL:
        raise FramingError("table does not end on a sentinel")
    # anchor the insertion on the sentinel it follows, plus whatever comes next
    after = world.payload[tail["record_end"] : tail["record_end"] + 16]

    count_old = struct.pack("<i", world.script_count)
    count_new = struct.pack("<i", world.script_count + 1)
    bump = Edit(world.count_off, count_old, count_new, "script-count",
                f"{world.tag} scriptCount {world.script_count} -> {world.script_count + 1}",
                {"world": world.tag})
    splice = Splice(
        ins_at, b"", after, blob, "splice-script",
        f"append script {as_name or donor['name']!r} ({len(blob)} bytes, "
        f"{donor['instr_count']} instructions, {len(donor['symtab']['symbols'])} symbols) "
        f"to the end of the {world.tag} table"
        + (f" from {Path(donor_path).name}" if donor_path else " (self-copy)"),
        {"world": world.tag, "donor_script": donor["name"],
         "as_name": as_name or donor["name"],
         "donor_archive": str(donor_path) if donor_path else "self",
         "instructions": donor["instr_count"],
         "symbols": len(donor["symtab"]["symbols"])},
    )
    return [bump], splice


def intent_replace_script(world: World, spec: dict, lab=None):
    """Replace one record without changing its name or table ordinal.

    This is the attachment-safe path for a probe program: a world thing that
    already names `Setup` continues to name the same record at the same ordinal.
    The replacement bytes come only from the bounded straight-line emitter;
    arbitrary record bytes are not accepted here.
    """
    unknown = set(spec) - {"op", "script", "program", "why"}
    missing = {"script", "program"} - set(spec)
    if unknown or missing:
        raise IntentError(
            f"replace-script schema mismatch: unknown={sorted(unknown)}, missing={sorted(missing)}"
        )
    target = world.script(spec["script"])
    try:
        emitted = mse.emit_record_from_lab(target["name"], spec["program"], bea_lab.find_lab(lab))
    except mse.EmitError as exc:
        raise IntentError(f"replace-script {target['name']}: {exc}") from exc

    old = world.payload[target["record_start"] : target["record_end"]]
    if emitted.record == old:
        raise IntentError(f"replace-script {target['name']} emitted an identity record")
    index = world.scripts.index(target)
    splice = Splice(
        world.abs(target["record_start"]),
        old,
        old,
        emitted.record,
        "replace-script",
        f"replace {world.tag} script {target['name']!r} at table ordinal {index} "
        f"({len(old)} -> {len(emitted.record)} bytes; "
        f"{target['instr_count']} -> {emitted.metadata['instructionCount']} instructions)"
        + (f"  [{spec['why']}]" if spec.get("why") else ""),
        {
            "world": world.tag,
            "script": target["name"],
            "scriptOrdinal": index,
            "oldRecordSha256": sha256(old),
            "newRecordSha256": emitted.metadata["recordSha256"],
            "oldInstructions": target["instr_count"],
            "newInstructions": emitted.metadata["instructionCount"],
            "emitter": emitted.metadata,
        },
    )
    return [], splice
INTENTS = {
    "set-constant": "intent_set_constant",
    "retarget-call": "intent_retarget_call",
    "poison-opcode": "intent_poison_opcode",
    "poison-datatype": "intent_poison_datatype",
    "null-control": "intent_null_control",
    "set-script-trace": "intent_set_script_trace",
    "raw": "intent_raw",
    "splice-script": "intent_splice_script",
    "replace-script": "intent_replace_script",
}
# Intents that are MEANT to break the format. The post-edit gate inverts itself
# for these: the predicted breakage must actually happen, and nothing else may.
#   "desync"   -> the grammar must stop walking (CreateFromType consumes nothing)
#   "sentinel" -> exactly one 10-byte sentinel must stop reading "end_script"
# poison-opcode is deliberately NOT here: a bad opcode is still 8 well-framed
# bytes, so our parser walks straight past it. It breaks the engine's instruction
# factory, not the framing -- which is precisely why it is the clean poison.
FRAMING_BREAKING = {"poison-datatype": "desync", "null-control": "sentinel"}


# --------------------------------------------------------------------------- #
# chunk-size fixups for a length change
# --------------------------------------------------------------------------- #
def size_fixups(inflated: bytes, splice: Splice) -> list[Edit]:
    """Every chunk whose body contains the splice point grows by `delta`."""
    delta = splice.delta
    if delta == 0:
        return []
    fix: list[Edit] = []

    def walk(base: int, end: int, path: str) -> None:
        for node in chunk_chain(inflated, base, end):
            if node.body <= splice.offset <= node.end:
                (size,) = struct.unpack_from("<I", inflated, node.size_off)
                fix.append(Edit(
                    node.size_off, struct.pack("<I", size), struct.pack("<I", size + delta),
                    "chunk-size",
                    f"chunk {node.tag.decode()} ({path}{node.tag.decode()}) size "
                    f"{size} -> {size + delta}",
                    {"tag": node.tag.decode()},
                ))
                if node.end - node.body >= 8:
                    try:
                        walk(node.body, node.end, f"{path}{node.tag.decode()}/")
                    except FramingError:
                        pass  # leaf chunk whose body is not a chunk chain
                return

    walk(0, len(inflated), "")
    if not fix:
        raise FramingError(f"splice point {splice.offset} is not inside any chunk")
    return fix


# --------------------------------------------------------------------------- #
# the authoring pipeline
# --------------------------------------------------------------------------- #
def _guard_output_path(src: str, out: str) -> None:
    """Never write into a tree the engine or the evidence base reads from."""
    o = Path(out).resolve()
    lowered = str(o).lower().replace("\\", "/")
    for bad in ("safe-copy-bea-pristine", "steamapps", "steamlibrary"):
        if bad in lowered:
            raise ProbeError(
                f"REFUSED: {out} lies under a protected tree ({bad}). Authored archives go to "
                "a scratch directory; the specimen and the installed game are never written."
            )
    if o == Path(src).resolve():
        raise ProbeError("REFUSED: output would overwrite the source archive")
    # A directory holding a shelf of retail archives is a game data directory,
    # whatever it is called. Dropping an authored archive in there is how an
    # unrelated measurement silently gets contaminated -- the autoexec.con
    # failure mode, in a different file.
    if len(list(o.parent.glob("*_res_PC.aya"))) >= 10:
        raise ProbeError(
            f"REFUSED: {o.parent} looks like a game Resources directory "
            "(10 or more *_res_PC.aya). Authored archives go somewhere the engine will "
            "not pick them up by accident."
        )


def diff_ranges(a: bytes, b: bytes) -> list[tuple[int, int]]:
    """Contiguous differing spans between two equal-length buffers."""
    if len(a) != len(b):
        raise ValueError("diff_ranges needs equal lengths")
    out: list[tuple[int, int]] = []
    i, n = 0, len(a)
    while i < n:
        if a[i] != b[i]:
            j = i
            while j < n and a[j] != b[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


def author(
    src_path: str | os.PathLike,
    out_path: str | os.PathLike,
    intents: list[dict],
    *,
    world_tag: str = "RLWD",
    allow_length_change: bool = False,
    lab=None,
    corpus: str | os.PathLike | None = None,
    profile_cache: str | os.PathLike | None = None,
    arm: str = "probe",
    label: str = "",
    notes: list[str] | None = None,
    force: bool = False,
) -> dict:
    """Author one archive. Returns the manifest dict; writes the .aya."""
    src_path = str(src_path)
    out_path = str(out_path)
    _guard_output_path(src_path, out_path)
    if Path(out_path).exists() and not force:
        raise ProbeError(f"REFUSED: {out_path} exists (pass force=True to overwrite)")

    arch = Archive(src_path, lab=lab)
    world = arch.world(world_tag)

    # ---- gate 1: the SOURCE must parse cleanly before we touch it -----------
    pre_sent = {t: w.sentinels_ok() for t, w in arch.worlds.items()}
    for t, (good, total) in pre_sent.items():
        if good != total:
            raise FramingError(f"source {t}: only {good}/{total} sentinels read 'end_script'")

    natives = load_natives(arch.lab_root)
    profile: dict = {}
    if any(i["op"] == "retarget-call" and not i.get("allow_unprofiled") for i in intents):
        profile = get_profile(corpus, profile_cache, lab=lab)

    # ---- resolve intents to anchored edits ---------------------------------
    edits: list[Edit] = []
    splice: Splice | None = None
    for spec in intents:
        op = spec.get("op")
        if op not in INTENTS:
            raise IntentError(f"unknown intent {op!r}; known: {', '.join(sorted(INTENTS))}")
        if op == "set-constant":
            e, s = intent_set_constant(world, spec)
        elif op == "retarget-call":
            e, s = intent_retarget_call(world, spec, natives, profile)
        elif op == "poison-opcode":
            e, s = intent_poison_opcode(world, spec)
        elif op == "poison-datatype":
            e, s = intent_poison_datatype(world, spec)
        elif op == "null-control":
            e, s = intent_null_control(world, spec)
        elif op == "set-script-trace":
            e, s = intent_set_script_trace(world, spec)
        elif op == "raw":
            e, s = intent_raw(world, spec)
        elif op == "splice-script":
            e, s = intent_splice_script(world, spec, lab=lab)
        else:
            e, s = intent_replace_script(world, spec, lab=lab)
        edits.extend(e)
        if s is not None:
            if splice is not None:
                raise ProbeError("at most one length-changing edit per authored archive")
            splice = s

    if splice is not None:
        if not allow_length_change:
            evidence_status = (
                "Controlled generated replacements have loaded and executed, but authoring "
                "cannot prove that this particular program will execute."
                if splice.kind == "replace-script"
                else "This length-changing path is only statically verified and has not executed."
            )
            raise LengthChangeRefused(
                f"{splice.kind} changes the payload length by {splice.delta:+d} bytes. "
                f"{evidence_status} "
                "Pass --allow-length-change if that is what you want."
            )
        if not arch.blocks_regular():
            raise ProbeError(
                "source container does not follow the 1 MiB-block rule, so re-blocking after "
                "a length change would not reproduce the shipped container shape. REFUSED."
            )
        edits.extend(size_fixups(arch.inflated, splice))

    if not edits and splice is None:
        notes = (notes or []) + ["identity build: no intents supplied"]

    # ---- apply (the refusal happens inside) --------------------------------
    patched = apply_edits(arch.inflated, edits, splice)
    expected_delta = splice.delta if splice else 0
    if len(patched) != len(arch.inflated) + expected_delta:
        raise ProbeError("internal: patched length does not match the expected delta")

    # ---- gate 2: the RESULT must break EXACTLY as intended, and no more -----
    #
    # A probe must still parse. A poison must not -- that is the whole point of
    # it. So the gate is not "the parse must succeed", it is "the parse must come
    # out the way this arm predicted". Inverting it for poisons keeps the gate
    # real: a poison-datatype that fails to desynchronise is refused too, because
    # an arm that should die and doesn't proves nothing.
    breaking = [i["op"] for i in intents if i["op"] in FRAMING_BREAKING]
    expect_desync = any(FRAMING_BREAKING[o] == "desync" for o in breaking)
    expect_sentinel_breaks = sum(1 for o in breaking if FRAMING_BREAKING[o] == "sentinel")

    post: dict[str, dict] = {}
    post_worlds: dict[str, World] = {}
    replacement_verification: dict[str, object] = {}
    parse_error: str | None = None
    try:
        list(chunk_chain(patched, 0, len(patched)))  # top-level chain must close exactly
        for tag in WORLD_TAGS:
            try:
                chain = find_chunk_path(patched, b"WRES", b"WRLD", tag)
            except FramingError:
                continue
            w2 = World(patched, chain, arch._sp)
            post_worlds[w2.tag] = w2
            good, total = w2.sentinels_ok()
            post[w2.tag] = {"scripts": total, "sentinels_ok": good,
                            "sentinels_broken": total - good}
    except FramingError as exc:
        parse_error = str(exc)

    if expect_desync:
        if parse_error is None:
            raise ProbeError(
                "poison-datatype did NOT desynchronise the grammar. An arm that should die "
                "and does not proves nothing. REFUSED."
            )
    elif parse_error is not None:
        raise FramingError(
            f"the edited payload no longer walks: {parse_error}\n"
            "  REFUSED -- nothing was written. A desynchronising edit reads back later as "
            "'the engine rejects our archives', which is the wrong conclusion."
        )
    else:
        broken = sum(v["sentinels_broken"] for v in post.values())
        if broken != expect_sentinel_breaks:
            raise FramingError(
                f"{broken} sentinel(s) no longer read 'end_script'; this arm intended "
                f"exactly {expect_sentinel_breaks}. REFUSED -- nothing was written."
            )
        expect_counts = {t: len(w.scripts) for t, w in arch.worlds.items()}
        if splice is not None and splice.kind == "splice-script":
            expect_counts[world_tag] += 1
        for t, want in expect_counts.items():
            if post.get(t, {}).get("scripts") != want:
                raise FramingError(
                    f"{t}: script count is {post.get(t, {}).get('scripts')}, expected {want}"
                )

        if splice is not None and splice.kind == "replace-script":
            w2 = post_worlds.get(world_tag)
            if w2 is None:
                raise FramingError(f"replacement result has no {world_tag} world")
            old_names = [s["name"] for s in world.scripts]
            new_names = [s["name"] for s in w2.scripts]
            if old_names != new_names:
                raise FramingError(
                    "replace-script changed script names or table order; "
                    f"before={old_names}, after={new_names}"
                )
            target_name = splice.meta["script"]
            target_ordinal = splice.meta["scriptOrdinal"]
            if new_names[target_ordinal] != target_name:
                raise FramingError(
                    f"replace-script target moved: ordinal {target_ordinal} is "
                    f"{new_names[target_ordinal]!r}, expected {target_name!r}"
                )
            unchanged = 0
            for ordinal, (before_script, after_script) in enumerate(zip(world.scripts, w2.scripts)):
                before_blob = world.payload[before_script["record_start"] : before_script["record_end"]]
                after_blob = w2.payload[after_script["record_start"] : after_script["record_end"]]
                if ordinal == target_ordinal:
                    if after_blob != splice.insert:
                        raise FramingError("replace-script target does not read back as the emitted record")
                elif before_blob != after_blob:
                    raise FramingError(
                        f"replace-script changed non-target record #{ordinal} {before_script['name']!r}"
                    )
                else:
                    unchanged += 1
            replacement_verification = {
                "replacementScriptOrderPreserved": True,
                "replacementTargetOrdinalPreserved": True,
                "replacementRecordReadbackExact": True,
                "replacementNonTargetRecordsIdentical": unchanged,
            }

    # ---- gate 3: no collateral damage --------------------------------------
    collateral: dict = {}
    if splice is None:
        ranges = diff_ranges(arch.inflated, patched)
        want = sorted((e.offset, e.end) for e in edits)
        collateral = {"diff_ranges": len(ranges), "edit_ranges": len(want),
                      "ranges_within_edits": all(
                          any(lo >= o and hi <= h for o, h in want) for lo, hi in ranges)}
        if not collateral["ranges_within_edits"]:
            raise ProbeError(f"collateral change outside the declared edits: {ranges}")
        collateral["changed_bytes"] = sum(hi - lo for lo, hi in ranges)
    else:
        head = splice.offset
        # Everything after the spliced region must be untouched, and everything
        # before it may differ only inside the declared same-length edits (the
        # chunk-size fixups live there).
        if arch.inflated[head + len(splice.expect_remove):] != patched[head + len(splice.insert):]:
            raise ProbeError("collateral change after the splice point")
        head_ranges = diff_ranges(arch.inflated[:head], patched[:head])
        want = sorted((e.offset, e.end) for e in edits if e.end <= head)
        if not all(any(lo >= o and hi <= h for o, h in want) for lo, hi in head_ranges):
            raise ProbeError(
                f"collateral change before the splice point: {head_ranges} vs {want}")
        collateral = {"splice_delta": splice.delta, "tail_identical": True,
                      "head_diff_ranges": len(head_ranges),
                      "head_ranges_within_edits": True}

    # ---- write, then re-inflate and prove the round trip -------------------
    block_sizes = arch.block_sizes if splice is None else reblock(len(patched))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    arch._aya.write_aya(out_path, patched, block_sizes)
    raw2, inf2, blocks2 = arch._aya.read_aya(out_path)
    if inf2 != patched:
        raise ProbeError("ROUND TRIP FAILED: re-inflated payload differs from what we patched")
    if [b[1] for b in blocks2] != block_sizes:
        raise ProbeError("ROUND TRIP FAILED: block structure differs")

    manifest = {
        "tool": "tools/probe/probe_author.py",
        "tool_version": TOOL_VERSION,
        "spec": SPEC,
        "specimen_sha256": SPECIMEN_SHA,
        "generated_utc": _now(),
        "arm": arm,
        "label": label or Path(out_path).stem,
        "source": {
            "path": arch.path,
            "sha256": arch.file_sha,
            "bytes": len(arch.raw),
            "inflated_sha256": arch.inflated_sha,
            "inflated_bytes": len(arch.inflated),
            "blocks": arch.block_sizes,
        },
        "output": {
            "path": str(Path(out_path).resolve()),
            "sha256": sha256(raw2),
            "bytes": len(raw2),
            "inflated_sha256": sha256(inf2),
            "inflated_bytes": len(inf2),
            "blocks": [b[1] for b in blocks2],
        },
        "world": {
            "tag": world.tag,
            "payload_offset": world.base,
            "payload_bytes": world.end - world.base,
            "script_count_before": world.script_count,
            "script_count_after": post.get(world.tag, {}).get("scripts"),
            "level_id": world.parsed["header"]["level_id"],
        },
        "intents": intents,
        "edits": [e.to_manifest(world.base) for e in sorted(edits, key=lambda x: x.offset)],
        "splice": splice.to_manifest(world.base) if splice else None,
        "verification": {
            "source_parsed": True,
            "source_sentinels": {t: f"{g}/{n}" for t, (g, n) in pre_sent.items()},
            "output_parsed": parse_error is None,
            "output_sentinels": {t: f"{v['sentinels_ok']}/{v['scripts']}" for t, v in post.items()},
            "chunk_chain_closes": parse_error is None,
            "intended_framing_break": (
                "desync" if expect_desync
                else (f"{expect_sentinel_breaks} sentinel(s)" if expect_sentinel_breaks else None)
            ),
            "framing_error": parse_error,
            "roundtrip_inflated_identical": True,
            "block_structure": "preserved" if splice is None else "reblocked",
            **replacement_verification,
            **collateral,
        },
        "unproven": _unproven(splice, intents),
        "notes": notes or [],
    }
    return manifest


def _unproven(splice, intents) -> list[str]:
    out: list[str] = []
    if splice is not None and splice.kind != "replace-script":
        out.append(
            "This archive changes the payload length. The container round-trip and the "
            "framing are verified statically here, but no length-changed archive has ever "
            "been loaded by the engine. Run it with a poison arm."
        )
        out.append(
            "Re-blocking preserves the shipped rule (every block inflates to 1 MiB except "
            "the last), but whether the loader depends on that rule is not established."
        )
    if any(i["op"] == "splice-script" for i in intents):
        out.append(
            "Whether world 'things' reference scripts by table index is not established; the "
            "splice appends at the end so no existing index moves, but a donor script's own "
            "assumptions about the level it now lives in are not checked."
        )
    if any(i["op"] == "replace-script" for i in intents):
        out.append(
            "This generated record is bytecode-authored by this project. The authoring step "
            "checks its grammar, native signatures, table ordinal, and non-target records, "
            "but cannot establish that this particular program executed. Require matched "
            "controls and a runtime receipt before claiming it ran."
        )
    if any(i["op"] == "set-script-trace" for i in intents):
        out.append(
            "The authored trailer value and archive framing are proven here, but trace "
            "output also requires the target script to execute and a separately enabled, "
            "writable logger. Require logger liveness plus value-0/value-2 controls before "
            "claiming a trace."
        )
    if any(i["op"] == "retarget-call" for i in intents):
        out.append(
            "retarget-call is checked against corpus-observed arity and return discipline. "
            "The native's runtime preconditions (does it need a target thing? a loaded "
            "resource?) are not modelled -- that is what the run is for."
        )
    return out


def write_manifest(manifest: dict, path: str | os.PathLike) -> str:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    return str(Path(path).resolve())


PREDICTIONS = {
    "poison-opcode": "DIES: 0xC0000005 during level load (SpawnFromOpcode returns NULL into "
                     "an unchecked array). Measured twice at ~13 s in the container experiment.",
    "poison-datatype": "DIES or misbehaves: 'FATAL ERROR: unknown data type', then every field "
                       "after the poisoned symbol is read at the wrong offset.",
    "null-control": "NO OBSERVABLE DIFFERENCE from the probe arm. The engine reads the sentinel "
                    "into a stack local it never examines. If this arm behaves differently, our "
                    "model of the format is wrong.",
}


def _prediction(intents: list[dict]) -> str:
    for i in intents:
        if i["op"] == "set-script-trace":
            value = i.get("value", 1)
            if value == 1:
                return (
                    "RUNS AND TRACES if this script executes and the separately enabled file "
                    "logger is writable; expect one post-instruction line per executed "
                    "non-RETURN instruction."
                )
            return (
                f"RUNS WITHOUT VM TRACE LINES: trailerA={value} is an exact-comparison "
                "control; retail enables tracing only for value 1."
            )
        if i["op"] in PREDICTIONS:
            return PREDICTIONS[i["op"]]
    return "RUNS: the probe's edits take effect; the engine loads the level normally."


def author_arms(
    src_path, out_dir, intents, *, control_arms: dict | None = None, name="probe", **kw
) -> dict:
    """Author the probe and each of its control arms.

    Every control arm is authored FROM THE PROBE ARCHIVE, not from the retail
    source. That makes "this arm differs from the probe only by its control edit"
    true by construction rather than by an after-the-fact comparison -- which is
    what lets "the poison arm died and the probe arm did not" mean "the engine
    consumed the bytes we changed here", instead of "something else was different
    between the two runs".

    Each control gets its OWN archive. A poison predicts death and a null control
    predicts no change; putting both in one file would make the outcome
    uninterpretable.
    """
    out_dir = Path(out_dir)
    probe_out = out_dir / f"{name}.aya"
    m_probe = author(src_path, probe_out, intents, arm="probe", label=name, **kw)
    m_probe["prediction"] = _prediction(intents)
    m_probe["manifest_path"] = write_manifest(m_probe, out_dir / f"{name}.manifest.json")
    result = {"probe": m_probe}

    _, aya, _, _ = bea_lab.load(kw.get("lab"))
    _, inf_p, _ = aya.read_aya(str(probe_out))

    for suffix, arm_intents in (control_arms or {}).items():
        arm_out = out_dir / f"{name}.{suffix}.aya"
        m = author(probe_out, arm_out, list(arm_intents),
                   arm=suffix, label=f"{name}.{suffix}", **kw)
        m["prediction"] = _prediction(arm_intents)
        m["derived_from"] = {
            "probe_manifest": m_probe["manifest_path"],
            "probe_archive": m_probe["output"]["path"],
            "probe_sha256": m_probe["output"]["sha256"],
            "retail_source": m_probe["source"]["path"],
            "retail_source_sha256": m_probe["source"]["sha256"],
        }
        # belt and braces: the property is structural, but check it anyway
        _, inf_x, _ = aya.read_aya(str(arm_out))
        same_len = len(inf_p) == len(inf_x)
        got = diff_ranges(inf_p, inf_x) if same_len else []
        want = sorted((e["offset"], e["offset"] + e["length"]) for e in m["edits"])
        # Containment, not equality: an anchored 4-byte edit that flips one byte
        # produces a 1-byte diff, and that is correct. What must hold is that
        # NOTHING changed outside the declared control edits.
        ok = same_len and bool(got) and all(
            any(lo >= o and hi <= h for o, h in want) for lo, hi in got)
        m["verification"]["differs_from_probe_only_by_this_arm"] = ok
        m["verification"]["probe_vs_arm_diff_ranges"] = [list(r) for r in got]
        m["verification"]["arm_edit_ranges"] = [list(r) for r in want]
        m["verification"]["probe_vs_arm_changed_bytes"] = sum(hi - lo for lo, hi in got)
        if not ok:
            raise ProbeError(
                f"arm {suffix!r} does not differ from the probe in exactly the intended way: "
                f"diff {got}, declared edits {want}, same length {same_len}"
            )
        m["manifest_path"] = write_manifest(m, out_dir / f"{name}.{suffix}.manifest.json")
        result[suffix] = m
    return result


def verify_manifest(manifest_path: str | os.PathLike, lab=None) -> dict:
    """Re-check an authored archive against its manifest, from scratch.

    Confirms the source is still the archive the edits were computed against
    (every expect_hex still present at its offset), and that the output on disk
    is still the file the manifest describes.
    """
    m = json.load(open(manifest_path, encoding="utf-8"))
    _root, aya, _sp, _ba = bea_lab.load(lab)
    report = {"manifest": str(Path(manifest_path).resolve()), "checks": {}}

    src_raw, src_inf, _ = aya.read_aya(m["source"]["path"])
    report["checks"]["source_sha256"] = sha256(src_raw) == m["source"]["sha256"]
    report["checks"]["source_inflated_sha256"] = sha256(src_inf) == m["source"]["inflated_sha256"]

    bad = []
    for e in m["edits"]:
        exp = bytes.fromhex(e["expect_hex"].replace(" ", ""))
        if src_inf[e["offset"] : e["offset"] + len(exp)] != exp:
            bad.append(e["offset"])
    splice = m.get("splice")
    if splice:
        off = splice["offset"]
        removed = splice["removed"]
        if removed:
            expected = bytes.fromhex(splice["expect_remove_hex"].replace(" ", ""))
            splice_anchor_ok = len(expected) == removed and src_inf[off : off + removed] == expected
        else:
            expected = bytes.fromhex(splice["expect_anchor_hex"].replace(" ", ""))
            splice_anchor_ok = bool(expected) and src_inf[off : off + len(expected)] == expected
        report["checks"]["splice_anchor_still_present_in_source"] = splice_anchor_ok
        if not splice_anchor_ok:
            bad.append(off)
    report["checks"]["all_anchors_still_present_in_source"] = not bad
    report["anchor_failures"] = bad

    try:
        out_raw, out_inf, out_blocks = aya.read_aya(m["output"]["path"])
    except Exception as exc:  # noqa: BLE001 - zlib raises its own types
        # A tampered container fails to inflate. That is a verification failure,
        # not a crash: report it and stop.
        report["checks"]["output_readable"] = False
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["ok"] = False
        return report
    report["checks"]["output_readable"] = True
    report["checks"]["output_sha256"] = sha256(out_raw) == m["output"]["sha256"]
    report["checks"]["output_inflated_sha256"] = sha256(out_inf) == m["output"]["inflated_sha256"]
    report["checks"]["output_blocks"] = [b[1] for b in out_blocks] == m["output"]["blocks"]
    if splice:
        off = splice["offset"]
        inserted = splice["inserted"]
        report["checks"]["splice_insert_present_in_output"] = (
            sha256(out_inf[off : off + inserted]) == splice["insert_sha256"]
        )

    for e in m["edits"]:
        new = bytes.fromhex(e["new_hex"].replace(" ", ""))
        off = e["offset"]
        if splice and off > splice["offset"]:
            off += splice["delta"]
        if out_inf[off : off + len(new)] != new:
            report["checks"].setdefault("all_new_bytes_present_in_output", True)
            report["checks"]["all_new_bytes_present_in_output"] = False
    report["checks"].setdefault("all_new_bytes_present_in_output", True)

    report["ok"] = all(report["checks"].values())
    return report


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
OPNAMES = {
    0x00: "NOP", 0x01: "PLUS", 0x02: "MINUS", 0x03: "MUL", 0x04: "DIV",
    0x05: "PUSH", 0x06: "POP", 0x07: "OR", 0x08: "AND", 0x09: "GT",
    0x0A: "LT", 0x0B: "GE", 0x0C: "LE", 0x0D: "LABEL", 0x0E: "REMOVE_TOP",
    0x0F: "CMP", 0x10: "CMPB", 0x11: "CMPNEB", 0x12: "JMPNE", 0x13: "JMPFALSE",
    0x14: "JMP", 0x15: "GETTOP", 0x16: "POINTER", 0x17: "RETURN", 0x18: "CALL",
    0x19: "CALLLOCAL", 0x1A: "PUSHPC",
}
EVENT_SLOTS = {0: "init", 3: "died", 4: "hit", 5: "started_dying", 6: "ready", 7: "shutdown"}


def _parse_kv_constant(s: str) -> dict:
    """`Script:symbol=value` -> a set-constant intent."""
    try:
        lhs, val = s.split("=", 1)
        script, sym = lhs.split(":", 1)
    except ValueError:
        raise IntentError(f"--set-constant wants Script:symbol=value, got {s!r}") from None
    v: object = val
    try:
        v = int(val)
    except ValueError:
        try:
            v = float(val)
        except ValueError:
            pass
    return {"op": "set-constant", "script": script, "symbol": sym, "value": v}


def _parse_kv_call(s: str) -> dict:
    """`Script:instruction=Native` -> a retarget-call intent."""
    try:
        lhs, native = s.split("=", 1)
        script, ins = lhs.split(":", 1)
    except ValueError:
        raise IntentError(f"--retarget-call wants Script:instr=Native, got {s!r}") from None
    return {"op": "retarget-call", "script": script, "instruction": int(ins), "native": native}


def cmd_list(a) -> int:
    arch = Archive(a.archive, lab=a.lab)
    print(f"{arch.path}\n  file sha256 {arch.file_sha}\n  inflated    {len(arch.inflated)} B "
          f"sha256 {arch.inflated_sha}\n  blocks      {arch.block_sizes}")
    for tag, w in arch.worlds.items():
        good, total = w.sentinels_ok()
        print(f"\n  {tag}: payload at {w.base} ({w.end - w.base} B), level "
              f"{w.parsed['header']['level_id']}, {w.script_count} scripts, "
              f"sentinels {good}/{total}")
        for s in w.scripts:
            calls = sum(1 for op, _ in s["instructions"] if op == OP_CALL)
            print(f"    {s['name']:<28} {s['instr_count']:>4} instr  "
                  f"{len(s['symtab']['symbols']):>3} sym  {calls:>3} calls  "
                  f"record +{s['record_start']}..{s['record_end']}")
    return 0


def cmd_show(a) -> int:
    arch = Archive(a.archive, lab=a.lab)
    w = arch.world(a.world)
    s = w.script(a.script)
    nat = load_natives(arch.lab_root)
    syms = s["symtab"]["symbols"]
    print(f"{w.tag} at inflated {w.base}; record +{s['record_start']}..{s['record_end']} "
          f"({s['record_end'] - s['record_start']} B)")
    print(f"script {s['name']!r}: {s['instr_count']} instructions, {len(syms)} symbols, "
          f"{s['event_count']} named-event handlers, trailer {s['trailer']} "
          f"at inflated {w.abs(s['end'] - 8)}")
    entries = {v: f"slot {i} ({EVENT_SLOTS.get(i, '?')})"
               for i, v in enumerate(s["event_table"]) if v != -1}
    for ev in s["events"]:
        for q in ev["params"]:
            entries.setdefault(ev["entry"], f"event {syms[q]['value']!r}")
    print(f"\ninstructions (inflated {w.abs(s['instr_off'])}, 8 B each):")
    for i, (op, arg) in enumerate(s["instructions"]):
        mark = f"   <== {entries[i]}" if i in entries else ""
        if op == OP_CALL:
            idx, argc, hi = decode_call(arg)
            note = f"{nat.get(idx, '?')}/{argc}" + (" ->value" if hi else " ->void")
        elif op == 0x05 and 0 <= arg < len(syms):
            note = f"{syms[arg]['name']}={syms[arg]['value']!r}"
        elif op in (0x13, 0x14):
            note = f"-> instr {arg}"
        else:
            note = "" if arg == -1 else str(arg)
        print(f"  {i:4}  {op:#04x} {OPNAMES.get(op, '?'):9} {arg:>11}  "
              f"@{w.abs(s['instr_off'] + i * 8)}  {note}{mark}")
    print(f"\nsymbols (tail={s['symtab']['tail']}):")
    for x in syms:
        editable = "editable" if x["type"] in WRITABLE_TAGS else "NOT WRITABLE"
        vo = w.abs(x["value_off"]) + (4 if x["type"] == 3 else 0)
        print(f"  #{x['index']:3} line {x['f0c']:4} tag {x['type']} ({editable:12}) "
              f"{x['name']:<24} = {x['value']!r}   value @{vo} ({x['value_len']} B)")
    return 0


def cmd_natives(a) -> int:
    root = bea_lab.find_lab(a.lab)
    nat = load_natives(root)
    if not a.profile:
        for i in sorted(nat):
            print(f"  {i:>4}  {nat[i]}")
        print(f"\n{len(nat)} named slots of 144")
        return 0
    prof = get_profile(a.corpus, a.profile_cache, lab=a.lab)
    print(f"corpus {prof['corpus']}: {prof['archives']} archives, "
          f"{prof['world_chunks']} world chunks, {prof['natives_called']} natives called")
    print(f"{'native':<28} {'idx':>4}  {'calls':>6}  profiles (argc/returns)")
    for name in sorted(prof["by_name"]):
        e = prof["by_name"][name]
        p = ", ".join(f"{k} x{v}" for k, v in sorted(e["profiles"].items()))
        print(f"{name:<28} {e['index']:>4}  {e['calls']:>6}  {p}")
    never = sorted(set(nat.values()) - set(prof["by_name"]))
    print(f"\nnever called by shipped scripts ({len(never)}) -- retarget refused without "
          f"allow_unprofiled:\n  {', '.join(never)}")
    return 0


def cmd_author(a) -> int:
    intents: list[dict] = []
    if a.recipe:
        r = json.load(open(a.recipe, encoding="utf-8"))
        intents += r.get("intents", [])
        if not a.world and r.get("world"):
            a.world = r["world"]
    for j in a.intent or []:
        intents.append(json.loads(j))
    for s in a.set_constant or []:
        intents.append(_parse_kv_constant(s))
    for s in a.retarget_call or []:
        intents.append(_parse_kv_call(s))

    controls: dict[str, list[dict]] = {}
    for p in a.poison or []:
        suffix, spec = _build_poison(p, intents)
        n, key = 1, suffix
        while key in controls:
            n += 1
            key = f"{suffix}{n}"
        controls[key] = [spec]

    out_dir = Path(a.out_dir)
    res = author_arms(
        a.archive, out_dir, intents,
        control_arms=controls or None, name=a.name,
        world_tag=a.world or "RLWD",
        allow_length_change=a.allow_length_change,
        lab=a.lab, corpus=a.corpus, profile_cache=a.profile_cache,
        notes=a.note or [], force=a.force,
    )
    for arm, m in res.items():
        v = m["verification"]
        print(f"\n=== {arm}: {m['output']['path']}")
        print(f"  sha256 {m['output']['sha256']}  {m['output']['bytes']} B  "
              f"inflated {m['output']['inflated_bytes']} B")
        for e in m["edits"]:
            print(f"  [{e['kind']}] @{e['offset']}  {e['expect_hex']} -> {e['new_hex']}")
            print(f"      {e['description']}")
        if m.get("splice"):
            s = m["splice"]
            print(f"  [{s['kind']}] @{s['offset']}  {s['delta']:+d} bytes")
            print(f"      {s['description']}")
        print(f"  verification: parsed={v['output_parsed']} sentinels={v['output_sentinels']} "
              f"roundtrip={v['roundtrip_inflated_identical']} "
              f"changed={v.get('changed_bytes', v.get('splice_delta'))}")
        if arm != "probe":
            print(f"  differs from probe only by this arm: "
                  f"{v['differs_from_probe_only_by_this_arm']} "
                  f"({v['probe_vs_arm_changed_bytes']} byte(s))")
        print(f"  PREDICTION: {m['prediction']}")
        print(f"  manifest {m['manifest_path']}")
        for u in m["unproven"]:
            print(f"  UNPROVEN: {u}")
    return 0


def _build_poison(spec: str, intents: list[dict]) -> tuple[str, dict]:
    """`kind` or `kind:Script:target` -- defaults aim at whatever the probe edited.

    Returns (arm_suffix, intent). Each control becomes its own archive.
    """
    parts = spec.split(":")
    kind = parts[0]
    target_script = parts[1] if len(parts) > 1 else None
    target = parts[2] if len(parts) > 2 else None
    if target_script is None:
        for i in reversed(intents):
            if i.get("script"):
                target_script = i["script"]
                break
    if target_script is None:
        raise IntentError("--poison needs a script (kind:Script[:target]) when no intent names one")
    if kind == "opcode":
        if target is None:
            for i in reversed(intents):
                if i["op"] == "retarget-call" and i["script"] == target_script:
                    target = str(i["instruction"])
                    break
        if target is None:
            raise IntentError(
                "--poison opcode needs an instruction index (opcode:Script:N) unless the probe "
                "retargeted a call in that script"
            )
        return "poison-opcode", {"op": "poison-opcode", "script": target_script,
                                 "instruction": int(target)}
    if kind == "datatype":
        if target is None:
            for i in reversed(intents):
                if i["op"] == "set-constant" and i["script"] == target_script:
                    target = str(i["symbol"])
                    break
        if target is None:
            raise IntentError("--poison datatype needs a symbol (datatype:Script:sym)")
        return "poison-datatype", {"op": "poison-datatype", "script": target_script,
                                   "symbol": target}
    if kind == "null":
        return "null-control", {"op": "null-control", "script": target_script}
    raise IntentError(f"unknown poison kind {kind!r}; use opcode, datatype or null")


def cmd_verify(a) -> int:
    r = verify_manifest(a.manifest, lab=a.lab)
    for k, v in r["checks"].items():
        print(f"  {'ok ' if v else 'FAIL'}  {k}")
    if r.get("anchor_failures"):
        print(f"  anchor failures at {r['anchor_failures']}")
    if r.get("error"):
        print(f"  {r['error']}")
    print(f"\n{'VERIFIED' if r['ok'] else 'FAILED'}")
    return 0 if r["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="probe_author.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lab", help="local-lab root (default: $BEA_LOCAL_LAB or <repo>/local-lab)")
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("list", help="list the scripts in an archive")
    q.add_argument("archive")
    q.set_defaults(fn=cmd_list)

    q = sub.add_parser("show", help="disassemble one script, with writable offsets")
    q.add_argument("archive")
    q.add_argument("script")
    q.add_argument("--world", default="RLWD")
    q.set_defaults(fn=cmd_show)

    q = sub.add_parser("natives", help="the 144-slot descriptor table, optionally profiled")
    q.add_argument("--profile", action="store_true", help="scan a corpus for arity/return")
    q.add_argument("--corpus", help="directory of *_res_PC.aya")
    q.add_argument("--profile-cache")
    q.set_defaults(fn=cmd_natives)

    q = sub.add_parser("author", help="author a probe (and its poison twin)")
    q.add_argument("archive")
    q.add_argument("--out-dir", required=True)
    q.add_argument("--name", default="probe")
    q.add_argument("--world", default=None)
    q.add_argument("--recipe", help="JSON file: {world, intents:[...]}")
    q.add_argument("--intent", action="append", help="a JSON intent object")
    q.add_argument("--set-constant", action="append", metavar="Script:symbol=value")
    q.add_argument("--retarget-call", action="append", metavar="Script:instr=Native")
    q.add_argument("--poison", action="append", metavar="opcode|datatype|null[:Script[:target]]")
    q.add_argument("--allow-length-change", action="store_true")
    q.add_argument("--corpus", help="directory of *_res_PC.aya for the call profile")
    q.add_argument("--profile-cache")
    q.add_argument("--note", action="append")
    q.add_argument("--force", action="store_true", help="overwrite an existing output")
    q.set_defaults(fn=cmd_author)

    q = sub.add_parser("verify", help="re-check an authored archive against its manifest")
    q.add_argument("manifest")
    q.set_defaults(fn=cmd_verify)
    return p


def main(argv=None) -> int:
    a = build_parser().parse_args(argv)
    try:
        return a.fn(a)
    except ProbeError as exc:
        print(f"\n{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    except bea_lab.LabNotFound as exc:
        print(f"\nLabNotFound: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
