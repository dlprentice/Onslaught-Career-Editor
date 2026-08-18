# IScript function map

Status: active static function map
Last updated: 2026-08-18 (event-id 2 / BSS scratch `0x0089c528` closed)
Source File: `C:\dev\ONSLAUGHT2\MissionScript\IScript.cpp` (SEH `__FILE__`
pointer `0x0064fa40` read out of `IScript__PostEvent`) | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — every byte below was re-read from the pristine specimen at
file offset VA − 0x400000 with `tools/disasm_va.py`; whole-image scans by
`tools/call_xref_scan.py` / `tools/operand_scan.py`; RTTI identities by a
COLOC → TypeDescriptor → ClassHierarchyDescriptor walk over the specimen's
`.rdata`. Function names are the live Ghidra name table (db.18627 lineage);
the byte contracts below are independent of the names.

## Shape

`IScript` is a mission-script runtime object. Its RTTI chain
(CompleteObjectLocator `0x00619588` → TypeDescriptor `0x0064fa28` →
`.?AVIScript@@`) names three bases: `IScript`, `CMonitor`, `IListener`
(ClassHierarchyDescriptor `0x00619578`, base array `0x00619568`). Its vftable
is at `0x005e4f08` (the dword before it, `0x005e4f04`, is the COLOC pointer):

| Slot | Address | Name |
| --- | --- | --- |
| 0 | `0x005385e0` | `IScript__HandleMessage` — the scheduled-event handler this map covers |
| 1 | `0x00533430` | `IScript__ScalarDeletingDestructor` |
| 2 | `0x00533810` | `IScript__VFunc_2_00533810` |

The dword at `0x005e4f14` (just past slot 2) is **not** a slot: it is the
float constant `57.29578f` = `180/π` (`RAD2DEG`), read by
`fmul dword [0x005e4f14]` at `0x00534718`. The next COLOC (`0x006195d8`,
`CVM`) sits at `0x005e4f18`.

Delivery: `CEventManager__Flush` executes
`event->[+0] target->vftable[0](target, event)` for each due event
([`CScriptEventNB.cpp.md`](CScriptEventNB.cpp.md) → "Message 0x7d0 fire
path"), and `IScript__HandleMessage` is exactly that slot-0 handler. The
post side of the same chain — `IScript__PostEvent` (`0x005383c0`) cloning the
name value into a `CPostEventData` and scheduling event `0x7d0` against the
`CScriptEventNB` singleton — is byte-closed in
[`CScriptEventNB.cpp.md`](CScriptEventNB.cpp.md) and not repeated here.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005385e0` | `IScript__HandleMessage` | `56 57 8bf9 8b4c240c 0fbf4104 2dd0070000 0f84a2000000 48 7448 48 0f859f000000 …` | `ret 4`; one arg = message struct at `[esp+0xc]`. **Signed** word dispatch `movsx eax, word [msg+4]; sub eax,0x7d0`: `0x7d0` (2000) → waypoint arm, `0x7d1` (2001) → destroyed arm, `0x7d2` (2002) → state arm, anything else returns. HIGH on the dispatch shape; the arms are byte-mapped below. |
| `0x00538470` | `CScriptEventNB__UpdateWaypointFollowing` *(owner review)* | `8b4614 8b4e08 83c01c d900 d8611c d94004 d86120 d9c0 d8c9 d9c2 d8cb 8b4134 … d9fa … d905a08b5d00 … a810 … ff9078010000 … a900000020 … d905bc855d00 …` | Distance check: `[[this+0x14]+0x1c]` (waypoint) minus `[[this+8]+0x1c]` (entity) in 2D, `fsqrt`; thresholds default `2.0f` (`0x005d8ba0`), large-unit `4.0f` (`0x005d85bc` behind `test eax,0x20000000`), vtable `+0x178` override behind `test al,0x10`. On arrival advances `[this+0x14] = [waypoint+0x3c]`; self-loop prints `"ERROR: Waypoint points to previous"` (`0x0064fe50`) via `CConsole__Printf` (`0x00441740`). See the owner review below. |

### The three message arms (byte-exact)

**2000** (`je 0x538699`): `mov ecx,edi; call 0x538470` — re-runs
`UpdateWaypointFollowing` on the same `this`; `ret 4`.

**2001** (`0x00538642`): `esi = [msg+0xc]`; null returns. Then
`push esi; mov ecx,0x0089c5e0; call 0x539910`
(`CScriptObjectCode__CopyState`),
`push esi; lea ecx,[edi+0x28]; call 0x004e5bd0` (`CSPtrSet__Remove` from the
IScript's own `+0x28` set), `mov edx,[esi]; push 1; mov ecx,esi;
call [edx+4]` (virtual delete of the payload with flags = 1), then a state
selector `cmp [0x008a9ac0],4`: `==4` → `mov ecx,0x0089c5e0; call 0x539980`
(`CScriptObjectCode__Reset`); else → `push [0x0089c7f4];
mov ecx,0x0089c5e0; call 0x539ae0` (`CScriptObjectCode__GotoInstruction`);
`ret 4`. The 2001 payload is the destroyed-object notification.

**2002** (`0x00538601`): guard `mov eax,[0x0089c7f0]; test eax,eax;
jne return`; `cmp [0x008a9ac0],4`: `==4` → `mov ecx,0x0089c5e0;
call 0x539980` (`CScriptObjectCode__Reset`); else → `mov eax,[edi+0xc];
push 0; push 0x0089c528; push 2; push eax; mov ecx,0x0089c5e0;
call 0x539990` (`CScriptObjectCode__CallEvent`); `ret 4`.

### `CScriptEventNB__UpdateWaypointFollowing` — owner review (not yet a rename)

The `CScriptEventNB__` prefix is mis-owned, byte-proven:

- Its teardown arms all load `mov ecx,0x0089c5e0` — the **CScriptObjectCode**
  singleton, never the `CScriptEventNB` singleton `0x0089c590` (the
  whole-image immediate census of `0x0089c590` finds only the
  register/post/lifecycle sites listed in
  [`CScriptEventNB.cpp.md`](CScriptEventNB.cpp.md)).
- Its only caller is `IScript__HandleMessage`, which passes its own `this`
  (`mov ecx,edi` at `0x00538699`).
- Its tail reschedules against **itself**: `push edi(0); push edi(0);
  lea ecx,[esp+0x18]; push edi(0); push ecx(&time); push esi(this);
  push 0x7d0; mov ecx,0x00672fc8; mov [esp+0x28],0xbf800000;
  call 0x0044b370` = `CEventManager__AddEvent_AtTime(2000, this, &-1.0f
  NEXT_FRAME, 0 START_OF_FRAME, data=0, re_use=0)` at `0x005385b8..0x005385d3`.
  So the waypoint follower is a self-sustaining next-frame loop: message 2000
  → move one step → reschedule 2000 against `this` → `Flush` → message 2000.

Candidate name `IScript__UpdateWaypointFollowing`; do not promote outside a
name cohort. The older decompiler gloss in
[`ScriptEventNB.cpp.md`](ScriptEventNB.cpp.md) claiming this function
rescheduled with `(2000, this, &nextFrame, 0, 0, 0)` is **confirmed** by the
tail above; the same document's `CScriptEventNB__HandleMessage` label was
already corrected to `IScript__HandleMessage`.

## Script-system vtable cluster (RTTI COLOC → TypeDescriptor walk)

Adjacent `.rdata` vftables, each preceded by its COLOC pointer (MSVC
`vtable-4` layout), recovered from the specimen with their base chains
(`ClassHierarchyDescriptor`). The same walk, executed independently, also
names `CStringDataType` (`0x005e4e4c`, COLOC `0x006194e8`) — the event-name
object class — and the `CMonitor` root (`0x005d92d4`, COLOC `0x0060cbe0`);
see [`CScriptEventNB.cpp.md`](CScriptEventNB.cpp.md) and
[`CMonitor.cpp.md`](CMonitor.cpp.md).

| COLOC | vftable | Class | RTTI name | Bases |
| --- | --- | --- | --- | --- |
| `0x00619448` | `0x005e4ea4` | `CFloatDataType` | `.?AVCFloatDataType@@` | `CFloatDataType`, `CDataType` |
| `0x00619538` | `0x005e4ef8` | `CEventFunction` | `.?AVCEventFunction@@` | `CEventFunction`, `CMonitor`, `IListener` |
| `0x00619588` | `0x005e4f08` | `IScript` | `.?AVIScript@@` | `IScript`, `CMonitor`, `IListener` |
| `0x006195d8` | `0x005e4f1c` | `CVM` | `.?AVCVM@@` | `CVM`, `CMonitor`, `IListener` |
| `0x00619608` | `0x005e4f2c` | `IListener` | `.?AVIListener@@` | `IListener` |
| `0x00619658` | `0x005e4f34` | `CPostEventData` | `.?AVCPostEventData@@` | `CPostEventData`, `CMonitor`, `IListener` |
| `0x006196a8` | `0x005e4f44` | `CScriptEventNB` | `.?AVCScriptEventNB@@` | `CScriptEventNB`, `CMonitor`, `IListener` |

Measured slot facts from the same walk: `IListener`'s single slot (`0x005e4f2c`)
is the CRT `__purecall` stub `0x0055df1f`; `CPostEventData` slot 2 is
`CMonitor__Shutdown_Core` (`0x004bacb0`, correcting the older
[`ScriptEventNB.cpp.md`](ScriptEventNB.cpp.md) claim of `0x004bac40`); the
`CEventFunction` and `CVM` tables carry the same `NoOpOneArg` /
scalar-deleting-destructor / `Shutdown_Core` shape. This cluster is a natural
follow-on cohort for the `SET_DATA_POINTER` vftable typing already promoted at
db.18627.

## Open questions (cheapest falsifier first)

- The name-key object's class: CLOSED (2026-08-17) — the COLOC walk names it
  `CStringDataType` (`.?AVCStringDataType@@`, vtable `0x005e4e4c`):
  `vtable+0x38` = `SharedVFunc__ReturnField04_0052f540` (name getter returning
  `[this+4]`) and `vtable+0x48` = `CStringDataType__Clone` (`0x0052f2c0`).
  The `vtable+0x38`/`+0x48` reads in `IScript__PostEvent` and
  `CScriptEventNB__RegisterEventListener` therefore take a `CStringDataType`
  key.
- The dispatch globals `0x008a9ac0` (state selector) and `0x0089c7f0` (2002
  guard): which state machine owns them.
- The 2002 arm's `CScriptObjectCode__CallEvent` invocation
  (`this=0x0089c5e0`, args `[edi+0xc], 2, &0x0089c528, 0`): CLOSED as
  event-id **2** of the 13-slot `CMissionScriptObjectCode+0x14` table.
  `0x0089c528` is a BSS scratch pointer shared with the other IScript
  CallEvent wrappers (see `CScriptObjectCode.cpp.md`). Authored name of
  id 2 is still open.
