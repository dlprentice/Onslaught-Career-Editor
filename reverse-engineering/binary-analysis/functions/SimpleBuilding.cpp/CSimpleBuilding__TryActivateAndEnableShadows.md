# CSimpleBuilding__TryActivateAndEnableShadows

> Address: `0x004DFCE0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `SimpleBuilding.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: CSimpleBuilding's slot-50 destruction override. It calls
`CUnit__MarkDestroyedAndCleanupLinks` first and returns 0 unchanged when the
receiver is already dying. On a fresh transition it calls the global static-
shadow manager's `CStaticShadows__UpdateVisibility` with the SimpleBuilding and
exact enable argument 1, then returns 1. The current saved name's broader
“activate” wording is not expanded beyond that byte-proved one-shot call.
Evidence: MEASURED — pristine SHA verified before complete-body disassembly and
raw hashing, whole-`.text` rel32 scan, image-wide aligned-imm32 census, strict
MSVC RTTI/vtable readback, and complete call/argument classification. No Ghidra
or rebuild owner changed.

## Contract (byte-exact)

Body `0x004dfce0`–`0x004dfd01` inclusive through the complete plain `ret`,
**34 bytes / 14 instructions**, raw SHA-256
`ab47a221b39e1ce15ac0f05f1e4cbc250dff57159b8b2e067a7f411a00395efc`.
It has **2 outbound direct `E8`, 0 outbound `E9`, and 0 indirect calls**. Both
branches remain inside the body. Signature shape is
`int __thiscall ...(CSimpleBuilding *simpleBuilding)`: no stack arguments are
read. EAX is the shared cleanup's 0 on the already-dying arm and explicit 1
after the fresh shadow call.

## Stage law (byte-exact)

1. **Shared one-shot gate** (`0x004dfce3`–`0x004dfced`): call
   [`CUnit__MarkDestroyedAndCleanupLinks`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
   If it returns 0, restore ESI and return that 0 without contacting the shadow
   manager.
2. **Fresh shadow activation** (`0x004dfcee`–`0x004dfcfa`): push exact integer
   1, push the SimpleBuilding, set ECX to global shadow manager `0x009c8010`,
   and call `CStaticShadows__UpdateVisibility 0x004ebfb0`.
3. **Fresh-transition result** (`0x004dfcfb`–`0x004dfd01`): set EAX to 1,
   restore ESI, and return. The shadow callee's EAX does not escape.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x004dfce3` | `CUnit__MarkDestroyedAndCleanupLinks 0x004fd140` |
| `0x004dfcf6` | `CStaticShadows__UpdateVisibility 0x004ebfb0`, manager `0x009c8010`, arguments `(simpleBuilding, 1)` |

## References and slot ownership

The whole-`.text` rel32 scan finds **zero** inbound `E8`/`E9` references. The
image-wide aligned-dword census finds exactly **one** copy of `0x004dfce0`:
`0x005dfe04`. The strict RTTI census resolves it as byte offset `+0xc8`, slot
50, in CSimpleBuilding vtable `0x005dfd3c`. Therefore this is the direct
CSimpleBuilding slot-50 body, reached virtually in the pristine image.

## Shared versus SimpleBuilding-specific law

The TF_DYING guard/store, sound stop, profile accounting, destroyable-segment
cascade, script event id 5, active-reader clear, and linked-set drain belong to
the shared CUnit callee. CSimpleBuilding adds only the fresh-only shadow-manager
call with enable argument 1. It does not release child units, call the
deployment-graph helper, create effects, or schedule another event in this
body. Shared result 0 suppresses the shadow call; the fresh arm returns 1.

This is distinct from
[`CBuilding__VFunc_50_00417a40`](../Building.cpp/CBuilding__VFunc_50_00417a40.md):
that CBuilding override has no direct shadow-manager call and instead adds its
controller-dependent explosion/effect/event behavior after shared cleanup.

## Open questions

- Static bytes prove the `UpdateVisibility(..., 1)` request but not the exact
  rendered frame when a shadow becomes visible or is rebuilt.
- The current saved name's “activate” term has no separate field write or call
  in this body; whether it is source-authentic terminology remains unproved.
- Authored SimpleBuilding definitions and rebuild parity remain unmeasured.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x004dfce0`–`0x004dfd01` is not
  `ab47a221…395efc`, or the final instruction stops being plain `ret`.
- The reference census is not zero rel32 plus the sole CSimpleBuilding slot-50
  dword at `0x005dfe04`.
- Shared cleanup returning 0 reaches the shadow manager, or the fresh arm stops
  passing `(simpleBuilding, 1)` before returning explicit 1.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before reading.
  Reproduced the complete body/hash, both direct calls, zero inbound rel32
  references, sole strict slot-50 entry, exact shadow-manager arguments, and
  result polarity with read-only PE/capstone/RTTI probes.
- Related contracts:
  [`../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md),
  [`../Building.cpp/CBuilding__VFunc_50_00417a40.md`](../Building.cpp/CBuilding__VFunc_50_00417a40.md).
