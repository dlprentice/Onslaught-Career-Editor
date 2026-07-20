# WinUI Third-Party Notices

Status: generated release notice source

This file is generated from the active WinUI product, AppCore/support, CLI/support, and test project dependency graph plus local NuGet package metadata. Public ZIPs pair it with a generated `THIRD_PARTY_LICENSES/` bundle containing applicable package license/notice files and the .NET runtime notices.

Retail executables, user saves, bulk extracted assets, raw captures, local NuGet cache paths, and local machine paths are intentionally omitted.

## Binary Release Boundary

- Generate this file from the final restored/published dependency graph before any public binary release.
- Include applicable package license and notice files in the final installer/ZIP/MSIX output.
- Keep the dynamically loaded LibVLC components replaceable and retain the matching LGPL notice, license, and source links.
- Test-only dependencies are listed for repo transparency; they are not expected in the product runtime output unless test artifacts are distributed.

## Package Notices

| Package | Version | Lane | Direct reference | License signal | Copyright | Project/source | Release posture |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| `LibVLCSharp` | 3.9.7.1 | Product/runtime | WinUI product | LGPL-2.1-or-later (expression) | - | https://code.videolan.org/videolan/LibVLCSharp | Ship as separate replaceable libraries with the LGPL license and exact upstream source links. |
| `Markdig` | 0.34.0 | Product/runtime | AppCore support | BSD-2-Clause (expression) | Alexandre Mutel | https://github.com/xoofx/markdig | Include in final notices when redistributed. |
| `microsoft.netcore.platforms` | 1.1.0 | Product/runtime | transitive | http://go.microsoft.com/fwlink/?LinkId=329770 | © Microsoft Corporation.  All rights reserved. | https://dot.net/ | Microsoft license/notice terms must be included as applicable. |
| `Microsoft.Web.WebView2` | 1.0.3912.50 | Product/runtime | WinUI product | LICENSE.txt (file) | © Microsoft Corporation. All rights reserved. | https://aka.ms/webview | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windows.ai.machinelearning` | 2.0.300 | Product/runtime | transitive | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windows.sdk.buildtools` | 10.0.26100.4654 | Product/runtime | transitive | https://aka.ms/WinSDKLicenseURL | © Microsoft Corporation. All rights reserved. | https://aka.ms/WinSDKProjectURL | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windows.sdk.buildtools.msix` | 1.7.251221100 | Product/runtime | transitive | sdk_license.txt (file) | © Microsoft Corporation. All rights reserved. | https://aka.ms/WinSDKProjectURL | Microsoft license/notice terms must be included as applicable. |
| `Microsoft.WindowsAppSDK` | 2.0.1 | Product/runtime | WinUI product | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.ai` | 2.0.185 | Product/runtime | transitive | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.base` | 2.0.3 | Product/runtime | transitive | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.dwrite` | 2.0.26041403 | Product/runtime | transitive | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://aka.ms/WindowsAppSDK | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.foundation` | 2.0.20 | Product/runtime | transitive | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://aka.ms/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.interactiveexperiences` | 2.0.12 | Product/runtime | transitive | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://aka.ms/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.ml` | 2.0.300 | Product/runtime | transitive | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.runtime` | 2.0.1 | Product/runtime | transitive | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.widgets` | 2.0.4 | Product/runtime | transitive | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.winui` | 2.0.12 | Product/runtime | transitive | license.txt (file) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `NAudio` | 2.3.0 | Product/runtime | WinUI product | MIT (expression) | © Mark Heath 2026 | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.asio` | 2.3.0 | Product/runtime | transitive | MIT (expression) | © Mark Heath 2026 | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.core` | 2.0.0 | Product/runtime | transitive | MIT (expression) | © Mark Heath 2021 | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.core` | 2.3.0 | Product/runtime | transitive | MIT (expression) | © Mark Heath 2026 | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.midi` | 2.3.0 | Product/runtime | transitive | MIT (expression) | © Mark Heath 2026 | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `NAudio.Vorbis` | 1.5.0 | Product/runtime | AppCore support, WinUI product | MIT (expression) | Copyright © Andrew Ward 2021 | https://github.com/naudio/Vorbis | Include in final notices when redistributed. |
| `naudio.wasapi` | 2.3.0 | Product/runtime | transitive | MIT (expression) | © Mark Heath 2026 | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.winforms` | 2.3.0 | Product/runtime | transitive | MIT (expression) | © Mark Heath 2026 | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.winmm` | 2.3.0 | Product/runtime | transitive | MIT (expression) | © Mark Heath 2023 | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `netstandard.library` | 1.6.1 | Product/runtime | transitive | http://go.microsoft.com/fwlink/?LinkId=329770 | © Microsoft Corporation.  All rights reserved. | https://dot.net/ | Include in final notices when redistributed. |
| `nvorbis` | 0.10.4 | Product/runtime | transitive | LICENSE (file) | Copyright © Andrew Ward 2021 | https://github.com/NVorbis/NVorbis | Include in final notices when redistributed. |
| `sharpdx` | 4.2.0 | Product/runtime | transitive | http://sharpdx.org/License.txt | Copyright (c) 2010-2016 Alexandre Mutel | https://github.com/sharpdx/SharpDX.git | Include in final notices when redistributed. |
| `sharpdx.direct3d11` | 4.2.0 | Product/runtime | transitive | http://sharpdx.org/License.txt | Copyright (c) 2010-2016 Alexandre Mutel | https://github.com/sharpdx/SharpDX.git | Include in final notices when redistributed. |
| `sharpdx.dxgi` | 4.2.0 | Product/runtime | transitive | http://sharpdx.org/License.txt | Copyright (c) 2010-2016 Alexandre Mutel | https://github.com/sharpdx/SharpDX.git | Include in final notices when redistributed. |
| `system.numerics.tensors` | 9.0.0 | Product/runtime | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/runtime | Include in final notices when redistributed. |
| `VideoLAN.LibVLC.Windows` | 3.0.23.1 | Product/runtime | WinUI product | LGPL-2.1-or-later (expression) | - | https://code.videolan.org/videolan/libvlc-nuget | Ship as separate replaceable libraries with the LGPL license and exact upstream source links. |
| `System.CommandLine` | 2.0.0-beta4.22272.1 | Support tooling | C# CLI support | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/command-line-api | Include in final notices when redistributed. |
| `coverlet.collector` | 6.0.4 | Test-only | WinUI automation tests | MIT (expression) | - | https://github.com/coverlet-coverage/coverlet.git | Not expected in product runtime output; keep if test artifacts are distributed. |
| `FlaUI.Core` | 5.0.0 | Test-only | WinUI automation tests | LICENSE.txt (file) | Copyright (c) 2016-2024 | https://github.com/FlaUI/FlaUI | Not expected in product runtime output; keep if test artifacts are distributed. |
| `FlaUI.UIA3` | 5.0.0 | Test-only | WinUI automation tests | LICENSE.txt (file) | Copyright (c) 2016-2024 | https://github.com/FlaUI/FlaUI | Not expected in product runtime output; keep if test artifacts are distributed. |
| `interop.uiautomationclient` | 10.19041.0 | Test-only | transitive | LICENSE.txt (file) | Copyright (c) 2020 | https://github.com/Roemer/UIAutomation-Interop | Not expected in product runtime output; keep if test artifacts are distributed. |
| `microsoft.applicationinsights` | 2.22.0 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/Microsoft/ApplicationInsights-dotnet | Microsoft license/notice terms must be included as applicable. |
| `microsoft.codecoverage` | 17.14.0 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.codecoverage` | 17.14.1 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.net.test.sdk` | 17.14.0 | Test-only | WinUI automation tests | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.net.test.sdk` | 17.14.1 | Test-only | AppCore tests | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testing.extensions.telemetry` | 1.5.3 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/testfx | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testing.extensions.trxreport.abstractions` | 1.5.3 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/testfx | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testing.extensions.vstestbridge` | 1.5.3 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/testfx | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testing.platform` | 1.5.3 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/testfx | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testing.platform.msbuild` | 1.5.3 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/testfx | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testplatform.objectmodel` | 17.14.0 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testplatform.objectmodel` | 17.14.1 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testplatform.testhost` | 17.14.0 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testplatform.testhost` | 17.14.1 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.win32.systemevents` | 8.0.0 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/runtime | Microsoft license/notice terms must be included as applicable. |
| `newtonsoft.json` | 13.0.3 | Test-only | transitive | MIT (expression) | Copyright © James Newton-King 2008 | https://github.com/JamesNK/Newtonsoft.Json | Not expected in product runtime output; keep if test artifacts are distributed. |
| `NUnit` | 4.3.2 | Test-only | WinUI automation tests | MIT (expression) | Copyright (c) Charlie Poole, Rob Prouse and Contributors. MIT License. | https://github.com/nunit/nunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `nunit.analyzers` | 4.7.0 | Test-only | WinUI automation tests | MIT (expression) | Copyright (c) 2018-2025 NUnit project | https://github.com/nunit/nunit.analyzers | Not expected in product runtime output; keep if test artifacts are distributed. |
| `nunit3testadapter` | 5.0.0 | Test-only | WinUI automation tests | MIT (expression) | Copyright (c) 2011-2021 Charlie Poole, 2014-2025 Terje Sandstrom | https://github.com/nunit/nunit3-vs-adapter | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.codedom` | 8.0.0 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/runtime | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.configuration.configurationmanager` | 8.0.1 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/runtime | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.diagnostics.eventlog` | 8.0.1 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/runtime | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.diagnostics.performancecounter` | 8.0.1 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/runtime | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.drawing.common` | 8.0.10 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/winforms | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.management` | 8.0.0 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/runtime | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.security.cryptography.protecteddata` | 8.0.0 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/runtime | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.security.permissions` | 8.0.0 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/runtime | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.windows.extensions` | 8.0.0 | Test-only | transitive | MIT (expression) | © Microsoft Corporation. All rights reserved. | https://github.com/dotnet/runtime | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit` | 2.9.3 | Test-only | AppCore tests | Apache-2.0 (expression) | Copyright (C) .NET Foundation | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.abstractions` | 2.0.3 | Test-only | transitive | https://raw.githubusercontent.com/xunit/xunit/master/license.txt | - | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.analyzers` | 1.18.0 | Test-only | transitive | Apache-2.0 (expression) | Copyright (C) .NET Foundation | https://github.com/xunit/xunit.analyzers | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.assert` | 2.9.3 | Test-only | transitive | Apache-2.0 (expression) | Copyright (C) .NET Foundation | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.core` | 2.9.3 | Test-only | transitive | Apache-2.0 (expression) | Copyright (C) .NET Foundation | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.extensibility.core` | 2.9.3 | Test-only | transitive | Apache-2.0 (expression) | Copyright (C) .NET Foundation | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.extensibility.execution` | 2.9.3 | Test-only | transitive | Apache-2.0 (expression) | Copyright (C) .NET Foundation | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.runner.visualstudio` | 3.1.4 | Test-only | AppCore tests | Apache-2.0 (expression) | Copyright (C) .NET Foundation | https://github.com/xunit/visualstudio.xunit | Not expected in product runtime output; keep if test artifacts are distributed. |

## Required Final Packaging Checks

1. Publish the exact WinUI binary candidate.
2. Re-run `py -3 tools\generate_winui_third_party_notices.py --check` after restore/publish so dependency drift is visible.
3. Verify the package contains this notice plus the generated `THIRD_PARTY_LICENSES/` bundle for its actual published dependency graph.
4. Verify `THIRD_PARTY_LICENSES/README.txt` documents the separate LibVLC files, compatible replacement path, LGPL terms, and exact upstream source locations.
5. Keep retail executables, user saves, bulk extraction output, and raw proof artifacts outside the release package.

## Current Limitations

- This notice source is generated from restored project assets and local NuGet metadata, not from a signed installer artifact.
- The portable ZIP gate owns the final dependency-license bundle and checks it against the exact published graph.
- These notices record the distribution boundary; they are not legal advice or a rightsholder endorsement.
