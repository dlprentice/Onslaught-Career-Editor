# CBattleEngineJetPart__IsWeaponOverheated

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
102 accepted through JetPart GetWeaponAmmoPercentage `109373ed` —
not redone. This wake already landed the overheat walker/dispatcher
pair `33080a9c` / `4013d039` — not redone. Envelope. Did not mill
FUN_*. Did not invent field names. Did not invent a Core owner.

> Address: `0x00412310`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [ecx]`. Live `ecx`
is this. Two bare `ret` (`0x00412348`, `0x00412361`). Body
`0x00412310`–`0x00412361` is 82 bytes, SHA-256
`0e41f1f9b25da253b92300c6236b9f4bbf9f29175d5000c25a9f18fdf8a73fde`.
Capstone: 36 insns, zero `E8`, zero `E9`.

Pinned body:

1. Counted list walk on `[ecx]` / `[ecx+8]` until the index
   matches `[ecx+0x10]`. Same shape JetPart GetWeaponCharge and
   GetWeaponAmmoPercentage already count. Empty / miss returns
   EAX=0.
2. Else `[eax+0xa4]` / `[ecx+0x18]` then EAX =
   `[ecx+eax*4+0x544]`. Those slots are **not** named here.

One inbound `.text` `E8`/`E9`: `JMP` at `0x0040c3ba` inside
already-pinned `CBattleEngine__IsWeaponOverheated` `0x0040c3a0`.
Zero encodings of imm `10 23 41 00` in the image (not a vtable
slot).

Source architecture (not proof):
`CBattleEngineJetPart::IsWeaponOverheated`
`BattleEngineJetPart.cpp:870-876`. Retail inlines the list walk
instead of `E8` GetCurrentWeapon. Bare `ret` matches zero stack
args.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00012310` is not `8b 01`, **or**
`0x00012348` is not `c3`, **or** `0x00012361` is not `c3`, **or**
body SHA-256 is not `0e41f1f9…3fde`, **or**
`tools/call_xref_scan.py` on `0x00412310` is not exactly one
`JMP` at `0x0040c3ba`, **or** any encoding of imm `10 23 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `0e41f1f9…3fde`. `call_xref_scan` still one JMP.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x10]` / `[+0x18]` / `[+0x544]`. Did not invent a Core owner.

Retail entity: jet-part IsWeaponOverheated query from the
already-pinned dispatcher. Stuart architecture (not proof):
`BattleEngineJetPart.cpp:870-876`.

Nearest reconstruction owner: **none added**. Existing
`RetailWeaponStores` readout is not rewritten and is not raised
to `REBUILD_READY` from this envelope. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__IsWeaponOverheated` /
`CBattleEngineJetPart__GetWeaponAmmoPercentage`. Next named:
`CBattleEngine__IsEnergyWeapon` `0x0040c480` (no 2026-08-19 PE
envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00412310` | `CBattleEngineJetPart__IsWeaponOverheated` | `8b01 … c3` (82 B) | incoming-ECX thiscall; bare ret ×2; 82 B; 0 E8 / 0 E9; 1 inbound JMP. HIGH on ABI, inlined list walk, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x544]` name or rebuild parity. |
