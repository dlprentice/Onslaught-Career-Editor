# CBattleEngine__SetCollisionShape

> Address: `0x004063b0` | Current saved name: `CBattleEngine__SetCollisionShape`

<!-- ghidra-name-drift-accepted: 0x004063b0 CBattleEngine__UpdateWeaponEffect (2026-08-28; dated db.18626 projection superseded by db.18634 readback) -->

Status: active measured function note; exact semantic identity promoted
Last updated: 2026-08-28
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — pristine bytes, cold instruction decode, direct-call
census, compiler file/line marker, allocation metadata, shape RTTI/vtable,
independently matching retained source, and separate-process Ghidra readback.

The exact body is `CBattleEngine::SetCollisionShape`. The former
`CBattleEngine__UpdateWeaponEffect` analyst label was replaced by a one-row
`SET_NAME` promotion on 2026-08-28 after an independent family-specific GO,
fresh replica rehearsal, verified H: PRE backup, live dry run, one live apply,
separate-process readback, verified H: POST backup, and tracked-snapshot reopen.

## Exact identity

The body is `[0x004063b0,0x00406459)`, 169 bytes / 53 instructions, raw
SHA-256
`fa65f74625e618d5c72064642a20c848ae261835f5297c076a81e34a6674f575`.
It receives `this` in `ECX`, takes no stack argument, and returns with a bare
`ret` at `0x00406458`.

The full released transaction is:

1. Call receiver virtual slot `+0x40` and retain the returned float.
2. Allocate `0x20` bytes through `CDXMemoryManager::Alloc`, category `0x15`
   (`MEMTYPE_BATTLEENGINE`), with embedded path
   `C:\dev\ONSLAUGHT2\BattleEngine.cpp` and compiled line `0x1f5` / 501.
3. If allocation succeeds, call receiver virtual slot `+0xc0`, multiply its
   float result by exact binary32 `0.5f`, install vtable `0x005d88cc`, clear
   object words `+0x04/+0x08/+0x0c`, store the first float at `+0x14`, its
   square at `+0x18`, and the halved second float at `+0x1c`.
4. If allocation fails, retain a null shape pointer.
5. Read `[this+0x38]`, pass the new-or-null shape, and call that object's
   virtual slot `+0x24`; then return. There is no local rollback or status
   result.

The body contains no store to shape `+0x10`; the previous note's claim that it
was zeroed was false. It also contains no weapon pointer, projectile list,
speed, angular velocity, life, or gravity operation.

## Source and type bridge

Retained `BattleEngine.cpp:495-502` is structurally exact:

```cpp
void CBattleEngine::SetCollisionShape()
{
    float r = GetRadius();
    CCylinder* shape = new(MEMTYPE_BATTLEENGINE)
        CCylinder(r, COfGHeight() * 0.5f);
    mCollisionSeekingThing->SetShape(shape);
}
```

The compiler marker is one line later than the retained snapshot's allocation
line, a source-revision line-number skew rather than a behavioral difference.
The two virtual calls, exact half constant, allocation size/category,
`CCylinder` vtable, radius/radius-squared/height layout, and final
`[this+0x38]` submission independently reproduce every operation in that
source body. Thus `+0x40` is `GetRadius`, `+0xc0` is `COfGHeight`, and
`this+0x38` is `mCollisionSeekingThing` for this transaction.

The pristine PC `CBattleEngine::GetRadius` returns `0.4f` in single-player and
`1.0f` in multiplayer; `COfGHeight` returns `BATTLE_ENGINE_COFGHEIGHT` /
`1.9f`. The resulting single-player cylinder arguments are therefore radius
`0.4f` and half-height `0.95f`. Neither getter selects on walker versus jet
state in this build.

The Xbox USA retail, Issue 11, and Europe homologs preserve the same shape
transaction but broaden `GetRadius`: they return `1.0f` when the current level
is strictly above 849 and below 900 **or** serialized `CWorld::WorldType` is
`1` (co-op) or `2` (versus), and `0.4f` otherwise. The USA getter is
`[0x001688d0,0x00168900)`, 48 bytes, SHA-256
`f47f6fd5da7d8d3d041f413553d9e99bd0e2f6931eda519042e4fb467e16741f`;
the equivalent field is Xbox `CWorld+0x26c` and PC `CWorld+0x27c`, loaded from
the final integer in version-3 world headers. PC, Xbox USA, and Xbox Europe
ship byte-identical `WorldHeaders.dat`; Level 100 has exact type `0`, so this
platform divergence does not alter its 0.4-m cylinder. A reconstruction should
carry the authored world type only when multiplayer worlds are admitted, not
invent a Battle-Engine-owned radius flag.

## Callers and ordering

The whole `.text` direct-transfer census finds exactly two calls, both in
`CBattleEngine::HandleEvent`:

- `0x0040c1db`, after accepted event 6000 writes transform start time and
  settled state 3 (`JET`);
- `0x0040c27f`, after event 6001 writes settled state 2 (`WALKER`).

The retained Init path also invokes `SetCollisionShape`. Retail inlines the
same construction/submission transaction at `[0x004054cb,0x0040554b)`, 128
bytes, SHA-256
`ef650b3bfe5f31fbec7da07daabe94f7eb8e92b20c1b7ab4b8ac35001edaf332`;
therefore the two out-of-line calls plus this inline twin account for all three
source-semantic use sites. For the two completion events, the state write
definitely precedes shape construction and submission.

## Receiver ownership and collision use

The default `CCSPersistentThing` receiver's slot `+0x24` is
`[0x00426370,0x004263e6)`, 118 bytes, raw SHA-256
`2d68bbd99b76e32861a4c8027999e8f056ef3d8dcf189d6ecdce45910d0ea5ec`.
It deletes the old shape, installs the incoming pointer, obtains the owner's
current centre, and writes the owner-relative centre into shape fields
`+0x04..+0x10`. Thus the default receiver owns the submitted shape and refreshes
placement even though the cylinder dimensions are mode-invariant.

Allocation failure is not a graceful keep-old-shape path. The helper still
submits null; the default receiver deletes the old shape, stores null, and then
dereferences it while refreshing the centre. `mCollisionSeekingThing` itself is
also unchecked. No local rollback restores caller state or the former shape.

The resolver prefix `[0x0043fe20,0x0043fe9d)`, 125 bytes, raw SHA-256
`b67356e3b951170916795695ecec42391e6bf4cffbf26e123e60eac00462dfff`,
independently fixes the geometry semantics: it adds two shapes' `+0x14` values
for the radial gate, then compares absolute axial centre separation against the
sum of their `+0x1c` values. Consequently `+0x14` is radius and `+0x1c` is axial
half-height; the stored `0.95f` represents a full 1.9-m cylinder height.

## Rebuild mapping

Grade: `PARTIAL_CONTRACT`. Core carries the released single-player collision
consequence used by Level 100 inbound actor rounds: radius 400 mm, half-height
950 mm, and centre 760 mm below the actor pose in Core's Y-up basis. An exact
rational finite-cylinder predicate reproduces the resolver's inclusive radial
and cap prefilter. Released mode 1 then computes candidate parameters from the
full three-dimensional norms, equivalent to
`(|P0|-radius)/|V|` and `(|P0|+radius)/|V|`, clamps each to `[0,1]`, rejects
only when both candidates lie strictly beyond the same cap, and selects
candidate zero even when it is not the geometric first contact. Core's
`TryResolveBattleEngineCylinderContact` reproduces that ordering and selected
integer-millimetre impact position with deterministic Q32 square roots. The Q32
step is an explicit approximation of retail binary32/x87 evaluation, not a
claim of sub-millimetre bit identity. The prior target-origin sphere shortcut
is removed.

All three measured Xbox builds preserve this ordinary finite policy and the
response ordering, including movement before callbacks. They diverge for a
generated zero-length line: Xbox's unordered clamps retain NaN roots and write
NaN XYZ, while PC clamps to zero and selects finite `P0`. Core follows the
pristine PC behavior. The released Round producer makes this a structurally
reachable natural branch when old and current positions are equal, although no
stock-play occurrence or frequency is claimed.

PS2 German demo, Europe retail, and USA retail independently preserve the
ordinary finite candidate and response contract. Their resolver returns only a
Boolean, rewrites and marks only the line participant from the minus-root
candidate, uses the plus root only for same-cap rejection, and writes no
contact or normal to the shared report. The concrete round/Battle Engine route
negotiates mode 1; the shared response moves the round, restores velocity,
marks the report hit, then invokes response-owner and peer-owner `Hit` in that
order. PS2 binary32/VU arithmetic is not claimed bit-identical to PC x87 at
exceptional or threshold inputs.

No heap-shaped compatibility layer is justified merely to mirror the retail
allocation. The mapping remains player-Battle-Engine-specific and does not
claim generic actor shapes, impact normals, simultaneous-candidate behavior,
or sub-millimetre x87 identity.

The Round-side line producer is now closed separately. Immediately before
shape dispatch it makes endpoint zero `old-current`; when authored
`RoundLength > 0.001f` and displacement is nonzero, endpoint one is
`normalize(current-old)*RoundLength`, otherwise endpoint one is zero. Thus the
world segment is old-to-current, optionally extended by the authored length,
and collapses to current-to-current when `old==current`. Canonical physics data
contains 61 line-backed Rounds: 51 length zero and ten length `0.5f`; all 91
Round definitions have positive authored speed. Positive speed makes ordinary
movement nondegenerate but does not erase the exact zero-displacement branch.

## Falsifiers

Any of the following rejects this identity: body hash differs; `0x004063cf`
stops calling receiver slot `+0x40`; allocation stops using size `0x20`,
category `0x15`, the BattleEngine source path, or line 501; the constructed
object stops using vtable `0x005d88cc`; the body stops storing radius,
radius-squared, and half of slot-`+0xc0`; or the final call stops submitting the
pointer through `[this+0x38]` slot `+0x24`.
