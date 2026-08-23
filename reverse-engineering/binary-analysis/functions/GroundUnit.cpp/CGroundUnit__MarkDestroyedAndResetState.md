# CGroundUnit__MarkDestroyedAndResetState

> Address: `0x0047CE80`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `GroundUnit.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the CBoat/CGroundUnit/CSentinel slot-50 destruction wrapper. It calls
`CUnit__MarkDestroyedAndCleanupLinks` first and returns 0 unchanged when the
receiver was already dying. On a fresh transition it clears the dword at
`[groundUnit+0x25c]` and returns 1. All other teardown belongs to the shared
CUnit callee or to one of this wrapper's direct callers.
Evidence: MEASURED — pristine SHA verified before complete-body disassembly and
raw hashing, whole-`.text` rel32 scan with all five hits disassembled, image-
wide aligned-imm32 census, strict MSVC RTTI/vtable readback, and complete call
classification. No Ghidra or rebuild owner changed.

## Contract (byte-exact)

Body `0x0047ce80`–`0x0047ce9e` inclusive through the complete plain `ret`,
**31 bytes / 11 instructions**, raw SHA-256
`1ae96b29c60955a4c845319c4eca0e60f471bebea0da8c84550bdd9968bded2c`.
It has **1 outbound direct `E8`, 0 outbound `E9`, and 0 indirect calls**. Both
branches stay inside the body. Signature shape is
`int __thiscall ...(CGroundUnit *groundUnit)`: no stack arguments are read. EAX
is the shared cleanup's 0 on the already-dying arm and explicit 1 after the
fresh field reset.

## Stage law (byte-exact)

1. **Shared one-shot gate** (`0x0047ce83`–`0x0047ce8d`): call
   [`CUnit__MarkDestroyedAndCleanupLinks`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
   If it returns 0, restore ESI and return that 0 without the field write.
2. **Ground-unit reset** (`0x0047ce8e`): on a fresh transition, write exact
   dword zero to `[groundUnit+0x25c]`. The bytes do not establish a semantic
   field name.
3. **Fresh-transition result** (`0x0047ce98`–`0x0047ce9e`): set EAX to 1,
   restore ESI, and return.

## Outbound call

| Site | Callee / role |
| --- | --- |
| `0x0047ce83` | `CUnit__MarkDestroyedAndCleanupLinks 0x004fd140` |

## Inbound rel32 census

Exactly **five** whole-`.text` calls, each disassembled as an instruction:

| Site | Current name-table owner |
| --- | --- |
| `0x0041b593` | `CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph` |
| `0x00489b4c` | `CInfantryUnit__VFunc50_HandleDeathPickupAndEffects` |
| `0x004a00b7` | `CMech__VFunc_50_004a00a0` — profile `+0x130` arm |
| `0x004a00d4` | `CMech__VFunc_50_004a00a0` — null profile `+0x130` arm |
| `0x004ba9d3` | `CMine__TryDestroyedResetAndDispatchVFunc1D4` |

Those caller-owned continuations are not folded into this 31-byte wrapper.

## Slot ownership

The image-wide aligned-dword census finds exactly **three** copies of
`0x0047ce80`. The strict RTTI census resolves all three as byte offset `+0xc8`,
slot 50:

| Entry | Vtable | RTTI class |
| --- | --- | --- |
| `0x005e09a8` | `0x005e08e0` | CSentinel |
| `0x005e2354` | `0x005e228c` | CBoat |
| `0x005e339c` | `0x005e32d4` | CGroundUnit |

The five rel32 callers are subclass/peer wrappers that explicitly delegate to
this body; they do not add further direct slot ownership for this VA.

## Shared versus ground-unit-specific law

The TF_DYING guard/store, sound stop, profile accounting, destroyable-segment
cascade, script event id 5, active-reader clear, and linked-set drain belong to
the shared CUnit callee. This body adds only the fresh-transition zero at
`+0x25c`. It neither releases child units nor invokes the deployment-graph
helper. Explosion, pickup, event, and virtual-dispatch effects visible in the
five inbound owners remain caller-specific.

## Open questions

- The semantic name and value domain of `[groundUnit+0x25c]` remain unknown.
- Static bytes do not establish why CBoat and CSentinel inherit this exact
  reset, or which authored states make the field nonzero before destruction.
- The five caller continuations require their own contracts before their
  pickup/effect/deployment behavior can be attributed beyond current names.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x0047ce80`–`0x0047ce9e` is not
  `1ae96b29…bded2c`, or the final instruction stops being plain `ret`.
- The reference census is not five rel32 calls plus the three RTTI-backed
  slot-50 dwords above.
- Shared cleanup returning 0 reaches the `+0x25c` write, or the fresh arm
  returns anything other than 1.
- The only class-specific write stops being exact dword zero at `+0x25c`.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before reading.
  Reproduced the complete body/hash, sole outbound call, five verified inbound
  calls, three strict slot-50 entries, result polarity, and exact field write
  with read-only PE/capstone/RTTI probes.
- Related contract:
  [`../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
