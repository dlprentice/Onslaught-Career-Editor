# CBattleEngineWalkerPart__IsWeaponOverheated

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
102 accepted through JetPart GetWeaponAmmoPercentage `109373ed` —
not redone. This tree already has `0c6bc5a1`/`b74fe451`/`12576541`
Walker/parent GetWeaponAmmoCount and Walker IsEnergyWeapon — not
independently re-read this cycle. Envelope. Did not mill FUN_*. Did
not invent field names. Did not invent a Core owner.

> Address: `0x004144f0`

## Contract

Incoming-ECX `thiscall`. First insn `push esi`. `esi = ecx`.
Two bare `ret` (`0x00414510`, `0x00414514`). Body
`0x004144f0`–`0x00414514` is 37 bytes, SHA-256
`607c914174e282b17efe575aa1382a088d4aa33c3cead35d7d07befb40638e86`.
Capstone: 14 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.

Pinned body, with `esi = ecx`:

1. `E8` already-pinned
   `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`.
   EAX==0 returns EAX=0.
2. Else `[eax+0xa4]` / already-counted `[esi+0x20]` then EAX =
   `[edx+ecx*4+0x544]`. That slot is **not** named here.

One inbound `.text` `E8`/`E9`: `JMP` at `0x0040c3af` inside
already-named `CBattleEngine__IsWeaponOverheated` `0x0040c3a0`. Zero
encodings of imm `f0 44 41 00` in the image (not a vtable slot).
The parent table name is counted, not rewritten.

Source architecture (not proof):
`CBattleEngineWalkerPart::IsWeaponOverheated`
`BattleEngineWalkerPart.cpp:870-876`. Bare `ret` matches zero
stack args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000144f0` is not `56`, **or**
`0x000144f1` is not `8b f1`, **or** `0x000144f3` is not
`e8 38 fb ff ff`, **or** `0x00014514` is not `c3`, **or** body
SHA-256 is not `607c9141…8e86`, **or**
`tools/call_xref_scan.py` on `0x004144f0` is not exactly one
`JMP` at `0x0040c3af`, **or** any encoding of imm `f0 44 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `607c9141…8e86`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x544]`. Did not invent a Core owner.

Retail entity: walker-part IsWeaponOverheated query. Stuart
architecture (not proof): `BattleEngineWalkerPart.cpp:870-876`.

Nearest reconstruction owner: **none added**. Existing
`RetailWeaponStores` readout is not rewritten and is not raised
to `REBUILD_READY` from this envelope. L100 card `t_aa5586e5` is
on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__IsEnergyWeapon` /
`CBattleEngineWalkerPart__GetCurrentWeapon`. Next named:
`CBattleEngine__IsWeaponOverheated` `0x0040c3a0` (no 2026-08-19
PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004144f0` | `CBattleEngineWalkerPart__IsWeaponOverheated` | `56 8bf1 e838fbffff … c3` (37 B) | incoming-ECX thiscall; bare ret ×2; 37 B; 1 E8 / 0 E9 / 1 target; 1 inbound JMP. HIGH on ABI, GetCurrentWeapon, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x544]` name or rebuild parity. |
