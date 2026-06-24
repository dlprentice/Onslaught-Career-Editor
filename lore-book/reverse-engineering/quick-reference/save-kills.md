Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
Summary: Kill counter and metadata lookup.
# Kill Tracking System

## Kill Counter Offsets (True View)

| Index | Offset | Category | Enum |
|-------|--------|----------|------|
| 0 | 0x23F6 | Aircraft | TK_AIRCRAFT |
| 1 | 0x23FA | Vehicles | TK_VEHICLES |
| 2 | 0x23FE | Emplacements | TK_EMPLACEMENTS |
| 3 | 0x2402 | Infantry | TK_INFANTY (typo!) |
| 4 | 0x2406 | Mechs | TK_MECHS |

## Encoding

```
stored = (meta << 24) | (kills & 0x00FFFFFF)
```

Preserve `meta` when patching. Clamp `kills` to 24-bit (`0..0x00FFFFFF`).

## Goodie Unlock Thresholds

| Category | Thresholds | Patch Value |
|----------|------------|-------------|
| Aircraft | 25, 50, 75, 100 | 100+ |
| Vehicles | 100, 200, 300, 400 | 400+ |
| Emplacements | 25, 50 (75 in combos) | 75+ |
| Infantry | 40, 80, 160 (100 appears in a combined unlock: Aircraft+Infantry 50+100) | 160+ |
| Mechs | 20, 40, 80 (40 unlocks 2 goodies) | 80+ |

**Recommendation**: Patch all to 400+ to unlock everything.

## Kill-Based Goodie Unlocks (Unit Goodies)

The full authoritative mapping lives in
`reverse-engineering/save-file/goodies-system.md`. This quick reference stays
link-closed so contributors can work from the public-primary repo without
digging through the larger proof forest first.

Unit-goodies highlights (retail/Steam):
- Infantry: 40 -> Muspell Grunt, 80 -> Commando, 160 -> Firebreather
- Aircraft: 25 -> ATF, 50 -> Ground Attack, 75 -> Dropship, 100 -> Bomber
- Vehicles: 100 -> M Tank, 200 -> M Truck, 300 -> Artillery, 400 -> SAM Launcher
- Mechs: 20 -> Gunwalker, 40 -> Gunwalker 2 + Arachnid, 80 -> Guncrab
- Emplacements: 25 -> MG Turret, 50 -> Laser Turret
- Combined examples: Aircraft+Infantry 25+80 (Dropship v2), Emplace+Vehicles 75+100 (Artillery Turret)

## Runtime Behavior

Kill counts alone don't immediately unlock goodies - game evaluates on level enter/exit.

## EKilledType Enum

```cpp
enum EKilledType {
    TK_AIRCRAFT = 0,
    TK_VEHICLES = 1,
    TK_EMPLACEMENTS = 2,
    TK_INFANTY = 3,      // TYPO preserved
    TK_MECHS = 4,
    TK_TOTAL = 5,        // Not saved
    TK_HACK_AGRADES = 6, // Runtime only
    TK_HACK_SGRADES = 7, // Runtime only
};
```
