# CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold

> Address: `0x00444160`

Status: active static function note
Last updated: 2026-08-22
Source File: none — the reference drop has no `DestructableSegmentsController.cpp`
source body (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the segmented-unit arm of
`CUnit__ApplyRandomDestructibleDamageBurst`: deduplicates the controller's
segment array into a temporary `CSPtrSet`, gives each unique segment whose
slot-5 selector is greater than one an independent 50% chance of receiving
`100000.0f` through damage slot 3, then refreshes the controller's
below-half-health one-shot latch. The slot-3 source argument is the owning
unit at `[ctrl+0x10]`. 367 bytes; every load-bearing claim below was re-read
from the pristine specimen this wake.
Evidence: MEASURED — pristine SHA verified before capstone whole-body
instruction decoding, raw body hashing, whole-`.text` rel32 scans,
image-wide imm32 censuses, caller-window reads, and controller-constructor
provenance. Broad TTD opening coverage is cited only as noncausal
corroboration. No `FUN_*` was a first gate; no Core owner changed.

## Contract (byte-exact)

Body `0x00444160`–`0x004442ce` inclusive through the complete plain `ret`,
**367 bytes / 134 instructions**, SHA-256
`d113f98a44513f01da283be287af827b956ec79d6ba32ec2116751171214ad96`.
SEH-framed (`push -1`, scope record `0x005d2158`), `sub esp,0x10`, saves
EBX/ESI/EDI. **6 direct `E8`, 0 `E9`**; all conditional branches stay
inside the body. Signature is `void __thiscall ...(void *this)`: ECX is
saved as controller EBX, no stack arguments are read, and the exit is a
plain `ret`.

## Stage law (byte-exact)

1. **Temporary-set init** (`0x0044417d`–`0x00444185`): construct an empty
   `CSPtrSet` at stack local `[esp+0xc]` through `CSPtrSet__Init`.
2. **Array deduplication** (`0x00444186`–`0x004441c4`): walk
   `[ctrl+0x4][0 .. count-1]`, where count is `[ctrl+0x8]`. Null entries
   are skipped. For each non-null pointer, call `CSPtrSet__Contains`; only
   a miss is passed to `CSPtrSet__AddToTail`. The `cmp index,-1` at
   `0x00444197` is unreachable from the zero-seeded incrementing loop and
   changes no live iteration.
3. **Independent random burst per unique segment**
   (`0x004441c6`–`0x0044422c`): walk the temporary set. For each segment:
   - call its vtable byte offset `+0x14` (slot 5); values `<= 1` skip it;
   - otherwise call `Random__NextLCGAbs` with global RNG object
     `[0x008a9d9c]` and normalize the signed remainder modulo two through
     `and eax,0x80000001` plus the negative fixup;
   - remainder zero calls segment vtable byte offset `+0x0c` (slot 3) as
     `ApplyDamage(100000.0f, [ctrl+0x10])`. The immediate
     `0x47c35000` is exactly float `100000.0f`; the owning unit is the
     source pointer. Remainder one leaves that segment unchanged.

   The selector's source virtual name is not proved; this note intentionally
   says only "slot-5 selector". The random decision is made inside the set
   loop, so eligible unique segments do not share one draw.
4. **Below-half latch refresh** (`0x0044422e`–`0x004442a9`): if
   `[ctrl+0x2c] == 1`, skip the refresh. Otherwise two identical scans of
   the original segment array test whether any non-null child has
   `[child+0x1c] != 0`:
   - scan 1 selects fresh
     `CDestroyableSegment__SumActiveValueRecursive([ctrl+0xc])`, or
     fallback `1.0f` when no active segment exists;
   - scan 2 selects cached metric `[ctrl+0x18]`, or the same `1.0f`
     fallback, then multiplies by `0.5f` from `0x005d85ec`.

   `fcompp` / C0 (`test ah,1`) stores `[ctrl+0x2c] = 1` only when the
   fresh sum is strictly below half the cached metric. Equality does not
   latch. Because the scans inspect the same state back-to-back, their
   fallback pairing cannot latch (`1.0 < 0.5` is false).
5. **Set cleanup / SEH restore** (`0x004442ac`–`0x004442ce`):
   `CSPtrSet__Clear` releases the temporary nodes, then the function
   restores FS and returns.

## Direct callees

| Site | Callee / role |
| --- | --- |
| `0x00444181` | `CSPtrSet__Init 0x004e5840` |
| `0x004441ab` | `CSPtrSet__Contains 0x004e5c30` |
| `0x004441b9` | `CSPtrSet__AddToTail 0x004e5b20` |
| `0x004441f2` | `Random__NextLCGAbs 0x004de8d0` |
| `0x00444263` | `CDestroyableSegment__SumActiveValueRecursive 0x00442890` |
| `0x004442b8` | `CSPtrSet__Clear 0x004e5c60` |

Indirect calls are segment slot 5 at `0x004441e5` and damage slot 3 at
`0x00444212`.

## Caller

Exactly **one** inbound rel32 image-wide and zero imm32 sites:
`0x004f943e` inside
`CUnit__ApplyRandomDestructibleDamageBurst 0x004f9430`. That caller loads
`[unit+0x178]`; a live controller takes this body, while a null controller
uses the caller's ordinary unit-life random-damage path. The caller body is
`0x004f9430`–`0x004f9481`, 82 bytes, SHA-256
`593dc455cb5a86bc861db640c00c0259f015fa717191b9c4c5d274d7f6328a46`.
Its sole inbound call is Mission native `IScript__HalfDestroy` at
`0x00534379`.

## Owner and latch provenance resolved this wake

`[ctrl+0x10]` is no longer an unknown generic object. The controller
constructor `0x00443fc0` stores stack arg 1 to `this+0x10` and has exactly
two callers:

- `CBuilding__VFunc_9_00417190` at `0x00417223` passes the building in ESI
  as arg 1, then stores the returned controller to `[building+0x178]`;
- `CHiveBoss__Init` at `0x0047fe99` passes the HiveBoss in ESI the same
  way and stores the result to `[hiveBoss+0x178]`.

Thus the burst's slot-3 source is the controller-owning CUnit-derived host,
not a controller/config object.

A concrete reader of the one-shot latch is also byte-proved:
`CBuilding__VFunc_37_00418100` loads `[building+0x178]`, and when live
compares `[controller+0x2c]` with 1. Equality returns immediately; otherwise
it tail-jumps `CThing__RenderImposter 0x004f3710`. Its complete 22-byte
body `0x00418100`–`0x00418115` hashes
`9c4caee0613ad3e46fdf06e763d56bff497fe8290f1be209290d4605d4fbe94a`.
This proves one consumer and its render-suppression effect; it does not prove
that no other consumer exists.

## Field map pinned by this body

| Offset | Static role | Anchor |
| --- | --- | --- |
| `[ctrl+0x4]` | segment pointer array | dedupe and both active scans |
| `[ctrl+0x8]` | array count | loop bounds |
| `[ctrl+0xc]` | root segment for recursive sum | `0x00444260` |
| `[ctrl+0x10]` | owning CBuilding/CHiveBoss host; damage source | ctor provenance + `0x00444205` |
| `[ctrl+0x18]` | cached total-health metric | second comparison operand |
| `[ctrl+0x2c]` | one-shot below-half latch | guard/store; CBuilding slot-37 reader |
| segment slot `+0x14` | selector; only values >1 enter RNG gate | `0x004441e5` |
| segment slot `+0x0c` | `ApplyDamage(float,source)` | `0x00444212` |
| `[segment+0x1c]` | active flag | both comparison scans |

## Runtime corroboration boundary

TTD deep-mine batches 3 and 4 report coverage of this named body during
bounded level-opening captures (`680 B` aggregate in batch 3 and `340 B`
in batch 4's report convention). That proves execution somewhere in those
captures only; it does not identify which segment, selector value, random
outcome, amount, or latch transition occurred.

## Pinned-source and rebuild status

No source body exists in the pinned reference drop. The rebuild has no
per-part destroyable-segment model, so no Core owner or focused parity test
was invented. A future owner must preserve unique-pointer dedupe, per-segment
random draws, the slot-5 eligibility gate, owner-as-source forwarding, and
the strict below-half latch.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00444160`–`0x004442ce` is not
  `d113f98a…14ad96`, or the last instruction is not plain `c3`.
- The body has an inbound rel32 other than `0x004f943e`, or any imm32
  reference appears.
- The damage immediate stops being `0x47c35000` (float `100000.0f`), the
  source push stops loading `[ctrl+0x10]`, or the indirect call leaves
  slot byte offset `+0x0c`.
- The latch multiplier at `0x005d85ec` stops being float `0.5f`, or the
  strict C0 store at `0x004442a9` changes polarity.
- `CBuilding__VFunc_37_00418100` stops reading
  `[building+0x178]->[+0x2c]` before its render-imposter tail path.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before
  reading. Reproduced with the read-only PE/capstone helper calibrated
  against the already pinned `0x00444030` body hash; whole-body hash,
  calls, rel32/imm32 censuses, constructor callsites, and latch-reader body
  were then re-read independently.
- Corroboration only:
  `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/batch-3.md`
  and `batch-4.md`.
- Related byte contracts:
  [`CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold.md`](CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold.md),
  [`CDestroyableSegment__SumActiveValueRecursive.md`](CDestroyableSegment__SumActiveValueRecursive.md),
  [`../Unit.cpp/CUnit__ApplyDamage.md`](../Unit.cpp/CUnit__ApplyDamage.md).
