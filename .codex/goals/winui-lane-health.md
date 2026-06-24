# WinUI Lane Health Goal

## Metadata

| Field | Value |
| --- | --- |
| Title | WinUI 3 lane health |
| Status | scaffolded for next run |
| Created | 2026-05-04 |
| Phase | Phase 2: WinUI build/run/test assessment |
| Scope | WinUI/AppCore build and test health, command documentation, minimal stabilization |
| Owner | Main/Codex agent operating in this repo |
| Allowed files | WinUI/AppCore project files, C# solution files, tests, docs/state needed to record commands and results |
| Forbidden files/actions | UX redesign, feature migration from Electron, Python GUI/product work, broad refactors, public release expansion, commits |

## Goal

Stabilize and assess the WinUI 3 product lane enough to prove whether it builds, which tests validate it, and what blocks the next WinUI UX/product sprint.

## Explicit Non-Goal

Do not redesign WinUI UX in this run. Do not migrate features between frameworks. Do not turn Electron or Python into product lanes.

## Files And Projects To Inspect

- `roadmap/three-lane-product-strategy.md`
- `.codex/state/three-lane-reset.md`
- `AGENTS.md`
- `OnslaughtCareerEditor.WinUI/`
- `OnslaughtCareerEditor.AppCore/`
- `OnslaughtCareerEditor.AppCore.Tests/`
- `OnslaughtCareerEditor.UiTests/`
- `OnslaughtCareerEditor.Cli/`
- `OnslaughtCareerEditor.Release.slnx`
- any solution/project files that already reference WinUI or AppCore

## Build/Test Commands To Discover And Run

Start with:

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
dotnet build .\OnslaughtCareerEditor.Release.slnx --nologo
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
```

Also inspect docs/project files for the correct WinUI run command. Document it, but do not require launching the UI if the environment cannot display it.

## Allowed Fixes

Only make minimal fixes needed to make the WinUI lane verifiable:

- build command corrections
- test command corrections
- project/solution reference fixes if clearly broken and low-risk
- documentation updates for accurate commands/results
- test expectation fixes only when the test is clearly stale relative to current lane policy

Do not make subjective product UX changes.

## Completion Criteria

This goal is complete only when:

1. The correct WinUI build/run/test commands are identified.
2. Feasible WinUI/AppCore validation commands have been attempted.
3. Results are recorded with exact command, pass/fail/warn/skipped status, and important output.
4. Any safe build/test/doc-command fixes are completed and revalidated.
5. Remaining blockers are listed with exact files/projects and suggested next action.
6. The final diff is coherent and reviewable.

## Final Response Requirements

Report:

- WinUI lane health verdict
- build/test commands run
- pass/fail/warn/skipped results
- blockers
- files changed
- remaining risks
- exact next `/goal` prompt for a WinUI 3 UX/product sprint
