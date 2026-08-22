# CDestructableSegmentsMotionController__VFunc_UpdateUnitAIIndexedEntryFlag

> Address: `0x00494FA0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — no destroyable-segments motion-controller body survives
in `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine
specimen `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: a shared motion-controller virtual bridge that updates only bit 0 of
an output flags dword. A live `entryState+0xa4` sets the bit immediately.
Otherwise it passes `entryState+0x88` to the controller-owned indexed-segment
predicate at `0x00444f20`: predicate TRUE clears bit 0; predicate FALSE sets
it. Every other output bit is preserved.
Evidence: MEASURED — pristine SHA verified before complete capstone body
decode and hash, whole-`.text` rel32 scan, image-wide imm32/vtable census,
constructor/vtable cross-check, and callee/branch-polarity read. The predicate
receiver proof is owned by the preceding note and is cross-linked rather than
restated as new evidence. No Ghidra or rebuild owner changed.

## Contract (byte-exact)

Body `0x00494fa0`–`0x00494fe0` inclusive through the complete `ret 8` at
`0x00494fde`, **65 bytes / 21 instructions**, SHA-256
`eb9758668b2c6fd58ca98df23adfdc739abb7b14a0d1bdb0b562c52cdda52fa5`.
It is frameless, saves no registers, has **1 direct `E8`, 0 `E9`**, and both
conditional branches stay inside the body. Signature shape is
`void __thiscall ...(void *motionController, void *entryState,
uint32_t *outFlags)`: two stack dwords, every exit `ret 8`.

## Flag law (byte-exact)

Let `flags = *outFlags` and `index = entryState[+0x88]`.

1. Load `[entryState+0xa4]`. When nonzero, execute
   `*outFlags = flags | 1` and return.
2. Otherwise load the segments-controller receiver from
   `[motionController+0x0c]`, push `index`, and call the current saved symbol
   `CUnitAI__CanUseIndexedSegmentEntry 0x00444f20`.
3. If the predicate returns zero, execute `*outFlags = flags | 1` and
   return.
4. If the predicate returns nonzero, execute
   `*outFlags = flags & 0xfffffffe` and return.

Thus bit 0 is exactly:
`entryState[+0xa4] != 0 || !CanUseIndexedSegmentEntry(index)`.
The body neither replaces the whole dword nor modifies bits 1–31. The source
virtual name and gameplay label for bit 0 remain unproved.

## Receiver and saved-name boundary

The prior predicate note byte-proves the receiver chain:
`CDestructableSegmentsMotionController__Ctor 0x00494c60` stores its
segments-controller argument at `[motionController+0x0c]`; the Building and
HiveBoss construction paths obtain that argument from their owning unit's
`+0x178`. Therefore the call at `0x00494fc2` passes a
`CDestructableSegmentsController`, not a CUnitAI object. The callee's current
saved `CUnitAI__` prefix remains a tracked stale identity and is not treated
as ownership evidence here.

This body does not touch `[unit+0x88]`. Its `+0x88` load is from the explicit
`entryState` argument and is immediately consumed as the integer segment
index, so it is not the unresolved float damage-cooldown expiry reader.

## Call and inbound census

The sole direct call is:

| Site | Callee / role |
| --- | --- |
| `0x00494fc2` | `CUnitAI__CanUseIndexedSegmentEntry 0x00444f20` — current saved name; controller-owned indexed-entry predicate |

There are **zero inbound rel32** sites. Exactly two image-wide imm32 dwords
point to this body, both vtable entries:

| Entry | Static table interpretation |
| --- | --- |
| `0x005dc294` | slot 6 of controller vtable `0x005dc27c` installed by `CDestructableSegmentsMotionController__Ctor`; the same dword is slot 17 when the overlapping `CMCBuggy` table is viewed from `0x005dc250` |
| `0x005dc3a0` | slot 6 of `CMCHiveBoss` table `0x005dc388` |

The dual data-only ownership explains why no direct caller exists and why the
saved function label describes a shared virtual bridge rather than an
ordinary named call target.

## Field map pinned by this body

| Offset | Static role | Anchor |
| --- | --- | --- |
| `[motionController+0x0c]` | segments-controller predicate receiver | `0x00494fbe` |
| `[entryState+0xa4]` | immediate force-set-bit-0 gate | `0x00494fa4` |
| `[entryState+0x88]` | integer indexed-segment argument | `0x00494fb8` |
| `*outFlags` bit 0 | set on live `+0xa4` or predicate FALSE; clear on predicate TRUE | three terminal arms |

## Pinned-source and rebuild status

No source body exists in the pinned drop. The rebuild has no per-part segment
controller or this motion bridge, so no Core behavior or focused test was
invented. A future implementation must preserve the short-circuit, predicate
polarity, and read-modify-write preservation of bits 1–31.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00494fa0`–`0x00494fe0` is not
  `eb975866…52fa5`, or an exit stops using `ret 8`.
- Any inbound rel32 appears, either vtable dword disappears, or a third imm32
  of the entry appears.
- The receiver load leaves `[this+0x0c]`, the index leaves
  `[entryState+0x88]`, or the direct call leaves `0x00444f20`.
- Predicate TRUE no longer clears bit 0, predicate FALSE no longer sets it,
  or either path overwrites another bit.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before
  reading. Complete body/hash, sole direct call, zero-rel32/two-imm32 census,
  all three output arms, and overlapping vtable interpretations reproduced
  with the read-only PE/capstone probe and current name/vtable tables.
- Related contract:
  [`../DestructableSegmentsController.cpp/CUnitAI__CanUseIndexedSegmentEntry.md`](../DestructableSegmentsController.cpp/CUnitAI__CanUseIndexedSegmentEntry.md).
