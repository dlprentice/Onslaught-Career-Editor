# WinUI Product And RE Campaign Goal

Status: active operating contract
Created: 2026-05-05

## Mission

Advance the repository around the WinUI 3 Windows application as the primary polished product lane, while keeping archived Electron, WPF, and old Python GUI/CLI lanes available as reference only.

Work in reviewable Ralph-style waves: inspect, prioritize, patch, validate, visually critique, update evidence/state, commit/push after each green wave, then continue until the campaign criteria are met or remaining work is speculative, risky, or product-design-dependent.

## Product Truth

- WinUI 3 is the only forward-facing GUI product lane.
- AppCore and the C# CLI remain active support/correctness lanes while useful.
- Electron, WPF, and the old Python GUI/CLI parity app are archived/reference lanes. Do not revive them as primary product surfaces without a later explicit strategy decision.
- Active Python remains narrow RE/tooling/lab support under `tools/` and related utility paths.
- Public release scope stays explicit, sanitized, and WinUI-centered.

## Local Game Install

The local retail install is:

```text
C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila
```

Treat this path as read-only source material. Do not mutate the installed game, installed `BEA.exe`, real saves, or installed options files. Any patching, runtime proof, copied executable work, generated media/cache output, screenshots, frames, or test saves must use copied profiles or app-owned artifact roots.

## Guardrails

- Inspect git status before each meaningful batch.
- Preserve unrelated uncommitted work.
- Do not delete archive/reference lanes.
- Do not synthesize `.bes` saves.
- Do not weaken AppCore, patching, release, or private-evidence safety gates.
- Keep private game/media/save/proof assets out of public release outputs.
- Do not claim "bug free"; report inspected areas and validation confidence.
- Amend stale constraints only when they contradict current WinUI-first reality or block real work without a valid safety reason.

## Work Loop

1. Discover real issues in WinUI, AppCore, tests, docs, release tooling, archive boundaries, and RE evidence.
2. Prioritize build/test failures, safety/correctness defects, product-lane clarity, docs/release drift, visual/accessibility defects, then maintainability.
3. Patch focused, reviewable batches.
4. Validate with the strongest practical targeted gates.
5. Capture visual/interaction evidence for WinUI when a batch changes user experience.
6. Update `.codex/state/winui-product-re-campaign-progress.md` and `.codex/state/winui-product-re-campaign-evidence.md`.
7. Commit and push only after a green wave.

## Validation Menu

Use the gates relevant to each batch:

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
npm run test:cli-smoke
npm run test:md-links
npm run test:doc-commands
npm run test:repo-hygiene
npm run test:public-allowlist
py -3 tools\docsync_check.py
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
git diff --check
```

Archived Electron commands are optional archive-health checks only when that archive is touched or explicitly inspected.

## Completion Criteria

The campaign is complete only when:

1. WinUI is polished, stable, and clearly primary in app behavior, docs, tests, and release posture.
2. Automated WinUI code/UI checks cover major product workflows.
3. WinUI visual QA evidence has been captured and summarized safely.
4. Docs, lore indexes, release cycle docs, manifests, and state files match current reality.
5. Archived Electron/WPF/Python GUI lanes are out of the product path but still referenceable.
6. Real RE progress beyond function naming is recorded: assets, media, logic, or rebuild-coverage evidence.
7. Remaining gaps are explicit and not hidden behind broad claims.
