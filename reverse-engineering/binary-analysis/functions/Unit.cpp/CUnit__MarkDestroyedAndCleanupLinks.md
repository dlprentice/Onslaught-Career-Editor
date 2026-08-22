# CUnit__MarkDestroyedAndCleanupLinks

> Address: `0x004FD140`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `Unit.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the shared CUnit teardown transition. It returns 0 when TF_DYING is
already set; otherwise it stops the unit's sounds, sets TF_DYING, adjusts two
profile-type counter/weight families when mode is 0 or 1, triggers the optional
destroyable-segment catch-up cascade, fires script event-id 5, clears an active
reader, drains a linked pointer set through each object's slot 2, and returns 1.
It is the direct slot-50 body for CUnit/CRadar/CSubmarine and the first call in
the proved CBuilding and CHiveBoss slot-50 overrides.
Evidence: MEASURED — pristine SHA verified before complete capstone body
decode and hash, whole-`.text` rel32 scan, image-wide imm32 census, complete
outbound-call classification, and direct caller/vtable reads. Prior segment
notes are cross-linked, not counted as new proof. No `FUN_*` was a first gate;
no Ghidra or rebuild owner changed.

## Contract (byte-exact)

Body `0x004fd140`–`0x004fd225` inclusive through the complete plain `ret`,
**230 bytes / 71 instructions**, SHA-256
`e46dc856ae589724b790f97c4232a8675fa3d96d078d2b9abf09883a1a56ccb8`.
It saves ESI, and EDI only around the final set drain. It has **7 outbound
direct `E8`, 0 `E9`**, plus one indirect object call at byte offset `+0x08`.
All direct and short branches remain inside the body. Signature shape is
`int __thiscall ...(CUnit *unit)`: no stack arguments are read; EAX is 0 for
an already-dying receiver and 1 after a newly completed transition.

The seven outbound direct calls are distinct from the **nine inbound** rel32
calls listed below. Older prose that said “nine direct E8s” conflated those two
counts.

## Stage law (byte-exact)

1. **One-shot guard** (`0x004fd143`–`0x004fd14c`): test byte bit `0x04` in
   `[unit+0x2c]`. If already set, return 0 without any cleanup. This bit is the
   source-aligned TF_DYING bit pinned by the existing CComplexThing family.
2. **Sound stop and transition mark** (`0x004fd14d`–`0x004fd161`): call
   `CSoundManager__KillSamplesForThing(0x00896988, unit)`, then OR TF_DYING
   into `[unit+0x2c]`.
3. **Optional profile/mode accounting** (`0x004fd162`–`0x004fd1d1`): when
   `[unit+0x164]` is live, inspect mode `[unit+0x138]`:
   - mode 1 decrements `[0x00855228 + profile[+0xe0]*4]`, obtains the integer
     type weight from `CUnit__GetTypePriorityWeight 0x00511510(profile)`, and
     adds that weight to global `[0x008a9b8c]`;
   - mode 0 decrements `[0x008551c0 + profile[+0xe0]*4]`, obtains the same
     weight, negates it, and adds it to the global (therefore subtracting the
     weight);
   - any other mode skips the counter, weight, and following flag write.

   Both mode-0 and mode-1 paths OR byte bit 0 into `[unit+0x2d]`. A null
   profile skips this entire stage.
4. **Destroyable-segment catch-up** (`0x004fd1d2`–`0x004fd1e0`): when
   `[unit+0x178]` is live, call
   `CDestructableSegmentsController__TriggerCoreCascadeIfEligible`
   `0x004443f0`. The cascade's two vetoes, activation-before-damage order,
   and final latch are owned by its existing byte contract.
5. **Started-dying script event** (`0x004fd1e1`–`0x004fd1ec`): when the
   attached script `[unit+0x74]` is still live, call
   `IScript__CallEventId5_OrReset 0x00533660`. That wrapper passes immediate
   event id 5 to `CScriptObjectCode__CallEvent`, except for its separately
   pinned global reset-mode arm. The event occurs after the segment cascade.
6. **Active-reader clear** (`0x004fd1ed`–`0x004fd1fa`): call
   `CGenericActiveReader__SetReader` on embedded reader `[unit+0x144]` with
   null.
7. **Linked-set drain** (`0x004fd1fb`–`0x004fd21d`): repeatedly take the
   current first object from the `CSPtrSet` at `[unit+0x18c]`, remove it with
   `CSPtrSet__Remove`, then invoke that object's virtual byte offset `+0x08`
   (slot 2). A null set head or null first object ends the loop.
8. Set EAX to 1 and return.

This body never reads `[unit+0x88]`; it does not resolve the separate damage-
cooldown expiry-reader question.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x004fd153` | `CSoundManager__KillSamplesForThing 0x004e1130` |
| `0x004fd190` | `CUnit__GetTypePriorityWeight 0x00511510` (mode 1) |
| `0x004fd1b6` | `CUnit__GetTypePriorityWeight 0x00511510` (mode 0) |
| `0x004fd1dc` | `CDestructableSegmentsController__TriggerCoreCascadeIfEligible 0x004443f0` |
| `0x004fd1e8` | `IScript__CallEventId5_OrReset 0x00533660` |
| `0x004fd1f6` | `CGenericActiveReader__SetReader 0x00401000` |
| `0x004fd210` | `CSPtrSet__Remove 0x004e5bd0` |
| `0x004fd219` | indirect object slot 2 (`vtable+0x08`) after removal |

## Inbound rel32 census

Exactly **nine** whole-`.text` inbound calls:

| Site | Current name-table owner |
| --- | --- |
| `0x00403693` | `CAirUnit__ReleaseAllAttachedParticleNodes` |
| `0x00417a61` | `CBuilding__VFunc_50_00417a40` |
| `0x00428822` | `CComponent__HandleTriggerEventAndMoveToOffset` |
| `0x0042883e` | `CComponent__HandleTriggerEventAndMoveToOffset` |
| `0x0047ce83` | `CGroundUnit__MarkDestroyedAndResetState` |
| `0x004802f4` | `CHiveBoss__MaybeScheduleEvent1388ForField74_004802f0` |
| `0x004d38c3` | `CPod__TryDestroyedCleanupAndResetDeploymentGraph` |
| `0x004dfce3` | `CSimpleBuilding__TryActivateAndEnableShadows` |
| `0x004f1059` | `CTentacle__VFunc_50_004f1050` |

The CBuilding and CHiveBoss entries are the two controller-host overrides
already proved by the preceding segment slice: their slot-50 functions call
this body first, then perform class-specific follow-up only when it returns 1.
This note does not re-claim their previously pinned body boundaries.

## Direct vtable entries

The image-wide imm32 census has exactly three dwords, all byte offset `+0xc8`
(slot 50):

| Entry | Vtable / class |
| --- | --- |
| `0x005dd850` | `0x005dd788` / CRadar |
| `0x005dfa60` | `0x005df998` / CUnit |
| `0x005e1558` | `0x005e1490` / CSubmarine |

CBuilding and CHiveBoss override slot 50 with `0x00417a40` and `0x004802f0`;
their direct calls above are how those classes enter this shared transition.

## Field map pinned by this body

| Offset | Static role | Anchor |
| --- | --- | --- |
| `[unit+0x2c]` bit `0x04` | TF_DYING one-shot guard/store | entry and `0x004fd15e` |
| `[unit+0x2d]` bit `0x01` | mode-0/1 teardown flag | `0x004fd1ce` |
| `[unit+0x74]` | attached IScript link | event-id 5 stage |
| `[unit+0x138]` | accounting mode; only 0/1 are handled | branch at `0x004fd16c` |
| `[unit+0x144]` | embedded active reader cleared to null | `0x004fd1f0` |
| `[unit+0x164]` | profile/type record pointer | accounting stage |
| `[profile+0xe0]` | counter index and type-weight selector | both accounting arms |
| `[unit+0x178]` | optional destroyable-segments controller | cascade stage |
| `[unit+0x18c]` | pointer set drained during final cleanup | loop at `0x004fd201` |

## Pinned-source and rebuild status

No `Unit.cpp` source body survives in the pinned drop. Existing rebuild
consumers cite this function only as the retail destruction/removal owner; no
new aggregate or per-segment behavior was invented. Any future implementation
must preserve the one-shot return value, cascade-before-script ordering, and
remove-before-slot-2 ordering.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x004fd140`–`0x004fd225` is not
  `e46dc856…56ccb8`, or the final instruction stops being plain `ret`.
- The inbound census is not nine rel32 calls plus the three slot-50 dwords
  above.
- The body no longer has seven outbound direct `E8`, or the cascade leaves
  callsite `0x004fd1dc`.
- TF_DYING no longer gates every side effect, event id 5 moves before the
  segment cascade, or the set object is no longer removed before slot 2.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before
  reading. Complete target disassembly and hash, seven outbound calls, nine
  inbound rel32 calls, three vtable imm32 sites, event/cascade ordering, and
  final drain loop reproduced with the read-only PE/capstone probe.
- Related contracts:
  [`../DestructableSegmentsController.cpp/CDestructableSegmentsController__TriggerCoreCascadeIfEligible.md`](../DestructableSegmentsController.cpp/CDestructableSegmentsController__TriggerCoreCascadeIfEligible.md),
  [`../IScript__CallEventId5.cpp/IScript__CallEventId5_OrReset.md`](../IScript__CallEventId5.cpp/IScript__CallEventId5_OrReset.md).
