# WinUI Patch Bench Copied Executable Smoke - 2026-05-06

Status: public-safe evidence

## Scope

This note records a focused native WinUI Patch Bench interaction smoke against a private local `BEA.exe` source. It does not embed screenshots, executable contents, private absolute paths, raw bytes, copied files, hash values, data URLs, or base64.

## What Changed

- Added stable WinUI automation IDs for Patch Bench source path, working-copy path, create-copy, verify, apply, restore, workflow hint, and operation log controls.
- Added an explicit desktop-only FlaUI smoke test, `WinUiPatchBenchInteractionSmokeTests.PatchBench_VerifiesAppliesAndRestoresCopiedExecutableWhenProvided`.
- The smoke is gated by `ONSLAUGHT_WINUI_REAL_BEA_EXE_PATH`, so normal test runs do not require a private executable.
- The smoke launches WinUI directly into Patch Bench with an ignored isolated app config root, creates an app-owned working copy, verifies selected byte patches, applies to the copy, restores from the backup, and asserts the source executable hash is unchanged.
- Patch Bench primary operation logs now summarize app-owned target and backup labels instead of showing full private working-copy paths by default.

## Private Visual Evidence

Ignored screenshot:

- `subagents/winui-patch-bench-interaction/2026-05-06/01-patch-bench-applied.png`

The screenshot is a scrolled workflow proof, not just a first-viewport proof. It shows Patch Bench after apply with selected patches, action state, and a path-summarized operation log. Private paths are intentionally not repeated here.

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench_VisibleCopyPromisesCopiedExecutableWorkflow|FullyQualifiedName~WinUiProductLaneTests.PatchBench_CodeRequiresAppOwnedWorkingCopyBeforeApply"` | PASS | 2/2 focused Patch Bench product-lane tests passed. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiPatchBenchInteractionSmokeTests.PatchBench_VerifiesAppliesAndRestoresCopiedExecutableWhenProvided"` | FAIL then PASS | Initial failures exposed test dedupe/wait-condition issues; final smoke passed after case-insensitive working-copy dedupe and restore-completion wait. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 33/33 active UiTests passed. |
| `py -3 tools\docsync_check.py` | PASS | Dsync policy check passed. |
| `npm run test:doc-commands` | PASS | 364 documented npm commands checked. |
| `npm run test:md-links` | PASS | Markdown link check passed. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Counts `R0=1176 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files: 1165; curated allowlist check passed. |
| `npm run test:public-allowlist` | PASS | 1165 rows checked. |
| `npm run test:repo-hygiene` | PASS | Repo text hygiene check passed. |
| `node -e "<parse developer_agent_state.json, documentation_agent_state.json, curated_release_manifest.json>"` | PASS | `json parse ok`. |
| `git diff --check` | PASS | No whitespace errors; Git emitted CRLF normalization warnings for generated release files only. |

## Proven

- Patch Bench can create an app-owned working copy from a private local `BEA.exe` source.
- Verification runs against the copied executable.
- Apply targets the copied executable only.
- A backup snapshot is created for the copied executable.
- Restore returns the working copy to the source hash captured at smoke start.
- The original source executable hash remains unchanged across create, apply, and restore.
- The primary Patch Bench operation log avoids full private source/working-copy paths by default.
- The desktop smoke scrolls to the action/output region before capturing visual evidence.

## Important Caveat

The private local source executable used for this smoke was already in a known patched state for the selected stable patch set. This smoke proves the copied Patch Bench workflow, idempotent apply handling, backup/restore behavior, and source preservation. It does not prove a first-time clean-retail-to-patched byte transition for this local source.

## Not Proven

- This does not mutate or launch the game.
- This does not patch the installed executable in place.
- This does not prove every catalog patch or every executable specimen.
- This does not prove signed installer/MSIX behavior.
