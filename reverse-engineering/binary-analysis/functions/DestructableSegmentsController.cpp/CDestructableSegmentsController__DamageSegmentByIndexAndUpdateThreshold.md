# CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold

> Address: `0x00444030`

Status: active static function note
Last updated: 2026-08-22
Source File: none — the reference drop has no `DestructableSegmentsController.cpp`
or `DestroyableSegment.cpp` source body (checked 2026-08-22 against the
main-tree `references/Onslaught/` inventory; the debug-path name survives only
in retail static evidence) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the indexed segment-damage entry of the destroyable-segments
controller — the terminal stage-8 dispatch of
[`CUnit__ApplyDamage`](../Unit.cpp/CUnit__ApplyDamage.md) that replaces
shield/life/bark processing for every segmented unit. Applies slot-3 damage to
the indexed child, warns on a missing part, then fires the owner's vtable
slot `0xc8` through either an all-core-children-destroyed gate or a
30%-of-metric threshold, and latches `[ctrl+0x2c] = 1` once the active-core
sum drops below half the cached metric. 296 bytes; every claim below re-read
from the pristine specimen this wake.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256 verified
before reading) with capstone whole-body disassembly, raw byte reads (body
hashes; float/double/string constant resolution), whole-.text rel32 scans and
image-wide imm32 censuses for every address in the family, and xref-site
ownership resolution against the tracked name table. Cross-checked against
[`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md),
[`function-c1-closure-2026-08-11.tsv`](../../function-c1-closure-2026-08-11.tsv),
and [`../Unit.cpp/CUnit__ApplyDamage.md`](../Unit.cpp/CUnit__ApplyDamage.md).
No `FUN_*` milled; no Core owner changed.

> Address: `0x00444030`

## Contract (byte-exact)

Body `0x00444030`–`0x00444157` inclusive through the complete `ret 0xc` at
`0x00444155`, **296 bytes**, SHA-256
`393ce58690812c3eebaa92dedebd34fcaf159e267a7cb9fc72d28d06c97a3240`.
Frame `sub esp, 8`, saves ebx/ebp/esi/edi. **5 `E8`, 0 `E9`**; all 21
conditional branches (including the two `0f 84` rel32 forms) stay inside the
body. Signature confirmed: `thiscall`, three stack dwords, `ret 0xc`.

Argument map:

| Arg | Meaning | Anchor |
| --- | --- | --- |
| `ecx` | `this` = segments controller (`mov esi, ecx` `0x0044403d`) | throughout |
| stack arg 1 | `int meshPartIndex` (`edi`; `-1` = none) | `cmp edi,-1` `0x0044403a` |
| stack arg 2 | `float amount` (forwarded to slot-3 damage) | pushed twice `0x00444054`–`0x00444060` |
| stack arg 3 | `CThing* source` | forwarded unchanged |

## Stage law (byte-exact)

1. **Index guard** (`0x0044403a`): `meshPartIndex == -1` jumps past all
   damage handling to the threshold epilogue (stage 5) with nothing applied.
2. **Indexed child fetch + missing-part warn** (`0x0044404a`–`0x004440ce`):
   child = `[ctrl+0x4][index]`. If null:
   `CConsole__Printf 0x00441740([0x0066f580], "WARNING: '%s', building part
   not found!!!!!! part = %d" @ .rdata 0x00628614,
   CMesh__GetNameOrUnknown 0x004aa6b0(mesh), index)` — the mesh name comes
   from `[ctrl+0x10]->[+0x30]` vtable slot `+0x24()`; a null there or a null
   result skips the warn. Then fall through to stage 5 without damaging.
3. **Slot-3 damage application** (`0x00444054`–`0x00444062`):
   `child->vtable[+0xc](amount, source)` — the `VFunc_03_ApplyDamage` virtual.
   For the base class this is `0x00442960` (see its own law below); core and
   swap subclasses override at `0x004435f0` / `0x00443780`.
4. **Owner callback through two alternative gates**
   (`0x00444063`–`0x00444099`) — fires `[[ctrl+0x10] vtable+0xc8]()`
   (argument-less) when **either** holds after the damage:
   - `CDestroyableCoreSegment__AreCoreChildrenDestroyed 0x004433f0([ctrl+0xc])`
     returned TRUE (all core children gone), **or**
   - the fresh `SumActiveValueRecursive 0x00442890([ctrl+0xc])` walk is
     strictly **below** `[ctrl+0x18] × 0.3`: x87 sequence
     `fld [ctrl+0x18]; fmul qword [0x005db0a0]` (the double `0.3`,
     `333333333333d33f`), `fstp [esp+0xc]`, then the sum call,
     `fcomp qword [esp+0xc]`, `fnstsw ax`, `test bl,ah` (bl=1 → C0),
     `jne`-style fall-through into the callback — C0 is set only when the
     sum is less than the threshold, so exact equality does not fire. In
     game terms: the owner callback triggers once remaining subtree life
     drops under 30% of the cached metric (unless every core child is
     already gone).
   `[ctrl+0x10]` is now byte-proved as the containing CUnit-derived host.
   The controller constructor has exactly two callers: CBuilding and
   CHiveBoss construction paths pass their host in arg 1, then store the
   returned controller at `[host+0x178]`. Slot `0xc8` is unit slot 50:
   CBuilding vtable `0x005d8eb4` entry `0x005d8f7c` points to
   `CBuilding__VFunc_50_00417a40`; CHiveBoss entry `0x005e17a8` points to
   `CHiveBoss__MaybeScheduleEvent1388ForField74_004802f0`. Both functions
   begin by calling `CUnit__MarkDestroyedAndCleanupLinks`, resolving the
   callback as the concrete host destruction entry for both owners.
5. **Half-metric latch** (`0x004440d1`–`0x0044414d`), reached from stages 1,
   2, and 4: if `[ctrl+0x2c] == 1` already, nothing runs. Two structurally
   identical any-active scans over the array `[ctrl+0x4]`, count
   `[ctrl+0x8]`, testing each non-null child's `[+0x1c] != 0`, bracket the
   comparison; each feeds its own x87 operand with its own fallback:
   - **Scan 1** (`0x004440d6`–`0x004440f9`): any active child found →
     `st0` = fresh `SumActiveValueRecursive` walk (the call at
     `0x00444106`); array empty / no active child / all nulls →
     `st0 = 1.0f` (`fld dword [0x005d8568]`, `0x004440fb`).
   - **Scan 2** (`0x0044410b`–`0x00444136`): same test → `st0` =
     `[ctrl+0x18]`, the cached metric (`fld [esi+0x18]`, `0x00444138`);
     otherwise `st0 = 1.0f` (`0x00444130`).
   - `fmul dword [0x005d85ec]` (`0.5f`) scales the scan-2 choice;
     `fxch` + `fcompp` compare the scan-1 value against it; the store
     `mov [esi+0x2c], 1` at `0x0044414c` executes only when
     scan1 < scan2×0.5 strictly (C0 set; equality does not latch). Because
     both scans read identical array state back-to-back they always agree,
     so the reachable law is simply: **live segments whose summed remaining
     life have fallen below half the cached metric → latch**; the
     all-inactive pairing (`1.0 < 1.0×0.5`) can never fire.
   A concrete reader is now proved: `CBuilding__VFunc_37_00418100` loads
   `[building+0x178]`, returns when `[controller+0x2c] == 1`, and otherwise
   tail-jumps `CThing__RenderImposter 0x004f3710`. Its complete 22-byte body
   hashes `9c4caee0613ad3e46fdf06e763d56bff497fe8290f1be209290d4605d4fbe94a`.
   This proves latch-driven imposter-render suppression for CBuilding; it
   is not an exhaustive consumer census.

## Callees (all five `E8`)

| Site | Callee |
| --- | --- |
| `0x00444066` | `CDestroyableCoreSegment__AreCoreChildrenDestroyed` `0x004433f0` |
| `0x0044407f` | `CDestroyableSegment__SumActiveValueRecursive` `0x00442890` |
| `0x00444106` | `CDestroyableSegment__SumActiveValueRecursive` `0x00442890` |
| `0x004440b9` | `CMesh__GetNameOrUnknown` `0x004aa6b0` |
| `0x004440c9` | `CConsole__Printf` `0x00441740` |

## Callers

Exactly **one** inbound rel32 image-wide: `0x004f9ddc` inside
[`CUnit__ApplyDamage`](../Unit.cpp/CUnit__ApplyDamage.md) stage 8, reached
only when `[unit+0x178]` is live — and that call is terminal for ApplyDamage
(shield/life/bark stages never run for segmented receivers). Zero imm32
sites. This makes the function the sole byte-proven route from unit damage
into the segment subsystem.

Named siblings that call the same helpers (from the xref-site ownership
scan, context only — none reaches this body): `ApplyRandomDamageBurstAndUpdateThreshold 0x00444160`,
`GetCurrentSubtreeHealthIfAnyActive 0x00444330`,
`TriggerCoreCascadeIfEligible 0x004443f0`,
`CUnitAI__CanUseIndexedSegmentEntry 0x00444f20`.

## Pinned-source status

Absent. No segment-class source body exists in the drop; the static-contract
document records the debug path name only. Architecture shape agrees with the
sealed c1-closure row (below).

## Prior-art status recorded by this note

- `function-c1-closure-2026-08-11.tsv` seals this address as
  `OPAQUE → SEALED_STATIC_RECEIPT` over exactly this range and byte count
  (296 bytes, 107 instructions counted there). Its `bodyDigest` column does
  not reproduce under raw body-byte SHA-256 — verified against
  [`CUnit__ApplyDamage`](../Unit.cpp/CUnit__ApplyDamage.md), whose
  independently hashed body also differs from its TSV digest — so the column
  is a different convention, not a contradiction; range, size, and identity
  corroborate exactly.
- The destroyable-segments contract's controller-dispatch row ("indexed
  controller entry … tied to controller threshold/callback state") is
  confirmed and made concrete: threshold = metric × {0.3 fire-or-wait,
  0.5 latch}, callback = vtable slot `0xc8` on `[ctrl+0x10]`.
- The base slot-3 implementation `0x00442960`–`0x00442996` (55 bytes,
  SHA-256
  `762a57856ec1f0db040b97154578973941e1ae0d1b752b16307db41c980f072c`)
  subtracts the amount from `[child+0xc]`, records
  `[child+0x14] = [0x00672fd0]` (the same global time snapshot the damage-
  cooldown writer reads) and `[child+0x18] = amount`, then clamps a
  below-zero `[child+0xc]` to `0.0f` (`[0x005d856c]`). Its single imm32 is
  the vtable-slot entry at `0x005db038` = `[0x005db02c + 0xc]`, matching the
  `mov dword [esi], 0x5db02c` vptr store in the `0x0044350f` constructor —
  independent confirmation that `+0xc` is the slot-3 damage virtual.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x4]` | segment pointer array | indexed fetch `0x0044404a`, both scans |
| `[this+0x8]` | segment count | loop bounds `0x004440d6`, `0x0044410b` |
| `[this+0xc]` | root/core segment handed to gates and sums | `0x00444063`, `0x00444103` |
| `[this+0x10]` | owning CBuilding/CHiveBoss host receiving unit slot-50 (`+0xc8`) destruction call | constructor/caller/vtable provenance; `0x0044408e` |
| `[this+0x18]` | cached health metric (seeded at init from `GetTotalHealth`, see [`GetTotalHealth`](CDestroyableSegment__GetTotalHealth.md)) | thresholds `0x0044406f`, `0x00444138` |
| `[this+0x2c]` | half-metric latch (one-shot); value 1 suppresses CBuilding slot-37 imposter render path | test `0x004440d1`, store `0x0044414c`, reader `0x0041810a` |
| child `[+0xc]` | remaining segment life | base slot-3 body |
| child `[+0x14]` | last-damage time (global snapshot) | base slot-3 body |
| child `[+0x18]` | last-damage amount | base slot-3 body |
| child `[+0x1c]` | active flag tested by both scans | `0x004440ea`, `0x0044411f` |

Field names above are functional roles read off this body plus its callees;
retail symbol names beyond the saved name table remain unproven and nothing
here renames a saved Ghidra symbol.

## Constants

| Address | Bytes | Value |
| --- | --- | --- |
| `0x005db0a0` | `333333333333d33f` | double `0.3` (fire-gate fraction of metric) |
| `0x005d85ec` | `0000003f` | float `0.5` (latch fraction of metric) |
| `0x005d8568` | `0000803f` | float `1.0` (no-active-comparison filler) |
| `0x005d856c` | `00000000` | float `0.0` (life ≠ 0 contributor test, callee) |
| `0x00628614` | — | `"WARNING: '%s', building part not found!!!!!! part = %d"` |
| `0x006285bc` | — | `"Warning: First core part has no children"` (callee string) |

## Rebuild mapping

No Core owner changes this wake. The rebuild has no per-part segment model;
`rebuild/OnslaughtRebuild.Core/Level100Destruction.cs` consumes segmented
units only through their observed aggregate outcome, which this body explains
at the mechanism level: once `[unit+0x178]` is live, ApplyDamage terminates
in this dispatcher and the shared shield/life/bark code never executes.
Focused tests correctly deferred until a Core owner models segments.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00444030`–`0x00444157` is not
  `393ce586…97a3240`, or the final instruction is anything but
  `c2 0c 00` at `0x00444155`.
- A second rel32 inbound to `0x00444030` appears, or any imm32 of it.
- The stage-4 multiplier stops being `fmul qword [0x005db0a0]` with
  `0x005db0a0` = `333333333333d33f` (double 0.3), or the latch multiplier
  stops being `fmul dword [0x005d85ec]` with `0x005d85ec` = `0000003f`.
- Either sum call stops targeting `0x00442890`, or the warn format string
  leaves `.rdata 0x00628614`.

## Receipts

- 2026-08-22 — pristine specimen
  (`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, main tree),
  SHA-256 verified before reading. Tools (this wake, rebuilt scratch):
  `local-lab/unitdmg-r698/bealib.py` (PE reader + capstone disassembly +
  hashes), `probe_444030.py` / `probe_family.py` / `probe_final.py` /
  `probe_call.py` (body censuses, constant resolution, xref-site ownership,
  call-target confirmation `e8 85 e7 ff ff` → `0x00442890`),
  `calibrate.py` (reader reproduced the pinned 2,586-byte ApplyDamage hash
  exactly before any new claim was recorded).
- Cross-references (same wake):
  [`../../destroyable-segments-static-contract.md`](../../destroyable-segments-static-contract.md)
  (controller-dispatch row, corroborated not superseded),
  [`../Unit.cpp/CUnit__ApplyDamage.md`](../Unit.cpp/CUnit__ApplyDamage.md)
  (terminal stage-8 caller),
  [`CDestroyableSegment__SumActiveValueRecursive.md`](CDestroyableSegment__SumActiveValueRecursive.md),
  [`CDestroyableCoreSegment__AreCoreChildrenDestroyed.md`](CDestroyableCoreSegment__AreCoreChildrenDestroyed.md),
  [`CDestroyableSegment__GetTotalHealth.md`](CDestroyableSegment__GetTotalHealth.md).
- 2026-08-22 continuation — resolved both carried controller questions from
  pristine bytes: constructor callers at `0x00417223` / `0x0047fe99`,
  CBuilding/HiveBoss slot-50 entries `0x005d8f7c` / `0x005e17a8`, and
  latch reader `CBuilding__VFunc_37_00418100` (22-byte hash above). See
  [`CDestructableSegmentsController__TriggerCoreCascadeIfEligible.md`](CDestructableSegmentsController__TriggerCoreCascadeIfEligible.md)
  for the complete callback/cascade chain.
