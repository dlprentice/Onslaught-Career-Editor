# CEventManager / CScheduledEvent function map

Status: active static, isolated-code and historical runtime contracts
Last updated: 2026-09-19 (readiness queue, precision boundary and allocation corrections)
Summary: event insertion, monitored ownership, dispatch timing and failure limits;
isolated original-code results remain separate from retained runtime extracts.
Source File: `C:\dev\ONSLAUGHT2\eventmanager.cpp` (allocator source pointer `0x00628d3c`; `0x005d250c` is the SEH handler) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: static addresses refer to that pristine specimen. September 19
independently binds the selected complete bodies and executable controls in
[validation](../../../VALIDATION.md#projectile-readiness-queue-and-speed-dependencies--september-19).
The rebuild already owns one of these laws
(`CEventManager::AddEvent(CScheduledEvent*)` → `RetailEventScheduler.AddEvent`,
a REBUILD_READY row): the event number is a 16-bit word.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0044b060` | `CEventManager__Init` | `0044b079..0044b0a5` passes `(size=0x10, type=0x43, file=0x00628d3c, line=0x34)` to `005490e0`; `0044b0fb..0044b130` allocates `0x61a84`, stores cookie `0x4e20`, and constructs records with stride `0x14`. | Initializes the existing manager, allocates its **16-byte overflow array object** at `+0x25b0`, and constructs **20,000 event records**. `+8/+10/+14` are time/current bucket/frame, not list heads. The former “52-byte manager allocation” confused source line 52 with size. |
| `0x0044b2a0` | `CEventManager__GetNextFreeEvent` | `56 8b7128 85f6 740a 8b4610 894128 8bc6 5ec3 68608d6200 6880f56600 e87f64ffff …` | Pops the free-list head at `+0x28`, advances it through `+0x10`, and returns the node; on empty it prints via two string references (`0x00628d60`, `0x0066f580`). HIGH: free-list pop with an error path. |
| `0x0044b2d0` | `CEventManager__AddEvent_TimeFromNow` | `8b442404 8b542418 d94108 d800 8b442414 … 50 e870000000 c21800` | Adds the argument float to the manager's current time (`fld [ecx+8]; fadd st0`), re-packs the tuple, and forwards to `AddEvent_AtTime` (+0x70). HIGH: a time-offset wrapper. |
| `0x0044b310` | `CEventManager__AddEvent_ScheduledEvent` | `568b742408 578bf9 85f6 7446 8b460c 53 d94708 d84610 8b16 8d5e0c 6a00 50 0fbf4604 d95c2418 … e82a000000 … c20400` | `ret 4`; arg = already-built `CScheduledEvent*`. `due = [this+8] + [event+0x10]`, then `AddEvent_AtTime` of that copy, then returns the supplied node to the free list. HIGH. This is how `Play*MessageWait` inserts its 2001 after CMessageBox event 3002. |
| `0x0044b370` | `CEventManager__AddEvent_AtTime` | `83ec08 535556 8bf1 57 8b4604 85c0 751c 68948d6200 6880f56600 e8b163ffff … 8b6c2420 85ed 0f8403020000` | `ret 0x18`; source-void absolute scheduler. Invalid manager logs and returns; null target returns; over-limit future time returns; empty event pool logs and returns. Otherwise normalize negative time, select current ring / computed ring / sorted overflow, initialize or mark reuse, request publication, and increment the count. Overflow helper failure can leave that increment without an insertion; see the capacity control below. No caller-visible status. |
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
  carries this law. On September 8, Simulation's weapon clock was connected to
  that shared calculation instead of dividing its absolute replay tick by 20.
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
- The 20,000-entry pool capacity: CLOSED statically on September 19 —
  `0x61a84 = 20,000 × 0x14 + 4`; the array cookie and construction count are
  both `0x4e20`. The final free-list link is cleared at pool `+0x61a7c`.
- The literal array-constructor callback `[0044b190,0044b1d0)` clears only
  event target `+0` and payload `+0c`, increments `0083cde8`, and returns.
  The current function export has no entry or containing body for that range.
  A fresh read-only Ghidra code-unit/function/reference inspection is still
  needed before declaring a database boundary defect or creating a function.

## Projectile readiness queue — September 19

The [selected collision Init](collisionseekingthing.cpp.md#selected-round-initialization--2026-09-19)
clears readiness `0x400` and submits component event 3000 with relative delay
`-1.0f`. A separate **23-case original-code composition** executes the actual
relative/absolute insertion, event initialization, monitored-reader/list
operations, clock advance, flush and readiness-handler bodies. Its manager,
component and resident pools are authored inputs; allocation and diagnostics
have constrained replacements. This is not a full collision Init or retail run.

For a manager already advanced to frame 1, insertion uses current bucket 1
while the ready-to-flush bucket is still 0. Insertion and a flush of bucket 0
leave the component unready. The next advance selects bucket 1 for delivery;
its flush invokes component slot 0 and native event 3000 sets `0x400`. ID
`0x12340bb8` has the same effect because the handler reads the low word; 2999
is delivered but leaves the flag unchanged. Priority-2, bucket-wrap and
already-ready controls distinguish those paths.

Relative `-1` is first added to the stored manager clock. At clocks 1.0 and
2.0 the resulting due values are respectively 0 and 1, not `clock+0.0001`.
They still enter the current insertion bucket and await its flush. Negative
absolute requests use the epsilon normalization. A computed future-bucket
control waits two advances. Overflow due exactly at 10.0 remains pending;
the tested sequence delivers it at frame 201, when clock time is strictly
greater. None of these insertions delivers a target inline.

### Floating-point admission boundary

The quick-path comparison at `0044b3ac..0044b3c2` adds stored `0.051f` to the
clock **without an intervening float store**. The selected x87 precision can
therefore change which bucket receives an event:

| Clock / request words | Controlled x87 word | Insertion and observed delivery |
| --- | --- | --- |
| frame 9 clock `3ee66667`, request `3f00418a` | `037f`, PC64/RN | computed offset 1; delivery after two advances |
| same exact inputs | `007f`, PC24/RN | current bucket; delivery after one advance |
| request one float step lower, `3f004189` | `037f` | current bucket; one advance |
| request one float step higher, `3f00418b` | `007f` | computed offset 1; two advances |

The finite future-time path also executes the unchanged CRT floor/control-word
helpers. Both tested entry control words are restored. These are controlled
precision cases, **not a measurement of the live scheduler's control word**.
The earlier Plane observation of `007f` belongs to its named calls/backend;
it does not automatically establish scheduler precision. A reconstruction
must preserve the chosen retail context and expression/store boundaries,
rather than assume wider intermediates always give equivalent event timing.

### Ownership and failure boundaries

Fresh insertion obtains a preconstructed event from manager `+28`; due time
reuses that record's free-list word `+10`. `004de1f0` registers the **address
of the target reader cell**, `&event[0]`, with the target monitor, and does the
same for a non-null payload through `&event[0c]`. Thus insertion changes target
monitor bookkeeping as well as scheduler state. With null data, ring insertion
consumes one event record and two shared list nodes: a monitor head node and
a bucket tail node. Later flush removes the reader and recycles both nodes.
Do not zero unspecified event padding or treat a reader-cell address as its
target pointer.

Invalid-manager, null-target, empty-event-pool and over-limit controls perform
no insertion or readiness callback. Missing monitor-list storage takes a
16-byte allocation; missing shared list nodes takes an 8-byte fallback.
These are different capacities from the 20,000-event pool. The experiment
allows only the monitor-list allocation and guards other allocator branches.
Static allocator inspection separately resolves the resident tiny-block path:
`005490e0 → 004a1810` rounds 8/16-byte requests to 16 and pops the selected
heap's `+8c4` list, surrounded by imported `WaitForSingleObject` / `ReleaseMutex`.
That path has no game virtual callback or RNG call; it does mutate heap state,
does not zero the payload and was not executed by this witness. Allocator
failure, logging, contention and exceptions remain outside that closure.
List-node fallback can log every twentieth allocation even if allocation
succeeds, so ordinary allocator success does not close that diagnostic path.

A deliberately full, growth-disabled overflow array exposes a distinct
failure: `00424260` returns without publishing the pointer, but AddEvent
still increments manager `+18`. The executed control consumes the event,
keeps its target reader registered and reports one live event with an empty
overflow array; no callback occurs over 200 advances. This is a bounded
failure contract, not the normal initialized capacity or a suggested repair.
The caller receives no status and performs no rollback.

The [validation receipt](../../../VALIDATION.md#projectile-readiness-queue-and-speed-dependencies--september-19)
binds all 18 executable bodies, constants, raw inputs/outputs and independent
review. Competing insertions, reuse/rearming, non-null payload delivery,
collision-event semantics, live FPU/heap state and full-shot RNG remain open.

## Bounded `AddEvent_AtTime` timed-insertion runtime proof

Retained extracts from the former Level-100 opening recording (6,199,181,312 bytes, SHA-256
`f3e677f7df5f5563ebb468f46ca6041756271f84dfc28ddf37b59210a4552b50`;
runtime image `e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`)
report a target census and two selected gap-free queue envelopes.
The recording itself was permanently deleted; these extracts cannot be
replayed or queried anew. The historical full replay found 12,973 call/entry pairs and 12,973 raw returns, of which
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
| `CGame__Update` | `0x0046ebce` | `Flush` (`0x0044b640`) — after the `[esi+0x29c]` controller Flush loop (virtual `call [eax+8]` starts at `0x0046eb98`; source `game.cpp:1909–1933`) |
| `IScript__PlayCharMessageWait` | `0x00537703` | `GetNextFreeEvent` (`0x0044b2a0`) |
| `IScript__PlayPCharMessageWait` | `0x005379ff` | `GetNextFreeEvent` (`0x0044b2a0`) |

So the frontend drives the scheduler with the combined `Update`, while
`CGame__Update` drives it with the split pair and runs gameplay between the
clock advance and the dispatch.

The September 8 weapon-clock correction uses the manager's own unsigned frame
count, reset by `InitRestartLoop`, and the stored result of
`frameCount * 0.05f`. `AdvanceTime` zero-extends the counter before `fild` at
`0x0044b624`, multiplies the stored float at `0x0044b62a`, then stores time at
`0x0044b630`. Its complete 59-byte body SHA-256 is
`792dab29b0913762b0e507a7e3bd8110cb30b3ec1a4138b9ece1ddd86196f6c8`,
measured from the pristine specimen named above. At frame 9, the result is
`0x3ee66667`; division by 20 incorrectly gives `0x3ee66666`. The update that
delivers gameplay pause advances this counter; following paused updates freeze
it. Focused `SimulationTests.RetailEventClock_*` and canonical-hash checks cover
those boundaries and reset independently of replay time.

The subsequent direct-controller correction moves Morph, Charge, Fire,
ChangeWeapon, ZoomIn and ZoomOut ahead of actor/mission events, in that order.
The shipped row initializer `[0x005142c4,0x00514350)` has SHA-256
`c0abfe7983230cddf9804aee2043992a15fff5b25f5aa45df1002e9be3da3ca9`;
the game-loop prefix `[0x0046eb37,0x0046ebd3)` has SHA-256
`e4bcf364ef8b1f4e4b987edc38000ed9819fbc1927088d0237d8c8da7244a539`.
The pinned `Controller.cpp:148-164,443-487` and `Player.cpp:319-398` establish
synchronous button dispatch. A later unlock, disable or morph-completion event
cannot retroactively change the earlier button's eligibility. Shots consume
the retained emitter before movement. `SimulationTests.Controller*` exercises
those causal boundaries; the disable case uses an isolated authored callback,
not a player-acceptance route. The test driver's old post-Move aim prediction
was removed to match the corrected launch phase.

Full axis/controller dispatch, actor/event priority, nominal terminal-event
timing and the natural pan boundary's later movement projection remain open.
This is not complete scheduler or player-experience parity.

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
| `CCSPersistentThing__Init` | `0x004269e3` | component readiness event 3000 |
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
