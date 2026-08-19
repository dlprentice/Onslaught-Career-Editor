# IScript function map

Status: active static function map
Last updated: 2026-08-18 (0x0050a0e0 first gates)
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
| `0x00537e40` | `IScript__FollowWaypointWait` | `538bd9 55bd01000000 8b4318 56 3bc5 57 0f8464010000 … 68d0070000 … c20c00` | `ret 0xc`. Early-out if `[this+0x18]==1`. Same `0x00505c30(name, thing+0x1c)` lookup; miss prints `FATAL ERROR: Cant find waypoint path '%s'` (`0x0064fe00`). If `[this+0x10] != [this+8]` prints `FATAL ERROR:  Cant Follow waypoint way for other object` (`0x0064fdc8`) and returns. Else copies waypoint `+0x1c` and calls thing `vtable[+0xf4]`; snapshot; `[this+0x1c]=1`, `[this+0x20]=CVM`, `[this+0x18]=1`; `AddEvent_AtTime(2000, this, NEXT_FRAME)`. HIGH. |
| `0x00537d70` | `IScript__FollowWaypoint` | `53 55 8b6c240c 56 8bf1 57 8b4d00 8b01 ff5038 8b4e10 8bd8 83c11c 51 53 e89fdefcff 8bf8 83c408 85ff 751a 53 68a8fd6400 … 8b4d04 8b11 ff5230 6a00 8d571c 83ec10 8b4e10 894624 … ff90f4000000 8b4610 8b4e08 3bc1 753c 8b4e18 … c7461c00000000 … 68d0070000 … c20c00` | `ret 0xc`; zero direct `E8` (native 0). `args[0]->vtable[+0x38]()` is the path name; `0x00505c30(name, thing+0x1c)` looks up the waypoint; miss prints `Cant find waypoint path '%s'` (`0x0064fda8`) and returns. `args[1]->vtable[+0x30]()` is stored at `[this+0x24]` with **no** later branch. Copies waypoint `+0x1c` (4 floats) onto the stack and calls thing `vtable[+0xf4]`. `[this+0x14]=waypoint`, `[this+0x1c]=0`. If `[this+0x18]!=1`, sets it and `AddEvent_AtTime(2000, this, NEXT_FRAME)`. HIGH. Descriptor `0x0064ce20+0x04=2` (arity); no arg-name strings. |
| `0x00505c30` | `NamedEntryList_T3_00505c30` | `a1c04f8500 56 85c0 57 a3c84f8500 7404 8b30 … e838270600 83c408 85c0 7422 … c744240c7f96184b 894610 … d9411c d822 d94120 d86204 d94124 d86208 … c3` | cdecl `(char* name, float* pos)`. Bare `ret`. Walks the `CSPtrSet` at `0x00854fc0` (cursor `0x00854fc8`) whose payloads are `CWaypointPath` (vptr store `0x005dfc8c`, COLOC `0x006172d0` → TypeDescriptor `0x0063d220` = `.?AVCWaypointPath@@`). Name test is CRT `stricmp` (`0x00568390`) of `[path+4]` vs `name`. Hit: walk the embedded `CSPtrSet` at `path+8` (cursor `path+0x10`) and keep the child with the smallest `(Δx²+Δy²+Δz²)` of `[child+0x1c]` vs `pos`; seed `9999999.0f` (`0x4b18967f`). Empty/miss returns 0. Two `E8`: `0x00537d8c`, `0x00537e6b`. HIGH. Table name stays the demoted placeholder — class `NamedEntryList` is absent. |
| `0x0047e2d0` | `CGuide__VFunc04_SetVectorMode1_0047e2d0` | `8b442414 85c0 750f 8b4118 8b903c010000 837a2002 7425 8b442404 … c7411c01000000 83c108 … c21400` | Slot 4 (`+0x10`) of `CGuide` `0x005dbdc4` (COLOC `0x006141a8` → `.?AVCGuide@@`). `ret 0x14`. If the BOOL is 0 and `[[owner+0x13c]+0x20]==2`, return without store. Else `[this+0x1c]=1` and copy the 4-dword vector to `[this+8]`. Zero direct `E8`. Same slot-4 dword on `CAirGuide` `0x005d8594`, `CMechGuide` `0x005dc4f4`, `CThunderheadGuide` `0x005df8d4`. HIGH. |
| `0x0047d750` | `CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750` | `81eca4000000 53 55 56 8bf1 57 8b4e18 f6412c04 7413 … e81ae90300 bd02000000 8b462c 85c0 0f840a050000 … 8a5c0aff 8d541b01 … d9f3` | Slot 3 of `CGroundVehicleGuide` `0x005dbd90` (COLOC `0x00614170` → `.?AVCGroundVehicleGuide@@`); slot 4 is still `0x0047e2d0`. Zero `E8`. Early-out if owner `mFlags` bit2 (`TF_DYING`). Dest `guide+8` minus `owner+0x1c` via `0x00401ec0`; zero `owner+0x14c`; 2D `d² < 0.5f` (`0x005d85ec`) or mode `0` or `0x004fde10(owner)` (`[unit+0x244]∈{3,4,5}`) → near exit `0x0047e183`. Mode-1 arm (`cmp [+0x1c],1`): skip if `[owner+0x13c]+0x20==2`; if `d² > 1.0f` (`0x005d8568`) and `[guide+0x20]` live, rebuild unless dest ints still match `guide+0x24/+0x28` within 1. Rebuild is `0x004bc2e0(grid=[+0x20], dest, owner-pos, 1, out=&guide+0x24)`. After the call: if `[guide+0x2c]==0` join `0x0047dee0`; else walk the path **from the end** — world `(2·byte+1, 2·byte+1)` from `[guide+0x34][n-1]` / `[guide+0x3c][n-1]` (`n=[guide+0x30]`); while 2D `d² < 0.5f` decrement `n` and pop; empty → head at dest `guide+8`; then `fpatan`. HIGH on the walk. After `fpatan` (and on the no-path join `0x0047dee0`): `[owner+0x120]=desired` from `[esp+0x18]`; current yaw is `[owner+0x114]` saved at `[esp+0x50]` in the prologue (`fpatan` of dest−owner, `fchs`). Unwrap via `2π` (`0x005d85e0`) / `±π/2`; `|Δ|≤0.6` (`0x005dbdb8` qword) near-exits `0x0047e183`. `|Δ|>0.6` at `0x0047df6a`: `ebp` is 2 (`mov ebp,2` restored `0x0047dedb`); skip occupancy if `[owner+0x13c]+0x20==2`. Else bit-test owner cell on `[guide+0x20]`; if occupied, probe one unit along `fchs`/`fsin`/`fcos` of current yaw and near-exit if the probe cell is clear. `mode==3` near-exits. Else `call [owner.vtable+0x1bc]` (`CUnit` slot 111 `0x004fe5c0`, zero `E8`) then `fmul 0.05f` (`0x005d8584`) then `fmul 4.0` (`0x005d85bc`) if mode 1 else `fmul -4.0` (`0x005d9290`). Local vector is `(0, scaled, 0)`; left-multiply `mOrientation` (`owner+0x3c`) into `owner+0x14c`. Authored `+0x114`/`+0x120`/`+0x14c` names open. |
| `0x004fdc90` | `CUnit__IsField13cNotMode2_004fdc90` | `8b813c010000 85c0 7409 83782002 7503 33c0 c3 b801000000 c3` | Slot 46 (`+0xb8`) of `CUnit` `0x005df998`. Zero-arg; bare `ret`; zero `E8`. 33 `.rdata` copies (CRadar `0x005dd840`, CSubmarine `0x005e1548`, …). EAX=0 iff `[this+0x13c]` live and `[[this+0x13c]+0x20]==2`; else EAX=1. Same compare is inlined in `CGuide` slots 4/7 — FollowWaypoint does not `E8` this body. Sibling slot 54 `0x004fdcb0` (`CUnit__SetEngagementModeAndMaybeClearTargetReader`, `ret 4`, one `E8` `0x0047a9ca`) writes `[this+0x210]=arg` and if arg==1 `SetReader([13c+0xc],0)` + zero `[13c+0x10]`. Sibling slot 81 `0x004175e0` returns `[13c+0xc]` or 0. `+0x13c` is the `CWarspite__Init` object on `CGroundVehicle` (`0x0047d1a5`). HIGH on ABI, slot, polarity, siblings. |
| `0x004fe710` | `CWarspite__Init` | `6aff 6819565d00 64a1 … c7061c8d5d00 … c74620ffffffff … c7462002000000` | `ret 8` (owner, init). vptr `0x005d8d1c`. Defaults `[+0x20]=-1`; writes **2** at `0x004fe7cb` only when `[this+0x28]` and `[init+0x3b8]` are live. 26 `E8` including `CGroundVehicle__Init` `0x0047d198` (store at owner `+0x13c`) and `CMechAI__ctor` `0x004a0309` (then vptr `0x005dc4c0`). Second image writer of `+0x20=2` on this layout is `CUnitAI__TryStartField28TimedEvent` `0x004ffb60` (virtual; needs `+0x28` and `+0x2c`). Unrelated `0x00545124` not claimed. Authored name of `2` open. HIGH. |
| `0x004fea30` | `CUnitAI__TryStartFollowWaypoint_004fea30` | `8b4124 83ec64 85c0 7446 8b4120 85c0 7545 … c7412000000000 51 68b90b0000 … c3` | Zero-arg; bare `ret`; zero `E8`; 21 `.rdata` copies (CWarspite vptr `0x005d8d1c` slot 5 at `+0x14`). If `[this+0x24]==0` return 0. If `[this+0x20]!=0`: store `0`, `AddEvent_AtTime(0xbb9, this, …)` `0x0044b370`, return 1. If `[this+0x20]==0`: print `\"%s CANT start following waypoints cos it already was !!!\"` (`0x00633cb0`) via `CConsole__Printf` `0x00441740` and return 0. So `+0x20==0` is already-following. Distinct from IScript `+0x24`. `0xbb9` is JT[1] of `0x004ff330`. HIGH. |
| `0x004ff330` | `CUnitAI__DispatchTimedAIEvent_004ff330` | `83ec08 53 56 8bf1 bb01000000 57 8b4e08 8b8144020000 … 0fbf4704 0548f4ffff 83f803 7794 ff2485d8f44f00 … c20400` | Slot 0 of CWarspite `0x005d8d1c`. `ret 4`; one arg = event. Zero inbound `E8` (virtual-only). 20 `.rdata` copies. Five `E8`: `Random__NextLCGAbs` `0x004de8d0` once and `AddEvent_AtTime` `0x0044b370` four times. `ebx=1`; if `[owner+0x244]∈{1,2}` `ebx=0`. `call [owner.vtable+0xd4]` is `CUnit__ReturnField210_00405e50` (`[owner+0x210]`). If EAX==4 or `ebx==0`, skip the switch and reschedule `0xbbb` at `mTime+2.0f+rand16*(2/65536)` (`fmul 0x005d8de4`, `fadd 0x005d8ba0`, `fadd [0x00672fd0]`). Else `movsx eax, word [event+4]; add eax,0xfffff448` (`−0xbb8`); `cmp eax,3; ja` same reschedule. JT `0x004ff4d8`: `[0]=0x004ff3fc` 3000, `[1]=0x004ff3de` 3001, `[2]=0x004ff431` 3002, `[3]=0x004ff442` 3003. **3001** (`0xbb9`): `[owner+0x214]==0` falls to that reschedule; else `call [this.vtable+0x20]` slot 8 `0x004feac0` and return. Does not itself write `this+0x20`/`+0x24`. **3003**: `[this+0x20]==1` schedules `0xbb8` NEXT_FRAME, `==0` schedules `0xbb9`, `==2` schedules `0xbba`, else return. HIGH on ABI, JT, 3001 arm, 3003 pick. Authored event names open. |
| `0x004feac0` | `CUnitAI__CheckField24RangeAgainstCandidate_004feac0` | `51 53 56 8bf1 57 8b4e24 8d7e24 85c9 747d … 68b90b0000 … c20400` | Slot 8 (`+0x20`) of CWarspite `0x005d8d1c`. `ret 4`; one unused event arg. Zero inbound `E8` (virtual-only). 13 `.rdata` copies. Three `E8`: `SetReader` `0x00401000`, `Random__NextLCGAbs` `0x004de8d0`, `AddEvent_AtTime` `0x0044b370`. `[this+0x24]` is the current waypoint (same `+0x1c` pos / `+0x3c` next layout as IScript). Null at entry → slot 6 `0x004febe0` and return. Else 2D `fsqrt` of waypoint−owner; if `< 4.0f` (`0x005d85bc`) and `[wp+0x3c] != wp`, `SetReader(+0x24, next)`. Then if `+0x24` live: thing `vtable[+0xf4]` `GoToPoint(wp+0x1c, 0)` and this slot 4 `0x004ff4f0`. If `+0x0c` live after that, slot 6 and return; if `+0x0c` null, reschedule `0xbb9` at `mTime+1.0f+rand16/65536` (`fmul 0x005d8d54`, `fadd 0x005d8568`). If `+0x24` became null: owner `vtable[+0x100]` `0x004fcf00`, owner `vtable[+0x148]` `0x00405e10` (`[+0x1f0]=1`), then slot 6. HIGH on ABI, 2D 4.0 advance, GoToPoint, 3001 reschedule. Slot 6 body closed below. Slot 4 body closed below. `+0x0c` is a SetReader thing slot (TF_DYING clears it). |
| `0x004febe0` | `CUnitAI__TryStartFightingMode1_004febe0` | `8b4120 83ec64 83f801 7545 8b4908 8b01 ff501c … c7412001000000 51 68b80b0000 … c3` | Slot 6 (`+0x18`) of CWarspite `0x005d8d1c`. Zero-arg; bare `ret`; zero inbound `E8` (virtual-only). 21 `.rdata` copies. Four `E8`: `sprintf` `0x0055de9b`, `CConsole__AppendToStatusBufferV` `0x00472240`, `CConsole__Printf` `0x00441740`, `CEventManager__AddEvent_AtTime` `0x0044b370`. If `[this+0x20]==1`: `[this+8]->vtable[+0x1c]()` (CUnit slot 7 `CUnit__VFunc_7_004f84a0` is `mov eax,0x00633ae0; ret` = `"CUnit"`), `sprintf` of `"%s CANT start fighting cos it already was !!!"` (`0x00633c80`), then Append+Printf, return 0. Else `[this+0x20]=1`, `AddEvent_AtTime(0xbb8, this, &mTime 0x00672fd0, 0, 0, 0)`, return 1. Does not read or write `+0x24`/`+0x0c`. Dual of slot 5 (already-0 / store-0 / `0xbb9`). Slot 8 calls this via `[vtable+0x18]` with no extra arg. HIGH. Authored name of `1` open. |
| `0x004ff4f0` | `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0` | `83ec28 55 56 8bf1 8b460c 8d6e0c 85c0 740f f6402c04 … ff522c … c3` | Slot 4 (`+0x10`) of CWarspite `0x005d8d1c`. Zero-arg; bare `ret` (four exits). Zero inbound `E8`. 18 `.rdata` copies. Eleven `E8`: `SetReader` `0x00401000` x2, `0x004fd5b0`, `0x004fb840` x2, `0x004fb5a0` x2, `0x004fd3d0`, `0x004fb3d0`, `0x004fdad0`, `0x004fb500`. `[this+0xc]` is a `SetReader` thing slot: live and `[obj+0x2c]&4` (`TF_DYING`) → `SetReader(+0xc, 0)`. Writes `[this+0x18]` / `[this+0x1c]`. If `[owner+0x148]` live and `[that]->vtable[+0x14c]()==0`: zero `+0x18/+0x1c`; null `+0xc` returns; `0x004fd5b0(owner,+0xc)` then `0x004fb840` + `+0x1c=0x004fb5a0` and join `0x004fb500`; else `SetReader(+0xc,0)` return. Else walk list `0x008550a0` (`[node+4]`); skip `edi==[owner+0x148]`; 3D `d²` vs `(1.0f − vfunc[+0x150]()*0.01f)*[[owner+0x164]+0x158]` (`0x005d8568` / `0x005d85fc`); one polarity calls `0x004fdad0`. After walk, if `+0xc` and `[this+0x10]` live: same `0x004fb840`/`0x004fb5a0` then `+0x18=0x004fb500(owner,+0xc,0)`. Else this slot 11 `0x004ff710`. Callee bodies not re-derived. HIGH on ABI, `+0xc` dying-clear, writes, two-arm shape. |
| `0x004fb500` | `CUnit__CanFireAtTarget_BallisticArcA` | `56 57 8b7c240c 8bf1 57 e862010000 85c0 7407 … 0f95c0 c20800` | `thiscall` `ret 8`; args `(target*, flag)`. Zero `.rdata` copies. Nine inbound `E8` including slot 4 `0x004ff6e3` and slot 11 `0x004ffb2c`. Three `E8`: `0x004fb670`, `0x0047eb80`, `0x00507ab0`. `0x004fb670(this,target)` nonzero → EAX=0. If `[this+0x140]==0` or the height gate fails: EAX = `[this+0x144]!=0`. Else `0x0047eb80(this=0x006fadc8, target+0x1c)`, cap vs BSS `0x006fbdfc` (not in the image), `fsub [target+0x24]`, compare to `[[this+0x140]+0xa0]+0x6c` / `+0x70`; pass returns `0x00507ab0(this, target, flag)`. First gates of that callee closed below. HIGH on ABI, reject, height gate, fallback. |
| `0x004fb5a0` | `CUnit__CanFireAtTarget_BallisticArcB` | `56 57 8b7c240c 8bf1 57 e8c2000000 … 0f95c0 c20400` | `thiscall` `ret 4`; one arg `(target*)`. Zero `.rdata`. Eleven inbound `E8` including slot 4 `0x004ff55a`/`0x004ff6ce` and slot 11 `0x004ff762`/`0x004ffb18`. Three `E8`: `0x004fb670`, `0x0047eb80`, `0x005088b0`. `0x004fb670(this,target)` nonzero → EAX=0. If `[this+0x140]==0`: EAX=`[+0x144]!=0`. Else `target->vtable[+0x10c]()` nonzero uses height `0.0f`; else `0x0047eb80(0x006fadc8, target+0x1c)` cap vs BSS `0x006fbdfc`, `fsub [target+0x24]`. Window vs `[[+0x140]+0xa0]+0x6c` / `+0x70`; pass `0x005088b0(this=[+0x140], target)`. HIGH on ABI, reject, height, inbound. |
| `0x00507ab0` | `OID__CanFireAtTarget_BallisticArcA` | `6aff 6859595d00 64a1 … c20800` | `thiscall` `ret 8`; SEH; args `(target*, flag)`. Zero `.rdata` copies. One inbound `E8` (`0x004fb578`). Body `0x00507ab0`–`0x005088ad`. Success `EAX=1` at `0x00508888`; reject `EAX=0` at `0x00508891`. First reject: `0x0044a850(this)` then `[eax+8] > BSS 0x006fbdfc`. Second: if `[this+0xa0]→+0x18→+0x58` live and `[owner+0x138]∈{0,1}`, `0x0044c780` on `target+0x1c` returning 0 (clearance dword 0). After those: `0x0044a930` (thiscall `ret 4` at `0x0044a9a2`; other arm not walked) then `0x00401ec0` (`ret 0xc`, three floats → `this+0/+4/+8`). If `[this+0x94]` live, remap via `[owner+0x3c]` / `[owner+0xe0]` through `0x0040d1f0` / `0x0040d320` and another `0x00401ec0`. `fpatan`/`fchs` parks facing at `[esp+0x2c]`. Pitch `[esp+0x20]`: `[owner+0xe8]` if `[this+0x98]` else `acos(z/\|v\|)` via `0x004026b0` / `0x0055dcb0` (0 if `\|v\|==0` vs `0x005d856c`). `0x0050a0e0(this, &out, target)` `ret 8` at `0x0050a283` then another `0x0044a850`; second `fpatan`/`fchs` at `[esp+0x18]`, second elevation at `[esp+0x1c]`. Wrap facing vs target across `±π` using `-π/2` / `π/2` / `2π` / `-π` / `π` (`0x005d85c8` / `e4` / `e0` / `dc` / `e8`). `|delta|` `fcomp [mode+0x84]`; `test ah,1` / `je 0x00508891` — need strictly `|yaw| < [mode+0x84]`. Then `0x0040d0f0([mode+0x18])`: EAX=0 → `0x00508627`; nonzero → `0x00507de1`. Zero arm: `[stmt+0x6c]!=0` samples owner XY via `0x0047eb80(0x006fadc8)` and returns 1 iff BSS `0x006fbdfc` `<` sample (`test ah,1` / `je 0x00508891`). `[stmt+0x6c]==0` and `[this+0x98]`: wrap parked pitch vs elevation with the same `±π` constants; need `|delta| ≤ [mode+0x84]` (inclusive, `test ah,0x41`; not the earlier yaw test). `[this+0x98]==0`: need `[mode+0x80] < (elev−pitch) < [mode+0x7c]` (`0x00508724` / `0x00508732`; fail pops ST0 at `0x0050888f`). Then `cmp [esp+0x1d8], ebx` (`ebx` still 0 from `0x00507b05`; this arm does not write it): flag 0 → EAX=1 and skip `0x00508756`. Flag≠0 tail: `0x0044a850` + `0x004098e0` + `0x0050b030(this=0x00855090)`; EAX=1 only if class 3, live hit, `[hit+0x34]&0x10`, and `[hit+0x138]==[target+0x138]`. Fire-join stores already pinned as flag 0, so they take the short-circuit. Nonzero arm `0x00507de1`: `cmp [this+0x98], ebx` / `je 0x00508016`. `[+0x98]!=0`: horiz `fsqrt` of the parked XY pair at `[esp+0x64]`/`[esp+0x68]`; a pitch/speed expression from parked pitch `[esp+0x20]`, `[stmt+0x2c]*0.05f` (`0x005d8584`), `[stmt+0x3c]*0.025f`, and Z delta; clamp if `< 0`; `|horiz − that|` must be strictly `< 12.0f` (`0x005db4e8`, `test ah,1` / `je 0x00508891`). Then `0x004062d0` (`ret 0xc` at `0x0040638e`) + two `0x0044a850` + `0x00401ec0` + `0x004098e0` + `0x0050b030(this=0x00855090)`; `EAX==0` or `EAX==3` → 1, else 0. `[+0x98]==0` at `0x00508016`: `ecx` is still owner (`[esi+8]` from `0x00507de1`). Remap `[owner+0x3c]` / `[owner+0xe0]` through `0x0040d1f0` (`ret 0xc`) / `0x0040d320` (`ret 8`) then `0x00401ec0` / `0x004026b0`; `|v|>0` (`fcom 0.0f` `0x005d856c`, `test ah,0x41`) → `acos` `0x0055dcb0` else 0. Park `acos+[mode+0x7c]` at `[esp+0x2c]` and `acos+[mode+0x80]` at `[esp+0x20]`. Split on `−π/4` (`f32 0x005d8dec` / `f64 0x005dfca8`). Two `fcomp` of the shared horiz `[esp+0x10]` at `0x005082dd` / `0x005082f0` fail to EAX=0. Then two `0x004062d0` (`[owner+0x114]` plus `[esp+0x30]`, then `[owner+0x114]` plus `[esp+0x20]`) + two line records (vptr `0x005d892c` then `0x005d8bfc`; scale `3.0f` `0x005d8cc0`) + two `0x0050b030(this=0x00855090)` (`ret 0x54` at `0x0050b504`). `edi=1`; class 1 or 2 on either call clears `edi`; class 3 + live hit + `[hit+0x34]&0x10` + `[hit+0x138]!=[target+0x138]`: first call clears `edi`, second rejects at `0x0050860f`. `edi==0` → 0 else 1. Sin/cos solve algebra not claimed. HIGH on ABI, exits, first two rejects, aim/`fpatan`, yaw slack, split, zero arm, both `[+0x98]` flavours. |
| `0x005088b0` | `OID__CanFireAtTarget_BallisticArcB` | `6aff 687b595d00 64a1 … c20400` | `thiscall` `ret 4` at `0x00509132`; SEH; one arg `(target*)`. Zero `.rdata` copies. One inbound `E8` (`0x004fb629`). Body `0x005088b0`–`0x00509134`. EAX ∈ {0,1}: fail `xor eax,eax` at `0x00509119`, success `mov eax,1` at `0x00509112`. First reject: `0x0044a850(this)` then `[eax+8] > BSS 0x006fbdfc` (`test ah,0x41` / `je 0x00509119`). Second: if `[this+0xa0]→+0x18→+0x58` live, grid is `[0x008a9d7c]` unless `[owner+0x138]` **any nonzero** then `[0x008a9d80]` (no `∈{0,1}` test); `0x0044c780` on a 16-byte copy of `target+0x1c`; EAX=0 → 0. Does not `E8` `0x0040d0f0` (20 body `E8`; one `0x0050b030` at `0x005090ea`). After the two rejects: park `[stmt+0x2c]`, `0x0044a930` (`ret 4`), scale that vector by the parked dword, `0x0050a0e0(this, &out, target)`, then `0x0044a850` and `acos` of the delta (`0x004026b0` / `0x0055dcb0`, 0 if `|v|==0`). `[this+0x98]` overwrites that with `[owner+0xe8]`. Inlined `0x0040d0f0` at `0x00508aac`: `[stmt+0x3c]*0.025f==0` (`0x005d8c6c`/`0x005d856c` C3) or `[stmt+0x50]` or `[stmt+0x6c]` → `0x00508e36`. That arm: `[stmt+0x6c]` → `0x0047eb80` at owner XY, EAX=1 iff BSS `<` sample. `[stmt+0x6c]==0` at `0x00508e71`: `[this+0x98]` live remaps `owner+0xe0/+0x3c` via `0x004011b0` / `0x004062d0` / `0x0040d320`, `fpatan`/`fchs`, `0x00401ec0`, then `0x0047ec60` (`CMonitor__SampleHeightfieldNormalAtXY`, `this=0x006fadc8`, out=`[esp+0x2c]`, pos=`owner+0x1c`; 21 inbound `E8`, this site `0x00508f6a`) and adds that mix into `[esp+0x14]` (entered as `[owner+0xe8]`). `[this+0x98]==0` keeps the earlier `[esp+0x14]` elev-minus-acos. Join `0x00508fab`: need `[this+0xa0]+0x80 <= [esp+0x14] <= [this+0xa0]+0x7c` (inclusive; `test ah,1` / `jne` is upper C0; `test ah,0x41` / `je` is lower not-≤). Then `[stmt+0x48]` live → `EAX=1` at `0x00508fe2`. Else one line record (vptr `0x005d892c` then `0x005d8bfc`) + `0x004098e0` + `0x0050b030(this=0x00855090)`; push flag is 0 iff `[target+0x34]&0x100`; `EAX==3` + live hit + `[hit+0x34]&0x10` + same `+0x138` else 0. Fall-through `0x00508adc` (zero `E8` through `0x00508e31`): horiz = hypot of parked `0x0044a850` ΔX/ΔY (`[esp+0x3c/+0x40]`); `[esp+0x18]=[stmt+0x2c]*0.05f` (`0x005d8584`); `[esp+0x24]=[stmt+0x3c]*0.025f`; `[esp+0x28]=[owner+0x24]−[target+0x24]`. Park `[esp+0x20]=ST0+[this+0xa0]+0x7c` and `[esp+0x14]=ST0+[this+0xa0]+0x80` (ST0 is `0` if `[this+0x98]` else the leftover third `acos`). Same −π/4 split constants as `0x00507ab0` (`0x005d8dec` / qword `0x005dfca8`): both strictly `>` or both strictly `<` → `0x00508b7f`; mixed or `==` → `0x00508c5b`. Each θ: `vsin=sin(θ)*[esp+0x18]`; `disc=vsin²+2*[esp+0x24]*[esp+0x28]`; disc `==0` (same-side C3) or `<=0` (mixed `test ah,0x41`) or result `<0` stores `0`; else `(([√disc]−vsin)/[esp+0x24])*cos(θ)*[esp+0x18]`. Same-side keeps two ranges; join `0x00508e06` succeeds iff `min <= horiz <= max` (`test ah,0x41` / `je 0x00509119` is `horiz > max`; `test ah,1` / `jne` is `horiz < min`); `EAX=1` at `0x00508e2c`. Mixed adds −π/4 as a third range; `[esp+0xc]` = **min** of the nonzero ones (`test ah,1` strictly `<`; else leftover `sin(−π/4)*[esp+0x18]` if `r(hi)==0`); ST0 = max of all three (zeros included); same window. Independently re-read after t_f63b7ac5 (the first pin had this min/max flipped). Physics identity not claimed. HIGH also on split, window, zero `E8`. |
| `0x0050b030` | `CWorld__FindFirstThingToHitLine` | `6aff 68b85b5d00 … c25400` | `thiscall`; **ECX unread**; `ret 0x54` at `0x0050b504`. Body `0x0050b030`–`0x0050b517`. Twelve inbound `E8` (0 `E9`), each preceded by `mov ecx, 0x00855090`. EAX = `[out+8]`. Stores of that dword: `0` at `0x0050b070` (`mov [edi+8], ebp` after `xor ebp,ebp`); `1` at `0x0050b102`; `3` at `0x0050b4df` and stop-early `0x0050b50e` (`mov eax,3; mov [ecx+8], eax`). **2 is never stored** (no `c7 … 08 02`). Table name is a label. Independently re-read after t_2b2fd826. HIGH on ABI, inbound, `{0,1,3}`, unread ECX. |
| `0x0050a0e0` | `OID__ComputeForwardProjectedPointTowardTarget` | `81ec88000000 56 8bf1 8b86a0000000 … c20800` | `thiscall` `ret 8` at `0x0050a241` and `0x0050a283`. Args `(out*, target*)`. Two inbound `E8`: `0x00507c9d` / `0x005089a8` (the two fire twins). Early-out if `[this+0xa0]==0` or `[[this+0xa0]+0xb0]==0`: `target->vtable[+0x168](&local)` then copy 4 dwords to `out`. Live: `0x0044a850(this)`; `target->vtable[+0x168]`; scale = `1000.0f` (`0x447a0000`) if `[stmt+0x50]` else `[stmt+0x2c]` else `0`; `0x0044a930`; `target->vtable[+0x6c]`; write 3 floats to `out+0/+4/+8` after a hypot ratio `* 20.0f` (`0x005d857c`). Projection algebra not claimed. Table name is a label. HIGH on ABI, inbound, early-out, scale pick. |
| `0x0044c780` | `CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta` | `83ec08 8d54240c 56 8bf1 b9c8ad6f00 … c21000` | `thiscall` `ret 0x10`; four stack floats (world pos). Zero `.rdata`. Two inbound `E8` (`0x00507b5b`, `0x00508953`). One `E8` `0x0047eb80(0x006fadc8, pos)`. `pos.z − height` `fcomp −5.0f` (`0x005db2b0`): C0\|C3 or OOB `[0,0x40)²` of `floor((x,y)+adjust)/8` → EAX=1. Else EAX = `[this + 0x4008 + (y*64+x)*4]`. Fire join treats EAX=0 as reject. HIGH. |
| `0x0040d0f0` | `CWeaponStatement__UsesBallisticArcNoLocks` | `d9413c d80d6c8c5d00 d81d6c855d00 … b801000000 c3 33c0 c3` | Zero-arg thiscall; two bare `ret` (`0x0040d119` / `0x0040d11c`). Zero `.rdata`. Five inbound `E8` (`0x0040caca`, `0x00507dd4`, `0x0050919a`, `0x005096c1`, `0x005099c1`). EAX=1 iff `[this+0x3c]*0.025f` (`0x005d8c6c`) is not 0.0 (`0x005d856c` C3) and `[this+0x50]==0` and `[this+0x6c]==0`; else EAX=0. Table name is a label. HIGH. |
| `0x004ff710` | `CUnitAI__SelectOrRefreshCloseTarget_004ff710` | `83ec20 53 55 56 8bf1 8b4e0c 57 8d6e0c 33ff 3bcf 7472 … c7442410f02374c9 … e81b15f0ff … 83c420 c3` | Slot 11 (`+0x2c`) of CWarspite `0x005d8d1c`. Zero-arg; bare `ret` (five exits). Zero inbound `E8` (virtual-only). 15 `.rdata` copies. 18 `E8`. Fast path: if `+0xc` live and `[target]->vtable[+0x16c]()` equals `0.0f` (`0x005d856c`, C3) and `[this+0x14]!=0` and `0x004fd5b0(owner,+0xc)`: same fire join as slot 4 (`0x004fb840` / `+0x1c=0x004fb5a0` / `+0x18=0x004fb500(owner,+0xc,0)` or 0) and return. Else zero `+0x18/+0x1c` and pick a list from `[owner+0x138]`: `1` → `0x008550b0`, `0` → `0x008550c0`, else `0x00855090`. Walk: `[node]` payload / `[node+4]` next; seed `-999999.0f` (`0xc97423f0`); best starts 0. `[ebx+0x34]` bit `0x20000000` → `edi=ebx->vtable[+0x128]()`; else bit `0x10` → `edi=ebx`; else next. Gates (all `ret 4`): `0x004fd5b0(owner,edi)` (EAX=0 if null / `TF_DYING` / `[+0x244]∈{1,2}`), `0x004fd3d0(owner,[edi+0x138])`, `0x004fb3d0(owner,edi)`. Range: 3D `d²` of `[ebx+0x1c]` vs `owner+0x1c` against `((1.0f − edi.vfunc[+0x16c]()*0.01f)*[[owner+0x164]+0x158])²` (`0x005d8568` / `0x005d85fc`); C0 skips. Score: `[[owner+0x164]+0x128]` live → `Random__NextLCGAbs` signed-16 `* 1/8192` (`0x005d96e4`); else first hit of `[edi+0x34]` bits `0x20000/+0x168`, `0x4000/+0x174`, `0x400/+0x178`, `0x40000/+0x164`, `0x100/+0x16c`, `0x8000/+0x170` (else 0), floor `+0x17c` if bit `0x80000`. Strictly greater score replaces best; equal goes secondary. Secondary: `d=fsqrt(d²)`; tmp=`1000.0f−d` (`0x005d8c54`); `0x004fb840`; `0x004fb780(owner, edi+0x1c)` `ret 0x10`; if that ST0 `≤ [esp+0x14]` (random-arm leftover) also `0x004fb7e0` and `d+=10000.0f` (`0x005db3b4`) or `1000000.0f` (`0x005db290`); record `edi` when adjusted `d > tmp`. Winner: `SetReader(+0xc,edi)`, `0x004fb840` twice, zero `+0x10`, then the same fire join (or zero `+0x10` and return). Empty / no winner: `SetReader(+0xc,0)` and zero `+0x10`. `0x004fb780`/`0x004fb7e0`/`0x004fb840`/`0x004fb3d0` bodies not re-derived. HIGH on ABI, walk filters, score/secondary shape, SetReader refresh. |
| `0x004ffb60` | `CUnitAI__TryStartField28TimedEvent_004ffb60` | `8b4128 85c0 743e 8b412c 85c0 7437 c7412002000000 … 68ba0b0000 d95944 … c3 33c0 c3` | Slot 7 (`+0x1c`) of CWarspite `0x005d8d1c`. Zero-arg; bare `ret` (two exits). Zero inbound `E8` (virtual-only). 21 `.rdata` copies. One `E8`: `CEventManager__AddEvent_AtTime` `0x0044b370`. If `[this+0x28]==0` or `[this+0x2c]==0` return 0. Else `[this+0x20]=2` (no already-was check, unlike slots 5/6), `fld [0x00672fd0]` (`mTime`) `fadd 10.0f` (`0x005d85cc`), `fstp [this+0x44]`, `AddEvent_AtTime(0xbba, this, &mTime, 0, 0, 0)`, return 1. `0xbba` is JT[2] of `0x004ff330` (3002), which calls this slot 10 (`[vtable+0x28]` `0x004ffbb0`). Completes the `+0x20` 0/1/2 trio. Authored name of `2` open. HIGH. |
| `0x004ffbb0` | `CUnitAI__UpdateField28TargetReaderGate_004ffbb0` | `83ec44 56 8bf1 57 8b4628 85c0 7406 f6402c04 … 68d3070000 … c20400` | Slot 10 (`+0x28`) of CWarspite `0x005d8d1c`. `ret 4`; one event arg (3002). Zero inbound `E8`. 21 `.rdata` copies. Four `E8`: `0x0047eb80`, `Random__NextLCGAbs` `0x004de8d0`, `AddEvent_AtTime` `0x0044b370` x2. If `+0x28` null or `[+0x28+0x2c]&4` (`TF_DYING`): `owner.vtable[+0xe4]()==1` then `owner.vtable[+0xc8]` (`StartDieProcess`) and return. Else require live `+0x28`, `[+0x28]->vtable[+0x184]()!=0`, live `+0x2c`, and `[this+0x44] > mTime` (slot 7 wrote `mTime+10`). Then `[+0x28]->vtable[+0x160](+0x2c, +0x30, &pos, &out)`; all-zero pos fails. Height: `0x0047eb80(0x006fadc8, pos)` minus `0.1f` (`0x005d85c0`), clamp Z. 3D `d²` vs `owner+0x1c`; `[owner+0x34]` bit `0x400` uses `6.25f` (`0x005dfb84`) else `0.5625f` (`0x005dfb80`); `d² <` thresh increments `+0x30`. `owner.vtable[+0xf4]` `GoToPoint(pos, 1)`. Reschedule `0xbba` at `mTime+0.1+rand16/65536` (`0x005d8c5c`). Fail: if `[owner+0x38]` live zero `[that+0x20]`; this slot 6; if `[owner+0x74]` `AddEvent_AtTime(0x7d3, owner, NEXT_FRAME)`. `+0x160`/`+0xe4`/`+0x184` bodies not re-derived. HIGH on ABI, deadline, GoToPoint loop, fail join. |
| `0x004fec60` | `CUnitAI__VFunc_9_004fec60` | `83ec58 56 8bf1 57 8b4e08 f6412c04 … 68b80b0000 … c20400` | Slot 9 (`+0x24`) of CWarspite `0x005d8d1c`. `ret 4`; one event arg. Zero inbound `E8`. 9 `.rdata` copies (some subclasses override). Ten `E8`. JT[0] of `0x004ff330` (3000) calls this after `owner.vtable[+0xd4]==0` and `[owner+0x214]` live. Early-out if owner `TF_DYING`, `[owner+0x244]∈{1,2}`, or `[this+0x20]==0`. Else if `[owner+0x148]==0`: `0x004fb670(owner,+0xc)` nonzero joins, else `0x004fce80(owner, target+0x1c)` or `owner.vtable[+0x100]` if `+0xc` null. If `+0x148` live and `vfunc[+0x14c]()==1`: `0x004fb670` 0/`1`/`2` picks `0x004fce80` / `0x004fcec0` / `0x004fce40`. Join: optional lerp of `+0x4c→+0x50` and `+0x58→+0x5c` when `[[owner+0x164]+0x19c]` and `0x004fd760`; then this slot 3 (`[vtable+0xc]`); `AddEvent_AtTime(0xbb8, this, mTime+delay)`. `0x004fce80`/`40`/`c0`/`0x004fd760`/`0x004062d0`/`0x004fb650` bodies not re-derived. HIGH on ABI, 3000 dispatch, early-outs, 0/1/2 pick, slot-3 join. |
| `0x004fef40` | `CUnitAI__Update` | `83ec68 53 56 8bf1 57 8b06 ff5010 … c3` | Slot 3 (`+0x0c`) of CWarspite `0x005d8d1c`. Zero-arg; bare `ret`; ST0 = 3000 delay (slot 9 adds it to `mTime`). Zero inbound `E8`. 16 `.rdata` copies. 20 `E8`. Always calls this slot 4 first. If `owner.vtable[+0x150]()` and `+0xc` live: if `[[owner+0x164]+0x19c]` then `[+0xc]->vtable[+0x168](&this+0x34)`, seed `+0x48/+0x54` as `0.04+rand16/65536*0.04` (`0x005d9088`/`0x005dfb7c`) maybe negated when `rand16/65536>0.5`, copy to `+0x4c/+0x50/+0x58/+0x5c`, then `0x00401ec0`/`0x004011b0`/`0x004062d0`/`0x004fb650`; else `0x004fb650(owner,+0xc,&+0x34)` and delay `rand16/65536+0.5`. If `[[owner+0x164]+0x128]` live: `SetReader(+0xc,0)`, `0x004fb840`, zero `+0x10`. Else if `+0x18` and `+0xc`: `0x004fb840`, maybe `+0x168`/`0x004fb650`, `owner.vtable[+0x158]`, `0x004fbc90+0.1`. Else zero `owner+0x1ec/+0x1e8` and return `rand16/65536+1.5` or `rand16*(2/65536)+3.0`. Matrix helpers not re-derived. HIGH on ABI, slot-4 first, delay returns, `+0x48` seed. |
| `0x004fe5c0` | `CUnit__ReturnField164B4ScaledByMode_004fe5c0` | `8b8144020000 83f801 7412 83f802 740d 8b8164010000 d980b4000000 c3` | Slot 111 (`+0x1bc`) of `CUnit` `0x005df998` / `CRadar` `0x005dd788` / `CSubmarine` `0x005e1490`. Zero-arg; zero `E8`. `fld [[this+0x164]+0xb4]`; if `[this+0x244]∈{1,2}` also `fmul 1.5f` (`0x005d8bd8`). HIGH. Table name is a label — `+0x164` identity open. |
| `0x004bc2e0` | `CExplosionInitThing__ClearCostGridBoundsAndBuildPath` | `51 a1b80a6300 53 8b1db40a6300 55 56 8b35c49d8200 … e8041e0000 83c42c 5f 5e 5d 5b 59 c22800` | `thiscall` `ret 0x28`. `this` is `[guide+0x20]` from `CUnit__GetGridMapByType` (`0x004fd380`). Clears the dirty-rect of the 256-wide word grid at `0x00809dc0` to `-1`, resets bounds (`0x00829dc4`/`0x00829dc8`=`0xff`, `0x00630ab4`/`0x00630ab8`=`0`), then the sole `E8` `0x004be1d0`. Four image `E8`: `0x0047d9c1`, `0x0048a880`, `0x004a0eab`, `0x004e7696`. HIGH on ABI, clear, and callers. Table class `CExplosionInitThing` is not a COLOC on this body — do not promote. |
| `0x004be1d0` | `CExplosionInitThing__BuildGridPathWithFallbackSearch` | `83ec0c d9442410 df7c2404 … 8916 33d2 897e04 895608 89560c … c7460801000000 c3` | cdecl; sole `E8` from `0x004bc3c7`. Writes the out-struct at `guide+0x24`: `+0/+4` dest ints, `+8=1` when a path exists, `+0xc` remaining count, `+0x10/+0x18` X/Y byte buffers (ctor `0x0047d590` allocs them via `Array.h` `0x0062cba4`, 0x54 bytes, seed dest=`-1`). If `0x004bc510` returns 0, store the dest cell and return; else `E8` `0x004be337` → `0x004be420`; EAX=0 falls through to `0x004beb30`. HIGH on the out-struct. |
| `0x004be420` | `CExplosionInitThing__SelectNextPathStepDirection` | `83ec08 33c0 89442400 89442404 8b442404 8b15c09d8200 … 83c408 c3` | cdecl; bare `ret`; EAX=1 dest-hit (`0x004be93d`), EAX=0 at 500 steps (`cmp [esp+4],0x1f4` / `0x004be946`). Zero stack args — walks globals `0x00829dc0` / `0x00809dbc` toward `0x00809db4` / `0x00809db0`, marks word grid `0x00809dc0`. One inbound `E8` `0x004be337`. Callees: `0x004be970` occupancy test, `0x004be9b0`/`0x004bea10`/`0x004bea70`/`0x004bead0` N/W/S/E step tests. Table class not a COLOC — do not promote. HIGH on ABI, cap, return, caller. Jump tables closed: `jmp [eax*4+0x004be94c]` at `0x004be826` (EAX 0..4). `[0]=0x004be82d` backtrack (`[esp]` depth `<=1` or `dir-1>3` → EAX=0); `[1]=0x004be883` B−1 / maybe shrink `0x00829dc4` / store 1; `[2]=0x004be8b1` A−1 / maybe shrink `0x00829dc8` / store 2; `[3]=0x004be8df` B+1 / maybe grow `0x00630ab4` / store 3; `[4]=0x004be90e` A+1 / maybe grow `0x00630ab8` / store 4. Forward arms `jmp 0x004be42d` (mark-head). Undo table `0x004be960`: `dir-1` 0 `inc B`, 1 `inc A`, 2 `dec B`, 3 `dec A`, then `jmp 0x004be471` (cap only). Abandoned cell keeps its word. Neighbour-choice independently re-read after t_62f80779: `|dA|` of `0x00829dc0−0x00809db4` vs `|dB|` of `0x00809dbc−0x00809db0` at `0x004be4a3`; `jle` (`|dA|≤|dB|`) is B-primary `0x004be728`, else A-primary `0x004be4ab`. Each arm tries four cardinals, first success `jmp 0x004be826`. Order is toward-dest primary, toward-dest secondary (`cur<=dest` uses `+`), opposite secondary, opposite primary. EAX 1=B− / 2=A− / 3=B+ / 4=A+. B-primary calls the four predicates; A-primary inlines the same unvisited-`0xFFFF` + `0x004be970` test. All four fail → `xor eax,eax` backtrack. Compass names not promoted. |
| `0x004beb30` | `CExplosionInitThing__FindNearestVisitedGridCell` | `83ec20 53 55 8b0db09d8000 56 57 8b3db49d8000 … 6681bc28c09d8000ffff … 81fd00010000 0f8cbefeffff 5f5e5d5b 83c420 c3` | cdecl; bare `ret`; zero stack args; zero `E8`. Sole inbound `E8` is `0x004be340` (the `EAX==0` arm of `0x004be1d0`). Reads dest cell `[0x00809db4]`/`[0x00809db0]` and the 256×256 word grid at `0x00809dc0` (row stride `0x200` bytes). Outer radius `ebp=0..0xFF`. First word `!= 0xFFFF` (the `0x004bc2e0` clear sentinel) wins and rewrites those dest globals — four hit exits `0x004becbd` / `0x004becdd` / `0x004becf7` / `0x004bed0c`. Miss (`cmp ebp,0x100` at `0x004bec99`) leaves dest unchanged (`0x004becb5`). Caller does not test EAX; it re-reads the globals then `0x004bed30`. Table class not a COLOC — do not promote. HIGH on ABI, caller, sentinel, rewrite-or-not. |
| `0x004bed30` | `CExplosionInitThing__StepToLowestCostNeighbor8` | `51 8b442408 8b54240c 53 55 8b08 8b12 … 668b046dc09d8000 … 668b1c6dc09b8000 … 8931 893a 5f5e5d5b 59 c3` | cdecl; two `int*` inout args (caller `add esp,8`). Zero `E8`. Sole inbound `E8` is `0x004be3d3`. `ecx=[arg0]` / `edx=[arg1]` / index `ecx*256+edx`. Seed best = current word at `0x00809dc0`. Eight bounded neighbors (N/S/W/E then NW/SW/NE/SE via `±0x200`/`±2`) win on **strictly smaller** unsigned word. Writes the winner back to `*arg0`/`*arg1`; stay if none. Table class not a COLOC — do not promote. HIGH on ABI, 8-neighbor, strictly-less, write-back. |
| `0x004beea0` | `CExplosionInitThing__SimplifyGridPathByLineOfSight` | `53 55 8b5c240c 56 8bf1 57 8b7e0c 4f 7831 … e836d6ffff 85c0 7503 4f 79cf … e8c8d5ffff … c20400` | `thiscall` `ret 4`. `this` = out-struct (`+0xc` count, `+0x10`/`+0x18` X/Y bytes). Arg = occupancy (`ebx` from `[0x00809db8]`). Two `E8` to `OccupancyBitplane__IsGridSegmentBlocked` `0x004bc510` (label). Pass 1: from `count-1` down, while EAX=0 (clear) drop; then compact and `sub [+0xc]`. Pass 2: from 0 up against cell 0, same. Sole inbound `E8` `0x004be40a`. Table class not a COLOC — do not promote. HIGH on ABI, both calls, count shrink. |
| `0x004bc510` | `OccupancyBitplane__IsGridSegmentBlocked` | `83ec10 8b542414 53 55 56 85d2 57 894c241c 0f8c9a010000 … 33c0 5b 83c410 c21000 / b801000000 5b 83c410 c21000` | `thiscall` `ret 0x10`. `this` = bitplane. Four int args `(A0,B0,A1,B1)` in `[0,0xff]` or EAX=1. Same cell → EAX=0, no read. Else swap each axis so min≤max and walk the **min→max** diagonal (slope = abs(dminor)/abs(dmajor), always ≥0): A-major samples `bitplane[(A>>3)*256+B] & (1<<(A&7))` from `minA` to `maxA`; B-major the same from `minB` to `maxB`. **Bit clear or OOB → EAX=1 (blocked); every sampled bit set → EAX=0 (clear).** Opposite-sign ΔA/ΔB therefore tests the other box diagonal. A-major tests dest; B-major skips dest. Three `E8`: `0x004be254` (start→dest; EAX=0 stores a 1-cell dest path), `0x004beed5` / `0x004bef43` (trim). HIGH. |
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
| `PlayCharMessageWait` / `PlayPCharMessageWait` | `GetNextFreeEvent` + `CScheduledEvent__Set(2001, 0.05f CLOCK_TICK, this, CVM)`. Ctor arg6 lands that node at `CMessage+0x28`. `CMessageBox__VFunc_0_004b81d0` event **3002** (`0xbba`, jump-table case 2 at `0x004b8206`) calls `CEventManager__AddEvent_ScheduledEvent` (`0x0044b310`): `due = mTime + [event+0x10]` so resume is **now+0.05s**, then the free-list recycle. 3002 is self-posted by `StartVoiceOrFallbackTextReveal` (`TimeFromNow` 0.5f when `CMessage+0x38` voice is set) and by two `AdvanceRevealAndScheduleNextTick` arms (2.7f / 0.3f). Actor `MOVE=3000` shares the number space; do not treat 3002 as an actor event |
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

## Waypoint path lookup and thing slot 61 (byte-exact 2026-08-18)

Independently re-read from pristine `74154bfa…`. `CWaypointManager__LoadWaypoints`
(`0x00505ae0`, `__FILE__` `0x0063d1f8` = `C:\dev\ONSLAUGHT2\WaypointManager…`)
allocates a **0x18-byte** object, installs vptr `0x005dfc8c`,
`CSPtrSet__Init` (`0x004e5840`) at `+8`, `CWaypoint__Load` (`0x00505960`),
then `CSPtrSet__AddToTail` (`0x004e5b20`) onto `0x00854fc0`. `CWaypoint__Load`
writes the path name at `+4` and `AddToHead`s (`0x004e5a80`) child things
whose `[thing+0x34] & 0x1000` (byte `ch` of `mThingType`) onto that set.
The type bit is occupancy only — not named here.

`0x00505c30` is therefore a named-path + nearest-child walk of that
manager set, not a `NamedEntryList` method. Both Follow natives pass
`[IScript+0x10]+0x1c` as the query position (`mPos`).

Thing `vtable[+0xf4]` is slot **61**. Independently read:

| Primary | COLOC → RTTI | Slot 61 |
| --- | --- | --- |
| `0x005df784` | `CComplexThing` | `0x00401520` `ret 0x14` — empty `GoToPoint(FVector, BOOL)` (`thing.h:293`) |
| `0x005df998` | `CUnit` | `0x004fce00` |
| `0x005dd788` | `CRadar` | `0x004fce00` |
| `0x005e1490` | `CSubmarine` | `0x004fce00` |

`CUnit__ForwardField208Slot10_004fce00`: if `[this+0x208]` live, copy the
four-dword vector + the BOOL and `call [guide->vtable+0x10]`. Independently
re-read that slot on `CGuide` `0x005dbdc4`, `CAirGuide` `0x005d8594`,
`CMechGuide` `0x005dc4f4`, and `CThunderheadGuide` `0x005df8d4`: all hold
`0x0047e2d0`. That body (`ret 0x14`): if BOOL is 0 and
`[[owner+0x13c]+0x20]==2`, no-op; else `[guide+0x1c]=1` and store the
vector at `guide+8`. Ctor `0x0047e290` sets `[+0x18]=owner`, copies
`owner+0x1c` into `+8`, zeroes `+0x1c`. Sibling predicate
`CUnit__IsField13cNotMode2_004fdc90` (`0x004fdc90`) is the same
`[+0x13c]+0x20==2` test: CUnit slot 46, 33 `.rdata` copies, EAX=0
only when the pointer is live and that dword is 2. `+0x13c` object
occupancy: `+0xc` is a `SetReader` slot (returned by slot 81
`0x004175e0`), `+0x10` cleared when slot 54 is called with 1,
`+0x20` is the mode dword. On `CGroundVehicle` the
`+0x13c` object is the `CWarspite__Init` allocation (`0x60` bytes,
store `0x0047d1a5`). That init defaults `+0x20=-1` and writes `2`
when `+0x28` and `init+0x3b8` are live; `CUnitAI__TryStartField28TimedEvent`
`0x004ffb60` (slot 7) is the other image writer of `2` on this layout:
it requires live `+0x28` and `+0x2c`, stores `mTime+10.0f` at `+0x44`,
and schedules `0xbba` (3002 → slot 10). Slot 10 keeps going while
`+0x44 > mTime`: `vfunc[+0x160]` sample, `GoToPoint`, reschedule
`~0.1s`; miss falls into slot 6. No already-was string.
`CUnitAI__TryStartFollowWaypoint` `0x004fea30` (slot 5) treats
`+0x20==0` as already-following (string `0x00633cb0`) and otherwise
writes `0` then schedules `0xbb9`. Slot 6
`CUnitAI__TryStartFightingMode1_004febe0` is the dual: `+0x20==1` is
already-fighting (string `0x00633c80`) and otherwise writes `1` then
schedules `0xbb8` at `&mTime`. Slot 8 calls it with no extra arg.
Slot 4 `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0` is the
`GoToPoint` companion: `+0xc` is a `SetReader` thing slot cleared
on `TF_DYING`; it writes `+0x18/+0x1c` and joins `0x004fb500`
(`ret 8`; reject `0x004fb670`; height gate via `0x0047eb80` /
`[target+0x24]` vs `[[+0x140]+0xa0]+0x6c/+0x70`; pass calls
`0x00507ab0`; fail/no `+0x140` is EAX=`[+0x144]!=0`).
Slot 11 `CUnitAI__SelectOrRefreshCloseTarget_004ff710` reuses that
join on a fast path (`vfunc[+0x16c]==0.0f` and `+0x14` live) else
walks `0x00855090`/`b0`/`c0` by `[owner+0x138]`. The walk takes
`[node]` / `[node+4]`, redirects `+0x34` bit `0x20000000` through
`vfunc[+0x128]`, keeps bit `0x10`, then gates `0x004fd5b0` /
`0x004fd3d0` / `0x004fb3d0`. Score is random `* 1/8192` or a
`[edi+0x34]` → `[owner+0x164]` table; secondary uses `0x004fb780` /
`0x004fb7e0` (`ret 0x10`) plus `10000`/`1000000`. A winner
`SetReader`s `+0xc` and always clears `+0x10`.
That message is JT[1] of
`0x004ff330`: if `[owner+0x214]` is live it calls slot 8
`0x004feac0`; it does not rewrite `+0x20`. 3000 calls slot 9
`0x004fec60` after the same `+0xd4`/`+0x214` gates. Slot 8 is the 2D
4.0f advance / `GoToPoint` / 3001-reschedule body. 3003
reschedules 3001 while `+0x20==0`. Authored name of `2` stays open. Sibling dest-mode slots on the same `CGuide` table (all virtual;
zero `E8`):

| Slot | Address | Name | Mode write | ABI |
| --- | --- | --- | --- | --- |
| 4 | `0x0047e2d0` | `CGuide__VFunc04_SetVectorMode1_0047e2d0` | `1`, skip if BOOL=0 and `[+0x13c]+0x20==2` | `ret 0x14` |
| 5 | `0x0047e310` | `CGuide__VFunc05_SetVectorMode2_0047e310` | `2` | `ret 0x10` |
| 6 | `0x0047e340` | `CGuide__VFunc06_SetVectorMode3_0047e340` | `3` | `ret 0x10` |
| 7 | `0x0047e370` | `CGuide__VFunc07_SetVectorModeFromOwnerState_0047e370` | `3`, or `0` if `[owner+0x140]+0x94` live; skip if `[+0x13c]+0x20==2` | `ret 0x10` |
| 8 | `0x0047e3d0` | `CGuide__VFunc08_ResetVectorsFromOwner_0047e3d0` | `0`, copy `owner+0x1c` to `+8`, zero `owner+0x14c` | `ret` |

FollowWaypoint uses slot 4 / mode 1. The ground-vehicle consumer of that
mode is `CGroundVehicleGuide` slot 3 (`0x0047d750`): after the dying /
near / mode-0 / `[unit+0x244]∈{3,4,5}` gates it `cmp [guide+0x1c],1`.
Mode 1 then path-queries `0x004bc2e0` into `guide+0x24` when
`d² > 1.0f` and `[guide+0x20]` is live, unless dest ints still match
`guide+0x24/+0x28` within 1. The out-struct (ctor `0x0047d590`, writer
`0x004be1d0`) is: `+0/+4` dest ints, `+8` path-present (`guide+0x2c`),
`+0xc` remaining count (`guide+0x30`), `+0x10/+0x18` X/Y bytes
(`guide+0x34/+0x3c`). Follow walks **from the end**: world cell
`(2·byte+1, 2·byte+1)`; pop while 2D `d² < 0.5f`; empty heads at dest
`guide+8`; then `fpatan`. Table class on `0x004bc2e0` stays unpromoted
(no COLOC). `FollowWaypointWait` refuses when
`[IScript+0x10] != [IScript+8]`. Heading apply: prologue saves
`[owner+0x114]` as current yaw and `fpatan(dest−owner)` as desired;
path-follow overwrites desired with the waypoint heading; join
`0x0047dee0` stores desired at `[owner+0x120]`. `|Δ|≤0.6` near-exits.
`|Δ|>0.6` writes a local-Y step (`slot 111 * 0.05 * ±4`) through
`mOrientation` into `owner+0x14c`. Apply: `CGroundUnit__UpdateLinkedEffectsByHeightClearance`
adds `+0x14c * 0.4f` into `mVelocity`; `CActor__Move` adds `mVelocity` to `mPos`.
`+0x120` is consumed by `CUnit__SmoothEulerTowardTargetAndBuildMatrix` (slot 77).
When `0x004be420` returns 0, `0x004be1d0` calls `0x004beb30` once, then
continues the same `0x004bed30` walk from whatever dest cell the fallback
left in `0x00809db4`/`0x00809db0`. Each `0x004bed30` step writes the
8-neighbor with the strictly smaller unsigned word (or stays). The loop
stops when the stepped cell equals the start cell (`[esp+0x10]`/`[esp+0x20]`
from the owner-pos fistp) or the previous cell, then `0x004beea0` may run.
`0x004beea0` is `thiscall` `ret 4` on the out-struct: two passes of
`0x004bc510` (clear=0) drop a prefix then a suffix of the X/Y bytes and
shrink `+0xc`. `0x004bc510` itself is `thiscall` `ret 0x10` on the
occupancy bitplane: four int cells, EAX=1 when any sampled bit is
**clear** (or a coord is outside `[0,0xff]`), EAX=0 when every sampled
bit is set. The walk is the min→max box diagonal, not the original
directed segment when ΔA and ΔB have opposite signs. Independently
re-read (not just the child report): `0x004be420` jump tables at
`0x004be94c` / `0x004be960` — EAX 0 backtracks, 1..4 step B−/A−/B+/A+
into the mark-head; undo reverses that step into the 500-cap check.

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
- When the `Play*MessageWait` `CScheduledEvent` actually fires: CLOSED.
  Stored at `CMessage+0x28`. `CMessageBox__VFunc_0_004b81d0`
  (`movsx [event+4]; add eax,0xfffff448`; cases 3000–3004) case 2
  (`0xbba`) is `AddEvent_ScheduledEvent` of that node. Due time is
  `mTime + 0.05f`. Cheapest falsifier: another reader of
  `CMessage+0x28` that also inserts the node.
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
  Flag=1 loose-`.msl` sites (independently re-listed 2026-08-18):
  `level600/Ship.msl` `FollowWaypoint("Interception", 1)`,
  `level600/Slave.msl` `FollowWaypoint("Slave", 1)`,
  `level731/messages.msl` and `level732/messages.msl`
  `FollowWaypoint("Fenrir", 1)`, `level741/Marshall.msl` and
  `level742/Marshall.msl` `FollowWaypoint("marshall", 1)`, plus
  commented `level731/732 Fenrir.msl` `FollowWaypoint("Withdraw", 1)`.
  None names the argument. Registry record `0x0064ce20` has no
  arg-name pointers. Authored name still open. Cheapest remaining
  instrument: pinned `IScript.cpp` we do not have, or a runtime
  `arrived()` handler that reads the boxed `CInt`. All 762 13-slot
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
