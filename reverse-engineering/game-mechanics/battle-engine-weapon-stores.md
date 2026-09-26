# Battle Engine weapon stores, charge and firing state

Status: active static contract for the rebuild's player weapons
Last updated: 2026-09-25
Summary: the Aquila's ammo and heat stores, when a shot spends them, cooling, the
Missile Pod and Pulse Cannon Pod charge law, what an empty store blocks, and what
`IsFiring` counts.
Evidence: MEASURED static reads of the pristine specimen and the shipped data; a
read-only research pass traced the functions and the RE lane re-checked the store
table, both spend paths, the cooling loop, `Charge`, the jet charge gate and both
`IsFiring` bodies at their addresses. No runtime capture.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
`data/battle engine configurations.dat`, 1,514 bytes, SHA-256 prefix `58722b12a04cae97`;
`data/default physics.dat`, SHA-256
`e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`.

The Battle Engine and part functions match the pinned GPL source
(`BattleEngine.cpp`, `BattleEngineJetPart.cpp`, `BattleEngineWalkerPart.cpp`,
`BattleEngineDataManager.cpp`). `CWeapon` is not in that drop; its behaviour below
comes from the bytes.

## Stores

The Aquila Prototype record (configuration file offset `0x2d2`, version 12) lists six
(heat flag, value) pairs at `0x35f`:

| Store | Kind | Capacity | Used by |
| ---: | --- | ---: | --- |
| 0 | ammo | 2000 | Mech Vulcan Cannon (jet, consumption 1), Mech Twin Vulcan Cannon (walker, 2) |
| 1 | ammo | 100 | none of the Aquila's weapons |
| 2 | heat | 150 | Pulse Cannon Pod (walker primary, consumption 4, charge rate 10); Pulse Cannon Pod Aug (0) |
| 3 | ammo | 200 | Missile Pod (jet, consumption 1, charge rate 8) |
| 4, 5 | heat | 100 | none |

The loader `0x00510800` reads the file. `CBattleEngineData::Initialise`
(`0x0040f590`) defaults every store to heat 0 and value 1000.0
(`0x0040f741-0x0040f75b`, `BattleEngineDataManager.cpp:55-59`). `Load` (`0x0040f980`)
reads each store's heat flag into configuration `+0x70+4n` and its value into
`+0x88+4n` (`0x0040fee8-0x0040ff0e`, `:357-362`). `CBattleEngine::Init`
(`0x0040572f-0x0040577f`, `BattleEngine.cpp:303-312`) and `UpdateConfiguration`
(`0x0040c650`, `:2923-2932`) clear overheat and start ammo stores full and heat stores
at 0.

## Spending and cooling

- **Once per burst event.** The burst spawner calls `CBattleEngine::WeaponFired`
  (`0x0040c2e0`) once, before its volley loop
  ([burst contract](../contracts/render-platform/ProjectileBurst__SpawnFromCurrentPreset__005069f0.md)).
  The spend is not tied to a round being created. A Mech Vulcan event spends 1 and
  fires 2 bullets; a Twin Vulcan event spends 2 and fires 4; each Missile Pod event
  spends 1 and fires one missile (volley 1).
- **Jet ammo** (`0x0041215d-0x00412192`): value −= consumption, clamped at 0.
- **Jet heat** (`0x00412135-0x00412155`): value += consumption − `kWeaponCoolRate`.
  Walker heat paths add the full consumption (list `0x00414110-0x00414154`,
  primary `0x004141dc-0x00414226`, Aug `0x00414304-0x00414381`), as in the source.
  A shot refused for heat sets overheat, calls `WeaponOverheated` and returns 0.
- **`kWeaponCoolRate`** is the integer 1, held twice: `0x00622f08` (read only by
  Move, `0x004095ed`) and `0x006236a4` (read only by jet `WeaponFired`,
  `0x0041214a`). Nothing writes either.
- **Cooling** (`CBattleEngine::Move` `0x004095d6-0x00409633`, `:1708-1718`). Every
  Move, each heat store's value goes down by 1.0. A result below 0 becomes 0;
  otherwise overheat clears when the value is strictly below 0.75 × capacity
  (`0x005d8bc4`). No branch in Move skips the loop.
- **Refill.** Ammo never regenerates over time. `CBattleEngine::Rearm`
  (`0x0040ac50`, `:2256-2275`) adds amount × capacity, clamped. Its only caller is the
  round-hit handler at `0x004d8d07`, for a hit on a Battle Engine (type bit `0x8`)
  by a round with `CRoundRearm`. Only the `Repair Pad` round carries it (200).

## Charge

- `CWeapon::Charge` (`0x005068f0`) adds the weapon's charge rate (profile `+0x08`)
  to `+0x60` when any charge level 1-4 exists and the charge is below 400.0.
- The jet part (`0x00411cd4-0x00411d4b`) and walker part (`0x00413d91-0x00413e04`)
  call it only while the charge is below 100 × the highest present level: 100 for
  both pods.
- The Missile Pod's charge runs 0, 8, …, 96, 104 and stops. Level 1 (Salvo) needs
  trunc(round(charge)/100) = 1, which first happens at 104, on the 13th charge call.
- Both pods share this path. An ammo store costs nothing while charging; the Pulse
  pod's heat store gains its consumption per charge call (jet
  `0x00411d62-0x00411d98`, walker `0x00413e1e-0x00413e53`).
- `ReadyToCharge` (`0x0050a080`) is true with no mode yet or once now > `+0x64`.
- The charge resets to 0 at `0x0041203b` (jet fire), `0x00414019` (walker fire),
  `0x00411f96` (the newly selected weapon in `ChangeWeapon`) and `0x0050602a`
  (`CWeapon::Fire`).

## Fire, empty stores and locks

- `CWeapon::Fire` (`0x00506010`; its saved label is wrong) resolves the level from
  round(charge)/100 with fallback, then sets the mode.
  - It sets the reload deadline `+0x64` to now + `CWeaponReloadTime` (`0x0050611a`),
    zeroes the burst counter `+0x6c`, and zeroes Battle Engine `+0x5e0`, the source's
    `mCurrentTarget` (`0x00506137`).
  - It then spawns the first burst (`0x00506143`), plays the launch sound, sets
    `+0x6c` to 1 and queues event 5001 at now + `CWeaponBurstDelay`
    (`0x005061ae-0x005061d8`).
  - The 5001 handler (`0x00506930`) spawns while `+0x6c` is below the mode's burst
    size, increments `+0x6c` after each spawn (`0x005069c3`), and does nothing while
    the owner is dying (`0x00506948`).
  - Retail quirk: Fire rewrites charge, level `+0x68` and mode `+0xa0` before its
    reload check. A second trigger press during a salvo therefore switches the rest
    of that burst to the launcher mode, because the handler reads the mode through
    `+0x68` (`0x00506952`).
- **Empty store and firing.** `FireWeapon` (`0x00409f20`, `:1958-1970`) has no ammo
  check, so Fire still resets the charge, sets the reload and runs the burst counter.
  Every burst event is refused in `WeaponFired`: no round, draw, lock or recoil. Each
  refusal refreshes `mAmmoDepletedTime` (`+0x608`) when it is more than 8.0 s old,
  and Move then plays `hud_ammunition_depleted`.
- **Empty store and charging.** Charging exits with an ammo store at or below 0
  (`0x00411cbc-0x00411cce`). `ChangeWeapon` skips a weapon whose consumption
  exceeds its store (`0x00411f3a-0x00411f49`).
- **Empty store and locks.** `CanWeaponFire` is false (jet `0x00412570`: ammo
  value > 0, or heat below capacity and not overheated; the walker version
  `0x00414630` also checks active). So `HandleLocks` drops every lock each frame
  and acquires none.
- **`WeaponOverheated`** (`0x0040f110`) only sets `mWeaponOverheatedTime`
  (`+0x60c`) to now when that is more than 4.0 s old. Its callers set the store's
  overheat flag first. `ChargeWeapon` additionally clears slow movement and forces a
  Fire (jet `0x00411da7-0x00411e5b`, walker `0x00413e61-0x00413e9a`).
- **`Charged()`** is weapon `+0x68 > 0`. A charged heat-weapon shot returns before
  the overheat test and costs no heat.

## Firing state

The parts' shared `IsFiring` (`0x00414b30`) walks the part's weapon list at `+0x00`
and returns 1 when any weapon's `CWeapon::IsFiring` (`0x0050a290`) holds: a current
mode, `+0x6c` nonzero and `+0x6c` below the mode's `CWeaponBurstSize`. The walker's
primary and Aug weapons are not in that list. A Missile Pod burst therefore counts
from its first missile until its last spawns: 0.4 s for the launcher, 0.45 s for the
salvo. Burst-size-1 weapons (both Vulcans) never count. `HandleLocks` asks the jet
part in state 3 and the walker part otherwise, so a pod burst during a transform to
walker is not seen.

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| How often the PC build calls `ChargeWeapon` while fire is held (buttons 18/19 reach `0x00409f20`/`0x00409ef0` through `0x004d32cd`/`0x004d32d4`; the hold/release mapping was not found) | Disassemble the controller code calling `CPlayer` vtable `0x005de770` slot 3, or count `0x00409ef0` calls per frame in a runtime trace |
| Whether Level 100's Health Pad fires `Repair Pad` rounds at the player (reload 30 s, range 7) | Read the repair-pad AI update's firing conditions |
