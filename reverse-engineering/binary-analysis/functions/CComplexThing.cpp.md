# CComplexThing function map

Status: active static function map
Last updated: 2026-08-18 (slot 61 GoToPoint + CUnit +0x208 forward)
Source File: `C:\dev\ONSLAUGHT2\thing.cpp` (SEH `__FILE__` pointer
`0x006331c0` read out of `CComplexThing__SetScript`) | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — every byte below was re-read from the pristine specimen at
file offset VA − 0x400000 with `tools/disasm_va.py`; whole-image scans by
`tools/call_xref_scan.py`. Architecture from pinned GPL
`references/Onslaught/thing.cpp` / `thing.h` (lines cited). Function names are
the live Ghidra name table (db.18627 lineage); the byte contracts below are
independent of the names.

## Shape

`CComplexThing` is the 0x7c-byte thing that can carry a mission script. The
layout finding
[`cthing-ccomplexthing-layout-2026-08-13.md`](../cthing-ccomplexthing-layout-2026-08-13.md)
already owns the envelope: `+0x2c` `mFlags`, `+0x34` `mThingType`,
`+0x74` `mMissionScript`. Primary vtable `0x005df784` (COLOC `0x00616f00`):

| Slot | Offset | Address | Name |
| --- | --- | --- | --- |
| 0 | `+0` | `0x004f4300` | `CComplexThing__HandleEvent` |
| 1 | `+4` | `0x004f3ee0` | `CComplexThing__scalar_deleting_dtor` |
| 2 | `+8` | `0x004f41b0` | `CComplexThing__Shutdown` |
| 14 | `+0x38` | `0x004f43d0` | `CComplexThing__AddShutdownEvent` |
| 50 | `+0xc8` | `0x004f4430` | `CComplexThing__StartDieProcess` |
| 59 | `+0xEC` | `0x004f45a0` | `CComplexThing__FinishedPlayingCurrentAnimation` |
| 61 | `+0xf4` | `0x00401520` | `CComplexThing__NoOpFiveArgs_00401520` — empty `GoToPoint` |

`HandleEvent` is also stored in nine other `.rdata` vtables (subclass
overrides that still share slot 0). `Flush` delivers scheduled events
through slot 0 (`CScriptEventNB.cpp.md`).

These thing-event numbers are **not** the IScript `HandleMessage`
2000/2001/2002 arms. They are `EThingEvent` (`thing.h:33-39`):

| Value | Source name | Retail arm |
| --- | --- | --- |
| 2000 | `SHUTDOWN` | IScript `Shutdown` then `CComplexThing__Shutdown` |
| 2001 | `INIT_SCRIPT` | IScript `Init` + maybe schedule 2003 |
| 2002 | `START_DIE_PROCESS` | virtual `StartDieProcess` |
| 2003 | `READY_SCRIPT` | IScript `Ready` |

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004f4230` | `CComplexThing__SetScript` | `8b4e74 85c9 740e 8b01 6a01 ff5004 c7467400000000 8b442418 85c0 7479 803800 7474 50 b990508500 e84a690100 … 6a18 6a3c … e84c4e0500 … 57 56 8bc8 e803f10300 … 68d1070000 b9c82f6700 … 894674 c7442430000080bf e89170f5ff … c20400` | `ret 4`; arg = `char*` name. If `+0x74` is set, `vtable[+4](script, 1)` then null it. Empty/null name returns. Else `CWorld__CloneScriptObjectCodeByName` (`0x0050abc0`, `this=0x00855090`); on hit allocate 0x3c via `CDXMemoryManager__Alloc` (`__FILE__` `0x006331c0` = `thing.cpp`, line `0x299` = 665) and `IScript__Constructor` (`0x005333b0`, `ret 8`) with `(thing, clone)`. Store the IScript at `+0x74`. `CEventManager__AddEvent_AtTime` (`0x0044b370`) with event `0x7d1`, `to_call=this`, time slot `0xbf800000` (`NEXT_FRAME`). HIGH. Sole `E8` to the constructor and to the clone-by-name helper. Matches `thing.cpp:651-668`. |
| `0x004f4300` | `CComplexThing__HandleEvent` | `0fbf4f04 8bc1 2dd0070000 7477 48 743a 83e802 7424 81e9d0070000 …` | `ret 4`; `movsx` of `word [event+4]` then `sub 0x7d0`. Four arms below. HIGH. Matches `thing.cpp:674-706` (the 2002 arm is the inlined `CThing::HandleEvent` `START_DIE_PROCESS` case). |
| `0x004f43d0` | `CComplexThing__AddShutdownEvent` | `f6462c01 7521 8b4e74 85c9 741a e8faf30300 … 6a01 ff5004 c7467400000000 … 0c01 56 68d0070000 … c744241c000080bf e8446ff5ff c3` | Zero-arg `ret`. If `mFlags` bit0 (`TF_DECLARED_SHUTDOWN`) is clear and `+0x74` is set: `IScript__CallEventId3_OrReset` (died), virtual-delete the IScript, null `+0x74`. Then set bit0 and `AddEvent_AtTime(0x7d0, this, NEXT_FRAME, …)`. HIGH. Matches `thing.cpp:711-723` plus `CThing::AddShutdownEvent` (`thing.cpp:183-189`). |
| `0x004f4430` | `CComplexThing__StartDieProcess` | `668b462c a804 751e 0c04 6689462c 8b06 ff5038 8b4e74 85c9 7405 e80ef20300 b801000000 5e c3` | Zero-arg. If `mFlags` bit2 (`TF_DYING`) already set, return 0. Else set bit2, `call [vtable+0x38]` (`AddShutdownEvent`), then if `+0x74` still set `IScript__CallEventId5_OrReset` (started_dying), return 1. HIGH on the bytes. On this class `AddShutdownEvent` has already nulled `+0x74`, so the CallEventId5 is unreachable here (same order as `thing.cpp:728-737`). |
| `0x004f4480` | `CComplexThing__Hit` | `8b4974 85c9 7413 8b442404 f7403400000080 7406 50 e8f6f10300 c20800` | `ret 8`; args `(other, report)`. `report` is unused. If `+0x74` and `other+0x34 & 0x80000000` (source `IsA(THING_TYPE_COMPLEX_THING)`), `IScript__CreateThingRefWithSquad` (hit). HIGH. Matches `thing.cpp:748-755`. |
| `0x004f45a0` | `CComplexThing__FinishedPlayingCurrentAnimation` | `8b4974 85c9 7405 e894f20300 b801000000 c3` | Zero-arg; `ecx=[this+0x74]`; if set, `IScript__RestoreSavedStateAndGotoInstruction` (`0x00533840`); `mov eax,1; ret`. Slot 59 (`+0xEC`) of vtable `0x005df784` and 25 other `.rdata` copies (26 total). One direct `E8` at `0x004fdfdd` (`CUnit__HandleDeployAndFireAnimationCompletion`). HIGH. This is the `PlayAnimationWait` resume. |
| `0x00401520` | `CComplexThing__NoOpFiveArgs_00401520` | `c21400` | Slot 61 (`+0xf4`) of primary `0x005df784`. `ret 0x14` — five stack dwords unused. Source `CComplexThing::GoToPoint(FVector, BOOL)` is `{}` (`thing.h:293`). HIGH. `IScript__FollowWaypoint` / `FollowWaypointWait` both `call [thing.vtable+0xf4]` with waypoint `+0x1c` (4 floats) and override `0`. |
| `0x004fce00` | `CUnit__ForwardField208Slot10_004fce00` | `8b8908020000 56 85c9 742a 8b542418 8b742408 52 8b01 83ec10 … ff5010 5e c21400` | Slot 61 of `CUnit` `0x005df998`, `CRadar` `0x005dd788`, `CSubmarine` `0x005e1490` (COLOCs independently walked). If `[this+0x208]==0` return; else forward the 4-dword vector + BOOL to `[+0x208]->vtable[+0x10]`. HIGH on the forward. `+0x208` is the guide pointer unit inits store; that slot-4 body is open. |
| `0x005333b0` | `IScript__Constructor` | `c706d4925d00 8d4e28 e85b24fbff … c706084f5e00 894608 894e0c 897168 … 897e24 … c20800` | `ret 8`; args `(thing, eventObj)`. Installs `CMonitor` vptr `0x005d92d4` then IScript vptr `0x005e4f08`. `CSPtrSet__Init` at `+0x28`. `[this+8]=[this+0x10]=thing`; `[this+0xc]=eventObj`; `[eventObj+0x68]=this`. Zeroes `+0x14` / `+0x18` / `+0x1c` / `+0x24` / `+0x38`. HIGH. Only `E8` is `SetScript` `0x004f42a8`. |
| `0x0050abc0` | `CWorld__CloneScriptObjectCodeByName` | `8b8520010000 … ff5038 … 3a16 … 7443 8b4f04 e8e1e30200 c20400` / miss `6858… 68d2886300 e8f56af3ff 33c0 c20400` | `ret 4`; `this` = world `0x00855090`. Walks `[world+0x120]` comparing each object's `vtable[+0x38]` string to the arg. Hit: `CScriptObjectCode__Clone` (`0x00539040`) of `[node+4]`. Miss: `CConsole__Printf` `\"FATAL ERROR: Cant find script '%s'\"` (`0x0063d288`) and return 0. HIGH. Only `E8` is `SetScript`. |
| `0x00535c50` | `IScript__SetScript` | `8b442404 8bf1 8b08 8b11 ff5238 8b4e10 50 e8c9e5fbff c20c00` | `ret 0xc`. `args[0]->vtable[+0x38]()` (name string) then `CComplexThing__SetScript` on `[IScript+0x10]` (the thing). HIGH. Registry command; second static `E8` to `SetScript`. |

### `HandleEvent` arms (byte-exact)

`edi` = event, `esi` = this, `word [edi+4]` = event number.

**2000 `SHUTDOWN`** (`je 0x004f438c`): `cmp [0x008a9ac0], 3` /
`jg` skip (`EGameState > GAME_STATE_PLAYING`). Else if `+0x74`:
`call [IScript.vtable+8]` = `IScript__VFunc_2_00533810` (CallEvent id 7,
shutdown). Then re-fetch the event number and `call [this.vtable+8]` =
`CComplexThing__Shutdown`. The re-fetch is the compiler sharing the
`CThing::HandleEvent` tail (`thing.cpp:163-166` calls virtual `Shutdown`).

**2001 `INIT_SCRIPT`** (`je 0x004f4352`): if `+0x74`,
`IScript__CallEvent0AndRegisterNestedListeners` (`0x00533500`, only `E8` in
the image). Then `test byte [this+0x34], 0x10`: if set, return. Else
`AddEvent_AtTime(0x7d3, this, NEXT_FRAME, …)`. `+0x34` bit `0x10` is
`THING_TYPE_UNIT` (16); source is `if (!IsA(THING_TYPE_UNIT))` at
`thing.cpp:692-693`. Units do not get a 2003 from this arm.

**2002 `START_DIE_PROCESS`** (`0x004f4332`):
`call [this.vtable+0xc8]` = `CComplexThing__StartDieProcess` on this
vtable (slot 50). Source `CComplexThing::HandleEvent` has no 2002 case;
`CThing::HandleEvent` (`thing.cpp:169-172`) does. Retail inlines that
virtual call. No IScript wrapper here.

**2003 `READY_SCRIPT`** (`je 0x004f4341`): if `+0x74`,
`IScript__CallEventId6_OrReset` (`0x005335a0`, only `E8` in the image).

### `StartDieProcess` and started_dying

`CComplexThing__StartDieProcess` calls slot 14 (`AddShutdownEvent`)
**before** `CallEventId5`. `AddShutdownEvent` already fired died and
nulled `+0x74`, so the started_dying call on this class is unreachable.
The same order is in `thing.cpp:728-737`.

The other two `E8` sites fire while `+0x74` is still live. Independently
re-read 2026-08-18:

| Address | Name | Body | `+0x74` at CallEventId5 |
| --- | --- | --- | --- |
| `0x0044cd80` | `CFeature__VFunc_50_0044cd80` | If `TF_DYING` already set, return 0. Else set bit2, `CallEventId5` if `+0x74`, return 1. No `AddShutdownEvent`. Zero direct `E8` — slot 50 of the `CFeature` vtable at `0x005e45e0` (COLOC `0x006184c0`). | live |
| `0x004fd140` | `CUnit__MarkDestroyedAndCleanupLinks` | If `TF_DYING` already set, return 0. Unlink (`0x004e1130` on `0x00896988`), set bit2, optional `+0x164` count teardown, optional `+0x178` call `0x004443f0`, **then** `CallEventId5` if `+0x74`, then `+0x144` / `+0x18c` cleanup, return 1. Nine direct `E8`s. Slot 50 of three vtables (`0x005dd788` COLOC `0x00615728`, `0x005df998` COLOC `0x00617050`, `0x005e1490` COLOC `0x00617a30`). | live |

So shipped `started_dying` bodies (142 objects) are reachable from
feature/unit slot-50 overrides, not from `CComplexThing__StartDieProcess`.
Cheapest falsifier: a fourth `E8` to `0x00533660`, or a feature/unit
path that nulls `+0x74` before those two sites.

## Callers (direct `E8`)

| Target | Site | Owner |
| --- | --- | --- |
| `SetScript` | `0x004f3ff8` | `CComplexThing__Init` — pushes `[init+0xac]` (`mScript`) |
| `SetScript` | `0x00535c62` | `IScript__SetScript` |
| `HandleEvent` | five sites | subclass forwards (`0x004019ff`, `0x0043fcbd`, `0x0044c14d`, `0x004e37ad`, `0x004e65ed`). Scheduled 2001/2003/2000 arrive via slot 0, not these `E8`s |
| `AddShutdownEvent` | `0x0044cdc5`, `0x004894cc`, `0x004d7e79` | plus the virtual call from `StartDieProcess` |
| `StartDieProcess` | `JMP 0x004db13a` | plus HandleEvent 2002's `[vtable+0xc8]` |
| `FinishedPlayingCurrentAnimation` | `0x004fdfdd` | `CUnit__HandleDeployAndFireAnimationCompletion`; also slot 59 of 26 vtables |
| `Hit` | five sites | including `CSphereTrigger__Hit` `0x004e5728` |

## Open questions (cheapest falsifier first)

- Authored name of `FollowWaypoint` args[1] (the `CInt` 0/1 at
  `IScript+0x24`): still open. Sole retail reader is the arrived()
  box at `0x0053857d`. Six compiled `1`s: 600 Ship/Slave, 731/732
  messages, 741/742 Marshall. Loose `.msl` never names the argument.
- Who schedules thing-event 2002 besides `HandleEvent`'s own arm and
  `CThing::StartDieProcess` callers: CLOSED. Five `push 0x7d2` sites
  in the image, independently classified:
  - `IScript__Die` (`0x00535cd0`, native 13, 0 `E8`):
    `AddEvent_AtTime(0x7d2, [IScript+0x10], NEXT_FRAME)`. 48 compiled
    uses, all argc 0.
  - `IScript__SetTimer` (`0x005358fd`): `TimeFromNow(0x7d2, IScript,
    delay)` — IScript `HandleMessage` timer, not a thing fire.
  - `CGame__HandleEvent` (`0x0047000d`): `EGameEvent`
    `FINISHED_PANNING` (`game.h:35`).
  - `CTree__UpdateFallingTree` (`0x004f6f93`): `TimeFromNow(0x7d2,
    this, 5.0f)`. `ebp` is `this` (`mov ebp,ecx` at `0x004f6b9d`).
    Five seconds later `CTree__HandleEvent` (`0x004f7050`) does not
    handle 2002 (it only special-cases 3000/3001) and tails to
    `CThing__HandleEvent` (`0x004f3730`), which does
    `call [vtable+0xc8]` = `StartDieProcess`.
  - `0x00590a55`: not an event. `push "unrecognized shader version"`
    (`0x005ed330`) then `push 0x7d2` then jmp — a parser error path.
- `CFeature__VFunc_50_0044cd80` / `CUnit__MarkDestroyedAndCleanupLinks`
  as the reachable started_dying fires: CLOSED (section above).
- `IScript__VFunc_2_00533810` has zero direct `E8`; the 2000 arm's
  `[IScript.vtable+8]` is the static witness. A second virtual caller
  would be another slot-2 site.
- `CThing__HandleEvent` (`0x004f3730`) else-arm vs source
  `CMonitor::HandleEvent`: CLOSED as equivalent. Retail `sub 0x7d0;
  je Shutdown; sub 2; je StartDieProcess; ret 4`. Source
  `thing.cpp:174-177` default-calls `CMonitor::HandleEvent`. CMonitor
  vtable `0x005d92d4[+0]` is `0x004014c0` (`ret 4`). No behavioral
  divergence.
