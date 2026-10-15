# Weapons of the Battle Engine and its enemies

- **Status:** live preservation record. Weapon names, mode chains, and the
  numeric examples below are measured from the shipped `default physics.dat`
  byte-reads and the resolved value-id tables
  ([physics-round-value-ids-2026-07-25.md](../reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md),
  raw `local-lab/physics-value-ids-2026-07-25/all_ids.tsv`), the pristine-exe
  string table
  ([binary-strings.md](../reverse-engineering/binary-analysis/binary-strings.md)),
  and the pinned source corpus. Faction flavor is carried from
  [world-lore.md](world-lore.md) and marked as fiction. Where this page and a
  measurement disagree, the measurement wins.
- **Last updated:** 2026-08-22
- **Summary:** all 139 literal weapon-record names, the
  weapon → weapon-mode → round → explosion data model that drives them, and
  what the numbers actually say for the two tutorial weapons measured end to
  end.

## How a weapon is built

The game models weapons as a chain of named PhysicsScript records, not as
per-weapon code. The measured chain for any shot is:

```
weapon (statement tag 2)      — the hardpoint: charge levels, ammo, icon,
                                versus-flags, LanguageName for the HUD
  └ weapon-mode (tag 3)       — how it fires: reload, burst, range, lock,
                                which round it launches (CWeaponRound)
      └ round (tag 4)         — the projectile in flight: velocity, damage,
                                lifespan, seek behavior, which explosion
                                it makes on impact (CRoundExplosion)
          └ explosion (tag 6) — the hit: radius, damage, effects, sound
```

Every arrow is a name reference resolved through the PhysicsScript registry
([physics-script-static-contract.md](../reverse-engineering/binary-analysis/physics-script-static-contract.md)):
`CWeaponChargeLevel` maps a charge state to a weapon-mode *name*;
`CWeaponRound` names the round; `CRoundExplosion` names the explosion. The
manager (`CPhysicsScript__Load`, `0x0042e950`) reads all of this from
`data/default physics.dat` at boot.

The measured field vocabulary per layer (all RTTI-resolved, with record
offsets, in the value-id tables):

- **Weapon (tag 2, 14 ids):** `CWeaponChargeLevel`, `CWeaponChargeRate`,
  `CWeaponAmmoStore`, `CWeaponConsumption`, `CWeaponIconName`,
  `CWeaponSmart`, `CWeaponAdjustAim`, `CWeaponZoomMode`,
  `CWeaponAllowMovement`, `CWeaponPlacement`, `CWeaponLanguageName`,
  `CWeaponVersusInfantry`, `CWeaponVersusTanks`, `CWeaponVersusAir`.
  `CWeaponChargeLevel`'s payload is `[i32 chargeLevel][cstring modeName]` —
  this is how one trigger produces different shots at different charge.
- **Weapon-mode (tag 3, 38 ids):** reload time, burst size/delay, volley size,
  min/max range and deflection, lock machinery (`CWeaponLockTime`,
  `CWeaponLockMode`, `CWeaponLockUnit`, `CWeaponLockRange`, `CWeaponLockRadius`,
  `CWeaponMaxLocks`, `CWeaponLockDeflection`), pre/post-fire delays and
  effects, launch sequence/angle/sound, muzzle light, `CWeaponPower`,
  `CWeaponPredictive` (lead-target aiming), `CWeaponTrack`, `CWeaponInaccuracy`.
- **Round (tag 4, 38 ids):** velocity, damage, lifespan, radius, gravity,
  bounce, seek family (`CRoundSeek`, `CRoundSeekAngle`, `CRoundSeekDelay`,
  `CRoundWeirdoSeek`, `CRoundGroundHugging`, `CRoundUnderWater`,
  `CRoundTorpedo`, `CRoundMissile`, `CRoundBeam`, `CRoundFlak`...), tree
  collision, water effects, rearm.
- **Explosion (tag 6, 15 ids):** radius, damage, time, smart flag,
  air/ground/water/unit effects, oriented, shockwave (a real no-op in this
  build — `CExplosionShockwave`'s apply slot points at the shared no-op
  `0x004014c0`), volumetric, light, sounds.

## The measured tutorial pair

Two weapons have been read end-to-end from the shipped `.dat` with every field
byte-identified ([physics-round-value-ids-2026-07-25.md §6](../reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md)):

### Pulse Cannon Pod (world 100's weapon)

```
weapon      Pulse Cannon Pod
              CWeaponChargeLevel 0 → mode "Mech Pulse Cannon Charged"
              CWeaponChargeLevel 1 → mode "Mech Pulse Cannon Charged 2"
mode        Mech Pulse Cannon Charged: reload 0.1 s, power 0.03,
              round "Mech Pulse Bolt Medium"
round       Mech Pulse Bolt Medium: velocity 35.0 u/s, damage 0.8,
              lifespan 6.0 s, radius 0.07, explodes on impact →
explosion   Mech Pulse Hit Medium: radius 0.5, damage 1.0
```

The velocity is not a guess: controlled copied-runtime runs saw pulse rounds
moving 1.75 units per update at the released 20 Hz tick — 35/20 exactly. That
measurement also fixes the unit system: **round velocities are units per
second, reload times are seconds**, and the tutorial pulse fires every 0.1 s =
2 updates.

The damage chain is measured too, including the subtle part: a direct hit
deals round damage **plus** explosion damage to the same receiver
(`CRound::Hit` @ `0x004D8AE0` creates the configured explosion, whose
synchronous scan reaches the original target through the filters) — 0.8 + 1.0
= 1.8 direct, 1.0 glancing. Both numbers were observed before the mechanism
was proven.

### Mech Twin Vulcan Cannon

```
weapon      Mech Twin Vulcan Cannon: consumption 2.0
mode        Mech Twin Vulcan Cannon: inaccuracy 0.006981317 rad (0.4°),
              reload 0.05 s (1 update), volley 4,
              round "Mech Bullet", predictive aiming on
round       Mech Bullet: velocity 60.0 u/s, damage 0.08, lifespan 1.0 s →
explosion   Mech Bullet Hit: radius 0.2, damage 0.001
```

The inaccuracy values being exact degree-converted radians (0.4° and the
pulse's 0.5°) is the evidence that `CWeaponInaccuracy` is in radians.

## The player arsenal

The short names below are shipped HUD/display strings from the pristine string
table, with icon keys alongside. They are not always the same as the exact
PhysicsScript record key; the complete 139-key census follows later.

| Weapon | HUD icon string | Notes |
|---|---|---|
| Pulse Cannon (Pod) | `hud_Pulse_Cannon` (+`_augmented`) | Tutorial weapon; chargeable (2 charge levels measured) |
| Vulcan Cannon | `hud_Vulcan_Cannon` | Twin variant measured end-to-end |
| Rail Gun | `hud_Rail_Gun` (+`_augmented`) | Precision slug; augmented variant exists |
| Beam Laser | `hud_beam_laser` (+`_augmented`) | Continuous beam (`CRoundBeam`) |
| Blaster | `hud_Blaster` | |
| Micro Missile(s) | `hud_Micro_Missiles` | Level-100 jet key is `Missile Pod`; `Micro Missile Launcher` also ships as a weapon key |
| Flux Missile | `hud_Flux_Missile` | Fired from exact weapon key `Flux Pod` |
| Spread Bomb | `hud_Spread_Bomb` | `Spread Pod` / `Spread Bomb Launcher` keys ship |
| Torpedo | `hud_Torpedo_launcher` | `Torpedo Pod` key; `CRoundTorpedo` owns the water path |
| Grenade | `hud_Grenade_launcher` | `Mech Grenade Launcher` key |
| Missile Pod | `hud_` icon set; `"Missile Pod"` string | Pod hardpoint |
| Plasma Cannon | (Forseti-flavor string) | `"Plasma Cannon"` string, 4 xrefs |
| Stream Laser | — | Exact weapon keys are `Stream Laser Pod` and `Stream Laser Pod Aug` |

The `_augmented` HUD variants (`hud_weapon_augmented`,
`hud_Pulse_Cannon_augmented`, `hud_beam_laser_augmented`,
`hud_Rail_Gun_augmented`) are the game telling the player a weapon is in its
boosted state — augmentation is a first-class HUD concept, not a fan term.
`HUD_Weapon_Overheating`, `hud_ammunition_depleted`, `hud_energy_low`, and
`hud_armour_low` complete the weapon-status vocabulary.

Which engines carry which weapons is loadout data
(`BattleEngineConfigurations.cpp` logs `"Loading battle engine configurations"`);
the four-configuration split (Pulsar/Blazer/Lancer/Sniper) and its weapon
assignments are marketing-level facts
([game-overview.md](game-overview.md#battle-engine-types)), not yet bound to
configuration records in this repository.

## Enemy and boss armament

Named strings for boss weapons, each bound to the boss that owns it (see
[units-and-mechs.md](units-and-mechs.md) for the bosses themselves):

| String | Owner |
|---|---|
| `"Thunderhead Main Gun"` | Thunderhead walker boss (episode 3) |
| `"Thunderhead Flamethrower"` | Thunderhead |
| `"Warspite Pulse Laser"` | Warspite battleship (episode 4) |
| `"Fenrir Main Gun"` | Fenrir fortress main gun (component 11) |
| `"Fenrir Bomb Launcher"` | Fenrir bomb bays (components 18-23) |
| `"Fenrir Flamethrower"` | Fenrir |
| `"Sentinel Flamethrower"` | Sentinel (8xx/finale) |
| `"Pulse Cannon Pod"`, `"Vulcan Cannon 1"` | also appear in engine-configuration context |

Flamethrower machinery is shared: the round family carries fire
(`CRoundFire`) and the effect family carries the burn visuals; three separate
bosses reuse it rather than owning three implementations.

The data table adds exact boss/enemy keys beyond those executable strings:
`Carver AAM Launcher`, `Carver Laser Cannon`, `Fenrir Beam Laser`,
`Fenrir Iron Bomb Launcher`, `Gill-M Breath`, `Gill-M Spit`, the five `Hive *`
keys, `Sentinel Main Gun`, `Thunderhead Missile Launcher`, six `Warspite *`
keys, and tentacle beam/pulse lasers. Their presence is a data-record fact, not
proof that every firing path is reachable in normal play.

## Complete named weapon-record census

The pinned `default physics.dat` is 175,603 bytes, SHA-256
`e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`.
The repository's exact framing consumes all 777 statements and encounters
**139 type-2 weapon statements with 139 different literal top-level names**.
The table preserves spelling (including developer spellings such as
`Gattling`). A key shipping in data does not prove campaign reachability, HUD
localization, or a distinct implementation.

| Name 1 | Name 2 | Name 3 | Name 4 |
|---|---|---|---|
| `AA Needle Laser` | `Gattling Cannon` | `Plasma Cannon 1` | `Torpedo Pod` |
| `AAM Launcher` | `Gill-M Breath` | `Plasma Cannon 2` | `Turret Beam Cannon` |
| `AG Needle Laser` | `Gill-M Spit` | `Plasma Grenade Launcher 1` | `Turret Cannon 88mm` |
| `AGM Launcher` | `Gnat Laser` | `Plasma Grenade Thrown` | `Turret Mortar 150mm` |
| `Air Rocket Launcher` | `HE Mine Blast` | `Pulse Cannon 2` | `Turret Mortar Naval` |
| `AMRAAM Launcher` | `Hive Beam Cannon` | `Pulse Cannon Pod` | `Turret Vulcan Cannon` |
| `APC SAT Launcher` | `Hive Beam Cannon Large` | `Pulse Cannon Pod Aug` | `Turret Vulcan Cannon Fenrir` |
| `Arachnadrone Heavy Laser` | `Hive Cannon` | `Pulse Laser 1` | `Turret Vulcan Cannon Naval` |
| `Arachnadrone Laser` | `Hive Machine Gun` | `Pulse Laser 2` | `Twin Assault Pistols` |
| `Assault Rifle` | `Hive Mine Launcher` | `Pulse Rifle` | `Twin Cannon 110mm` |
| `Beam Cannon 1` | `Homing Mine Launcher` | `Pulse Torpedo Launcher` | `Twin Cannon 130mm` |
| `Beam Cannon 2` | `Iron Bomb Launcher` | `Quad AAM Launcher` | `Twin Cannon 88mm` |
| `Beam Rifle` | `IS2 Pulse Cannon` | `Quad AGM Launcher` | `Twin IS2 Pulse Cannon` |
| `Blaster Pod` | `IS3 Pulse Cannon` | `Rail Gun` | `Twin Machine Gun` |
| `Cannon 110mm` | `Light Cannon 88mm` | `Rail Gun Aug` | `Twin Needle Laser` |
| `Cannon 88mm` | `M4 Blaster` | `Repair Pad` | `Twin SAM Launcher` |
| `Carrier Beam Laser` | `M44 Blaster` | `Repair Pulse Gun` | `Vulcan Cannon 1` |
| `Carrier Beam Laser Multiplayer` | `M6 Blaster` | `Rocket Launcher 1` | `Vulcan Cannon 2` |
| `Carrier Blaster` | `M6N Blaster` | `SAM Launcher` | `Vulcan Cannon 3` |
| `Carrier Pulse Cannon` | `Man Portable Rocket Launcher` | `SAT Launcher` | `Vulcan Cannon 4` |
| `Carver AAM Launcher` | `Man Portable SAM Launcher` | `Sentinel Flamethrower` | `Warrior Laser` |
| `Carver Laser Cannon` | `Mech Flamethrower` | `Sentinel Main Gun` | `Warspite Beam Laser` |
| `Cutting Beam` | `Mech Grenade Launcher` | `Shotgun` | `Warspite Main Gun` |
| `Drone Vulcan Cannon` | `Mech Twin Vulcan Cannon` | `Spread Bomb Launcher` | `Warspite Pulse Laser` |
| `Emitter Test` | `Mech Vulcan Cannon` | `Spread Pod` | `Warspite Pulse Laser 2` |
| `Fenrir Beam Laser` | `Micro Missile Launcher` | `Stream Laser Pod` | `Warspite SAM Launcher` |
| `Fenrir Flamethrower` | `Missile Launcher 1` | `Stream Laser Pod Aug` | `Wingman Beam Laser` |
| `Fenrir Iron Bomb Launcher` | `Missile Pod` | `Sub Missile Launcher` | `Wingman Blaster` |
| `Flak Cannon` | `Missile Pod Prototype` | `Tank Machine Gun` | `Wingman Micro Missile Launcher` |
| `Flamethrower` | `Mobile SAT Launcher` | `Tentacle Beam Laser` | `Wingman Spread Bomb Launcher` |
| `Flux Cannon` | `Mortar 150mm` | `Tentacle Pulse Laser` | `Wingman Torpedo Launcher` |
| `Flux Pod` | `Muspell Beam Cannon` | `Thunderhead Flamethrower` | `Wingman Twin Blaster` |
| `Forseti Drone Missile Launcher` | `Muspell Torpedo Launcher` | `Thunderhead Main Gun` | `Wingman Vulcan Cannon` |
| `Forseti Missile Launcher` | `Naval Pulse Cannon` | `Thunderhead Missile Launcher` | `Wrist Blade` |
| `Forseti Missile Trainer Launcher` | `Needle Laser` | `Tiger Claw Launcher` |  |

## Round behaviors worth knowing

The 38 round value-ids are the full behavioral palette any weapon draws from.
Beyond straight bullets the shipped data can express: seeking rounds
(`CRoundSeek` + turn rate + seek angle/delay/termination), weirdo-seek
(`CRoundWeirdoSeek` — the name is the developers'), flak with inaccuracy
(`CRoundFlak`, `CRoundFlakInaccuracy`), bouncing rounds (`CRoundBounce`),
ground-hugging and underwater rounds, torpedoes, beams, proximity triggers,
grid-of-fear effects (`CRoundGridOfFear`), jump-delay mortar behavior
(`CRoundJumpDelay`/`CRoundJumps`/`CRoundJumpRange`), and rearming rounds
(`CRoundRearm`). Negative `CRoundDamage` is the repair-weapon case — the same
pipeline heals (noted in the round-ids document).

## Honest boundaries

- Seconds and units-per-second are established via the 20 Hz/1.75 measurement;
  radians strongly indicated for inaccuracy. **No measurement pins
  `CRoundDamage`, `CWeaponPower`, or the radius fields to a world unit** —
  the names say what the fields are, not what one unit of them is.
- The literal 139-name weapon census is closed. A complete **field-value**
  ledger for all 139 weapons, 145 weapon modes, 91 rounds, and 118 explosion
  statements remains open; only selected chains are currently deep-read.
- Augmentation mechanics (what raises a weapon to its `_augmented` state) are
  visible as HUD strings but not yet bound to a measured mechanic in this
  repository.

## Sources

- Field tables and the two end-to-end chains:
  [physics-round-value-ids-2026-07-25.md](../reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md)
  (byte-reads of `data/default physics.dat`, RTTI + apply-body resolution).
- Manager/load contract:
  [physics-script-static-contract.md](../reverse-engineering/binary-analysis/physics-script-static-contract.md).
- Damage pipeline (round + explosion composition, radial falloff):
  `cround-hit-damage-path-2026-08-10.md` (cited in the round-ids document §6.2).
- String table: `reverse-engineering/binary-analysis/binary-strings.md`
  (pristine specimen; addresses retained per string).
- HUD plumbing: `references/Onslaught/BattleEngineJetPart.cpp:903`
  (`GetLanguageName` → `TEXT_DB.GetString`).
- Exact statement framing reused by the materializer:
  `rebuild/tools/materialize_retail_assets.py` (`_physics_records`).
- Faction weapon flavor: [world-lore.md](world-lore.md) — fiction.
