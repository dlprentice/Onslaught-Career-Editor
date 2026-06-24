# WinUI Lane Health Evidence

Status: complete pending review
Last updated: 2026-05-04

## Baseline Checks

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `git status --short --branch` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | `## wip/sandbox...origin/wip/sandbox`; no changed files at start. | The health pass started from a clean tracked tree on `wip/sandbox`. |
| `git rev-parse HEAD` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | `ace94b5b1d1f89812363fbd241d3cc30d96f572c` | Confirms the pass started from the pushed three-lane strategy reset head. |

## Project And Command Discovery

| File/area | Result |
| --- | --- |
| `AGENTS.md` | Confirms WinUI 3 is primary product lane and relevant .NET commands must run serially. |
| `roadmap/three-lane-product-strategy.md` | Confirms WinUI health is phase 2 and public WinUI scope remains deferred. |
| `.codex/goals/winui-lane-health.md` | Defines the health pass and allowed fixes. |
| `README.MD`, `CURRENT_CAPABILITIES.md`, `RELEASE_SCOPE_AND_TEST_COMMANDS.md` | Contain the WinUI/AppCore validation commands; minor command-doc drift was corrected. |
| `OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj` | WinUI project is `WinExe`, targets `net10.0-windows10.0.19041.0`, references AppCore, uses Windows App SDK `2.0.1`, and sets Windows App SDK self-contained properties. |
| `OnslaughtCareerEditor.Release.slnx` | Existing release support solution excludes WinUI and includes AppCore, AppCore.Host, AppCore.Tests, C# CLI, and UiTests. |
| `roadmap/app-validation-checklist.md` | Documents the WinUI run command: `dotnet run --project ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj"`. |

## Validation Commands

| Command | Working directory | Result | Important output | Blocker or reason skipped | What it proves |
| --- | --- | --- | --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS/WARN | Build succeeded. `0 Warning(s)`, `0 Error(s)`. Output assembly: `OnslaughtCareerEditor.WinUI\bin\Debug\net10.0-windows10.0.19041.0\win-x64\OnslaughtCareerEditor.WinUI.dll`. SDK printed preview `.NET` informational `NETSDK1057`. | None. | WinUI 3 product project and AppCore dependency currently compile. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS/WARN | Passed `19/19`, failed `0`, skipped `0`. SDK printed preview `.NET` informational `NETSDK1057`. | None. | Shared AppCore correctness tests pass for the Windows lane core. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS/WARN | Passed `21/21`, failed `0`, skipped `0`. SDK printed preview `.NET` informational `NETSDK1057`. | None. | Active non-legacy UI/static checks pass while excluding explicit archived WPF reference tests. |
| `dotnet build .\OnslaughtCareerEditor.Release.slnx --nologo` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS/WARN | Build succeeded. `0 Warning(s)`, `0 Error(s)`. Projects built: AppCore, C# CLI, AppCore.Tests, UiTests, AppCore.Host. SDK printed preview `.NET` informational `NETSDK1057`. | None. | Existing support/parity solution remains healthy even though WinUI builds separately. |
| `dotnet run --project .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj` | `C:\Users\david\source\Onslaught-Career-Editor-private` | SKIPPED | Command identified and documented. | UI launch proof was not required by this health pass; no interactive WinUI launch was attempted. | Establishes the run command for a later manual or UX/product smoke pass. |

## Docs And Diff Validation

These checks were run after command-documentation changes.

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `py -3 tools\docsync_check.py` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | `Docsync policy check: PASS` | Checks required canonical/lore-book mirrors after roadmap doc edits. |
| `npm run test:doc-commands` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | `NPM script documentation check: PASS`; `317` documented script references checked. | Checks documented npm script examples still map to actual scripts. |
| `npm run test:md-links` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Markdown link check passed and wrote ignored audit output under `subagents/md-link-check/`. | Checks tracked markdown links after doc edits. |
| `node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('developer_agent_state.json','utf8')); JSON.parse(fs.readFileSync('documentation_agent_state.json','utf8')); console.log('state json ok')"` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | `state json ok` | Confirms updated repo state JSON remains parseable. |
| `git diff --check` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | No whitespace errors. | Checks final diff hygiene. |

## Blockers

No build or test blockers were found.

## Non-Blocking Follow-Ups

- WinUI visual/manual launch smoke remains undone.
- WinUI About-page copy should be reviewed in the product sprint because it may still contain older strategy language.
- Public WinUI release scope remains deferred pending build/license/dependency/public-safety review.
- A separate Windows-lane solution can be considered later, but is not required for current health.

## Verdict

GREEN for WinUI build/test lane health. The next step should be a WinUI UX/product sprint, not build stabilization.
