# CBuilding__VFunc_50_00417a40

> Address: `0x00417A40`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `Building.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: CBuilding's slot-50 destruction override. It first delegates the
one-shot TF_DYING transition to `CUnit__MarkDestroyedAndCleanupLinks`; a 0
result returns 0 without any building-specific work. On a fresh transition it
releases child units. A live destroyable-segments controller then suppresses
the building explosion/particle branch; otherwise the body creates and
initializes a configured explosion, writes `-1.0f` to `[building+0xf8]`, emits
one optional configured particle effect and 40 `Generic Mesh` effects. Both
success arms optionally schedule event `0x1388` for the building on the next
frame and return 1.
Evidence: MEASURED — pristine SHA verified before complete-body disassembly
and hashing, whole-`.text` rel32 scan, image-wide imm32 census, RTTI reads,
complete outbound-call classification, and bounded shadow-path context. The
current saved address-qualified name is retained; no Ghidra or rebuild owner
changed.

## Contract (byte-exact)

Body `0x00417a40`–`0x00417de5` inclusive through the complete plain `ret`,
**934 bytes / 252 instructions**, raw SHA-256
`5d6c0aafecde6de89a12074adf221684f29124bda2a920b29710849cfd30804f`.
It has an SEH prologue, a `0x418`-byte local frame, **17 outbound direct `E8`,
0 outbound `E9`**, and two indirect calls. All conditional and direct
unconditional branches remain inside the body. Signature shape is
`int __thiscall ...(CBuilding *building)`: no stack arguments are read. EAX is
the shared cleanup's 0 on the already-dying arm and explicit 1 after every
fresh-transition arm.

## Stage law (byte-exact)

1. **Shared one-shot gate** (`0x00417a61`–`0x00417a68`): call
   [`CUnit__MarkDestroyedAndCleanupLinks`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
   If it returns 0, jump directly to the epilogue. Therefore no child release,
   field write, explosion, particle effect, or event below repeats.
2. **Child release** (`0x00417a6e`): on a fresh transition, call
   `CUnit__ReleaseChildUnits 0x004fcfe0` before inspecting the building's
   controller.
3. **Controller split** (`0x00417a75`–`0x00417a7f`): if
   `[building+0x178]` is live, jump to the event stage at `0x00417da3`. This
   suppresses every stage from configured explosion creation through all 40
   generic effects. The shared cleanup has already called the controller's
   eligible core-cascade path before this wrapper receives 1.
4. **Configured explosion** (`0x00417a85`–`0x00417b67`, null-controller arm):
   - read index `[building+0x164]+0xe8` and pass it to
     `CWorldPhysicsManager__CreateExplosion 0x0050ff10`;
   - construct a stack `CInitThing`, then install vtable `0x005d8c80`. Its
     Complete Object Locator resolves strict RTTI `CExplosionInitThing`;
   - walk the explosion-definition list at global `[0x008553f8]` to the same
     index, store that record in the init context, copy the building's four
     dwords at `+0x1c`, and copy `[building+0x138]` into the context;
   - when the factory result is non-null, call its virtual byte offset `+0x24`
     (slot 9, the already pinned `CExplosion::Init` dispatch) with that context.

   A null factory result skips only the virtual initializer. The function still
   executes the remaining null-controller stages.
5. **Building field write** (`0x00417b6a`): set `[building+0xf8]` to exact
   float `-1.0f` (`0xbf800000`). The body does not establish a semantic field
   name, so this note does not infer one.
6. **Optional configured particle effect** (`0x00417b7a`–`0x00417bef`): re-read
   the definition index. If it is not `-1`, walk `[0x008553f8]`, resolve the
   definition record's `+0x30` name through
   `CParticleSet__FindByNameAndTrackLinkSlot 0x004cd7a0`, and call
   `CParticleManager__CreateEffect 0x004cb3d0` once with the building transform.
   Index `-1` skips this one configured effect, but not the next stage.
7. **Forty `Generic Mesh` effects** (`0x00417bf4`–`0x00417d9d`): resolve the
   literal `Generic Mesh` at `0x00623b94`, set a loop count of `0x28`, and call
   `CParticleManager__CreateEffect` once per iteration. Each iteration obtains
   three independent low-eight-bit `_rand` values, subtracts `0x80`, and uses
   constants `0.0003125f`, `20.0f`, and `1.0f` to form a randomized point around
   the building (the third axis includes the explicit `building[+0x24]-1.0f`
   term). When the effect link exposes a live object, the body sends that point
   to current saved target `CUnit__PushTransformHistoryAndSetCurrent`
   `0x004097a0`; that saved owner prefix is not used here to claim the
   link-produced receiver is a CUnit.

   If the link's `+0xa8` object and `[building+0x30]` are both live, the body
   writes a four-dword randomized block at object `+0x48`, calls
   `[building+0x30]` virtual byte offset `+0x28` (slot 10), stores its result at
   object `+0x8c`, and copies `[result+0x164]` to object `+0x74`. Every iteration
   then calls `CParticleManager__RemoveOwnerLinkFromGlobalList` on its local
   effect link before decrementing the exact 40-count loop.
8. **Optional event and return** (`0x00417da3`–`0x00417dc8`): if
   `[building+0x74]` is live, call global event manager `0x00672fc8` at
   `CEventManager__AddEvent_AtTime 0x0044b370` with event number `0x1388`, the
   building, exact `-1.0f` (`NEXT_FRAME`), and zero-valued remaining tuple
   slots. Then return 1. The controller and null-controller arms join here.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x00417a61` | `CUnit__MarkDestroyedAndCleanupLinks 0x004fd140` |
| `0x00417a70` | `CUnit__ReleaseChildUnits 0x004fcfe0` |
| `0x00417a92` | `CWorldPhysicsManager__CreateExplosion 0x0050ff10` |
| `0x00417aaa` | `CInitThing__ctor 0x0048dcf0` |
| `0x00417afc`, `0x00417b8d` | `CSPtrSet__First 0x00406d20` — two definition-list walks |
| `0x00417b67` | indirect explosion slot 9 (`vtable+0x24`) |
| `0x00417bc3`, `0x00417bfe` | `CParticleSet__FindByNameAndTrackLinkSlot 0x004cd7a0` |
| `0x00417bef`, `0x00417c54` | `CParticleManager__CreateEffect 0x004cb3d0` |
| `0x00417c15` | `ParticleEffectLink_T3_004cb040 0x004cb040` |
| `0x00417c59`, `0x00417c6c`, `0x00417c7f` | `_rand 0x0055dbfe` |
| `0x00417d20` | current saved `CUnit__PushTransformHistoryAndSetCurrent 0x004097a0`; receiver bounded above |
| `0x00417d6e` | indirect `[building+0x30]` slot 10 (`vtable+0x28`) |
| `0x00417d8f` | `CParticleManager__RemoveOwnerLinkFromGlobalList 0x004cb050` |
| `0x00417dc3` | `CEventManager__AddEvent_AtTime 0x0044b370` |

## References and slot ownership

The whole-`.text` rel32 scan finds **zero** inbound `E8`/`E9` references.
The image-wide imm32 census finds exactly **one** dword containing
`0x00417a40`: `0x005d8f7c`. It is byte offset `+0xc8`, slot 50, in vtable
`0x005d8eb4`; the Complete Object Locator resolves `.?AVCBuilding@@`.
Therefore this is the direct CBuilding slot-50 body, reached virtually in this
image rather than by a direct rel32 call.

## Shadow-path coupling and class boundary

This body has no direct `CStaticShadows` call. Its shared TF_DYING mark has a
bounded CBuilding shadow consequence through
`CBuilding__RenderAndUpdateStaticShadow 0x00417540`: that complete 77-byte /
27-instruction body hashes
`90a387faf926c280696c0785d1d466404c56f09e403cc118e657a33740babd8a`.
When `[building+0x178]` is null, it tests TF_DYING and returns before both
`CThing__Render` and `CStaticShadows__UpdateVisibility`; a live controller
bypasses that dying-bit early-out and continues the render/shadow path. Thus the
same controller split that suppresses this wrapper's explosion effects also
preserves that separate render/shadow path.

Do not conflate this override with
`CSimpleBuilding__TryActivateAndEnableShadows 0x004dfce0`. That separate
34-byte wrapper calls the same shared cleanup, then explicitly calls
`CStaticShadows__UpdateVisibility(..., 1)` on success. It is a bounded
cross-class contrast, not part of this CBuilding body.

## Shared versus subclass-specific law

The TF_DYING guard/store, sounds, profile accounting, segment cascade, script
event id 5, active-reader clear, and linked-set drain all belong to the shared
CUnit callee. CBuilding alone adds the child release, controller-dependent
explosion/effect split, `+0xf8` write, 40-count `Generic Mesh` fan-out, and
optional next-frame event `0x1388`. Slot number 50 identifies placement; these
behaviors, not the ordinal alone, establish the destruction contract.

## Open questions

- The semantic name of `[building+0xf8]` remains unknown.
- The concrete types behind the generic-effect link's `+0xa8` object,
  `[building+0x30]`, and its slot-10 result remain unresolved. The exact field
  traffic is pinned without assigning gameplay names.
- Static bytes do not establish which authored building definitions use index
  `-1`, which configured effect name each definition carries, or runtime visual
  timing.
- This body never reads `[unit+0x88]`; the separate cooldown-reader question is
  not part of this family.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x00417a40`–`0x00417de5` is not
  `5d6c0aaf…804f`, or the final instruction stops being plain `ret`.
- The reference census is not zero rel32 plus the single CBuilding slot-50
  dword at `0x005d8f7c`.
- Shared cleanup returning 0 reaches any subclass stage, or a fresh transition
  returns anything other than 1.
- A live `[building+0x178]` stops skipping the explosion/particle branch, the
  generic loop count stops being exactly `0x28`, or event `0x1388` moves before
  that branch rejoins.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before reading.
  Reproduced the complete body/hash, 17 direct calls, two indirect calls, zero
  inbound rel32 references, sole RTTI-backed slot-50 dword, controller split,
  explosion-init context, exact 40-count effect loop, next-frame event tuple,
  and bounded render/shadow coupling with the read-only PE/capstone probe.
- Related contracts:
  [`../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md),
  [`../DestructableSegmentsController.cpp/CDestructableSegmentsController__TriggerCoreCascadeIfEligible.md`](../DestructableSegmentsController.cpp/CDestructableSegmentsController__TriggerCoreCascadeIfEligible.md).
