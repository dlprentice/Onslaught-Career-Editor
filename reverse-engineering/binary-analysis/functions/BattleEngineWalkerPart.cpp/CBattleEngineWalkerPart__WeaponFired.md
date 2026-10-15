# CBattleEngineWalkerPart__WeaponFired

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
redone. This wake already landed ChargeWeapon `9bde6c3a` — not
redone. Envelope. Did not mill FUN_*. Did not implement lock sets.

> Address: `0x004140d0`

## Contract

Incoming-ECX `thiscall`. First insn `push ebx`. `esi = ecx`.
Seven `ret 4` (`0x00414226`, `0x0041424c`, `0x00414318`,
`0x00414365`, `0x00414381`, `0x004143d6`, `0x00414404`). Body
`0x004140d0`–`0x00414406` is 823 bytes, SHA-256
`a9c2ed4de55f1c3bc4bee4a459e9e7c31e2ff17b8b3cd7eb286f5c0cbffb5f65`.
Capstone: 220 insns, 3 `E8`, 2 `E9`, 3 unique rel32 targets.
Raw `0xE8` byte count is 7 and is not the instruction count.
Both `E9` targets (`0x004143b2`, `0x004143bc`) sit inside this
body. Neighbour table
`CBattleEngineWalkerPart__GetWeaponAmmoPercentage` starts at
`0x00414410` after a `nop` pad and is not rewritten.

Pinned body, with `esi = ecx`:

1. `ebp = [esp+0x14]` after the four pushes — the one stack
   argument. `ret 4` matches that one dword.
2. Counted list walk on `[esi]` / `[esi+8]` (same shape
   GetCurrentWeapon / ChangeWeapon already count). Compare the
   node to `ebp`.
3. Store/heat/overheat walk on already-counted `[+0x20]`.
   `fcomp` 0.0f at `0x005d856c`. `fcomp` 8.0f at `0x005d8c44`.
   Those slots are **not** named here.
4. Three `E8`, all already-named neighbour
   `CEngine__ClampBurstStartTimeFloorNow` `0x0040f110`. That
   existing note is not rewritten. EAX is set `1` or `0` on the
   `ret 4` paths.

One inbound `.text` `E8`/`E9`: `CALL` at `0x0040c313` inside
already-named `CBattleEngine__CanSpawnBurstForResolvedEntry`
`0x0040c2e0`. Zero encodings of imm `d0 40 41 00` in the image
(not a vtable slot). The parent table name is counted, not
rewritten.

Source architecture (not proof):
`CBattleEngineWalkerPart::WeaponFired`
`BattleEngineWalkerPart.cpp:686+`. Retail `ret 4` matches the
one `CWeapon*` argument. Source `WeaponOverheated()` sites
match the three ClampBurst `E8`s only as a counted table name —
do **not** equate them. Source `return TRUE/FALSE` matches EAX
`1`/`0`.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000140d0` is not `53`, **or**
`0x000140d3` is not `8b f1`, **or** `0x0001414f` is not
`e8 bc af ff ff`, **or** `0x00014404` is not `c2 04 00`, **or**
body SHA-256 is not `a9c2ed4d…5f65`, **or**
`tools/call_xref_scan.py` on `0x004140d0` is not exactly one
`CALL` at `0x0040c313`, **or** any encoding of imm `d0 40 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `a9c2ed4d…5f65`. `call_xref_scan` still one CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
store/heat/overheat slots. Did not walk the primary/aug arms.
Did not equate ClampBurst to source `WeaponOverheated`.

Retail entity: walker-part WeaponFired from the already-named
CanSpawnBurst parent. Stuart architecture (not proof):
`BattleEngineWalkerPart.cpp:686+`.

Nearest reconstruction owner: **none**. L100 card `t_aa5586e5`
is on a playable training-path diet — do not implement from this
mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__ChargeWeapon` /
`CBattleEngineWalkerPart__FireWeapon` /
`CBattleEngineWalkerPart__GetCurrentWeapon`. Next named:
`CBattleEngine__CanSpawnBurstForResolvedEntry` `0x0040c2e0` (no
2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004140d0` | `CBattleEngineWalkerPart__WeaponFired` | `53 8bf1 … c20400` (823 B) | incoming-ECX thiscall; ret-4 ×7; 823 B; 3 E8 / 2 E9 / 3 targets; 1 inbound CALL. HIGH on ABI, list walk, three ClampBurst E8, unique inbound. Mapping `PARTIAL_CONTRACT`. **Not** on store-slot names or rebuild parity. |
