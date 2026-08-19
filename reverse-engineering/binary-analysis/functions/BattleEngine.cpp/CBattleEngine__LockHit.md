# CBattleEngine__LockHit

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is the 2026-08-04 target-lock promotion label, not this proof.
This wake landed `1093bee8` `CBattleEngine__StartLock` — not redone.
Cycle 90 accepted the lock-trio map. Did not adopt a C1 rename.
Did not reopen Generation 17's one-node C2. Operator closed the
unlabeled first-gates mill; this is the last of the 2026-08-04
five-row lock cohort without a 2026-08-19 PE note.

> Address: `0x00407140`

## Contract

Incoming-ECX `thiscall`. First insn `mov edx, [esp+4]`. Two
`ret 0x4` (`0x00407186`, `0x004071a6`). Body
`0x00407140`–`0x004071a8` is 105 bytes, SHA-256
`eb6914393a80a1a0d314385955c4188946ad9a2115fe5d49da6224c7dd80605c`.
That is the PE-file hash; the 2026-08-11 C1-closure SHA is a
Ghidra-export digest and is not this proof. Three `E8`, zero `E9`.
Neighbour table `CBattleEngine__GetCurrentTarget` starts at
`0x004071b0` after seven `nop`s and is not rewritten. Preceding
table `CBattleEngine__FireLock` ends at `0x0040713e` and is not
rewritten.

The body:

1. `edx = [esp+4]` / `test edx, edx` / `je` the shared epilogue.
2. Walk the set at `this+0x2a4` (`add ecx, 0x2a4`). Same occupancy
   FireLock uses for the fired-lock set. For each live node `esi`:
   `cmp [esi], edx`. No match continues; walk-end `ret 0x4` at
   `0x00407186`.
3. Match: `push esi` / `E8` `CSPtrSet__Remove` `0x004e5bd0`.
4. If `esi != 0`: `ecx=esi` / `E8` `CGenericActiveReader__dtor`
   `0x0044b1d0`, then `push esi` / `mov ecx, 0x009c3df0` / `E8`
   `CDXMemoryManager__Free` `0x00549220`.

Those field names and the callee bodies are **not** this proof.
Generation 17 already admits the retained non-null sole-matching-node
removal path as `C2_BOUNDED_RUNTIME`. This note does not widen that
grade. Other list paths, free-head, destructor, return, identity,
and rebuild remain open.

Six inbound `.text` `E8`/`E9`: `CALL` at `0x004d8e00` inside
table `VFuncSlot_02_004d8dc0`; `0x004d9351`, `0x004d93a7`,
`0x004d959a` inside table `VFuncSlot_66_004d8e40`; `0x004daafc`
inside table `CRound__SetTargetReaderIfAllowed`; `0x004dab6b`
inside table `CRound__RemoveActiveReaderById`.

Three measured sites (`0x004d8e00`, `0x004daafc`, `0x004dab6b`)
do `ecx=[esi+0xec]` / `test byte [ecx+0x34], 8` / `push [esi+0xe8]`
/ `E8` this entry. `ecx` at the call is still `[esi+0xec]`. Those
round fields are **not** this proof. Zero encodings of imm
`40 71 40 00` in the image.

Source architecture (not proof): `CBattleEngine::LockHit`
`BattleEngine.cpp:882-897` walks `mFiredLocks`, `Remove`s the
matching node, and `delete`s it. Retail inlines the dtor+Free.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00007140` is not `8b 54 24 04`, **or**
`0x00007149` is not `8b 81 a4 02 00 00`, **or** `0x0000718a` is
not `e8 41 ea 0d 00`, **or** `0x00007195` is not
`e8 36 40 04 00`, **or** `0x000071a0` is not `e8 7b 20 14 00`,
**or** `0x000071a6` is not `c2 04 00`, **or** body SHA-256 is not
`eb691439…605c`, **or** `tools/call_xref_scan.py` on
`0x00407140` is not exactly those six `CALL`s, **or** a seventh
`.text` `E8`/`E9` to this entry exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `eb691439…605c`. `call_xref_scan` still six `CALL`s.
Did not open Ghidra. Did not edit `rebuild/**`. Did not change
the Generation 17 C2 row.

Retail entity: `CBattleEngine` fired-lock-set remove-and-free.
Stuart architecture (not proof): `BattleEngine.cpp:882-897`.

Nearest reconstruction owner: **none**. Core has no `+0x2a4`
fired-lock occupancy. `Simulation.TryFire` is the FireLock spawn
owner, not this hit-time removal.

Not the owner: Godot `Level100EffectCue.AquilaTargetLocked` is the
homing-missile lock sound.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement lock sets from this mapping
until that lane names the arm.

Siblings: `CBattleEngine__StartLock` /
`CBattleEngine__FireLock` /
`CBattleEngine__DisplayLock` /
`CBattleEngine__GetCurrentTarget` in this folder. The 2026-08-04
five-row lock cohort now all have 2026-08-19 PE notes. Next named:
`CBattleEngine__HandleLocks` `0x00406560` (StartLock's only
inbound owner; existing withdrawn-filename note is not a
2026-08-19 PE contract).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00407140` | `CBattleEngine__LockHit` | `8b542404 56 85d2 … 8b81a4020000 … e841ea0d00 … e836400400 … e87b201400 … c20400` (105 B) | incoming-ECX thiscall; ret 0x4 ×2; 105 B; 3 E8 Remove + dtor + Free / 0 E9; 6 inbound round/vfunc sites. HIGH on ABI, `+0x2a4` walk, remove-then-free. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on field names, Gen17 widen, or rebuild parity. |
