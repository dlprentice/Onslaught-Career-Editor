# WinUI PatchBench Presentation-Helper Boundary Guard - 2026-06-25

Status: accepted test-hardening slice

## Scope

This slice added static guard coverage for the existing Windowed & Mods
`PatchBench*` presentation helpers. It did not change production WinUI code.

Changed path:

- `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`

## Accepted Evidence

- `PatchBench_PresentationHelpersStayBehaviorFree` enumerates the current
  `PatchBench*` helper files and requires future helper additions to make an
  explicit test-boundary decision.
- The guard blocks behavior-bearing tokens from helpers, including file/process
  APIs, async/task execution, safe-copy runtime services, music replacement
  services, patch engines, launch-plan builders, Host/Join controls,
  matchmaking controls, release/package wording, and installer/package tokens.
- The guard keeps the existing narrow exception for
  `PatchBenchSelectedProfileText`: it may format `SafeCopyProfilePreset` data
  and compare catalog profile IDs for copy, but it still may not build patch
  keys, choose music presets, read launch controls, or own profile preset IDs.
- Final review requested additional drift tokens for selected-profile catalog
  lookup, visible-selection validation, selected-spec/signature building,
  launch-plan building, stop/profile-prepare DTOs, control-options requests,
  and music-replacement result types. Those guard tokens were accepted and added.

## Non-Claims

This is test hardening only. It does not change patch catalog rows, byte
patches, selected-key semantics, `FunctionalArea` mappings, dependency/conflict
policy, safe-copy creation or launch behavior, music behavior, online
readiness, runtime proof, release packaging, app release assets, or installed
game/original `BEA.exe` mutation rules.

## Consult Review

- Specialist consult suggested a possible production extraction for advanced
  BEA.exe-only selection-summary copy.
- Adversarial consult blocked production extraction for this slice and
  recommended the safer helper-boundary static guard instead.
- Codex root accepted the adversarial path for this slice because it strengthens
  all recent helper extractions without moving behavior.
- Final adversarial review approved the test-hardening direction with no
  blockers. Non-blocking token additions were accepted.

## Focused Validation

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench_PresentationHelpersStayBehaviorFree"
```

Result: PASS, 1 test.

Broad closeout validation passed:

```powershell
npm run test:winui-primary-lane
npm run test:doc-commands
npm run test:md-links
npm run test:hard-payload-safety
npm run test:public-allowlist
npm run test:repo-hygiene
```

Closeout counts:

- WinUI solution build: PASS, 0 warnings, 0 errors
- AppCore tests: 1178 passed
- WinUI tests: 88 passed, 2 catalog-dependent skips
- documented npm commands checked: 4301
- Markdown files scanned: 3634
- local Markdown links checked: 6125
- public candidate files checked by hard-payload safety: 19334
- public tracked paths in migration inventory: 19334
- submodule payload candidate files checked: 19518
- accepted private-only hard-payload/scratch paths: 5557
- explicit text files checked by repo line-ending guard: 18487
