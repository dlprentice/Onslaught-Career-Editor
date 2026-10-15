# CBattleEngineWalkerPart__GetWeaponCharge

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
100 accepted through ChargeWeapon `9bde6c3a` — not redone. This
wake already landed the WeaponFired cluster `384e45cb` /
`d8424bfa` / `4ae71dfc` — not redone. Envelope. Did not mill
FUN_*. Did not implement lock sets.

> Address: `0x00414520`

## Contract

Incoming-ECX `thiscall`. First insn `push ecx`. Three bare `ret`
(`0x0041457f`, `0x00414589`, `0x00414591`). Body
`0x00414520`–`0x00414591` is 114 bytes, SHA-256
`d517b686182b766f4a90aae3251a9add31b8ee74ae7af2d5196878d0a7cfc016`.
Capstone: 43 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.
Raw `0xE8` byte count is 1 and matches the instruction count.
Raw `0xE9` byte count is 1 and is not an `E9` instruction.

Pinned body:

1. `E8` already-pinned
   `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030`.
   EAX==0 loads 0.0f at `0x005d856c` and returns.
2. `edx = [eax+0xa4] + 0xc` then the same 5-slot / `+=0x64` /
   cap `0x1f4` walk ChargeWeapon already counts. All `-1` loads
   0.0f and returns. Those slots are **not** named here.
3. Else a second walk, `fild`, `fdivr [eax+0x60]`. ST(0) is the
   return. `[+0x60]` is **not** named here.

One inbound `.text` `E8`/`E9`: `CALL` at `0x0040c52b` inside
already-named `CBattleEngine__GetWeaponCharge` `0x0040c4a0`.
Zero encodings of imm `20 45 41 00` in the image (not a vtable
slot). The parent table name is counted, not rewritten.

Source architecture (not proof):
`CBattleEngineWalkerPart::GetWeaponCharge`
`BattleEngineWalkerPart.cpp:879-885`. Retail is not a one-call
`GetCharge()` wrapper — the `[+0xa4]+0xc` walk is the body.
Bare `ret` matches zero stack args. ST(0) is the returned
float.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00014520` is not `51`, **or**
`0x00014521` is not `e8 0a fb ff ff`, **or** `0x00014591` is
not `c3`, **or** body SHA-256 is not `d517b686…c016`, **or**
`tools/call_xref_scan.py` on `0x00414520` is not exactly one
`CALL` at `0x0040c52b`, **or** any encoding of imm `20 45 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `d517b686…c016`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0xa4]` / `[+0x60]`. Did not walk a `GetCharge` callee.

Retail entity: walker-part current-weapon charge query. Stuart
architecture (not proof): `BattleEngineWalkerPart.cpp:879-885`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__ChargeWeapon` /
`CBattleEngineWalkerPart__GetCurrentWeapon`. Next named:
`CBattleEngine__GetWeaponCharge` `0x0040c4a0` (no 2026-08-19 PE
envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00414520` | `CBattleEngineWalkerPart__GetWeaponCharge` | `51 e80afbffff … c3` (114 B) | incoming-ECX thiscall; bare ret ×3; 114 B; 1 E8 / 0 E9 / 1 target; 1 inbound CALL. HIGH on ABI, GetCurrentWeapon, 0.0f empty, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x60]` name or rebuild parity. |
