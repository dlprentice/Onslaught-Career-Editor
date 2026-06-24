# CEndLevelData__IsAllSecondaryObjectivesComplete

- **Address:** `0x004496e0`
- **Saved signature:** `bool __fastcall CEndLevelData__IsAllSecondaryObjectivesComplete(void * this)`
- **Source context:** `references/Onslaught/EndLevelData.cpp`, `CEndLevelData::IsAllSecondaryObjectivesComplete`

## Summary

Scans the secondary-objective status slots at `this+0x4d0`, returns false when any failed status is present, and logs `ERROR: No secondary objectives` when no complete or failed secondary objective is defined.

## Notes

- Wave 381 supersedes the older `CCareer__AreSecondaryObjectivesComplete` label.
- Callers still include `CCareer__ReCalcLinks`, `CGame__FillOutEndLevelData`, and `CGame__RunOutroFMV`, so this helper bridges career progression and end-level summary paths without being a `CCareer` method.
- Saved via serialized headless dry/apply/read-back on 2026-05-13.
- Wave1049 (`endlevel-objective-progression-review-wave1049`) re-read `0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete` with no mutation. Fresh evidence keeps callers `0x0046d470 CGame__FillOutEndLevelData`, `0x0041bdf0 CCareer__ReCalcLinks`, and `0x0046d9f0 CGame__RunOutroFMV` coherent with the saved predicate. Verified backup: `G:\GhidraBackups\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified`.
- 2026-06-08 MissionScript Objective/Outcome Command-Effect static proof: `missionscript-objective-outcome-command-effect-static-proof.md` and `missionscript-objective-outcome-command-effect.v1.json` use this function as the EndLevelData predicate bridge from objective state slots into CGame/Career progression context, alongside `CGame__FillOutEndLevelData`, `CGame__DeclareLevelWon`, `CGame__DeclareLevelLost`, and `CCareer__Update`. This is static bridge accounting only; runtime objective UI, runtime level outcome behavior, runtime save/career behavior, exact layout, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Not Proven

- Runtime progression behavior is not proven by this static pass.
- Complete EndLevelData source-file coverage, concrete layout, locals, and types remain open.
- BEA launch behavior, game patching, and rebuild parity are not proven.
