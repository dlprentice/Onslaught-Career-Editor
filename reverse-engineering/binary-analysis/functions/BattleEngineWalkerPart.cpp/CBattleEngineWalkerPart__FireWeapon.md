# CBattleEngineWalkerPart__FireWeapon

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
99 accepted through WalkerPart ChangeWeapon `addcaf8d` — not
redone. This wake already landed JetPart ChangeWeapon `4956cc53`
and GetCurrentWeapon `2e7141cb` — not redone. Envelope. Did not
mill FUN_*. Did not implement lock sets.

> Address: `0x00413cc0`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [ecx+0x20]`. One
bare `ret` at `0x00413ce7`. Body `0x00413cc0`–`0x00413ce7` is
40 bytes, SHA-256
`1b4b807fe9ffaba838c82cd888f74346601d10ac618ab72d2c5c86b249ed3902`.
Capstone: 11 insns, 1 `E8`, 1 `E9`, 2 unique rel32 targets.

Pinned body:

1. `eax = [ecx+0x20]` then store 0 at `[eax+0x588]`. Same
   `[+0x588]` slot ChangeWeapon already writes. **Not** named
   here. `[+0x20]` is the already-counted main-part slot.
2. `E8` already-pinned `CBattleEngineWalkerPart__GetCurrentWeapon`
   `0x00414030`. EAX==0 or `[eax+0x9c]==0` returns.
3. Else `ecx = eax` / `E9`
   `ProjectileBurst__SpawnFromPercentBucketFallback`
   `0x00506010`. That table name is counted, not contracted.

One inbound `.text` `E8`/`E9`: `JMP` at `0x00409f5a`. Zero
encodings of imm `c0 3c 41 00` in the image (not a vtable slot).

Source architecture (not proof):
`CBattleEngineWalkerPart::FireWeapon`
`BattleEngineWalkerPart.cpp:507+`. Retail bare `ret` matches
zero stack args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00013cc0` is not `8b 41 20`, **or**
`0x00013cc3` is not `c7 80 88 05 00 00 00 00 00 00`, **or**
`0x00013ccd` is not `e8 5e 03 00 00`, **or** `0x00013ce7` is
not `c3`, **or** body SHA-256 is not `1b4b807f…3902`, **or**
`tools/call_xref_scan.py` on `0x00413cc0` is not exactly one
`JMP` at `0x00409f5a`, **or** any encoding of imm `c0 3c 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `1b4b807f…3902`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x588]` / `[+0x9c]`. Did not walk ProjectileBurst.

Retail entity: walker-part FireWeapon. Stuart architecture (not
proof): `BattleEngineWalkerPart.cpp:507+`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__GetCurrentWeapon` /
`CBattleEngineWalkerPart__ChangeWeapon`. Next named:
`CBattleEngineJetPart__FireWeapon` `0x00411b90` if present;
else `CBattleEngine__ChargeWeapon` `0x00409ef0`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00413cc0` | `CBattleEngineWalkerPart__FireWeapon` | `8b4120 c7808805000000000000 e85e030000 … c3` (40 B) | incoming-ECX thiscall; bare ret ×1; 40 B; 1 E8 / 1 E9 / 2 targets; 1 inbound JMP. HIGH on ABI, `[+0x588]=0`, GetCurrentWeapon, tail-jmp. Mapping `PARTIAL_CONTRACT`. **Not** on ProjectileBurst or rebuild parity. |
