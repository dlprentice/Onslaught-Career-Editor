# CBattleEngine__GetCurrentTarget

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
This wake landed `97773418` `CBattleEngine__DisplayLock` and
`9f66373e` `CBattleEngine__FireLock` — not redone. Cycle 88
accepted FireLock. Did not adopt a C1 rename. Operator closed the
unlabeled first-gates mill; this is the last open/opaque sibling of
that named lock cohort. Cycle 89 accepted this byte note. This
follow-on names rebuild owners only; it does not redo the body.

> Address: `0x004071b0`

## Contract

Incoming-ECX `thiscall`. First insn `push ecx`. Three bare `ret`
(`0x00407242`, `0x004072ff`, `0x00407305`). Body
`0x004071b0`–`0x00407305` is 342 bytes, SHA-256
`311eadaf6a6ab665fec93b03a0d9181ab7dbef6df718d4f296d7e29b0d1879d4`.
Zero `E8`, zero `E9`. Neighbour table `CBattleEngine__DisplayLock`
starts at `0x00407310` and is not rewritten. Preceding table
`CBattleEngine__LockHit` ends at `0x004071a8` and is not rewritten.

The body:

1. `edi=[this+0x5e0]`; store `edi+1` back to `+0x5e0`. `esi=0`.
2. Snapshot `[0x00672fd0]` (BSS `mTime`) to `[esp+8]`. If word
   `[this+0x2b4]==0`, return 0.
3. Walk set `this+0x294` (same occupancy as FireLock). For each
   live node: `fld [node+8]` / `fcomp [esp+8]` / `test ah, 1`
   then `cmp dword [node], 0`. Both true → return `[node]`.
4. Else walk set `this+0x2a4`. Any `[node]!=0` sets `esi=1`.
   If `esi==0`, return 0.
5. Walk `+0x2a4` again. Word `[this+0x2b4]` wraps the cursor.
   When saved `edi` reaches 0 and `[node]!=0`, return `[node]`.
   Else `dec edi` and continue. Empty walk returns 0.

Those field names are **not** this proof.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`b0 71 40 00`: file `0x001d8b08` / VA `0x005d8b08` =
`CBattleEngine` vtable `0x005d89c4` slot 81 (`+0x144`).
Neighbouring dwords are **not** this proof.

Source architecture (not proof): `CBattleEngine::GetCurrentTarget`
`BattleEngine.cpp:913-977` increments `mCurrentTarget`, returns the
first finished live `mLocks` unit, else round-robins `mFiredLocks`
using `mRecentLocks`. Retail inlines both walks with the same
`+0x294` / `+0x2a4` sets FireLock uses.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x000071b0` is not `51`, **or**
`0x00007305` is not `c3`, **or** `0x000071bb` is not
`66 39 b1 b4 02 00 00`, **or** body SHA-256 is not
`311eadaf…79d4`, **or** `tools/call_xref_scan.py` on
`0x004071b0` is not empty, **or** `0x001d8b08` is not
`b0 71 40 00`, **or** a second encoding of that imm exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `311eadaf…79d4`. `call_xref_scan` still empty.
File `0x001d8b08` still `b0 71 40 00`. Cycle 89 accepted this
byte note. Origin even at `30ade64e`. Did not open Ghidra.
Did not edit `rebuild/**`.

Retail entity: `CBattleEngine` vtable slot 81 lock-set reader.
Stuart architecture (not proof): `BattleEngine.cpp:913-977`.

Nearest reconstruction owner: **none**. Core has no lock-set
walk, no `+0x5e0` cursor, and no `+0x2b4` recent-lock word.

Not the owner: Godot `Level100EffectCue.AquilaTargetLocked` in
`rebuild/OnslaughtRebuild.Godot/Level100AudioCatalog.cs` is the
homing-missile lock **sound**. HUD README: the canonical actor
snapshot does not supply target lock. Do not treat that cue as
this vtable reader.

If L100 later owns player lock sets, this reader belongs next
to that Core type — not in Godot. Focused test: none. L100
card `t_aa5586e5` is on a playable training-path diet — do not
implement lock sets from this mapping until that lane names
the arm.

Siblings: `CBattleEngine__FireLock` /
`CBattleEngine__DisplayLock` in this folder.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004071b0` | `CBattleEngine__GetCurrentTarget` | `51 5657 8bb9e0050000 … 6639b1b4020000 … 59c3` (342 B) | incoming-ECX thiscall; bare ret ×3; 342 B; 0 E8/E9; 0 inbound; unique vtable slot 81 at `0x005d8b08`. HIGH on ABI, `+0x294`/`+0x2a4` walks, `+0x5e0` increment, `+0x2b4` word gate. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on field names or rebuild parity. |
