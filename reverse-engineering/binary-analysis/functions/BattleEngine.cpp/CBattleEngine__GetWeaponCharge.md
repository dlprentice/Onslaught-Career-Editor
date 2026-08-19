# CBattleEngine__GetWeaponCharge

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
100 accepted through ChargeWeapon `9bde6c3a` — not redone. This
wake already landed WalkerPart GetWeaponCharge `2224cd05` — not
redone. Envelope. Did not mill FUN_*. Did not implement lock sets.

> Address: `0x0040c4a0`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 0x10`. `esi = ecx`.
Three bare `ret` (`0x0040c51b`, `0x0040c534`, `0x0040c544`). Body
`0x0040c4a0`–`0x0040c544` is 165 bytes, SHA-256
`c595c24f9b36fb449bbbc9662efec37422215ecb08de9c68ac3dcf379d0762ae`.
Capstone: 50 insns, 4 `E8`, zero `E9`, 4 unique rel32 targets.
Raw `0xE8` byte count is 4 and matches the instruction count.

Pinned body, with `esi = ecx`:

1. `E8` table-named `stricmp` `0x00568390` against the image
   string `Racer` at `0x006234f4`. EAX==0 takes the height/water
   arm: `E8` `CStaticShadows__SampleShadowHeightBilinear`
   `0x0047eb80` counted, not contracted. `fmul` 0.2f at
   `0x005d8c68`. Clamp 1.0f at `0x005d8568`.
2. Else `[esi+0x260]==3` → `ecx = [esi+0x57c]` / `E8`
   table-named `CBattleEngineJetPart__GetWeaponCharge`
   `0x00412370` counted, not contracted.
3. Else `ecx = [esi+0x578]` / `E8` already-pinned
   `CBattleEngineWalkerPart__GetWeaponCharge` `0x00414520`.

Two inbound `.text` `E8`/`E9`: `CALL` at `0x00485b34` inside
`CHud__RoutePanel_T3_004858d0`; `CALL` at `0x00535762` inside
`IScript__GetWeaponCharge`. Zero encodings of imm `a0 c4 40 00`
in the image (not a vtable slot). Those parent names are
counted, not rewritten.

Source architecture (not proof): `CBattleEngine::GetWeaponCharge`
`BattleEngine.cpp:2795-2816`. The Racer `stricmp` and the
`[+0x260]==3` jet/walker split match that shape. Do **not**
equate the shadow-sample `E8` to source `MAP.Collide`.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000c4a0` is not `83 ec 10`, **or**
`0x0000c4a6` is not `68 f4 34 62 00`, **or** `0x0000c52b` is
not `e8 f0 7f 00 00`, **or** `0x0000c544` is not `c3`, **or**
body SHA-256 is not `c595c24f…62ae`, **or**
`tools/call_xref_scan.py` on `0x0040c4a0` is not exactly those
two `CALL`s, **or** any encoding of imm `a0 c4 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `c595c24f…62ae`. `call_xref_scan` still two CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not walk the
Racer height arm. Did not name `[+0x4b0]`.

Retail entity: BattleEngine GetWeaponCharge dispatcher (Racer
arm, then jet/walker part). Stuart architecture (not proof):
`BattleEngine.cpp:2795-2816`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetWeaponCharge` /
`CBattleEngine__CanSpawnBurstForResolvedEntry`. Next named:
`CBattleEngineJetPart__GetWeaponCharge` `0x00412370` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040c4a0` | `CBattleEngine__GetWeaponCharge` | `83ec10 8bf1 68f4346200 … e8f07f0000 … c3` (165 B) | incoming-ECX thiscall; bare ret ×3; 165 B; 4 E8 / 0 E9 / 4 targets; 2 inbound. HIGH on ABI, Racer stricmp, `[+0x260]==3` part dispatch, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on shadow-sample identity or rebuild parity. |
