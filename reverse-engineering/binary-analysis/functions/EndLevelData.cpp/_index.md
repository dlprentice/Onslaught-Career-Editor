# EndLevelData.cpp Function Mappings

Wave1219 final current-risk closure note: `CEndLevelData__IsAllSecondaryObjectivesComplete` remains mapped to secondary-objective status scanning; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`. Runtime progression behavior and rebuild parity remain separate proof.

2026-06-08 MissionScript Objective/Outcome Command-Effect static proof: `missionscript-objective-outcome-command-effect-static-proof.md` and `missionscript-objective-outcome-command-effect.v1.json` preserve the EndLevelData side of the objective/outcome bridge through `CEndLevelData__IsAllSecondaryObjectivesComplete`, `CGame__FillOutEndLevelData`, `CGame__DeclareLevelWon`, `CGame__DeclareLevelLost`, `CCareer__Update`, and the `IScript__PrimaryObjectiveComplete` / `IScript__SecondaryObjectiveComplete` / `IScript__PrimaryObjectiveFailed` / `IScript__SecondaryObjectiveFailed` / `IScript__LevelWon` / `IScript__LevelLost` / `IScript__LevelLostString` handler family. This is MissionScript Objective/Outcome Command-Effect static bridge accounting only, not runtime command effects, runtime objective UI, runtime level outcome behavior, runtime save/career progression, exact `END_LEVEL_DATA` layout, patch, Godot, rebuild, or no-noticeable-difference proof.

> Functions from EndLevelData.cpp mapped to BEA.exe binary
> Source: references/Onslaught/EndLevelData.cpp (Stuart's code)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.


## Current Caveat

Wave 381 corrected the older Career-owner label at `0x004496e0` to `CEndLevelData__IsAllSecondaryObjectivesComplete`. This is saved static Ghidra source-parity evidence for one helper only. It does not prove complete EndLevelData source-file coverage, concrete structure layout, runtime progression behavior, or rebuild parity.

Wave1049 (`endlevel-objective-progression-review-wave1049`) re-read `0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete` as part of the end-level objective/progression bridge with no mutation. Fresh evidence ties the predicate to `0x0046d470 CGame__FillOutEndLevelData`, `0x0041bdf0 CCareer__ReCalcLinks`, and `0x0046d9f0 CGame__RunOutroFMV`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified`. Runtime objective UI/progression behavior, complete EndLevelData layout, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x004496e0 | CEndLevelData__IsAllSecondaryObjectivesComplete | VERIFIED_STATIC | [View](CEndLevelData__IsAllSecondaryObjectivesComplete.md) |

## Related

- Source: `references/Onslaught/EndLevelData.cpp`
- Header: `references/Onslaught/EndLevelData.h`
- Parent: [../README.md](../README.md)
