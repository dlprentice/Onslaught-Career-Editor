# CBattleEngineJetPart__WeaponFired

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake already landed ChargeWeapon `9bde6c3a`, WalkerPart
WeaponFired `384e45cb`, and CanSpawnBurst `d8424bfa` — not
redone. Envelope. Did not mill FUN_*. Did not implement lock sets.

> Address: `0x00412050`

## Contract

Incoming-ECX `thiscall`. First insn `push ebx`. `esi = ecx`.
Three `ret 4` (`0x00412132`, `0x0041215a`, `0x004121a0`). Body
`0x00412050`–`0x004121a2` is 339 bytes, SHA-256
`9526b4cfa6ff6853a291443c3bccce17556a05e5b45f7130954b9bc10af73e0f`.
Capstone: 99 insns, 1 `E8`, zero `E9`, 1 unique rel32 target.
Raw `0xE8` byte count is 1 and matches the instruction count.

Pinned body, with `esi = ecx`:

1. `ebx = [esp+0x10]` after the three pushes — the one stack
   argument. `ret 4` matches that one dword.
2. Counted list walk on `[esi]` / `[esi+8]` (same shape
   WalkerPart WeaponFired already counts). Compare the node to
   `ebx`.
3. Store/heat/overheat walk on `[esi+0x18]`. That slot is **not**
   named here. `fcomp` 0.0f at `0x005d856c`. `fcomp` 8.0f at
   `0x005d8c44`.
4. One `E8` already-named neighbour
   `CEngine__ClampBurstStartTimeFloorNow` `0x0040f110`. That
   existing note is not rewritten. EAX is set `1` or `0` on the
   `ret 4` paths.

One inbound `.text` `E8`/`E9`: `CALL` at `0x0040c2ef` inside
already-pinned `CBattleEngine__CanSpawnBurstForResolvedEntry`
`0x0040c2e0`. Zero encodings of imm `50 20 41 00` in the image
(not a vtable slot).

Source architecture (not proof):
`CBattleEngineJetPart::WeaponFired`
`BattleEngineJetPart.cpp:776-823`. Retail `ret 4` matches the
one `CWeapon*` argument. Source has no primary/aug arms — the
retail body is the list walk only. Do **not** equate the
ClampBurst `E8` to source `WeaponOverheated`.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00012050` is not `53`, **or**
`0x00012052` is not `8b f1`, **or** `0x000120d0` is not
`e8 3b d0 ff ff`, **or** `0x000121a0` is not `c2 04 00`, **or**
body SHA-256 is not `9526b4cf…3e0f`, **or**
`tools/call_xref_scan.py` on `0x00412050` is not exactly one
`CALL` at `0x0040c2ef`, **or** any encoding of imm `50 20 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `9526b4cf…3e0f`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x18]` or store/heat/overheat slots. Did not equate ClampBurst
to source `WeaponOverheated`.

Retail entity: jet-part WeaponFired from the already-pinned
CanSpawnBurst dispatcher. Stuart architecture (not proof):
`BattleEngineJetPart.cpp:776-823`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__WeaponFired` /
`CBattleEngine__CanSpawnBurstForResolvedEntry`. Next named:
`CBattleEngineWalkerPart__GetWeaponCharge` `0x00414520` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00412050` | `CBattleEngineJetPart__WeaponFired` | `53 8bf1 … e83bd0ffff … c20400` (339 B) | incoming-ECX thiscall; ret-4 ×3; 339 B; 1 E8 / 0 E9 / 1 target; 1 inbound CALL. HIGH on ABI, list walk, ClampBurst E8, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0x18]` name or rebuild parity. |
