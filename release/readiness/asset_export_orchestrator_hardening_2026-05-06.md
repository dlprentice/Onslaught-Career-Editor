# Asset Export Orchestrator Hardening - 2026-05-06

Status: public-safe RE/tooling evidence

## Scope

This note records the hardening pass that followed the initial full-corpus asset smoke. The initial full run completed but showed mesh conversion failures. Follow-up isolated tests showed the same mesh samples could export successfully, which pointed at legacy extractor process state or shared template-file locking rather than unsupported source files.

This report is public-safe. It does not include private absolute Windows paths, raw game asset paths, extracted PNG/FBX files, raw media files, screenshots, hashes of private payloads, data URLs, base64, copied executables, save contents, or proof JSON.

## Changes

| File | Change | Why |
| --- | --- | --- |
| `tools/BeaAssetExportHarness/Program.cs` | Error rows now include unwrapped target-invocation exception type/message plus wrapper details. Console errors also print the unwrapped exception. | Legacy extractor reflection failures previously collapsed to a generic target-invocation message, hiding actionable root cause detail. |
| `tools/export_game_assets.py` | Asset export now runs texture, loose-mesh, and embedded-mesh harness lanes as separate serial processes and writes a combined summary with `process_model = "separate_process_per_lane"`. | The legacy extractor touches shared runtime/template files and is safer when lanes do not share one process or run concurrently. |

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `dotnet build .\tools\BeaAssetExportHarness\BeaAssetExportHarness.csproj --nologo` | PASS | Build succeeded with one existing `Prefer32Bit` warning and no errors. | Confirms the harness diagnostic change compiles. |
| `py -3 tools\export_game_assets.py --game-root <read-only local install> --out-root subagents\asset_orchestrator_split_smoke_2026-05-06 --limit-archives 1 --limit-loose-textures 1 --limit-loose-meshes 1 --limit-embedded-bodies 1 --progress-every 1` | PASS | Bounded split-lane orchestrator smoke completed all phases; asset summary records `separate_process_per_lane`. | Confirms the new orchestrator process model works for a quick smoke. |
| `dotnet run ... export-loose-meshes ... --start-loose-meshes 142 --limit-loose-meshes 1` | PASS | A loose mesh that failed in the initial full run succeeded when run in an isolated lane. | Confirms the earlier failure was not a stable file-level unsupported-mesh result. |
| `dotnet run ... export-embedded-meshes ... --limit-embedded-bodies 1` | PASS | An embedded mesh body that failed in the initial full run succeeded when run in an isolated lane. | Confirms the embedded-mesh exporter can handle the sampled body when isolated. |
| Parallel loose/embedded lane experiment | WARN | Loose mesh export passed; embedded export had one file-lock failure against the legacy extractor template file while the loose lane was also running. | Confirms mesh export lanes should be serialized, not parallelized. |
| Serial full loose-mesh lane | PASS | 213 attempted, 213 succeeded, 0 failed. | Confirms full loose-mesh export coverage when the lane is isolated. |
| Serial full embedded-mesh lane | PASS | 139 attempted, 139 succeeded, 0 failed. | Confirms full embedded-mesh export coverage when the lane is isolated. |
| `py -3 tools\export_game_assets.py --game-root <read-only local install> --out-root subagents\asset_full_export_split_2026-05-06 --progress-every 200` | PASS | Full split-lane orchestrator completed: 847/847 textures, 213/213 loose meshes, 139/139 embedded meshes, language/video/catalog generation complete, 3,817 catalog entries. | Confirms current full-corpus backend extraction is GREEN with the split-lane process model. |

## What Is Proven

- Full current texture export works.
- Full current loose mesh export works when the lane is isolated.
- Full current embedded mesh export works when the lane is isolated.
- The Python orchestrator now avoids the legacy shared-process/shared-template-file failure mode by running asset lanes serially in separate processes.
- If a reflected extractor failure happens again, the manifest and console output will include the inner exception type/message.

## What Is Not Proven

- WinUI asset browser/preview integration.
- Public redistribution rights for extracted assets.
- Rebuildability of the full game from extracted assets.
- Semantic gameplay logic reconstruction.
- Safety of running loose and embedded mesh export lanes concurrently; observed evidence says not to do that.

## Release Validation

| Command | Result | Important output summary |
| --- | --- | --- |
| `py -3 -m py_compile tools\export_game_assets.py` | PASS | Python syntax check completed. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Profile counts `R0=1149 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Curated allowlist selected 1,137 files and passed. |
| `py -3 tools\docsync_check.py` | PASS | Protected docs mirrors are synchronized. |
| `npm run test:public-allowlist` | PASS | Public allowlist safety check passed for 1,137 rows. |
| `npm run test:repo-hygiene` | PASS | 24 hygiene tests passed and live scan passed. |
| `npm run test:md-links` | PASS | Markdown link check passed. |
| `npm run test:doc-commands` | PASS | 233 documented npm commands checked. |
| `node -e "<parse state/manifest JSON>"` | PASS | State files and curated manifest parse successfully. |
| `git diff --check` | PASS | No whitespace errors; generated TSV/inventory line-ending warnings only. |

## Privacy And Release Boundary

Generated extraction outputs, logs, catalogs, and private asset files remain under ignored local output. Public release accounting must continue to exclude generated asset payloads, raw media, private game paths, `subagents/**`, and any extracted PNG/FBX/media output unless a later review explicitly sanitizes and reclassifies a narrow public-safe fixture.
