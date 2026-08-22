# CDestroyableSegment__GetTotalHealth

> Address: `0x00442900`

Status: active static function note
Last updated: 2026-08-22
Source File: none — the reference drop has no `DestroyableSegment.cpp` source
body (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: sibling of
[`SumActiveValueRecursive`](CDestroyableSegment__SumActiveValueRecursive.md)
over the same first-child → next-sibling walk — returns `[this+0xc]`
(remaining life) for every segment whose parent-break slot-6 gate stays open,
with no liveness and no zero test. Seeds the controller's cached metric
`[ctrl+0x18]` during controller init. 96 bytes; every claim below re-read
from the pristine specimen this wake.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256 verified
before reading) with capstone whole-body disassembly, raw byte reads (body
hash, xref census). No `FUN_*` milled; no Core owner changed.

> Address: `0x00442900`

## Contract (byte-exact)

Body `0x0042900`–`0x0044295f` inclusive through `ret` at `0x0044295a`
followed by five `nop`s to the next-function boundary `0x0044295f`,
**96 bytes**, SHA-256
`962a94f033e56b34a1bf524aed7abcabb35e103f5f598e0375042ba7aa7a11d4`.
Frame: `push ecx/esi`, no SEH. **1 `E8`, 0 `E9`** — the single call is its own
recursion at `0x00442934`. Signature confirmed: `thiscall`, zero stack args,
returns float in st(0).

## Stage law (byte-exact)

1. **Contribution** (`0x0044290c`–`0x00442921`): if `[this+0x1c]` is null the
   node contributes nothing. Otherwise it calls vtable slot `+0x18`
   (`VFunc_06`) on itself; a **nonzero** return skips the node (same gate as
   the active-value walker). No liveness flag and no zero-life test — a dead
   segment's residual `[+0xc]` still counts here whenever the gate stays
   open.
2. **Recursion** (`0x00442923`–`0x00442952`): identical child-chain walk to
   SumActiveValueRecursive (`[+0x24]` then `[+0x4]`), each child's result
   added with `fadd dword [esp+4]`.
3. **Return** (`0x00442954`): accumulated stack cell; empty subtree is
   `0.0f`.

## Callers

Three inbound rel32 image-wide, zero imm32:

| Site | Caller | Shape |
| --- | --- | --- |
| `0x00442934` | itself (recursion) | child-chain walk |
| `0x004443a8` | `CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive 0x00444370` | runtime health queries |
| `0x00444924` | `CDestructableSegmentsController__Init 0x00444660` | seeds `[ctrl+0x18]` via `fstp dword [ctrl+0x18]` after the call (window read this wake) |

## Pinned-source status

Absent. No `DestroyableSegment.cpp` in the drop.

## Prior-art status recorded by this note

The destroyable-segments contract's "damage telemetry getters" row names
field pair `+0x14/+0x18`; this body shows the same offsets used as the base
segment's last-damage time and amount cells, and the controller-level `+0x18`
as the cached total-health metric seeded from this function at init — the
offsets are frame-relative to different classes, which the earlier row could
not separate.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0xc]` | remaining life contributed unconditionally (gate permitting) | `0x0044291c` |
| `[this+0x1c]` | parent link tested before contributing | `0x0044290c` |
| `[this+0x24]` / `[+0x4]` | child-set head / next-sibling links | `0x00442923`, `0x00442939` |
| vtable slot `+0x18` | parent-break gate predicate (`VFunc_06`) | `0x00442915` |
| `[ctrl+0x18]` | controller cached metric seeded from this function at init | Init store `0x0044929` |

Field names above are functional roles read off this body; retail symbol
names beyond the saved name table remain unproven and nothing here renames a
saved Ghidra symbol.

## Constants

| Address | Bytes | Value |
| --- | --- | --- |
| `0x005d856c` | `00000000` | float `0.0` — present in the sibling walker only; this body performs **no** float compare |

## Rebuild mapping

No Core owner; nothing in the rebuild models per-part totals. Focused tests
correctly deferred until one exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00442900`–`0x0044295f` is not
  `962a94f0…7a11d4`, or the final instruction is anything but a bare `ret`
  at `0x0044295a`.
- A fourth rel32 inbound appears, or any imm32 of `0x00442900` exists.
- An `fld/fcomp` pair against `[0x005d856c]` appears inside this body (it has
  none today).

## Receipts

- 2026-08-22 — pristine specimen
  (`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, main tree),
  SHA-256 verified before reading. Tools:
  `local-lab/unitdmg-r698/bealib.py` + `probe_family.py` /
  `probe_printf_twin.py` (disassembly, hash, xref census) +
  `probe_init.py` (Init seeding window `0x0044924`–`0x0044929`).
