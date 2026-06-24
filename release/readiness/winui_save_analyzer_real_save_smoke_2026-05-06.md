# WinUI Save Analyzer Real Save Smoke - 2026-05-06

Status: public-safe evidence

## Scope

This note records a focused native WinUI Save Lab interaction smoke against a private real `.bes` save. It does not embed screenshots, save contents, private absolute paths, raw save bytes, copied files, data URLs, or base64.

## What Changed

- Added stable WinUI automation IDs for the Save Analyzer input, analyze action, result title, file-kind metric, summary title, summary tree, and report area.
- Added an explicit desktop-only FlaUI smoke test, `WinUiSaveAnalyzerInteractionSmokeTests.SaveAnalyzer_AnalyzesRealSaveThroughUiWhenProvided`.
- The smoke is gated by `ONSLAUGHT_WINUI_REAL_SAVE_PATH`, so normal test runs do not require private saves.
- The smoke launches WinUI with an ignored isolated app config root, enters the provided real save path, invokes Analyze, waits for the analyzer result, and captures a private screenshot.

## Private Visual Evidence

Ignored screenshot:

- `subagents/winui-save-analyzer-interaction/2026-05-06/01-save-analysis.png`

The screenshot shows the real save analysis result with the primary metrics visible: file kind, mission count, goodie count, kill total, and tech slots. The private save path is intentionally not repeated here.

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.SaveLab_VisibleCopyUsesProductLaneName"` | PASS | 1/1 focused Save Lab product-lane test passed. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiSaveAnalyzerInteractionSmokeTests.SaveAnalyzer_AnalyzesRealSaveThroughUiWhenProvided"` | PASS | 1/1 explicit real-save analyzer smoke passed with the private save supplied through an environment variable. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 33/33 active UiTests passed. |
| `py -3 tools\docsync_check.py` | PASS | Dsync policy check passed. |
| `npm run test:doc-commands` | PASS | 348 documented npm commands checked. |
| `npm run test:md-links` | PASS | Markdown link check passed. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Counts `R0=1173 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files: 1162; curated allowlist check passed. |
| `npm run test:public-allowlist` | PASS | 1162 rows checked. |
| `npm run test:repo-hygiene` | PASS | Repo text hygiene check passed. |
| `node -e "<parse developer_agent_state.json, documentation_agent_state.json, curated_release_manifest.json>"` | PASS | `json parse ok`. |
| `git diff --check` | PASS | No whitespace errors; Git emitted CRLF normalization warnings for generated release TSV files only. |

## Proven

- The WinUI Save Analyzer can analyze a real private `.bes` through the desktop UI.
- Analyzer result metrics become visible in the first viewport.
- The smoke remains private-safe by requiring an environment variable and writing screenshots only under ignored `subagents/`.

## Not Proven

- This does not prove every private save variant.
- This does not mutate or patch a save.
- This does not prove signed installer/MSIX behavior.
- This does not replace broader manual Save Editor workflow review.
