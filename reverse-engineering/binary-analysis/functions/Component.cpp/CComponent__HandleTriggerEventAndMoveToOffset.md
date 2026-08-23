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
That event's shared CUnit arm performs the profile-drop call and virtual
shutdown scheduling; it is no longer an unresolved handler. Every fresh arm
returns 1.
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
   [`CUnit__ResetDeploymentGraphAndScheduleEvent`](../Unit.cpp/CUnit__ResetDeploymentGraphAndScheduleEvent.md)
   `0x004fd040`, then returns explicit 1. This arm does **not** call
   `CUnit__ReleaseChildUnits` directly. The helper queues thing-event 2000
   (`SHUTDOWN`) for this component at `mTime+0.05f`; that tuple and dispatch
   path are helper-owned.
3. **Other-combination shared gate and child release**
   (`0x0042883c`–`0x00428855`): call the same shared CUnit cleanup at
   `0x0042883e`. A 0 result returns 0. On 1, call
   `CUnit__ReleaseChildUnits 0x004fcfe0`, then re-read profile `+0x198`.
4. **Live-`+0x198` linked-vector move** (`0x0042885b`–`0x00428970`): load the
   linked object from `[component+0x26c]` without a local null check. Let
   `(dx,dy)` be component position `(+0x1c,+0x20)` minus linked-object position
   `(+0x1c,+0x20)`. Normalize that 2D vector using exact constants `1.0f` and
   `0.0f` at `0x005d8568/0x005d856c`; a zero length leaves `(ux,uy)=(0,0)`.

   The stack operands in this arm require tracking the argument pushes rather
   than treating every printed `[esp+N]` as one fixed local. Define `F` as ESP
   immediately after `push esi` at `0x00428803`. The normalization stores `uy`
   at `[F+0x0c]` (`0x00428883`, then `0x004288be` on the nonzero route), stores
   zero at `[F+0x10]` (`0x0042886f`/`0x004288ac`), and leaves `ux` in ST(0).
   At `0x004288d7`, pushing the slot-27 destination changes ESP to `P=F-4`.
   Therefore the scaling block maps as follows:

   | Instructions | Printed operand | Stable-frame value |
   | --- | --- | --- |
   | `0x004288f6`–`0x004288fc` | `[P+0x1c]` | `[F+0x18] = 0.4*ux` |
   | `0x00428900`–`0x0042890a` | `[P+0x10]` -> `[P+0x20]` | `[F+0x0c]` -> `[F+0x1c] = 0.4*uy` |
   | `0x0042890e`–`0x00428918` | `[P+0x14]` -> `[P+0x24]` | `[F+0x10]` -> `[F+0x20] = 0` |

   Thus the operand printed as `[esp+0x14]` at `0x0042890e` aliases the proved
   zero local, not unwritten `[F+0x14]`; `[F+0x14]` is not read by this arm.
   The one-explicit-argument MSVC `__thiscall` is callee-clean: this body has no
   caller adjustment, and the immediately preceding sibling at `0x004287c0`
   uses the same push/call shape for slot 27. ESP is consequently back at `F`
   after `0x0042891c`, so the reads at `0x0042891f`, `0x00428925`, and
   `0x00428934` consume the initialized `[F+0x18]`, `[F+0x1c]`, and
   `[F+0x20]` values above.

   Slot 27 receives a local four-dword destination. The sibling at
   `0x004287c0` proves the same slot writes such a destination buffer. Let
   `(rx,ry,rz)` be the first three floats at the pointer this call returns in
   EAX; this note does not assume that return aliases the supplied buffer or
   invent the slot's source virtual name. With exact `0.4f` at `0x005d8c40`,
   the push-aware transfer derives:

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
   `CEventManager::mTime 0x00672fd0` plus exact `7.0f` (`0x005d8c48`). The
   complete tuple is `(event=4004, target=this, time=&local(mTime+7.0f),
   priority=0, data=null, reuse=null)`. Then return 1 regardless of the
   source-void scheduler's queue outcome.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x00428822`, `0x0042883e` | `CUnit__MarkDestroyedAndCleanupLinks 0x004fd140`; mutually exclusive sites |
| `0x0042882d` | [`CUnit__ResetDeploymentGraphAndScheduleEvent`](../Unit.cpp/CUnit__ResetDeploymentGraphAndScheduleEvent.md) `0x004fd040` |
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

## Event 0x0FA4 consumer and queue boundary

The pristine operand census has exactly two event-producing `push 0x0fa4`
sites: this one and `CMech__VFunc_50_004a00a0`; a third raw `0x0fa4` occurrence
is an unrelated `HResultToString` comparison. The CMech producer uses
`mTime+3.5f`; this component uses `mTime+7.0f`. Both target the scheduling
receiver itself with priority/data/reuse zero.

At fixed manager time, 7.0 seconds maps to ring offset
`floor((7.0-0.001)*20)=139` from the current insertion bucket and fires after
140 `AdvanceTime` ticks. `CEventManager__Flush` calls target slot 0; both the
CComponent and CGillMHead vtables place
[`CUnit__HandleEvent`](../Unit.cpp/CUnit__HandleEvent.md) `0x004f9820` there.
Its 4004 arm calls `CUnit__SpawnProfileDropPickup`, then receiver slot 14.
Both vtables resolve slot 14 to
`CComplexThing__AddShutdownEvent 0x004f43d0`, which schedules thing-event 2000
(`SHUTDOWN`) for `NEXT_FRAME`. The shared manager owns allocation, ring order,
and slot-0 delivery; this component owns only the fresh-arm tuple above, while
the CUnit/ComplexThing handlers own the delayed effects.

`AddEvent_AtTime` has no status result. Invalid-manager and pool-exhaustion
paths log and return; null-target and over-1,000,000-second paths return without
queueing. This wrapper still returns 1 after the call and does not roll back its
already-completed child release if insertion fails.

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
- The absent `Unit.cpp` event-enum spelling for 4004 remains unknown. Its retail
  handler effect is proved; runtime presentation and rebuild parity are not.
- The separately named deployment-graph helper owns its node/script/drop/
  event-2000 teardown and failure boundary; this wrapper proves its
  fresh-only conditional invocation.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x00428800`–`0x004289a5` is not
  `0e2f7950…23df309`, or the final instruction stops being plain `ret`.
- The reference census is not zero rel32 plus exactly the CComponent and
  CGillMHead slot-50 dwords above.
- Either profile route skips shared cleanup, shared result 0 reaches child/
  helper/move/event work, or a fresh route returns anything other than 1.
- The slot-27 argument push no longer gives `P=F-4`, its callee-clean return no
  longer restores `F`, the three post-call reads stop resolving to initialized
  `[F+0x18/+0x1c/+0x20]`, or the derived normalized-XY/`0.4f` formula changes.
- Event `0x0fa4` stops using the exact tuple above, or CComponent/CGillMHead
  slot 0 no longer reaches CUnit's 4004 drop-plus-slot-14 arm.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before reading.
  Reproduced the complete body/hash, five direct calls, two indirect calls,
  zero inbound rel32 references, two strict slot-50 entries, both shared-gate
  sites, exact event tuple, and the vector formula with a push-aware FPU/local
  replay. In particular, the slot-27 argument changes `F` to `P=F-4`; the
  apparent `[esp+0x14]` read is initialized `[F+0x10]`, and the post-call
  `[esp+0x18]` read is initialized `[F+0x18]`. Read-only PE/capstone/RTTI probes
  were used throughout.
- 2026-08-22 event-chain closure — re-read both event-4004 producers, the
  manager queue/failure law, CComponent/CGillMHead slots 0/14, CUnit's exact
  4004 arm, and the downstream 2000 shutdown dispatch. The authored 4004 enum
  spelling remains unknown; the delayed drop-plus-shutdown effect does not.
- Related contract:
  [`../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
