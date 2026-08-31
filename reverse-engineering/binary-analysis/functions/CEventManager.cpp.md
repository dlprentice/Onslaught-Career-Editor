# CEventManager / CScheduledEvent function map

Status: active function map — bounded AddEvent runtime insertion candidate added
Last updated: 2026-08-24 (timed insertion C2 candidate; canonical Generation 32 unchanged pending review)
Source File: `C:\dev\ONSLAUGHT2\EventManager.cpp` (SEH `__FILE__` pointer `0x005d250c` in `Init`; see the map below) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — every byte below was re-read from the pristine specimen at
file offset VA − 0x400000. The rebuild already owns one of these laws
(`CEventManager::AddEvent(CScheduledEvent*)` → `RetailEventScheduler.AddEvent`,
a REBUILD_READY row): the event number is a 16-bit word.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0044b060` | `CEventManager__Init` | `6aff 680c255d00 64a100000000 … 6a34 8bf1 683c8d6200 33ff 6a43 6a10 b9f03d9c00 … 897e08 897e10 897e14 …` | SEH prologue with `__FILE__`/`__LINE__`, allocates **0x34** bytes from pool `0x009c3df0`, and zeroes the three heads at `+0x08`, `+0x10`, `+0x14`. HIGH: a constructor/init that allocates the 52-byte manager and clears its three lists. |
| `0x0044b2a0` | `CEventManager__GetNextFreeEvent` | `56 8b7128 85f6 740a 8b4610 894128 8bc6 5ec3 68608d6200 6880f56600 e87f64ffff …` | Pops the free-list head at `+0x28`, advances it through `+0x10`, and returns the node; on empty it prints via two string references (`0x00628d60`, `0x0066f580`). HIGH: free-list pop with an error path. |
| `0x0044b2d0` | `CEventManager__AddEvent_TimeFromNow` | `8b442404 8b542418 d94108 d800 8b442414 … 50 e870000000 c21800` | Adds the argument float to the manager's current time (`fld [ecx+8]; fadd st0`), re-packs the tuple, and forwards to `AddEvent_AtTime` (+0x70). HIGH: a time-offset wrapper. |
| `0x0044b310` | `CEventManager__AddEvent_ScheduledEvent` | `568b742408 578bf9 85f6 7446 8b460c 53 d94708 d84610 8b16 8d5e0c 6a00 50 0fbf4604 d95c2418 … e82a000000 … c20400` | `ret 4`; arg = already-built `CScheduledEvent*`. `due = [this+8] + [event+0x10]`, then `AddEvent_AtTime` of that copy, then returns the supplied node to the free list. HIGH. This is how `Play*MessageWait` inserts its 2001 after CMessageBox event 3002. |
| `0x0044b370` | `CEventManager__AddEvent_AtTime` | `83ec08 535556 8bf1 57 8b4604 85c0 751c 68948d6200 6880f56600 e8b163ffff … 8b6c2420 85ed 0f8403020000` | `ret 0x18`; source-void absolute scheduler. Invalid manager logs and returns; null target returns; time >1,000,000 seconds returns; pool exhaustion logs and returns. Otherwise normalize negative time, select current ring / computed ring / sorted overflow, allocate or mark reuse, store the int16 event ID, append, and increment the live count. HIGH: exact failure and insertion law; no caller-visible status. |
| `0x0044b5c0` | `CEventManager__Update` | `83ec08 8b4114 56 40 bec8000000 894114 89442404 8b4110 c744240800000000 89411c 40 99 df6c2404 f7fe d80d78855d00 d95908 895110 e845000000 5e 83c408 c3` | `mov eax,[ecx+14h]; inc eax; mov [ecx+14h],eax` increments the frame counter; `mov [esp+4],eax` + `mov [esp+8],0` build the zero-extended 64-bit count that `fild qword [esp+4]` loads; **`fmul dword [0x005d8578]`** multiplies by the stored `0.05f` (`3d4ccccd` = `CLOCK_TICK`) and `fstp [ecx+8]` lands `mTime = frame × 0.05f`. Separately `mov eax,[ecx+10h]; mov [ecx+1ch],eax; inc eax; cdq; idiv esi(0xc8)` computes the ring rotation and `mov [ecx+10h],edx` lands `mCurrentBufferNum = (old + 1) % 200` with the quotient discarded. Then `call 0x0044b640` = `CEventManager__Flush`. HIGH: byte-exact; the rebuild's `RetailEventScheduler.AdvanceTime` carries the identical law. |
| `0x0044b600` | `CEventManager__AdvanceTime` | `83ec08 8b4114 56 40 bec8000000 894114 89442404 8b4110 c744240800000000 89411c 40 99 df6c2404 f7fe d80d78855d00 d95908 5e 895110 83c408 c3` | The same conversion body as `Update` through `fstp [ecx+8]` (`d95908`), then `mov [ecx+10h],edx` and return — **no trailing call**. HIGH: the advance half of the pair; the two functions share the conversion byte-for-byte and differ only in the Flush dispatch tail (`Update = AdvanceTime + Flush`). |
| `0x0044b640` | `CEventManager__Flush` | `83ec08 535556 8bf1 33ed 57 8b5e1c 8b460c 89442414 896e24 8d0c5b … c1e104 8d7c3138 8b47f8 3bc5 8907 …` | Drains the ready slot (`+0x1C`) in lane order, then the overflow list while `fcomp` at `0x0044b6d5` + `test ah,1 / je` at `0x0044b6d9` keeps `head.mTime < mTime` (strict — an event due exactly on the boundary waits a frame). At `0x0044b68a` / `0x0044b6f2` it passes the `CScheduledEvent*` to `mToCall->vtable[0]`; numeric interpretation belongs to that receiver. Then it frees non-rearmed events. HIGH. |
| `0x004de1f0` | `CScheduledEvent__Set` | `668b442404 56 8bf1 8b4c240c 66894604 8b442410 8b11 50 8bce 895610 e8ef2df2ff … 66c746080000 51 8d4e0c e8dc2df2ff` | Stores the event number as a **16-bit word** at `+0x04` (`mov [esi+4],ax`), copies a dword into `+0x10`, and zeroes the word at `+0x08` — the byte witness behind the already-landed REBUILD_READY `AddEvent` law. HIGH: direct corroboration of the rebuild's int16 event-number contract. |

## Open questions (cheapest falsifier first)

- `Update` vs `AdvanceTime`: CLOSED — `Update`'s trailing `call` at `0x0044b5f6`
  targets `0x0044b640` = `CEventManager__Flush`, so `Update` is the conversion
  plus a ring flush and `AdvanceTime` is the conversion alone.
- The constant at `0x005d8578`: CLOSED — it is the canonical single-precision
  `0.05f` (`3d4ccccd`, `CLOCK_TICK`; its neighbour `0x005d857c` is `20.0f`,
  `GAME_FR`), and the opcode is `fmul` (`d8 /1`), not a subtract: no epoch
  offset, `time = frame × 0.05f`. The rebuild's `RetailEventScheduler` already
  carries this law; the carry step is a focused parity test, not new code.
- The 200 divisor: the `idiv esi, 0xc8` dividend is `(old mCurrentBufferNum +
  1)` sign-extended by `cdq`, so `edx = (old + 1) % 200` reaches `+0x10` (the
  ring rotation) and the quotient is discarded; the previous slot is saved to
  `+0x1c` before the rotate. 200 is the ring modulus, not a time denominator.
- `AddEvent_AtTime` insertion axis: CLOSED — the overflow scan at `0x0044b459`
  (`fnstsw ax; test ah,0x41; je`) advances while the resident due time is
  **less than or equal to** the new one, so equal-time events keep insertion
  order. The ring arm is plain FIFO per lane.
- `Flush` overflow gate: CLOSED — `test ah,1 / je` at `0x0044b6d9` fires an
  overflow event only while its due time is **strictly less than** `mTime`.
- The 20,000-entry pool capacity (`MAX_NUM_EVENTS`) is sourced from
  `eventmanager.h:20`, not yet read out of the image — the exhaustion string
  `0x00628d60` is verified, its capacity is not.

## Bounded `AddEvent_AtTime` timed-insertion runtime proof

The retained Level-100 opening trace (6,199,181,312 bytes, SHA-256
`f3e677f7df5f5563ebb468f46ca6041756271f84dfc28ddf37b59210a4552b50`;
runtime image `e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`)
now supplies a complete target census and two selected gap-free queue envelopes.
The full replay found 12,973 call/entry pairs and 12,973 raw returns, of which
11,325 are validated gap-free returns. The terminal-padding control
`[0x0044b5b5,0x0044b5c0)` stayed `0/0/0`.

Both selected calls use manager `0x00672fc8`, event 3000, priority 0, null
data, and requested time bits `0xbf800000` (`-1.0f`). The function normalizes
that negative request against manager time `0x3d4ccccd` (`0.05f`) to stored due
time `0x3d4d35a9` (`0.0501000024f`) and chooses current ring buffer 1, priority
lane 0, whose `GenericSPtrSet` header is `0x00673028`.

| selected path | caller / fallthrough | entry / return | payload / reuse event | list before → after | insertion position |
| --- | --- | --- | --- | --- | --- |
| A | `CAnimation__VFunc_0_00404750` call `0x0040477a` / `0x0040477f` | `0x17A1B5:0x2477` / `0x17A1B5:0x24CB` | `to_call=0x08090160`, record `0x04094b4c` | first `0x03f160d0` unchanged; last `0x03f184f8→0x03f18510`; size `3→4` | new node `0x03f18510` contains record A |
| B | `CActor__HandleEvent` call `0x00401b41` / `0x00401b46` | `0x17A1B5:0x256E` / `0x17A1B5:0x25C2` | `to_call=0x08015c60`, record `0x04094b74` | exact A final is B initial; first unchanged; last `0x03f18510→0x03f18518`; size `4→5` | node A's next changes `0→0x03f18518`, so B follows A |

The live-count field at manager `+0x18` advances `1713→1714→1715` across
the two calls. Each final reused 20-byte event record carries its exact target,
low-word event 3000, reuse word 1, null data, and the common normalized due
time. The B record's initial 16-byte endpoint is a split/sequence-invalid TTD
query and is not consumed; its final record, standalone due-time word, queue
header, prior-node link, and every consumed queue endpoint are complete,
single-range, sequence-matched observations. Both call/entry/return envelopes
and all queue write pairs are gap-free.

A preregistered different-time control at `CUnitAI__VFunc_9_004fec60` call
`0x004fef33` requests bits `0x400338b3` (`2.0503356457f`) and reaches ring
buffer 40 / lane header `0x00673778`, rather than buffer 1. The narrow internal
replay observes ring-join buffers `[40, 1, 1]` and reused event records
`[0x04094b38, 0x04094b4c, 0x04094b74]`, with three exact entries, calls, and
returns and zero padding hits.

The deterministic verifier pins full call-context SHA-256
`21be79e8eb954c805960f73b5bc7856443c589b4bf1ffb56b83718ac280434a7`,
narrow internal-context `256797a203816a8e82dc418a818e9e286e0a877a638b8f42d1db0af5fe451e43`,
envelope A writes `8ed5cce0979476955b5ec72993fce1974ce9f8fffe2e07b2b15f252fc9af96f4`,
and envelope B writes `42139f887fd9722d9047366598d0003a50e6d54c376e39da6af9ee02c104fc40`.
Verifier SHA-256 is
`2fa0858488cb3c89bd95ff723709f1a1ad254bae9a237744e6a9260bd0d8e8f9`;
result SHA-256 is
`4f396d54169f191930b991cbabb5e3e7393ff17d783895c0882159373af7157b`.
Injected wrong-payload, wrong-time, wrong-manager-receiver, and wrong-list
controls all fail as required.

This is a bounded C2 candidate for the two observed reused-event, priority-0
ring insertions only. It does not establish allocation/free-list behavior,
null/invalid/exhaustion paths, priorities 1/2, nonnegative current-bucket
requests, wraparound, overflow insertion, concurrency, callback effects, or a
generic scheduler parity claim. Generation 32 and shared counts remain
unchanged until independent review and serialized integration.

## Cleanup-event queue / dispatch boundary

The manager does not assign global semantics to numeric IDs. It stores the
low 16 bits and later invokes the target's virtual slot 0. The now-closed
Unit-family chains demonstrate the boundary:

- [`CComponent__HandleTriggerEventAndMoveToOffset`](Component.cpp/CComponent__HandleTriggerEventAndMoveToOffset.md)
  queues `(4004, component, mTime+7.0f, priority 0, data null, reuse null)`.
  The 7.0-second delay uses ring offset 139 from the current insertion bucket
  and fires after 140 fixed 0.05-second advances. Component slot 0 is
  [`CUnit__HandleEvent`](Unit.cpp/CUnit__HandleEvent.md); its 4004 arm performs
  the profile-drop call and virtual slot-14 shutdown scheduling.
- [`CMech__VFunc_50_004a00a0`](Mech.cpp/CMech__VFunc_50_004a00a0.md)
  queues `(4004, mech, mTime+3.5f, priority 0, data null, reuse null)` only
  after its null-`[profile+0x130]` path reports a fresh ground-unit transition
  and releases child units. The 3.5-second delay uses ring offset 69 and fires
  after 70 fixed advances. CWarspite, CGillM, CThunderHead, and CMech all place
  `CUnit__HandleEvent` in slot 0 and `CComplexThing__AddShutdownEvent` in slot
  14, closing the same delayed profile-drop plus shutdown-finalization path.
- [`CUnit__ResetDeploymentGraphAndScheduleEvent`](Unit.cpp/CUnit__ResetDeploymentGraphAndScheduleEvent.md),
  called by the CComponent both-zero and CPod fresh arms, queues
  `(2000, unit, mTime+0.05f, priority 0, data null, reuse null)`. That near-time
  tuple enters the current insertion bucket and fires on the next update. The
  receiver chain identifies 2000 as `EThingEvent::SHUTDOWN`, then reaches the
  receiver's slot-2 cleanup.

These producers receive no success value. If insertion fails after their local
cleanup or child release (invalid manager or exhausted event pool), the manager
logs/returns and the caller does not roll back. Null target and over-limit time
are silent non-insertions. The tuple/effects belong to the named Unit-family
notes; ring, clock, allocation, order, and slot-0 delivery belong here.

## Callers and lifecycle (byte-cited)

Every direct caller below loads `mov ecx, 0x00672fc8` immediately before the
call, so `0x00672fc8` is the address of the global `CEventManager` instance
these shipped call sites share. A whole-image direct `E8`/`E9` rel32 scan
finds exactly one caller each for `Update` and `AdvanceTime`; indirect or
register-computed calls are outside that scan's reach.

| Caller | Call site | Target |
| --- | --- | --- |
| `CFrontEnd__Init` | `0x0046630b` | `Init` (`0x0044b060`) |
| `CGame__InitRestartLoop` | `0x0046c587` | `Init` (`0x0044b060`) |
| `CFrontEnd__Process` | `0x00466bfe` | `Update` (`0x0044b5c0`) — the combined AdvanceTime + Flush path, once per frontend frame |
| `CGame__Update` | `0x0046eb5d` | `AdvanceTime` (`0x0044b600`) — early in the frame |
| `CGame__Update` | `0x0046ebce` | `Flush` (`0x0044b640`) — late in the frame, after the `[esi+0x29c]` object-update loop (which ends `cmp ebp,eax; jl` at `0x0046ebaa` and makes virtual calls through `call [eax+8]` at `0x0046eb9a`) |
| `IScript__PlayCharMessageWait` | `0x00537703` | `GetNextFreeEvent` (`0x0044b2a0`) |
| `IScript__PlayPCharMessageWait` | `0x005379ff` | `GetNextFreeEvent` (`0x0044b2a0`) |

So the frontend drives the scheduler with the combined `Update`, while
`CGame__Update` drives it with the split pair and runs gameplay between the
clock advance and the dispatch.

### `AddEvent_TimeFromNow` consumers (24 direct call sites, whole-image scan)

| Owner (name-table range) | Call sites | What it schedules |
| --- | --- | --- |
| `CGame__InitRestartLoop` | `0x0046c5f0` | restart sequencing |
| `CGame__DeclareLevelLost` | `0x0046f50e` | level-lost follow-up |
| `CGame__DeclarePlayerDead` | `0x0046f6e3` `0x0046f71a` `0x0046f75b` `0x0046f792` | death follow-up (four distinct delays) |
| `CGame__HandleEvent` | `0x00470018` | event-driven reschedule |
| `CGame__RespawnPlayer` | `0x00470330` `0x00470416` | respawn timing |
| `CMessageBox__TryAdvanceQueuedMessage` | `0x004b7c90` | reveal pacing |
| `CMessageBox__StartVoiceOrFallbackTextReveal` | `0x004b7eec` | reveal pacing |
| `CMessageBox__AdvanceRevealAndScheduleNextTick` | `0x004b8096` `0x004b80c4` `0x004b8141` `0x004b8184` `0x004b81b9` | the self-reschedule: five arms re-post the next reveal tick at a time-from-now offset |
| `CMessageBox__VFunc_0_004b81d0` | `0x004b8263` | reveal pacing |
| `CCSPersistentThing__Init` | `0x004269e3` | persistent-thing polling |
| `CFenrir__VFunc_50_0044e1c0` | `0x0044e1e9` | Fenrir virtual arm |
| `CPlayer__GotoPanView` | `0x004d2fbe` | pan-view transition |
| `CTree__CreateFallingTree` | `0x004f6a74` | tree fall start |
| `CTree__UpdateFallingTree` | `0x004f6fa6` | tree fall continuation |
| `CUnit__HandleEvent` | `0x004f9964` | unit event follow-up |
| `IScript__SetTimer` | `0x00535908` | mission-script timers — script delays run on the manager clock |

`AddEvent` has 128 direct call sites (not listed); re-run
`python ./tools/call_xref_scan.py <pristine> 0x0044b2d0 0x0044b370` to reproduce
either census, and the owning-function attribution comes from
`ghidra-function-name-table-2026-08-17.tsv` body ranges.
