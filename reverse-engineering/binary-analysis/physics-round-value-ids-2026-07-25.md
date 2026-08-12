# PhysicsScript round and weapon-mode value ids — resolved

> Date: 2026-07-25. Scope: what the previously unnamed value ids in
> `data/default physics.dat` Round and WeaponMode records mean, and which
> record offset each one writes.
> Updated 2026-08-12 with the recovered `CRound` primary virtual surface, an
> independently linked PC-demo code comparison, and the bounded Generation-21
> strict-`CRound` slot-66 runtime placement.
>
> Every row below is backed by bytes: an RTTI type descriptor read out of the
> pristine Steam binary, the vtable slot that descriptor sits in front of, the
> `MOV`/`FSTP` in that class's apply body, and — for the closure check — the
> value ids actually present in the shipped `.dat`. No class name is invented.
> No claim here rests on a code path alone; where a *behavioural* claim is
> made it cites a measurement recorded elsewhere in the repository.

Prior status: [`functions/CPhysicsScriptStatements.cpp.md`](functions/CPhysicsScriptStatements.cpp.md)
stated for every factory that "exact value classes/layouts remain unproven."
That is now false for the round (type-5) and weapon-mode (type-4) factories,
and for the weapon (type-3) and explosion (type-7) factories as a by-product.

## 1. Method

1. `CPhysicsScriptStatements__CreateStatementType5` (`0x00437490`) and
   `...Type4` (`0x00435010`) were decompiled read-only. Each `case N` allocates
   a leaf object and stores one vtable pointer, giving a complete
   **value id → vtable** map (38 round ids `0x1..0x26`; 37 weapon-mode ids
   `0x1..0x26`, id `0x7` absent).
2. Each of these vtables is laid out as
   `[RTTI complete-object-locator][slot0 dtor][slot1 apply][slot2 size][slot3 load]`,
   5 dwords, `0x14` apart. `tools/ResolveVtableTypeNames.java` read the MSVC
   type descriptor at `vtable-4` for all 75 vtables, giving the **class name**.
   Every one resolved; none is a guess.
3. `tools/DumpDisassemblyRange.java` dumped `0x00431b00..0x0043e700`. Each
   slot-1 apply body was walked to its terminating write, giving the
   **record offset**.
4. Closure check: `data/default physics.dat` was parsed independently (below)
   and every value id it actually uses was checked against the factory maps.

Ghidra was used strictly read-only (`-readOnly`). Nothing was renamed,
retyped, or written to the maintainer database; no backup was taken because no
mutation was attempted.

## 2. The `.dat` container, decoded and closed

`local-lab/safe-copy-bea-pristine/data/default physics.dat`,
sha256 `e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`,
175,603 bytes.

```
file      := u16 0x0012 , statement*
statement := u32 tag , u32 declaredSize , cstring name , node*
node      := u32 valueId , u32 payloadLen , payloadLen bytes , u32 link
             link == 0x00000000 -> another node follows
             link == 0xFFFFFFFF -> end of this statement
```

Parsing on the `link` sentinel rather than `declaredSize` consumes
**777 statements** and 175,599 of 175,603 bytes (a trailing 4-byte sentinel is
left). 777 is exactly the record count previously reported for this file.
`declaredSize` is *not* a whole-body length for every statement — the walk
diverges first at `0x0000b078` (`Flamethrower`, declared `0x82`) — so a decoder
must not trust it.

The two anchor offsets in the prior assessment fall out of this parse
unchanged: `Mech Bullet` at `0xA3F2`, `Mech Pulse Bolt Medium` at `0xAC16`.

Statement tag → value factory (established by id-set closure, not by guessing
an offset rule):

| tag | count | factory | statement |
| ---: | ---: | --- | --- |
| 1 | 160 | Type2 | Unit |
| 2 | 139 | Type3 | Weapon |
| 3 | 145 | Type4 | WeaponMode |
| 4 | 91 | Type5 | Round |
| 5 | 38 | Type6 | Spawner |
| 6 | 118 | Type7 | Explosion |
| 7 | 39 | Type10 | Component |
| 8 | 43 | Type8 | Feature |
| 9 | 4 | Type9 | Hazard |

**Closure result: across all 777 statements, every value id used by the file is
covered by the corresponding factory's case list. Unknown ids: 0.** Note the
tag→factory mapping is *not* a uniform `tag+1`: tags 7/8/9 are
component/feature/hazard, not feature/hazard/component.

## 3. Round value ids (statement tag 4, factory `0x00437490`)

Record size `0xa8`. Record name lives at `+0x18` (read by every apply body's
`MOV ESI, dword ptr [EDI + 0x18]` name compare).

| id | RTTI class | vtable | apply body | writes |
| ---: | --- | --- | --- | --- |
| `0x01` | `CRoundLifeSpan` | `0x005da570` | `0x004382e0` | `+0x24` |
| `0x02` | **`CRoundDamage`** | `0x005da548` | `0x004381b0` | `+0x1c` |
| `0x03` | **`CRoundVelocity`** | `0x005da55c` | `0x00438370` | `+0x2c` |
| `0x04` | `CRoundSeek` | `0x005da534` | `0x004394e0` | `+0x48` (nested) |
| `0x05` | `CRoundTurnRate` | `0x005da520` | `0x00438420` | `+0x28` |
| `0x06` | `CRoundGravity` | `0x005da50c` | `0x004384b0` | `+0x3c` (FSTP `0x00438540`) |
| `0x07` | `CRoundBounce` | `0x005da4f8` | `0x00438550` | `+0x30` |
| `0x08` | `CRoundEffect` | `0x005da4e4` | `0x00439710` | `+0x10` owned string |
| `0x09` | `CRoundExplosion` | `0x005da4bc` | `0x00439910` | `+0x08` owned string |
| `0x0a` | `CRoundSeekDelay` | `0x005da4a8` | `0x004388f0` | `+0x34` |
| `0x0b` | `CRoundWiggle` | `0x005da480` | `0x00438680` | `+0x38` |
| `0x0c` | `CRoundRadius` | `0x005da3a4` | `0x004385e0` | `+0x8c` |
| `0x0d` | `CRoundFlak` | `0x005da46c` | `0x00438710` | `+0x4c` |
| `0x0e` | `CRoundFlakInaccuracy` | `0x005da458` | `0x004387b0` | `+0x7c` (FSTP `0x00438840`) |
| `0x0f` | `CRoundSeekAngle` | `0x005da494` | `0x00438a20` | `+0x40` |
| `0x10` | `CRoundBeam` | `0x005da444` | `0x00438850` | `+0x50` |
| `0x11` | `CRoundSoundMaterial` | `0x005da430` | `0x00438100` | `+0x80` |
| `0x12` | `CRoundWeirdoSeek` | `0x005da41c` | `0x00439440` | `+0x54` |
| `0x13` | `CRoundRearm` | `0x005da408` | `0x00438240` | `+0x20` (FSTP `0x004382d0`) |
| `0x14` | `CRoundBasedOn` | `0x005da3f4` | `0x00437d00` | bulk field copy from source round |
| `0x15` | `CRoundSeekTerminationTime` | `0x005da3e0` | `0x00438ab0` | `+0x44` |
| `0x16` | `CRoundMissile` | `0x005da2c8` | `0x00438e10` | `+0x70` flag |
| `0x17` | `CRoundProximity` | `0x005da3cc` | `0x00438980` | `+0x88` |
| `0x18` | `CRoundGridOfFear` | `0x005da3b8` | `0x00438b40` | `+0x58` |
| `0x19` | `CRoundUnderWater` | `0x005da390` | `0x00438bf0` | `+0x5c` |
| `0x1a` | `CRoundGroundHugging` | `0x005da37c` | `0x00438ca0` | `+0x68` |
| `0x1b` | `CRoundPassiveCollision` | `0x005da354` | `0x00439050` | `+0x64` |
| `0x1c` | `CRoundJumps` | `0x005da340` | `0x00439100` | `+0x84` |
| `0x1d` | `CRoundJumpRange` | `0x005da32c` | `0x004391b0` | `+0x90` |
| `0x1e` | `CRoundJumpDelay` | `0x005da318` | `0x00439250` | `+0x94` |
| `0x1f` | `CRoundExplode` | `0x005da304` | `0x00439390` | `+0x74` flag |
| `0x20` | `CRoundTorpedo` | `0x005da368` | `0x00438d50` | `+0x6c` flag |
| `0x21` | `CRoundWaterEffect` | `0x005da4d0` | `0x00439800` | `+0x14` owned string |
| `0x22` | `CRoundFire` | `0x005da2f0` | `0x00438ed0` | `+0x60` flag |
| `0x23` | `CRoundTreeCollision` | `0x005da2dc` | `0x00439a00` | `+0xa4` (nested) |
| `0x24` | `CRoundMesh` | `0x005da2b4` | `0x00439620` | `+0x0c` owned string |
| `0x25` | `CRoundSmart` | `0x005da2a0` | `0x00438f90` | `+0x78` flag |
| `0x26` | `CRoundLength` | `0x005da28c` | `0x004392f0` | `+0x98` |

The four string ids independently reproduce the four offsets already recorded
in [`functions/CPhysicsScriptStatements.cpp.md`](functions/CPhysicsScriptStatements.cpp.md)
(`CRoundExplosion +0x8`, `CRoundMesh +0xc`, `CRoundEffect +0x10`,
`CRoundWaterEffect +0x14`), as do `CRoundSeek +0x48`, `CRoundTreeCollision +0xa4`
and `CRoundGridOfFear +0x58`. That is four/three independent agreements with
work done by a different method on a different day.

### 3.1 The layout is corroborated by the live projectile class

`CRound` (the runtime projectile actor) holds its round-definition record at
`this+0xf0` (`CRound__ctor 0x004d81e0`, `CRound__Init 0x004d8410`). The reads
off that pointer line up with the table above:

- `CRound__ArmProjectileAndSpawnTrailEffect` (`0x004db630`):
  `*(float *)(*(int *)(this + 0xf0) + 0x2c) * _DAT_005d8584` scales the
  normalised velocity vector — `+0x2c` **is** the speed term.
- `CRound__SpawnConfiguredProjectile` (`0x004db150`) copies `config+0x24`
  (`CRoundLifeSpan`) into the init payload and later compares a squared
  distance against `lifeSpan * speed` — a time × speed = range product.
- `CRound__SetTargetReaderIfAllowed` (`0x004daab0`) and
  `CRound__SelectBestTargetReaderAndSyncAimState` (`0x004dac90`) both gate
  target acquisition on `config+0x48 != 0 || config+0x1c < 0.0`, i.e. on
  `CRoundSeek` or on **negative `CRoundDamage`** — the repair-weapon case
  (`Repair Pulse Gun` exists in the same file).
- `CRound__Init` branches on `config+0x50` (`CRoundBeam`), `+0x6c`
  (`CRoundTorpedo`), `+0x70` (`CRoundMissile`), `+0xa0`, `+0xa4`
  (`CRoundTreeCollision`), `+0x8c` (`CRoundRadius`), `+0x98` (`CRoundLength`),
  `+0x58` (`CRoundGridOfFear`). Every one of those is a flag/scalar in the
  table above and is used flag-like or scalar-like accordingly.

### 3.2 `CRound` primary virtual surface

The strict `CRound` vtable at `0x005DE82C`, the matching inherited slots in
`CMissile` at `0x005E3BA4`, and the retained `CThing`/`CComplexThing`/`CActor`
virtual declaration order resolve fifteen formerly generic slots as one coherent
runtime surface. The names below identify the inherited virtual operation; they
do not assert that the stripped retail linker retained an original symbol.

| slot | retail -> PC demo | resolved operation | bytes | bounded retail contract |
| ---: | --- | --- | ---: | --- |
| 0 | `0x004D9910` -> `0x004D97F0` | `CRound__HandleEvent` | 1,078 | Switches on `event+4`: 4000 creates/schedules the configured launch path, 4001 updates impact state and conditionally dies, 4002 spawns the configured projectile then clears `+0x120` and dies, 4003 selects/synchronizes the target reader; other events delegate to `CActor::HandleEvent`. |
| 2 | `0x004D8DC0` -> `0x004D8CA0` | `CRound__Shutdown` | 121 | Removes optional grid-of-fear/reader registrations, clears the particle/effect link and active reader, then delegates to `CComplexThing::Shutdown`. |
| 7 | `0x004D8290` -> `0x004D8170` | `CRound__GetClassNameString` | 6 | Returns the literal class string `CRound`; the independently linked demo returns the same string from its relocated address. |
| 15 | `0x004D82A0` -> `0x004D8180` | `CRound__GetMaxVelocity` | 43 | Calls the round's gravity virtual; returns `160.0f` when gravity is nonzero, otherwise returns configured `CRoundVelocity` from `roundConfig+0x2c`. |
| 16 | `0x004D8AC0` -> `0x004D89A0` | `CRound__GetRadius` | 28 | Returns `CRoundRadius + CRoundVelocity * 0.05f * 0.5f`: the authored radius plus half of one established 20 Hz movement step. |
| 38 | `0x004D8320` -> `0x004D8200` | `CRound__SetThingType` | 15 | Stores the caller mask OR `0x80000007`, retaining the inherited thing/complex-thing/actor bits plus the ammunition bit. |
| 43 | `0x004D8340` -> `0x004D8220` | `CRound__GetSoundMaterial` | 13 | Returns `roundConfig+0x80`, the independently resolved `CRoundSoundMaterial` field. |
| 44 | `0x004D82E0` -> `0x004D81C0` | `CRound__ClipToGround` | 63 | Returns true when bounce or gravity is nonzero, or turn rate is positive; otherwise false. |
| 45 | `0x004DB600` -> `0x004DB4E0` | `CRound__Gravity` | 40 | Returns zero for the active torpedo-state branch; otherwise returns `CRoundGravity * 0.025f`. |
| 47 | `0x004D82D0` -> `0x004D81B0` | `CRound__BounceFactor` | 10 | Returns `roundConfig+0x30` (`CRoundBounce`). |
| 49 | `0x004D8330` -> `0x004D8210` | `CRound__CanGoUnderWater` | 10 | Returns `roundConfig+0x5c` (`CRoundUnderWater`). |
| 50 | `0x004DB130` -> `0x004DB010` | `CRound__StartDieProcess` | 18 | Delegates to `CComplexThing::StartDieProcess` only while `this+0x120` is clear; otherwise returns false. |
| 66 | `0x004D8E40` -> `0x004D8D20` | `CRound__Move` | 2,757 | Owns per-tick beam/round movement, target-relative and velocity/config branches, transform-history updates, effect transforms, reader cleanup, and contact/lifetime dispatch. Individual branch semantics remain bounded to the visible fields and callees. |
| 68 | `0x004D9DD0` -> `0x004D9CB0` | `CRound__DeclareOnGround` | 282 | Bouncing rounds delegate to `CActor::DeclareOnGround`; a non-bouncing, non-fire round traces/corrects the ground contact, applies effect mode 1, then enters the virtual death path. |
| 69 | `0x004D9EF0` -> `0x004D9DD0` | `CRound__DeclareInWater` | 60 | Arms the projectile/trail link and updates the `+0xd0` timestamp; when neither underwater nor torpedo behavior is configured, applies effect mode 2 then enters the virtual death path. |

The independent input is the 2,510,848-byte PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`;
the retail baseline remains
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
For all twelve bodies, complete x86-32 decoding produced the same instruction
count, offsets, sizes, mnemonics, register forms, relative branches, and literal
constant shapes. Normalizing only relocated address/displacement encodings left
zero instruction differences. The demo thus independently corroborates the
entire interface, not just a shared RTTI label.

Retail body SHA-256 pins, in the table's address order:

```text
004d9910 d54da932205b40f631e650c2f3902faa230f69c1efe029c428aff1305cff2c2b
004d8dc0 6115be53ac54c0be415084c24c4b40bf6b8c8e68b67f2f2e96e28feeeaeb45ed
004d8290 b255442129093c839144a11c6315d0c555714f692cb71fd92c9342397bdf8b6d
004d82a0 ba0fab8d92af843dba3b9c5f1211ddd201ec160e393f36a42458602847c13b4d
004d8ac0 c986f432cbada785b922a589cef8b7ed95fe96df48d1cb41090a06326e6e9382
004d8320 6ecb411d5107118adc9f1069e90032b6493f6678cd462e47928f644174622d98
004d8340 3f59723d13c058fc8da764b0c39e4e3724e16109ceec8b0b8d9720d03aa46e2b
004d82e0 e43a75c9c1a2cdb47bb5429f5d7a125e40bc2916ae9a7efee9502459ffd475eb
004db600 7f549e893dcde13ddd86f75f080144f76b173910a0d4dea4153b0007134bb967
004d82d0 768a01e896e2198144e55e39b47aa9bcd771e8fd6dc1f1eb9dd8c2ec61e47732
004d8330 c53cb3534a10d96d95d69e776931bb1e999f75ce32548c4a7e17faa8d897e6e5
004db130 7e2fbd18483548889909606c71d115fa6f162daa4fc9e0232939af06655cb1f6
004d8e40 819f5211e6e246292a3f0a9bbfa60b712711d7c8ded288d26e08734a88071638
004d9dd0 bdd3b27c15a77fe7a964a5c37fa3b055b3eb7c449c7f0944d2eeba7f504421f9
004d9ef0 cca25281f2ca91e693706e799be2672bd435992e7ed85329ba1f41bda019aacb
```

### 3.2.1 Generation-21 slot-66 runtime placement

Two retained retail trace sessions independently reach `0x004D8E40` through
the inherited actor slot-66 dispatcher at `0x00401AEA`. Level 522 contributes
231 call-entry pairs over 21 session-local receivers; Level 741 contributes
7,282 over 50 session-local receivers. All 7,513 calls use strict `CRound`
vtable `0x005DE82C`, with call `ECX=ESI` continuing unchanged into entry
`ECX/ESI`. All 7,513 raw callbacks land at the function's `RET` at
`0x004D9904`; 7,204 form gap-free return envelopes and 309 remain raw orphans
across trace-continuity barriers. No call uses the shared `CMissile`-style
vtable `0x005E3BA4`.

Discovery and exact replay projections agree for both sessions. A poisoned
Level-522 replay requiring 232 calls against the unchanged 231-call event
stream exits 10, fails the expectation/pairing/collector gates, and publishes
no READY. The proof therefore promotes only the observed strict-`CRound`
placement and receiver-preserving call envelope. It does not measure receiver
writes, discriminate internal branches, establish a semantic return value,
observe `CMissile` placement, prove the shipped source spelling, or claim full
Move/contact/lifetime/effect behavior. Generation 21 retains the saved campaign
name `VFuncSlot_66_004d8e40`; no live Ghidra or executable mutation occurred.

### 3.3 Construction, targeting, and launch helpers

The same class/data join closes thirteen adjacent lifecycle and launch bodies.
Unlike the inherited virtual names in Section 3.2, some helper names here are
descriptive semantic labels recovered from their callers and visible state
changes rather than claimed original source symbols.

| retail -> PC demo | function | bytes | bounded contract |
| --- | --- | ---: | --- |
| `0x004D81E0` -> `0x004D80C0` | `CRound__ctor` | 164 | Constructs the complex/actor bases, installs the `CRound` primary/render tables, links the effect handle, stores round data at `+0xf0`, seeds time/state fields, and clears reader/launch fields. |
| `0x004D8350` -> `0x004D8230` | `CRound__scalar_deleting_dtor` | 32 | Calls the teardown body, conditionally frees on deleting-destructor flag bit 0, and returns the receiver. |
| `0x004D8370` -> `0x004D8250` | `CRound__ShutdownAndDetachReaders` | 151 | Detaches both reader cells, removes the particle/effect owner link, then destroys the actor base. |
| `0x004D8410` -> `0x004D82F0` | `CRound__Init` | 1,591 | Copies round-init aim/data fields, selects beam versus ordinary collision setup, initializes `CActor`, schedules event 4000, registers optional fear-grid tracking, and starts target selection. |
| `0x004D8A50` -> `0x004D8930` | `CCollisionSeekingRound__scalar_deleting_dtor` | 32 | Runs the collision-seeking-round teardown and conditionally frees the object. |
| `0x004DAAB0` -> `0x004DA990` | `CRound__SetTargetReaderIfAllowed` | 159 | Gates target assignment on seek/negative-damage configuration, optionally removes the old reader, binds the new reader, and updates the global tracked-round set. |
| `0x004DAB50` -> `0x004DAA30` | `CRound__RemoveActiveReaderById` | 77 | Removes owner-monitor/global-set registrations and clears the active target reader. |
| `0x004DABA0` -> `0x004DAA80` | `CRound__FindNearbyHostileWithinProjectileRadius` | 240 | Scans MapWho within `CRoundJumpRange`, rejects the current target and flag-ineligible entries, and returns the first candidate whose center lies inside the configured radius. |
| `0x004DAC90` -> `0x004DAB70` | `CRound__SelectBestTargetReaderAndSyncAimState` | 852 | Scores eligible readers in round-local aim space, applies seek-angle/polarity and allegiance gates, binds the best reader, writes aim state, and schedules event 4003. |
| `0x004DAFF0` -> `0x004DAED0` | `FearGridTrackedObject__LookupFearWeightByArchetype` | 152 | Matches the tracked object's round-data name against the preset list and returns entry scalar `+0x34`, otherwise zero/default. |
| `0x004DB090` -> `0x004DAF70` | `CRound__GetPresetScalarByConfigName` | 152 | Performs the parallel name lookup and returns entry scalar `+0x38`, otherwise zero/default. |
| `0x004DB150` -> `0x004DB030` | `CRound__SpawnConfiguredProjectile` | 1,185 | Chooses a nearby target or randomized ground point, creates the configured projectile, builds its round-init payload, and dispatches its init virtual. |
| `0x004DB630` -> `0x004DB510` | `CRound__ArmProjectileAndSpawnTrailEffect` | 541 | For the unarmed torpedo branch, marks launch state, clamps height, normalizes/scales velocity from `CRoundSpeed`, replaces the effect link, creates the configured trail, and synchronizes its transform/time. |

All thirteen independently linked demo bodies again decode with identical
instruction boundaries, mnemonics, operands after relocation normalization,
and zero normalized differences. Exact retail ranges and body SHA-256 values
are retained in
`local-lab/console-output-topology-v2-ready/inputs/ghidra-body-ranges.tsv`;
the bounded decompiles are in W006/W007 under
`local-lab/ghidra-fullpass-2026-07-23/exports/`.

## 4. Weapon-mode value ids (statement tag 3, factory `0x00435010`)

Record size `0xc0`. Record name at `+0x30`.

| id | RTTI class | vtable | apply body | writes |
| ---: | --- | --- | --- | --- |
| `0x01` | `CWeaponInaccuracy` | `0x005da250` | `0x00435cd0` | `+0x34` |
| `0x02` | `CWeaponRound` | `0x005da1ec` | `0x004370a0` | round reader/index |
| `0x03` | **`CWeaponReloadTime`** | `0x005da200` | `0x004365f0` | `+0x38` |
| `0x04` | `CWeaponBurstSize` | `0x005da23c` | `0x00435ff0` | `+0x44` |
| `0x05` | `CWeaponBurstDelay` | `0x005da228` | `0x004360a0` | `+0x3c` |
| `0x06` | `CWeaponMuzzleEffect` | `0x005da1d8` | `0x00436410` | `+0x1c` owned string |
| `0x08` | `CWeaponLaunchSequence` | `0x005da1c4` | `0x00435a00` | list append |
| `0x09` | `CWeaponMinRange` | `0x005da19c` | `0x00436800` | `+0x74` |
| `0x0a` | `CWeaponMaxRange` | `0x005da188` | `0x00436890` | `+0x78` |
| `0x0b` | `CWeaponMinDeflection` | `0x005da174` | `0x00436920` | `+0x7c` |
| `0x0c` | `CWeaponMaxDeflection` | `0x005da160` | `0x004369b0` | `+0x80` |
| `0x0d` | `CWeaponPreFireDelay` | `0x005da138` | `0x004361e0` | `+0x88` |
| `0x0e` | `CWeaponPostFireDelay` | `0x005da124` | `0x00436280` | `+0x8c` |
| `0x0f` | `CWeaponClip` | `0x005da0fc` | `0x00436500` | `+0x00` owned string |
| `0x10` | `CWeaponLockTime` | `0x005da0e8` | `0x00436c10` | `+0x94` |
| `0x11` | `CWeaponLockDeflection` | `0x005da0d4` | `0x00436cb0` | `+0x98` |
| `0x12` | `CWeaponPreFireEffect` | `0x005da110` | `0x00436320` | `+0x20` owned string |
| `0x13` | `CWeaponLockMode` | `0x005da0c0` | `0x00436d50` | `+0xa8` |
| `0x14` | `CWeaponLockUnit` | `0x005da0ac` | `0x00436df0` | `+0xa4` |
| `0x15` | `CWeaponLockRange` | `0x005da098` | `0x00436e90` | `+0x9c` |
| `0x16` | `CWeaponMaxLocks` | `0x005da070` | `0x00436fd0` | `+0x90` |
| `0x17` | `CWeaponLockRadius` | `0x005da084` | `0x00436f30` | `+0xa0` |
| `0x18` | `CWeaponLaunchSound` | `0x005da048` | `0x004371c0` | `+0x24` owned string |
| `0x19` | `CWeaponBasedOn` | `0x005da00c` | `0x00435840` | bulk field copy |
| `0x1a` | `CWeaponMinTargetHeight` | `0x005d9ff8` | `0x00436a50` | `+0x6c` |
| `0x1b` | `CWeaponMaxTargetHeight` | `0x005d9fe4` | `0x00436ae0` | `+0x70` |
| `0x1c` | `CWeaponVolleySize` | `0x005da214` | `0x00436130` | `+0x48` |
| `0x1d` | `CWeaponTrack` | `0x005d9fd0` | `0x00436680` | `+0xac` |
| `0x1e` | `CWeaponYawTolerance` | `0x005da14c` | `0x00436b70` | `+0x84` |
| `0x1f` | `CWeaponLaunchAngle` | `0x005da1b0` | `0x00435b50` | angle triple, list-backed |
| `0x20` | `CWeaponPower` | `0x005d9fbc` | `0x00435d60` | `+0x40` |
| `0x21` | `CWeaponPredictive` | `0x005da264` | `0x00435f30` | `+0xb0` flag |
| `0x22` | `CWeaponPreFireSound` | `0x005da034` | `0x004372b0` | `+0x28` owned string |
| `0x23` | `CWeaponSoundPerBurst` | `0x005da05c` | `0x00436740` | `+0xb4` |
| `0x24` | `CWeaponPostFireSound` | `0x005da020` | `0x004373a0` | `+0x2c` owned string |
| `0x25` | `CWeaponMuzzleLight` | `0x005d9fa8` | `0x00435df0` | `+0xb8` |
| `0x26` | `CWeaponMuzzleLightRadius` | `0x005d9f94` | `0x00435e90` | `+0xbc` |

Independent agreements with the existing function map: `CWeaponVolleySize +0x48`,
`CWeaponMuzzleEffect +0x1c`, `CWeaponPreFireEffect +0x20`,
`CWeaponLaunchSound +0x24`, `CWeaponPreFireSound +0x28`,
`CWeaponPostFireSound +0x2c`, and `CWeaponLaunchAngle` as a three-float value.

**Weapon-mode value id 3 is `CWeaponReloadTime`.** The open question in the
prior assessment is answered.

## 5. Explosion and weapon value ids (by-product, complete)

Explosion (statement tag 6, factory `0x0043a860`), record `0x50`:

| id | class | writes | id | class | writes |
| ---: | --- | --- | ---: | --- | --- |
| `0x01` | `CExplosionBasedOn` | copy | `0x09` | `CExplosionTime` | `+0x40` |
| `0x02` | `CExplosionAirEffect` | `+0x18` str | `0x0a` | `CExplosionSound` | `+0x28` str |
| `0x03` | `CExplosionRadius` | `+0x34` | `0x0b` | `CExplosionSmart` | `+0x44` |
| `0x04` | **`CExplosionDamage`** | `+0x38` | `0x0c` | `CExplosionLight` | `+0x4c` |
| `0x05` | `CExplosionGroundEffect` | `+0x20` str | `0x0d` | `CExplosionOriented` | `+0x48` |
| `0x06` | `CExplosionWaterEffect` | `+0x1c` str | `0x0e` | `CExplosionShockwave` | shared no-op slot |
| `0x07` | `CExplosionUnitEffect` | `+0x24` str | `0x0f` | `CExplosionWaterSound` | `+0x2c` str |
| `0x08` | `CExplosionVolumetric` | `+0x3c` | | | |

This reproduces the seven offset-only scalar rows already in the function map
(`+0x34 +0x38 +0x3c +0x40 +0x44 +0x48 +0x4c`) and names all seven.

Weapon (statement tag 2, factory `0x00434300`), ids `0x1..0xe`:
`CWeaponChargeLevel`, `CWeaponChargeRate`, `CWeaponAmmoStore`,
`CWeaponConsumption`, `CWeaponIconName`, `CWeaponSmart`, `CWeaponAdjustAim`,
`CWeaponZoomMode`, `CWeaponAllowMovement`, `CWeaponPlacement`,
`CWeaponLanguageName`, `CWeaponVersusInfantry`, `CWeaponVersusTanks`,
`CWeaponVersusAir`. `CWeaponChargeLevel`'s payload is `[i32 chargeLevel][cstring weaponModeName]`.

## 6. Applying this to the two open Level 100 questions

### 6.1 Which round does the tutorial Pulse Cannon actually fire

Chain read straight out of the `.dat`:

```
weapon      Pulse Cannon Pod @0x17463
              CWeaponChargeLevel = 0 -> "Mech Pulse Cannon Charged"
              CWeaponChargeLevel = 1 -> "Mech Pulse Cannon Charged 2"
weaponmode  Mech Pulse Cannon Charged @0x134e3
              CWeaponReloadTime = 0.1
              CWeaponRound      = "Mech Pulse Bolt Medium"
              CWeaponPower      = 0.03
round       Mech Pulse Bolt Medium @0xac16
              CRoundVelocity = 35.0
              CRoundDamage   = 0.8
              CRoundLifeSpan = 6.0
              CRoundExplosion= "Mech Pulse Hit Medium"
              CRoundRadius   = 0.07
              CRoundExplode  = 1
explosion   Mech Pulse Hit Medium @0x4718
              CExplosionRadius = 0.5
              CExplosionDamage = 1.0
```

This chain was derived, not assumed, and it is confirmed from the other end by
an existing measurement: `SimulationConstants.ProjectileSpeedPerTick` records
that fresh copied-Steam Level 100 runs saw pulse rounds carrying "definition
speed 35" and moving 1.75 units per 20 Hz update. `35 / 20 = 1.75` exactly.

Two consequences follow immediately and are worth stating separately from the
hypothesis below:

- **`CRoundVelocity` is in units per second, and the released simulation runs
  at 20 Hz.** This is a measured 1.75-units-per-update datum divided by a
  byte-read 35.0, not an inference from naming.
- Therefore the `.dat`'s other time-dimensioned fields are seconds.
  `CWeaponReloadTime` `0.1 s` for the tutorial pulse is **2 released updates**
  per shot. The prior assessment's arithmetic ("3 ticks at 30 Hz") assumed a
  30 Hz released tick; the released rate here is 20 Hz.
  `reverse-engineering/game-mechanics/fire-cooldown-retail-to-core-translation-policy.md`
  remains the owner of what Core should do with that; this document does not
  claim `FireCooldownTicks` should be any particular value.

Twin Vulcan, for the P0 gap:

```
weapon      Mech Twin Vulcan Cannon @0x171b4  CWeaponConsumption 2.0
weaponmode  Mech Twin Vulcan Cannon @0x13360
              CWeaponInaccuracy = 0.006981317   (= 0.4 degrees, radians)
              CWeaponReloadTime = 0.05          (1 released update at 20 Hz)
              CWeaponVolleySize = 4
              CWeaponRound      = "Mech Bullet"
              CWeaponPredictive = 1
round       Mech Bullet @0xa3f2
              CRoundVelocity = 60.0   CRoundDamage = 0.08
              CRoundLifeSpan = 1.0    CRoundExplosion = "Mech Bullet Hit"
explosion   Mech Bullet Hit @0x4373
              CExplosionRadius = 0.2  CExplosionDamage = 0.001
```

That is the released rate/damage/spread evidence the P0 item was waiting on.
`CWeaponInaccuracy 0.006981317 rad` is `0.4°` to seven digits, which is a
strong indication the inaccuracy unit is radians; the Mech Pulse Cannon's
`0.008726646` is `0.5°` on the same reading.

### 6.2 The `0.8 + 1.0 = 1.8` chain: conditional same-receiver path closed

Status: **retail `CRound::Hit` creates the configured `CExplosion`; the small
explosion registers and scans synchronously during initialization, reaches
`CExplosion::Hit` on the surviving original receiver when the explicit filters
pass, and composes the two authored values.**

What changed:

- Both addends are now RTTI-named damage fields on the exact two records the
  tutorial pulse uses: `CRoundDamage = 0.8` on `Mech Pulse Bolt Medium`,
  `CExplosionDamage = 1.0` on `Mech Pulse Hit Medium`. They are no longer
  "field 2" and "field 4".
- The identification of *which* round is involved is independent of the damage
  numbers: it comes from the `CWeaponChargeLevel` chain and is confirmed by the
  separately measured speed 35.
- Against the recorded measurements (direct hit removes 1.8, glancing part hit
  removes 1.0), the three simplest models score:
  - round damage only → predicts 0.8. **Killed.**
  - explosion damage only → predicts 1.0 for a direct hit. **Killed.**
  - round damage to the struck part + explosion damage to the body → predicts
    1.8 direct and 1.0 glancing. **Both measurements survive.**

Resolved on 2026-08-10: [`CRound::Hit @ 0x004D8AE0`](cround-hit-damage-path-2026-08-10.md)
loads `roundData+0x1C` at `0x004D8CE3` and passes it as the first argument to
the struck thing's slot-40 `Damage` call at `0x004D8CEF`. The joined
RTTI/apply-body table identifies that field as `CRoundDamage`; two replicated
Level-521 observations preserve the same callsite and raw `0.05f` carrier.
This kills the old concern that no round-damage consumer had been located.

The same 2026-08-10 pass resolves the explosion consumer. `CExplosion::Hit`
at `0x0044BF10` reads configured `CExplosionDamage` from `config+0x38` and
dispatches target slot-40 `Damage` with radial falloff. For radius `R`,
effective distance `d`, damage `D`, and explosion time `T`, retail computes
`((R-d)*D)/R` when `R <= 3`, otherwise
`((R-d)*(D/T))/R`. The body is independently instruction-identical in the
distinct PC demo after relocation normalization.

The missing factory join is now resolved. `CRound::Hit` passes mode `3` to
`CRound::ProcessImpactExplosionAndEffects`; jump-table mode 3 reaches
`0x004DA502`, reads `CRoundExplosion` from `roundData+0x08`, resolves its
ordinal in `DAT_008553F8`, calls
`CWorldPhysicsManager::CreateExplosion` at `0x004DA521`, and invokes the new
object's slot-9 `CExplosion::Init` at `0x004DA670`.

The post-factory edge is now resolved too. Mode 3 constructs a source-shaped
`CExplosionInitThing` with `mColType = kCollideThing`, null `mAttachedTo`, and
false `mUseAttachedRadius`. `CExplosion::Init` therefore does not ignore the
original target by attachment identity. It installs a passive immediate
collision configuration and, for `R <= 3`, makes the full configured radius
live before inherited `CThing::Init` runs.

`CThing::InitCollisionSeekingThing` allocates `CCSPersistentThing`; its slot-3
initializer retains ready bit `0x400` because `mStartCollideOnNextFrame` is
false and immediately scans the surrounding 3x3 MapWho sectors. The pair
dispatcher handles an existing overlap synchronously. Persistent slot 6 then
resolves the pair and invokes owner slot 39 (`Hit`) on both sides, one of which
is the new `CExplosion`. For tutorial radius `0.5`, the target-surface distance
clamps to zero and the radial arm supplies the full `1.0` when the mutual
thing-flag and smart/allegiance filters pass. The Target Drone remains alive
after direct `0.8` against life `1.0`; the prior measured direct loss of `1.8`
independently corroborates that its released path passes those filters.

The Twin Vulcan pair remains a useful optional runtime corroborator:
`0.08 + 0.001` predicts `0.081`, while round-only predicts `0.08` and
explosion-only predicts `0.001`. It is no longer needed to discover the static
same-receiver dispatch mechanism. `Mech Pulse Bolt Small` remains a control in
the other direction: `CRoundDamage 1.5` with `CExplosionDamage 0.0`.

Note also that `Mech Pulse Bolt Small` is **not** the tutorial round, despite
`Mech Pulse Cannon` (the mode that fires it) having a very similar name. Any
future measurement must go through `Pulse Cannon Pod`.

## 7. What I could not resolve

- **The second damage call's exact mesh part and runtime trace.** Section 6.2
  closes the static same-receiver order for immediate small explosions. A
  copied-runtime trace would corroborate both slot-40 calls and identify the
  precise per-part report selection; expanding `R > 3` timing remains separate.
- **Units for non-time scalars.** Seconds is established for time via the
  20 Hz/1.75 datum, and radians is strongly indicated for `CWeaponInaccuracy`
  by the exact 0.4°/0.5° values, but no measurement pins `CRoundDamage`,
  `CWeaponPower`, `CExplosionRadius`, or `CRoundRadius` to a world unit. The
  names say what the fields *are*; they do not say what one unit of them is.
- **Four record offsets, deliberately.** `CWeaponRound` (`M 0x02`),
  `CWeaponLaunchSequence` (`M 0x08`), `CWeaponLaunchAngle` (`M 0x1f`),
  `CRoundBasedOn` (`R 0x14`) and `CWeaponBasedOn` (`M 0x19`) do not write one
  fixed scalar slot — they resolve an index through a global list, append to a
  list, or bulk-copy a source record. Reducing them to a single "+offset" would
  be wrong, so they are recorded as what they are.
- **`CExplosionShockwave` (`T7 0x0e`).** Its vtable slot 1 points at the shared
  no-op `0x004014c0`, so the class exists and is named but applies nothing to
  the explosion record in this build. Not a failure to resolve — a real
  negative.
- Unit (`Type2`, 69 ids), spawner (`Type6`), feature, hazard, component,
  seek, behaviour, alligence, navmap and state factories were resolved to RTTI
  class names as part of the closure check but their record offsets were not
  transcribed here; the raw export is listed below and the work is
  mechanical.

## 8. Reproduction

Read-only, from this repository, with the maintainer Ghidra project closed:

```
analyzeHeadless.bat C:\Users\david\Ghidra\Projects BEA -process BEA.exe \
  -noanalysis -readOnly -scriptPath tools \
  -postScript ExportFunctionsByAddressDecompile.java <addrs> <outdir> 120
analyzeHeadless.bat ... -postScript ResolveVtableTypeNames.java <vtables> <out.tsv>
analyzeHeadless.bat ... -postScript ExportVtableSlots.java <vtables> <out.tsv> 5
analyzeHeadless.bat ... -postScript DumpDisassemblyRange.java 0x00431b00 0x0043e700 <out.tsv>
```

Consolidated id/class/offset table and the `.dat` parse output are in the
ignored lab path `local-lab/physics-value-ids-2026-07-25/`.

## Claim boundary

Sections 3–5 are static findings: RTTI type descriptors, vtable slot contents,
source-interface order, apply-body writes in the pristine Steam `BEA.exe`, and
the separately linked PC-demo comparison, cross-checked for completeness against
the shipped `default physics.dat`. They establish class/interface identity,
visible control flow, and which record offsets the named accessors consume. They
do not establish every runtime branch, unit systems beyond the two noted,
gameplay outcomes, or rebuild parity. Section 6.1's 20 Hz / units-per-second
result rests on a previously recorded controlled copied-runtime measurement,
cited inline. Section 6.2 proves the direct round term, configured explosion
creation, immediate collision registration, and conditional same-receiver
additive path; it does not generalize through failed filters, expanding-radius
timing, or rebuild parity.
