# CDestroyableSegment__SumActiveValueRecursive

> Address: `0x00442890`

Status: active static function note
Last updated: 2026-08-22
Source File: none — the reference drop has no `DestroyableSegment.cpp` source
body (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: recursive active-value sum over a segment subtree — each node
contributes its remaining life `[this+0xc]` only while its parent-break slot-6
gate stays open and its life is non-zero, then recurses through the child-set
head and next-sibling links. Called twice per damage by the controller
dispatcher for its 30% fire gate and 50% latch, plus seven other named sites.
107 bytes; every claim below re-read from the pristine specimen this wake.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256 verified
before reading) with capstone whole-body disassembly, raw byte reads (body
hash, float constant resolution, whole-.text rel32 scan, image-wide imm32
census), and xref-site ownership resolution against the tracked name table.
Cross-checked against
[`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md)'s
bulk-refresh row. No `FUN_*` milled; no Core owner changed.

> Address: `0x00442890`

## Contract (byte-exact)

Body `0x00442890`–`0x004428fa` inclusive through `ret` at `0x004428fa`
followed by five `nop`s padding to the next function boundary,
**107 bytes**, SHA-256
`6edfd5544bf96509f88287c6e954d7cb5470ddc953cb1d5fbe3ddb192b752e93`.
Frame: `push ecx/esi`, no SEH. **1 `E8`, 0 `E9`** — the single call is its own
recursion at `0x004428d4`. Signature confirmed: `thiscall`, zero stack args,
returns float in st(0).

## Stage law (byte-exact)

1. **Contribution gate** (`0x0044289c`–`0x004428bf`): if `[this+0x1c]` is
   null the node contributes nothing. Otherwise it calls vtable slot `+0x18`
   (`VFunc_06`, parent-break gate) on itself; a **nonzero** return skips the
   node entirely. Then `fld dword [this+0xc]; fcomp [0x005d856c]` (`0.0f`,
   bytes `00000000`): the node contributes only when its remaining life is
   **not equal to zero** (`test ah,0x40` / ZF on `fcomp`).
2. **Recursion** (`0x004428c3`–`0x004428f2`): walk the child set — head at
   `[this+0x24]`, next-link at `[entry+4]` — calling self on each entry and
   accumulating with `fadd dword [esp+4]`.
3. **Return** (`0x004428f4`): accumulated stack cell as float; empty or
   fully-gated subtree returns `0.0f`.

The unnamed sibling [`CDestroyableSegment__GetTotalHealth`](CDestroyableSegment__GetTotalHealth.md)
at `0x00442900` walks the identical structure but contributes `[+0xc]`
without the liveness test.

## Callers

Ten inbound rel32 image-wide, zero imm32 (sites resolved against the tracked
name table):

| Site | Caller | Shape |
| --- | --- | --- |
| `0x004428d4` | recursion into itself | child-chain walk |
| `0x0044407f`, `0x00444106` | [`CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold`](CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold.md) | 30% fire gate + 50% latch operand |
| `0x00444263` | `ApplyRandomDamageBurstAndUpdateThreshold 0x00444160` | same threshold pattern after burst damage |
| `0x00444368` | `GetCurrentSubtreeHealthIfAnyActive 0x00444330` | health query |
| `0x00444413` | `TriggerCoreCascadeIfEligible 0x004443f0` | cascade eligibility |
| `0x004444fa` | `SetSegmentFields0C10ByName 0x004444b0` | metric refresh after field writes |
| `0x004445f5` | `SetSegmentActiveFlagByName 0x004445b0` | metric refresh after flag writes |
| `0x0044464c` | `SetAllSegmentsActiveFlagAndRefreshMetric 0x00444620` | bulk refresh row of the segments contract |
| `0x00444fdf` | `CUnitAI__CanUseIndexedSegmentEntry 0x00444f20` | AI eligibility |

## Pinned-source status

Absent. No `DestroyableSegment.cpp` in the drop.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0xc]` | remaining life contributed when gate open and non-zero | load `0x004428ac` |
| `[this+0x1c]` | parent link tested before contributing | `0x0044289c` |
| vtable slot `+0x18` | parent-break gate predicate (`VFunc_06`) | call `0x004428a5` |
| `[this+0x24]` / entry `[+4]` | child-set head / next-sibling links | `0x004428c3`, `0x004428d9` |

Field names above are functional roles read off this body; retail symbol
names beyond the saved name table remain unproven and nothing here renames a
saved Ghidra symbol.

## Constants

| Address | Bytes | Value |
| --- | --- | --- |
| `0x005d856c` | `00000000` | float `0.0` (non-zero-life contributor test) |

## Rebuild mapping

No Core owner; nothing in the rebuild models per-part totals or thresholds.
Focused tests correctly deferred until one exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00442890`–`0x004428fa` is not
  `6edfd554…52e93` (full:
  `6edfd5544bf96509f88287c6e954d7cb5470ddc953cb1d5fbe3ddb192b752e93`), or the
  final instruction is anything but a bare `ret` at `0x004428fa`.
- An eleventh rel32 inbound appears, or any imm32 of `0x00442890` exists.
- The zero test stops comparing against `[0x005d856c]` = `00000000`.

## Receipts

- 2026-08-22 — pristine specimen
  (`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, main tree),
  SHA-256 verified before reading. Tools:
  `local-lab/unitdmg-r698/bealib.py` + `probe_family.py` /
  `probe_final.py` / `probe_printf_twin.py` (disassembly, hash, constant
  resolution, xref census + site ownership).
