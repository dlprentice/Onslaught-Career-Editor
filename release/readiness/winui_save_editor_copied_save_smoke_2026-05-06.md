# WinUI Save Editor Copied Save Smoke - 2026-05-06

Status: public-safe evidence

## Scope

This note records a focused native WinUI Save Editor interaction smoke against a copied private real `.bes` save. It does not embed screenshots, save contents, private absolute paths, raw save bytes, copied files, data URLs, or base64.

## What Changed

- Added stable WinUI automation IDs for the Save Editor input path, output path, patch action, pending-changes text, safety hint, output log, and result banner.
- Fixed the Save Editor result banner so patch success or block messages become visible after a patch attempt.
- Extended the explicit desktop-only FlaUI smoke test with `SaveEditor_PatchesCopiedRealSaveThroughUiWhenProvided`.
- The smoke is gated by `ONSLAUGHT_WINUI_REAL_SAVE_PATH`, so normal test runs do not require private saves.
- The smoke copies the supplied private save into an ignored `subagents/` evidence folder, patches that copy to a distinct output file, verifies the copied input hash is unchanged, and captures a private screenshot.

## Private Visual Evidence

Ignored screenshot:

- `subagents/winui-save-editor-interaction/2026-05-06/01-save-editor-patched.png`

The screenshot shows the Save Editor patch summary and patch output after a successful copied-save patch. Private paths are intentionally not repeated here. A later scrolled visual/accessibility review tightened the primary UI so the visible patch output also summarizes the selected output file instead of printing full copied input/output paths.

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.SaveLab_VisibleCopyUsesProductLaneName"` | PASS | 1/1 focused Save Lab product-lane test passed. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiSaveAnalyzerInteractionSmokeTests"` | PASS | 2/2 explicit real-save UI smokes passed: analyzer and copied-save editor patch. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 33/33 active UiTests passed. |
| `py -3 tools\docsync_check.py` | PASS | Dsync policy check passed. |
| `npm run test:doc-commands` | PASS | 356 documented npm commands checked. |
| `npm run test:md-links` | PASS | Markdown link check passed. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Counts `R0=1175 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files: 1163; curated allowlist check passed. |
| `npm run test:public-allowlist` | PASS | 1163 rows checked. |
| `npm run test:repo-hygiene` | PASS | Repo text hygiene check passed. |
| `node -e "<parse developer_agent_state.json, documentation_agent_state.json, curated_release_manifest.json>"` | PASS | `json parse ok`. |
| `git diff --check` | PASS | No whitespace errors; Git emitted CRLF normalization warnings for generated release files only. |

## Proven

- The WinUI Save Editor can patch a copied real private `.bes` through the desktop UI.
- The original supplied private save is not mutated by the smoke; only an ignored copied input and distinct ignored output are used.
- The copied input hash is unchanged after patching.
- The patched output exists and remains the expected 10,004-byte `.bes` shape.
- The result banner and output log surface the patch result in the UI.

## Not Proven

- This does not prove every private save variant.
- This does not patch the user's source save in place.
- This does not prove signed installer/MSIX behavior.
- This does not replace broader manual Save Editor workflow review.
