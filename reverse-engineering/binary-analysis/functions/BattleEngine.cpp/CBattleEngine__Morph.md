# CBattleEngine__Morph

Status: active static function note
Last updated: 2026-08-28
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake landed `9a0035f5` Init and `934efc5c` Move — not redone. Cycle
93 accepted HandleLocks through HandleAutoAim — not redone.
Whole-function envelope plus one focused branch closure, not a complete
224-instruction walk. Did not mill FUN_*. Did not implement lock sets.
Historical alias
`CMonitor__UpdateFlightWalkerTransitionState.md` is not rewritten.

> Address: `0x0040a580`

## Contract

Incoming-ECX `thiscall`. First insn `push ecx`. Three bare `ret`
(`0x0040a6e2`, `0x0040a84a`, `0x0040a880`). Body
`0x0040a580`–`0x0040a880` is 769 bytes, SHA-256
`c68b3693adb38cf592353905c177abbaaa1bebaf000694282affaf60421e1093`
(PE bytes; not the C1-table Ghidra digest `7badfbd6…`). Capstone:
224 insns, 20 `E8`, zero `E9`, 14 unique rel32 targets. Neighbour
table `CBattleEngine__Damage` starts at `0x0040a890` after
alignment `nop`s and is not rewritten. Preceding table
`CBattleEngine__VFunc_101_0040a560` ends at `0x0040a57f` and is
not rewritten.

Pinned prologue, with `esi = ecx` and `edi = 0`:

1. If `[esi+0x58c] == 0` and `[esi+0x260] == 2`, jump to the
   last epilogue. Same WALKER=2 polarity Init already pins.
   `[esi+0x58c]` is **not** named here.
2. Store 0 at `[esi+0x588]`. If `[esi+0x260]` is 1 or 0, jump
   to the last epilogue (already-closed morphing-into-jet is 1;
   the 0 early-out is not named).
3. `ecx = [esi+0x57c]` / `E8`
   `CBattleEngineJetPart__GetIsDoingSpecialAirMove` `0x00411b70`.
   EAX==1 jumps to the last epilogue. Then `ecx = [esi+0x578]` /
   `E8` `CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove`
   `0x004135d0`. EAX==1 same early-out. Same part slots Init
   stores.
4. `E8` `0x00414010` (table
   `CMonitor__ClearCurrentTrackedEntryFlag60`) on the walker
   part, then `E8` `CBattleEngineJetPart__LoseWeaponCharge`
   `0x00412000` on the jet part. The walker-side table name is
   **not** adopted as `LoseWeaponCharge`.
5. Store `0x3f800000` (1.0f) at `[esi+0x2cc]`. `cmp eax, 3`
   (JET): that arm later writes `[esi+0x260] = 0` at
   `0x0040a672`. The other arm writes `[esi+0x260] = 1` at
   `0x0040a753`. Value 0 is **not** named here.
6. Counted, not contracted: `E8`
   `CGeneralVolume__BeginFlyToWalkTransition` `0x00424920` and
   `BeginWalkToFlyTransition` `0x00424990`; two `E8`
   `SharedUnitAnimation__PlayAnimationByNameIfPresent`
   `0x004f4560`; `E8`
   `CBattleEngine__SwapPrimarySecondaryPartReadersForState`
   `0x00406460`; two `E8` `CEventManager__AddEvent_AtTime`
   `0x0044b370`. Other of the 14 targets are counted, not
   contracted.

Five inbound `.text` `E8`/`E9`: `CALL` at `0x00408d70` inside
table `CBattleEngine__Move` (already pinned); `JMP` at
`0x0040dcd5` inside
`CBattleEngine__ClearFlag58CAndMorphIfState3`; two `CALL`s
inside `CBattleEngineJetPart__Move` (`0x00410df9`,
`0x00411228`); `CALL` at `0x004d32aa` inside
`CPlayer__ReceiveButtonAction`. Zero encodings of imm
`80 a5 40 00` in the image (not a vtable slot).

Source architecture outside the focused branch below is not proof:
`CBattleEngine::Morph` `BattleEngine.cpp:2038-2365`. Retail bare `ret`
matches zero stack args. Flight-disabled + walker early-out matches the
`+0x58c`/`+0x260==2` gate.

Rebuild mapping: `PARTIAL_CONTRACT` overall. The exact walker-to-jet
recent-ground branch is already carried by Core; the rest of this function is
not. See the sections below.

Cheapest falsifier: file `0x0000a580` is not `51`, **or**
`0x0000a582` is not `8b f1`, **or** `0x0000a58f` is not
`83 be 60 02 00 00 02`, **or** `0x0000a753` is not
`c7 86 60 02 00 00 01 00 00 00`, **or** `0x0000a880` is not
`c3`, **or** body SHA-256 is not `c68b3693…1093`, **or**
`tools/call_xref_scan.py` on `0x0040a580` is not exactly those
five sites, **or** a sixth `.text` `E8`/`E9` to this entry
exists, **or** any encoding of imm `80 a5 40 00` exists.

### Walker-to-jet recent-ground branch — exact 2026-08-28

The pristine subrange `[0x0040a771,0x0040a7c7)` is 86 bytes, raw
SHA-256
`85ad5341fb34f67e5c9d39e035a7a0a0652e350ba7b2e45b5a4fbdc8940103fe`.
It loads the global game time at `[0x00672fd0]`, subtracts
`[this+0xcc]` (`mLastTimeOnGround`), and uses an x87 strict `<`
comparison against `[0x005d8bb8]`. That constant is binary32
`0x3f19999a` / approximately `0.6f`; equality therefore takes the stale-ground
arm.

The recent-ground arm copies `[this+0x24]` (`mPos.Z`) to
`[this+0x2f0]` (`mTakeOffHeight`). The stale-ground arm instead writes
binary32 `0x47c34f80` / `99999.0f` there and schedules event `0x1770`
(`BECOME_JET`, decimal 6000) at game time plus the binary32 `0.1f` constant
at `[0x005d85c0]`, with start-of-frame ordering. Both arms join before
writing `[this+0x2f4]` (`mTakeOffTime`). This matches the retained source at
`BattleEngine.cpp:2099-2107`.

The nearby `[0x005d85ec] = 0.5f` and `[0x005d8cb4] = 0.3f` constants
belong to other predicates; neither controls this branch. Two independent
carrier-first reads reproduced the full-body and focused-range bytes, control
flow, fields, event ID, and all three constants without opening Ghidra. The
cheapest focused falsifier is a different 86-byte SHA-256, a non-strict
comparison, or either arm writing a different `+0x2f0` value.

## Rebuild mapping — 2026-08-28

Grade: `PARTIAL_CONTRACT`. Not wholly `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body SHA-256
still `c68b3693…1093`; the focused branch is closed above.
`call_xref_scan` still finds five sites. Did not open Ghidra, walk all 20
callees, or name `+0x260==0`.

Retail entity: walker/jet morph request from Move, JetPart
Move, and the player button path. Stuart architecture (not
proof): `BattleEngine.cpp:2038-2365`.

Nearest reconstruction owner: `Simulation.TryToggleMode`, through
`RecentGroundContactTicks` and `WalkerToJetAirborneTransitionTicks`. At Core's
20 Hz fixed step, 12 and 2 ticks carry the released strict 0.6-second gate and
0.1-second stale-ground delay exactly. Core's transition enum remains a
deliberate simulation abstraction, not a byte-for-byte model of every retail
field and event-manager operation.

Focused test: none added. The values and strict comparison were already in
Core; this closure repairs their provenance and removes a false open question
without changing behavior. The remaining Morph arms still require their own
contracts before further parity work.

Siblings: `CBattleEngine__Move` /
`CBattleEngine__HandleEvent` in this folder. Historical alias:
`../monitor.h/CMonitor__UpdateFlightWalkerTransitionState.md`.
Next named: `CBattleEngine__UpdateAutoAim` `0x0040b120` (Move
callee; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040a580` | `CBattleEngine__Morph` | `51 56 8bf1 … 83be6002000002 … c7866002000001000000 … c3` (769 B) | incoming-ECX thiscall; bare ret ×3; 769 B; 20 E8 / 0 E9 / 14 targets; 5 inbound Move+JMP+JetPart×2+Player. HIGH on ABI, `+0x260` 2/1/3/0 gates, `+0x578`/`+0x57c` part tests, and exact recent-ground/stale-ground walker-to-jet branch. Mapping `PARTIAL_CONTRACT`; focused timing owner is `Simulation.TryToggleMode`, but no complete Morph parity claim. **Not** on `+0x58c` name or `+0x260==0` name. |
