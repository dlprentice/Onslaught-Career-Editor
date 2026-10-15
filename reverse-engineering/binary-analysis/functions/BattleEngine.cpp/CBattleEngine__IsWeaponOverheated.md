# CBattleEngine__IsWeaponOverheated

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
102 accepted through JetPart GetWeaponAmmoPercentage `109373ed` —
not redone. This wake already landed Walker IsWeaponOverheated
`33080a9c` — not redone. Envelope. Did not mill FUN_*. Did not
invent field names. Did not rename the jet JMP target. Did not
invent a Core owner.

> Address: `0x0040c3a0`

## Contract

Incoming-ECX `thiscall`. First insn `cmp dword [ecx+0x260], 3`.
Zero `ret`. Body `0x0040c3a0`–`0x0040c3be` is 31 bytes, SHA-256
`6b0541de3c37cb09850c55d1ed0fe55f9ef83c2414f6fd99dcff9128a084b96a`.
Capstone: 6 insns, zero `E8`, 2 `E9`, 2 unique rel32 targets.

Pinned body:

1. `[ecx+0x260]==3` → `ecx = [ecx+0x57c]` / `E9`
   table-named `CBattleEngineJetPart__IsWeaponOverheated`
   `0x00412310`. That table name is counted, not rewritten.
2. Else `ecx = [ecx+0x578]` / `E9` already-pinned
   `CBattleEngineWalkerPart__IsWeaponOverheated` `0x004144f0`.

One inbound `.text` `E8`/`E9`: `CALL` at `0x00486af5` inside
`CHud__RoutePanel_T5_00486940`. Zero encodings of imm
`a0 c3 40 00` in the image (not a vtable slot). The inbound
parent is counted, not rewritten.

Source architecture (not proof):
`CBattleEngine::IsWeaponOverheated`
`BattleEngine.cpp:2749-2755`. The `[+0x260]==3` jet/walker split
matches that shape. Do **not** treat the jet JMP target as a
2026-08-19 PE envelope.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000c3a0` is not
`83 b9 60 02 00 00 03`, **or** `0x0000c3af` is not
`e9 3c 81 00 00`, **or** `0x0000c3ba` is not
`e9 51 5f 00 00`, **or** body SHA-256 is not `6b0541de…b96a`,
**or** `tools/call_xref_scan.py` on `0x0040c3a0` is not exactly
one `CALL` at `0x00486af5`, **or** any encoding of imm
`a0 c3 40 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `6b0541de…b96a`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not rename
`0x00412310`. Did not invent a Core owner.

Retail entity: BattleEngine overheat dispatcher. Stuart
architecture (not proof): `BattleEngine.cpp:2749-2755`.

Nearest reconstruction owner: **none**. Existing
`RetailWeaponStores` readout is not rewritten and is not raised
to `REBUILD_READY` from this envelope. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__IsWeaponOverheated` /
`CBattleEngine__GetWeaponAmmoCount`. Next named:
`CBattleEngineJetPart__IsWeaponOverheated` `0x00412310` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040c3a0` | `CBattleEngine__IsWeaponOverheated` | `83b96002000003 … e93c810000 … e9515f0000` (31 B) | incoming-ECX thiscall; 0 ret; 31 B; 0 E8 / 2 E9 / 2 targets; 1 inbound CALL. HIGH on ABI, `[+0x260]==3` tail-jmp dispatch, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on jet-target rewrite or rebuild parity. |
