---
status: archived/reference workbench architecture; superseded as product strategy
last_updated: 2026-05-26
doc_version: 1.4
---

> **SUPERSEDED as product strategy:** WinUI 3 is the primary user-facing product lane. This document records the **archived** Electron/React/TypeScript workbench under `archive/electron-workbench/`. Do not treat Electron as an active community product surface. Current strategy: [three-lane-product-strategy.md](three-lane-product-strategy.md).

# Electron Workbench Architecture

## Direction

This document now describes the archived Electron maintainer/agentic RE workbench record. It is no longer the primary product strategy. The canonical product strategy is [three-lane-product-strategy.md](three-lane-product-strategy.md): WinUI 3 is the primary user-facing Windows product lane, Electron is archived/reference infrastructure, active Python scripts are RE/tooling/lab support, and the historical Python GUI/CLI app is archived/reference.

The archived Electron + TypeScript workbench remains useful for typed IPC/job boundaries, Browser Use validation, Ghidra/CDB/game-harness workflows, release-policy inspection, diagnostics, and automation when that support lane is explicitly in scope. Halt broad Electron product polish and broad visual redesign unless it is required for maintainer workflow correctness, job-runner safety, security, IPC integrity, or test stability.

Application shape decision for this lane: keep one Electron codebase for maintainer workflows and automation, not a second polished community product app. If public distribution later needs an Electron support bundle, cut it from the same contracts and job runner without changing the WinUI-first product focus.

## Why

The project still needs a browser-testable automation loop:

- project maintainers who need a controlled reverse-engineering workbench for patches, Ghidra exports, debugger probes, game capture, and evidence trails;
- browser-driven automation, including Browser Use, that can operate the same UI humans use when a visual loop is the right way to validate behavior.

Electron gives the project a browser-testable renderer while still allowing a native desktop shell for files, process launch, capture, and local tool integration.

Default workbench posture: the first screen should make sense to maintainers and agents doing inspection, patch proof, release safety checks, or runtime evidence. It does not need to carry the full community product polish burden now assigned to WinUI 3.

The two lanes should share the same typed job system, artifact ledger, game-profile model, and curated content index. Separation comes from navigation, audience labels, release policy, feature flags, and packaging profiles, not duplicated parsers or a second renderer.

## Stack

- Electron for the desktop host.
- React + TypeScript + Vite for the renderer.
- Tailwind + shadcn-style editable components for the UI system.
- Typed preload/context bridge for renderer-to-main calls.
- Browser mode at `http://127.0.0.1:3000` for fast UI testing and Browser Use inspection.
- Electron/Playwright integration tests later for native file, IPC, and process behavior.

## Architecture Rules

- The renderer must not get raw Node, shell, debugger, or filesystem access.
- The preload bridge exposes narrow typed APIs only.
- Native work is job-based: no raw command strings from the renderer.
- Mutating jobs require explicit approval and must run against copied profiles by default.
- Community workflows must be useful without exposing maintainer-only debugging controls by default.
- Maintainer workflows may use Ghidra, CDB, process launch, and harness jobs only through typed IPC/job contracts and durable artifacts.
- C# AppCore/AppCore.Host/C# CLI support surfaces stay until the WinUI product lane has equivalent validated coverage. Python GUI/product work stays archived; active Python remains tooling/lab support only.
- Private game/media/save artifacts must stay out of public packages unless explicitly cleared.

## Functional Foundation

The first shippable Electron foundation started read-only:

1. Select or detect a Battle Engine Aquila game directory.
2. Hash and classify `BEA.exe`.
3. Load the curated patch catalog.
4. Verify patch byte states without applying anything.
5. Write a read-only artifact bundle for the job.

This foundation proved the IPC boundary, specimen model, artifact ledger, patch catalog reuse, and browser-testable UI before moving into gated mutation, debugger control, Ghidra, and game harness work.

Current status: the read-only specimen foundation is implemented, and copied-profile save/options plus executable mutation jobs now exist behind typed gates. Save Lab has first-class copied-save and copied-options workflows, Patch Bench has a first-class copied-executable workflow, Game Harness now guides capture users to apply the copied-target `force_windowed` display patch, and Media now has a first-class read-only catalog browser for texture, mesh, grouped Bink video sidecars, language/audio-linked rows, OGG playback, catalog-constrained PNG previews, and desktop-proven Bink `.vid` preparation into an app-owned MP4 cache for the in-app video panel where the returned cache supports it. The TypeScript CLI under `archive/electron-workbench/packages/cli` is preserved as archived automation/reference over the same job runner. The renderer has been reset into a calmer product workbench: Home routes the user by task, Save Lab and Patch Bench are guided copied-target workflows, Media uses local inline playback panels, Lore reads as an article reader, RE Lab is a searchable investigation surface, Game Harness explains the bounded loop in plain language, and Release summarizes public-safe readiness. The same typed job boundaries remain in place.

## Shelved Electron Workbench

The archived Electron workbench lives under:

- `archive/electron-workbench/apps/electron`
- `archive/electron-workbench/packages/contracts`
- `archive/electron-workbench/packages/cli`
- `archive/electron-workbench/packages/ui`

Useful commands:

```powershell
npm run archive:electron:dev:ui
npm run archive:electron:dev
npm run archive:electron:typecheck
npm run archive:electron:build
npm run archive:electron:test:renderer-smoke
npm run archive:electron:test:cli-smoke
```

The UI currently uses a browser preview-mode bridge so `http://127.0.0.1:3000` can be inspected without launching Electron.

When launched through Electron, the preload bridge exposes active app APIs for read-only specimen inspection, save/options workflows, media catalog, media preview, audio playback, native TypeScript save/options patching, native TypeScript executable patch apply/restore, content, release-policy, the typed job runner, and RE readiness. AppCore host diagnostics are now opt-in (`ONSLAUGHT_ENABLE_APPCORE_DIAGNOSTICS=1`) instead of part of the default product catalog. The renderer can ask the main process to select or verify `BEA.exe`; the main process hashes the file, loads `patches/catalog/patches.v2.json`, classifies every catalog row as original, patched, mismatch, or out-of-range, and writes a read-only `specimen-verification.v1` artifact.

The renderer can also inspect `.bes`, `.bea`, or `defaultoptions.bea` files through true-dword-view parsing, compare two save/options files by known region, and write read-only `save-inspection.v1` / `save-comparison.v1` artifacts. The native TypeScript save/options patchers now validate full patch intent, including rank/kill sections, per-level ranks, all supported global option fields, keybind overrides, options-entry copy, and options-tail copy. They write source-preserving plan/preview artifacts (`save-patch-plan.v1`, `save-patch-preview.v1`, `options-patch-plan.v1`, `options-patch-preview.v1`) and support armed copied-file apply/restore (`save-patch-apply.v1`, `save-patch-restore.v1`, `options-patch-apply.v1`) inside the app artifact/profile root without invoking C#.

Save Lab exposes copied-save and copied-options flows directly for community use. The native TypeScript executable patcher applies/restores curated catalog patches only on artifact-root copied `BEA.exe` targets, with preimage checks, first-snapshot backups, post-write verification, and `patch-apply.v1` / `patch-restore.v1` artifacts. C# AppCore and the CLI remain dev-time parity oracles, but AppCore host job rows are omitted from the normal product catalog unless explicitly enabled for diagnostics.

The renderer can request a bounded read-only hex window (`hex-read.v1`), convert a PE virtual address to a file offset, inventory pinned Ghidra headless paths/scripts, inventory CDB probe helpers, inspect or persist a selected local game harness profile, preview curated markdown documents, classify release/content policy (`release-policy.v1`), start/get allowlisted jobs, write non-launching CDB/game plan artifacts, write a read-only BEA window capture plan, request one bounded still-frame capture or short frame sequence for managed game launches, route capture users to `force_windowed` patch plan/apply actions on copied `BEA.exe` targets only, plan scoped game-window input, and send explicitly armed allowlisted keyboard input to managed `BEA.exe` windows. The renderer never receives raw Node, shell, debugger, Ghidra, desktop-capture, raw input, or filesystem access.

The renderer now has distinct sections for Overview, Save Lab, Patch Bench, Media, Lore, RE Lab, Game Harness, and Release, plus a command bar that searches sections and typed job definitions and routes users to the owning workbench lane. Navigation must keep unrelated workflows out of the active section; Browser Use should catch regressions where clicking around merely changes a label while leaving the same mixed dashboard in place.

The repo also owns an Electron renderer smoke gate: `npm run archive:electron:test:renderer-smoke` builds the workspaces, starts a local Vite preview on a free port, launches Electron against that renderer, and checks the product Home shell, visible-copy audit, Save Lab editor, Media inline audio/video/texture behavior, Lore reader fidelity plus internal/heading/external/unknown markdown link handling, Patch Bench guided copy/apply flow, RE Lab search/inspector/bounded-plan state, Game Harness guided loop with exact-target input arming, Release dashboard, and the absence of internal backend wording in default visible UI chrome.

## RE Automation Foundation

The RE Lab is now intentionally split into read-only primitives:

- Hex byte windows for patch/save evidence, capped at 4 KiB per read.
- PE address conversion for `BEA.exe` so `.text` shortcuts are verified from section headers instead of assumed.
- Ghidra headless readiness inventory for pinned installs, project roots, read-only export scripts, and mutation-capable scripts that remain blocked.
- Ghidra read-only export jobs for weak-function inventory and address decompile evidence.
- Debugger readiness inventory for CDB helper scripts and canned probe command files.
- Game Harness inventory for `game/BEA.exe`, `defaultoptions.bea`, runtime DLLs, safe copied-profile setup, copied-target `force_windowed` patch guidance, launch planning, managed-window capture planning, bounded still-frame/short-sequence capture, scoped keyboard input planning/sending, and gated launch/debug jobs.
- Selectable/persistent game-folder profile support stored under Electron user data, with reset back to the repo-local default.
- An allowlisted job catalog (`job-catalog.v1`) that names the host-understood boundaries for file, patch, Ghidra, debugger, game, and asset work.
- Non-launching CDB probe and game launch planning jobs that validate profiles, allowlisted probe files, safe arguments, and executable hashes before any future armed launch path exists.
- Managed runtime lifecycle jobs that list processes, read bounded log tails, and stop only PIDs/log paths previously recorded by typed game/CDB launch jobs.

## Content Browser Foundation

The Lore section now uses a curated content allowlist rather than arbitrary repo browsing. Current native APIs:

- `content-index.v1`: lists allowlisted lore, save docs, RE docs, and roadmap markdown files that exist in the repo. The current native index returns 16 docs: 13 community-safe and 3 maintainer-only.
- `content-document.v1`: reads one allowlisted markdown document, capped for preview, and returns its audience label (`community` or `maintainer`) with the document payload.

The renderer now provides search, an audience filter (`All`, `Community`, `Maintainer`), a generated heading outline for the active document, and safe markdown rendering for headings, lists, tables, code fences, inline code, and bold text. It does not render raw HTML and still cannot request arbitrary file paths.

## Media Catalog Foundation

The Media section now uses typed `media-catalog.v1`, `media-preview.v1`, `audio-playback.v1`, and `video-playback.v1` APIs instead of placeholder cards. In development it reads the generated asset catalog under `subagents/asset_catalog_wave1_2026-03-14`; in packaged/community bundles it also supports `asset-catalog/catalog.json` and falls back to selected-game-folder audio rows when the private extracted manifest is absent. It exposes search and lane filters, renders counts plus rows for textures, loose meshes, embedded meshes, Bink video sidecars, language/audio-linked strings, previews cataloged PNG texture exports, scans constrained OGG audio from `data\Music` plus `data\sounds\english\MessageBox`, and prepares cataloged `.vid` files into an app-owned MP4 cache using VLC as backend transcode infrastructure.

Audio playback is read-only and catalog-constrained: the renderer can request only a `playbackId`, and the Electron main process verifies the resolved OGG stays under the selected game root before returning an inline media payload. PNG image preview is also catalog-constrained: the renderer can request only a `previewId`, and the main process resolves that ID through the generated catalog, requires a PNG export under the app workspace, caps inline bytes, and returns `media-preview.v1`; Electron desktop dev proof completed on 2026-04-29 for a cataloged 64x64 PNG texture row. Save Lab now exposes per-slot goodie rows with true-view offsets, state, unlock hints, content type, and a media lookup action. Bink `.vid` rows now get friendly labels, sequence ids, family grouping, codec/status metadata, and a `videoPlaybackId`. The renderer can request that id only; Electron main resolves the catalog row under the selected `data\video` root, uses VLC as backend transcode infrastructure, prepares an app-owned MP4 cache under the app/user artifact root, and returns `video-playback.v1` for the in-app video panel where the returned payload/cache supports playback; Electron desktop dev proof completed on 2026-04-29 for `LTLogo.vid` using a cache hit. Raw `.vid` bytes and arbitrary process commands are not exposed to the renderer. The older external VLC open helper remains a fallback/legacy-supported boundary, not the default user-facing playback path.

## TypeScript CLI Foundation

The archived TypeScript CLI lives under `archive/electron-workbench/packages/cli` and wraps the same typed workbench job runner used by Electron. It is reference automation, not the active product CLI lane. Its supported commands are:

- `onslaught catalog` for the current job catalog.
- `onslaught run` for a `WorkbenchJobRunRequest` JSON object from stdin or `--input`.
- `onslaught list` for persisted job-run history under the selected artifact root.

CLI stdout is parseable JSON. When `--progress` is used, progress events are emitted as stderr NDJSON so automation can consume progress without corrupting stdout. The archived regression command is `npm run archive:electron:test:cli-smoke`.

Example local calls after `npm --workspace @onslaught/cli run build`:

```powershell
node archive/electron-workbench/packages/cli/dist/index.js catalog --pretty
'{"definitionId":"release.inspectPolicy","inputs":{}}' | node archive/electron-workbench/packages/cli/dist/index.js run --progress
node archive/electron-workbench/packages/cli/dist/index.js run --input .\request.json --pretty
node archive/electron-workbench/packages/cli/dist/index.js list --limit 5
```

## Release Policy Foundation

The Release section now shows a read-only `release-policy.v1` inventory:

- Curated content rows are split into community-shippable docs and maintainer-only docs.
- Path rules classify source/docs/test families, patch catalog data, reference submodules, private game installs, media, save attempts, generated subagent outputs, and repo state handoff files, including `developer_agent_state.json`, `documentation_agent_state.json`, and `re_orchestrator_state.json`.
- Two release profiles are visible: clean source tree and portable community bundle.
- The current private working tree is correctly treated as blocked for direct public source release because hard-deny paths exist locally.
- The portable bundle path remains viable with review because it can ship app code, curated docs, and patch metadata while requiring users to select their own game files.

This is an inventory and policy surface only. It does not copy files, delete files, build packages, upload artifacts, or change sharing/access.

## Job Runner Foundation

The first typed job runner exists, and still keeps every job on an allowlist:

- `file.hexRead`
- `file.peAddressConvert`
- `save.prepareCopy`
- `save.applyPatch`
- `save.planPatch`
- `save.previewPatch`
- `save.restoreBackup`
- `settings.planOptionsPatch`
- `settings.previewOptionsPatch`
- `settings.applyOptionsPatch`
- `patch.verifySpecimen`
- `patch.planCatalogPatch`
- `patch.prepareExecutableCopy`
- `patch.applyCatalogPatch`
- `patch.restoreCatalogBackup`
- `release.inspectPolicy`
- `ghidra.exportWeakFunctions`
- `ghidra.exportAddressDecompile`
- `ghidra.validateRenameMap`
- `ghidra.applyRenameMap`
- `debug.resolveCdb`
- `debug.planProbeSession`
- `debug.startProbeServer`
- `runtime.listManagedProcesses`
- `runtime.tailManagedLog`
- `runtime.stopManagedProcess`
- `game.inventoryProfile`
- `game.planWindowCapture`
- `game.captureWindowFrame`
- `game.captureWindowSequence`
- `game.planWindowInput`
- `game.sendWindowInput`
- `game.planLaunchProfile`
- `game.prepareSafeProfile`
- `game.launchProfile`
- `assets.catalogGameFiles`
- `content.readDocument`

These jobs write `job-run.v1` artifacts under the app artifact root, expose run summaries back to the renderer, and can be listed again from persisted artifact history. Launch and mutation jobs are executable only through explicit typed runner cases with fixed arm phrases and copied/artifact-root path boundaries.

Every catalog row now carries policy metadata: timeout budget, cancellation posture, and whether the row represents an external process. The in-process runner enforces a timeout wrapper, records the effective policy in `job-run.v1`, exposes a typed cancel endpoint for future long-running jobs, and emits typed progress events over IPC. Those progress events are persisted into the job artifact and shown in the RE Lab so Browser Use can verify queued/running/artifact/completed/rejected states through the same UI a human sees.

Portable bundle smoke uses a unique disposable bundle name by default and omits Electron's unused stock `default_app.asar` from the copied runtime. The launcher always starts the workbench app root explicitly, so skipping the stock default app avoids Windows file-handle issues during archive creation without changing the shipped app entrypoint.

`debug.resolveCdb` is the first external-process adapter. It runs only the allowlisted `tools/get_cdb_path.ps1 -AsLiteral` helper, captures the resolved `cdb.exe` path, emits progress, and writes the normal `job-run.v1` artifact. It does not launch the game, start a debug server, attach a debugger, or accept renderer-provided command strings.

`save.planPatch` is the first native TypeScript save-patching job. It accepts the same structured patch intent used by the AppCore host boundary, validates exact file size/version and `.bea` career-section guardrails, preserves true-dword-view layout rules, and writes `save-patch-plan.v1` without mutating source bytes.

`save.previewPatch` is the second native TypeScript save-patching job. It applies the native patcher only to an artifact-owned candidate copy, compares that candidate back to the source with known-region grouping, writes `save-patch-preview.v1`, and keeps the original save/options file unchanged.

`save.prepareCopy` is the copied-save setup job for the community Save Lab path. It requires `COPY SAVE FILE`, copies a valid `.bes`, `.bea`, or `defaultoptions.bea` file into the app artifact root, verifies read-back bytes, writes `save-copy.v1`, and returns the copied target path for later apply/restore jobs. The source file is read-only.

`save.applyPatch` is the first armed source-writing save job, but it is deliberately limited to copied targets inside the app artifact/profile root. It requires `APPLY SAVE PATCH`, writes a backup first, applies the TypeScript patcher, reads the target back, verifies the bytes, and writes `save-patch-apply.v1`. Repo-local saves and arbitrary original user files are rejected by the path boundary.

`save.restoreBackup` is the paired restore job for copied save/options targets. It requires `RESTORE SAVE BACKUP`, accepts only artifact-root target and backup paths, keeps a pre-restore backup, restores the selected backup, verifies read-back bytes, and writes `save-patch-restore.v1`.

The Save Lab now exposes the copied `defaultoptions.bea` path as a first-class community workflow too: copy options into the artifact root, plan settings/keybind changes, preview byte differences, apply only to the copied target, and restore the artifact-root backup without asking users to run the maintainer RE Lab job table.

`ghidra.exportWeakFunctions` is the first headless Ghidra adapter. It runs only `tools/run_ghidra_headless_postscript.sh ExportWeakFunctionList.java <artifact_tsv> weak`, writes its TSV under the app artifact root, parses the exported row count plus the Ghidra-reported total/weak function counts, emits progress, and records the result in `job-run.v1`. A live smoke on this workstation completed successfully against the pinned `BEA` project: `total_functions=5861`, `weak_functions=0`, and `rows=0` for weak mode. (Historical 2026-04 snapshot; current loaded-database closure is **6113/6113**, Wave900, 2026-05-26.)

`ghidra.exportAddressDecompile` is the second headless Ghidra adapter. It accepts structured address tokens only, writes the address list and decompile output directory under the app artifact root, then runs `ExportFunctionsByAddressDecompile.java`. A live smoke for `0x00421200` completed with `1` OK row and an `index.tsv` artifact.

`ghidra.validateRenameMap` is the first rename-map automation adapter. It accepts only an artifact-root two-column map path, runs `tools/run_ghidra_batch_rename_headless.sh <map> dry`, captures stdout/stderr as artifacts, and records whether save success or project-lock errors appeared. `ghidra.applyRenameMap` is the paired mutation-gated adapter: it requires `APPLY GHIDRA RENAME MAP`, `acceptsGhidraMutation=true`, the same artifact-root map, and a successful dry-run artifact for that map before it calls the helper in `apply` mode.

`assets.catalogGameFiles` rebuilds the existing cross-surface asset catalog from the known generated manifests into the app artifact root. It runs only `tools/export_asset_catalog.py` with a host-owned `--out-dir`, then reports texture, mesh, video, language, and total catalog counts. A live smoke completed successfully with `3817` total entries.

The optional `appcore.*` host jobs remain in the runner for explicit diagnostics only and are omitted from the default catalog unless `ONSLAUGHT_ENABLE_APPCORE_DIAGNOSTICS=1` is set before building the catalog. This keeps packaged/community use on the native TypeScript product path while preserving a narrow C# oracle lane for maintenance.

`patch.planCatalogPatch` is the first patch-workbench planning job. It verifies the selected `BEA.exe`, selects the stable patch set by default, reports ready/already-applied/blocked counts, and writes a `patch-plan.v1` artifact. It does not write bytes or accept an arbitrary command.

`patch.prepareExecutableCopy` is the copied-executable setup job for the community Patch Bench path. It requires `COPY BEA EXE`, copies a verified retail `BEA.exe` into the app artifact root, verifies the copied bytes and specimen hash, writes `patch-executable-copy.v1`, and returns the copied target path for later plan/apply/restore jobs. The source executable is read-only.

`patch.applyCatalogPatch` applies curated catalog patch bytes only to an artifact-root copied `BEA.exe`. It requires `APPLY CATALOG PATCH`, verifies selected patch preimages, refuses mismatch/out-of-range rows before backup/write, creates a first-snapshot `BEA.exe.original.backup`, writes only catalog-declared file offsets, verifies read-back bytes, verifies the post-write patch state, and writes `patch-apply.v1`.

`patch.restoreCatalogBackup` restores an artifact-root executable backup to an artifact-root copied `BEA.exe`. It requires `RESTORE CATALOG BACKUP`, keeps a pre-restore backup, verifies read-back bytes, verifies the restored executable through the patch catalog, and writes `patch-restore.v1`.

`game.captureWindowSequence` repeats the same bounded desktop-capture path used by `game.captureWindowFrame` for a short capped frame series (`game-window-frame-sequence.v1`). It is for observe-act-observe automation, not a persistent stream: no live capture handle remains open and no input is sent.

Prompt 7 runtime proof completed on 2026-04-29 in Electron desktop dev mode: a task-scoped harness used the Game Harness UI surface and typed jobs to prepare a copied profile, apply only `force_windowed` to the copied `BEA.exe`, launch a managed process, capture frame 1, choose `tap:F12` from a rule-based decision record only after exact `ProcessId`/`HwndHex` evidence existed, send the bounded input, capture frame 2, and stop the managed process. This proves one bounded observe/decide/act/observe/stop loop. It does not prove open-ended autonomy, continuous streaming, packaged portable-bundle behavior, or semantic gameplay reaction.

`game.planWindowInput` validates a small allowlisted input sequence (`tap:KEY`, `down:KEY`, `up:KEY`, `wait:MS`) for a managed `BEA.exe` process and writes `game-window-input.v1` without focusing the window or sending input. `game.sendWindowInput` uses the same helper only after `SEND GAME INPUT` arming and a recorded managed game process; it focuses the selected `BEA.exe` top-level window and sends only allowlisted keyboard events. The renderer still never receives raw window handles as commands, arbitrary key APIs, or shell access.

`release.inspectPolicy` classifies curated content and release path families, then writes a `release-policy.v1` artifact. It does not package, copy, delete, or upload files.

`debug.planProbeSession` is the first debugger planning job. It validates the game profile, selects an allowlisted command file from `tools/runtime-probes`, verifies the executable specimen, and writes a `debug-probe-plan.v1` artifact with server/client/tail command previews. It does not launch the game, start CDB, attach a debugger, or open a socket.

`game.planLaunchProfile` is the first game-launch planning job. It validates the active or supplied game root, defaults to no launch arguments, accepts only explicit allowlisted diagnostic arguments, verifies the executable hash, and writes a `game-launch-plan.v1` artifact with a command preview. It does not start `BEA.exe`.

`debug.startProbeServer` is the first armed debugger execution job. It still accepts only structured inputs: `BEA.exe`, an allowlisted probe id, a validated copied/safe game profile outside the repo root, a bounded local port, `armPhrase: "ATTACH CDB"`, and an explicit runtime-attach acknowledgement. It starts only `tools/start_cdb_server.ps1`, writes `debug-session.v1`, and refuses the repo-local `game/` profile so automated parity cannot attach to the private working tree by accident.

`game.launchProfile` is the first armed game execution job. It accepts only a validated copied/safe game root, defaults to no launch arguments, keeps the old retail `-forcewindowed` token as an explicit diagnostic-only argument, requires `armPhrase: "LAUNCH BEA"` plus an explicit profile-write acknowledgement, starts only `tools/start_game_profile.ps1`, writes `game-launch.v1`, and refuses repo-local profiles for the same reason.

`game.planWindowCapture` is the first visual-loop boundary. It selects a recorded managed `game.launchProfile` process, runs only `tools/list_game_windows.ps1 -ProcessName BEA.exe`, filters the discovered top-level windows back to that PID, and writes `game-window-capture-plan.v1`. It does not open a desktop stream, embed the game, focus the window, or send input.

`game.captureWindowFrame` extends that boundary by reusing the managed-window plan, then asking the desktop host for one bounded `desktopCapturer` window thumbnail. It writes `game-window-frame-capture.v1` and `frame.png` under the artifact root, returns only typed result details plus a small preview data URL for the UI, and sends no input. Fullscreen BEA can still return no source or an empty/black thumbnail; apply the windowed/display patch before treating capture failures as meaningful game evidence.

`game.prepareSafeProfile` is the copied-profile setup job. It requires `armPhrase: "COPY GAME PROFILE"` and explicit local-copy acknowledgement, then runs only `tools/prepare_game_profile.ps1` to copy a validated source game root under the app artifact/profile root. The helper refuses to overwrite an existing target and writes `game-profile-prepare.v1`.

`runtime.listManagedProcesses`, `runtime.tailManagedLog`, and `runtime.stopManagedProcess` are the lifecycle controls for external processes. Launch/attach jobs record only their own returned PIDs and artifact-root log paths into a workbench-owned registry. The list job writes `managed-process-registry.v1`; the log-tail job reads a bounded `managed-process-log-tail.v1` payload only from recorded artifact-root log paths; the stop job requires `armPhrase: "STOP PROCESS"` plus explicit acknowledgement and can target only a recorded run/PID, writing `managed-process-stop.v1`.

Debug planning and attach sessions now generate a per-run CDB server password inside the job runner instead of using a fixed shared value. The renderer still does not supply debugger credentials or raw command text.

Ghidra mutation jobs still remain rejected until separate armed adapters exist. Do not let the renderer send arbitrary shell commands.

## Verified 2026-04-26

- `npm run typecheck`
- `npm run build`
- Direct verifier against `game\BEA.exe`: 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, known Steam hash, 7/7 patch catalog rows in original state.
- Direct save inspector against `save-attempts\haha-cannon-goes-brrrrr.bes`: valid `0x4BD1`, 16 options entries, 16 decoded binding rows, 43 completed missions, 232 displayable goodies unlocked, read-only artifact written.
- Direct save comparison smoke: identical fixture reports 0 differing bytes; one-byte mutated scratch copy reports 1 differing byte under `Kills[Aircraft]`; read-only artifact written.
- Direct native RE workbench smoke: `readHexRange('game/BEA.exe', '0x129696', '32')` returned 32 bytes from the expected offset; `convertExecutableAddress('game/BEA.exe', '0x00529696')` mapped to `.text` file offset `0x129696`; Ghidra, CDB, and game harness readiness all returned ready on this workstation without launching any external process.
- Direct native job-catalog smoke now returns 37 allowlisted job definitions: 36 available, 1 blocked, 0 planned, 25 read-only, and 12 gated.
- Direct AppCore host smoke completed `dotnet run --no-launch-profile --project OnslaughtCareerEditor.AppCore.Host -- inspect-save save-attempts\haha-cannon-goes-brrrrr.bes`, returned `appcore-save-analysis.v1`, valid `0x4BD1`, 43/43 missions, 232/233 displayable goodies, and `mutation: false`.
- Direct AppCore host comparison smoke completed `dotnet run --no-launch-profile --project OnslaughtCareerEditor.AppCore.Host -- compare-saves save-attempts\haha-cannon-goes-brrrrr.bes save-attempts\haha-cannon-goes-brrrrr.bes`, returned `appcore-save-comparison.v1`, `identical: true`, `differingBytes: 0`, and `mutation: false`.
- Direct AppCore host patch-plan smoke completed `dotnet run --no-launch-profile --project OnslaughtCareerEditor.AppCore.Host -- plan-save-patch <appcore-save-patch-request.v1.json>`, returned `appcore-save-patch-plan.v1`, `mutation: false`, two level-rank rows, two per-category kill rows, `requiresCopiedApply: true`, and `sourceUnchanged: true`.
- Direct AppCore host patch-preview smoke completed `dotnet run --no-launch-profile --project OnslaughtCareerEditor.AppCore.Host -- preview-save-patch save-attempts\haha-cannon-goes-brrrrr.bes --rank S --kills 100`, returned `appcore-save-patch-preview.v1`, `mutation: false`, `wouldChange: true`, `differingBytes: 14`, `topRegion: Kills`, and `tempOutputDeleted: true`.
- Direct native TypeScript save-patcher parity now byte-matches AppCore/C# outputs for default patching, kills-only patching with preserved high meta bytes, one-based per-level rank targeting, and displayable-goodie boundary behavior while rejecting unsafe `.bea/defaultoptions` career-section mutation.
- Direct native TypeScript save-patcher noop guard verified `.bea/defaultoptions` can produce a zero-change source-preserving preview when every career patch section is disabled.
- Direct native save-copy job coverage now rejects missing `COPY SAVE FILE`, copies a valid save into the app artifact root with `save-copy.v1`, verifies read-back bytes, and feeds that copied target into the apply/restore parity path.
- Direct native copied-save apply/restore parity now rejects repo-local source targets, applies only to artifact-root copied saves, writes a backup, verifies read-back bytes, byte-matches the applied target against C# AppCore output, restores the backup, and retains a pre-restore backup artifact.
- Direct native job-runner smoke completed `file.hexRead` against `game\BEA.exe` and `content.readDocument` against `lore-book/BOOK.md`, with `job-run.v1` artifacts written.
- Direct native job-history smoke reloaded a persisted `job-run.v1` artifact through the typed run-history API.
- Direct native job-progress smoke emitted queued, running, artifact, completed, and rejected progress events; persisted progress traces in `job-run.v1`; and kept job history compatible with the new progress field.
- Direct native CDB resolver smoke completed `debug.resolveCdb`, returned a `CDB path` detail ending in `cdb.exe`, persisted the progress-bearing `job-run.v1` artifact, and reloaded it from job history.
- Direct native Ghidra weak-function export smoke completed `ghidra.exportWeakFunctions` through the typed job runner, ran the pinned headless project script, wrote `weak-functions-weak.tsv` under the artifact root, and returned `total_functions=5861`, `weak_functions=0`, `rows=0`. (Historical 2026-04 snapshot; current closure **6113/6113**, Wave900.)
- Direct native Ghidra address-decompile export smoke completed `ghidra.exportAddressDecompile` for `0x00421200`, wrote an artifact-owned address list and decompile output directory, and returned `1` OK row in `index.tsv`.
- Direct native asset catalog smoke completed `assets.catalogGameFiles`, rebuilt the catalog under the artifact root, wrote `summary.json` and `catalog.json`, and returned `3817` total catalog entries.
- Direct native patch-plan smoke completed `patch.planCatalogPatch`, selected the stable patch set for clean retail `game\BEA.exe`, reported `6` ready rows and `0` blocked rows, and wrote a `patch-plan.v1` artifact.
- Direct native TypeScript options/defaultoptions parity now byte-matches C# CLI output for settings, keybinds, options entry copy, and tail override workflows; applies only to artifact-root copied options files with backup/read-back verification; and rejects repo-local `defaultoptions.bea` apply targets.
- Direct native TypeScript executable patch apply/restore parity now rejects repo-local `game\BEA.exe`, applies the stable catalog patch set only to artifact-root copied `BEA.exe`, writes a non-overwritten `BEA.exe.original.backup`, verifies all selected rows become patched, rejects mismatch preimages before backup/write, restores the backup with read-back verification, and writes `patch-apply.v1` / `patch-restore.v1`.
- Direct native media catalog parity now verifies `media-catalog.v1` against the generated 3,817-row asset catalog, including 828 textures, 213 loose meshes, 139 embedded meshes, 66 Bink video rows, three friendly video groups, Bink codec/VLC playback posture, 2,571 language rows, briefing-video filtering, the `LAP_2` audio-linked language row, `media-preview.v1` for the Hawk goodie PNG texture export, and dry-run `video-playback.v1` resolution for cataloged `.vid` files.
- Direct native release/content policy smoke completed `getContentIndex`, `readContentDocument`, `getReleasePolicy`, and `release.inspectPolicy`; wrote `release-policy.v1`; reported `16` curated docs (`13` community, `3` maintainer); reported `7` existing hard-deny paths; confirmed `game/` and `re_orchestrator_state.json` are classified as `deny`; and confirmed document previews preserve their audience label.
- Direct native planner smoke completed `game.planLaunchProfile` and `debug.planProbeSession`, wrote `game-launch-plan.v1` and `debug-probe-plan.v1` artifacts under a temp artifact root, emitted completed progress for both, and did not launch the game, CDB, or a debug client.
- Direct native debugger-plan smoke now asserts the generated CDB password starts with `bea-`, is not the old fixed `secret` value, and appears consistently in both server and client command previews.
- Direct armed-launch boundary smoke proved `debug.startProbeServer` rejects without `ATTACH CDB`, `game.launchProfile` rejects without `LAUNCH BEA`, and both armed launch paths reject the repo-local `game/` profile because executable jobs require a copied/safe profile outside the repo root.
- Direct native managed-process lifecycle smoke completed `runtime.listManagedProcesses`, wrote `managed-process-registry.v1`, rejected `runtime.stopManagedProcess` without `STOP PROCESS`, and completed an armed stop against a fake already-exited registry target without touching arbitrary local processes.
- Direct native game-window capture-plan smoke completed `game.planWindowCapture` against a fake managed game process record, wrote `game-window-capture-plan.v1`, kept `mutation: false`, and points to scoped keyboard input as an armed follow-up.
- Direct native game-window still-frame and frame-sequence smoke completed `game.captureWindowFrame` / `game.captureWindowSequence` against the same fake managed game process record, wrote `game-window-frame-capture.v1` / `game-window-frame-sequence.v1`, kept `mutation: false`, and stopped cleanly at `no-window` in Node parity when no Electron desktop capture capability or real BEA window was present.
- Safe-profile helper preview smoke completed `tools/prepare_game_profile.ps1 -PrintOnly`, returned `game-profile-prepare.v1`, listed 9 copy entries, and did not copy files.
- Helper preview smoke completed `tools/start_game_profile.ps1 -PrintOnly` and `tools/start_cdb_server.ps1 -PrintOnly`; both printed command previews without launching BEA.exe, CDB, a server, or a client.
- Direct native game-profile smoke moved from repo-default to selected to stored and back to repo-default using a temporary settings root; all states stayed ready.
- Direct native content-browser smoke returned 16 curated documents and confirmed `god-mode` is `community` while `windbg-cdb-runbook` is `maintainer`.
- Browser mode at `http://127.0.0.1:3000` remains usable with the preview-mode bridge for Browser Use inspection; Browser Use clicked all 8 nav sections, verified one active section each, exercised save inspect, save compare, and patch verifier preview-mode flows, and reported no console warnings/errors.
- Browser Use also exercised the RE Lab and Game Harness preview-mode surfaces: hex reader, PE address converter, Ghidra readiness, debugger readiness, and local game profile inventory rendered as expected with no console warnings/errors.
- Browser Use verified that the RE Lab job catalog exposes read-only and gated boundaries, including hex read, patch verification, Ghidra export, CDB probe server, and game launch profile rows.
- Browser Use ran the first RE Lab preview-mode sample job from the catalog; the job completed through the browser bridge and no new warning/error logs appeared after the verification start.
- Browser Use ran the RE Lab `Read curated document` preview-mode sample job and verified the live progress panel reached `completed` at `100%`, the result retained a `Progress trace`, and no warning/error console logs appeared after the verification start.
- Browser Use ran the RE Lab `Resolve CDB path` preview-mode sample job, verified the row is read-only/external with a 30 second timeout, confirmed the result reports `CDB path` instead of stale document details, and found no warning/error console logs after the verification start.
- Browser Use ran the RE Lab `Export weak function list` preview-mode sample job, verified the row is read-only/cancellable/external with a 10 minute timeout, confirmed the result reports total/weak/row counts plus an output TSV, and found no warning/error console logs after the verification start.
- Browser Use ran the RE Lab `Export decompile for addresses` preview-mode sample job, verified the row is read-only/cancellable/external with a 10 minute timeout, confirmed the `ghidra-decompile-export.v1` result reports `1` OK row for `0x00421200`, and found no fresh warning/error console logs.
- Browser Use ran the RE Lab `Catalog game assets` preview-mode sample job, verified the row is read-only/cancellable/external with a 10 minute timeout, confirmed the result reports `3817` entries plus texture/mesh/video/language counts, and found no warning/error console logs after the verification start.
- Browser Use ran the RE Lab `Plan stable patch set` preview-mode sample job, verified the read-only `patch-plan.v1` result, confirmed `6` ready rows and `0` blocked rows, and found no fresh warning/error console logs.
- Browser Use opened the Release section and verified the release policy cards/tables render community docs, maintainer docs, hard-deny counts, clean source tree, portable community bundle, maintainer-only Ghidra runbook, and hard-deny `game/` rows.
- Browser Use ran the RE Lab `Inspect release policy` preview-mode sample job, verified the read-only `release-policy.v1` result, confirmed community/maintainer/hard-deny counts and policy artifact details, and found no fresh warning/error console logs.
- Browser Use ran the RE Lab `Plan CDB probe session` preview-mode sample job, verified the read-only `debug-probe-plan.v1` result, confirmed `pause-persist-wave1.cdb.txt`, server/client command previews, plan artifact details, and completed `100%` progress, and found no fresh warning/error console logs.
- Browser Use ran the RE Lab `Plan verified game launch` preview-mode sample job, verified the read-only `game-launch-plan.v1` result, confirmed default arguments are `none`, known Steam hash `yes`, command preview, plan artifact details, and completed `100%` progress, and found no fresh warning/error console logs.
- Browser Use verified the RE Lab run-history panel: the retained preview-mode sample job rendered, a new browser-run job was prepended after execution, and no new warning/error logs appeared after the verification start.
- Browser Use verified Game Harness folder controls (`Use folder`, `Reset default`) through the preview-mode bridge.
- Browser Use verified the Lore document browser and switching from Lore book to Cheat codes through the preview-mode bridge.
- Browser Use verified the upgraded Lore browser: filtered the allowlist with search, selected Cheat codes, confirmed the generated outline and rendered markdown preview, and observed no new warning/error logs.
- Browser Use verified the Lore audience filter after reload: Maintainer + `WinDbg CDB runbook` rendered the maintainer-only row, Community + `God mode` rendered the community row, the preview kept its audience badge, the Release page showed the new `RE orchestration state file` deny row, and recent warning/error console logs were clean.
- Browser Use verified the browser preview-mode job catalog after reload against the earlier native catalog posture, including `Plan save patch with TypeScript`, `Preview save patch with TypeScript`, `Apply save patch to copied file`, `Restore copied save backup`, `Inspect save with AppCore host`, `Compare saves with AppCore host`, `Plan save patch with AppCore host`, `Preview save patch with AppCore host`, `List managed runtime processes`, `Stop managed runtime process`, `Prepare copied game profile`, `Attach CDB probe server`, `Launch verified game profile`, and `Apply Ghidra rename map`.
- Browser Use ran the RE Lab `Inspect save with AppCore host` preview-mode sample job, verified the `appcore-save-analysis.v1` result, confirmed the AppCore artifact detail, and found no fresh warning/error console logs after reload.
- Browser Use ran the RE Lab `Compare saves with AppCore host` preview-mode sample job, verified the `appcore-save-comparison.v1` result and artifact detail, and found no fresh warning/error console logs after reload.
- Browser Use ran the RE Lab `Plan save patch with AppCore host` preview-mode sample job, verified the `appcore-save-patch-plan.v1` result, confirmed request and plan artifact details plus `Requires copied apply: yes` and `Source unchanged: yes`, and found no fresh warning/error console logs after reload.
- Browser Use ran the RE Lab `Preview save patch with AppCore host` preview-mode sample job, verified the `appcore-save-patch-preview.v1` result, confirmed `Would change: yes`, `Temp copy deleted: yes`, and the preview artifact detail, and found no recent warning/error console logs.
- Browser Use verified the browser preview-mode job catalog after the native TypeScript save patcher, save-copy job, options/defaultoptions patcher, and copied executable workflow work: RE Lab showed 34 rows, 33 available, 1 blocked, 0 planned, 22 read-only, and 12 gated, including `Copy save/options into workspace`, `Plan save patch with TypeScript`, `Preview save patch with TypeScript`, `Apply save patch to copied file`, `Restore copied save backup`, `Plan global options patch with TypeScript`, `Preview global options patch with TypeScript`, `Apply global options patch to copied file`, `Copy BEA.exe into workspace`, `Apply curated catalog patch`, and `Restore copied executable backup`.
- Browser Use exercised the first-class Save Lab patch workflow in browser mode: `Copy into workspace`, `Plan`, `Preview`, `Apply copied save`, and `Restore backup`; the final card showed `save-patch-restore.v1`, read-back verification, target/backup/pre-restore artifact details, and zero warning/error console logs.
- Browser Use exercised the first-class global-options workflow in browser mode: `Copy options into workspace`, `Plan options`, `Preview options`, `Apply copied options`, and `Restore options backup`; the final card kept `a preview-mode copied-options sample path`, showed `save-patch-restore.v1`, options backup/pre-restore artifact details, and zero warning/error console logs.
- Browser Use exercised the first-class Patch Bench copied-executable workflow in browser mode: `Copy executable into workspace`, `Plan / preview`, `Apply copied executable`, and `Restore executable backup`; the final card kept `a preview-mode copied-executable sample path`, showed `patch-restore.v1`, executable backup/pre-restore artifact details, and zero warning/error console logs.
- Browser Use exercised the first-class Media catalog browser in browser mode: loaded the catalog, confirmed 3,817-row counts and texture/mesh/video/language rows, filtered to briefing videos, confirmed BIKi sidecar metadata, and found zero warning/error console logs.
- Browser Use ran the RE Lab `Plan save patch with TypeScript` preview-mode sample job, verified the `save-patch-plan.v1` result, confirmed `Requires copied apply: yes`, `Source unchanged: yes`, request details, and the plan artifact, and found no warning/error console logs.
- Browser Use ran the RE Lab `Preview save patch with TypeScript` preview-mode sample job, verified the `save-patch-preview.v1` result, confirmed `Would change: yes`, `Differing bytes: 14`, `Source unchanged: yes`, candidate and preview artifact details, and found no warning/error console logs.
- Browser Use armed the execution gate, ran `Apply save patch to copied file`, verified the `save-patch-apply.v1` result, confirmed backup/read-back/apply artifact details, and found no warning/error console logs.
- Browser Use ran `Restore copied save backup`, verified the `save-patch-restore.v1` result, confirmed pre-restore backup/read-back/restore artifact details, and found no warning/error console logs.
- Browser Use armed the RE Lab launch gate, ran the `Launch verified game profile` preview-mode sample job, verified `game-launch.v1`, and confirmed `Safe profile`, `Process ID`, and launch artifact details.
- Browser Use ran the armed `Attach CDB probe server` preview-mode sample job, verified `debug-session.v1`, and confirmed `Safe profile`, `CDB PID`, log path, and session artifact details.
- Browser Use ran the armed `Prepare copied game profile` preview-mode sample job, verified `game-profile-prepare.v1`, and confirmed target root, copied-entry count, and prepare artifact details.
- Browser Use ran the RE Lab `List managed runtime processes` preview-mode sample job, verified `managed-process-registry.v1`, and confirmed managed process count, running count, latest process, and registry artifact details.
- Browser Use ran the RE Lab `Read managed runtime log tail` preview-mode sample job, verified `managed-process-log-tail.v1`, and confirmed target run, log path, bounded tail text, and tail artifact details.
- Browser Use armed the launch gate, ran the RE Lab `Stop managed runtime process` preview-mode sample job, verified `managed-process-stop.v1`, and confirmed target run, PID, current status, stop-requested state, and stop artifact details.
- Browser Use found no recent warning/error console logs after the armed launch preview-mode verification.
- Browser Use verified the Game Harness readiness refresh: the visible harness phases now mark specimen/patch/runtime/Ghidra foundations as active, and the agentic-loop readiness panel calls out read-only window discovery plus bounded still-frame capture separately from the remaining live frame-streaming/input work.
- Native content-document smoke re-read `grade-system` and `kill-tracking` after cleanup; both remain `community` docs and neither preview contains the visible mojibake markers flagged by the content-audience audit.
- `npm run archive:electron:test:parity` now builds the Electron main code, runs the TypeScript save inspector against 13 save/options fixtures, runs the C# CLI analyzer against the same fixtures, compares important save/options values including controller/invert settings, verifies read-only artifact writing, confirms a one-byte `Kills[Aircraft]` mutation is grouped correctly by the TypeScript comparer, verifies patch-catalog states against the clean retail `game\BEA.exe`, covers bad-size, bad-version, unsupported-extension, wrong-executable-name, and short-executable negative cases, runs the stable patch-plan job, proves native options/defaultoptions parity, copies `BEA.exe` into the artifact root, applies/restores copied executable patch fixtures, verifies the media catalog and PNG preview boundary, runs the AppCore host save-inspection, save-comparison, save-patch-plan, and save-patch-preview jobs, runs the release-policy job, runs the asset catalog job, runs the CDB/game planner jobs when available, checks safe-profile and armed launch rejection for missing arm phrases and repo-local profiles, checks managed runtime registry/log-tail/stop boundaries, checks the game-window capture-plan and still-frame artifact boundaries, checks the Ghidra export catalog boundary, runs `debug.resolveCdb` when available, and proves executable jobs do not run from unsafe defaults. With `ONSLAUGHT_RUN_GHIDRA_EXPORT_PARITY=1`, the same parity script also runs the real Ghidra weak-function and address-decompile export adapters.
- Native job-policy smoke confirmed real catalog policies, a completed read-only `file.hexRead` job, launch-gated rejection behavior, persisted job history, and a false return for cancelling a missing run id.
- Browser Use verified the RE Lab job-policy column (`10 s fixed`, `10 min cancel external`, `5 min cancel external`) and a read-only job result with the timeout badge. DOM interaction and console checks succeeded; screenshot capture was not retained for that historical pass.
- 2026-04-27 media/bundle pass: grouped Bink video browsing now renders mission briefings, story cutscenes, and root/menu clips with sequence ranges and a visible VLC playback boundary; Browser Use verified the Media section and found no warning/error console logs.
- 2026-04-27 media/bundle pass: `archive/electron-workbench/packages/ui/vite.config.ts` now uses relative build assets for packaged `file://` loading, and Electron packaged-root resolution no longer depends on `AGENTS.md` being present in community bundles.
- 2026-04-27 media/bundle pass: packaged/community media catalogs hide PNG preview actions when extracted preview exports are not bundled, while dev/private catalogs still expose preview IDs for existing workspace PNG exports.
- 2026-04-27 bundle smoke: `npm run archive:electron:test:bundle-smoke` produces a disposable community portable folder, zip, and `bundle-policy.v1.json` with `deniedPathCount: 0`; the bundled Electron runtime launches the packaged app with `ONSLAUGHT_RENDERER_SMOKE=1` and exits `0`.
- 2026-04-29 Prompt 6 Game Harness runtime proof: Electron desktop dev mode prepared a copied profile under the app artifact root, applied only catalog patch id `force_windowed` to the copied `BEA.exe`, launched the copied profile as a managed process, planned a BEA window capture, captured a bounded PNG frame, planned and sent one bounded `tap:F12` input action to the managed BEA window handle, captured a second bounded PNG frame, then stopped the managed process and confirmed the registry had zero running BEA processes. Sanitized proof lives in `release/readiness/private_runtime_evidence/2026-04-29-game-harness-proof.md`; raw frame PNGs and local proof JSON remain private/ignored.
- Optional gates for an archived Electron workbench validation pass: `npm run archive:electron:typecheck`, `npm run archive:electron:build`, `npm run archive:electron:build:main`, `npm run archive:electron:test:parity`, `npm run archive:electron:test:cli-smoke`, `npm run archive:electron:test:renderer-smoke`, `npm run archive:electron:test:bundle-policy`, `npm run archive:electron:test:bundle-smoke`, `npm run test:doc-commands`, `npm run test:md-links`, `npm run test:public-allowlist`, `npm run test:repo-hygiene`, direct TypeScript/C# byte parity checks, copied-save/options/executable copy/apply/restore read-back checks, expanded options patch intent checks, per-slot goodie row checks, media-catalog and PNG preview checks, managed runtime registry/log-tail/stop checks, game-window capture-plan/still-frame checks, portable bundle smoke, documented npm command checks, tracked markdown link checks, public allowlist safety checks, stale-placeholder/text-hygiene checks, and renderer route/copy checks. The 2026-05-01 UX goal pass also captured private ignored screenshots for Home, Save Lab, Patch Bench, Media, Lore, RE Lab, Game Harness, and Release; public-safe summary lives in `release/readiness/ux_goal_evidence_2026-05-01.md`.

## Release Posture

The final release shape is still open. Two viable paths remain:

- make the repo itself cleaner and more public-ready as the normal release source;
- keep a curated portable bundle as a separate output for users who do not need private/local RE assets.

Either way, private `game/`, `media/`, `save-attempts/`, generated subagent outputs, and unclear-rights artifacts need explicit boundaries before public distribution.

## Next Implementation Path

1. Keep packaged portable-bundle runtime behavior for media playback and Game Harness behavior as optional maintainer-workbench validation only. Desktop dev-mode texture/video/Game Harness proof is complete; packaged Electron proof is not the primary product gate.
2. Keep continuous streaming, semantic gameplay-state interpretation, broader agentic control, signed installer readiness, and C# parity retirement as explicitly separate follow-ups.
3. Decide whether the default `npm run archive:electron:bundle` path should auto-clean, use unique names, or stay collision-safe by failing when the output already exists.
4. Expand Browser Use and renderer smoke coverage for deeper media playback, runtime lifecycle, and copied-profile flows.
5. Replace or retire the remaining AppCore parity diagnostics once native TypeScript fixtures cover the same edge cases.
6. Extend attach/client log streaming beyond bounded tail reads once broader live debugger automation needs continuous follow mode.
7. Add sanitized public variants where maintainer indexes link private runtime evidence.
