# WinUI Configuration Editor Copied Options Smoke - 2026-05-06

Status: public-safe evidence

## Scope

This note records a focused native WinUI Configuration Editor interaction smoke against a copied private real `.bea` options snapshot. It does not embed screenshots, options contents, private absolute paths, raw bytes, copied files, data URLs, or base64.

## What Changed

- Added stable WinUI automation IDs for the Configuration Editor detected-file picker, input/output paths, controller config override, patch action, safety hint, output log, and copy-output action.
- Extended the desktop-only FlaUI smoke test with `ConfigurationEditor_PatchesCopiedOptionsThroughUiWhenProvided`.
- The smoke is gated by `ONSLAUGHT_WINUI_REAL_OPTIONS_PATH`, so normal test runs do not require private options files.
- The smoke copies the supplied private `.bea` into an ignored `subagents/` evidence folder, patches that copy to a distinct output file, verifies the copied input hash is unchanged, and captures a private screenshot.
- The visible Configuration Editor patch result now summarizes the selected output instead of printing full copied input/output paths in the primary UI.

## Private Visual Evidence

Ignored screenshot:

- `subagents/winui-configuration-editor-interaction/2026-05-06/01-configuration-editor-patched.png`

The screenshot shows the Configuration Editor patch summary and sanitized output after a successful copied-options patch. Private paths are intentionally not repeated here.

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` | FAIL then PASS | The first run failed on missing Configuration Editor automation IDs; after the XAML fix, the focused audit passed 1/1. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiSaveAnalyzerInteractionSmokeTests.ConfigurationEditor_PatchesCopiedOptionsThroughUiWhenProvided"` | FAIL then PASS | The first run exposed an initial-tab/navigation assumption; after selecting the Configuration Editor tab explicitly through UIA, the copied-options smoke passed 1/1. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 35/35 active UiTests passed. |
| `py -3 tools\release_profile_snapshot.py` | PASS | Regenerated release profile artifacts; final counts `R0=1182 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py` | PASS | Regenerated curated manifest and public allowlist; selected files: 1169. |
| `py -3 tools\docsync_check.py` | PASS | Dsync policy check passed. |
| `npm run test:doc-commands` | PASS | 380 documented npm commands checked. |
| `npm run test:md-links` | PASS | Markdown link check passed. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Release profile snapshot check passed; final counts `R0=1182 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Curated allowlist check passed; final selected files: 1169. |
| `npm run test:public-allowlist` | PASS | 1169 public allowlist rows checked. |
| `npm run test:repo-hygiene` | PASS | 24 hygiene unit tests passed; live scan checked 19 text and 2 path rules. |
| `node -e "<parse developer_agent_state.json, documentation_agent_state.json, curated_release_manifest.json>"` | PASS | `json parse ok`. |
| `git diff --check` | PASS | No whitespace errors; Git emitted CRLF normalization warnings for generated TSV files only. |

## Proven

- The WinUI Configuration Editor can patch a copied real private `.bea` through the desktop UI.
- The original supplied private options snapshot is not mutated by the smoke; only an ignored copied input and distinct ignored output are used.
- The copied input hash is unchanged after patching.
- The patched output exists and remains the expected 10,004-byte file shape.
- The primary patch output does not expose the copied input or copied output absolute path.
- Configuration Editor long-workflow controls now have stable automation IDs for UIA/FlaUI automation.

## Not Proven

- This does not prove every options/defaultoptions variant.
- This does not patch the user's installed or repo-local source options file in place.
- This does not prove every advanced keybind override combination.
- This does not prove signed installer/MSIX behavior.
- This does not replace broader manual Configuration Editor workflow review.
