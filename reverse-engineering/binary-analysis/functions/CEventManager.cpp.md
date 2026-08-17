# CEventManager / CScheduledEvent function map

Status: active static function map
Last updated: 2026-08-17
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
| `0x0044b370` | `CEventManager__AddEvent_AtTime` | `83ec08 535556 8bf1 57 8b4604 85c0 751c 68948d6200 6880f56600 e8b163ffff … 8b6c2420 85ed 0f8403020000` | Validates the head pointer (`+0x04`), asserts on null, then enters a ~0x200-byte insertion scan by time. MEDIUM-HIGH: ordered-ring insertion by timestamp; the exact comparison axis needs one more witness. |
| `0x0044b5c0` | `CEventManager__Update` | `83ec08 8b4114 56 40 bec8000000 894114 89442404 8b4110 c744240800000000 89411c 40 99 df6c2404 f7fe d80d78855d00 d95908 895110 e845000000 5e 83c408 c3` | `mov eax,[ecx+14h]; inc eax; mov [ecx+14h],eax` increments the frame counter; `mov [esp+4],eax` + `mov [esp+8],0` build the zero-extended 64-bit count that `fild qword [esp+4]` loads; **`fmul dword [0x005d8578]`** multiplies by the stored `0.05f` (`3d4ccccd` = `CLOCK_TICK`) and `fstp [ecx+8]` lands `mTime = frame × 0.05f`. Separately `mov eax,[ecx+10h]; mov [ecx+1ch],eax; inc eax; cdq; idiv esi(0xc8)` computes the ring rotation and `mov [ecx+10h],edx` lands `mCurrentBufferNum = (old + 1) % 200` with the quotient discarded. Then `call 0x0044b640` = `CEventManager__Flush`. HIGH: byte-exact; the rebuild's `RetailEventScheduler.AdvanceTime` carries the identical law. |
| `0x0044b600` | `CEventManager__AdvanceTime` | `83ec08 8b4114 56 40 bec8000000 894114 89442404 8b4110 c744240800000000 89411c 40 99 df6c2404 f7fe d80d78855d00 d95908 5e 895110 83c408 c3` | The same conversion body as `Update` through `fstp [ecx+8]` (`d95908`), then `mov [ecx+10h],edx` and return — **no trailing call**. HIGH: the advance half of the pair; the two functions share the conversion byte-for-byte and differ only in the Flush dispatch tail (`Update = AdvanceTime + Flush`). |
| `0x0044b640` | `CEventManager__Flush` | `83ec08 535556 8bf1 33ed 57 8b5e1c 8b460c 89442414 896e24 8d0c5b … c1e104 8d7c3138 8b47f8 3bc5 8907 …` | Drains the ready slot (`+0x1C`) in lane order, then the overflow list while `fcomp` at `0x0044b6d5` + `test ah,1 / je` at `0x0044b6d9` keeps `head.mTime < mTime` (strict — an event due exactly on the boundary waits a frame), then frees non-rearmed events. HIGH: byte-verified against the rebuild's `RetailEventScheduler.Flush`. |
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
`py -3 tools\call_xref_scan.py <pristine> 0x0044b2d0 0x0044b370` to reproduce
either census, and the owning-function attribution comes from
`ghidra-function-name-table-2026-08-17.tsv` body ranges.
