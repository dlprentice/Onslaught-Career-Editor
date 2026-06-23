# WinUI Third-Party Notices Draft

Status: public-safe release readiness draft

This file is generated from the active WinUI product, AppCore/support, CLI/support, host/support, and test project dependency graph plus local NuGet package metadata. It is a source-controlled notice draft for review. It is not a signed-installer legal approval and is not proof that a final binary package contains every required notice file.

Private game files, extracted assets, screenshots, copied executables, runtime proof, local NuGet cache paths, and local machine paths are intentionally omitted.

## Binary Release Boundary

- Generate this file from the final restored/published dependency graph before any public binary release.
- Include applicable package license and notice files in the final installer/ZIP/MSIX output.
- LGPL-bearing LibVLC packages require a focused redistribution review for the chosen binary shape.
- Test-only dependencies are listed for repo transparency; they are not expected in the product runtime output unless test artifacts are distributed.

## Package Notices

| Package | Version | Lane | Direct reference | License signal | Project/source | Release posture |
| --- | ---: | --- | --- | --- | --- | --- |
| `LibVLCSharp` | 3.9.7.1 | Product/runtime | WinUI product | LGPL-2.1-or-later (expression) | https://code.videolan.org/videolan/LibVLCSharp | LGPL/media redistribution review required before public binaries. |
| `Markdig` | 0.34.0 | Product/runtime | AppCore support | BSD-2-Clause (expression) | https://github.com/lunet-io/markdig | Include in final notices when redistributed. |
| `microsoft.netcore.platforms` | 1.1.0 | Product/runtime | transitive | http://go.microsoft.com/fwlink/?LinkId=329770 | https://dot.net/ | Microsoft license/notice terms must be included as applicable. |
| `Microsoft.Web.WebView2` | 1.0.3912.50 | Product/runtime | WinUI product | LICENSE.txt (file) | https://aka.ms/webview | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windows.ai.machinelearning` | 2.0.300 | Product/runtime | transitive | license.txt (file) | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windows.sdk.buildtools` | 10.0.26100.4654 | Product/runtime | transitive | https://aka.ms/WinSDKLicenseURL | https://aka.ms/WinSDKProjectURL | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windows.sdk.buildtools.msix` | 1.7.251221100 | Product/runtime | transitive | sdk_license.txt (file) | https://aka.ms/WinSDKProjectURL | Microsoft license/notice terms must be included as applicable. |
| `Microsoft.WindowsAppSDK` | 2.0.1 | Product/runtime | WinUI product | license.txt (file) | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.ai` | 2.0.185 | Product/runtime | transitive | license.txt (file) | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.base` | 2.0.3 | Product/runtime | transitive | license.txt (file) | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.dwrite` | 2.0.26041403 | Product/runtime | transitive | license.txt (file) | https://aka.ms/WindowsAppSDK | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.foundation` | 2.0.20 | Product/runtime | transitive | license.txt (file) | https://aka.ms/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.interactiveexperiences` | 2.0.12 | Product/runtime | transitive | license.txt (file) | https://aka.ms/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.ml` | 2.0.300 | Product/runtime | transitive | license.txt (file) | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.runtime` | 2.0.1 | Product/runtime | transitive | license.txt (file) | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.widgets` | 2.0.4 | Product/runtime | transitive | license.txt (file) | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `microsoft.windowsappsdk.winui` | 2.0.12 | Product/runtime | transitive | license.txt (file) | https://github.com/microsoft/windowsappsdk | Microsoft license/notice terms must be included as applicable. |
| `NAudio` | 2.3.0 | Product/runtime | WinUI product | MIT (expression) | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.asio` | 2.3.0 | Product/runtime | transitive | MIT (expression) | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.core` | 2.0.0 | Product/runtime | transitive | MIT (expression) | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.core` | 2.3.0 | Product/runtime | transitive | MIT (expression) | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.midi` | 2.3.0 | Product/runtime | transitive | MIT (expression) | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `NAudio.Vorbis` | 1.5.0 | Product/runtime | AppCore support, WinUI product | MIT (expression) | https://github.com/naudio/Vorbis | Include in final notices when redistributed. |
| `naudio.wasapi` | 2.3.0 | Product/runtime | transitive | MIT (expression) | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.winforms` | 2.3.0 | Product/runtime | transitive | MIT (expression) | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `naudio.winmm` | 2.3.0 | Product/runtime | transitive | MIT (expression) | https://github.com/naudio/NAudio | Include in final notices when redistributed. |
| `netstandard.library` | 1.6.1 | Product/runtime | transitive | http://go.microsoft.com/fwlink/?LinkId=329770 | https://dot.net/ | Include in final notices when redistributed. |
| `nvorbis` | 0.10.4 | Product/runtime | transitive | LICENSE (file) | https://github.com/NVorbis/NVorbis | Include in final notices when redistributed. |
| `sharpdx` | 4.2.0 | Product/runtime | transitive | http://sharpdx.org/License.txt | http://sharpdx.org/ | Include in final notices when redistributed. |
| `sharpdx.direct3d11` | 4.2.0 | Product/runtime | transitive | http://sharpdx.org/License.txt | http://sharpdx.org/ | Include in final notices when redistributed. |
| `sharpdx.dxgi` | 4.2.0 | Product/runtime | transitive | http://sharpdx.org/License.txt | http://sharpdx.org/ | Include in final notices when redistributed. |
| `system.numerics.tensors` | 9.0.0 | Product/runtime | transitive | MIT (expression) | https://dot.net/ | Include in final notices when redistributed. |
| `VideoLAN.LibVLC.Windows` | 3.0.23.1 | Product/runtime | WinUI product | LGPL-2.1-or-later (expression) | https://code.videolan.org/videolan/libvlc-nuget | LGPL/media redistribution review required before public binaries. |
| `System.CommandLine` | 2.0.0-beta4.22272.1 | Support tooling | C# CLI support | MIT (expression) | https://github.com/dotnet/command-line-api | Include in final notices when redistributed. |
| `coverlet.collector` | 6.0.4 | Test-only | WinUI automation tests | MIT (expression) | https://github.com/coverlet-coverage/coverlet | Not expected in product runtime output; keep if test artifacts are distributed. |
| `FlaUI.Core` | 5.0.0 | Test-only | WinUI automation tests | LICENSE.txt (file) | https://github.com/FlaUI/FlaUI | Not expected in product runtime output; keep if test artifacts are distributed. |
| `FlaUI.UIA3` | 5.0.0 | Test-only | WinUI automation tests | LICENSE.txt (file) | https://github.com/FlaUI/FlaUI | Not expected in product runtime output; keep if test artifacts are distributed. |
| `interop.uiautomationclient` | 10.19041.0 | Test-only | transitive | LICENSE.txt (file) | https://github.com/Roemer/UIAutomation-Interop | Not expected in product runtime output; keep if test artifacts are distributed. |
| `microsoft.applicationinsights` | 2.22.0 | Test-only | transitive | MIT (expression) | https://go.microsoft.com/fwlink/?LinkId=392727 | Microsoft license/notice terms must be included as applicable. |
| `microsoft.codecoverage` | 17.14.0 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.codecoverage` | 17.14.1 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.net.test.sdk` | 17.14.0 | Test-only | WinUI automation tests | MIT (expression) | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.net.test.sdk` | 17.14.1 | Test-only | AppCore tests | MIT (expression) | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testing.extensions.telemetry` | 1.5.3 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/testfx | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testing.extensions.trxreport.abstractions` | 1.5.3 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/testfx | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testing.extensions.vstestbridge` | 1.5.3 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/testfx | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testing.platform` | 1.5.3 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/testfx | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testing.platform.msbuild` | 1.5.3 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/testfx | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testplatform.objectmodel` | 17.14.0 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testplatform.objectmodel` | 17.14.1 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testplatform.testhost` | 17.14.0 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.testplatform.testhost` | 17.14.1 | Test-only | transitive | MIT (expression) | https://github.com/microsoft/vstest | Microsoft license/notice terms must be included as applicable. |
| `microsoft.win32.systemevents` | 8.0.0 | Test-only | transitive | MIT (expression) | https://dot.net/ | Microsoft license/notice terms must be included as applicable. |
| `newtonsoft.json` | 13.0.3 | Test-only | transitive | MIT (expression) | https://www.newtonsoft.com/json | Not expected in product runtime output; keep if test artifacts are distributed. |
| `NUnit` | 4.3.2 | Test-only | WinUI automation tests | MIT (expression) | https://nunit.org/ | Not expected in product runtime output; keep if test artifacts are distributed. |
| `nunit.analyzers` | 4.7.0 | Test-only | WinUI automation tests | MIT (expression) | https://github.com/nunit/nunit.analyzers | Not expected in product runtime output; keep if test artifacts are distributed. |
| `nunit3testadapter` | 5.0.0 | Test-only | WinUI automation tests | MIT (expression) | https://docs.nunit.org/articles/vs-test-adapter/Index.html | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.codedom` | 8.0.0 | Test-only | transitive | MIT (expression) | https://dot.net/ | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.configuration.configurationmanager` | 8.0.1 | Test-only | transitive | MIT (expression) | https://dot.net/ | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.diagnostics.eventlog` | 8.0.1 | Test-only | transitive | MIT (expression) | https://dot.net/ | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.diagnostics.performancecounter` | 8.0.1 | Test-only | transitive | MIT (expression) | https://dot.net/ | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.drawing.common` | 8.0.10 | Test-only | transitive | MIT (expression) | https://github.com/dotnet/winforms | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.management` | 8.0.0 | Test-only | transitive | MIT (expression) | https://dot.net/ | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.security.cryptography.protecteddata` | 8.0.0 | Test-only | transitive | MIT (expression) | https://dot.net/ | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.security.permissions` | 8.0.0 | Test-only | transitive | MIT (expression) | https://dot.net/ | Not expected in product runtime output; keep if test artifacts are distributed. |
| `system.windows.extensions` | 8.0.0 | Test-only | transitive | MIT (expression) | https://dot.net/ | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit` | 2.9.3 | Test-only | AppCore tests | Apache-2.0 (expression) | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.abstractions` | 2.0.3 | Test-only | transitive | https://raw.githubusercontent.com/xunit/xunit/master/license.txt | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.analyzers` | 1.18.0 | Test-only | transitive | Apache-2.0 (expression) | https://github.com/xunit/xunit.analyzers | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.assert` | 2.9.3 | Test-only | transitive | Apache-2.0 (expression) | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.core` | 2.9.3 | Test-only | transitive | Apache-2.0 (expression) | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.extensibility.core` | 2.9.3 | Test-only | transitive | Apache-2.0 (expression) | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.extensibility.execution` | 2.9.3 | Test-only | transitive | Apache-2.0 (expression) | https://github.com/xunit/xunit | Not expected in product runtime output; keep if test artifacts are distributed. |
| `xunit.runner.visualstudio` | 3.1.4 | Test-only | AppCore tests | Apache-2.0 (expression) | https://github.com/xunit/visualstudio.xunit | Not expected in product runtime output; keep if test artifacts are distributed. |

## Required Final Packaging Checks

1. Publish the exact WinUI binary candidate.
2. Re-run `py -3 tools\generate_winui_third_party_notices.py --check` after restore/publish so dependency drift is visible.
3. Verify the package contains this notice draft or a final derivative plus package-provided license/notice files required by redistributed dependencies.
4. Document the LGPL strategy for `LibVLCSharp` and `VideoLAN.LibVLC.Windows`, including how users can replace or relink the LGPL-covered components if required by the final distribution shape.
5. Keep private game assets and private proof artifacts outside the release package.

## Current Limitations

- This draft is generated from restored project assets and local NuGet metadata, not from a signed installer artifact.
- It does not embed full third-party license texts; final packaging must include license files where package terms require them.
- It does not grant legal approval for redistribution.
