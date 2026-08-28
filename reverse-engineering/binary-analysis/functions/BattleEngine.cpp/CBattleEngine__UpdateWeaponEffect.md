# CBattleEngine__UpdateWeaponEffect

> Address: `0x004063b0` | Current saved name: `CBattleEngine__UpdateWeaponEffect`

Status: superseded saved-name note; exact semantic identity recovered
Last updated: 2026-08-28
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — pristine bytes, cold instruction decode, direct-call
census, compiler file/line marker, allocation metadata, shape RTTI/vtable, and
independently matching retained source. No Ghidra project was opened or
mutated.

The title and path preserve the current saved Ghidra name so tracked links and
the current name-table gate remain honest. That name is semantically wrong.
The exact body is `CBattleEngine::SetCollisionShape`; a Ghidra rename remains a
separate promotion requiring the owning backup/apply/readback procedure.

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

Grade: `PARTIAL_CONTRACT`. Core already carries the exact single-player
horizontal contact radius as
`SimulationConstants.Level100PlayerContactRadiusMillimeters = 400` and the
released center-of-gravity height as
`Level100Terrain.WalkerCenterOfGravityMillimeters = 1900`. It does not expose a
generic collision-object replacement or a deterministic `CCylinder` state.

No heap-shaped compatibility layer is justified merely to mirror the retail
allocation. When a current collision consumer needs the vertical cylinder
extent, the proven contract is radius 400 mm, half-height 950 mm, installed
after the settled mode write and before completion is externally observed.
The existing swept projectile hit test is a separate collision contract and is
not silently redefined by this function alone.

## Falsifiers

Any of the following rejects this identity: body hash differs; `0x004063cf`
stops calling receiver slot `+0x40`; allocation stops using size `0x20`,
category `0x15`, the BattleEngine source path, or line 501; the constructed
object stops using vtable `0x005d88cc`; the body stops storing radius,
radius-squared, and half of slot-`+0xc0`; or the final call stops submitting the
pointer through `[this+0x38]` slot `+0x24`.
