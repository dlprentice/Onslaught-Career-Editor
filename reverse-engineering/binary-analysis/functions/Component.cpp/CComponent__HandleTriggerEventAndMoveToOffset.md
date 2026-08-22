# CComponent__HandleTriggerEventAndMoveToOffset

> Address: `0x00428800`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `Component.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the CComponent/CGillMHead slot-50 destruction override. Two profile
fields select one of three fresh-transition continuations, but both entry arms
call `CUnit__MarkDestroyedAndCleanupLinks` exactly once. An already-dying result
returns 0 without component work. A fresh transition either resets the unit's
deployment graph, releases child units and moves through linked-object vector
slots, or releases child units and schedules event `0x0fa4` at `mTime+7.0f`.
Every fresh arm returns 1.
Evidence: MEASURED — pristine SHA verified before complete-body disassembly and
raw hashing, whole-`.text` rel32 scan, image-wide aligned-imm32 census, strict
MSVC RTTI/vtable readback, exact constant reads, and complete direct/indirect-
call classification. No Ghidra or rebuild owner changed.

## Contract (byte-exact)

Body `0x00428800`–`0x004289a5` inclusive through the complete plain `ret`,
**422 bytes / 125 instructions**, raw SHA-256
`0e2f7950513b98d3c8f02bb3c4ba428ef15718b7527cced1e0c35090923df309`.
It uses a `0x54`-byte local frame and has **5 outbound direct `E8`, 0 outbound
`E9`, and 2 indirect calls**. All branches remain inside the body. Signature
shape is `int __thiscall ...(CComponent *component)`: no stack arguments are
read. EAX is 0 when the shared cleanup reports already dying and explicit 1 on
every fresh-transition continuation.

## Stage law (byte-exact)

1. **Profile split before the shared gate** (`0x00428806`–`0x00428820`): load
   `[component+0x164]` without a local null check and inspect dwords at profile
   offsets `+0x124` and `+0x198`. Only when both are zero does control use the
   first shared-cleanup callsite. Every other combination uses the second.
2. **Both-zero deployment-graph arm** (`0x00428822`–`0x0042883b`): call
   [`CUnit__MarkDestroyedAndCleanupLinks`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
   A 0 result joins the common 0 return. A 1 result calls current saved
   `CUnit__ResetDeploymentGraphAndScheduleEvent 0x004fd040`, then returns
   explicit 1. This arm does **not** call `CUnit__ReleaseChildUnits` directly.
3. **Other-combination shared gate and child release**
   (`0x0042883c`–`0x00428855`): call the same shared CUnit cleanup at
   `0x0042883e`. A 0 result returns 0. On 1, call
   `CUnit__ReleaseChildUnits 0x004fcfe0`, then re-read profile `+0x198`.
4. **Live-`+0x198` linked-vector move** (`0x0042885b`–`0x00428970`): load the
   linked object from `[component+0x26c]` without a local null check. Let
   `(dx,dy)` be component position `(+0x1c,+0x20)` minus linked-object position
   `(+0x1c,+0x20)`. Normalize that 2D vector using exact constants `1.0f` and
   `0.0f` at `0x005d8568/0x005d856c`; a zero length leaves `(ux,uy)=(0,0)`.

   Call the linked object's virtual byte offset `+0x6c` (slot 27) with a local
   four-dword output. The immediately preceding named sibling at `0x004287c0`
   proves this same slot receives and writes such a destination buffer. Let
   `(rx,ry,rz)` be the first three floats at the pointer this call returns in
   EAX; this note does not assume that return aliases the supplied buffer or
   invent the slot's source virtual name. Using exact `0.4f` at `0x005d8c40`,
   form:

   ```text
   out.x = rx + 0.4*ux + 0.4*linked[0x40]
   out.y = ry + 0.4*uy + 0.4*linked[0x50]
   out.z = rz          + 0.4*linked[0x60]
   ```

   Pass the resulting XYZ block to the component's virtual byte offset `+0x70`
   (slot 28), then return 1. The offsets and formula are byte-derived; no basis,
   bone, or gameplay attachment names are inferred.
5. **Null-`+0x198`, live-`+0x124` event arm**
   (`0x00428971`–`0x004289a5`): because the both-zero case already returned,
   this route has profile `+0x124` live. Schedule event `0x0fa4` through
   `CEventManager__AddEvent_AtTime 0x0044b370` for the component at BSS
   `CEventManager::mTime 0x00672fd0` plus exact `7.0f` (`0x005d8c48`), with the
   remaining tuple slots zero. Then return 1.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x00428822`, `0x0042883e` | `CUnit__MarkDestroyedAndCleanupLinks 0x004fd140`; mutually exclusive sites |
| `0x0042882d` | `CUnit__ResetDeploymentGraphAndScheduleEvent 0x004fd040` |
| `0x00428850` | `CUnit__ReleaseChildUnits 0x004fcfe0` |
| `0x0042891c` | indirect linked-object slot 27 (`vtable+0x6c`) with output buffer |
| `0x00428964` | indirect component slot 28 (`vtable+0x70`) with computed XYZ |
| `0x00428997` | `CEventManager__AddEvent_AtTime 0x0044b370` |

## References and slot ownership

The whole-`.text` rel32 scan finds **zero** inbound `E8`/`E9` references. The
image-wide aligned-dword census finds exactly **two** copies of `0x00428800`;
the strict RTTI census resolves both as byte offset `+0xc8`, slot 50:

| Entry | Vtable | RTTI class |
| --- | --- | --- |
| `0x005e3e08` | `0x005e3d40` | CComponent |
| `0x005e42c0` | `0x005e41f8` | CGillMHead |

Thus this body is reached virtually for both proved classes in the pristine
image, not by a direct rel32 caller.

## Shared versus component-specific law

The TF_DYING guard/store, sound stop, profile accounting, destroyable-segment
cascade, script event id 5, active-reader clear, and linked-set drain belong to
the shared CUnit callee. This override adds the pre-gate profile split and,
only after a fresh result, one of three continuations: deployment-graph helper,
child release plus linked-vector movement, or child release plus delayed event
`0x0fa4`. The two shared callsites are mutually exclusive and converge on the
same 0 polarity; no fresh arm returns anything other than 1.

## Open questions

- Semantic names and authored value domains for profile offsets `+0x124` and
  `+0x198` remain unproved.
- The concrete type of `[component+0x26c]` and source virtual names for slots 27
  and 28 remain unresolved; only exact traffic and arithmetic are pinned.
- The runtime handler/gameplay meaning of event `0x0fa4` is not established by
  this body.
- The separately named deployment-graph helper owns its internal node/script/
  event-2000 teardown; this wrapper proves only its conditional invocation.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x00428800`–`0x004289a5` is not
  `0e2f7950…23df309`, or the final instruction stops being plain `ret`.
- The reference census is not zero rel32 plus exactly the CComponent and
  CGillMHead slot-50 dwords above.
- Either profile route skips shared cleanup, shared result 0 reaches child/
  helper/move/event work, or a fresh route returns anything other than 1.
- The move stops using the exact normalized XY/`0.4f` formula, or event
  `0x0fa4` stops using `mTime+7.0f`.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before reading.
  Reproduced the complete body/hash, five direct calls, two indirect calls,
  zero inbound rel32 references, two strict slot-50 entries, both shared-gate
  sites, exact vector formula, and exact event tuple with read-only
  PE/capstone/RTTI probes.
- Related contract:
  [`../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
