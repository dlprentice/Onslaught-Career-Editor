# CComplexThing function map

Status: active static function map
Last updated: 2026-09-12 (aircraft weapon model inputs and original model-time fraction experiment)
Summary: script-bearing Thing contracts and related Unit movement ownership,
including the bounded angle-update, matrix and controller arithmetic evidence.
Source File: `C:\dev\ONSLAUGHT2\thing.cpp` (SEH `__FILE__` pointer
`0x006331c0` read out of `CComplexThing__SetScript`) | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — every byte below was re-read from the pristine specimen at
file offset VA − 0x400000 with `tools/disasm_va.py`; whole-image scans by
`tools/call_xref_scan.py`. Architecture from pinned GPL
`references/Onslaught/thing.cpp` / `thing.h` (lines cited). Function names are
the dated Ghidra readbacks; current name authority remains in
`developer_state.json` → `current_re_authority.latestLiveGhidraState`.
The byte contracts below are independent of the names.

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
| `0x004fce00` | `CUnit__ForwardField208Slot10_004fce00` | `8b8908020000 56 85c9 742a 8b542418 8b742408 52 8b01 83ec10 … ff5010 5e c21400` | Slot 61 of `CUnit` `0x005df998`, `CRadar` `0x005dd788`, `CSubmarine` `0x005e1490` (COLOCs independently walked). If `[this+0x208]==0` return; else forward the 4-dword vector + BOOL to `[+0x208]->vtable[+0x10]`. That slot is `CGuide__VFunc04_SetVectorMode1_0047e2d0` on `CGuide` / `CAirGuide` / `CMechGuide` / `CThunderheadGuide`. HIGH on the forward. |
| `0x0047d1c0` | `CGroundVehicle__VFunc_66_0047d1c0` | `81ec94000000 56 8bf1 8b06 ff90b8000000` | Slot 66 at `.rdata` `0x005e2a84` (vtable `0x005e297c`). Early-outs on `vtable[+0xb8]==0` or `[this+0x260]==0` jump to the tail, not over it. Tail `E8` `0x0047d396` is `CGroundUnit__UpdateLinkedEffectsByHeightClearance`. HIGH on the tail. |
| `0x0047c970` | `CGroundUnit__UpdateLinkedEffectsByHeightClearance` | `83ec68 53 55 8be9 56 57 8b4500 ff5060 … d9854c010000 d80d408c5d00` | Nine inbound `E8` (Boat/Cannon/GV/Infantry/Mech/Mine/Sentinel/WarspiteDome). Reads `owner+0x14c/+0x150/+0x154`, `fmul 0.4f` (`0x005d8c40`) into `[esp+0x38/+0x3c/+0x40]`. At `0x0047ccc3` adds that vector into `mVelocity` (`+0x7c/+0x80/+0x84`) `edi` times then `fmul [esp+0x10]`. Then `E8` `0x0047cd94` → `CUnit__UpdateMotionAttachmentsAndEffects`. HIGH on the `+0x14c`→`+0x7c` add. Table name is a label. |
| `0x004fa8d0` | `CUnit__UpdateMotionAttachmentsAndEffects` | `81eca8000000 53 55 8be9 56 57 8b8d08020000 85c9 7417 … ff500c` | Slot 66 of `CUnit` `0x005df998`. If `[this+0x208]` live and (`[this+0x214]` live or `TF_DYING`), `call [guide.vtable+0xc]` = VFunc03. Then `0x004fa800`, then `CActor__Move` `0x004015e0` (`E8` `0x004fa91b`). Does **not** itself read `+0x14c`. If slot 76 returns nonzero, compares `+0x114` vs `+0x120` as three floats and on mismatch `call [vtable+0x134]` (`0x004fa4b0`). HIGH on the order. |
| `0x004015e0` | `CActor__Move` | `83ec30 a1d02f6700 53 8bd9 55 56 8d6b1c 8983d8000000` | `lea ebp,[this+0x1c]` (`mPos`). `fadd [this+0x7c]` / `[+0x80]` / `[+0x84]` into `mPos` XYZ (`0x0040175a..0x00401775`). Matches `actor.cpp:58` / `114`. HIGH on the add. |
| `0x004fa4b0` | `CUnit__SmoothEulerTowardTargetAndBuildMatrix` | `8b01 83ec38 56 8b742440 57 8b7c2448 ff5060 d906 d81f … f3a5 5f 5e 83c438 c21000` | Slot 77 (`+0x134`) of `CUnit` / `CRadar` / `CSubmarine`. `ret 0x10` — four args: current*, desired*, rate*, `FMatrix*`. Slot 66 passes `+0x114`, `+0x120`, `+0x12c`, `mOrientation`. Smooths current XYZ toward desired (X/Z unwrap via `±π/2` / `2π` / `±π`; Y no wrap). Step scaled by `vtable[+0x60]()` and `0.1f` (`0x005d85c0`), capped by a float store of `rate[i] * multiplier`. Then sin/cos of the three current angles; `rep movsd` copies nine meaningful words and three unwritten padding words into arg3. One `E8` `0x00428c21` (`CComponent__MaybeSmoothVectorTowardTarget`). HIGH. |
| `0x004de700` | `Return1f` | `d90568855d00 c3` | Slot 24 (`+0x60`) of `CUnit` `0x005df998` / `CRadar` `0x005dd788` / `CSubmarine` `0x005e1490` (re-read dwords `00 e7 4d 00`). Zero-arg; `ECX` unused; zero `E8`; zero inbound `E8`/`E9`. `fld dword [0x005d8568]` (`00 00 80 3f` = `1.0f`); bare `ret`. HIGH. Child `t_416de69b` REPORT.md independently reproduced. Do not promote a CUnit-owned name — this is a folded stub. |
| `0x0050e940` | `CGroundUnit__ReturnFloat005d85bc_0050e940` | `d905bc855d00 c3` | Slot 24 of `CGroundVehicle` `0x005e297c` is **not** `Return1f`. Same shape; `[0x005d85bc]` = `00 00 80 40` = `4.0f`. HIGH on these bytes. Subclass override, not the CUnit answer. |
| `0x005333b0` | `IScript__Constructor` | `c706d4925d00 8d4e28 e85b24fbff … c706084f5e00 894608 894e0c 897168 … 897e24 … c20800` | `ret 8`; args `(thing, eventObj)`. Installs `CMonitor` vptr `0x005d92d4` then IScript vptr `0x005e4f08`. `CSPtrSet__Init` at `+0x28`. `[this+8]=[this+0x10]=thing`; `[this+0xc]=eventObj`; `[eventObj+0x68]=this`. Zeroes `+0x14` / `+0x18` / `+0x1c` / `+0x24` / `+0x38`. HIGH. Only `E8` is `SetScript` `0x004f42a8`. |
| `0x0050abc0` | `CWorld__CloneScriptObjectCodeByName` | `8b8520010000 … ff5038 … 3a16 … 7443 8b4f04 e8e1e30200 c20400` / miss `6858… 68d2886300 e8f56af3ff 33c0 c20400` | `ret 4`; `this` = world `0x00855090`. Walks `[world+0x120]` comparing each object's `vtable[+0x38]` string to the arg. Hit: `CScriptObjectCode__Clone` (`0x00539040`) of `[node+4]`. Miss: `CConsole__Printf` `\"FATAL ERROR: Cant find script '%s'\"` (`0x0063d288`) and return 0. HIGH. Only `E8` is `SetScript`. |
| `0x00535c50` | `IScript__SetScript` | `8b442404 8bf1 8b08 8b11 ff5238 8b4e10 50 e8c9e5fbff c20c00` | `ret 0xc`. `args[0]->vtable[+0x38]()` (name string) then `CComplexThing__SetScript` on `[IScript+0x10]` (the thing). HIGH. Registry command; second static `E8` to `SetScript`. |

### Unit Euler update: isolated execution, September 8

Pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`:
the complete half-open body `0x004fa4b0..0x004fa7ff` is 847 bytes, SHA-256
`3cfa2696dd4a9092812c0ea179a4e5f7bde29612cd9f5723312a417122fce9fc`.
Its constant span `0x005d85c0..0x005d85ec` is 44 bytes, SHA-256
`12f15b616e7383bee36c61feaa35e9bf36973b86f17979a41ee8924a1ad51b69`.

The private ELF32 probe executes those unchanged bytes at their retail virtual
addresses, supplying only the virtual move-multiplier return. Nineteen finite
cases ran at controlled PC24/RN and PC53/RN. The probe copies the three updated
angles and nine meaningful matrix words; it excludes the three unwritten
padding words copied by retail. Private files `unit-euler-native-probe.s`,
`unit-euler-native-probe.py`, `unit-euler-native-probe` and
`unit-euler-native-final-20260908.log` are in
`local-data/test-runs/linux-route-20260906-af1sa_l9/`.
No game frame, initialization, resource, RNG or live gameplay FPU was sampled.

The update uses retained yaw/pitch/roll, not matrix-derived integer angles:

- Equal components skip every update/store; yaw and roll also skip wrapping.
  Equal `-0/+0` therefore preserves current `0x80000000`.
- Yaw/roll adjust a temporary desired value across strict opposite `±π/2`
  boundaries. Direction separately uses the original difference against `+π`.
  Pitch never wraps. Updated yaw/roll are stored before at most one `±2π`
  correction. Generic normalized error does not reproduce these branches.
- The cap is a float store of `multiplier × rate`. Calculated step is ordered
  `abs(current − adjustedDesired) × multiplier × 0x3dcccccd`; it is replaced by
  the cap only when greater and otherwise stays on the x87 stack through addition.
  The subnormal case current word 1, desired word 6 produces word 2; prematurely
  storing the step produces word 1.
  From zero toward `0.1f` with unit rate/multiplier, retail produces
  `0x3c23d70b`; division by ten would produce `0x3c23d70a`.

Matrix construction stores yaw sine/cosine and roll/pitch cosines as float32,
but retains roll/pitch sines. The product at `0x004fa784` is stored **without
popping**: M02 uses the retained product, while M12 reloads the stored copy.
For equal Euler words `(3f333333,3f8ccccd,becccccd)`, controlled PC24 produces
M02 `3e6c827e`; PC53 produces `3e6c8280`. Neither `Math.Sin/Cos` equivalence nor
the live game's control word follows from these measurements.

`rebuild/OnslaughtRebuild.Core/RetailUnitEuler.cs` carries the finite PC24
angle update and matrix operation order. Matrix construction uses managed
double sine/cosine for the retained transcendental results, with the measured
PC24 operations and separate float stores. This is provisional outside its
finite native comparisons; general x87 trig equivalence is not established.
The creation/movement transaction remains unported, so the current Level 100
Plane mover and its replay fingerprint are unchanged by this primitive.

### Copied-retail Plane observation, September 8

The installed Linux Steam `BEA.exe` matched the pristine identity above before
copying. A fresh copy of its data and six selected executable/options/DLL inputs
ran through the installed Proton Experimental Wine loader on an authenticated,
TCP-disabled private Xvfb display, with software OpenGL requested. The required
three VKD3D DLLs came from that existing Proton installation into the private
prefix. This used WineD3D, not the normal Steam container/DXVK launch route.
Proton's installed version was `experimental-11.0-20260903c-x86_64`.

Launch arguments were `-forcewindowed -nosound -nomusic -skipfmv -level 100`.
Level 100 rendered successfully; this development entry bypasses the frontend
and is not a cold-start or player-input acceptance run. No desktop input,
desktop capture, Ghidra opening or game-code patch was used.

Hardware breakpoints were installed **after** Wine exec'd its i386 preloader.
Earlier pre-exec attempts yielded no samples. The accepted `observe-f` receipt
contains one AirGuide constructor exit (`0x004021e7`), twelve clearance-cache
entries (`0x004028e0`) and twelve Plane Euler entries (`0x004fa4b0`). Both
complete constructor/Euler bodies matched the pinned pristine bytes in live
memory. All 25 samples read x87 control word **`0x007f`**, PC24/RN, on the
same thread. This establishes those calls on this backend, not all gameplay
sites, Steam-default behavior or Windows precision.

The one authored Trainer receiver had position `(265.5, 392.5, -15)`, current
and desired Euler words `(40490fdb, 00000000, 00000000)`, zero velocity/drive,
all three caps `3d32b8c2`, normal state zero and motion gate one. Its initial
guide cache X/Y words were zero. Static constructor bytes do not write those
two cache fields; this one observed allocation does not establish zero as a
general initialization rule. At the first cache entry the owner had already
updated orientation but had not translated, consistent with the initial
movement preceding the first clearance event.

The existing unchanged-byte native oracle reproduced **eleven consecutive
live Euler and nine-word basis transitions** using the twelve captured inputs
and the measured Plane multiplier getter (`0x004de700`, returning `1.0f`).
The managed matrix matches all nineteen original and twelve live-input native
outputs. Focused Core checks passed **50/50**: nineteen angle cases and those
thirty-one matrix cases. These comparisons exclude matrix padding and do not
establish an entire aircraft trajectory or universal trig equivalence.

Private launch/debugger scripts, `observe-f/observations.jsonl`, live identity
checks and `euler-comparison.log` are in
`local-data/retail-runtime/aircraft-20260908-a/`. The copied executable and real
options file retained their input hashes after the run. Each owned prefix and
display was stopped and its temporary authority cookie removed. The separate
Core test log is `unit-euler-live-matrix-20260908.log` under the existing
`local-data/test-runs/linux-route-20260906-af1sa_l9/` owner.

A second bounded run, `observe-plane-motion-a`, captured **32 consecutive
living authored-Trainer Moves** at four boundaries per call: Plane entry
`0x004d1cd0`, Guide entry `0x00402280`, Unit Euler entry `0x004fa4b0`, and
Plane exit `0x004d1efd`. All 128 samples used the same owner/thread and control
word `0x007f`. `observations.jsonl` is 201,256 bytes, SHA-256
`8646c4f0d52b421cfcdf1daf86b5e15374540876c810e5b7c659a0d1efa96120`.
The six live bodies matched pristine before sampling:

| Half-open body | SHA-256 |
| --- | --- |
| Guide `00402280..004026a3` | `f0b8a93f873609f61f457633ad1ea6e350f0727b03f534184ca8124393b97b55` |
| Air `00402fa0..0040364c` | `15b1267923260b84c6cbe1731add1d17f27e2b7eb84815806aa7e362ef6ff69e` |
| Unit `004fa8d0..004fb264` | `2f2dfe0e12adc623380755ddec800c90bd611fd884e9bca61818a90897c58d5f` |
| Actor `004015e0..004018fa` | `083c7a029afed634fa4108036a3057355e7dc3b78f8716f5d6588d49f8505a23` |
| Euler `004fa4b0..004fa7ff` | `3cfa2696dd4a9092812c0ea179a4e5f7bde29612cd9f5723312a417122fce9fc` |
| Plane `004d1cd0..004d1f05` | `049e2d26e948b444190073c335fb7d233aefa75893870e86ebf33f15d4f5e72f` |

The compiled Core arithmetic matched **352 grouped comparisons** across all
32 calls: integrated velocity, next drive, desired/current Euler, bank flag,
translation, old pose, new basis and final aligned velocity. This comparison
supplied the observed guide destination/cache, mode, controller state and
speed mode; it did not reconstruct the callback/random stream. The retained
log is `managed-plane-comparison.log` beside the private launch scripts.
The first Move does not translate. Its Guide writes the next drive; the
second Move's cap is the stored-float product `9.2f * 0.05f`, not division
by twenty. Air consumes old drive before Guide; Actor translates before
Unit smoothing; Plane aligns velocity to the new forward column afterward.
The final observed position words are `4384b1b6,43bd21ff,c17d37c4`.

No captured contact timestamp changed and the avoidance reader was null.
This bounds the comparison to the living free-flight branch; it does not
prove absent MapWho effects, complete death/trail/audio behavior or arbitrary
managed/x87 trig equivalence. The copied executable and real options retained
their input hashes; the owned Wine prefix/private display stopped cleanly.

The production Level100 mover now uses `RetailPlaneMotion` with creation-owned
raw Actor state and the existing `RetailEventScheduler` for Move and Guide
events 2000/2001. Script waypoints supply full raw XYZ. Ground-clearance cache
refresh uses the native integer lookup and callback cadence, including the
draw on an unchanged cell. The observed zero cache-coordinate allocation is
the explicitly selected deterministic startup seed, not an inferred native
constructor store. Frame/pool/guide state survives snapshot, restore and hash.

Remaining controller inputs are material: script `SetAIState` writes Unit
`+0x210`, whereas Guide reads controller `+0x20`. The native Plane controller
`[004d21c0,004d248c)` retains approach/retreat hysteresis and schedules its own
callbacks; the current script/weapon bridge still refreshes an attacked
target during Move. The common `004fef40` callback can consume zero or one
direct random draw depending on its readiness/support arm, with further
effects in callees; adding an unconditional draw would be incorrect.
Plane profiles Air Trainer/Target Drone keep `+0x120=0`, excluding the optional
player-distance detour. Battle Engine's Level100 radius is `0.4f`, and its
ground-mode aim point adds `0.76f` to retail Z; jet aim uses its origin. These
virtual inputs and common AI calls still need production integration.

The September 12 working-project export confirms the controller's saved body
already contains wing-helper calls `004d229f` and `004d2400`; the old Plane
note's missing-boundary statement was stale. The actual ABI passes the receiver
in ECX and one event pointer at entry stack offset `+4`: dispatcher
`004ff420–004ff425` pushes the event and calls vtable slot `+24h`, while
`004d244b` reloads that argument after the `34h` local allocation and three
saved registers. `004d2453` forwards it for event reuse; `004d2489` is `RET 4`.
The [one-function prototype correction](../../../tools/cohort-specs/plane-controller-event-argument.manifest.tsv)
preserves the unknown return type, existing name, body, comments and tags.

The reopened decompiler still invents `unaff_retaddr` in that event call.
Its local-vector expressions also disagree across the indirect output-pointer
call at `004d22ae`: raw `004d22a7` and `004d22ba` use the same `[esp+10h]`
location before the push and after the callee returns. A missing four-byte
cleanup in indirect-call analysis is a candidate explanation, not an applied
correction. The read-only depth probe reports unknown depth after the first
indirect call, no explicit stack-depth overrides, and unchanged saved purge
metadata. Do not translate the decompiled locals as if this artifact were fixed.
Fresh exports, raw disassembly, prototype receipts and the private depth probe
are under `local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/`.

The September 12 isolated ELF32 probe executes the unchanged 716-byte Plane
controller at its retail address, with all six referenced constant words
verified against the pristine specimen above. Parent re-execution passed
**11/11** cases: strict 70/25 separation boundaries and adjacent floats,
initial retreat even when setting the approach latch, classifier 0/1/2,
signed zero, call order and event due time under PC24/RN. Reflection preserves
the native subtractions: for each component `P=1`, `Aim=33554432`, the result
is `cc000000`, whereas simplifying to `2P-Aim` gives `cbffffff`.
The body hash is `9a6baa321ef93f4dc6385441a425428ee0ea13904f5dd9394201698d7f605c93`.
Private `plane-controller-20260912.py`, its inputs/outputs/results and
`plane-controller-parent-20260912.log` are under the existing Linux test owner
named above. Common Update, aim, radii, range classification, random draw and
event admission are explicit stubs; this does not validate their live inputs
or establish an aircraft gameplay trajectory.

The separate `plane-controller-scheduling-20260912.py` continuation passes
18 cases, retaining the original 11-case artifacts. Supplied common-return
delays 0, -10 and 100000 do not affect the Plane's own due time. Its dying-owner
branch makes no calls. A null target clears hysteresis; a nonzero slot-5 return
bypasses the direct recurrence, while zero reaches the waiting/scheduling arm.
The incoming event is forwarded unchanged. This verifies supplied-return and
branch behavior, not absence of side effects inside the stubbed common Update
or slot 5.

### Aircraft spawner exit and script readiness — September 12

The compiled LevelScript at IP423 spawns Air Trainer from Airfield/SpawnerB
with selector 1; Hangar's drone calls use SpawnerB or alternate SpawnerA/B,
also selector 1. The shipped `.msl` files under `data/MissionScripts/level100/`
and the admitted `.mso.bin` objects in Core's Level100 script assets agree.
Selector, animation frame and list ordinal are separate values.

`IScript` SpawnThing writes its current source owner to initializer `+3b4` at
`00536fb3`, and SpawnerA/B map to `+3b8=15/16`. The shared initializer at
`004fe710` constructs RTTI CUnitAI; its saved name is now `CUnitAI__Init`. Plane Init
then installs CPlaneAI and stores the separate listener at Unit `+13c`.
For these spawns the controller starts at `+20=2`, index `+30=1`, and deadline
`+44=float32(NOW+10)`, requesting event 3002 at NOW with null reuse. It does
not request script Ready during this constructor. Unit AI state `+210` starts
at zero independently. Both selected profiles inherit Sweeping `+19c=0`,
excluding the constructor's optional four direct random draws.

The original event-3002 callback `004ffbb0` queries the spawning owner's
`+160(tag,index,position,basis)`. Deadline comparison is strict; an all-zero
position terminates the exit. It clamps Z to terrain minus `0.1f`, increments
the index at strict squared distance below `6.25f` for owner type bit `0x400`
(`0.5625f` otherwise), and requests GoTo with override TRUE. Arrival uses raw
XYZ float deltas and the PC24 sum `(Z² + Y²) + X²`; the old selector's point
is still sent on the incrementing update. Continuation draws once
directly and submits 3002 with incoming-event reuse at the float32 store of
`rand16*float32(0.1/65536) + NOW + 0.1f`, preserving that order.
Normal completion invokes the real `004febe0` state-1 helper. When controller
state is not already 1, it submits a new controller 3000 at NOW; the already-1
branch reports the redundant transition and submits none. If the Plane owns
a script, completion then submits a new **Plane-owned** event 2003 at NEXT_FRAME.
A missing/dying spawning owner first checks **GetVulnerable == 1**, not an
owner-kind discriminator. Plane slot `+e4` selects `00405e40`, which reads
Unit `+15c`; the selected constructors initialize it to 1. None of the admitted
Level100 object programs sets vulnerability. AirUnit `00403690` calls Unit
`004fd140`: mark TF_DYING and notify StartedDying, without the base CThing's
immediate shutdown declaration. Child/particle/provider cleanup and complete
dying flight remain separate work. This path bypasses Ready and normal handoff.
The working Ghidra exit comment now carries this distinction through the
[one-comment correction](../../ghidra/README.md#unitai-exit-contract-comment-2026-09-12).
The preceding correction manifest remains frozen.

The terminal write at `004ffd87` clears **CST +20**, reached through
Unit `+38`: it is the raw collision-ignore pointer, as corroborated by
`thing.h:248`, `InitThing.h:97` and the constructor copy at `0042619a`.
It is not the AirGuide's clearance or mode. The controller's monitored
spawning-owner reader at `+28` survives StartedDying; it is invalidated by
the spawner's shutdown/delete reader chain. These two identities have separate
lifetimes, including when a deleted spawner leaves the raw CST value retained.

AirUnit GoTo `[00403a90,00403b52)` applies a **second** altitude clamp after
the exit arrival comparison: RN-rounded target X/Y select the integer terrain
sample `0047ea20`; height is multiplied by the world scale, limited by water,
then reduced by profile MinAltitude. Guide `[0047e2d0,0047e30f)` receives the
four-word point and TRUE override, allowing it to set mode 1 while controller
state remains 2. The profile default store at `0042f0e9` sets `+15c=4.0f`;
the field-42 factory at `004321b1` and setter `00432be0` identify the override.
Air Trainer row 601 and Target Drone row 660 inherit Base Air Unit row 570;
all three omit field 42 in the exact 175,603-byte physics input identified
below. Core therefore uses 4.0f for this admitted pair only.

Private `plane-controller-init-20260912.py` passed 18 cases and
`plane-controller-exit-20260912.py` passed 26. They execute unchanged bodies,
check all 100 synthetic receiver bytes, preserved registers and stack state;
the initializer also checks the original SEH push/pop against private FS memory.
The exit probe executes the real state-1 helper from state 2 in all 26 cases;
the already-1 guard above is separate static instruction evidence. SetReader, scene virtuals,
terrain, random values and AddEvent remain explicit stubs: event **submission
order and reuse arguments** are established, not complete dispatch or arrival
time. Independent reviewers checked the retained ELF load mappings and outputs.
The three body hashes, in address order, are:

| Range | SHA-256 |
| --- | --- |
| `004fe710..004fea24` | `2eadfbd3a63747b453291d5b7584cb973c6b5bc239e755cfa329ccf3b16dfd1d` |
| `004febe0..004fec5b` | `cd1eee4e958eaf9ef083c911b6bdf5f2383d6cdacb4e54916009562f0d448181` |
| `004ffbb0..004ffdca` | `76ba731fe0d45a277013a54c9526266b1dbb5f0e2f697630ae1dc9d4c3057a20` |

The later private `plane-controller-exit-goto-20260912.py` passed **26/26**
cases with the same unchanged exit/transition and actual GoTo/Guide bodies.
Its CST and guide are distinct receivers: completion clears only CST-ignore,
while guide mode, destination and clearance survive. The added body hashes are
`1254c7668761e7053297ebe62104d681018df8c5d5228bdc35abb5b0f4f663ba`
(GoTo, 194 bytes) and
`af5c2fb30c7f793d22d559118bca26416965260210cf615e98e2414e3eaf53b5`
(Guide, 63 bytes). Integer/interpolated terrain, scene queries, vulnerability,
StartDying, RNG and event admission remain controlled stubs. This composition
tests both clamps and their order, not a live arrival time or full world dispatch.
The earlier probe's synthetic `guide` variable named the CST receiver;
its raw write observation was valid, but that variable did not identify its type.

The Airfield is CBuilding, whose `+184` capability returns 1. Attachment tags
15/16 explicitly bypass the Unit/profile cache and query case-insensitive
**WaypointA/B**, with exact CEMT selector matching. They are not SpawnerA/B's
launch transforms. The selected aircraft-factory mesh has only selector 1:
WaypointA is part 18 and WaypointB is part 12, with no selector 2. Both points
own CPOS; CORI inherits through flag `+120` to root part 0. Native
`004b1149..004b1169` follows the first flag-zero ancestor independently of
the `+11c` position owner. All relevant chains have one hierarchy pose and
101 zero frame-map entries. This closes constant stored-cache interpretation;
the separate render cache and arbitrary animation remain outside it.

The materializer now carries these exit selectors/model transforms into the
four Airfield spawn definitions. Core owns/hashes them and exposes the bounded
seated-owner lookup through `GetPlaneSpawnerExitPoint`. The selected mesh is
86,028 bytes, SHA-256
`23219fc98eba73c19c83b3ae07ea92fa750d8f71362ccedfc1bfdec474629899`;
its inflated hash is `893b5b0141d66394a6e19506be82c38c720f000a476391174862ef6864f33276`.
Exact calculated world-pose checks use independent PC24 composition and HFLD
inputs, not observed live cache words. Core now owns the separate 3002 exit
listener and both retained owner identities, selector/deadline, normal callback
and targeted script Ready delivery. It defers script destination/target control
and new burst requests until handoff, without canceling an already pending burst.
The next normal callback explicitly resumes the pre-existing approximate
target/weapon bridge; it does not implement common AI/provider selection,
readiness, hysteresis or recurring normal 3000/3001 work. Ready's script commands
settle inside callback dispatch, and restore retains this ordering. Spawner-loss
death preserves health/parts and Move recurrence, but actual dying motion and
transitive teardown are still absent. These are in-process implementation
checks, not an observed retail exit or complete combat acceptance.
The [validation record](../../../VALIDATION.md#aircraft-spawner-exit-inputs--september-12)
owns earlier input receipts; the [lifecycle record](../../../VALIDATION.md#aircraft-exit-lifecycle-integration--september-12)
owns the new checks, private output paths and remaining limits.

### Remaining selected-provider integration

The remaining weapon integration is consequential. Static inspection of
`004fc000` requires the selected `Unit+140` provider, `+1e8` readiness and the
weapon's strict `NOW > +64` gate. `004fbcb0` prepares that provider;
`004fc080` fires only that provider on a later ready invocation and clears
`+1ec/+1e8`. The existing every-tick/all-slots weapon loop is therefore not
an implementation of this callback chain. Selected-provider retention,
readiness, burst callbacks and common AI effects still need runtime ownership.
When wiring Fire into scheduler callbacks, preserve round admission order: the
current Core round loop follows scheduler Flush. Moving launches into that
Flush without changing round admission would move newborn rounds on their
birth tick, bypassing their next-frame movement contract.

The selected-provider helper `[004fb840,004fbc8b)` is 1,099 bytes, SHA-256
`8cafb4818c878d1be88a5b30a47375ad1190949cb836110e27a17fb4040106df`.
The working database now carries these descriptive corrections, with the
existing ABI and function boundaries preserved:

| Address | Current Ghidra name |
| --- | --- |
| `0x004fb840` | CUnit__SelectAttackProvider |
| `0x00509f70` | CWeapon__IsReadyToFire |
| `0x0050a0b0` | CWeapon__GetActiveTargetMaskIntersection |
| `0x0050a0d0` | CWeapon__GetTargetMaskIntersection |
| `0x0050a290` | CWeapon__HasIncompleteBurst |

The old squad/support, expired-range and target-timeout descriptions were
misleading. [The exact correction](../../ghidra/README.md#weapon-provider-semantics-2026-09-12)
replaces those comments and semantic tags while retaining provenance tags.
The September 12 static review distinguishes these finite-input rules:

- Any in-progress weapon burst preserves the current selection. A null target
  also preserves it. Otherwise weapon `+140` and spawner reader `+144` clear,
  and scoring visits spawners before weapons in linked-list order.
- A weapon must be active and mask-compatible, with target height strictly
  between mode `+6c/+70`. Height is `min(terrain,water)-targetZ`.
  Distance uses raw three-dimensional positions, without aim offsets or radii.
- The weapon score starts at zero, or 2,000,000 for the shared `80000h` mask.
  Inclusive minimum/maximum range adds 1,000,000; an out-of-range candidate
  instead adds its positive distance outside the interval. It is not rejected
  solely for being out of range. Readiness adds another 1,000,000, with the
  separate float stores at `004fbc21` and `004fbc3a`. The raw constant at
  `005db290` is `49742400`. Only a strictly greater score replaces selection;
  ties preserve the first candidate.

The installed `data/default physics.dat` was freshly hashed: 175,603 bytes,
SHA-256 `e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`.
Its ordered field-7 records give Air Trainer the trainer launcher, and Target
Drone the Vulcan followed by the drone launcher; their use flags are `20400h`.
The existing all-slots hard-range check is not this selection algorithm.
The private `provider-selection-20260912.py` now executes the unchanged
selector and nine helper bodies at their retail addresses. Its 37 cases cover
those boundaries, including an inactive, mask-incompatible weapon whose burst
still locks selection. Terrain sampling and monitored-reader clearing are
explicit stubs; inputs use empty spawner lists, current modes and nonnull
nonballistic projectiles. Core's `RetailUnitWeaponSelection` carries this
bounded algorithm with existing PC24 arithmetic and strict readiness comparison.
For `(0.1f,0.1f,1.1f)`, native distance is `3f8df578`; a widened norm gives
`3f8df579`. The first three distance examples did not distinguish that wrong
implementation; the added original-code case does. Exact tests, negative
controls and limits are in [VALIDATION.md](../../../VALIDATION.md#bounded-unit-weapon-selector--september-12).
The selector is not yet called by the approximate actor firing loop. Actual
candidate state, preparation/fire/burst ownership and live combat remain open.

The next transaction must retain these static distinctions. Unit readiness
`004fc000` reads selected weapon `+140`, prepared flag `+1e8` and weapon
readiness. Fire `004fc080` marks its own success before calling `00506010`,
ignores that callee's returned EAX, invokes virtual `+15c`, then clears
`+1ec/+1e8`; refusal paths clear those two flags too. Phase completion
`004fa800` uses `due <= NOW` for phase 1 but `due < NOW` for phase 2.
Burst continuation `[00506930,005069f0)` checks event 5001, owner dying state,
mode lookup and the signed emitted count. It does not recheck AI state, active
state, attack intent, target liveness, selection or reload. After a shot it
increments the count and schedules another event with reuse zero, including
the terminal no-shot callback; that callback does not clear the emitted count.
Current countdown/intent cancellation is not this event ownership.

The unchanged-code `weapon-phases-20260912.py` experiment confirms the selected
current-mode Unit path across 26 synthetic cases and 32 calls. It executes seven
original bodies, including preparation, readiness, fire, phase completion and
the real post-fire callback with its empty-effect helper. Weapon Fire and the
waiting-animation callback are explicit stubs. It confirms strict readiness,
zero-delay preparation, the unequal phase-1/phase-2 deadlines, and clearing both
request/prepared flags on refused fire. A zero or negative Weapon Fire result
still leaves Unit Fire returning one; that result denotes an accepted attempt,
not a projectile. On canceled phase 1, `004fa8a1` invokes the post callback,
which can set phase 2 and a new deadline; `004fa8a7` then clears the phase again
while retaining that deadline. These bounded observations do not establish
effects, spawners, deployment, phase-3 pose restoration or gameplay acceptance.
[Validation](../../../VALIDATION.md#unit-weapon-preparation-and-fire-phases--september-12)
owns the command, outputs and review limits.

The later `plane-common-weapon-phases-20260912.py` composes unchanged common
update `004fef40`, slot-4 refresh `004ff4f0`, and the Unit preparation/readiness/
fire/phase bodies. **21 cases / 27 calls** pass, including complete four-word
retained/forwarded aim checks, ordered call traces, preserved registers/stack,
PC24/RN control word and unchanged receiver bytes outside declared state.
Independent review matched all ten routine bodies and constants in the ELF's
actual load mappings and reconciled the saved inputs/outputs.

Slot 4 refreshes the selected provider and computes B feasibility into `+1c`,
then A into `+18`. Common readiness runs afterward. A ready weapon with a
nonnull target still attempts fire when the refreshed `+18` is zero; this
flag gates preparation instead. The preparation arm selects a second time.
While Unit phase `+168==1`, it retains the previously captured `+34` aim:
changing the supplied target X through 99, 123, 456 and 789 leaves the captured
and forwarded vector `(99,22,33,44)`. Losing feasibility clears the request
before the separately invoked phase helper cancels preparation. These examples
refute re-aiming every callback and applying the preparation gate to ready fire.

This composition supplies synthetic target-aim capture and aim application,
provider selection, A/B feasibility, reader registration, acquisition, RNG,
Weapon Fire and waiting animation. Support/spawner membership is absent.
Positive delays and clear-after-fire are controlled branch variants. It does
not execute the Plane dispatcher/recurrence, Move scheduling, burst delivery,
geometry or projectile creation; selected production integration remains open.

The static follow-up also refutes two omissions in the old firing-loop comments.
Unit `004f8858..004f8880` supplies the weapon attachment with owner, selector 1
and the field-7 GunA/GunB tag; `0044a830..0044a848` stores those values.
An absent LaunchSequence does not remove that attachment origin. In the
nonballistic B path `00508fab..0050911b`, pitch bounds are inclusive. Round
`+48!=0` bypasses the line query; otherwise `005090ea` requires result 3, a
nonnull Unit hit and allegiance equal to the target's, not necessarily the
target itself. The same hash-pinned physics file has Forseti Missile Seek 3;
Blaster omits Seek and inheritance, with the default Round `+48` cleared at
`0043010e`. The selected missile therefore bypasses this query; the drone's
Vulcan/Blaster needs it. The model mount inputs below are recovered; live pose
evaluation and collision results remain required before replacing centre launch.
The [composition validation](../../../VALIDATION.md#common-controller-and-unit-weapon-composition--september-12)
records raw body identities and the private static receipt.

#### Selected aircraft weapon mounts and runtime pose inputs

The selected Steam mesh `data/resources/meshes/m_FA_F24_training.msh.aya` is
26,677 bytes, SHA-256 `48876552ae836750221241719f333fb9b5221f78f1ab8bc03d5950cdbf4e6ec5`.
The already-pinned physics input supplies ordered field-7 uses: Air Trainer
has Forseti Missile Trainer Launcher/GunB; Target Drone has Drone Vulcan
Cannon/GunA then Forseti Drone Missile Launcher/GunB. All carry raw flags
`00020400`. Unit initialization supplies emitter selector **1**, separately
from the tag index. Lookup `004aa820` compares names case-insensitively and
selectors exactly. The mesh's earlier GunA/2 is a distinct, valid binding.

| Binding | Part ordinal | CPOS meaningful XYZ words |
| --- | --- | --- |
| GunA/1 | 3 | `bd60ceb4 3f6a3a59 bd4d3bb0` |
| GunB/1 | 4 | `bb7ae95a 3f5b84b4 3d88c1bf` |

Both meaningful CORI bases are `3f800000 a818719e 00000000 / 2818719e
3f800000 00000000 / 00000000 00000000 3f800000`. Each selected gun and root
ancestor has one hierarchy pose and 64 zero frame-map entries. The selected
guns own both caches (`CMSP+118/+11c/+120 = 1/0/0`); meaningful cached words
equal the parser's model transforms. Padding is excluded. Part-local HPOS
differs from model-space CPOS, and the mesh's Trail parts are animated.

These ordered uses, selectors and twelve meaningful model words now flow
through the existing materializer and Client decoder into immutable
`Level100ActorMotionDefinition.WeaponMounts`, shared by authored and spawned
instances. Definition identity format 8 binds them, with formats 6/7 retained
when mounts are unavailable. This is input admission; the firing loop does
not yet consume live muzzle poses.

Read-only instruction review separates three runtime paths:

- Unit `004fc4e0` can use a profile-owned local pose keyed only by tag/selector,
  then compose it with current Unit position/basis. Eligibility includes
  `Unit+110==0`, nonnull profile and profile `+1a0==0`. Its cold miss requests
  skip-controller/force-refresh flags `(1,1)`. Unit event4003 recomputes `+110`
  using camera distance; it is not a permanent constructor property.
- Its fallback requests flags `(0,1)` through `004fc6e0`, renderer `004dd160`
  and evaluator `004b4de0`. A render-cache path can reuse the same integer-frame
  stamp despite force-refresh. It uses Actor render getters `00401be0/00401c50`,
  which interpolate old/current pose using global `008a9e44`.
- Without that render cache, `004b0fb0` has a separate direct-evaluator cache.
  Position accumulation/store order differs across these paths. Constant
  gun/root hierarchy data does not prove equal live results or justify replacing
  interpolation with a current-pose copy. Motion-controller and hierarchy
  evaluation beyond the selected null-controller case remain unexecuted here.

The unchanged MainLoop fragment `[0046ef40,0046efd5)` computes the model-time
fraction before calling game update. The private eight-case experiment executes
its 149 original bytes, SHA-256
`72fba6a65a6d45e0104ea275f634c1cbb5e3beca98aefd36f489a0bd33b3e356`.
At supplied base time 256 and frame-length word `3d4ccccd`, PC24/RN yields
`3f7ff000`, while PC53/RN yields `3f800000`. Both store the same frame-time
word `43800666`: native FST retains the arithmetic intermediate. This falsifies
a literal-one replacement for all supplied model-time/precision states, without
establishing the states encountered throughout retail MainLoop. No game update,
attachment query or renderer runs in this fraction experiment; see
[validation](../../../VALIDATION.md#aircraft-weapon-model-inputs-and-model-time-fraction--september-12).

The subsequent unchanged attachment composition passes **27 cases / 33 calls**
through the actual Unit/routing/lookup/getter/math bodies with synthetic
receivers and warm caches. It confirms current versus interpolated pose,
different accumulation order, and a direct-cache hit that retains an earlier
world pose within the same frame. Advancing the frame or selecting another
part invalidates that observed reuse. The exact receiver distinction is
`R=Unit+8`: animation is primary `Unit+6c`, not basis word `Unit+64`.
The [Unit attachment owner](Unit.cpp/CUnit__UpdateTransform.md#isolated-aircraft-attachment-composition)
records these controls and limits. These supplied comparisons are now executed;
native cache population, camera-latch lifecycle and production firing integration
remain open. No full combat, player acceptance or Ghidra mutation is implied.

For profile `+19c==0`, common-controller preparation writes the target virtual
`+168` result into controller `+34` at `004ff24b..004ff262`. The later ready
arm at `004ff19a` passes that retained vector to `004fb650`, then consumes its
direct random draw at `004ff1aa`. Re-aiming from the current quantized target
position on every burst shot changes this ownership. A successful selected
Round initializer calls Actor Init at `004d867b`; Actor Init draws at
`0040135d` before testing its movement flag. This adds a draw beyond the two
scatter calls at `00506e0a/00506e3e`, but does not prove an exhaustive total.
Before Actor's draw, renderer registration `005164b0` can call a resolved
renderer initializer at `0051654c`; the selected live registry remains an
open dependency. Do not substitute a guessed total or omit the resulting
Actor movement-event admission.

Particle and sound randomness use separate CRT state: `0055dbfe` updates
thread-data `+14` with `state * 0x343fd + 0x269ec3`, whereas shared gameplay
`004de8d0` updates its ECX receiver. Sprite initialization calls the CRT at
`004c0acb`; sound selection calls it at `004e196b` and conditionally at
`004e19c4` for pitch. These calls must not advance the gameplay stream.
Timeline initialization `[004c2620,004c263a)` only clears counters and stores
lifetime; its children belong to later updates. These are static call-path
findings, with effect/resource admission and actual renderer selection still
requiring observation.

Avoidance callback `004027c0` requires the actual ordered MapWho radius stream
and a monitored identity whose current Z is read during movement. Its only
candidate exclusions are null, self and ammunition type bit 4; dying or
inactive registered Things remain eligible. It minimizes float-stored
`((dz²+dx²)+dy²)-candidateRadius²-ownerRadius²` below strict `225f`, preserving
the first exact tie. `RetailMapWho` now carries the native rectangular iterator,
but Level100 does not yet supply its complete memberships/radii/reader lifetime.
The live mover therefore still has no avoidance input; an Active actor-ID scan
would not close that gap.

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
| `0x004fd140` | `CUnit__MarkDestroyedAndCleanupLinks` | If `TF_DYING` already set, return 0. Kill sound samples for the unit (`0x004e1130` on `0x00896988`), set bit2, optional `+0x164` count teardown, optional `+0x178` call `0x004443f0`, **then** `CallEventId5` if `+0x74`, then `+0x144` / `+0x18c` cleanup, return 1. Seven outbound direct `E8`s; nine inbound rel32 `E8`s. Slot 50 of three vtables (`0x005dd788` COLOC `0x00615728`, `0x005df998` COLOC `0x00617050`, `0x005e1490` COLOC `0x00617a30`). | live |

Independently re-read 2026-08-18 (cycle 10): **zero** `.text` `E8`/`E9`
land on the inner `CallEvent` site `0x00533685`. The three `E8`s land on
wrapper `0x00533660` (`push 5` at `0x0053367d`) at `0x0044cd98` /
`0x004fd1e8` / `0x004f444d`. Slot 14's nuller is
`mov dword [esi+0x74], 0` at `0x004f43f4` (`c7 46 74 00 00 00 00`).
A 32/30 slot-50 class census was reported by `t_f2e7ff28` and is
**not** adopted here.

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
