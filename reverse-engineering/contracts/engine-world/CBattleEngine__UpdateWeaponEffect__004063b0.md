# CBattleEngine__UpdateWeaponEffect

Status: active corrected static contract; saved Ghidra name pending promotion
Last updated: 2026-08-28
Summary: the current saved name at `0x004063b0` is retained as document
identity, but exact pristine instructions and independently matching source
identify the function as `CBattleEngine::SetCollisionShape`, not a weapon
effect helper.
Evidence: MEASURED — exact body, instruction-level calls/stores, compiler
file/line allocation marker, `CCylinder` RTTI/vtable, direct caller census, and
retained source correspondence.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004063b0`

## Adjudicated identity

- Exact half-open body: `[0x004063b0,0x00406459)`, 169 bytes / 53
  instructions.
- Raw body SHA-256:
  `fa65f74625e618d5c72064642a20c848ae261835f5297c076a81e34a6674f575`.
- ABI: incoming-`ECX` `thiscall`, no explicit argument, bare `ret`.
- Current saved Ghidra name: `CBattleEngine__UpdateWeaponEffect`.
- Exact semantic/source identity: `CBattleEngine::SetCollisionShape`.
- Ghidra mutation: not performed by this correction. Rename promotion remains
  subject to the Ghidra backup, isolated validation, apply, and readback gate.

The former packet label and weapon-effect prose were analyst metadata, not
semantic proof. The packet itself already contained the decisive contrary
facts: BattleEngine source path/line, `0x20` allocation, two float-returning
virtual calls, a radius square, and submission through `[this+0x38]`. Direct
instruction and type evidence now adjudicate those facts.

## Contract

1. Call `this` virtual `+0x40` (`GetRadius`) and retain its float result.
2. Allocate 32 bytes with category 21 (`MEMTYPE_BATTLEENGINE`), source path
   `C:\dev\ONSLAUGHT2\BattleEngine.cpp`, compiled line 501.
3. On success, call virtual `+0xc0` (`COfGHeight`), multiply it by exact
   `0.5f`, construct the `CCylinder` object with vtable `0x005d88cc`, radius
   at `+0x14`, radius squared at `+0x18`, and half-height at `+0x1c`.
4. On allocation failure, use a null shape pointer.
5. Submit new-or-null through `[this+0x38]`
   (`mCollisionSeekingThing`) virtual `+0x24` (`SetShape`) and return without
   a scalar result or local recovery.

There is no weapon/effect/projectile-list access and no store at shape `+0x10`.
The previous `CLine-like`, max-life, gravity, weapon speed, and angular-velocity
interpretations are superseded.

## Call graph and consumers

Direct `.text` callers are exactly `0x0040c1db` and `0x0040c27f` in
`CBattleEngine::HandleEvent`, after accepted 6000/6001 completion writes. The
retained Init source call is an exact inline twin at
`[0x004054cb,0x0040554b)`, SHA-256
`ef650b3bfe5f31fbec7da07daabe94f7eb8e92b20c1b7ab4b8ac35001edaf332`.

The default receiver at `0x00426370` deletes the previous shape, owns the
incoming pointer, and refreshes its owner-relative centre. Because the caller
still submits null on allocation failure, that default path deletes the former
shape and then faults during centre refresh rather than preserving it. The
`CCylinder` collision-resolver prefix at `0x0043fe20` separately proves that
`+0x14` is radial extent and `+0x1c` is axial half-extent.

Current Core owns the single-player 0.4 m horizontal radius and 1.9 m
center-of-gravity height, but no replaceable cylinder object. This contract does
not justify a generic event or heap-compatibility framework. A future vertical
collision consumer must use the proven 0.95 m half-height and install the shape
after settled state selection.

## Evidence and limits

- Retained source owner: `BattleEngine.cpp:495-502`; allocation expression at
  retained line 500 versus compiled marker 501 is a one-line revision skew.
- Direct caller pair and body bytes were independently reproduced from the
  pristine specimen without opening Ghidra.
- Historical TTD coverage of 166 body bytes proves execution in its named
  capture only; it is not needed for the semantic identity.
- The tracked source-crosswalk's older `NO_MATCH_FOUND` row is a bounded
  historical reducer result, not current counterevidence. This correction does
  not rewrite that generated ledger.

Cheapest falsifier: cold-disassemble the exact body and show any mismatch in
the allocation metadata, `CCylinder` vtable/layout, two virtual float inputs,
or final `[this+0x38]` `SetShape` submission.
