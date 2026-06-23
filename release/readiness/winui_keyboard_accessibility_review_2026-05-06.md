# WinUI Keyboard Accessibility Review - 2026-05-06

Status: public-safe evidence

## Scope

This note records a focused WinUI keyboard accessibility hardening pass for primary shell actions. It does not claim full accessibility certification, screen-reader certification, or a complete keyboard-only workflow audit.

## What Changed

- Added unique WinUI `AccessKey` values for the primary shell setup action and top navigation items.
- Extended `WinUiAccessibilityAuditTests` with `PrimaryShellActions_ExposeUniqueKeyboardAccessKeys`.
- The test first failed because the shell controls had stable automation IDs but no access keys; after adding the access keys, the focused audit passed.
- Accessibility Insights for Windows was not found in the standard local install paths during this pass, so no Accessibility Insights report is claimed here.

## Access Keys

| Control | Access key |
| --- | --- |
| Review Setup | `R` |
| Home | `H` |
| Save Lab | `S` |
| Media | `M` |
| Asset Library | `A` |
| Lore | `L` |
| Patch Bench | `P` |
| Settings | `T` |
| About | `B` |

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellActions"` | FAIL then PASS | The first compile attempt exposed a test API mistake; the corrected red test then failed on missing access keys; after XAML updates, the focused test passed 1/1. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 36/36 active UiTests passed. |
| `py -3 tools\release_profile_snapshot.py` | PASS | Regenerated release profile artifacts; counts `R0=1183 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py` | PASS | Regenerated curated manifest and public allowlist; selected files: 1170. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Release profile snapshot check passed; counts `R0=1183 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Curated allowlist check passed; selected files: 1170. |
| `py -3 tools\docsync_check.py` | PASS | Dsync policy check passed. |
| `npm run test:doc-commands` | PASS | 388 documented npm commands checked. |
| `npm run test:md-links` | PASS | Markdown link check passed. |
| `npm run test:public-allowlist` | PASS | 1170 public allowlist rows checked. |
| `npm run test:repo-hygiene` | PASS | 24 hygiene unit tests passed; live scan checked 19 text and 2 path rules. |

## Proven

- Primary shell navigation and setup action have stable keyboard access-key declarations.
- The access keys are unique within the primary shell set.
- The active WinUI static/product-lane test suite remains green after the accessibility change.

## Not Proven

- This is not a full screen-reader audit.
- This is not a full tab-order audit for every nested control on every page.
- This does not prove every long workflow can be completed keyboard-only.
- This does not replace a future Accessibility Insights or equivalent manual audit before public binary release.
