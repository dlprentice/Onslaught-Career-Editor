# CDestroyableCoreSegment__AreCoreChildrenDestroyed

> Address: `0x004433f0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — the reference drop has no `DestroyableSegment.cpp` source
body (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: core-segment destruction predicate over the child list — warns and
returns TRUE when there is no child set at all; otherwise returns FALSE while
any child fails vtable slot `+0x14` or still reports field `+0x38` clear.
Called by the controller dispatcher after each indexed damage to decide
whether to fire the owner's vtable slot `0xc8`. 102 bytes; every claim below
re-read from the pristine specimen this wake.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256 verified
before reading) with capstone whole-body disassembly, raw byte reads (body
hash, string constant resolution, xref census). Cross-checked against
[`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md)'s
core-child state gate row, which it confirms and sharpens (the missing-first-
child warning path is byte-pinned below). No `FUN_*` milled; no Core owner
changed.

> Address: `0x004433f0`

## Contract (byte-exact)

Body `0x00433f0`–`0x00443455` inclusive through `ret` at `0x00443455`,
**102 bytes**, SHA-256
`2203209cd442f2957720b3e22a269936ff90301424ef9e6a154565894ff5fa9f`.
Frame: `push esi/edi`, no SEH. **1 `E8`, 0 `E9`**, 9 conditional branches all
in-body. Signature confirmed: `thiscall`, zero stack args, returns BOOL in
eax (1 = destroyed/empty, 0 = some child alive).

## Stage law (byte-exact)

1. **No-children arm** (`0x004433f0`–`0x00443412`): if `[this+0x30]` (the
   child-set container) is null, emit
   `CConsole__Printf 0x00441740([0x0066f580], "Warning: First core part has
   no children" @ .rdata 0x006285bc)` once through the shared console sink
   and return TRUE immediately.
2. **Child walk** (`0x00443413`–`0x00443450`): iterate the child set head
   `[this+0x24]` → `[entry+4]` next-link. For each entry:
   - vtable slot `+0x14` called with the entry as `ecx`; nonzero → child is
     fine, continue;
   - otherwise if `[entry+0x38] == 0` → return FALSE (a child still stands);
   - else continue (slot returned zero but `[+0x38]` is set — treated as
     destroyed).
3. **All children passed** (`0x00443449`–`0x00443455`): return TRUE.

## Callers

Exactly **three** inbound rel32 image-wide, zero imm32:

| Site | Caller | Shape |
| --- | --- | --- |
| `0x00444066` | [`CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold`](CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold.md) | post-damage callback gate |
| `0x004443f9` | `CDestructableSegmentsController__TriggerCoreCascadeIfEligible 0x004443f0` | cascade eligibility |
| `0x00444fc5` | `CUnitAI__CanUseIndexedSegmentEntry 0x00444f20` | AI eligibility |

## Pinned-source status

Absent. No `DestroyableSegment.cpp` in the drop.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x30]` | child-set container tested for existence | `0x004433f0` |
| `[this+0x24]` | child-set iteration head | `0x00443413` |
| entry `[+4]` | next-link of the child set | `0x00443436` |
| entry `[+0x38]` | destroyed-style state flag | `0x0044342f` |
| vtable slot `+0x14` | per-entry destroyed predicate | `0x00443428` |

Field names above are functional roles read off this body; retail symbol
names beyond the saved name table remain unproven and nothing here renames a
saved Ghidra symbol.

## Constants

| Address | Bytes | Value |
| --- | --- | --- |
| `0x006285bc` | — | `"Warning: First core part has no children"` |

## Rebuild mapping

No Core owner; nothing in the rebuild models core-child destruction gates.
Focused tests correctly deferred until one exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x004433f0`–`0x00443455` is not
  `2203209c…ff5fa9f`, or the final instruction is anything but a bare `ret`
  at `0x00443455`.
- A fourth rel32 inbound appears, or any imm32 of `0x004433f0` exists.
- The warning string leaves `.rdata 0x006285bc`, or the null-children arm
  ever returns 0 instead of 1.

## Receipts

- 2026-08-22 — pristine specimen
  (`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, main tree),
  SHA-256 verified before reading. Tools:
  `local-lab/unitdmg-r698/bealib.py` + `probe_family.py` /
  `probe_final.py` (disassembly, hash, string resolution, xref census).
