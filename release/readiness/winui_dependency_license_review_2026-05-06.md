# WinUI Dependency And License Review - 2026-05-06

Status: public-safe release readiness evidence

## Scope

This note records a release-facing dependency and license review for the current WinUI-first product lane. It is not a signed-installer approval. It proves the current package surface is inventoried, the current vulnerability check is clean against configured NuGet sources, and the main binary redistribution obligations are visible before a public Windows installer or ZIP is claimed.

This report is public-safe. It does not include private game paths, extracted game assets, screenshots, runtime evidence, copied executables, raw package payloads, or local proof JSON.

## Commands Run

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `dotnet list .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj package --include-transitive` | PASS | Listed WinUI direct packages and transitive packages for `net10.0-windows10.0.19041.0`. | Captures the current primary product dependency surface. |
| `dotnet list .\OnslaughtCareerEditor.Release.slnx package --include-transitive` | PASS | Listed AppCore, C# CLI, AppCore.Host, AppCore.Tests, and UiTests package surfaces. | Captures the current support/parity solution dependency surface. |
| `dotnet list .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj package --vulnerable --include-transitive` | PASS | NuGet reported no vulnerable packages for the WinUI project from the configured sources. | Confirms no currently reported NuGet advisory hit for the primary product project. |
| `dotnet list .\OnslaughtCareerEditor.Release.slnx package --vulnerable --include-transitive` | PASS | NuGet reported no vulnerable packages for the support/parity solution projects from the configured sources. | Confirms no currently reported NuGet advisory hit in the retained support/parity solution. |
| `dotnet list .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj package --outdated` | PASS | After the Windows App SDK 2.x migration, NuGet reports no direct WinUI package updates from the configured sources. | Confirms the primary WinUI direct package set is current for the configured feeds. |
| Local NuGet `.nuspec` / license-file metadata inspection | PASS | Direct WinUI package licenses were identifiable from local package metadata. | Confirms the dependency/license review is grounded in installed NuGet package metadata. |

## Primary WinUI Direct Packages

| Package | Current version | License signal from local NuGet metadata | Release posture |
| --- | ---: | --- | --- |
| `LibVLCSharp` | `3.9.7.1` | `LGPL-2.1-or-later` | Allowed only with explicit LGPL notice/compliance review before binary redistribution. |
| `Microsoft.Web.WebView2` | `1.0.3912.50` | package `LICENSE.txt` | Requires Microsoft license notice review for redistributed binaries. |
| `Microsoft.WindowsAppSDK` | `2.0.1` | Microsoft Windows App SDK license terms | Requires Microsoft license notice review; self-contained WinUI output may carry runtime components. |
| `NAudio` | `2.3.0` | MIT-style package license file | Low friction; include notice if packaging third-party notices. |
| `NAudio.Vorbis` | `1.5.0` | MIT | Low friction; include notice if packaging third-party notices. |
| `VideoLAN.LibVLC.Windows` | `3.0.23.1` | `LGPL-2.1-or-later` | Allowed only with explicit LGPL notice/compliance review before binary redistribution. |

## Support/Parity Packages

The retained support and test lanes include `Markdig`, `System.CommandLine`, `xunit`, `NUnit`, `FlaUI`, `coverlet.collector`, and Microsoft test platform packages. These are source/test/support dependencies, not proof of installer readiness by themselves. They remain acceptable for source candidate review, but any distributed binary package should generate a third-party notices file from the final resolved dependency set.

## Dependency Freshness

NuGet reported these WinUI direct packages as newer before the compatibility update:

- `LibVLCSharp`
- `Microsoft.Web.WebView2`
- `Microsoft.WindowsAppSDK`
- `NAudio`
- `VideoLAN.LibVLC.Windows`

The non-major runtime/media packages were upgraded in `release/readiness/winui_dependency_compatibility_update_2026-05-06.md` and validated with WinUI build, AppCore tests, active UiTests, and native Media interaction smoke. Windows App SDK `2.x` was then migrated and validated separately in `release/readiness/winui_windows_appsdk2_migration_2026-05-06.md`.

## Solution Structure Note

`OnslaughtCareerEditor.Release.slnx` intentionally remains a retained support/parity solution for AppCore, AppCore.Host, AppCore.Tests, the C# CLI, and UiTests. It does not include the WinUI project. Current release docs correctly require the explicit WinUI project build/publish commands in addition to the support/parity solution build.

If future release automation wants one Windows-lane entry point, prefer a separate `OnslaughtCareerEditor.WinUI.slnx` or a clearly named product-lane solution rather than silently changing the meaning of `OnslaughtCareerEditor.Release.slnx`.

## What Is Proven

- Current WinUI direct and transitive NuGet dependencies are inventoried.
- Current support/parity NuGet dependencies are inventoried.
- Configured NuGet advisory sources reported no vulnerable packages for WinUI or the support/parity solution.
- LGPL-bearing media packages are explicitly identified as binary redistribution review items.
- Dependency updates are visible but deferred to a compatibility slice.

## Follow-Up Completed After This Review

`release/readiness/THIRD_PARTY_NOTICES.winui-draft.md` now provides a source-controlled draft notice file generated from restored project assets and local NuGet metadata. `release/readiness/winui_lgpl_redistribution_review_2026-05-06.md` records the current LGPL binary-release checklist for LibVLCSharp and VideoLAN.LibVLC.Windows.

`release/readiness/winui_dependency_compatibility_update_2026-05-06.md` records the validated non-major WinUI runtime/media package updates. `release/readiness/winui_windows_appsdk2_migration_2026-05-06.md` records the Windows App SDK `2.0.1` migration. `release/readiness/winui_published_notice_inclusion_2026-05-06.md` records that disposable publish output includes `THIRD_PARTY_NOTICES.md`.

## What Is Not Proven

- Signed installer/MSIX/ZIP redistribution compliance.
- Store submission readiness.
- Legal approval for public redistribution of game-origin assets or private media.

## Required Follow-Up Before Public Binary Release

1. Complete legal/compliance review for LGPL obligations in the chosen binary distribution shape.
2. Re-run WinUI build, publish, launch smoke, Media interaction smoke, and public release policy checks after any future dependency upgrade.
3. Keep private game assets, extracted assets, runtime proof, copied executables, and local screenshots outside public release scope.
