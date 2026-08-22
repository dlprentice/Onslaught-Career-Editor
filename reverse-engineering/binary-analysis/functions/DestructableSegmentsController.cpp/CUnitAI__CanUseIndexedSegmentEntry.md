# CUnitAI__CanUseIndexedSegmentEntry

> Address: `0x00444f20`

Status: active static function note — current saved Ghidra name retained for
identity checking, but the byte-proved receiver is a
`CDestructableSegmentsController`, not a `CUnitAI`
Last updated: 2026-08-22
Source File: none — the reference drop has no `DestructableSegmentsController.cpp`
source body (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: a controller-owned indexed-entry predicate used by the destroyable-
segments motion bridge. It resolves either the directly indexed segment or
an owner-mesh alias, normally returns whether segment field `+0x38` is zero,
and adds one core/30%-health veto for a narrow direct-segment state. The
saved `CUnitAI__` prefix is disproved by constructor and caller dataflow;
`CDestructableSegmentsController__CanUseIndexedSegmentEntry` is the
byte-supported rename candidate. 237 bytes; every load-bearing claim below
was re-read from the pristine specimen this wake.
Evidence: MEASURED — pristine SHA verified before capstone whole-body
instruction decoding, raw body/helper hashing, whole-`.text` rel32 scans,
image-wide imm32 censuses, caller and constructor dataflow, and constant
reads. W003 plates were consulted only after the independent byte read. No
`FUN_*` was a first gate; no Ghidra mutation or Core change was made.

## Contract (byte-exact)

Body `0x00444f20`–`0x0044500c` inclusive through the complete `ret 4` at
`0x0044500a`, **237 bytes / 92 instructions**, SHA-256
`0e79d11cbd2a59246204c9b972686f2589a05d982a66e99204fc54dd791e6d83`.
Frame `sub esp,8`, saves EBX/ESI/EDI. **2 direct `E8`, 0 `E9`**; all 12
conditional branches stay inside the body. Signature shape is
`bool __thiscall ...(void *controller, int entryIndex)`: ECX is saved as
ESI, the one stack dword is saved as EBX, and every exit is `ret 4`.

The current saved symbol is intentionally preserved in the title so the
tracked name table can detect future drift. It is not treated as owner
proof.

## Receiver ownership (byte-proved correction)

The sole caller is
`CDestructableSegmentsMotionController__VFunc_UpdateUnitAIIndexedEntryFlag`
at `0x00494fc2`. That caller executes:

```
mov eax,[arg+0x88]       ; entryIndex
mov ecx,[motion+0x0c]    ; predicate receiver
push eax
call 0x00444f20
```

`CDestructableSegmentsMotionController__Ctor 0x00494c60` stores its only
stack argument directly to `[motion+0x0c]`. Its two callers pass the
segments controller already stored at the owning unit's `[unit+0x178]`:
`CBuilding__VFunc_9_00417190` and `CMCHiveBoss__Constructor 0x00497090`.
The motion constructor's complete 51-byte body hashes
`7a0b51756fa6d4e4105b92ba279fab128e6fa97d33b211e3ce7bf5b77744a02e`;
the caller body `0x00494fa0`–`0x00494fe0` is 65 bytes, SHA-256
`eb9758668b2c6fd58ca98df23adfdc739abb7b14a0d1bdb0b562c52cdda52fa5`.

Inside this body, the same receiver is independently used with the proved
controller layout: array `+0x4`, root `+0xc`, owner `+0x10`, cached metric
`+0x18`, and mode field `+0x24`. This closes W003's owner question:
`CUnitAI__` is a stale prefix, not merely an uncertain one.

## Predicate law (byte-exact)

Let `index` be the one stack argument and
`direct = [ctrl+0x4][index]`.

### A. No directly indexed segment (`0x00444f32`–`0x00444fa7`)

1. If `direct == null`, load the owning host `[ctrl+0x10]`, then its mesh
   link `[owner+0x30]`. A null mesh link returns **TRUE**.
2. Call that mesh object's vtable byte offset `+0x24`. A null result returns
   **TRUE**.
3. Resolve entry `[result+0x160][index]`. A null entry returns **TRUE**.
4. Require `[entry+0x8c] == 5`; any other value returns **TRUE**.
5. Require `[entry+0x98] != null`; null returns **TRUE**.
6. Read alias index `[[entry+0x98]+0x88]`, then
   `alias = [ctrl+0x4][aliasIndex]`. A null alias returns **TRUE**.
7. Return `alias[+0x38] == 0`.

This is a permissive fallback: absent/unsupported owner-mesh metadata does
not veto the entry; only a resolved alias with nonzero `+0x38` returns
FALSE.

### B. Directly indexed segment exists (`0x00444faa`–`0x0044500c`)

The normal result is `direct[+0x38] == 0`, but a narrow special arm can
force FALSE first:

1. `[ctrl+0x24] != 0` skips directly to the normal result.
2. Otherwise call direct segment vtable byte offset `+0x14` (slot 5).
   A nonzero result skips to the normal result.
3. Require `[direct+0x40] == 1`; any other value skips to normal result.
4. Call `CDestroyableCoreSegment__AreCoreChildrenDestroyed([ctrl+0xc])`.
   Return value 1 forces **FALSE**.
5. Otherwise compute `[ctrl+0x18] * 0.3` (double constant
   `0x005db0a0`) and call
   `CDestroyableSegment__SumActiveValueRecursive([ctrl+0xc])`.
   A fresh sum strictly below the threshold forces **FALSE**; equality or
   greater continues to the normal result.
6. Return `direct[+0x38] == 0`.

The special veto is therefore:
`ctrl.mode24 == 0 && slot5(direct) == 0 && direct.field40 == 1 &&
(allCoreChildrenDestroyed || activeSum < cachedMetric*0.3)`.
No source enum names are attached to mode `+0x24`, slot 5, field `+0x40`,
or field `+0x38`.

## Caller result use

The sole caller owns two DATA/vtable entries (`0x005dc294` and
`0x005dc3a0`). It first short-circuits to **setting** output bit 0 when
`[arg+0xa4]` is live. Otherwise it passes `[arg+0x88]` as the index, then
writes predicate result to that flags dword: TRUE clears bit 0; FALSE sets
bit 0.
This proves only flag polarity and the static bridge; the flag's source
virtual/gameplay name remains unproved.

Exactly **one** inbound rel32 image-wide (`0x00494fc2`) and zero imm32 sites
point to `0x00444f20`.

## Field map pinned by this body

| Offset | Static role | Anchor |
| --- | --- | --- |
| `[ctrl+0x4]` | segment pointer array | direct and alias lookup |
| `[ctrl+0xc]` | root/core segment | both direct calls |
| `[ctrl+0x10]` | owning unit/host | owner-mesh fallback |
| `[ctrl+0x18]` | cached total-health metric | 30% special veto |
| `[ctrl+0x24]` | mode gate that bypasses the special veto when nonzero | `0x00444faa` |
| `[owner+0x30]` | mesh link | fallback path |
| `[mesh-result+0x160]` | indexed metadata pointer array | fallback path |
| `[entry+0x8c]` | required value 5 for alias resolution | `0x00444f72` |
| `[entry+0x98]` | alias metadata pointer | `0x00444f7b` |
| `[entry+0x98]+0x88` | alias segment index | `0x00444f85` |
| `[segment+0x38]` | zero means predicate TRUE | all terminal result paths |
| `[segment+0x40]` | required value 1 for the special veto | `0x00444fbc` |
| segment slot `+0x14` | selector; zero enters special veto | `0x00444fb5` |

### The `+0x88` cooldown question remains open

The nested `[[entry+0x98]+0x88]` load here is an integer segment-array
alias index, not the float expiry written to `[unit+0x88]` by
`CUnit__ResetDamageCooldownTimer`. Receiver provenance and immediate array
indexing (`[ctrl+4][ecx*4]`) distinguish them. A focused whole-function
probe for an x87 `[reg+0x88]` operand in a function also referencing global
time `0x00672fd0` returned zero candidates; that negative heuristic is not
an exhaustive proof of no reader. The per-unit cooldown consumer therefore
stays unresolved.

## Owner callback and latch cross-links

The same constructor chain proves `[ctrl+0x10]` is the owning CBuilding or
CHiveBoss host. Their vtable byte offset `+0xc8` is unit slot 50:
`CBuilding__VFunc_50_00417a40` and
`CHiveBoss__MaybeScheduleEvent1388ForField74_004802f0`, both of which begin
with `CUnit__MarkDestroyedAndCleanupLinks`.

A concrete `[ctrl+0x2c]` consumer is
`CBuilding__VFunc_37_00418100`: latch value 1 suppresses its tail-jump to
`CThing__RenderImposter`. These facts are proved in the sibling cascade and
random-burst notes and are not inferred from this predicate's saved name.

## Pinned-source and rebuild status

No source body exists in the pinned reference drop. The rebuild has no
per-part segment controller or motion bridge, so no Core owner or focused
test was invented. A future implementation must preserve the permissive
missing-metadata returns, alias path, narrow special veto, strict 30%
comparison, and output-bit polarity. It should not model this as a generic
CUnitAI method without new evidence.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00444f20`–`0x0044500c` is not
  `0e79d11c…1e6d83`, or an exit stops using `ret 4`.
- A second rel32 inbound or any imm32 site appears.
- `CDestructableSegmentsMotionController__Ctor` stops storing its argument
  at `motion+0xc`, or the caller stops loading that exact field into ECX.
- The no-direct path stops returning TRUE on absent mesh/entry/alias
  metadata, or the final resolved test leaves `segment+0x38`.
- The special veto's all-core / strict-below-30% polarity changes.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before
  reading. Reproduced target/caller/constructor body hashes, complete target
  disassembly, rel32/imm32 censuses, receiver dataflow, field offsets, and
  output-bit polarity with a read-only PE/capstone reader calibrated against
  the already pinned controller-damage body.
- Cross-checked after measurement against W003 primary A10 and adversarial
  B10. B10's `needs_name` warning is resolved to a concrete controller
  receiver by the constructor/callsite chain; no Ghidra rename was applied.
- Related notes:
  [`CDestructableSegmentsController__TriggerCoreCascadeIfEligible.md`](CDestructableSegmentsController__TriggerCoreCascadeIfEligible.md),
  [`CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold.md`](CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold.md),
  [`../Unit.cpp/CUnit__ResetDamageCooldownTimer.md`](../Unit.cpp/CUnit__ResetDamageCooldownTimer.md).
