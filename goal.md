# Active Goal Slice

Status: active
Last updated: 2026-06-25
Policy: `goal.policy.md`

## Current Slice

Start the next bounded WinUI modularity/test-hardening inspection: read the
Windowed & Mods safe-copy canceled/failed/restored/source-changed status copy
and receipt fallback guards after the safe-copy outcome text extraction, then
choose one small extraction or guard-hardening candidate only if it strengthens
claim boundaries without moving patch semantics, launch arguments, safe-copy
behavior, music behavior, online readiness, runtime proof, or release
packaging. Keep this slice read-first unless exact evidence supports a narrow
edit. Continue from this checkout:

`C:\Users\david\source\Onslaught-Career-Editor`

This repo is the normal day-to-day working repo. The former private checkout is
an archived comparison/source snapshot, not required for normal public
contributor work.

## Current Truth

- Static Ghidra closure remains complete: `6411/6411 = 100.00%`, static debt
  `0 / 0 / 0`, active current-risk re-audit `1179/1179 = 100.00%`.
- Public source is primary and is not a sparse export. Track useful source,
  tools, tests, RE notes, wave notes, state batons, agent reports, readiness
  notes, compact proof summaries, and non-secret/non-payload scratch text.
- Hard payloads remain local/ignored overlays: actual game executables/DLLs/
  archives/media, copied runtime profiles, arbitrary save/options payloads,
  raw screenshots/frame dumps, raw CDB logs, bulky generated proof captures,
  full Ghidra databases/backups, secrets, local config, caches, and build/test/
  package outputs.
- `game/`, `save-attempts/`, `local-rom-input/`, `mcps/`, `local-proofs/`, and
  `local-ghidra/` are maintainer-local ignored overlays in this checkout. They
  are useful locally but are not public clone requirements.
- `local-proofs/OnslaughtRuntimeProofArchive` and
  `local-ghidra/GhidraBackups` are ignored junctions to `G:` archives rather
  than duplicated on `C:`.
- The public app release `v1.0.7` is the latest published GitHub asset. It keeps
  the friendly wrapper layout, includes the generated short-path `lore-pack/`
  content pack, and avoids raw deep `lore-book/` paths that can hit Windows
  Explorer `0x80010135` path-too-long extraction failures.
- The source tree stages packaged public Lore library content through a
  generated short-path `lore-pack/` content pack. Package
  probes build and validate `lore-pack/onslaught-lore.v1.index.json` plus
  `lore-pack/onslaught-lore.v1.jsonl`, keep only short `lore-book/` entry files
  beside it, and reject raw deep `lore-book/` mirror leakage. The latest local
  package probe generated 943 public-safe offline Markdown/TXT Lore documents
  and passed launch/Home/Lore/Media smokes; external references may still open
  in the browser.
- The maintainer-local live Ghidra project path is
  `C:\Users\david\Ghidra\Projects\BEA.gpr` with store
  `C:\Users\david\Ghidra\Projects\BEA.rep\`. The repo tracks scripts, exports,
  ledgers, and docs instead of full binary project stores.
- Repo-specific Codex skill and Ghidra policy inventory is accepted in
  `release/readiness/repo_skills_ghidra_policy_inventory_2026-06-25.md`.
  The public repo remains durable through normal tracked docs/tools/state, not
  copied runtime `.codex/skills`; full Ghidra project stores remain local/
  ignored.
- Current WinUI Lore cleanup loads generated `lore-pack/` documents when present,
  falls back to `lore-book/BOOK.md` otherwise, keeps included document links
  inside the reader, and labels source/external links as browser actions.
- Windowed & Mods selected-state UX for safe-copy profiles and menu-background
  choices is accepted: visible selected button styling, plain selected-status
  text, UIA selected names, and focused runtime UIA/visual smoke coverage are in
  place. This did not change patch rows, byte patches, safe-copy launch
  behavior, online proof, music audible-output proof, rebuild proof, or
  installed-game mutation.
- Asset Library first-run catalog guidance is accepted: the page now tells
  users to generate a catalog from their own game install outside the app, load
  the generated export folder containing `asset_catalog/catalog.json` rather
  than the game install folder itself, and confirms the app does not bundle
  assets or generate catalogs in place. A focused AppCore regression confirms a
  game-install-shaped folder is not treated as a catalog candidate, and native
  UIA smoke verifies the first-run guide text is accessible.
- Asset Library export-folder QOL is accepted in
  `release/readiness/winui_asset_library_export_folder_qol_2026-06-25.md`.
  The browse action now says `Browse export folder`, the first-run guide says
  to use the install as source for the external extractor before loading the
  separate generated export folder, and missing-catalog status now calls out a
  selected full BEA install as the game install rather than a generated export
  folder. The focused implementation is committed as `9b27745b`. This did not
  change catalog resolution, service behavior, asset bundling, in-app
  extraction/generation, runtime proof, full 3D rendering, rebuild parity,
  release packaging, or installed-game mutation rules.
- Windowed & Mods selected-choice modularity is accepted in
  `release/readiness/winui_windowed_mods_selected_choice_modularity_2026-06-25.md`.
  Profile/menu-background selected-state UIA names and styles now flow through
  a small WinUI model/helper, while `BinaryPatchesPage` still owns selected-key
  predicates, profile matching, menu-color matching, safe-copy state, and patch
  semantics.
- Windowed & Mods menu-color selected-status text modularity is accepted in
  `release/readiness/winui_windowed_mods_menu_color_text_modularity_2026-06-25.md`.
  Raw `frontend_clear_screen_*` patch keys and key-to-kind mapping remain
  page-local in `BinaryPatchesPage`; `PatchBenchMenuColorSelectionText` formats
  enum values only. Runtime UIA smoke now covers red, green, black, and clear
  selected-status text. Focused PatchBench tests, WinUI build, native UIA smoke,
  patch-plan regression tests, primary WinUI lane, docs commands, Markdown
  links, hard-payload safety, public allowlist, and repo hygiene passed. This
  did not change patch rows, byte patches, safe-copy launch behavior, music
  replacement behavior, online status, runtime proof, AppCore correctness
  logic, release packaging, or installed-game mutation rules.
- Windowed & Mods patch-group helper modularity is accepted in
  `release/readiness/winui_windowed_mods_patch_group_helper_modularity_2026-06-25.md`.
  Patch group titles, order, descriptions, and missing-group fail-closed
  behavior now live in `PatchBenchPatchGroups`, while
  `BinaryPatchItemModel.FunctionalArea` and AppCore patch policy remain
  unchanged. Focused PatchBench tests, WinUI build, runtime UIA smoke, patch-
  plan regression tests, docs commands, Markdown links, hard-payload safety,
  public allowlist, repo hygiene, state JSON, and whitespace diff checks
  passed. The source slice is committed and pushed as `de1ccc0c`. This did not
  change patch catalog rows, byte changes,
  `FunctionalArea` mappings, selection/dependency/conflict policy, safe-copy
  creation/launch/music/online behavior, runtime proof, release packaging, or
  installed-game/original `BEA.exe` mutation rules.
- Windowed & Mods PatchBench presentation-helper boundary guard is accepted in
  `release/readiness/winui_patchbench_presentation_helper_boundary_guard_2026-06-25.md`.
  The static test now enumerates the current `PatchBench*` helper files and
  blocks behavior-bearing file/process, runtime-service, patch-engine,
  launch-plan, Host/Join, matchmaking, and release/package tokens from those
  helpers. WinUI primary lane, docs commands, Markdown links, hard-payload
  safety, public allowlist, repo hygiene, state JSON, and whitespace diff
  checks passed. The source slice is committed and pushed as `94e07124`. This
  is test hardening only; no production WinUI code or user behavior changed.
- Windowed & Mods advanced BEA.exe-only selection-summary text modularity is
  accepted in
  `release/readiness/winui_windowed_mods_advanced_summary_text_modularity_2026-06-25.md`.
  Advanced selection-summary copy now flows through
  `PatchBenchSelectedProfileText.BuildAdvancedCopySelectionSummary(...)`, while
  `BinaryPatchesPage` still owns selected-key matching, profile
  classification, `SetEquals`, `MatchSelectableSafeCopyProfileId`,
  `ProfilePresetId`, safe-copy manifests/signatures, launch, music, and online
  logic. Focused red/green source-shape tests, full PatchBench static tests,
  WinUI build, WinUI primary lane, a fresh WinUI UI test rerun, docs commands,
  Markdown links, hard-payload safety, public allowlist, repo hygiene,
  whitespace diff, and process cleanup checks passed. The source slice is
  committed as `0bf9f87a`. This did not change patch rows, byte patches,
  selected-key semantics, safe-copy launch behavior, music behavior, online
  readiness, runtime proof, release packaging, app release assets, or
  installed-game/original `BEA.exe` mutation rules.
- Windowed & Mods prepared safe-copy outcome text modularity is accepted in
  `release/readiness/winui_windowed_mods_safe_copy_outcome_text_modularity_2026-06-25.md`.
  Prepared safe-copy summary, operation log, and music replacement status copy
  now flow through `PatchBenchSafeCopyOutcomeText` using primitive
  presentation state. `BinaryPatchesPage` still owns AppCore service calls,
  result projection, safe-copy signatures, launch planning, process state,
  music staging state, receipt creation/rendering, and online/readiness
  behavior. Focused red/green guard tests, full PatchBench static tests, WinUI
  build, WinUI primary lane, docs commands, Markdown links, hard-payload
  safety, public allowlist, repo hygiene, whitespace diff, state JSON parse,
  and process cleanup checks passed. The source slice is committed and pushed as
  `3bd3bfb3`. This did not change patch rows, byte patches, selected-key
  semantics, launch arguments, copied-profile launch behavior, music
  replacement behavior, online readiness, runtime proof, release packaging, app
  release assets, or installed-game/original `BEA.exe` mutation rules.
- Windowed & Mods selected-profile text modularity is accepted in
  `release/readiness/winui_windowed_mods_selected_profile_text_modularity_2026-06-25.md`.
  Selected-profile status/details copy now flows through a small WinUI
  presentation model/helper, while `BinaryPatchesPage` still owns profile
  matching, selected patch keys, `ProfilePresetId`, safe-copy manifests, launch,
  music, and online logic. Focused build, static PatchBench guard, runtime UIA
  selected-state smoke, AppCore safe-copy profile validation, public allowlist,
  Markdown link, repo hygiene, state JSON, and diff checks passed.
- Adversarial review noted a pre-existing weak static guard around Enhanced
  Profile Preview and create-time music-swap reset. That is a next-slice
  test-hardening candidate, not behavior changed by the selected-profile text
  modularity slice.
- Windowed & Mods Enhanced Profile Preview music-swap guard hardening is
  accepted in
  `release/readiness/winui_enhanced_preview_music_swap_guard_2026-06-25.md`.
  Static tests now scope the no-music-swap default to the constructor, pin the
  default index/XAML item, and verify Enhanced Preview does not touch create-time
  music-swap controls or preset constants. Runtime UIA smoke now selects
  `BEA_02 over BEA_01`, invokes Enhanced Profile Preview, and verifies that
  selection remains unchanged. This is test hardening only; no user behavior
  changed.
- Windowed & Mods launch text modularity is accepted in
  `release/readiness/winui_windowed_mods_launch_text_modularity_2026-06-25.md`.
  Copied-profile launch boundary copy, launch modifier summaries, and stale/
  ready/error launch-readiness text now flow through small WinUI presentation
  models plus `PatchBenchLaunchText`, while `BinaryPatchesPage` still owns
  `LaunchPresetSelection`, `ApplyLaunchPreset`, `BuildSelectedLaunchArguments`,
  `TryBuildCopiedProfileLaunchPlan`, safe-copy launch, manifest handling, music,
  online readiness, and all AppCore calls. Focused static PatchBench tests,
  WinUI build, runtime UIA selected-state smoke, hard-payload safety, public
  allowlist, Markdown links, repo hygiene, state JSON parse, and whitespace diff
  checks passed.
- Windowed & Mods launch-preset selected-state UX is focused-validated in
  `release/readiness/winui_windowed_mods_launch_preset_selected_state_2026-06-25.md`.
  The seven launch preset buttons now reuse the selected-choice visual pattern
  and selected UIA names. Manual edits to launch-preset-owned controls clear
  the selected marker; savegame and create-time music-swap controls remain
  independent. Static guards keep selected UIA/style state out of launch
  argument construction, copied-profile launch planning, safe-copy signatures,
  runtime/preflight services, and online wording. Focused static PatchBench
  tests, WinUI build, runtime UIA smoke, docs command checks, hard-payload
  safety, public allowlist, Markdown links, repo hygiene, state JSON parse,
  whitespace diff check, and process cleanup checks passed. Commit
  `eeb9c299` pushed this slice to `origin/main`.
- Windowed & Mods choice-style helper modularity is accepted in
  `release/readiness/winui_windowed_mods_choice_style_helper_modularity_2026-06-25.md`.
  The repeated Patch Bench selected/normal style lookup now lives in
  `PatchBenchChoiceVisualState.ApplyPatchBenchChoiceStyles`, while
  `BinaryPatchesPage` still owns selected-key predicates, profile matching,
  menu-color matching, launch-preset selected marker, and manual-edit routing.
  Runtime UIA smoke now verifies launch-preset selected state clears after
  launch-owned checkbox, combo, and text edits while create-time music-swap
  selection remains independent. Focused static PatchBench tests, WinUI build,
  and runtime UIA smoke passed. No launch arguments, launch preset payloads,
  copied-profile launch behavior, safe-copy signatures/manifests, patch
  semantics, music, online/runtime proof, AppCore correctness logic, release
  packaging, or installed-game mutation rules changed. Commit `e2e0c07d`
  pushed this slice to `origin/main`.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof both exist.
- Music audible output is still not proven. The previous rejected live bundle
  showed CDB decode instants at about 44-46 seconds but raw WAV data spanning
  only about 11-12 seconds, so the accepted 2026-06-25 helper/materializer
  hardening now preserves/verifies wall-clock WAV data span, helper-authored
  padding metadata, and canonical WAV header/data-frame consistency before any
  later private live materializer attempt.
- Installed Steam game files and original `BEA.exe` remain read-only.

## Public Reproducible Gates

These are normal public source/release checks:

```powershell
git submodule update --init --recursive
node --version # v24.x
npm --version  # >=11.12 <12; npm@11.12.1 is the packageManager target
npm run test:hard-payload-safety
npm install
npm run build:winui
npm run build:cli
npm run build:host
npm run test:appcore
npm run test:winui
npm run test:winui-primary-lane
npm run test:winui-safe-copy-preflight
npm run test:winui-patch-engine-safety
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
npm run release:profile-check
npm run release:curated-check
npm run test:winui-zip-release-candidate-probe
```

## Maintainer-Local Evidence

These are useful only when the local archive/material exists; they are not
public clone setup requirements:

```powershell
py -3 tools\public_primary_migration_inventory.py --check --private-root C:\Users\david\source\Onslaught-Career-Editor-private --require-private-root
py -3 tools\winui_safe_copy_music_decode_window_correlation_diagnostic.py --check G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime\music-audible-live-20260624-144834\raw\decode-window-correlation-diagnostic.json
Get-Process BEA,cdb -ErrorAction SilentlyContinue
```

## Next Executable Work

1. Inspect `BinaryPatchesPage.xaml.cs`, current `PatchBench*` helpers, and
   focused PatchBench tests around safe-copy canceled/failed/restored/
   source-changed status copy and the defensive receipt `No Host/Join` fallback.
2. Use at least one specialist consult and one adversarial reviewer before any
   nontrivial edit.
3. If a small improvement is justified, keep it bounded to WinUI presentation
   models/helpers or source-shape/UIA guard hardening; validate with
   focused PatchBench/WinUI gates plus docs/state updates. If no edit is
   justified, record that decision and choose the next bounded UX/modularity
   slice.
4. Keep patch rows, byte changes, copied-profile launch behavior, safe-copy
   manifests/signatures, music replacement behavior, online/readiness gates,
   runtime proof, release packaging, and installed-game mutation rules out of
   this slice unless a concrete bug is found and documented.

## Stop Conditions

- Any step would mutate the installed Steam game folder or original `BEA.exe`.
- Any tracked file would add actual game executable/DLL/archive/media payload,
  arbitrary save/options payload, full Ghidra database/backup, raw CDB log,
  screenshot/frame dump, secret, `.env*`, copied runtime output, or build
  artifact.
- Online wording or UI implies player-ready online multiplayer before required
  distinct-endpoint and source-bound runtime proofs exist.
- A runtime proof requires unavailable operator hardware/endpoints and no other
  bounded progress remains.
- A static RE contradiction appears; stop product/runtime work and correct the
  static claim with bounded evidence first.
