# CBattleEngineJetPart__ChangeWeapon

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
98 accepted Hit and Gravity — not redone. This wake landed
WalkerPart ChangeWeapon `addcaf8d` and AutoZoomOut `f75aa0b4` —
not redone. Envelope, not a 150-instruction walk. Did not mill
FUN_*. Did not implement lock sets.

> Address: `0x00411e70`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 8`. `esi = ecx`.
Two bare `ret` (`0x00411f61`, `0x00411ff0`). Body
`0x00411e70`–`0x00411ff0` is 385 bytes, SHA-256
`239dd00d1b7fe0c85caa0b5c3b8572593d8a4e702d3acff290bab2becb923962`.
Capstone: 150 insns, 5 `E8`, zero `E9`, 3 unique rel32 targets.
Neighbour after this body is not rewritten.

Pinned prologue, with `esi = ecx`:

1. `E8` `CSPtrSet__First` `0x00406d20`. EAX==0 jumps past the
   walk.
2. Compare walk index to `[esi+0x10]`. That slot is **not**
   named here.
3. Counted, not contracted: two more `E8` First; one `E8`
   `CSPtrSet__Next` `0x00406d30`. Tail `E8` already-pinned
   `CBattleEngine__AutoZoomOut` `0x00409e80` at `0x00411fe5`.

Two inbound `.text` `E8`/`E9`: `CALL` at `0x00409fd3` inside
already-pinned `CBattleEngine__ChangeWeapon`; `CALL` at
`0x004128cd`. Zero encodings of imm `70 1e 41 00` in the image
(not a vtable slot).

Source architecture (not proof): jet-part ChangeWeapon sibling
of walker `BattleEngineWalkerPart.cpp:562-599`. Retail bare
`ret` matches zero stack args. AutoZoomOut tail matches the
walker sibling.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00011e70` is not `83 ec 08`, **or**
`0x00011e76` is not `8b f1`, **or** `0x00011e7a` is not
`e8 a1 4e ff ff`, **or** `0x00011fe5` is not
`e8 96 7e ff ff`, **or** `0x00011ff0` is not `c3`, **or** body
SHA-256 is not `239dd00d…3962`, **or**
`tools/call_xref_scan.py` on `0x00411e70` is not exactly those
two `CALL`s, **or** a third `.text` `E8`/`E9` to this entry
exists, **or** any encoding of imm `70 1e 41 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `239dd00d…3962`. `call_xref_scan` still two
sites. Did not open Ghidra. Did not edit `rebuild/**`. Did not
name `[+0x10]`.

Retail entity: jet-part ChangeWeapon from the already-pinned
BattleEngine ChangeWeapon dispatcher. No new Core owner.

Nearest reconstruction owner: **none** added. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__ChangeWeapon` /
`CBattleEngine__ChangeWeapon` / `CBattleEngine__AutoZoomOut`.
Next named: `CBattleEngineWalkerPart__GetCurrentWeapon`
`0x00414030` (already counted; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00411e70` | `CBattleEngineJetPart__ChangeWeapon` | `83ec08 8bf1 e8a14effff … e8967effff … c3` (385 B) | incoming-ECX thiscall; bare ret ×2; 385 B; 5 E8 / 0 E9 / 3 targets; 2 inbound. HIGH on ABI, First/Next walk, AutoZoomOut tail. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x10]` name or rebuild parity. |
