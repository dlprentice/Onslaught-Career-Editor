# WinUI Product Sprint Evidence

Status: in progress, first batch complete pending review
Last updated: 2026-05-04

## Baseline

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `git status --short --branch` | `[maintainer-private-checkout]` | PASS/WARN | Branch `wip/sandbox`; carried-forward uncommitted WinUI health docs/state were present. | Sprint started from the expected branch and preserved the prior no-commit health-pass diff. |
| `git rev-parse HEAD` | `[maintainer-private-checkout]` | PASS | `ace94b5b1d1f89812363fbd241d3cc30d96f572c` | Confirms the sprint started from the pushed three-lane strategy reset head. |

## Inspection

| Area | Result |
| --- | --- |
| `AGENTS.md` and three-lane docs | Confirmed WinUI primary product lane, Electron shelved support/workbench lane, active Python script/tooling support, and archived Python GUI/CLI plus WPF reference lanes. |
| WinUI shell and pages | Found stale product copy and Patch Bench wording that still treated the installed executable as the patch target. |
| `BinaryPatchesPage.xaml.cs` | Found the WinUI page loaded the configured game `BEA.exe` directly into the patch target textbox. |
| UiTests | Existing filtered active-lane tests passed before this sprint; added focused static product-lane assertions. |

## Changes

| File/area | Change | Safety note |
| --- | --- | --- |
| WinUI shell | Updated product copy, `Save Lab`, `Patch Bench`, and friendly footer game-directory label with tooltip. | No backend behavior change. |
| Save Lab | Updated page title and status prefix from `Saves` to `Save Lab`. | Naming/copy alignment only. |
| About page | Removed legacy-reference/Electron-primary wording and recorded WinUI as the primary user-facing Windows lane. | Product truth alignment only. |
| Settings page | Updated Patch Bench description to say it works on an app-owned executable copy. | Copy-only wording. |
| Patch Bench | Added source executable, create-working-copy action, read-only working copy target, and apply/restore guards requiring the working copy path under `%APPDATA%\OnslaughtCareerEditor\PatchBench\...`. | Original `BEA.exe` is treated as read-only source. |
| UiTests | Added product-lane tests for About copy, Patch Bench visible copy, copied-target code guard, and friendly footer label. | Static tests guard against strategy/safety drift. |

## Validation Commands

| Command | Working directory | Result | Important output | Blocker or reason skipped | What it proves |
| --- | --- | --- | --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | `[maintainer-private-checkout]` | PASS/WARN | Build succeeded. `0 Warning(s)`, `0 Error(s)`. SDK printed preview `.NET` informational `NETSDK1057`. | None. | WinUI product project still compiles after the shell/About/Patch Bench changes. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | `[maintainer-private-checkout]` | PASS/WARN | Passed `26/26`, failed `0`, skipped `0`. SDK printed preview `.NET` informational `NETSDK1057`. | None. | Active UI/static tests pass, including new WinUI product-lane, Save Lab naming, and copied-executable Patch Bench assertions. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | `[maintainer-private-checkout]` | PASS/WARN | Passed `19/19`, failed `0`, skipped `0`. SDK printed preview `.NET` informational `NETSDK1057`. | None. | Shared AppCore behavior remains healthy after WinUI shell/Patch Bench changes. |
| `py -3 tools\docsync_check.py` | `[maintainer-private-checkout]` | PASS | `Docsync policy check: PASS`. | None. | Canonical/lore-book mirrored docs remain synced. |
| `npm run test:doc-commands` | `[maintainer-private-checkout]` | FAIL, then PASS | First run failed because `.codex/state/winui-lane-health-evidence.md` used wording that looked like an invalid npm script reference. Wording was corrected, then final rerun passed with `321` documented npm script references checked. | Transient documentation wording issue fixed. | Documented npm command examples remain valid. |
| `npm run test:md-links` | `[maintainer-private-checkout]` | PASS | Markdown link check passed and wrote ignored audit output under `subagents/md-link-check/`. | None. | Markdown links remain valid after docs/state edits. |
| `npm run test:public-allowlist` | `[maintainer-private-checkout]` | PASS | Public allowlist safety check passed; rows checked changed from `1162` to `1163` after adding the new UiTest file. | None. | Public allowlist remains free of hard-deny families. |
| `npm run test:repo-hygiene` | `[maintainer-private-checkout]` | PASS | Hygiene unit tests passed; repo text hygiene check passed with `19` text and `2` path rules. | None. | Active docs/code avoid known stale wording and generated-output hygiene regressions. |
| `py -3 tools\release_profile_snapshot.py --check` | `[maintainer-private-checkout]` | FAIL, then PASS | First check found stale generated profile artifacts. `py -3 tools\release_profile_snapshot.py` regenerated them. After marking new files intent-to-add, profile artifacts were regenerated again; final rerun passed with `R0=1176 R2=0 R3=2 R4=18140`. | Stale generated artifacts refreshed. | Release profile accounting includes the new test file and `.codex` state files. |
| `py -3 tools\release_curated_manifest.py --check` | `[maintainer-private-checkout]` | FAIL, then PASS | First check found stale `public_candidate_allowlist.tsv` because `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs` was newly added. `py -3 tools\release_curated_manifest.py` regenerated it; rerun passed with `1163` selected files. | Stale generated allowlist refreshed. | Curated public allowlist remains synchronized with the manifest. |
| `node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('developer_agent_state.json','utf8')); JSON.parse(fs.readFileSync('documentation_agent_state.json','utf8')); console.log('state json ok')"` | `[maintainer-private-checkout]` | PASS | `state json ok`. | None. | Updated state JSON is parseable. |
| `git diff --check` | `[maintainer-private-checkout]` | PASS/WARN | Exit code 0. Git printed CRLF-normalization warnings for regenerated TSV files. | None. | Final diff has no whitespace errors. |

## Not Performed Yet

- Manual WinUI visual launch was not attempted in this first batch.
- No BEA.exe launch was performed.
- No executable patch apply was performed.
- No Electron or Python product work was performed.
- No public release-scope change was performed.
- No commit was made.
