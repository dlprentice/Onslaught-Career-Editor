# WinUI Published Notice Inclusion - 2026-05-06

Status: public-safe release readiness evidence

## Scope

This note records the focused publish-output notice inclusion pass for the WinUI-first product lane. It ensures disposable WinUI publish folders include the generated third-party notice draft as `THIRD_PARTY_NOTICES.md`.

This report is public-safe. It does not include private game paths, screenshots, copied executables, extracted assets, runtime proof JSON, local NuGet cache paths, or generated publish output contents.

## What Changed

- Added a WinUI publish target, `CopyWinUINoticesToPublishDirectory`.
- The target copies `release/readiness/THIRD_PARTY_NOTICES.winui-draft.md` into publish output as `THIRD_PARTY_NOTICES.md`.
- Added a static WinUI product-lane test that guards the publish notice target and destination filename.

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.WinUiPublish_CopiesThirdPartyNoticesIntoPublishOutput"` | PASS | 1/1 focused product-lane test passed. | Confirms source contains the publish notice target and expected notice filenames. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. | Confirms the publish target does not break WinUI build. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | 11/11 focused product-lane tests passed. | Confirms the product-lane static checks remain green. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 32/32 active UiTests passed. | Confirms active WinUI automation remains green. |
| `dotnet publish .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj -c Release -r win-x64 --self-contained true -o .\subagents\winui-notice-publish-smoke\2026-05-06\publish --nologo` | PASS | Publish completed. | Confirms disposable unpackaged publish still works. |
| Publish output notice check | PASS | `THIRD_PARTY_NOTICES.md` exists in the publish root, has nonzero byte size, and the app PRI still exists. | Confirms the generated notice is actually included in disposable publish output. |
| Published launch smoke with `ONSLAUGHT_WINUI_TEST_EXE_PATH` | PASS | 1/1 launch smoke passed against the disposable published executable. | Confirms notice inclusion does not break published app startup. |
| Guarded process check | PASS | No `OnslaughtCareerEditor.WinUI` process remained after smoke. | Confirms the smoke did not leave the app running. |

## What Is Proven

- WinUI publish output includes `THIRD_PARTY_NOTICES.md`.
- The included notice is generated from the current source-controlled WinUI notice draft.
- The publish output still includes the required app PRI resource.
- The disposable published executable still launches after notice inclusion.

## What Is Not Proven

- Legal/compliance approval for the final notice text.
- Signed installer/MSIX install/uninstall flow.
- SmartScreen, trust, or store-submission posture.
- Public redistribution approval for any private game-origin assets.

## Current Decision

Keep the publish-output notice inclusion target. Treat legal/compliance approval and signed installer-grade release work as separate future release gates.
