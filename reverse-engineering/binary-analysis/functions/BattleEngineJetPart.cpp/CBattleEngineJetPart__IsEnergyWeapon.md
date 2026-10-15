# CBattleEngineJetPart__IsEnergyWeapon

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
103 follow-up accepted overheat parent/jet `4013d039` /
`63c63909` — not redone. This wake already landed energy
dispatcher `b5df91bf` — not independently accepted this
follow-up. Envelope. Did not mill FUN_*. Did not invent field
names. Did not invent a Core owner.

> Address: `0x004122b0`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [ecx]`. Live `ecx`
is this. Two bare `ret` (`0x004122e8`, `0x00412301`). Body
`0x004122b0`–`0x00412301` is 82 bytes, SHA-256
`f48d4e1d6ca82de213a6c3dd689734c76efaf4e487afc8e48780e189c17e3f10`.
Capstone: 36 insns, zero `E8`, zero `E9`.

Pinned body:

1. Counted list walk on `[ecx]` / `[ecx+8]` until the index
   matches `[ecx+0x10]`. Same shape JetPart IsWeaponOverheated
   already counts. Empty / miss returns EAX=0.
2. Else `[eax+0xa4]` / `[ecx+0x18]` then EAX =
   `[ecx+eax*4+0x55c]`. Those slots are **not** named here.

One inbound `.text` `E8`/`E9`: `JMP` at `0x0040c49a` inside
already-pinned `CBattleEngine__IsEnergyWeapon` `0x0040c480`.
Zero encodings of imm `b0 22 41 00` in the image (not a vtable
slot).

Source architecture (not proof):
`CBattleEngineJetPart::IsEnergyWeapon`
`BattleEngineJetPart.cpp:861-867`. Retail inlines the list walk
instead of `E8` GetCurrentWeapon. Bare `ret` matches zero stack
args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000122b0` is not `8b 01`, **or**
`0x000122e8` is not `c3`, **or** `0x00012301` is not `c3`, **or**
body SHA-256 is not `f48d4e1d…3f10`, **or**
`tools/call_xref_scan.py` on `0x004122b0` is not exactly one
`JMP` at `0x0040c49a`, **or** any encoding of imm `b0 22 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `f48d4e1d…3f10`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x10]` / `[+0x18]` / `[+0x55c]`. Did not invent a Core owner.

Retail entity: jet-part IsEnergyWeapon query from the
already-pinned dispatcher. Stuart architecture (not proof):
`BattleEngineJetPart.cpp:861-867`.

Nearest reconstruction owner: **none added**. Existing
`RetailWeaponStores` readout is not rewritten and is not raised
to `REBUILD_READY` from this envelope. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__IsEnergyWeapon` /
`CBattleEngineJetPart__IsWeaponOverheated`. Next named:
`CBattleEngineWalkerPart__GetWeaponName` `0x004145a0` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004122b0` | `CBattleEngineJetPart__IsEnergyWeapon` | `8b01 … c3` (82 B) | incoming-ECX thiscall; bare ret ×2; 82 B; 0 E8 / 0 E9; 1 inbound JMP. HIGH on ABI, inlined list walk, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x55c]` name or rebuild parity. |
