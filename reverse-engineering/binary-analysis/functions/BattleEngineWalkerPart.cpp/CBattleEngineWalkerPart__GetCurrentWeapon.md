# CBattleEngineWalkerPart__GetCurrentWeapon

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
98 accepted Hit and Gravity — not redone. This wake landed
Walker/Jet ChangeWeapon — not redone. Envelope. Did not mill
FUN_*. Did not implement lock sets.

> Address: `0x00414030`

## Contract

Incoming-ECX `thiscall`. First insn `push ebx`. Live `ecx` is
this (no `mov esi, ecx`). Three bare `ret` (`0x004140a8`,
`0x004140be`, `0x004140c5`). Body `0x00414030`–`0x004140c5` is
150 bytes, SHA-256
`be9c716b45e42511a087ee08591c8f0362b7bf5fed57f42a52b5a3f152f08405`.
Capstone: 70 insns, zero `E8`, zero `E9`. Neighbour after the
`nop` pad is not rewritten.

Pinned body:

1. `ebp = [ecx+0x10]`. Zero takes the `[ecx+0x20]` /
   `[eax+0x2fc]` / `[ecx+0x1c]` / `[ecx+0x18]` fallbacks.
   Those slots are **not** named here.
2. Else walk `[ecx]` / `[ecx+8]` until the index matches
   `[ecx+0x10]`. Return that node or `[ecx+0x18]` / first
   node / 0.

28 inbound `.text` `E8`/`E9` (27 `CALL`, 1 `JMP` at
`0x0040c38f`). Already-pinned callers include HandleLocks
`0x004065cc`, DisplayLock `0x0040732c`, WalkerPart Move
`0x00413773`, and WalkerPart ChangeWeapon
`0x00413eb8`/`0x00413fd0`/`0x00413fe2`. Zero encodings of imm
`30 40 41 00` in the image (not a vtable slot).

Source architecture (not proof):
`CBattleEngineWalkerPart::GetCurrentWeapon`
`BattleEngineWalkerPart.cpp:609+`. Retail bare `ret` matches
zero stack args. EAX is the returned weapon pointer.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00014030` is not `53`, **or**
`0x00014032` is not `8b 69 10`, **or** `0x000140c5` is not
`c3`, **or** body SHA-256 is not `be9c716b…8405`, **or**
`tools/call_xref_scan.py` on `0x00414030` is not exactly 28
sites, **or** any encoding of imm `30 40 41 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `be9c716b…8405`. `call_xref_scan` still 28 sites.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x10]` / `[+0x18]`.

Retail entity: walker-part current-weapon getter used by Move,
ChangeWeapon, DisplayLock, and HandleLocks. Stuart architecture
(not proof): `BattleEngineWalkerPart.cpp:609+`.

Nearest reconstruction owner: **none** added. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__ChangeWeapon` /
`CBattleEngineWalkerPart__Move`. Next named:
`CBattleEngineWalkerPart__FireWeapon` `0x00413cc0` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00414030` | `CBattleEngineWalkerPart__GetCurrentWeapon` | `53 8b6910 … c3` (150 B) | incoming-ECX thiscall; bare ret ×3; 150 B; 0 E8 / 0 E9; 28 inbound. HIGH on ABI, `[+0x10]` index walk, unique inbound count. Mapping `PARTIAL_CONTRACT`. **Not** on field names or rebuild parity. |
