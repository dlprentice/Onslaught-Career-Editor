# CBattleEngine__Damage

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
97 accepted JetPart Move and GroundParticleEffect. This wake
landed Hit `efbf8e53` and Gravity `5f7915a1` — not redone.
Envelope, not a 233-instruction walk. Did not mill FUN_*. Did not
implement lock sets. Did not widen the existing Gen31 C2 row.

> Address: `0x0040a890`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 0x3c`. `esi = ecx`.
One `ret 0x10` at `0x0040ac22`. Body `0x0040a890`–`0x0040ac24`
is 917 bytes, SHA-256
`224c0577b539bbf0d6fa118a6355502f9aead3bc588e59ae3bf08bdf3cd1ff91`.
Capstone: 233 insns, 3 `E8`, zero `E9`, 3 unique rel32 targets.
Neighbour table after this body is not rewritten. Preceding table
`CBattleEngine__Morph` is already pinned and is not rewritten.

Pinned prologue, with `esi = ecx`:

1. `fld [esp+0x40]` / `fcomp [0x005d856c]` (0.0f). CF+ZF set
   jumps to the late epilogue (amount <= 0).
2. Copy `[esi+0xf8]` / `[esi+0x100]` / `[esi+0xfc]` onto the
   stack. Those fields are **not** named here.
3. `fmul [0x005d8c50]` then add into `[[esi+0x574]+0x48]`. The
   player-stat slot is **not** named here.
4. Counted, not contracted: `E8` `CDXMemoryManager__Alloc`
   `0x005490e0`; `E8` `CSPtrSet__AddToHead` `0x004e5a80`;
   `E8` `CBattleEngine__RandomizeOffsets4B8_4C0` `0x00407940`.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`90 a8 40 00`: file `0x001d8a64` / VA `0x005d8a64` (vtable
slot 40, `+0xa0` from the `CBattleEngine` vtable base
`0x005d89c4` named by HandleEvent; adjacent to already-pinned
Hit slot 39). Neighbouring dwords are **not** this proof.

Source architecture (not proof): `CBattleEngine::Damage`
`BattleEngine.cpp:2127+`. Retail `ret 0x10` matches four stack
args.

Rebuild mapping: `PARTIAL_CONTRACT` (PE envelope only). The
existing Gen31 C2 bounded Damage row is **not** raised. See the
section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x0000a890` is not `83 ec 3c`, **or**
`0x0000a89e` is not `8b f1`, **or** `0x0000ac22` is not
`c2 10 00`, **or** body SHA-256 is not `224c0577…ff91`, **or**
`tools/call_xref_scan.py` on `0x0040a890` is not empty, **or**
`0x001d8a64` is not `90 a8 40 00`, **or** a second encoding of
that imm exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `224c0577…ff91`. `call_xref_scan` still empty.
File `0x001d8a64` still `90 a8 40 00`. Did not open Ghidra. Did
not edit `rebuild/**`. Did not walk the three callees. Did not
name `[+0xf8]` / `[+0xfc]` / `[+0x100]`. Did not widen the
existing C2.

Retail entity: `CBattleEngine` vtable slot-40 Damage. Stuart
architecture (not proof): `BattleEngine.cpp:2127+`. Existing
campaign C2 is a bounded runtime row on this same entry; this
note is the PE envelope only.

Nearest reconstruction owner: **none** added. Existing C2 /
Level 521 Damage evidence is not re-derived. L100 card
`t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngine__Hit` / `CBattleEngine__Morph` in this
folder. Next named: `CBattleEngine__ChangeWeapon` `0x00409f70`
(named; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0040a890` | `CBattleEngine__Damage` | `83ec3c 8bf1 … c21000` (917 B) | incoming-ECX thiscall; ret-0x10; 917 B; 3 E8 / 0 E9 / 3 targets; 0 inbound; unique vtable slot 40 at `0x005d8a64`. HIGH on ABI, amount<=0 early-out, unique slot. Mapping `PARTIAL_CONTRACT`; existing C2 not widened. **Not** on field names or rebuild parity. |
