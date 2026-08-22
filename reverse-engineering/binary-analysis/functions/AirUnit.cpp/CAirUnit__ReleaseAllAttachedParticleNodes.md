# CAirUnit__ReleaseAllAttachedParticleNodes

> Address: `0x00403690`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `AirUnit.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the shared slot-50 destruction body for the nine RTTI-backed air-unit
classes listed below. It delegates the one-shot TF_DYING transition to
`CUnit__MarkDestroyedAndCleanupLinks`; a 0 result returns 0 without air-unit
work. On a fresh transition it releases child units, drains the two pointer sets
at `+0x25c` and `+0x26c`, applies the same particle-link teardown/free sequence
to every removed node, and returns 1.
Evidence: MEASURED — pristine SHA verified before complete-body disassembly and
raw hashing, whole-`.text` rel32 scan with the sole hit disassembled, image-wide
aligned-imm32 census, strict MSVC RTTI/vtable readback, and complete outbound-
call classification. No Ghidra or rebuild owner changed.

## Contract (byte-exact)

Body `0x00403690`–`0x00403723` inclusive through the complete plain `ret`,
**148 bytes / 56 instructions**, raw SHA-256
`17b8a6643e4f9029c31a8532bba4c13c13e869965fd17d5e437d7bb3a8c851f3`.
It has **10 outbound direct `E8`, 0 outbound `E9`, and 0 indirect calls**.
Every branch remains inside the body. Signature shape is
`int __thiscall ...(CAirUnit *airUnit)`: no stack arguments are read. EAX is the
shared cleanup's 0 on the already-dying arm and explicit 1 after the complete
fresh-transition arm.

## Stage law (byte-exact)

1. **Shared one-shot gate** (`0x00403693`–`0x0040369d`): call
   [`CUnit__MarkDestroyedAndCleanupLinks`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
   If it returns 0, pop EBX and return that 0. No child release or particle-node
   set access occurs.
2. **Child release** (`0x0040369e`–`0x004036a6`): save ESI/EDI and call
   `CUnit__ReleaseChildUnits 0x004fcfe0` before either air-unit set is touched.
3. **First set drain** (`0x004036a7`–`0x004036df`): operate on the `CSPtrSet`
   embedded at `[airUnit+0x25c]`. At each iteration copy the current set-head
   dword to set offset `+0x08`, take the node through the head's first dword, and
   stop on a null head or null node. For a live node, in exact order:
   - remove it with `CSPtrSet__Remove`;
   - call current saved `ParticleEffectLink_T3_004cb0b0(node, 0)`;
   - call `CParticleManager__RemoveOwnerLinkFromGlobalList(node)`;
   - free the node through `CDXMemoryManager__Free` with manager
     `0x009c3df0`.

   The loop then re-reads the set head.
4. **Second set drain** (`0x004036e1`–`0x00403719`): repeat the identical
   head-copy, remove, Tier-3 link call, global-list removal, and free sequence on
   the `CSPtrSet` at `[airUnit+0x26c]`.
5. **Fresh-transition result** (`0x0040371b`–`0x00403723`): restore EDI/ESI,
   set EAX to 1, restore EBX, and return.

The current Tier-3 name at `0x004cb0b0` is intentionally retained. Older saved
names proposed handle-state semantics, but the current name table demoted that
claim; this note pins only the argument and call order visible here.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x00403693` | `CUnit__MarkDestroyedAndCleanupLinks 0x004fd140` |
| `0x004036a2` | `CUnit__ReleaseChildUnits 0x004fcfe0` |
| `0x004036bf`, `0x004036f9` | `CSPtrSet__Remove 0x004e5bd0` |
| `0x004036c8`, `0x00403702` | current saved `ParticleEffectLink_T3_004cb0b0 0x004cb0b0` with argument 0 |
| `0x004036cf`, `0x00403709` | `CParticleManager__RemoveOwnerLinkFromGlobalList 0x004cb050` |
| `0x004036da`, `0x00403714` | `CDXMemoryManager__Free 0x00549220` via manager `0x009c3df0` |

## References and slot ownership

The whole-`.text` rel32 scan finds exactly **one** inbound call:

| Site | Current name-table owner |
| --- | --- |
| `0x0044e2ab` | `CFenrir__VFunc_0_0044e240` |

The call was disassembled in place: it follows a clear of TF_DYING in
`[receiver+0x2c]` and returns through that caller's `ret 4`; it is not a raw-byte
false positive.

The image-wide aligned-dword census finds exactly **nine** copies of
`0x00403690`. The strict RTTI census resolves all nine as byte offset `+0xc8`,
slot 50:

| Entry | Vtable | RTTI class |
| --- | --- | --- |
| `0x005e0e54` | `0x005e0d8c` | CCarver |
| `0x005e1304` | `0x005e123c` | CDiveBomber |
| `0x005e19f8` | `0x005e1930` | CPlane |
| `0x005e1ea0` | `0x005e1dd8` | CDropship |
| `0x005e2100` | `0x005e2038` | CCarrier |
| `0x005e2c94` | `0x005e2bcc` | CGroundAttackAircraft |
| `0x005e2ee8` | `0x005e2e20` | CBomber |
| `0x005e35ec` | `0x005e3524` | CBigAirUnit |
| `0x005e3840` | `0x005e3778` | CAirUnit |

Thus this body is the direct shared slot-50 implementation for those nine
classes, while the CFenrir path reaches it by a direct call.

## Shared versus air-unit-specific law

The TF_DYING guard/store, sound stop, profile accounting, destroyable-segment
cascade, script event id 5, active-reader clear, and `[unit+0x18c]` linked-set
drain all belong to the shared CUnit callee. This air-unit body adds child
release plus the two later set drains at `+0x25c` and `+0x26c`. Its removed-node
order is set removal, Tier-3 link call, particle-manager global unlink, then
memory free. None of that class-specific work repeats after the shared callee
returns 0.

## Open questions

- Static bytes do not establish semantic field names or concrete node types for
  the two air-unit sets.
- The exact internal effect of current Tier-3 helper `0x004cb0b0` remains
  intentionally unresolved here.
- The reason CFenrir clears TF_DYING and calls this body directly is a caller-
  level lifecycle question, not proof that CFenrir owns this slot-50 body.
- Runtime particle disappearance timing and rebuild parity remain unmeasured.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x00403690`–`0x00403723` is not
  `17b8a664…c851f3`, or the final instruction stops being plain `ret`.
- The reference census is not one rel32 call plus the nine RTTI-backed slot-50
  dwords above.
- Shared cleanup returning 0 reaches child release or either set, or a complete
  fresh arm returns anything other than 1.
- Either set stops using remove → Tier-3 call(0) → global unlink → free order.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before reading.
  Reproduced the complete body/hash, 10 direct calls, sole inbound rel32 call,
  nine strict slot-50 entries, result polarity, child-release order, and both
  particle-node drain loops with read-only PE/capstone/RTTI probes.
- Related contract:
  [`../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
