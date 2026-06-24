# GillMHeadAI / PauseMenu Ghidra Correction - 2026-05-14

Status: public-safe evidence

Source branch: `wip/sandbox`

Recorded at: 2026-05-14

## Scope

This wave records a serialized saved-Ghidra metadata correction for the GillMHead/GillMHeadAI cluster and one adjacent pause-menu owner correction. It updates saved names, signatures, comments, and tags for eleven targets after dry run, apply, read-back exports, and focused validation.

It does not mutate `BEA.exe`, launch the game, patch the installed Steam copy, include raw decompile excerpts, or prove runtime gameplay behavior.

## Private Evidence Policy

Ignored local evidence remains under `subagents/ghidra-static-reaudit/gillmhead-wave390/current/`. This report does not include decompiled source excerpts, private absolute paths, screenshots, frame data, copied executables, copied saves, raw private JSON, or Ghidra project files.

## Functions Corrected

| Address | Current saved name | Result | Selected evidence |
| --- | --- | --- | --- |
| `0x0047a760` | `CGillMHead__CreateGillMHeadAIComponent` | PASS | Allocates a `0x64`-byte type-`0x16` component, initializes through `CWarspite__Init`, installs the `CGillMHeadAI` RTTI vtable, clears `+0x60`, and stores the component at owner `+0x13c`. |
| `0x0047a7f0` | `CGillMHeadAI__ScalarDeletingDestructor` | PASS | `CGillMHeadAI` vtable slot-1 scalar-deleting destructor wrapper. |
| `0x0047a810` | `CGillMHeadAI__Destructor` | PASS | Destructor restores the `CUnitAI` base vtable and removes tracked handles before monitor shutdown. |
| `0x0047a8b0` | `CGillMHeadAI__TryTransitionIdleToOpen` | PASS | Pointer table `0x005e42d8` slot `30`, `idle` / `open` animation state context, and shared animation helper calls. |
| `0x0047a900` | `CGillMHeadAI__AdvanceOpenAttackCloseState` | PASS | Pointer table `0x005e42d8` slot `3`, `open` / `attack` / `close` / `idle` context, and target/timeout gate context. |
| `0x0047afc0` | `CGillMHeadAI__UpdateAimTransformAndTargetReader` | PASS | `CGillMHeadAI` vtable slot `3`, target-reader update path, and the 100.0 facing-vector context. |
| `0x0047b090` | `CGillMHeadAI__UpdateTargetBallisticArcFlags` | PASS | `CGillMHeadAI` vtable slot `4`, stale target-reader clear, and ballistic arc fire-readiness helpers. |
| `0x004d0ff0` | `CPauseMenu__InitPauseSession` | PASS | `CGame__Pause` calls this on `CGame::mPauseMenu`; source confirms the pause-menu activation path. |
| `0x004d10b0` | `CPauseMenu__DeactivatePauseSession` | PASS | Corrects the older GillMHead label; `CGame__UnPause` calls this on `CGame::mPauseMenu`; source confirms the pause-menu deactivation path. |
| `0x004f4530` | `SharedUnitAnimation__FindAnimationIndexOrZero` | PASS | Corrects the old GillMHead-specific helper label to shared animation helper context used outside GillMHeadAI. |
| `0x004f4560` | `SharedUnitAnimation__PlayAnimationByNameIfPresent` | PASS | Corrects the old GillMHead-specific helper label to shared animation helper context used by BattleEngine morph/animation paths. |

## Commands Run

```powershell
py -3 tools\ghidra_gillmhead_ai_wave390_probe_test.py
cmd.exe /c npm run test:ghidra-gillmhead-ai-wave390
py -3 -m py_compile tools\ghidra_gillmhead_ai_wave390_probe.py tools\ghidra_gillmhead_ai_wave390_probe_test.py
```

Result: PASS.

Important output:

- Focused probe unit tests passed with `2/2`.
- Package-script probe status was `PASS` with `11` targets, `11` metadata rows, `11` tag rows, and `0` failures.
- Python compile check passed.

Headless dry/apply results:

- Dry run: `updated=0 skipped=11 renamed=0 would_rename=10 missing=0 bad=0`.
- Apply: `updated=11 skipped=0 renamed=10 would_rename=0 missing=0 bad=0`.
- Apply log reported `REPORT: Save succeeded`.

Read-back results:

- `11` metadata rows.
- `11` decompile exports.
- `25` xref rows.
- `11` tag rows.
- `2` vtable type rows.
- `16` vtable slot rows.
- `80` pointer-table rows.

The refreshed queue reports `6027` functions, `1466` commented functions, `4561` commentless functions, `1927` undefined signatures, and `1895` `param_N` signatures. Current confirmation proxies are telemetry only: comment-backed `1466/6027 = 24.32%`; strict clean-signature `1401/6027 = 23.25%`.

## What Is Proven

- The saved Ghidra project now records the checked `0x0047a760..0x0047b090` cluster with GillMHeadAI owner/state/targeting metadata where evidence supports it.
- The saved Ghidra project now records `0x004d10b0` as `CPauseMenu__DeactivatePauseSession`, superseding the older GillMHead pause-latch owner claim.
- The saved Ghidra project now records the shared animation helpers at `0x004f4530` and `0x004f4560` with owner-neutral names, superseding older GillMHead-specific helper labels.
- The focused proof script validates the saved metadata, tags, selected decompile tokens, vtable/RTTI context, pointer-table context, xref context, and overclaim boundaries.

## What Is Not Proven

- This does not prove runtime GillMHeadAI animation, targeting, firing, pause-menu, or BattleEngine morph behavior.
- This does not prove exact source method identity for every corrected function.
- This does not recover concrete class layouts, local variable names, local types, or structure definitions.
- This does not prove complete GillMHead/GillM/CGillMHeadAI system coverage.
- This does not mutate or patch `BEA.exe`.
- This does not prove rebuild parity.

## Release Posture

GREEN for public-safe saved-Ghidra metadata correction evidence. It should be treated as static retail-binary evidence and as a correction to stale docs/probes, not as runtime proof or source-complete gameplay implementation.
