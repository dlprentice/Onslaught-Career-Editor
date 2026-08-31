# CUnit__ResetDeploymentGraphAndScheduleEvent

> Address: `0x004FD040`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `Unit.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: shared CUnit post-destruction teardown. It drains the child/deployment
reader set, clears two other link families, performs the profile-drop and
attached-script teardown, obtains a virtual delay, and schedules thing-event
`0x07d0` (`SHUTDOWN`) against the same Unit. For the proved CComponent,
CGillMHead, and CPod vtables the delay virtual is exactly `0.05f`, so that event
is queued for `CEventManager::mTime + 0.05f` and fires on the next 20 Hz update.
Evidence: MEASURED — pristine identity, complete-body decode/hash, whole-`.text`
rel32 census, image-wide operand census, exact vtable/constant reads, current
8,329-row name table, and the already-pinned manager/thing dispatch owners. No
Ghidra or rebuild owner changed.

## Contract (byte-exact)

Body `0x004fd040`–`0x004fd139` inclusive through the complete plain `ret`,
**250 bytes / 89 instructions**, raw SHA-256
`70a795dd8fa05726479e973e5393ddbe43d63ed0f5b017bcf9ec9f4377ae4924`.
It has **10 outbound direct `E8`, 0 outbound `E9`, and 5 indirect call sites**.
All branches remain inside the body. Signature shape is
`void __thiscall ...(CUnit *unit)`: no stack argument is read and no result is
consumed by any of the three direct callers. EAX after the final source-void
scheduler call is incidental, not a status contract.

## Stage law (byte-exact)

1. **Child/deployment reader drain** (`0x004fd049`–`0x004fd0a9`): initialize a
   cursor over the `CSPtrSet` at `[unit+0x19c]`, then repeatedly obtain the
   current reader wrapper. When its target is live, call target slot 50
   (`vtable+0xc8`) if the parent Unit has TF_DYING bit `0x04` at `+0x2c`, else
   call target slot 2 (`vtable+0x08`). Remove the wrapper from the set, run
   `CGenericActiveReader__dtor`, free the wrapper, and restart the cursor. A
   null wrapper or target bounds the corresponding branch exactly as decoded.
2. **Reader/link cleanup** (`0x004fd0ab`–`0x004fd0d9`): clear embedded active
   reader `[unit+0x144]` to null. Then drain the set at `[unit+0x18c]` by
   removing each live object and invoking its virtual slot 2 (`vtable+0x08`).
3. **Profile drop** (`0x004fd0db`): call
   `CUnit__SpawnProfileDropPickup 0x004fd230` before script teardown.
4. **Attached-script teardown** (`0x004fd0e2`–`0x004fd0fc`): if
   `[unit+0x74]` is live, call
   [`IScript__CallEventId3_OrReset`](../IScript__CallEventId3.cpp/IScript__CallEventId3_OrReset.md),
   then virtual-delete the script with scalar-delete flag 1 and null `+0x74`.
   The exact event-id-3/reset wrapper is pinned; this note does not invent a
   missing `Unit.cpp` spelling for the surrounding helper.
5. **Delay and queue tuple** (`0x004fd103`–`0x004fd12d`): call receiver virtual
   slot 112 (`vtable+0x1c0`) for an x87 float, add global manager time
   `[0x00672fd0]`, and call
   [`CEventManager__AddEvent_AtTime`](../CEventManager.cpp.md) with:

   | Argument | Exact value |
   | --- | --- |
   | `event_num` | `0x07d0` (2000) |
   | `to_call` | the same Unit (`edi`) |
   | `time` | pointer to local `mTime + slot112()` float |
   | `priority` | `0` (`START_OF_FRAME`) |
   | `data` | null |
   | `re_use_event` | null |

   Then restore the saved registers/frame and return.

## Proved Component / Pod delay

The strict vtable reads are identical at slot 112:

| Class / vtable | Slot-112 entry | Byte result |
| --- | --- | --- |
| CComponent / `0x005e3d40` | `0x00405ea0` | `fld [0x005d8578]; ret` |
| CGillMHead / `0x005e41f8` | `0x00405ea0` | same folded stub |
| CPod / `0x005dff8c` | `0x00405ea0` | same folded stub |

`[0x005d8578]` is `cd cc 4c 3d` = single-precision `0.05f`. Therefore the
CComponent both-zero route and CPod fresh route do not have an unresolved
virtual delay: both queue event 2000 at the current fixed manager time plus one
20 Hz tick.

## Dispatch meaning for this event 2000

The numeric ID alone is overloaded elsewhere. This tuple targets a CUnit
subclass, which makes its meaning provable:

1. `CEventManager__Flush` calls the target's vtable slot 0 with the
   `CScheduledEvent*` at ring site `0x0044b68a` (or overflow site
   `0x0044b6f2`). A `+0.05f` tuple takes the current ring bucket and fires on
   the next `AdvanceTime`/`Flush` update.
2. CComponent, CGillMHead, and CPod vtables all place
   [`CUnit__HandleEvent`](CUnit__HandleEvent.md) `0x004f9820` in slot 0.
3. Event 2000 misses CUnit's 4001–4005 switch and
   `CActor__HandleEvent`'s 3000/3001 switch, reaching
   `CComplexThing__HandleEvent 0x004f4300`.
4. `references/Onslaught/thing.h:33-39` names 2000 `SHUTDOWN`, and the retail
   2000 arm at `0x004f438c`–`0x004f43c4` calls receiver slot 2. The helper has
   already nulled `[unit+0x74]`, so the optional script-shutdown callback in
   that arm cannot run for this chain.
5. CComponent, CGillMHead, and CPod slot 2 is
   `CUnit__VFunc02_CleanupWorldLinksAndForward 0x004f95d0`, the shared
   world/link cleanup that ultimately forwards to `CComplexThing__Shutdown`.

Thus `0x07d0` here is exactly the Unit's delayed `EThingEvent::SHUTDOWN`, not a
mission-script timer or another subsystem's unrelated numeric 2000.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x004fd057`, `0x004fd0a0` | `LinkedPtrCursor__MoveFirstAndGet 0x00409760` |
| `0x004fd081`, `0x004fd0cd` | `CSPtrSet__Remove 0x004e5bd0` |
| `0x004fd08c` | `CGenericActiveReader__dtor 0x0044b1d0` |
| `0x004fd097` | `CDXMemoryManager__Free 0x00549220` |
| `0x004fd0b3` | `CGenericActiveReader__SetReader 0x00401000` |
| `0x004fd0dd` | `CUnit__SpawnProfileDropPickup 0x004fd230` |
| `0x004fd0e9` | `IScript__CallEventId3_OrReset 0x005337e0` |
| `0x004fd12d` | `CEventManager__AddEvent_AtTime 0x0044b370` |
| `0x004fd071`, `0x004fd07b` | child target slot 50 / slot 2 alternatives |
| `0x004fd0d6` | `[unit+0x18c]` object slot 2 |
| `0x004fd0f9` | attached-script scalar deleting destructor slot 1 |
| `0x004fd107` | Unit slot 112 delay getter |

## References

The whole-`.text` rel32 census finds exactly three calls:

| Site | Current name-table owner |
| --- | --- |
| `0x0041b5a0` | `CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph` |
| `0x0042882d` | [`CComponent__HandleTriggerEventAndMoveToOffset`](../Component.cpp/CComponent__HandleTriggerEventAndMoveToOffset.md) |
| `0x004d38d0` | [`CPod__TryDestroyedCleanupAndResetDeploymentGraph`](../Pod.cpp/CPod__TryDestroyedCleanupAndResetDeploymentGraph.md) |

The image-wide little-endian operand scan finds zero absolute dword encodings
of `0x004fd040`; the three rel32 calls are the complete direct-reference set.

## Manager boundary and failure behavior

This helper owns the tuple and its pre-queue effects. The shared manager owns
clock normalization, ring placement, allocation, dispatch, and failure policy.
`AddEvent_AtTime` is source-void: invalid-manager and pool-exhaustion paths log
and return, null targets and times above 1,000,000 seconds return without
queueing, and callers receive no success flag. This helper does not roll back
its completed teardown if queue insertion fails.

## Open questions

- Authored `Unit.cpp` method and event-enum spelling are unavailable; the saved
  function name remains a bounded research label.
- Concrete object types in the `+0x19c` and `+0x18c` sets, and the gameplay
  conditions that populate them, are not established here.
- Runtime side effects inside profile-drop creation and slot-2 cleanup remain
  bounded to their existing named static owners; no rebuild parity is claimed.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x004fd040`–`0x004fd139` is not
  `70a795dd…7ae4924`, the body is not 250 bytes / 89 instructions, or the final
  instruction stops being plain `ret`.
- The direct-reference census is not exactly the three calls above, or an
  absolute `0x004fd040` dword appears.
- The queue tuple stops being `(2000, this, mTime+slot112(), 0, null, null)`.
- CComponent, CGillMHead, or CPod slot 112 stops resolving to the `0.05f` stub,
  slot 0 stops resolving to `CUnit__HandleEvent`, or slot 2 stops resolving to
  `0x004f95d0`.
- Event 2000 no longer reaches the retail `CComplexThing` shutdown arm through
  the Unit/Actor default chain.

## Reproduction

Run read-only from the repository root after verifying the official specimen:

```bash
sha256sum ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup
python ./tools/disasm_va.py ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x004fd040 --count 89 --bytes
python ./tools/call_xref_scan.py ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x004fd040 0x0044b370
python ./tools/operand_scan.py ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x004fd040 0x000007d0 --window 8
python ./tools/pe_read_va.py ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x005d8578 --count 4 --as float
```
