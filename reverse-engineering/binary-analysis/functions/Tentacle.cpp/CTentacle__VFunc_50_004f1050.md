# CTentacle__VFunc_50_004f1050

> Address: `0x004F1050`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `Tentacle.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: CTentacle's slot-50 destruction override. It returns 0 immediately
when `CUnit__MarkDestroyedAndCleanupLinks` reports an already-dying receiver.
On a fresh transition it copies `[tentacle+0x70]+0xe8` to
`[tentacle+0x304]`, creates a configured explosion, builds a
`CExplosionInitThing` whose position is the tentacle-local `+0x2d4` vector
transformed into world space, dispatches explosion slot 9 when creation
succeeds, releases child units, and returns 1.
Evidence: MEASURED — pristine SHA verified before complete-body disassembly
and hashing, whole-`.text` rel32 scan, image-wide imm32 census, RTTI/vtable
readback, and complete direct/indirect-call classification. The current saved
address-qualified name is retained; no Ghidra or rebuild owner changed.

## Contract (byte-exact)

Body `0x004f1050`–`0x004f1217` inclusive through the complete plain `ret`,
**456 bytes / 124 instructions**, raw SHA-256
`bfdd797acbb0a9986cd4c6964801e80668e4c464dae6ae9ebeccc2a8a8809104`.
It uses a `0x3f8`-byte local frame and has **4 outbound direct `E8`, 0 outbound
`E9`, and 1 indirect call**. All branches remain inside the body. Signature
shape is `int __thiscall ...(CTentacle *tentacle)`: no stack arguments are
read. EAX is the shared cleanup's 0 on the already-dying arm and explicit 1
after every fresh-transition arm.

## Stage law (byte-exact)

1. **Shared one-shot gate** (`0x004f1059`–`0x004f1069`): call
   [`CUnit__MarkDestroyedAndCleanupLinks`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
   If it returns 0, unwind the local frame and return that 0. No tentacle field,
   explosion, context, or child-release work below repeats.
2. **Tentacle-specific field copy** (`0x004f106a`–`0x004f107c`): load the
   object at `[tentacle+0x70]`, read its `+0xe8` dword, and store that value at
   `[tentacle+0x304]`. There is no null check on the `+0x70` object. The bytes
   prove the copy but not semantic names for either field.
3. **Configured explosion creation** (`0x004f1082`–`0x004f108e`): read index
   `[tentacle+0x164]+0xe8` and pass it to
   `CWorldPhysicsManager__CreateExplosion 0x0050ff10`. The profile pointer is
   likewise dereferenced without a local null check.
4. **Explosion-init context** (`0x004f1091`–`0x004f114d`): construct a stack
   `CInitThing`, then install vtable `0x005d8c80`. Its Complete Object Locator
   resolves strict RTTI `CExplosionInitThing`. The body inlines a zero-based
   walk of the explosion-definition list rooted at global `[0x008553f8]` for
   the same profile `+0xe8` index and stores the selected record at context
   `+0x3bc`. It stores the tentacle at context `+0x3c4` and copies
   `[tentacle+0x138]` to context `+0xa0`. A missing list entry becomes null in
   the context; this body does not reject it.
5. **Tentacle-local to world-space position** (`0x004f1153`–`0x004f11f1`):
   only when the explosion factory result is non-null, multiply the local
   three-float vector `[tentacle+0x2d4..+0x2dc]` by the three transform rows at
   `[tentacle+0x3c..+0x64]`, then add translation
   `[tentacle+0x1c..+0x24]`. Store the resulting XYZ at init-context offsets
   `+0x04`, `+0x08`, and `+0x0c`.
6. **Explosion dispatch** (`0x004f11f5`–`0x004f11fe`): call the created
   explosion's virtual byte offset `+0x24` (slot 9, the already pinned
   `CExplosion::Init` dispatch) with the completed context. A null factory
   result skips both the transform calculation and this indirect call.
7. **Child release and result** (`0x004f1201`–`0x004f1217`): call
   `CUnit__ReleaseChildUnits 0x004fcfe0`, then set EAX to 1 and return. Child
   release therefore still occurs when the explosion factory returned null,
   but not when the shared one-shot gate returned 0.

## Exact transform equations

Let `(lx, ly, lz)` be floats at `+0x2d4`, `+0x2d8`, `+0x2dc`; let `(tx, ty,
tz)` be `+0x1c`, `+0x20`, `+0x24`. The stored context position is:

```text
x = tx + [0x3c]*lx + [0x40]*ly + [0x44]*lz
y = ty + [0x4c]*lx + [0x50]*ly + [0x54]*lz
z = tz + [0x5c]*lx + [0x60]*ly + [0x64]*lz
```

This is a byte-derived affine transform. The note does not infer a bone,
socket, or authored attachment name for the local vector.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x004f1059` | `CUnit__MarkDestroyedAndCleanupLinks 0x004fd140` |
| `0x004f1089` | `CWorldPhysicsManager__CreateExplosion 0x0050ff10` |
| `0x004f1097` | `CInitThing__ctor 0x0048dcf0` |
| `0x004f11fe` | indirect explosion slot 9 (`vtable+0x24`) |
| `0x004f1203` | `CUnit__ReleaseChildUnits 0x004fcfe0` |

The two decoded direct `jmp` instructions at `0x004f10f6` and `0x004f1118`
target local join points `0x004f10fa` and `0x004f111c`; they are not outbound
transfers and are not `E9` opcodes.

## References and slot ownership

The whole-`.text` rel32 scan finds **zero** inbound `E8`/`E9` references.
The image-wide imm32 census finds exactly **one** dword containing
`0x004f1050`: `0x005e4064`. It is byte offset `+0xc8`, slot 50, in vtable
`0x005e3f9c`; the Complete Object Locator resolves `.?AVCTentacle@@`.
Therefore this is the direct CTentacle slot-50 body, reached virtually in this
image rather than by a direct rel32 call.

## Shared versus subclass-specific law

The TF_DYING guard/store, sound stop, profile accounting, segment cascade,
script event id 5, active-reader clear, and linked-set drain all belong to the
shared CUnit callee. CTentacle adds the `+0x304` copy, local-vector world
transform, configured explosion initialization, and post-explosion child
release. Unlike
[`CBuilding__VFunc_50_00417a40`](../Building.cpp/CBuilding__VFunc_50_00417a40.md),
it has no controller-dependent particle fan-out or event `0x1388`; unlike
[`CHiveBoss__MaybeScheduleEvent1388ForField74_004802f0`](../HiveBoss.cpp/CHiveBoss__MaybeScheduleEvent1388ForField74_004802f0.md),
it has an indirect explosion initializer. Slot number 50 identifies placement;
the bytes establish the destruction semantics.

## Open questions

- Semantic names for `[tentacle+0x70]+0xe8`, `[tentacle+0x304]`, and the local
  vector at `+0x2d4..+0x2dc` remain unknown.
- Static evidence does not establish which authored explosion definition the
  profile index selects or the runtime audiovisual result.
- This body never reads `[unit+0x88]`; the separate cooldown-reader question is
  not part of this family.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x004f1050`–`0x004f1217` is not
  `bfdd797a…09104`, or the final instruction stops being plain `ret`.
- The reference census is not zero rel32 plus the single CTentacle slot-50
  dword at `0x005e4064`.
- Shared cleanup returning 0 reaches the `+0x304` write, or a fresh transition
  returns anything other than 1.
- The world-space point stops using the exact nine transform multiplies and
  three translations above, or child release moves before explosion dispatch.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before reading.
  Reproduced the complete body/hash, four direct calls, one indirect call, zero
  inbound rel32 references, sole RTTI-backed slot-50 dword, result polarity,
  field copy, inlined definition lookup, exact affine transform, and child-
  release ordering with the read-only PE/capstone probe.
- Related contracts:
  [`../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md),
  [`../../cexplosion-factory-callers-2026-08-10.md`](../../cexplosion-factory-callers-2026-08-10.md).
