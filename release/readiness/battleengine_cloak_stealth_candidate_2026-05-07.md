# BattleEngine Cloak / Stealth Candidate - 2026-05-07

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`); `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe bounded read-only retail-candidate evidence, not exact cloak identity or runtime proof

> **Current name correction (2026-07-12):** references below to
> `CMonitor__Process` at `0x004081c0` now mean `CBattleEngine__Move`. The body
> tokens remain historical static evidence; the Monitor owner interpretation is
> superseded by the current BattleEngine movement crosswalk.

## Objective

Narrow the remaining source-only BattleEngine cloak/stealth gap without mutating the installed game, the original `BEA.exe`, or the Ghidra project.

This pass intentionally stays narrower than exact source identity. It records candidate retail evidence for cloak latch/config checks, active energy burn, forced-decloak clearing, stealth-style interpolation, and target-range scaling while keeping exact `HandleCloak` / `Cloak` / `Decloak` / `Render` method identity, weapon-fire reset, render-flag identity, runtime behavior, and rebuild parity open.

## Inputs

Fresh ignored Ghidra headless exports were written under:

```text
subagents/battleengine-cloak-stealth-candidate/current/decompile/
```

The export index reported:

- first pass: targets `10`, dumped `10`, missing `0`, failed `0`
- player/context pass: targets `7`, dumped `7`, missing `0`, failed `0`

Read-only constant checks were written under:

```text
subagents/battleengine-cloak-stealth-candidate/current/constants.json
```

Those raw decompile and constant files remain ignored/private evidence. The committed check stores only repo-relative paths, public function names/addresses already present in the project, token names, line hits, and proof boundaries.

## What The Probe Checks

Command:

```powershell
npm run test:battleengine-cloak-stealth-candidate
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_cloak_stealth_candidate_probe.py --check
```

The probe checks:

- source cloak/decloak, active energy burn, stealth interpolation, target-scaling, and render tokens in `references/Onslaught/BattleEngine.cpp`
- a candidate cloak toggle/latch helper in `CGeneralVolume__Update4ACLatchFromHeightAndA0`
- active energy burn and forced-decloak clearing in `CMonitor__Process`
- a candidate current/target transition around offsets `0x2c8` and `0x2cc` in `CMonitor__Process`
- target-selection context containing a `0.01` stealth-style range-scaling factor in `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`
- render-mesh context export presence without claiming `RF_CLOAKED` identity
- read-only constants `_DAT_005d85c0 == 0.1` and `_DAT_005d85fc == 0.01`

Result:

```text
BattleEngine cloak/stealth candidate probe
Status: pass
Source tokens: 15/15
Cloak helper tokens: 7/7
CMonitor tokens: 10/10
Targeting tokens: 4/4
Render context tokens: 3/3
```

## What This Proves

- The source still contains cloak/decloak, active cloak energy burn, forced decloak, stealth interpolation, target-range stealth reduction, render alpha, and `RF_CLOAKED` render-flag tokens.
- Fresh read-only `CGeneralVolume__Update4ACLatchFromHeightAndA0` decompile contains a candidate cloak toggle/latch helper that sets or clears offsets `0x4ac` and `0x5dc` after energy/config checks.
- Fresh read-only `CMonitor__Process` decompile contains active energy burn and forced-decloak clearing for the `0x4ac` / `0x5dc` latch plus a candidate current/target transition around offsets `0x2c8` and `0x2cc`.
- Fresh read-only target/fire decompile contains a stealth-style `0.01` range-scaling factor used in target selection context.
- Render mesh context was exported and checked as context only.
- The current constants check maps `_DAT_005d85c0` to `0.1` and `_DAT_005d85fc` to `0.01`.

## What This Does Not Prove

- Exact source-to-retail identity for `CBattleEngine::HandleCloak`, `Cloak`, `Decloak`, `Render`, or `WeaponFired`.
- Cloak button handling identity in the retail control path.
- Retail `RF_CLOAKED` render-flag identity.
- Weapon-fired stealth reset identity.
- Runtime cloak, target-lock, render, or weapon behavior.
- Ghidra rename-map mutation.
- Rebuildable open-source gameplay implementation.

## Outcome

This is useful narrowing evidence, not a closure. `cloak_energy_gate_burn_and_render` is now a partial retail candidate in the aggregate source-to-binary gap accounting, while `weapon_fire_breaks_stealth` remains source-only until a later pass proves exact retail identity or promotes a narrower candidate with enough independent evidence.

## Privacy / Release Safety

The committed report is public-safe. It does not include binaries, source excerpts, private absolute paths, screenshots, runtime captures, raw decompile bodies, private assets, or Ghidra mutation logs.

The raw decompile and constant JSON outputs remain ignored under `subagents/`.
