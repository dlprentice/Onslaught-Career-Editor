# CDestructableSegmentsController__TriggerCoreCascadeIfEligible

> Address: `0x004443f0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — the reference drop has no `DestructableSegmentsController.cpp`
source body (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the segmented-unit death-cleanup cascade. It no-ops when every core
child is already destroyed or active subtree health is strictly below 30%
of the cached metric. Otherwise it marks the root subtree active, applies
`100000.0f` to each immediate child through damage slot 3 using the root's
controller/config source, and sets the controller latch. Sole caller is
`CUnit__MarkDestroyedAndCleanupLinks`. 84 bytes; every claim below was
re-read from the pristine specimen this wake.
Evidence: MEASURED — pristine SHA verified before capstone whole-body
instruction decoding, raw body and helper hashing, whole-`.text` rel32
scans, image-wide imm32 censuses, callsite-window reads, constant decoding,
and owner/vtable provenance. No `FUN_*` was a first gate; no Core owner
changed.

## Contract (byte-exact)

Body `0x004443f0`–`0x00444443` inclusive through the complete plain `ret`,
**84 bytes / 25 instructions**, SHA-256
`f672d7d17a00de73a201092f45036f206c360212b1ba5cc43cf64df0f65c017a`.
Frame `sub esp,8`, saves ESI. **4 direct `E8`, 0 `E9`**, two conditional
branches, both internal. Signature is
`void __thiscall ...(void *this)`: ECX is the segments controller, there are
no stack arguments, and the exit is a plain `ret`.

## Stage law (byte-exact)

1. **Already-destroyed veto** (`0x004443f6`–`0x00444401`): call
   `CDestroyableCoreSegment__AreCoreChildrenDestroyed([ctrl+0xc])`.
   Return value exactly 1 jumps to the epilogue; no activation, damage, or
   latch write occurs.
2. **Below-30% veto** (`0x00444403`–`0x00444421`): compute double
   threshold `[ctrl+0x18] * 0.3` using qword constant `0x005db0a0`, then
   call `CDestroyableSegment__SumActiveValueRecursive([ctrl+0xc])`.
   `fcomp` / C0 (`test ah,1`) returns when the fresh sum is **strictly
   below** the threshold. Equality and greater-than continue.
3. **Recursive activation** (`0x00444423`–`0x0044442a`): call
   `CDestructableSegment_T3_00442a80([ctrl+0xc])`. That 51-byte helper
   stores `[segment+0x1c] = 1`, then recursively repeats over every child
   in the `CSPtrSet` at `segment+0x24`.
4. **Catch-up damage fan-out** (`0x0044442b`–`0x00444437`): push immediate
   `0x47c35000` (float `100000.0f`) and call
   `CDestroyableSegment__PropagateDamageToChildren([ctrl+0xc], amount)`.
   The callee has one stack argument (`ret 4`). For each immediate child of
   the root, it calls damage slot 3 with that amount and source
   `[[root+0x3c]+0x10]`. This instruction read resolves the older
   decompiler's `unaff_ESI` / invented-extra-argument uncertainty: the
   cascade passes exactly one dword to the helper.
5. **Latch** (`0x00444438`): store `[ctrl+0x2c] = 1`, then return.

The positive law is therefore exact: cascade only when core children are
not all destroyed **and** fresh active health is at least 30% of the cached
metric. The body is invoked during unit teardown, not ordinary indexed
segment damage.

## Direct callees

| Site | Callee / role |
| --- | --- |
| `0x004443f9` | `CDestroyableCoreSegment__AreCoreChildrenDestroyed 0x004433f0` |
| `0x00444413` | `CDestroyableSegment__SumActiveValueRecursive 0x00442890` |
| `0x00444426` | `CDestructableSegment_T3_00442a80` — recursively set active flag 1 |
| `0x00444433` | `CDestroyableSegment__PropagateDamageToChildren 0x00442ac0` — one float argument |

## Caller and ordering

Exactly **one** inbound rel32 image-wide and zero imm32 sites:
`0x004fd1dc` inside
`CUnit__MarkDestroyedAndCleanupLinks 0x004fd140`. That 230-byte caller
hashes
`e46dc856ae589724b790f97c4232a8675fa3d96d078d2b9abf09883a1a56ccb8`.
It first rejects an already-marked unit, unlinks the unit, sets the unit's
destroyed bit, and performs optional profile/count teardown. It then loads
`[unit+0x178]`; a live controller calls this cascade. Only afterwards does
it process the unit's event-5 script link and remaining cleanup lists.

This establishes the function as a death-path segment catch-up, not the
30% owner-callback path inside ordinary indexed damage. The ordinary path
is documented in
[`CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold.md`](CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold.md).

## Controller owner and callback slot resolved this wake

The controller constructor `0x00443fc0` stores arg 1 to `[ctrl+0x10]` and
has exactly two rel32 callers. `CBuilding__VFunc_9_00417190` passes the
building in ESI and stores the controller at `[building+0x178]`;
`CHiveBoss__Init` does the same for the HiveBoss. Therefore the controller
owner is the containing CUnit-derived host, with two concrete classes in
this image.

The owner's virtual byte offset `+0xc8` used by ordinary controller damage
is slot 50 in both host vtables:

- CBuilding vtable `0x005d8eb4` entry `0x005d8f7c` points to
  `CBuilding__VFunc_50_00417a40`. That function begins by calling
  `CUnit__MarkDestroyedAndCleanupLinks`, so its controller path reaches
  this cascade.
- CHiveBoss vtable entry `0x005e17a8` points to
  `CHiveBoss__MaybeScheduleEvent1388ForField74_004802f0`. Its complete
  66-byte body hashes
  `97dfac69c4ae326b509e66edc15f1d5741b657b729681bce00682b2d82bb0a3c`;
  it likewise first calls `CUnit__MarkDestroyedAndCleanupLinks`, then, on
  success and a live `[unit+0x74]`, schedules event `0x1388`.

Thus slot `+0xc8` is not an unknown arbitrary callback: for both proved
controller owners it is their unit slot-50 destruction entry. On entry from
ordinary segment damage after the all-core or below-30% gate, its nested
cascade call immediately takes one of this function's two vetoes, avoiding
a second catch-up fan-out.

## Latch consumer resolved this wake

`CBuilding__VFunc_37_00418100` is a concrete `[ctrl+0x2c]` reader. It loads
`[building+0x178]`; when the controller is live and its latch equals 1, the
function returns. Otherwise it tail-jumps
`CThing__RenderImposter 0x004f3710`. The complete 22-byte body hashes
`9c4caee0613ad3e46fdf06e763d56bff497fe8290f1be209290d4605d4fbe94a`.
This proves latch-driven imposter-render suppression for CBuilding; it does
not prove an exhaustive consumer census.

## Field and constant map

| Offset / value | Static role | Anchor |
| --- | --- | --- |
| `[ctrl+0xc]` | root/core segment | all four direct calls |
| `[ctrl+0x10]` | owning CBuilding/CHiveBoss host | constructor provenance |
| `[ctrl+0x18]` | cached total-health metric | 30% comparison |
| `[ctrl+0x2c]` | cascade/below-half one-shot latch | final store; CBuilding reader |
| `[root+0x24]` | child set | recursive activation and fan-out helpers |
| `[root+0x3c]+0x10` | source forwarded to child damage slot 3 | `PropagateDamageToChildren` |
| `0x005db0a0` | qword double `0.3` | threshold multiply |
| immediate `0x47c35000` | float `100000.0f` | catch-up damage amount |

## Pinned-source and rebuild status

No source body exists in the pinned reference drop. The rebuild has no
per-part segment tree or controller, so no Core owner or focused test was
invented. A future implementation must preserve the two vetoes, their
strict/equality polarity, activation-before-damage ordering, immediate-child
fan-out source, and final latch store.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x004443f0`–`0x00444443` is not
  `f672d7d1…5c017a`, or the last instruction is not plain `c3`.
- A second rel32 inbound appears, the caller is not `0x004fd1dc`, or any
  imm32 site appears.
- `AreCoreChildrenDestroyed == 1` or fresh sum `< cached*0.3` stops
  reaching the no-op epilogue.
- The helper at `0x00442ac0` stops ending in `ret 4`, or the caller pushes
  anything other than the single immediate `0x47c35000`.
- CBuilding/HiveBoss slot-50 entries stop resolving to `0x00417a40` /
  `0x004802f0`, respectively.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before
  reading. Reproduced body/hash/call/xref/constant facts and helper arity
  with a read-only PE/capstone reader calibrated against the already pinned
  controller-damage body.
- Cross-checked against prior sealed W003 plates only after the byte read;
  the byte read resolves W003's recorded `unaff_ESI` arity uncertainty.
- Related notes:
  [`CDestroyableCoreSegment__AreCoreChildrenDestroyed.md`](CDestroyableCoreSegment__AreCoreChildrenDestroyed.md),
  [`CDestroyableSegment__SumActiveValueRecursive.md`](CDestroyableSegment__SumActiveValueRecursive.md),
  [`CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold.md`](CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold.md).
