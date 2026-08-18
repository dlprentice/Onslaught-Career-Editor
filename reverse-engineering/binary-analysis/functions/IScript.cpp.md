# IScript function map

Status: active static function map
Last updated: 2026-08-18 (PlayAnimationWait resumes via FinishedPlaying)
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
| `0x005385e0` | `IScript__HandleMessage` | `56 57 8bf9 8b4c240c 0fbf4104 2dd0070000 0f84a2000000 48 7448 48 0f859f000000 …` | `ret 4`; one arg = message struct at `[esp+0xc]`. **Signed** word dispatch `movsx eax, word [msg+4]; sub eax,0x7d0`: `0x7d0` (2000) → waypoint arm, `0x7d1` (2001) → **CVM wait-resume**, `0x7d2` (2002) → timer arm, anything else returns. HIGH on the dispatch shape; the arms are byte-mapped below. |
| `0x00538470` | `CScriptEventNB__UpdateWaypointFollowing` *(owner review)* | `8b4614 8b4e08 83c01c d900 d8611c d94004 d86120 d9c0 d8c9 d9c2 d8cb 8b4134 … d9fa … d905a08b5d00 … a810 … ff9078010000 … a900000020 … d905bc855d00 …` | Distance check: `[[this+0x14]+0x1c]` (waypoint) minus `[[this+8]+0x1c]` (entity) in 2D, `fsqrt`; thresholds default `2.0f` (`0x005d8ba0`), large-unit `4.0f` (`0x005d85bc` behind `test eax,0x20000000`), vtable `+0x178` override behind `test al,0x10`. On arrival advances `[this+0x14] = [waypoint+0x3c]`; self-loop prints `"ERROR: Waypoint points to previous"` (`0x0064fe50`) via `CConsole__Printf` (`0x00441740`). See the owner review below. |

| `0x00535cd0` | `IScript__Die` | `8b4910 6a00 6a00 8d442408 6a00 50 51 68d2070000 b9c82f6700 c7442418000080bf e87956f1ff c20c00` | `ret 0xc`; zero direct `E8` (native 13). `AddEvent_AtTime(0x7d2, [this+0x10], NEXT_FRAME)` — thing-event `START_DIE_PROCESS` on the attached thing. 48 compiled uses, all argc 0. HIGH. Distinct from IScript `HandleMessage` 2002 (`timer`) and from `CGame` `FINISHED_PANNING`. |
| `0x00537c70` | `IScript__Pause` | `8b442404 538bd9 568b08 8b11 ff5234 d95c240c 68a8070000 6840fa6400 6a18 6828020000 … c20c00` | `ret 0xc`. `args[0]->vtable[+0x34]()` (float), snapshot a 0x228 `CVM`, `AddEvent_AtTime(2001, this, mTime+delay, data=CVM)`, then `[0x0089c800]=1`. HIGH. |
| `0x005351d0` | `IScript__PlayAnimationWait` | `538bd9 56578b4310 8b7030 8b4074 85c0 7404 3bc3 7412 6864fb6400 … 897338 c20c00` | `ret 0xc`. Plays via `CMesh__FindAnimationIndexByName` + thing `vtable[+0xf0]`; snapshots a `CVM` into `[this+0x38]`; sets the stop flag. Resume is `IScript__RestoreSavedStateAndGotoInstruction`. HIGH. |
| `0x005375f0` | `IScript__PlayCharMessageWait` | `6aff 6849735d00 64a1 … 68d1070000 … c7442440cdcc4c3d e8c36afaff … c20c00` | `ret 0xc`. Registry 36. Snapshot + `GetNextFreeEvent` + `CScheduledEvent__Set(2001, 0.05f, this, CVM)` + `CMessage__ctor_base` / `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`. HIGH on the snapshot and event id. |
| `0x005378e0` | `IScript__PlayPCharMessageWait` | `6aff 68a9735d00 64a1 … 68d1070000 … c7442420cdcc4c3d e8c767faff … c20c00` | `ret 0xc`. Registry 91. Same CVM + 2001 `Set` shape as `PlayCharMessageWait`, then a seven-arg `CMessage` with the extra script dword. HIGH on the snapshot and event id. |
| `0x00537e40` | `IScript__FollowWaypointWait` | `538bd9 55bd01000000 8b4318 56 3bc5 57 0f8464010000 … 68d0070000 … c20c00` | `ret 0xc`. Early-out if `[this+0x18]==1`. Snapshot; `[this+0x1c]=1`, `[this+0x20]=CVM`, `[this+0x18]=1`; `AddEvent_AtTime(2000, this, NEXT_FRAME)`. HIGH. |
| `0x00533840` | `IScript__RestoreSavedStateAndGotoInstruction` | `568bf1 8b4638 85c0 7453 50 b9e0c58900 e8bb600000 8b4638 8d4e28 50 e86f23fbff … c3` | Zero-arg `ret`. If `[this+0x38]==0` return. Else `CopyState(+0x38)`, `CSPtrSet__Remove(+0x28)`, delete, `[this+0x38]=0`, then Reset on LEVEL_LOST else `GotoInstruction([0x0089c7f4])`. Same resume as HandleMessage 2001. Only `E8` is `CComplexThing__FinishedPlayingCurrentAnimation` `0x004f45a7`. HIGH. |

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
`ret 4`. The 2001 payload is a **CVM snapshot** (see Wait helpers). The
older "destroyed-object notification" gloss is withdrawn: Pause and both
`Play*MessageWait` natives schedule this same message with `data = CVM`.
Thing-event 2001 (`INIT_SCRIPT` on `CComplexThing`) is a different
receiver.

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
name cohort. Independently re-read 2026-08-18: the only `E8` is still
`0x0053869b` (`mov ecx,edi; call 0x00538470`). A second static witness is
`IScript__FollowWaypoint` (`0x00537d70`, zero direct `E8` — a registry
command) which writes `[this+0x14]`, **zeroes** `[this+0x1c]`, and
schedules the same `AddEvent_AtTime(2000, this, NEXT_FRAME, …)` loop.
`FollowWaypointWait` writes `[this+0x1c]=1` and stores the CVM at
`[this+0x20]`. End-of-chain (`[this+0x14]` advanced to null at
`0x0053850b`): `[this+0x18]=0`, then `cmp [this+0x1c],0` — zero fires
`CreateThingRef` / arrived(); nonzero runs the same CopyState / Remove
`+0x28` / delete / `GotoInstruction` sequence as HandleMessage 2001,
using `[this+0x20]` as the payload. Ready for a future
name-only cohort row; cheapest falsifier is `[ecx] != 0x005e4f08` at
entry. The older decompiler gloss in
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

## Wait helpers — CVM snapshot (byte-exact 2026-08-18)

Five `IScript__*Wait` natives allocate a **0x228-byte** object from
`CDXMemoryManager__Alloc` (`0x005490e0`, pool `0x009c3df0`,
`__FILE__` `0x0064fa40` = `IScript.cpp`) and install the same
construction dance. Independently re-read from pristine `74154bfa…`:

1. `[eax] = 0x005e4f2c` (`IListener`; slot 0 is `CRT__Purecall_0055df1f`).
2. `[eax+4] = [0x0089c5e4]` (singleton `+4`).
3. `[eax] = 0x005d92d4` (`CMonitor`).
4. `[eax+8] = [0x0089c5e8]`; `rep movsd` **0x81** dwords from
   `0x0089c5ec` (singleton `+0xc`) to `eax+0xc` — the inline 128-slot
   operand stack plus the depth dword at `+0x20c`.
5. Copy the six-dword interpreter tail:

   | CVM / singleton | Source | Meaning |
   | --- | --- | --- |
   | `+0x210` | `0x0089c7f0` | running |
   | `+0x214` | `0x0089c7f4` | PC |
   | `+0x218` | `0x0089c7f8` | |
   | `+0x21c` | `0x0089c7fc` | stack-base snapshot |
   | `+0x220` | `0x0089c800` | stop flag (copied **before** the live store) |
   | `+0x224` | `0x0089c804` | `CALLLOCAL` depth |

6. `[eax] = 0x005e4f1c` (`CVM`). Slots: `+0` `0x004014c0`
   (`SharedVFunc__NoOpOneArg_004014c0`, `ret 4`), `+4` `0x00535330`
   (`CVM__ScalarDeletingDestructor`), `+8` `0x004bacb0`
   (`CMonitor__Shutdown_Core`). COLOC at `vtable-4` is `0x006195d8`.

Then `CSPtrSet__AddToTail` (`0x004e5b20`) on `IScript+0x28`, and
`mov dword [0x0089c800], 1` — singleton `+0x220` — so `Run` exits
after the current instruction. A whole-image immediate census of
`0x0089c800` finds **exactly ten** hits, all inside these five
functions (one copy + one store-1 each). No other writer. A sixth
image store of vptr `0x005e4f1c` is
`CScriptObjectCode__InitRuntime` (`0x005398d0`): it installs the
CVM vtable on the **singleton** and zeroes `+4` / `+8` / `+0x20c` /
`+0x210` / `+0x214` / `+0x218` / `+0x21c` / `+0x224`. Different
shape (`mov [eax+0x20c],ecx` then `c7 00 1c 4f 5e 00`); not a Wait
snapshot.

Per-native after the shared ctor:

| Native | Resume |
| --- | --- |
| `Pause` | `fld [0x00672fd0]` (`CEventManager+8` = `mTime`) `fadd` delay; `AddEvent_AtTime(2001, this, &due, data=CVM)` |
| `PlayCharMessageWait` / `PlayPCharMessageWait` | `GetNextFreeEvent` + `CScheduledEvent__Set(2001, 0.05f CLOCK_TICK, this, CVM)` then `CMessage__ctor_base` / insert. The message owns the event; **when** it fires is not claimed here |
| `FollowWaypointWait` | `AddEvent_AtTime(2000, this, NEXT_FRAME)`; `[this+0x1c]=1`, `[this+0x20]=CVM`. Resume is the end-of-chain arm above, not message 2001 |
| `PlayAnimationWait` | `[this+0x38]=CVM` after `CMesh__FindAnimationIndexByName` (`0x004aa630`) + thing `vtable[+0xf0]`. Replaces a prior `+0x38` (Remove `+0x28` + delete). If `[thing+0x74] != this` it prints `FATAL ERROR: Called PlayAnimWait on the non base script object` (`0x0064fb64`) and **continues**. Resume is `IScript__RestoreSavedStateAndGotoInstruction` (`0x00533840`) |

`IScript` ctor (`0x005333b0`, `ret 8`) zeroes `+0x14`, `+0x18`,
`+0x1c`, `+0x24`, `+0x38` and constructs the `CSPtrSet` at `+0x28`.
`+0x18` is the in-flight waypoint loop (both Follow natives set it
to 1; end-of-chain clears it). `+0x1c` is the wait-resume latch.

Thirteen `.text` `push 0x7d1` sites exist. The three IScript wait
schedulers are `0x0053771a`, `0x00537a16`, `0x00537d4c`.
`0x004f42be` is thing `INIT_SCRIPT` (different receiver).
`0x00590913` / `0x00590ab2` are the shader parser (`push 0x7d1` +
string, `call 0x0058c893`) — not events.

## Open questions (cheapest falsifier first)

- The name-key object's class: CLOSED (2026-08-17) — the COLOC walk names it
  `CStringDataType` (`.?AVCStringDataType@@`, vtable `0x005e4e4c`):
  `vtable+0x38` = `SharedVFunc__ReturnField04_0052f540` (name getter returning
  `[this+4]`) and `vtable+0x48` = `CStringDataType__Clone` (`0x0052f2c0`).
  The `vtable+0x38`/`+0x48` reads in `IScript__PostEvent` and
  `CScriptEventNB__RegisterEventListener` therefore take a `CStringDataType`
  key.
- The dispatch globals `0x008a9ac0` and `0x0089c7f0`: CLOSED.
  `0x008a9ac0` is the `EGameState` dword (`references/Onslaught/game.h:42-54`).
  `DAT_008a9a98+0x28`. IScript's `cmp …,4` is `GAME_STATE_LEVEL_LOST`. Sibling writers match the
  rest of the enum: `con_win` stores `5` (`GAME_STATE_LEVEL_WON`), and
  `SetQuit`-shaped sites (`FUN_00429ab0`, `CGame__HandleEvent`,
  `CEngine__MarkDeviceResetPending`, `con_map`) store `9`
  (`GAME_STATE_QUIT`) when the current value is `<= 3` (`GAME_STATE_PLAYING`).
  The adjacent dword `0x008a9acc` is the `SetQuit` partner (those sites write
  `1` = `QT_QUIT_TO_FRONTEND` there). `0x0089c7f0` is not a free flag: it is
  the `CScriptObjectCode` singleton `0x0089c5e0+0x210` (running); `0x0089c7f4`
  is `+0x214` (PC). The 2002 `test [0x0089c7f0]` is therefore "VM already
  running". Wait-helper CVM construction: CLOSED (section above).
- Who reads `IScript+0x38` to resume `PlayAnimationWait`: CLOSED.
  `IScript__RestoreSavedStateAndGotoInstruction` (`0x00533840`) is
  the sole reader. Only `E8` is
  `CComplexThing__FinishedPlayingCurrentAnimation` (`0x004f45a0`):
  `ecx=[this+0x74]; if ecx call Restore; mov eax,1; ret`. That
  function is slot **59** of `CComplexThing` vtable `0x005df784`
  (`0x005df784+0xEC = 0x005df870`) and sits in **26** `.rdata`
  vtables. One direct `E8` at `0x004fdfdd` inside
  `CUnit__HandleDeployAndFireAnimationCompletion`. Cheapest
  falsifier: another `E8` to `0x00533840`.
- When the `Play*MessageWait` `CScheduledEvent` actually fires: open.
  `Set` writes `0.05f` into the event; `CMessage` holds the node.
  Cheapest falsifier: the `CMessageBox` arm that `AddEvent`s or
  `Flush`es that node.
- The 2002 arm's `CScriptObjectCode__CallEvent` invocation
  (`this=0x0089c5e0`, args `[edi+0xc], 2, &0x0089c528, 0`): CLOSED as
  event-id **2** (`timer` in the `0x0064fef8` table). The 13-slot IP is
  `-1` in all 762 shipped objects, so the call no-ops. `IScript__SetTimer`
  (`0x005358e0`, zero direct `E8`, registry `"SetTimer"`) is the command
  that would schedule this message:
  `AddEvent_TimeFromNow(2002, this, delay)` via `0x0044b2d0` (`push 0x7d2`
  at `0x005358fd`). Zero compiled uses and zero loose-`.msl` `SetTimer(` /
  `timer()` / `event("timer")`. See
  [`CScriptObjectCode.cpp.md`](CScriptObjectCode.cpp.md) for the named
  `CEventFunction` occupancy (994 records, 0 listen-string `timer`).
- **arrived (id 1).** CLOSED as a fire site, empty as a shipped body.
  Only `E8` to `IScript__CreateThingRef` (`0x005335d0`) is `0x00538583`
  in the end-of-waypoint-chain arm of `UpdateWaypointFollowing` (next
  waypoint null and `[this+0x1c]==0`). It boxes `[this+0x24]` as a
  `CInt` (`vptr 0x005e4af8`) and `CallEvent(id=1, argc=1)`.
  `FollowWaypoint` (`0x00537d70`, native 0, `ret 0xc`) is the writer:
  `mov [esi+0x24],eax` at `0x00537dc7` after
  `args[1]->vtable[+0x30]()`. For `CInt` that slot is
  `SharedVFunc__ReturnField04_0052f540` (`mov eax,[ecx+4]; ret`).
  19 shipped `CALL` native-0 sites: the second PUSH is always type-1
  (`CInt`), value **0** in 13 and **1** in 6. The only other `+0x24`
  access in `0x00533000..0x00539000` is the read at `0x0053857d` that
  boxes arrived(). FollowWaypoint itself does not branch on the flag.
  Flag=1 objects: 600 `Ship`/`Slave`, 731/732 `messages`, 741/742
  `Marshall`. Loose `.msl` writes `1` at those same six sites and
  never names the argument. Authored name still open. All 762 13-slot
  IPs are `-1`; 0 listen-string `arrived`.
- Nested-listener registration / thing attach. CLOSED. `+0x74` is
  `mMissionScript`. `CComplexThing__SetScript` (`0x004f4230`) clones the
  named object, constructs this IScript (`0x005333b0`, only `E8`), stores
  it at `+0x74`, and `AddEvent_AtTime(INIT_SCRIPT=2001, thing, NEXT_FRAME)`.
  `HandleEvent` 2001 (only `E8` to `0x00533500`) runs `Init` then, unless
  `mThingType & 0x10` (`THING_TYPE_UNIT`), schedules `READY_SCRIPT=2003`.
  2003 is the only `E8` to `IScript__CallEventId6_OrReset`. Thing 2000
  is `SHUTDOWN` (`[IScript.vtable+8]` = `IScript__VFunc_2_00533810`,
  id 7). See [`CComplexThing.cpp.md`](CComplexThing.cpp.md). The IScript
  `HandleMessage` 2000/2001/2002 arms are a different receiver.
