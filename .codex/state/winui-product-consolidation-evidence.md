# WinUI Product Consolidation Evidence

Status: active
Last updated: 2026-05-04

## Baseline

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `git status --short --branch` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS/WARN | Working tree already had uncommitted WinUI health/product-sprint files. | Confirms the goal starts by preserving existing uncommitted work instead of clobbering it. |
| `git rev-parse HEAD` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | `ace94b5b1d1f89812363fbd241d3cc30d96f572c` | Confirms the goal starts from the pushed three-lane strategy reset head. |

## Commands Run So Far

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `Get-Content -Raw .gitignore` plus `.codex` listings | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | `.codex/goals` and `.codex/state` already exist; `.codex/**` is release-denied by policy even though tracked in this private branch. | Confirms the goal contract and ledger location are consistent with current repo practice. |
| `py -3 tools\release_profile_snapshot.py` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Regenerated classification/profile/private inventory. Counts: `R0=1144 R2=0 R3=2 R4=18175`. | Confirms release classification now treats WinUI as public-candidate source and Electron/UI as hard-excluded shelved workbench source. |
| `py -3 tools\release_curated_manifest.py` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Selected `1132` files; curated allowlist generation passed. | Confirms the curated public allowlist regenerated from the WinUI-first manifest. |
| `rg -n "^archive/electron-workbench/apps/electron|^archive/electron-workbench/packages/ui|^OnslaughtCareerEditor.WinUI" release/readiness/public_candidate_allowlist.tsv roadmap/release-allowlist-classification.tsv release/readiness/private_only_inventory.tsv` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Public allowlist includes WinUI rows and excludes Electron/UI rows; classification/private inventory record Electron/UI as `R4_DENY`. | Confirms the release surface flip is visible in generated evidence. |
| `git log --all --reverse --grep=Electron` and `git show <pre-electron>:README.MD` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | First Electron-migration commit found at `5a54c7fb...`; pre-Electron README identified WinUI as the active Windows app and C# CLI/AppCore as the support path. | Confirms the WinUI-first reset is consistent with the repo's pre-Electron product direction rather than a new invention. |
| `git log --all --reverse -- archive\legacy-python ...` plus `Get-Content archive\legacy-python\README.md` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | History shows the Python GUI/CLI parity lane before WinUI/Electron; archive README is now corrected to reference-only. | Confirms docs now distinguish the archived Python app from active script/tooling work. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Build succeeded with preview SDK informational output only. | Confirms the active WinUI product project builds after the inherited product-lane edits. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | 19/19 tests passed. | Confirms shared AppCore correctness tests still pass. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | 27/27 tests passed. | Confirms active UI/static tests, including WinUI product-lane guards and the no-visible-backtick copy guard, pass without legacy WPF-filtered tests. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiLaunchSmokeTests"` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | 1/1 explicit WinUI runtime smoke passed. | Confirms the built WinUI app launches in this desktop session, exposes the product shell/navigation, and can be closed by the test. |
| `Get-Process -Name OnslaughtCareerEditor.WinUI -ErrorAction SilentlyContinue \| Select-Object -Property Id,ProcessName,Path` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | No rows returned. | Confirms the explicit launch smoke did not leave a WinUI app process running. |
| `npm run test:cli-smoke` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Contracts, Electron main, and CLI packages built; CLI smoke passed with temp artifact root. | Confirms the active TypeScript automation lane remains healthy after release-policy changes. |
| `py -3 tools\docsync_check.py` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | `Docsync policy check: PASS`. | Confirms roadmap/lore mirrors affected by this batch are synchronized. |
| `rg -n '\`' OnslaughtCareerEditor.WinUI -g '*.cs' -g '*.xaml'` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | No WinUI page/source matches were found. | Confirms the Windows app no longer renders Markdown backticks in visible page copy. |
| `npm run test:doc-commands` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Documented npm script references checked: 317 after one false-positive evidence phrase was corrected. | Confirms active docs do not contain broken npm script references. |
| `npm run test:md-links` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Markdown link check passed; output written under ignored `subagents/md-link-check/`. | Confirms markdown links remain valid after docs edits. |
| `npm run test:repo-hygiene` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | 24 rule tests passed; live scan passed with 19 text and 2 path rules. | Confirms stale Electron/WinUI/Python/product-direction hygiene rules pass. |
| `py -3 tools\release_curated_manifest.py` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Regenerated allowlist after adding `OnslaughtCareerEditor.UiTests/WinUiLaunchSmokeTests.cs`; selected files: 1133. | Confirms the new public-safe WinUI smoke test is accounted for in generated release evidence. |
| `npm run test:public-allowlist` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Public allowlist safety check passed; rows checked: 1133. | Confirms the regenerated WinUI-first public candidate allowlist remains free of forbidden/private families. |
| `py -3 tools\release_profile_snapshot.py` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Regenerated profile artifacts after adding `OnslaughtCareerEditor.UiTests/WinUiLaunchSmokeTests.cs`; counts: `R0=1145 R2=0 R3=2 R4=18175`. | Confirms release profile artifacts account for the new public-safe WinUI smoke source file. |
| `py -3 tools\release_profile_snapshot.py --check` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Counts: `R0=1145 R2=0 R3=2 R4=18175`. | Confirms release classification artifacts are current. |
| `py -3 tools\release_curated_manifest.py --check` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | Selected files: 1133; curated allowlist check passed. | Confirms curated manifest and generated public allowlist are in sync. |
| `node -e "JSON.parse(...developer_agent_state.json...); JSON.parse(...documentation_agent_state.json...)"` | `C:\Users\david\source\Onslaught-Career-Editor-private` | PASS | `state json ok`. | Confirms state files remain valid JSON after state updates. |

## Pending Validation

Final whitespace/diff validation remains to be run after the last state update.
