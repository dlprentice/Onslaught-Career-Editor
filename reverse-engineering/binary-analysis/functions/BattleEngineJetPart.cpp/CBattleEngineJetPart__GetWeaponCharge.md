# CBattleEngineJetPart__GetWeaponCharge

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
100 accepted through ChargeWeapon `9bde6c3a` — not redone. This
wake already landed WalkerPart GetWeaponCharge `2224cd05` and the
dispatcher `ae8c3f44` — not redone. Envelope. Did not mill FUN_*.
Did not implement lock sets.

> Address: `0x00412370`

## Contract

Incoming-ECX `thiscall`. First insn `push ecx`. Live `ecx` is
this (no `mov esi, ecx`). Three bare `ret` (`0x004123b4`,
`0x0041240a`, `0x00412414`). Body `0x00412370`–`0x00412414` is
165 bytes, SHA-256
`12804b64d6f383ec457942f4fbd64363e057a87c39f9e942082356326fbd42ed`.
Capstone: 70 insns, zero `E8`, zero `E9`.

Pinned body:

1. Counted list walk on `[ecx]` / `[ecx+8]` until the index
   matches `[ecx+0x10]`. Same shape WalkerPart GetCurrentWeapon
   already counts. Those slots are **not** named here. Empty
   list loads 0.0f at `0x005d856c` and returns.
2. `ecx = [edi+0xa4] + 0xc` then the same 5-slot / `+=0x64` /
   cap `0x1f4` walk ChargeWeapon already counts. All `-1` loads
   0.0f. Else `fild` / `fdivr [edi+0x60]`. ST(0) is the return.
   `[+0x60]` is **not** named here.

One inbound `.text` `E8`/`E9`: `CALL` at `0x0040c53b` inside
already-pinned `CBattleEngine__GetWeaponCharge` `0x0040c4a0`.
Zero encodings of imm `70 23 41 00` in the image (not a vtable
slot).

Source architecture (not proof):
`CBattleEngineJetPart::GetWeaponCharge`
`BattleEngineJetPart.cpp:879-885`. Retail does **not** `E8`
GetCurrentWeapon — it inlines the list walk. Bare `ret` matches
zero stack args. ST(0) is the returned float.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00012370` is not `51`, **or**
`0x00012371` is not `8b 01`, **or** `0x00012414` is not `c3`,
**or** body SHA-256 is not `12804b64…42ed`, **or**
`tools/call_xref_scan.py` on `0x00412370` is not exactly one
`CALL` at `0x0040c53b`, **or** any encoding of imm `70 23 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `12804b64…42ed`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x10]` / `[+0x60]`.

Retail entity: jet-part current-weapon charge query from the
already-pinned dispatcher. Stuart architecture (not proof):
`BattleEngineJetPart.cpp:879-885`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__GetWeaponCharge` /
`CBattleEngineWalkerPart__GetWeaponCharge`. Next named:
`CBattleEngineWalkerPart__CanWeaponFire` `0x00414630` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00412370` | `CBattleEngineJetPart__GetWeaponCharge` | `51 8b01 … c3` (165 B) | incoming-ECX thiscall; bare ret ×3; 165 B; 0 E8 / 0 E9; 1 inbound CALL. HIGH on ABI, inlined list walk, 0.0f empty, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x10]` name or rebuild parity. |
