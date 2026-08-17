#!/usr/bin/env python3
"""Path-correct incoming-stack-argument-slot measure, from pristine bytes only.

Why this exists
---------------
The ABI cleanup axis had exactly one witness: the RET immediate. A sweep of all
1,001 FLAGGED(ABI) rows found 498 addresses whose bytes imply a database
correction, but only 82 carried a second, independent witness, so 416 rested on
the RET immediate ALONE. That is the single-assertion weakness that blocks any
cohort promotion, and adjudicating 416 rows by hand is the expensive way out.

This file is the cheap way out: a second witness derived from the *body*, never
from the terminator. Two mechanisms, deliberately independent of each other:

  A. Per-basic-block ESP/EBP abstract interpretation. Build the CFG confined to
     the declared body ranges, propagate the stack pointer as an interval of
     offsets relative to the ENTRY ESP, and resolve every ESP/EBP-relative
     memory operand to a frame-invariant slot index. `[entry_esp + 0]` is the
     return address, `+4` is argument slot 0, `+8` slot 1, and so on.

  B. Caller-side measurement. Every direct `call` in the image is collected from
     a boundary-validated decode of every declared body, and each call site is
     asked how many bytes of stack arguments it supplied — exactly, when the
     caller cleans up with `add esp, N`; by push-run count otherwise.

The two disagree in an informative direction. A is a LOWER bound (see below), so
it can only corroborate corrections that raise the argument extent. B measures
what the caller actually supplied, so it is the only one of the two that can
corroborate a correction that LOWERS it.

Why "path-correct" is in the name
---------------------------------
A path-oblivious version of mechanism A already existed: it swept each body
linearly, carrying one running ESP counter in address order. On
`CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40` it
reported argument slot 2513 in one earlier form and slot 71 in another. Both are
garbage, for two separate reasons this file fixes:

  * a linear sweep walks fall-through and branch targets in address order, so a
    block reached only from a deeper stack is read at the shallower delta;
  * `[EBP + disp]` was assumed to mean `disp >= 8 => slot (disp-8)/4`, which is
    true only for the `push ebp; mov ebp, esp` prologue.

`005a3a40` does `sub esp, 0x10c` FIRST and only then `mov ebp, esp`, so EBP is
`entry - 0x10c` and `[ebp + 0x124]` is entry-relative `+0x18`, argument slot 5 —
six dwords, 24 bytes, which is exactly its `RET 24`. Tracking EBP symbolically
rather than assuming its offset turns that "over-read" into an agreement.

That matters for the record: the 11 flagged EBP over-reads were characterised as
`CFastVB__DispatchOp_*` kernels "using EBP as a DATA POINTER rather than a frame
pointer". Measured here, they are frame pointers — established at a non-standard
displacement because MSVC aligned the stack with `and esp, -16` after taking the
frame. The instrument still detects real non-frame EBP (any EBP definition not
derived from ESP drops EBP to UNKNOWN and its memory reads stop counting), which
is what would have been needed had the original diagnosis been right.

What this measures, precisely
-----------------------------
`arg_bytes_min` = `(max_slot_touched + 1) * 4`, where `max_slot_touched` is the
highest incoming argument slot any reachable instruction reads or writes at an
EXACT stack delta. Reads and writes both count: an offset at or above
`entry_esp + 4` is the caller's argument area either way, because outgoing
argument space always lies below the entry ESP.

What this CANNOT measure — stated, not buried
---------------------------------------------
1. It is a LOWER bound on the declared argument extent, never an upper bound.
   A function is free to ignore a parameter, and an argument address that
   escapes into a register (`lea eax, [esp+8]` then `mov ecx, [eax+4]`) is
   followed no further. So `arg_bytes_min > paramSize` refutes paramSize;
   `arg_bytes_min < paramSize` refutes nothing. `exactness` reports whether the
   enumeration was complete enough for the distinction to even be arguable.
2. It cannot determine a calling CONVENTION. Where a register argument exists it
   is not on the stack and this instrument never sees it. A convention that
   cannot be read out of the bytes stays UNDETERMINED; correcting arity is not
   licence to resolve `cc=unknown` to `__cdecl`.
3. It cannot see through an indexed stack access (`[esp + eax*4 + 0x10]`). Those
   are counted and reported, not resolved. They cannot invalidate the lower
   bound — an unresolved access can only hide a HIGHER slot — but they do stop
   `exactness` from reaching COMPLETE.
4. A body that tail-dispatches through JMP performs no local cleanup, so there
   is no cleanup axis to corroborate. Those report
   `local_cleanup=NONE_TAIL_DISPATCH` and their slot measure stands alone.
5. Mechanism B sees direct `E8` calls and `call [imm32]` through the IAT. A
   virtual call through `call [reg+disp]` is not attributable to a target from
   static bytes, so a function reached only virtually has no B witness. This is
   also why `index.tsv`'s inbound-reference count is useless for this: it counts
   vtable slots, which are not call sites.

Internal validity oracle
------------------------
At every `ret`, the stack delta must be exactly 0 — ESP points at the return
address. That constraint never mentions the RET immediate (`ret` and `ret N` are
identical at the instruction), so it is a free, independent check that the
lattice is right. `ret_delta_ok` reports it. On non-code it is the property that
fails, which is what makes the negative controls bite.

Usage
-----
  python tools/re_stack_arg_slot_measure.py \
      --specimen local-lab/.../BEA.exe \
      --bodies <byte_truth.json | bodies.tsv> \
      --addresses <one VA per line, optional; default all bodies> \
      --tsv-out slots.tsv --json-out slots.json

Does not write the specimen, does not touch Ghidra, does not invent names.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
    from capstone.x86 import (
        X86_OP_IMM,
        X86_OP_MEM,
        X86_OP_REG,
        X86_REG_EAX,
        X86_REG_EBP,
        X86_REG_ESP,
    )
except ImportError:  # pragma: no cover - capstone is a hard requirement
    Cs = None  # type: ignore

# Slot arithmetic. At the entry instruction ESP points at the return address, so
# entry-relative +0 is the return address and +4 is the first stack argument.
RETADDR_OFFSET = 0
FIRST_ARG_OFFSET = 4
DWORD = 4

RET_MNEMONICS = ("ret", "retf", "iret", "iretd", "retn")
COND_JUMPS = frozenset(
    """jo jno js jns je jz jne jnz jb jnae jc jnb jae jnc jbe jna ja jnbe
       jl jnge jge jnl jle jng jg jnle jp jpe jnp jpo jcxz jecxz
       loop loope loopne""".split()
)

# Guard rails. A body larger than this, or a CFG that needs more visits than
# this, is reported rather than silently truncated.
MAX_BODY_BYTES = 1 << 20
MAX_VISITS = 200_000


# --------------------------------------------------------------------------- PE


class Specimen:
    """Byte reader over a PE, mapping VA -> file offset from the real headers.

    The flat `offset = VA - 0x400000` rule that the campaign notes quote holds
    for `.text`/`.rdata`/`.data` in this specimen and NOT for `.rsrc`. This
    class parses the section table instead of trusting it, and
    `flat_mapping_holds_for` re-derives the claim so a caller can assert it.
    """

    def __init__(self, data: bytes):
        self.data = data
        e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
        self.image_base = struct.unpack_from("<I", data, e_lfanew + 24 + 28)[0]
        n_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
        size_opt = struct.unpack_from("<H", data, e_lfanew + 20)[0]
        table = e_lfanew + 24 + size_opt
        self.sections = []
        for i in range(n_sections):
            o = table + i * 40
            name = data[o : o + 8].rstrip(b"\0").decode("ascii", "replace")
            vsize, rva, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
            self.sections.append((name, rva, vsize, rawptr, rawsize))

    @classmethod
    def load(cls, path: Path, require_pristine: bool = True) -> "Specimen":
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        if require_pristine and sha != PRISTINE_SHA256:
            raise SystemExit(f"specimen sha256 mismatch: {sha}")
        spec = cls(data)
        spec.sha256 = sha
        return spec

    def offset(self, va: int) -> int | None:
        rva = va - self.image_base
        for _name, srva, vsize, rawptr, rawsize in self.sections:
            if srva <= rva < srva + max(vsize, rawsize):
                delta = rva - srva
                if delta >= rawsize:
                    return None  # BSS: virtual only, no bytes on disk
                return rawptr + delta
        return None

    def read(self, va: int, n: int) -> bytes | None:
        off = self.offset(va)
        if off is None:
            return None
        chunk = self.data[off : off + n]
        return chunk if chunk else None

    def section_of(self, va: int) -> str | None:
        rva = va - self.image_base
        for name, srva, vsize, rawptr, rawsize in self.sections:
            if srva <= rva < srva + max(vsize, rawsize):
                return name
        return None

    def flat_mapping_holds_for(self, section: str) -> bool:
        for name, srva, _vsize, rawptr, _rawsize in self.sections:
            if name == section:
                return rawptr == srva
        return False

    def executable_ranges(self) -> list[tuple[int, int]]:
        out = []
        for name, srva, vsize, rawptr, rawsize in self.sections:
            if name.startswith(".text"):
                lo = self.image_base + srva
                out.append((lo, lo + min(vsize, rawsize)))
        return out


# -------------------------------------------------------------- stack lattice


class Stk:
    """An interval of offsets relative to the entry ESP, or UNKNOWN.

    Exact when `lo == hi`. `and esp, -16` makes ESP inexact but still BOUNDED
    ABOVE, which is enough to prove the accesses that follow are locals rather
    than arguments, and that distinction is the whole reason this is an interval
    and not a scalar.
    """

    __slots__ = ("lo", "hi")

    # An interval wider than this is treated as unknown, so a loop that keeps
    # pushing cannot widen forever and stall the fixed point.
    MAX_WIDTH = 1 << 16

    def __init__(self, lo: int | None, hi: int | None):
        self.lo = lo
        self.hi = hi

    @staticmethod
    def exact(v: int) -> "Stk":
        return Stk(v, v)

    @staticmethod
    def unknown() -> "Stk":
        return Stk(None, None)

    @property
    def is_unknown(self) -> bool:
        return self.lo is None and self.hi is None

    @property
    def is_exact(self) -> bool:
        return self.lo is not None and self.lo == self.hi

    def shift(self, d: int) -> "Stk":
        if self.is_unknown:
            return Stk.unknown()
        lo = None if self.lo is None else self.lo + d
        hi = None if self.hi is None else self.hi + d
        return Stk(lo, hi)

    def align_down(self, align: int) -> "Stk":
        if self.is_unknown:
            return Stk.unknown()
        hi = self.hi
        lo = None if self.lo is None else self.lo - (align - 1)
        return Stk(lo, hi)

    def key(self):
        return (self.lo, self.hi)

    def __eq__(self, other):
        return isinstance(other, Stk) and self.key() == other.key()

    def __repr__(self):  # pragma: no cover - diagnostics only
        if self.is_unknown:
            return "UNKNOWN"
        if self.is_exact:
            return f"{self.lo:+d}"
        return f"[{self.lo:+d},{self.hi:+d}]"


class State:
    """Abstract state at a program point: ESP, EBP, and why EBP is what it is.

    `eax_imm` exists for one reason: MSVC allocates a frame larger than a page
    through `mov eax, <bytes>; call _alloca_probe`, and the probe moves ESP
    itself. Without EAX the caller's whole frame is off by that constant, and
    every ESP-relative access in it resolves to a fictional slot.
    """

    __slots__ = ("esp", "ebp", "ebp_kind", "eax_imm")

    def __init__(self, esp: Stk, ebp: Stk, ebp_kind: str, eax_imm: int | None = None):
        self.esp = esp
        self.ebp = ebp
        self.ebp_kind = ebp_kind
        self.eax_imm = eax_imm

    @staticmethod
    def entry() -> "State":
        # At the entry instruction ESP is the reference point; EBP still holds
        # the CALLER's frame pointer, which is not addressable in our frame.
        return State(Stk.exact(0), Stk.unknown(), "CALLER", None)

    def copy(self) -> "State":
        return State(
            Stk(self.esp.lo, self.esp.hi),
            Stk(self.ebp.lo, self.ebp.hi),
            self.ebp_kind,
            self.eax_imm,
        )

    def key(self):
        return (self.esp.key(), self.ebp.key(), self.ebp_kind, self.eax_imm)


def _meet_stk(a: Stk, b: Stk) -> tuple[Stk, bool]:
    """Lattice meet. Returns (joined, exact_conflict).

    UNKNOWN is the top element, so meeting a known delta with an unknown one
    degrades to unknown - that is imprecision, not a defect. Two DIFFERENT
    EXACT deltas at the same instruction is a defect: real code cannot reach one
    point with two stack depths, so it means the CFG or the callee-cleanup model
    is wrong here. That case is reported, never averaged.
    """
    if a == b:
        return a, False
    if a.is_unknown or b.is_unknown:
        return Stk.unknown(), False
    if a.is_exact and b.is_exact:
        return Stk.unknown(), True
    lo, hi = min(a.lo, b.lo), max(a.hi, b.hi)
    if hi - lo > Stk.MAX_WIDTH:
        return Stk.unknown(), False
    return Stk(lo, hi), False


def meet_state(a: State, b: State) -> tuple[State, bool, bool]:
    """(joined, changed, exact_conflict)"""
    esp, esp_conflict = _meet_stk(a.esp, b.esp)
    ebp, ebp_conflict = _meet_stk(a.ebp, b.ebp)
    kind = a.ebp_kind if a.ebp_kind == b.ebp_kind else "MERGED"
    eax = a.eax_imm if a.eax_imm == b.eax_imm else None
    joined = State(esp, ebp, kind, eax)
    return joined, joined.key() != a.key(), esp_conflict or ebp_conflict


def _mem_offset_range(state: State, mem) -> tuple[int | None, int | None, str]:
    """Entry-relative offset range of a memory operand, plus a base tag."""
    base = mem.base
    if base == X86_REG_ESP:
        anchor, tag = state.esp, "ESP"
    elif base == X86_REG_EBP:
        anchor, tag = state.ebp, "EBP"
    else:
        return None, None, "NONSTACK"
    if mem.index != 0:
        return None, None, tag + "_INDEXED"
    if anchor.is_unknown:
        return None, None, tag + "_UNKNOWN"
    shifted = anchor.shift(mem.disp)
    return shifted.lo, shifted.hi, tag


def _and_alignment(imm: int) -> int | None:
    """`and esp, 0xfffffff0` -> 16.  Anything else -> None (unmodelled)."""
    mask = imm & 0xFFFFFFFF
    low = (~mask) & 0xFFFFFFFF
    align = low + 1
    if align & (align - 1):
        return None  # not a power of two: not an alignment mask
    if align <= 1 or align > 4096:
        return None
    return align


# ------------------------------------------------------------------- decoding


def _decoder() -> "Cs":
    if Cs is None:  # pragma: no cover
        raise SystemExit("capstone is required")
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    return md


def decode_body(spec: Specimen, ranges: list[tuple[int, int]], md=None) -> dict:
    """Linear decode of every declared range. `ranges` are [lo, hi) VAs.

    Linear, not recursive, so that every byte of the declared body is accounted
    for; reachability is decided afterwards by the CFG walk.
    """
    md = md or _decoder()
    insns = {}
    for lo, hi in ranges:
        if hi <= lo or hi - lo > MAX_BODY_BYTES:
            continue
        code = spec.read(lo, hi - lo)
        if code is None:
            continue
        for ins in md.disasm(code, lo):
            insns[ins.address] = ins
    return insns


MAX_JUMP_TABLE = 512


def resolve_jump_table(spec: Specimen, ins, inside) -> list[int]:
    """Targets of an MSVC switch dispatch `jmp dword ptr [reg*4 + table]`.

    Without this, every case block of a switch is unreachable from the entry, the
    CFG walk never assigns it a delta, and its argument reads silently vanish
    from the measure. That is not hypothetical: it is the whole reason
    `CRT__ParseFloatTextToLongDouble` measured 24 bytes where the body really
    reads `[ebp+0x20]` — 28 — from a case block.

    The table is read as consecutive dwords and accepted only while each entry
    lands inside the declared body, so a table that is really data stops the walk
    instead of seeding it with fiction.
    """
    ops = ins.operands
    if not ops or ops[0].type != X86_OP_MEM:
        return []
    mem = ops[0].mem
    if mem.index == 0 or mem.scale != 4 or mem.base != 0:
        return []
    table = mem.disp & 0xFFFFFFFF
    out = []
    for i in range(MAX_JUMP_TABLE):
        raw = spec.read(table + i * 4, 4)
        if raw is None or len(raw) < 4:
            break
        tgt = struct.unpack("<I", raw)[0]
        if not inside(tgt):
            break
        out.append(tgt)
    return out


def _successors(ins, inside, spec=None) -> tuple[list[int], str]:
    """Control-flow successors of `ins`, and its terminator class."""
    m = ins.mnemonic
    nxt = ins.address + ins.size
    if m in RET_MNEMONICS:
        return [], "RET"
    if m in ("jmp", "ljmp"):
        ops = ins.operands
        if ops and ops[0].type == X86_OP_IMM:
            tgt = ops[0].imm
            if inside(tgt):
                return [tgt], "JMP_INTERNAL"
            return [], "JMP_EXTERNAL"
        if spec is not None:
            tbl = resolve_jump_table(spec, ins, inside)
            if tbl:
                return tbl, "JMP_TABLE"
        return [], "JMP_INDIRECT"
    if m in COND_JUMPS:
        out = []
        ops = ins.operands
        if ops and ops[0].type == X86_OP_IMM and inside(ops[0].imm):
            out.append(ops[0].imm)
        if inside(nxt):
            out.append(nxt)
        return out, "COND"
    if m in ("int3", "int", "int1", "into", "ud2", "hlt"):
        # MSVC emits `int 6` (#UD) as the unreachable/error stub between the
        # arms of a jump table. Falling through it joined an error arm's post
        # `add esp, N` depth onto the next arm's dispatch depth and produced a
        # spurious rejoin conflict in the CRT x87 emulator trampoline block.
        return [], "TRAP"
    if inside(nxt):
        return [nxt], "FALLTHROUGH"
    return [], "FALL_OFF_END"


# ------------------------------------------------------- mechanism A: the body


def measure_body(
    spec: Specimen,
    entry: int,
    ranges: list[tuple[int, int]],
    callee_cleanup=None,
    md=None,
) -> dict:
    """Measure the highest incoming argument slot the body touches.

    `callee_cleanup(target_va) -> int | None` supplies a callee's stack-cleanup
    byte count so the delta after a direct call is known. Returning None makes
    ESP UNKNOWN after that call, which is the sound answer, not a guess. The
    cleanup of a CALLEE is a byte fact about a DIFFERENT function, so using it
    here does not make this measure depend on the measured function's own RET.
    """
    md = md or _decoder()
    insns = decode_body(spec, ranges, md)
    inside = lambda a: any(lo <= a < hi for lo, hi in ranges)

    result = {
        "entry": f"0x{entry:08x}",
        "ranges": [f"{lo:08x}-{hi - 1:08x}" for lo, hi in ranges],
        "body_bytes": sum(hi - lo for lo, hi in ranges),
        "insn_count": len(insns),
        "status": "UNDETERMINED",
        "reason": "",
        "max_slot_touched": -1,
        "max_slot_read": -1,
        "arg_bytes_min": 0,
        "arg_slots_touched": [],
        "exactness": "LOWER_BOUND",
        "frame": "NONE",
        "frame_ebp_offset": None,
        "blocks_visited": 0,
        "rejoin_conflicts": [],
        "unresolved_stack_accesses": 0,
        "indexed_stack_accesses": 0,
        "stack_address_escapes": 0,
        "unresolved_calls": 0,
        "resolved_calls": 0,
        "unreached_bytes": 0,
        "ret_sites": 0,
        "ret_delta_ok": None,
        "ret_delta_seen": [],
        "local_cleanup": "UNKNOWN",
        "terminators": {},
    }

    if not insns:
        result["reason"] = "NO_INSTRUCTIONS_DECODED"
        return result
    if entry not in insns:
        result["reason"] = "ENTRY_NOT_AN_INSTRUCTION_BOUNDARY"
        return result

    conflicts: list[str] = []
    slots_touched: set[int] = set()
    slots_read: set[int] = set()
    counters = Counter()
    terminators = Counter()
    ret_deltas: set[tuple] = set()
    ebp_offsets: set[int] = set()

    # ------------------------------------------------------------- phase 1
    # Fixed point of the per-instruction abstract state. Merging is a LATTICE
    # MEET, so an unknown delta arriving from one predecessor degrades the join
    # to unknown instead of pretending the known one is authoritative. Two
    # different EXACT deltas at one instruction is the case the brief calls out:
    # it is recorded as a conflict and the whole body is refused, because there
    # is no honest single answer and averaging would invent one.
    at: dict[int, State] = {}
    work = [(entry, State.entry())]
    visits = 0
    while work:
        addr, incoming = work.pop()
        visits += 1
        if visits > MAX_VISITS:  # pragma: no cover - guard rail
            conflicts.append("VISIT_LIMIT")
            break
        ins = insns.get(addr)
        if ins is None:
            continue
        prior = at.get(addr)
        if prior is None:
            at[addr] = incoming.copy()
        else:
            joined, changed, exact_conflict = meet_state(prior, incoming)
            if exact_conflict:
                conflicts.append(
                    f"{addr:08x}:esp{prior.esp!r}/{incoming.esp!r}"
                    if prior.esp != incoming.esp
                    else f"{addr:08x}:ebp{prior.ebp!r}/{incoming.ebp!r}"
                )
            if not changed:
                continue
            at[addr] = joined
        state = at[addr]
        nxt_state = _transfer(ins, state, callee_cleanup, Counter(), set())
        for s in _successors(ins, inside, spec)[0]:
            work.append((s, nxt_state))

    # ------------------------------------------------------------- phase 2
    # Resolve accesses only against the FINAL state, so nothing is credited on
    # the strength of a delta that a later merge widened away.
    for addr in sorted(at):
        ins = insns[addr]
        state = at[addr]
        for op in ins.operands:
            if op.type != X86_OP_MEM:
                continue
            lo, hi, tag = _mem_offset_range(state, op.mem)
            if tag == "NONSTACK":
                continue
            if lo is None:
                counters[
                    "indexed_stack_accesses"
                    if tag.endswith("_INDEXED")
                    else "unresolved_stack_accesses"
                ] += 1
                continue
            if hi < FIRST_ARG_OFFSET:
                continue  # provably a local or the return address slot
            if lo != hi:
                counters["unresolved_stack_accesses"] += 1
                continue
            if lo % DWORD:
                # A misaligned access into the argument area: real, but not a
                # slot. Count it as unresolved rather than rounding it.
                counters["unresolved_stack_accesses"] += 1
                continue
            slot = (lo - FIRST_ARG_OFFSET) // DWORD
            slots_touched.add(slot)
            access = getattr(op, "access", 0)
            if access & 1:  # CS_AC_READ
                slots_read.add(slot)

        # --- register-escape of a stack address weakens completeness only
        if ins.mnemonic == "lea":
            ops = ins.operands
            if len(ops) == 2 and ops[1].type == X86_OP_MEM:
                if ops[1].mem.base in (X86_REG_ESP, X86_REG_EBP) and ops[0].reg not in (
                    X86_REG_ESP,
                    X86_REG_EBP,
                ):
                    counters["stack_address_escapes"] += 1
        elif ins.mnemonic == "mov":
            ops = ins.operands
            if (
                len(ops) == 2
                and ops[1].type == X86_OP_REG
                and ops[1].reg in (X86_REG_ESP, X86_REG_EBP)
                and not (ops[0].type == X86_OP_REG and ops[0].reg in (X86_REG_ESP, X86_REG_EBP))
            ):
                counters["stack_address_escapes"] += 1
        elif ins.mnemonic == "push":
            ops = ins.operands
            if ops and ops[0].type == X86_OP_REG and ops[0].reg in (X86_REG_ESP, X86_REG_EBP):
                counters["stack_address_escapes"] += 1

        _transfer(ins, state, callee_cleanup, counters, ebp_offsets)

        term = _successors(ins, inside, spec)[1]
        terminators[term] += 1
        if term == "RET":
            ret_deltas.add(state.esp.key())

    # ------------------------------------------------------------- assemble
    result["blocks_visited"] = len(at)
    result["rejoin_conflicts"] = sorted(set(conflicts))[:8]
    for k in (
        "unresolved_stack_accesses",
        "indexed_stack_accesses",
        "stack_address_escapes",
        "unresolved_calls",
        "resolved_calls",
    ):
        result[k] = counters[k]
    reached = sum(insns[a].size for a in at)
    result["unreached_bytes"] = max(0, result["body_bytes"] - reached)
    result["terminators"] = dict(terminators)
    result["ret_sites"] = terminators.get("RET", 0)
    result["ret_delta_seen"] = sorted(str(Stk(*d)) for d in ret_deltas)
    if ret_deltas:
        # Three-valued on purpose. A RET reached at a KNOWN non-zero delta is a
        # real inconsistency; a RET reached at an UNKNOWN delta only means the
        # lattice lost track upstream, usually at an unresolvable call, and must
        # not be reported as a failed oracle.
        exact = {d for d in ret_deltas if d[0] is not None and d[0] == d[1]}
        unknown = {d for d in ret_deltas if d[0] is None or d[0] != d[1]}
        if exact and any(d != (0, 0) for d in exact):
            result["ret_delta_ok"] = False
        elif unknown:
            result["ret_delta_ok"] = None
        else:
            result["ret_delta_ok"] = True
    if ebp_offsets:
        result["frame_ebp_offset"] = sorted(ebp_offsets)[0] if len(ebp_offsets) == 1 else None
        result["frame"] = (
            "EBP_STANDARD"
            if ebp_offsets == {-4}
            else ("EBP_ALIGNED" if len(ebp_offsets) == 1 else "EBP_MULTIPLE")
        )
    elif counters["esp_frame"]:
        result["frame"] = "ESP_ONLY"

    if terminators.get("RET", 0):
        result["local_cleanup"] = "RET_PRESENT"
    elif terminators.get("JMP_EXTERNAL") or terminators.get("JMP_INDIRECT"):
        result["local_cleanup"] = "NONE_TAIL_DISPATCH"
    elif terminators.get("TRAP"):
        result["local_cleanup"] = "NONE_TRAP"
    else:
        result["local_cleanup"] = "NONE_OTHER"

    if result["rejoin_conflicts"]:
        result["status"] = "UNDETERMINED"
        result["reason"] = "REJOIN_CONFLICT"
        return result
    if result["ret_delta_ok"] is False:
        # The internal oracle failed: a RET was reached at a known non-zero
        # stack depth, so the delta lattice does not describe this body and any
        # slot it produced is fiction. This is the gate that caught the six
        # `_alloca_probe` frames and the `push eax; ret` trampoline.
        result["status"] = "UNDETERMINED"
        result["reason"] = "RET_DELTA_INCONSISTENT"
        result["max_slot_touched"] = -1
        result["max_slot_read"] = -1
        result["arg_bytes_min"] = 0
        return result

    if slots_touched:
        result["max_slot_touched"] = max(slots_touched)
        result["arg_slots_touched"] = sorted(slots_touched)
        result["arg_bytes_min"] = (max(slots_touched) + 1) * DWORD
    if slots_read:
        result["max_slot_read"] = max(slots_read)
    result["status"] = "DETERMINATE"
    result["reason"] = "ARG_ACCESS_RESOLVED" if slots_touched else "NO_ARG_ACCESS_RESOLVED"
    complete = (
        counters["unresolved_stack_accesses"] == 0
        and counters["indexed_stack_accesses"] == 0
        and counters["stack_address_escapes"] == 0
        and counters["unresolved_calls"] == 0
        and result["unreached_bytes"] == 0
    )
    result["exactness"] = "COMPLETE_ENUMERATION" if complete else "LOWER_BOUND"
    return result


def _transfer(ins, state: State, callee_cleanup, counters, ebp_offsets) -> State:
    """Abstract effect of one instruction on ESP/EBP. Unmodelled => UNKNOWN."""
    out = state.copy()
    m = ins.mnemonic
    ops = ins.operands

    if m == "push":
        size = ops[0].size if ops else DWORD
        out.esp = out.esp.shift(-size)
        return out
    if m == "pop":
        size = ops[0].size if ops else DWORD
        out.esp = out.esp.shift(size)
        if ops and ops[0].type == X86_OP_REG and ops[0].reg == X86_REG_EBP:
            out.ebp, out.ebp_kind = Stk.unknown(), "RESTORED"
        return out
    if m in ("pushfd", "pushal", "pushad"):
        out.esp = out.esp.shift(-(32 if m in ("pushal", "pushad") else 4))
        return out
    if m in ("popfd", "popal", "popad"):
        out.esp = out.esp.shift(32 if m in ("popal", "popad") else 4)
        if m in ("popal", "popad"):
            out.ebp, out.ebp_kind = Stk.unknown(), "RESTORED"
        return out
    if m in ("pushfw", "pushf"):
        out.esp = out.esp.shift(-2)
        return out
    if m in ("popfw", "popf"):
        out.esp = out.esp.shift(2)
        return out
    if m == "leave":
        out.esp = Stk(state.ebp.lo, state.ebp.hi).shift(DWORD)
        out.ebp, out.ebp_kind = Stk.unknown(), "RESTORED"
        return out
    if m == "enter":
        out.esp = Stk.unknown()
        out.ebp, out.ebp_kind = Stk.unknown(), "ENTER"
        return out
    if m == "call":
        cleanup = None
        if ops and ops[0].type == X86_OP_IMM and callee_cleanup is not None:
            cleanup = callee_cleanup(ops[0].imm, state)
        out.eax_imm = None  # the callee's return value lands in EAX
        if cleanup is None:
            counters["unresolved_calls"] += 1
            out.esp = Stk.unknown()
        else:
            counters["resolved_calls"] += 1
            out.esp = out.esp.shift(cleanup)
        return out

    if _writes(ins, X86_REG_EAX):
        if (
            m == "mov"
            and len(ops) == 2
            and ops[0].type == X86_OP_REG
            and ops[0].reg == X86_REG_EAX
            and ops[1].type == X86_OP_IMM
        ):
            out.eax_imm = ops[1].imm
        else:
            out.eax_imm = None

    writes_esp = _writes(ins, X86_REG_ESP)
    writes_ebp = _writes(ins, X86_REG_EBP)
    if not writes_esp and not writes_ebp:
        return out

    if writes_esp:
        counters["esp_frame"] += 1
        handled = False
        if m in ("sub", "add") and len(ops) == 2 and ops[1].type == X86_OP_IMM:
            delta = -ops[1].imm if m == "sub" else ops[1].imm
            out.esp = out.esp.shift(delta)
            handled = True
        elif m == "and" and len(ops) == 2 and ops[1].type == X86_OP_IMM:
            align = _and_alignment(ops[1].imm)
            out.esp = out.esp.align_down(align) if align else Stk.unknown()
            handled = True
        elif m == "mov" and len(ops) == 2 and ops[1].type == X86_OP_REG:
            if ops[1].reg == X86_REG_EBP:
                out.esp = Stk(state.ebp.lo, state.ebp.hi)
            else:
                out.esp = Stk.unknown()
            handled = True
        elif m == "lea" and len(ops) == 2 and ops[1].type == X86_OP_MEM:
            lo, hi, tag = _mem_offset_range(state, ops[1].mem)
            out.esp = Stk(lo, hi) if lo is not None else Stk.unknown()
            handled = True
        if not handled:
            out.esp = Stk.unknown()

    if writes_ebp:
        handled = False
        if m == "mov" and len(ops) == 2 and ops[1].type == X86_OP_REG:
            if ops[1].reg == X86_REG_ESP:
                out.ebp, out.ebp_kind = Stk(state.esp.lo, state.esp.hi), "FROM_ESP"
                if state.esp.is_exact:
                    ebp_offsets.add(state.esp.lo)
            else:
                out.ebp, out.ebp_kind = Stk.unknown(), "FROM_REG"
            handled = True
        elif m == "lea" and len(ops) == 2 and ops[1].type == X86_OP_MEM:
            lo, hi, tag = _mem_offset_range(state, ops[1].mem)
            if lo is not None:
                out.ebp, out.ebp_kind = Stk(lo, hi), "FROM_LEA"
                if lo == hi:
                    ebp_offsets.add(lo)
            else:
                out.ebp, out.ebp_kind = Stk.unknown(), "FROM_LEA_NONSTACK"
            handled = True
        if not handled:
            # mov ebp,[mem] / xor ebp,ebp / add ebp,eax / pop-free reload:
            # EBP is now a DATA pointer, not a frame pointer. Its memory
            # operands must stop counting as argument reads from here on.
            out.ebp, out.ebp_kind = Stk.unknown(), "DATA_POINTER"
    return out


def _writes(ins, reg) -> bool:
    try:
        _regs_read, regs_written = ins.regs_access()
    except Exception:  # pragma: no cover - capstone build without regs_access
        regs_written = ()
    if reg in regs_written:
        return True
    for op in ins.operands:
        if op.type == X86_OP_REG and op.reg == reg and (getattr(op, "access", 0) & 2):
            return True
    return False


# ------------------------------------------------- mechanism B: the callers


def collect_call_sites(spec: Specimen, bodies: dict, md=None) -> dict:
    """Boundary-validated call-site index: target VA -> list of site records.

    Every declared body is decoded linearly, so an `E8` byte that is really an
    immediate inside another instruction is never mistaken for a call. That
    distinction has bitten this campaign before: a reducer that scanned for the
    first `E8` BYTE without boundary validation produced false negatives that
    looked like corpus gaps.

    Each record carries the two caller-side witnesses:
      `add_esp`   bytes the CALLER popped immediately after the call, or None.
                  Exact when present: the caller supplied exactly that much.
      `push_run`  bytes pushed in the unbroken run before the call, and whether
                  that run was clean (a non-push, ESP-neutral instruction ahead
                  of it) or interleaved.
    """
    md = md or _decoder()
    sites: dict[int, list[dict]] = defaultdict(list)
    for va, info in bodies.items():
        insns = decode_body(spec, info["ranges"], md)
        if not insns:
            continue
        order = sorted(insns)
        pos = {a: i for i, a in enumerate(order)}
        # a jump target inside the body starts a new block: a push run must not
        # be counted across it, because the pushes may not be on this path
        targets = set()
        for a in order:
            ins = insns[a]
            if ins.mnemonic in COND_JUMPS or ins.mnemonic in ("jmp", "ljmp"):
                for op in ins.operands:
                    if op.type == X86_OP_IMM:
                        targets.add(op.imm)
        for a in order:
            ins = insns[a]
            if ins.mnemonic != "call":
                continue
            ops = ins.operands
            if not ops or ops[0].type != X86_OP_IMM:
                continue
            target = ops[0].imm
            i = pos[a]
            after = insns.get(a + ins.size)
            add_esp = None
            if (
                after is not None
                and after.mnemonic == "add"
                and len(after.operands) == 2
                and after.operands[0].type == X86_OP_REG
                and after.operands[0].reg == X86_REG_ESP
                and after.operands[1].type == X86_OP_IMM
            ):
                add_esp = after.operands[1].imm
            pushed, clean = _push_run(insns, order, i, targets)
            sites[target].append(
                {
                    "caller": f"0x{va:08x}",
                    "site": f"0x{a:08x}",
                    "add_esp": add_esp,
                    "push_run": pushed,
                    "push_run_clean": clean,
                }
            )
    return sites


def _push_run(insns, order, i, targets) -> tuple[int, bool]:
    """Bytes pushed in the run immediately before `order[i]` (the call).

    Walks back over instructions that neither touch ESP nor transfer control.
    Stops at a basic-block boundary or the previous control transfer, which is
    what stops an earlier call's arguments being counted for this one. Clean
    means the run terminated on such a boundary rather than running out of
    window.
    """
    total = 0
    j = i - 1
    steps = 0
    while j >= 0 and steps < 64:
        a = order[j]
        ins = insns[a]
        if a in targets:
            # the instruction itself may still be a push belonging to this run,
            # but anything before it is on another path
            if ins.mnemonic == "push":
                total += ins.operands[0].size if ins.operands else DWORD
            return total, True
        m = ins.mnemonic
        if m == "push":
            total += ins.operands[0].size if ins.operands else DWORD
        elif m in RET_MNEMONICS or m in COND_JUMPS or m in ("jmp", "ljmp", "call"):
            return total, True
        elif m in ("pop", "leave", "enter", "popad", "pushad", "popfd", "pushfd"):
            return total, True
        elif _writes(ins, X86_REG_ESP):
            return total, True
        j -= 1
        steps += 1
    return total, j < 0


def caller_witness(sites: list[dict]) -> dict:
    """Fold a target's call sites into one caller-side witness, or a conflict."""
    out = {
        "n_sites": len(sites),
        "add_esp_values": {},
        "push_run_values": {},
        "witness": None,
        "witness_kind": "NONE",
        "conflict": False,
    }
    if not sites:
        return out
    adds = Counter(s["add_esp"] for s in sites if s["add_esp"] is not None)
    runs = Counter(s["push_run"] for s in sites if s["push_run_clean"])
    out["add_esp_values"] = dict(adds)
    out["push_run_values"] = dict(runs)
    if adds:
        if len(adds) == 1:
            out["witness"] = next(iter(adds))
            out["witness_kind"] = "CALLER_CLEANUP_ADD_ESP"
        else:
            out["conflict"] = True
            out["witness_kind"] = "CALLER_CLEANUP_CONFLICT"
        return out
    if runs:
        if len(runs) == 1:
            out["witness"] = next(iter(runs))
            out["witness_kind"] = "PUSH_RUN_UNANIMOUS"
        else:
            out["witness"] = min(runs)
            out["witness_kind"] = "PUSH_RUN_SPLIT"
            out["conflict"] = True
        return out
    return out


# ----------------------------------------------------------------- body input


def load_bodies(path: Path) -> dict:
    """Body ranges keyed by entry VA.

    Accepts a `byte_truth.json`-shaped object (address -> {"ranges": [...]}) or
    a TSV with `addr` and `ranges` columns. Ranges are `lo-hi` with hi the last
    byte INCLUSIVE, matching the exporter's `body_ranges`.
    """
    text = path.read_text(encoding="utf-8")
    out: dict[int, dict] = {}
    if text.lstrip().startswith("{"):
        raw = json.loads(text)
        for addr, rec in raw.items():
            va = int(addr, 16)
            out[va] = {
                "ranges": _parse_ranges(rec["ranges"]),
                "name": rec.get("name", ""),
                "ret_imms": _ret_imms(rec),
                "paramSize": rec.get("paramSize"),
                "paramCount": rec.get("paramCount"),
                "callingConv": rec.get("callingConv", ""),
                "sigSource": rec.get("sigSource", ""),
                "signature": rec.get("signature", ""),
            }
        return out
    lines = text.splitlines()
    cols = lines[0].split("\t")
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        row = {cols[i]: parts[i] if i < len(parts) else "" for i in range(len(cols))}
        va = int(row["addr"], 16)
        out[va] = {
            "ranges": _parse_ranges(row["ranges"].split(";")),
            "name": row.get("name", ""),
            "ret_imms": [],
            "paramSize": None,
            "paramCount": None,
            "callingConv": row.get("cc", ""),
            "sigSource": row.get("sig_source", ""),
            "signature": "",
        }
    return out


def _parse_ranges(items) -> list[tuple[int, int]]:
    out = []
    for s in items:
        s = s.strip()
        if not s or "-" not in s:
            continue
        lo, hi = s.split("-", 1)
        out.append((int(lo, 16), int(hi, 16) + 1))  # exporter hi is inclusive
    return out


def _ret_imms(rec) -> list[int]:
    vals = set()
    for key in ("L_ret", "D_ret"):
        for _site, pair in (rec.get(key) or {}).items():
            mn, imm = pair[0], pair[1]
            if mn in RET_MNEMONICS:
                vals.add(imm if imm is not None else 0)
    return sorted(vals)


# The MSVC page-probe allocator, matched on its BYTES rather than on a name so
# a renamed or unnamed copy is still found. The prologue is
#   51                push ecx
#   3d 00 10 00 00    cmp eax, 0x1000
#   8d 4c 24 08       lea ecx, [esp+8]
# and the body ends `push eax; ret`, relocating the return address after
# `mov esp, ecx`. Net effect on the CALLER: ESP -= EAX. Derived by hand from
# 0x0055def0 in this specimen; `find_stack_probes` re-finds it from the bytes.
ALLOCA_PROBE_PREFIXES = (bytes.fromhex("513d001000008d4c2408"),)


def find_stack_probes(spec: Specimen, bodies: dict) -> dict:
    """Bodies that move ESP by EAX and return: MSVC `_alloca_probe`/`__chkstk`.

    Identified by the exact prologue bytes plus a `push eax; ret` tail, so the
    claim "this callee subtracts EAX from the caller's ESP" is anchored in the
    bytes of that callee and not in its symbol.
    """
    found = {}
    for va, info in bodies.items():
        rgs = info["ranges"]
        if not rgs:
            continue
        lo, hi = rgs[0]
        head = spec.read(lo, 10)
        if head is None:
            continue
        if not any(head.startswith(p) for p in ALLOCA_PROBE_PREFIXES):
            continue
        tail = spec.read(hi - 2, 2)
        if tail != b"\x50\xc3":  # push eax ; ret
            continue
        found[va] = info.get("name", "")
    return found


def build_cleanup_resolver(spec: Specimen, bodies: dict, md=None) -> tuple:
    """Resolver for "how much does ESP move across a call to this callee".

    The general law, derived rather than assumed: if the callee reaches its
    `ret` at entry-relative delta D and that `ret` carries immediate N, then the
    caller's ESP after the call is `pre + D + N`. D is 0 for an ordinary
    function; it is -16 for MSVC's `__SEH_prolog`-shaped `push eax; ret`
    trampoline, which is why assuming D=0 produced a fictional +8460 stack at
    the RET of six cohort bodies.

    D comes from a first pass of this same instrument over every declared body,
    so it is a byte measurement of the CALLEE. It is never the subject's own
    terminator, which is what keeps this witness independent of the RET axis it
    is meant to corroborate.
    """
    md = md or _decoder()
    probes = find_stack_probes(spec, bodies)
    single_imm = {
        va: info["ret_imms"][0] for va, info in bodies.items() if len(info["ret_imms"]) == 1
    }

    def make(delta_map):
        def resolve(va: int, state: State):
            if va in probes:
                return None if state.eax_imm is None else -state.eax_imm
            n = single_imm.get(va)
            if n is None:
                return None
            d = delta_map.get(va)
            if d is None:
                return None
            return d + n

        return resolve

    # pass A: assume the ordinary D = 0 so that a delta can be measured at all
    pass_a = make({va: 0 for va in single_imm})
    delta_map = {}
    for va, info in bodies.items():
        r = measure_body(spec, va, info["ranges"], pass_a, md)
        if r["rejoin_conflicts"]:
            continue
        seen = r["ret_delta_seen"]
        if len(seen) == 1 and seen[0].startswith(("+", "-")) and "," not in seen[0]:
            try:
                delta_map[va] = int(seen[0])
            except ValueError:
                continue
    return make(delta_map), {
        "probes": {f"0x{va:08x}": name for va, name in probes.items()},
        "delta_resolved": len(delta_map),
        "delta_nonzero": {
            f"0x{va:08x}": d for va, d in delta_map.items() if d != 0
        },
    }


def cleanup_resolver(bodies: dict):
    """Minimal resolver: the callee's single RET immediate, D assumed 0.

    Kept for tests and for callers that have no specimen-wide pass available.
    Prefer `build_cleanup_resolver`, which measures D instead of assuming it.
    """
    direct = {}
    for va, info in bodies.items():
        imms = info["ret_imms"]
        if len(imms) == 1:
            direct[va] = imms[0]

    def resolve(va: int, state: State | None = None):
        return direct.get(va)

    return resolve


# ------------------------------------------------------------------ negatives


def negative_control_non_boundary(spec: Specimen, bodies: dict, n: int, seed: int, md=None) -> dict:
    """Feed the instrument VAs that are NOT instruction boundaries.

    An address in the middle of an instruction decodes into a different, valid
    instruction stream. If the instrument accepts those as measured functions it
    is measuring noise. `false_accepts` counts the ones that come back
    DETERMINATE with a positive argument extent AND a self-consistent RET delta,
    which is exactly the gate a witness has to clear downstream.
    """
    import random

    md = md or _decoder()
    rng = random.Random(seed)
    boundaries = set()
    covered = []
    for va, info in bodies.items():
        for lo, hi in info["ranges"]:
            covered.append((lo, hi))
    for va, info in list(bodies.items()):
        for a in decode_body(spec, info["ranges"], md):
            boundaries.add(a)
    pool = []
    for lo, hi in covered:
        pool.append((lo, hi))
    picked = []
    guard = 0
    while len(picked) < n and guard < n * 50:
        guard += 1
        lo, hi = pool[rng.randrange(len(pool))]
        if hi - lo < 8:
            continue
        va = rng.randrange(lo + 1, hi)
        if va in boundaries:
            continue
        picked.append(va)
    stats = Counter()
    false_accepts = []
    resolver = build_cleanup_resolver(spec, bodies, md)[0]
    for va in picked:
        r = measure_body(spec, va, [(va, min(va + 96, va + 96))], resolver, md)
        stats[r["status"]] += 1
        accept = (
            r["status"] == "DETERMINATE"
            and r["arg_bytes_min"] > 0
            and r["ret_delta_ok"] is True
        )
        if accept:
            false_accepts.append({"va": f"0x{va:08x}", "arg_bytes_min": r["arg_bytes_min"]})
        stats["ACCEPT" if accept else "REJECT"] += 1
    return {
        "probed": len(picked),
        "status_histogram": dict(stats),
        "false_accepts": len(false_accepts),
        "false_accept_examples": false_accepts[:10],
    }


def negative_control_corrupt_ret(spec: Specimen, bodies: dict, addrs, md=None) -> dict:
    """Corrupt the RET immediate in a COPY of the image; the measure must not move.

    This is the independence proof, not a robustness test. If the argument-slot
    number changes when only the terminator's immediate changes, the witness is
    not independent of the thing it is meant to corroborate.
    """
    md = md or _decoder()
    resolver = build_cleanup_resolver(spec, bodies, md)[0]
    moved = []
    checked = 0
    for va in addrs:
        info = bodies.get(va)
        if not info:
            continue
        base = measure_body(spec, va, info["ranges"], resolver, md)
        if base["status"] != "DETERMINATE":
            continue
        insns = decode_body(spec, info["ranges"], md)
        ret_sites = [
            a
            for a, i in insns.items()
            if i.mnemonic in RET_MNEMONICS and i.size == 3  # C2 imm16
        ]
        if not ret_sites:
            continue
        data = bytearray(spec.data)
        for a in ret_sites:
            off = spec.offset(a)
            if off is None:
                continue
            data[off + 1] = (data[off + 1] + 0x40) & 0xFF
            data[off + 2] = (data[off + 2] + 1) & 0xFF
        alt = Specimen(bytes(data))
        after = measure_body(alt, va, info["ranges"], resolver, md)
        checked += 1
        if after["arg_bytes_min"] != base["arg_bytes_min"] or after["status"] != base["status"]:
            moved.append(
                {
                    "va": f"0x{va:08x}",
                    "before": base["arg_bytes_min"],
                    "after": after["arg_bytes_min"],
                }
            )
    return {"checked": checked, "moved": len(moved), "moved_examples": moved[:10]}


def sensitivity_control_corrupt_frame(spec: Specimen, bodies: dict, addrs, md=None) -> dict:
    """Non-vacuity proof: perturb the frame the measure DOES depend on.

    Bumping `sub esp, imm` re-anchors every ESP-relative access, so a working
    instrument must report a different argument extent for at least some bodies.
    A checker that cannot be moved by the thing it claims to read is decoration.
    """
    md = md or _decoder()
    resolver = build_cleanup_resolver(spec, bodies, md)[0]
    moved = 0
    checked = 0
    for va in addrs:
        info = bodies.get(va)
        if not info:
            continue
        base = measure_body(spec, va, info["ranges"], resolver, md)
        if base["status"] != "DETERMINATE" or base["arg_bytes_min"] == 0:
            continue
        insns = decode_body(spec, info["ranges"], md)
        subs = [
            a
            for a, i in insns.items()
            if i.mnemonic == "sub"
            and len(i.operands) == 2
            and i.operands[0].type == X86_OP_REG
            and i.operands[0].reg == X86_REG_ESP
            and i.operands[1].type == X86_OP_IMM
            and i.size >= 3
        ]
        if not subs:
            continue
        data = bytearray(spec.data)
        for a in subs:
            off = spec.offset(a)
            if off is None:
                continue
            data[off + 2] = (data[off + 2] + 4) & 0xFF
        after = measure_body(Specimen(bytes(data)), va, info["ranges"], resolver, md)
        checked += 1
        if after["arg_bytes_min"] != base["arg_bytes_min"] or after["status"] != base["status"]:
            moved += 1
    return {"checked": checked, "moved": moved}


# ----------------------------------------------------------------------- main

TSV_COLUMNS = [
    "addr",
    "name",
    "status",
    "reason",
    "frame",
    "frame_ebp_offset",
    "max_slot_touched",
    "max_slot_read",
    "arg_bytes_min",
    "exactness",
    "local_cleanup",
    "ret_imms",
    "ret_delta_ok",
    "ret_delta_seen",
    "paramSize",
    "paramCount",
    "callingConv",
    "sigSource",
    "body_bytes",
    "insn_count",
    "blocks_visited",
    "unreached_bytes",
    "unresolved_stack_accesses",
    "indexed_stack_accesses",
    "stack_address_escapes",
    "unresolved_calls",
    "resolved_calls",
    "rejoin_conflicts",
    "caller_sites",
    "caller_witness",
    "caller_witness_kind",
    "caller_add_esp_values",
    "caller_push_run_values",
]


def measure_all(spec: Specimen, bodies: dict, addrs, with_callers: bool = True) -> list[dict]:
    md = _decoder()
    resolver = build_cleanup_resolver(spec, bodies, md)[0]
    sites = collect_call_sites(spec, bodies, md) if with_callers else {}
    rows = []
    for va in addrs:
        info = bodies.get(va)
        if info is None:
            rows.append({"addr": f"0x{va:08x}", "status": "NO_BODY", "reason": "NOT_IN_BODY_INDEX"})
            continue
        r = measure_body(spec, va, info["ranges"], resolver, md)
        cw = caller_witness(sites.get(va, []))
        rows.append(
            {
                "addr": f"0x{va:08x}",
                "name": info.get("name", ""),
                "status": r["status"],
                "reason": r["reason"],
                "frame": r["frame"],
                "frame_ebp_offset": r["frame_ebp_offset"],
                "max_slot_touched": r["max_slot_touched"],
                "max_slot_read": r["max_slot_read"],
                "arg_bytes_min": r["arg_bytes_min"],
                "exactness": r["exactness"],
                "local_cleanup": r["local_cleanup"],
                "ret_imms": ",".join(str(x) for x in info["ret_imms"]),
                "ret_delta_ok": r["ret_delta_ok"],
                "ret_delta_seen": ";".join(r["ret_delta_seen"]),
                "paramSize": info.get("paramSize"),
                "paramCount": info.get("paramCount"),
                "callingConv": info.get("callingConv", ""),
                "sigSource": info.get("sigSource", ""),
                "body_bytes": r["body_bytes"],
                "insn_count": r["insn_count"],
                "blocks_visited": r["blocks_visited"],
                "unreached_bytes": r["unreached_bytes"],
                "unresolved_stack_accesses": r["unresolved_stack_accesses"],
                "indexed_stack_accesses": r["indexed_stack_accesses"],
                "stack_address_escapes": r["stack_address_escapes"],
                "unresolved_calls": r["unresolved_calls"],
                "resolved_calls": r["resolved_calls"],
                "rejoin_conflicts": ";".join(r["rejoin_conflicts"]),
                "caller_sites": cw["n_sites"],
                "caller_witness": cw["witness"],
                "caller_witness_kind": cw["witness_kind"],
                "caller_add_esp_values": ",".join(
                    f"{k}x{v}" for k, v in sorted(cw["add_esp_values"].items())
                ),
                "caller_push_run_values": ",".join(
                    f"{k}x{v}" for k, v in sorted(cw["push_run_values"].items())
                ),
            }
        )
    return rows


def write_tsv(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(TSV_COLUMNS) + "\n")
        for r in rows:
            fh.write(
                "\t".join("" if r.get(c) is None else str(r.get(c, "")) for c in TSV_COLUMNS)
                + "\n"
            )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--specimen", required=True, type=Path)
    ap.add_argument("--bodies", required=True, type=Path)
    ap.add_argument("--addresses", type=Path, help="one VA per line; default all bodies")
    ap.add_argument("--tsv-out", type=Path)
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--no-callers", action="store_true")
    ap.add_argument("--allow-any-specimen", action="store_true")
    ap.add_argument("--negative-controls", type=int, default=0,
                    help="probe N non-boundary VAs and N corrupted bodies")
    args = ap.parse_args(argv)

    spec = Specimen.load(args.specimen, require_pristine=not args.allow_any_specimen)
    bodies = load_bodies(args.bodies)
    if args.addresses:
        addrs = [
            int(line.strip(), 16)
            for line in args.addresses.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
    else:
        addrs = sorted(bodies)

    rows = measure_all(spec, bodies, addrs, with_callers=not args.no_callers)
    hist = Counter(r["status"] for r in rows)
    det = [r for r in rows if r["status"] == "DETERMINATE"]
    print(f"specimen sha256 : {spec.sha256}")
    print(f"bodies indexed  : {len(bodies)}")
    print(f"addresses asked : {len(addrs)}")
    print(f"status          : {dict(hist)}")
    print(f"determinate     : {len(det)} ({100.0 * len(det) / max(1, len(rows)):.1f}%)")
    print(f"  with arg>0    : {sum(1 for r in det if r['arg_bytes_min'] > 0)}")
    print(f"  complete enum : {sum(1 for r in det if r['exactness'] == 'COMPLETE_ENUMERATION')}")
    print(f"  ret_delta_ok  : {sum(1 for r in det if r['ret_delta_ok'] is True)}")
    print(f"  ret_delta_bad : {sum(1 for r in det if r['ret_delta_ok'] is False)}")
    print(f"caller witness  : {sum(1 for r in rows if r.get('caller_witness') is not None)}")

    payload = {
        "specimen_sha256": spec.sha256,
        "bodies_indexed": len(bodies),
        "rows": rows,
        "status_histogram": dict(hist),
    }
    if args.negative_controls:
        payload["negative_control_non_boundary"] = negative_control_non_boundary(
            spec, bodies, args.negative_controls, seed=20260817
        )
        payload["negative_control_corrupt_ret"] = negative_control_corrupt_ret(
            spec, bodies, addrs[: args.negative_controls]
        )
        payload["sensitivity_control_corrupt_frame"] = sensitivity_control_corrupt_frame(
            spec, bodies, addrs[: args.negative_controls]
        )
        print("negative controls:")
        print(json.dumps({k: v for k, v in payload.items() if "control" in k}, indent=2)[:2000])
    if args.tsv_out:
        write_tsv(rows, args.tsv_out)
        print(f"wrote {args.tsv_out}")
    if args.json_out:
        args.json_out.write_text(json.dumps(payload, indent=1), encoding="utf-8")
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
