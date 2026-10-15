# ScriptEventNB.cpp - Function Mappings

Source File: retained MissionScript/ScriptEventNB.cpp mapping | Binary: BEA.exe (superseded byte claims; current owners linked below)

Status: retired evidence; current byte owners are linked below
Last updated: 2026-09-27 (current listener/cleanup identities linked; historical rows preserved)
Summary: preserved script-event mapping history, superseded for current byte contracts.

The September 27 container identity correction (private RE archive: `reverse-engineering/ghidra/README.md`)
resolves the historical list rows below as `GenericSPtrSet__Remove` and
`GenericSPtrSet__RemoveAll`; their retired packet wording remains unchanged.
<!-- ghidra-name-drift-accepted: 0x004e5bd0 GenericSPtrSet__Remove (2026-09-27) -->
<!-- ghidra-name-drift-accepted: 0x004e5c60 GenericSPtrSet__RemoveAll (2026-09-27) -->

The retained `CConsole__Printf` label at `0x00441740` now resolves to
`CDebugLog__Printf`; see [the current logger contract](string-helpers.md#debug-log-ownership-and-history--september-19).
Its older table and pseudocode below remain historical evidence.
<!-- ghidra-name-drift-accepted: 0x00441740 CConsole__Printf (2026-09-19) -->

> **Superseded for current byte contracts (2026-08-17).** The active
> byte-level maps are
> [`CScriptEventNB.cpp.md`](CScriptEventNB.cpp.md) (register/post/handle,
> world loader, and the message-0x7d0 fire path) and
> [`IScript.cpp.md`](IScript.cpp.md) (`IScript__HandleMessage`, the
> waypoint-following owner review, and the script-system vtable cluster).
> This page is retained for its name-correction provenance and the Wave586
> read-back record only; its decompiler-derived pseudocode and its
> `0x005e4f34` slot table carry stale values (for example slot 2 is
> `CMonitor__Shutdown_Core` `0x004bacb0`, not `0x004bac40`) and must not be
> read as current byte truth. Its `CRelaxedSquad` base-class labels (overview,
> the 0x10-byte `CreateListenerSet` reading, and the `eventListener` field
> gloss) are refuted by the 2026-08-17 RTTI COLOC walk: the event-listener
> base is `CMonitor : IListener`, never `CRelaxedSquad`.

> Source file: `MissionScript/ScriptEventNB.cpp`
> Debug path: `[maintainer-local-source-export-root]\MissionScript\ScriptEventNB.cpp` (0x0064fe98)
> Last updated: 2026-05-19

> **September 27 deleting-entry recheck:** `0x005386b0 CPostEventData__scalar_deleting_dtor`; `0x00538780 CScriptEventNB__scalar_deleting_dtor`. The compiler-entry audit (private RE archive: `reverse-engineering/ghidra/README.md`) binds these entries to pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, using the exact wrapper, raw RTTI holders and normal-path CMonitor teardown chain. This verifies entry identity; it does not revalidate every older cleanup, prototype or runtime claim.

Historical table spellings below remain unchanged; the identities above supersede them.
<!-- ghidra-name-drift-accepted: 0x005386b0 CPostEventData__scalar_deleting_dtor (2026-09-27) -->
<!-- ghidra-name-drift-accepted: 0x00538780 CScriptEventNB__scalar_deleting_dtor (2026-09-27) -->

> **September 27 current identities:** `0x005385e0 IScript__HandleEvent` and
> `0x00538c70 CScriptEventNB__HandleEvent` supersede the older spellings below.
> The listener audit (private RE archive: `reverse-engineering/ghidra/README.md`)
> proves the interface identity from pristine `BEA.exe.original.backup`, SHA-256
> `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
> this does not revalidate the retained Wave586 behavior or signatures.
<!-- ghidra-name-drift-accepted: 0x005385e0 IScript__HandleEvent (2026-09-27) -->
<!-- ghidra-name-drift-accepted: 0x00538c70 CScriptEventNB__HandleEvent (2026-09-27) -->

> **September 27 cleanup identity:** `0x005386d0 CPostEventData__dtor_body`
> supersedes the neutral `DestructorBody_005386d0` label. The cleanup audit (private RE archive: `reverse-engineering/ghidra/README.md`)
> binds the complete 105-byte body to pristine `BEA.exe.original.backup`, SHA-256
> `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, through
> fresh RTTI, the sole matching deletion wrapper, own primary-vptr and normal
> CMonitor teardown. The old July extent included padding; 29 instructions end
> at exclusive `0x00538739`. Names do not certify saved types or full cleanup
> behavior. The retained `scripteventnb`/`scripteventnb-wave586` tags are historical
> subsystem/wave groupings, also present on IScript and the CPostEventData wrapper;
> they do not assert exclusive CScriptEventNB ownership.

<!-- ghidra-name-drift-accepted: 0x005386d0 CPostEventData__dtor_body (2026-09-27) -->

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](_index.md#the-name-corrections-of-2026-07-28).
Old cell text is quoted below rather than deleted, so a reader who remembers the
withdrawn label can tell it was corrected and not lost.

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x0044b370` | `FUN_0044b370` | `CEventManager__AddEvent_AtTime` | placeholder replaced; this address carries a name now |
| `0x005385e0` | `CScriptEventNB__HandleMessage` | `IScript__HandleMessage` | Class moved, suffix unchanged. UNKNOWN on what evidence — no tracked ledger records this rename; the 2026-07-27 export is the only artefact that carries it. |
| `0x005386b0` | `CScriptEventNB__ScalarDeletingDestructor` | `CPostEventData__ScalarDeletingDestructor` | Class moved, suffix unchanged. MEASURED from the pristine specimen: `CPostEventData`'s vtable `0x005e4f34` slot 1 is this address (second demotion ledger (private RE archive: `reverse-engineering/binary-analysis/name-grading-ledger-2026-07-27-demotion2.md`)). |
| `0x005386d0` | `CScriptEventNB__Destructor` | `DestructorBody_005386d0` | **Demotion, not a rename.** The class name was proven false and withdrawn on 2026-07-27; see the second demotion ledger (private RE archive: `reverse-engineering/binary-analysis/name-grading-ledger-2026-07-27-demotion2.md`). No positive name is claimed. |
| `0x00538ea0` | `CScriptObjectCode__scalar_deleting_dtor` | `CMissionScriptObjectCode__scalar_deleting_dtor` | class prefix moved; suffix unchanged |
| `0x00549220` | `OID__FreeObject` | `CDXMemoryManager__Free` | class prefix and suffix both moved |

Where a row's **suffix** moved rather than only its class prefix, the behavioural
text beside it in this note was written for the old name. This sweep corrected
names against the export and re-derived no behaviour, so read any such gloss as
unverified against the new name until it is re-measured.

---

## Overview

Non-blocking script event system for mission scripting. "NB" stands for "Non-Blocking" - these are script events that execute without pausing the game loop, allowing waypoint following, message handling, and event posting to continue in parallel.

**Key Classes:**
- `CScriptEventNB` - Non-blocking script event manager
- Related to `CEventFunction` (event callbacks) and `CRelaxedSquad` (base class)

**Inheritance:**
- `CScriptEventNB` inherits from a base class with vtable at 0x005e4f34
- Uses `CSPtrSet` for managing event listener lists

---

## Functions (13 total)

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x00538760 | CScriptEventNB__Init | WAVE586 | `void __fastcall ... (void * event_nb)`; sets vtable, zeroes fields |
| 0x005386d0 | DestructorBody_005386d0 | WAVE586 | `void __fastcall ... (void * event_nb)`; cleans up listener set and monitor base |
| 0x005386b0 | CPostEventData__ScalarDeletingDestructor | WAVE586 | `void * __thiscall ... (void * this, byte delete_flags)` |
| 0x00538780 | CScriptEventNB__ScalarDeletingDestructor2 | WAVE586 | `void * __thiscall ... (void * this, byte delete_flags)` |
| 0x00538950 | CScriptEventNB__BaseDestructor | WAVE586 | `void __fastcall ... (void * event_nb)`; restores vtable and shuts down monitor base |
| 0x00538860 | CScriptEventNB__CreateListenerSet | WAVE586 | `void __fastcall ... (void * event_nb)`; allocates the listener set. Renamed 2026-08-17 to agree with the behaviour this row already recorded; the class keeps its RTTI anchor. |
| 0x00538960 | CScriptEventNB__RegisterEventListener | WAVE586 | `void * __thiscall ... (void * this, void * event_name_ref, void * event_function)` |
| 0x005387b0 | CScriptEventNB__ClearListenerEntry | WAVE586 | `void __fastcall ... (void * listener_entry)`; clears one listener entry. Renamed 2026-08-17 from the plural `ClearEventListeners`, which contradicted this row's own singular reading and its `listener_entry` parameter. |
| 0x005388d0 | CScriptEventNB__Shutdown | WAVE586 | `void __fastcall ... (void * event_nb)`; destroys all listener entries |
| 0x00538470 | IScript__UpdateWaypointFollowing | WAVE586 | `void __fastcall ... (void * event_nb)`; waypoint following logic with distance checks |
| 0x005385e0 | IScript__HandleMessage | WAVE586 | `void __thiscall ... (void * this, void * message)`; message IDs 2000, 0x7d1, 0x7d2 |
| 0x00538b70 | CScriptEventNB__PostEvent | WAVE586 | `void __thiscall ... (void * this, char * event_name)`; posts event to matching listeners |
| 0x00538c70 | CScriptEventNB__HandleEventMessage | WAVE586 | `void __thiscall ... (void * this, void * message)`; handles event-manager payload message 2000 |

Note: `0x00538ea0` and `0x00538ec0` were previously attributed to this file, but they are now mapped to `CScriptObjectCode` destructor/constructor rows (see `ScriptObjectCode.cpp.md`).

The current static contract ties `CScriptEventNB__RegisterEventListener`,
`CScriptEventNB__PostEvent`, and `CScriptEventNB__HandleEventMessage` to the
path `IScript__ScheduleEvent` → `CScriptEventNB__PostEvent` →
`CEventFunction__Execute` → `CScriptObjectCode__CallEventDirect`. Runtime event
outcomes and exact listener/payload layout remain separate proof.

## Wave586 Static Read-Back

Wave586 hardened the CScriptEventNB listener/event-manager tranche at `0x00538470` through `0x00538c70`. The saved signatures classify ECX-only helpers as `__fastcall`, one-stack-argument methods as `__thiscall`, deleting destructor wrappers with a `byte delete_flags` parameter, and the named event post method with a `char * event_name` argument.

Read-back evidence: `ApplyScriptEventNBWave586.java` dry/apply/final dry reported `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=13 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `13` metadata rows, `13` tag rows, `18` xref rows, `5577` instruction rows, `13` decompile rows, and `72` vtable rows. The queue refresh after Wave586 reports `6093` functions, `2978` commented, `3115` commentless, `1387` exact-undefined signatures, `1116` `param_N` signatures, and next queue head `0x00538ea0 CMissionScriptObjectCode__scalar_deleting_dtor`.

The bounded evidence is static retail Ghidra state only. Runtime mission-script behavior remains unproven, script corpus coverage remains separate evidence, exact `CScriptEventNB`/listener/message/payload/waypoint layouts remain open, and 0x00538ea0 and 0x00538ec0 remain CScriptObjectCode rows rather than ScriptEventNB rows.

---

## Function Details

### CScriptEventNB__Init (0x00538760)

**Constructor** - Initializes the CScriptEventNB object.

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`, block 1).*

**Key Details:**
- Very simple initialization - sets vtable and zeroes two fields
- Vtable pointer: 0x005e4f44

---

### CScriptEventNB__Destructor (0x005386d0)

**Destructor** - Cleans up the event listener and calls base destructor.

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`, block 2).*

**Key Details:**
- Resets vtable to base class before cleanup
- Cleans up field_0x08 if allocated
- Calls base monitor shutdown helper CMonitor__Shutdown (formerly FUN_004bac40)

---

### CScriptEventNB__CreateEventListener (0x00538860)

**Creates Event Listener** - Allocates a new CRelaxedSquad event listener.

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`, block 3).*

**Key Details:**
- Allocates 0x10 (16) bytes for a CRelaxedSquad object
- Object type: 0x76
- Line number: 0x42 (66) in source file
- Stores result at this+0x08

---

### CScriptEventNB__RegisterEventListener (0x00538960)

**Registers Event Listener** - Complex function that registers a listener by matching event names.

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`, block 4).*

**Key Details:**
- Creates listeners with size 0x18 (24) bytes, type 0x76
- Creates wrappers with size 4 bytes
- Line numbers: 0x19 (25), 0x68 (104), 0x11 (17) in source file
- Uses string comparison via vtable call at offset 0x38 (GetName)
- Clone function at vtable offset 0x48

---

### CScriptEventNB__UpdateWaypointFollowing (0x00538470)

**Waypoint Following Update** - Updates the entity following a waypoint path.

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`, block 5).*

**Key Details:**
- Calculates 2D distance to current waypoint
- Arrival thresholds: 2.0f (default), 4.0f (large units), or custom via vtable
- Schedules event ID `2000` for `NEXT_FRAME` (`-1.0f`), so this is a
  next-frame waypoint check rather than a 2000 ms timer
- Detects infinite waypoint loops
- Error message at 0x0064fe50: "ERROR: Waypoint points to previous"

---

### CScriptEventNB__HandleMessage (0x005385e0)

**Message Handler** - Handles three message types.

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`, block 6).*

**Key Details:**
- Message ID 2000: next-frame waypoint update event
- Message ID 0x7d1 (2001): Object destroyed notification
- Message ID 0x7d2 (2002): Unknown purpose, state-dependent
- Global state variable DAT_008a9ac0 controls behavior

---

### CScriptEventNB__PostEvent (0x00538b70)

**Posts Event** - Posts a named event to all registered listeners.

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`, block 7).*

**Key Details:**
- Warns if posting event when not "game playing"
- Uses string comparison to find matching listeners
- Sets triggered flag at listener+0x14 (offset 5 in int* terms)
- Iterates through all CEventFunction objects and executes them
- Warning message at 0x0064fecc: "Warning: No listeners for posted event '%s'"
- Special event name: "game playing" (at 0x0062c258)

---

### Moved Mapping: CScriptObjectCode Constructor (0x00538ec0)

Older notes attributed `0x00538ec0` to a `CScriptEventNB__LoadFromBuffer` row. Current Ghidra state maps this function to `CScriptObjectCode__CScriptObjectCode`, with `0x00538ea0` as the adjacent `CScriptObjectCode__scalar_deleting_dtor`. Keep the bytecode/symbol-table/load-from-buffer details in `ScriptObjectCode.cpp.md`, not in this file.

---

## Related Data

### Vtables

| Address | Name | Notes |
|---------|------|-------|
| 0x005e4f34 | CScriptEventNB base-vtable prefix | Prefix includes no-op/delete wrapper/monitor slots plus `HandleEventMessage`, `ScalarDeletingDestructor2`, and `DestroyAllEvents` |
| 0x005e4f44 | CScriptEventNB main-vtable prefix | Set by `CScriptEventNB__Init`; slots 0-2 are `HandleEventMessage`, `ScalarDeletingDestructor2`, and `DestroyAllEvents` |
| 0x005e4f54 | Adjacent CScriptObjectCode vtable/data region | Not a proven CScriptEventNB derived vtable; current function ownership moves to `ScriptObjectCode.cpp.md` |

Wave586 vtable exports deliberately treat only the listed CScriptEventNB prefix slots as evidence. Later raw pointer rows enter adjacent data/vtable regions and must not be counted as CScriptEventNB slots without a separate boundary pass.

### Vtable at 0x005e4f34 (Base)

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x004014c0 | (scalar deleting destructor wrapper) |
| 0x04 | 0x005386b0 | ScalarDeletingDestructor |
| 0x08 | 0x004bac40 | Base class function |
| 0x0c | 0x006196a8 | (unknown) |
| 0x10 | 0x00538c70 | HandleEventMessage |
| 0x14 | 0x00538780 | ScalarDeletingDestructor2 |
| 0x18 | 0x005388d0 | DestroyAllEvents |
| ... | ... | ... |

### Vtable at 0x005e4f44 (Main)

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x00538c70 | HandleEventMessage |
| 0x04 | 0x00538780 | ScalarDeletingDestructor2 |
| 0x08 | 0x005388d0 | DestroyAllEvents |
| ... | ... | ... |

---

## Class Layout (Partial)

### CScriptEventNB

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | void* | vtable | Virtual function table |
| 0x04 | int | field_0x04 | Unknown, zeroed in Init |
| 0x08 | void* | eventListener | CRelaxedSquad event listener |
| 0x0c | void* | field_0x0c | List pointer |
| 0x14 | void* | currentWaypoint | Current waypoint in path |
| 0x18 | int | field_0x18 | Waypoint state flag |
| 0x1c | int | field_0x1c | State flag |
| 0x20 | void* | field_0x20 | Associated object |
| 0x24 | void* | thingRef | IScript thing reference |
| ... | ... | ... | ... |

Offsets formerly listed from `0x58` through `0x6c` came from the now-moved `CScriptObjectCode__CScriptObjectCode` row and are not retained here as CScriptEventNB layout evidence.

---

## Message IDs

| ID | Hex | Purpose |
|----|-----|---------|
| 2000 | 0x7d0 | Next-frame waypoint update event |
| 2001 | 0x7d1 | Object destroyed notification |
| 2002 | 0x7d2 | Unknown state-dependent action |

---

## Error Messages

| Address | Message | Context |
|---------|---------|---------|
| 0x0064fe50 | "ERROR: Waypoint points to previous" | Waypoint infinite loop detected |
| 0x0064fecc | "Warning: No listeners for posted event '%s'" | Event posted with no listeners |

---

## Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x0062c258 | "game playing" | Special event name - no warning |
| 0x0064fe98 | "[maintainer-local-source-export-root]\\MissionScript\\ScriptEventNB.cpp" | Debug path |
| 0x0064fe80 | ".?AVCScriptEventNB@@" | RTTI class name |

---

## Cross-References

### Called By
| Address | Function | Notes |
|---------|----------|-------|
| Various | Script system | Part of mission scripting |

### Calls
| Address | Function | Notes |
|---------|----------|-------|
| 0x00549220 | CDXMemoryManager__Free | Memory deallocation |
| 0x004e5bd0 | CSPtrSet__Remove | Remove entry from list (returns node to pool) |
| 0x004e5c60 | CSPtrSet__Clear | List cleanup |
| 0x004bac40 | CMonitor__dtor_base | Base monitor cleanup helper (formerly `FUN_004bac40`) |
| 0x0044b370 | CEventManager__AddEvent_AtTime | Event scheduling; this call uses `NEXT_FRAME` |
| 0x00441740 | CConsole__Printf (`FUN_00441740`) | Debug/error output |

---

## Notes

1. **Non-Blocking Design**: The "NB" suffix indicates these script events don't
   block the game loop. Waypoint following and event posting happen
   asynchronously; the waypoint update reschedules event ID `2000` for the next
   frame.

2. **Event System**: The system uses a publisher-subscriber pattern where events are posted by name and listeners execute their CEventFunction callbacks when their name matches.

3. **Waypoint System**: Entities can follow waypoint paths with arrival detection based on distance thresholds. Different unit types have different thresholds (2.0f default, 4.0f for large units).

4. **Memory Management**: Uses OID__AllocObject with type 0x76 for most allocations. Objects are typically 0x10 (16), 0x18 (24), or 0x20 (32) bytes.

5. **RTTI**: The ".?AVCScriptEventNB@@" string at 0x0064fe80 is MSVC RTTI type information for the class.

6. **Related Files**: Works closely with ScriptFunctionManager.cpp (0x00650040) and EventFunction.cpp for the complete scripting system.
