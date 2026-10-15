# CBattleEngine__SetCollisionShape

Status: active measured contract; saved Ghidra identity promoted
Last updated: 2026-08-28
Summary: exact pristine instructions, independently matching source, and the
separately read-back Ghidra promotion identify `0x004063b0` as
`CBattleEngine::SetCollisionShape`; the former weapon-effect label is retired.
Evidence: MEASURED — exact body, instruction-level calls/stores, compiler
file/line allocation marker, `CCylinder` RTTI/vtable, direct caller census, and
retained source correspondence.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004063b0`

## Identity

- Body `[0x004063b0,0x00406459)`, 169 bytes / 53 instructions, SHA-256 `fa65f74625e618d5c72064642a20c848ae261835f5297c076a81e34a6674f575`.
- ABI: incoming-`ECX` `thiscall`, no explicit argument, bare `ret`.
- Current saved Ghidra name: `CBattleEngine__SetCollisionShape`.
- Exact semantic/source identity: `CBattleEngine::SetCollisionShape`.
- Ghidra promotion: one-row `SET_NAME` cohort applied and independently read
  back on 2026-08-28; 1 of 8,329 functions changed and all frozen columns held.

The former packet label and weapon-effect prose were analyst metadata, not
semantic proof. The packet itself already contained the decisive contrary
facts: BattleEngine source path/line, `0x20` allocation, two float-returning
virtual calls, a radius square, and submission through `[this+0x38]`. Direct
instruction and type evidence now adjudicate those facts.

## Calling convention

- `__thiscall`: the Battle Engine receiver arrives in `ECX`.
- There are no explicit stack arguments, and the function ends with bare
  `RET` at `0x00406458`.
- The body preserves no scalar caller result contract; x87 float results from
  the two virtual getters are consumed internally.

## Prototype and parameter semantics

```c
void __thiscall CBattleEngine::SetCollisionShape(CBattleEngine *this)
```

`this` owns the `mCollisionSeekingThing` pointer at `+0x38` and supplies the
virtual `GetRadius` and `COfGHeight` values. No explicit shape, mode, weapon,
or event parameter enters this body. A null or invalid receiver is not guarded.

## Return value meaning

The function is `void`. It returns no success flag, shape pointer, collision
result, or allocation status. The externally visible result is the receiver's
collision component owning the submitted new shape, subject to the failure
behavior below.

## Globals read/written

The PC body directly writes no mutable global. Its virtual `GetRadius` callee
consults the game's multiplayer verdict, while allocation and `SetShape` have
their own transitive state. The Xbox homolog's getter additionally reads the
serialized `CWorld` type described below. This section does not claim the
transitive callees are side-effect-free.

## Behavior summary

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

## Callees relied on / callers

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

All three measured Xbox builds preserve the transaction but broaden the radius
getter to `1.0f` for strict level range 850--899 or serialized `CWorld` type
`1`/`2` (co-op/versus), otherwise `0.4f`. The selector is Xbox
`CWorld+0x26c`, corresponding to PC `CWorld+0x27c`, and is populated by the
version-3 world-header reader; it is not a Battle Engine or generic network
flag. The USA getter body is `[0x001688d0,0x00168900)`, SHA-256
`f47f6fd5da7d8d3d041f413553d9e99bd0e2f6931eda519042e4fb467e16741f`.
Level 100's exact authored type is `0`, so its released radius remains 0.4 m
on PC and Xbox.

## Error / edge behavior

- Allocation failure produces a null shape pointer, but the body still invokes
  `mCollisionSeekingThing->SetShape(NULL)`.
- The default receiver deletes the former shape, stores null, then faults while
  refreshing the centre through the null pointer; it does not preserve the old
  collider or return an error.
- `mCollisionSeekingThing` and `this` are unchecked. A nondefault derived
  collision component could override slot `+0x24`; its behavior is not inferred
  from the default implementation.
- Radius/height NaNs, infinities, or corrupted virtual returns have no accepted
  bounded witness and remain unknown.

## Runtime corroboration (TTD, bounded)

Historical TTD coverage observed 166 of the 169 body bytes in its named
capture. That proves execution only; it does not establish argument values,
shape ownership, allocation success, or the post-call collision response. The
semantic identity and transaction here rest on pristine instructions,
allocation/type metadata, callers, consumers, and independently matching
retained source, not on an overstated runtime envelope.

Core now consumes the collision consequence needed by Level 100 inbound actor
rounds: a world-vertical cylinder of radius 400 mm and half-height 950 mm,
centred 760 mm below the Core pose origin after retail Z-down is mapped to Core
Y-up. `Level100ActorMechanics.TryResolveBattleEngineCylinderContact` first
uses exact rational comparisons so the finite-cylinder prefilter retains side
and cap equality without a floating tolerance. It then reproduces released
mode 1's unusual response: candidate parameters equivalent to
`(|P0|-radius)/|V|` and `(|P0|+radius)/|V|`, independent `[0,1]` clamping, a
strict same-cap rejection, and unconditional selection of candidate zero. Core
uses deterministic Q32 square roots and returns the selected integer-millimetre
impact position; that Q32 boundary is an explicit approximation of retail
binary32/x87 evaluation rather than a sub-millimetre identity claim. This does
not add a replaceable heap shape or generalize the Battle Engine cylinder to
other actor classes.

The three measured Xbox builds match this response for ordinary finite inputs
and move the marked line owner before callbacks. On a generated zero-length
line, however, Xbox retains unordered NaN roots and writes NaN XYZ, whereas PC
clamps the roots to zero and selects finite `P0`. Core deliberately follows the
pristine PC behavior. The Round producer makes a zero-length line structurally
reachable when old and current positions are equal; occurrence in an
unmodified play trace remains unestablished.

PS2 German demo, Europe retail, and USA retail independently agree for the
ordinary finite transaction. Their Boolean-only resolver rewrites and marks
only the line record from candidate zero, writes no contact/normal to the
report, and the concrete mode-1 response moves the round and restores velocity
before response-owner then peer-owner `Hit` callbacks. PS2 binary32/VU and PC
x87 threshold or exceptional-input equivalence is not promoted.

## Evidence

- Retained source owner: `BattleEngine.cpp:495-502`; allocation expression at
  retained line 500 versus compiled marker 501 is a one-line revision skew.
- Direct caller pair and body bytes were independently reproduced from the
  pristine specimen without opening Ghidra.
- The complete PC line/cylinder resolver is
  `[0x00440510,0x00440ab2)`, SHA-256
  `0ac2091c288520726b727f41a0ae5f720d588508ed5ca8cae75d88f3f5face47`.
  Xbox USA `[0x00181890,0x00181ccf)`, Issue 11
  `[0x00181900,0x00181d3f)`, and Europe
  `[0x001816a0,0x00181adf)` have respective raw SHA-256 values
  `f0e3c676547f7ac4594b0e8f81b57627d381446e70fe2c54e1ad65edd8e2f53e`,
  `d9bf53df0b4683b933c2a6c807d910d6e89985ba048b15be8044377ed0d422bd`,
  and `2f44a76dc4147ecdb2f5ab1aec78f5f9155e1eae1d6f46fdb056d128229c6ddd`.
  The PS2 German-demo/Europe/USA resolver is byte-identical across relocated
  ranges, 1,164 bytes, SHA-256
  `8b2652d7abc84ef21e08c43272e070e2605b91accd4ca009bfe3aaa4864f82db`.
- The PC Round line updater `[0x00425e30,0x00426052)`, SHA-256
  `6bb7d32835c39367ff9b02e0f1401f018a86973c951cabf741c1bef82c531cea`,
  runs after old-position capture/velocity integration and immediately before
  dispatch. It constructs old-to-current, optionally length-extended, or
  zero-displacement lines. The canonical 91-Round census is `19` beam + `11`
  sphere + `61` line, with line lengths `51 × 0` and `10 × 0.5f`; every
  definition has positive speed.
- Live promotion inputs are the one-row manifest SHA-256
  `79ecb856bdc754c77139a9cbe6f1076577991a9db49d61df1d14f10ac910e01b`
  and spec SHA-256
  `67db5cce30b70fdf31b278004f6fee560e6b6caae91148acb55f8a633b41987f`;
  separate-process readback and both H: POST and tracked-snapshot reopen gates
  passed.
- Historical TTD coverage of 166 body bytes proves execution in its named
  capture only; it is not needed for the semantic identity.
- The tracked source-crosswalk's older `NO_MATCH_FOUND` row is a bounded
  historical reducer result, not current counterevidence. This correction does
  not rewrite that generated ledger.

Cheapest falsifier: cold-disassemble the exact body and show any mismatch in
the allocation metadata, `CCylinder` vtable/layout, two virtual float inputs,
or final `[this+0x38]` `SetShape` submission.

## Confidence

4 - exact pristine body, independently matching retained source, RTTI/layout,
caller/consumer closure, and separate-process Ghidra readback agree on the
identity and transaction.

- **High/static-exact:** PC body/range/hash, ABI, calls and stores, allocation
  metadata, `CCylinder` layout, retained-source identity, direct caller pair,
  inline Init twin, and promoted Ghidra name.
- **High/static-exact:** default receiver ownership/failure sequence, inclusive
  finite-cylinder extents, Xbox USA getter body, Level 100 world type 0, and
  the three-build PS2 Boolean/output/callback order.
- **Bounded reconstruction:** Level 100's 400 mm by 1,900 mm world-vertical
  cylinder, centre offset, exact overlap prefilter, mode-1 candidate ordering,
  same-cap rejection, and Q32-selected integer-millimetre impact position.
  Generic actor collision is not promoted by this card.

## Unresolved questions

- The original spelling of the serialized Xbox/PC `CWorld` type member is not
  retained.
- Nondefault collision-component overrides and corrupt/NaN virtual dimensions
  are not characterized.
- Xbox zero-length mode-1 lines preserve NaN output while PC selects finite
  `P0`; the producer admits `old==current`, but stock-play occurrence is
  unknown.
- Generic actor shapes, returned impact normals, simultaneous-candidate
  behavior, stock frequency of zero-displacement lines, ordinary finite
  cross-platform rounding-boundary equivalence, and sub-millimetre x87 identity
  remain outside this bounded contract.
