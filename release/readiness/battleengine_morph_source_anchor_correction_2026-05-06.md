# BattleEngine Morph Source Anchor Correction - 2026-05-06

## Summary

This pass corrected stale active wording that treated the transform flow as if the source method had a separate `Transform` name.

The Stuart source anchor is `CBattleEngine::Morph()`. The existing retail evidence still proves selected transition helper xrefs and read-back tokens only; it does not prove exact source-to-retail identity for the full Morph / transform-morph flow.

## Traceability

- Branch: `wip/sandbox`
- Implementation commit: `c8d288d4f5f546f9714afd5518597a4e3c8c2fb5`
- Traceability commit: `5e820545fd7b2b8cadd748c93fbb11feab793a27`

## What Changed

- Added a repo text hygiene rule that blocks future active-doc/tool references to stale transform-method identity wording.
- Added a focused hygiene unit test for that rule.
- Updated `tools/battleengine_logic_coverage_probe.py` to check a new `transform_morph_method_anchor` against `void CBattleEngine::Morph()`, both morphing states, and the `flytowalk` / `walktofly` animation calls.
- Updated the source-to-binary gap probe so the new Morph anchor remains explicitly source-only pending retail identity proof.
- Corrected active public-safe docs, release notes, function docs, and lore-book mirrors to name source `CBattleEngine::Morph` / transform-morph identity accurately.

## Commands Run

| Command | Result | Important Output |
| --- | --- | --- |
| `py -3 tools/repo_text_hygiene_check_test.py` | PASS | 26 focused hygiene tests passed. |
| `py -3 tools/repo_text_hygiene_check.py` | PASS after correction | New stale transform-method guard passed after active references were corrected. |
| `py -3 tools/battleengine_logic_coverage_probe.py --check` | PASS | Source anchors 12/12; new `transform_morph_method_anchor` passed. |
| `py -3 tools/battleengine_source_binary_gap_probe.py --check` | PASS | Source anchors 12/12; source-only anchors pending binary identity 12. |

## What This Proves

- The source transform/morph entry point is now machine-checked as `CBattleEngine::Morph()`.
- Active public-safe docs no longer imply an exact source method with a separate `Transform` name.
- Current release/readiness language keeps retail helper evidence separate from unproven exact Morph body identity.

## What This Does Not Prove

- Exact Steam retail binary identity for the full source `CBattleEngine::Morph()` body.
- Runtime transform behavior in a running mission.
- Ghidra rename-map mutation or read-back for a Morph body.
- Rebuildable gameplay parity.

## Safety

- Did not launch BEA.exe.
- Did not mutate the installed game, copied profiles, or any executable.
- Did not mutate Ghidra state.
- Did not commit private assets, raw proof JSON, screenshots, frames, or local game paths.
