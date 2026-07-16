---
status: active
last_updated: 2026-06-19
doc_version: 1.2
---

# Reverse Engineering Coverage Map

## Purpose

This map is the public-safe operating surface for Ralph-loop reverse-engineering work. It answers:

- what is already proven,
- what is only partially proven,
- what is missing,
- what proof needs WinUI native UI, archived Electron reference checks, C# CLI/tools, private evidence, or a real runtime run,
- which areas are player-facing versus maintainer-facing,
- and what bounded objective shape should be used for the next slice.

WinUI 3 is the active product workbench. The Electron/React/TypeScript workbench under `archive/electron-workbench/` is archived reference only unless a later prompt explicitly reactivates it.

This file does not claim complete game reverse engineering. It tracks usable coverage and the next bounded objectives.

## Proof Legend

| Tag | Meaning |
| --- | --- |
| `proven` | There is repo evidence, code, tests, or docs proving the stated slice. |
| `partially proven` | A useful subset is implemented or documented, but important behavior or coverage remains open. |
| `missing` | No reliable current implementation or proof exists yet. |
| `browser-preview-only` | Archived Electron browser/Vite preview mode proves renderer behavior only. It is not proof of WinUI native behavior, filesystem, process, debugger, Ghidra, capture, input, or real game behavior. |
| `winui-native` | The slice is implemented or proven in the WinUI 3 product lane (`OnslaughtCareerEditor.WinUI`) with AppCore-backed services. |
| `desktop-required` | The slice needs a native desktop host (WinUI, archived Electron desktop, C# CLI, Node CLI), local filesystem, Ghidra, CDB, VLC, Win32 capture, process launch, or another native capability. |
| `archived-electron` | The slice lives in `archive/electron-workbench/` as historical/reference proof or tooling, not the active product lane. |
| `private-evidence-only` | The proof depends on local game files, extracted media, runtime screenshots, frame captures, local artifact roots, or ignored/private reports. Public docs may summarize it, but raw evidence must not ship. |
| `player-facing` | The workflow is suitable for the community/user lane when copy-target and bring-your-own-file boundaries are preserved. |
| `maintainer-facing` | The workflow is for maintainers, RE agents, or diagnostics. It may still be exposed in the workbench behind clear labels and gates. |

## Current WinUI Product Surfaces

| Surface | Current status | Proof posture |
| --- | --- | --- |
| Home | Primary task routing into Save Lab, Media, Asset Library, Lore, Windowed & Mods, and setup status. | `winui-native`, `player-facing`; focused UI Automation and visual smoke exist. |
| Save Lab | Three subtabs: **Save Analyzer**, **Save Editor** (`.bes`), and **Game Options** (`defaultoptions.bea` / global options). Copy-first inspect/plan/preview/apply/restore through AppCore. | `proven`, `winui-native`, `player-facing`; real file work is `desktop-required`. |
| Windowed & Mods | Verifies patch catalog state, prepares copied game folders and copied `BEA.exe` targets, plans/applies/restores curated patches on copied targets, launches/stops managed safe copies, and stages copied-game music/mod options. | `proven`, `winui-native`, `player-facing`; actual bytes are native/copy-target only and installed game files stay read-only. |
| Media | Browses catalog audio/video rows; plays constrained inline audio/video; prepares Bink `.vid` into app-owned MP4 cache where supported. Audio/Video subtabs persist selection. | `partially proven`, `winui-native`, `player-facing`; focused and broader-family native playback are recorded; all-row and packaged proof remain open. |
| Asset Library | Loads generated local asset catalogs; browses texture/mesh rows; bounded in-app wireframe preview; scoped open/copy for exported assets. | `partially proven`, `winui-native`, `player-facing`; representative native row-breadth and catalog-wide export readability are recorded; full 3D rendering remains open. |
| Lore | Curated document search, selection, and in-app reader. | `proven`, `winui-native`, `player-facing`; broader content coverage remains ongoing. |
| Settings | Game-directory auto-detect, path-safe install summary, and explicit path-details disclosure. | `proven`, `winui-native`, `player-facing`. |
| About | Product/version/support copy. | `winui-native`, `player-facing`. |

## Archived Electron Workbench Surfaces (reference)

These surfaces live under `archive/electron-workbench/` and are not the active product lane.

| Surface | Current status | Proof posture |
| --- | --- | --- |
| Home | Task routing across Save Lab, Media, Lore, RE Lab, and loop summary. | `archived-electron`, `browser-preview-only` for renderer navigation unless archived desktop smoke is explicitly run. |
| Save Lab | Historical renderer/CLI save/options workflow over typed jobs. | `archived-electron`, `proven` for archived lane behavior; superseded by WinUI Save Lab for product work. |
| Patch Bench | Historical copied-executable patch workflow. | `archived-electron`, `proven` for archived lane behavior; superseded by WinUI Windowed & Mods for product work. |
| Media | Historical catalog browser and renderer playback paths. | `archived-electron`, `partially proven`; superseded by WinUI Media for product work. |
| Lore | Historical curated reader with renderer-handled markdown links. | `archived-electron`, `proven` for archived renderer behavior; superseded by WinUI Lore for product work. |
| RE Lab | Maintainer search surface, sample investigation rows, tool readiness, job catalog, read-only jobs, Ghidra/debug/asset/file lanes. | `archived-electron`, `partially proven`, `maintainer-facing`; reference only unless the archive is deliberately reactivated. |
| Game Harness | Copied-profile workflow, windowed-patch guidance, managed launch/capture/input/stop job controls. Desktop dev-mode bounded proof completed **2026-04-29** (prepare profile, `force_windowed`, launch, capture, one scoped input, capture again, stop). | `archived-electron`, `partially proven`, `desktop-required`, `private-evidence-only`; not a WinUI page; browser preview mode is not runtime proof. |
| Release | Historical release policy inventory and bundle-smoke posture in the archived workbench. | `archived-electron`, `proven` for inventory reference; active release work uses repo release docs and WinUI packaging proof. |
| TypeScript CLI | `catalog`, `run`, and `list` over the archived typed job runner; JSON stdout and optional stderr NDJSON progress. | `archived-electron`, `proven`, `maintainer-facing`; revalidate with `npm run archive:electron:test:cli-smoke` only when archive health is in scope. |

## Typed Job Boundary Summary

Use these job groups as the preferred execution boundaries. Renderer code must not receive raw shell, filesystem, debugger, Ghidra, process, capture, or input access.

| Lane | Jobs | Boundary |
| --- | --- | --- |
| File | `file.hexRead`, `file.peAddressConvert` | Read-only byte windows and PE section conversion. |
| Save/options | `save.prepareCopy`, `save.planPatch`, `save.previewPatch`, `save.applyPatch`, `save.restoreBackup`, `settings.planOptionsPatch`, `settings.previewOptionsPatch`, `settings.applyOptionsPatch` | Copy first; apply only to artifact-root copied targets with arm phrases. |
| Patch | `patch.verifySpecimen`, `patch.planCatalogPatch`, `patch.prepareExecutableCopy`, `patch.applyCatalogPatch`, `patch.restoreCatalogBackup` | Catalog-only byte patches; copy executable before any write. |
| Ghidra | `ghidra.exportWeakFunctions`, `ghidra.exportAddressDecompile`, `ghidra.validateRenameMap`, `ghidra.applyRenameMap` | Read-only exports by default; rename apply requires dry-run artifact, arm phrase, and mutation acknowledgement. |
| Debug/runtime | `debug.resolveCdb`, `debug.planProbeSession`, `debug.startProbeServer`, `runtime.listManagedProcesses`, `runtime.tailManagedLog`, `runtime.stopManagedProcess` | Probe and managed process work only through allowlisted helpers and managed registry. |
| Game harness | `game.inventoryProfile`, `game.prepareSafeProfile`, `game.planLaunchProfile`, `game.launchProfile`, `game.planWindowCapture`, `game.captureWindowFrame`, `game.captureWindowSequence`, `game.planWindowInput`, `game.sendWindowInput` | Copied/safe profiles, explicit launch/input/stop gates, bounded captures. |
| Assets/content/release | `assets.catalogGameFiles`, `content.readDocument`, `release.inspectPolicy` | Read-only catalog/content/policy surfaces. |

## Coverage Matrix

| Area | Audience | Status tags | Current coverage | Known gaps and next objectives |
| --- | --- | --- | --- | --- |
| Save/options format | `player-facing`, `maintainer-facing` | `proven`, `partially proven` | Retail `.bes` / `defaultoptions.bea` fixed-size layout, true dword view, ranks, goodies, kill counters, options entries/tail, TypeScript inspect/compare/plan/preview/copy/apply/restore, and C# parity oracle are documented and tested. | Unknown/reserved bytes remain preserve-only. `CCareerNode.state` is not fully mapped. AppCore retirement needs broader TypeScript golden fixtures. |
| Save/options behavior | `maintainer-facing` | `partially proven`, `desktop-required`, `private-evidence-only` | Steam load semantics for `flag=0` versus `flag=1`, defaultoptions application, and save/menu rewrite behavior are documented from binary/runtime evidence. | More runtime proof is needed before expanding behavior-edit UX beyond known safe fields. Do not synthesize saves. |
| Executable patch catalog | `player-facing`, `maintainer-facing` | `proven`, `desktop-required` | `patches/catalog/patches.v2.json` defines stable and experimental byte patches; WinUI Windowed & Mods and CLI jobs verify, plan, copy, apply, and restore copied executables with preimage and post-write checks. | Runtime effects are not universally proven for every environment. Other specimens need explicit hash/layout review. BSS/runtime-only flags remain non-file-patchable. |
| Windowed/display runtime path | `player-facing`, `maintainer-facing` | `partially proven`, `desktop-required`, `private-evidence-only` | Copied-profile runtime proof used the catalog `force_windowed` path successfully for bounded Game Harness proof. | Packaged portable-bundle proof and broader machine/environment coverage remain missing. |
| Ghidra/function naming | `maintainer-facing` | `proven`, `partially proven`, `desktop-required` | Function-quality queue is closed at **6411/6411 = 100.00%** with `0 / 0 / 0` commentless / exact-undefined / `param_N` debt. Wave1220 validates active current-risk focused accounting at **1179/1179 = 100.00%** with remaining active focused work `0`; current percentages are owned by `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`. Per-source docs, static validation, read-only exports, and rename-map validation/apply jobs exist behind typed boundaries. | Strong/static-coherent names are not the same as complete runtime semantics. Java/name preflight and richer read-back for future rename maps remain useful. Ghidra mutation evidence stays maintainer-only. |
| Source-to-binary mapping | `maintainer-facing` | `partially proven` | Stuart source is indexed and used for names, ownership, and subsystem hypotheses; Steam retail binary, real saves, runtime traces, and Ghidra read-back remain authority. | Do not promote names from source alone. Future objectives should record at least two independent signals before renames or behavior claims. |
| Runtime debugger/probes | `maintainer-facing` | `partially proven`, `desktop-required`, `private-evidence-only` | CDB resolver, probe planner, attach server job, managed registry, bounded log tail, and stop jobs exist. Runbooks and probe files are documented. | Continuous attach/client streaming, deeper target-vfunc proof, environmental hazard retests, and packaged-runtime coverage remain missing. |
| Game Harness capture/input | `maintainer-facing` | `partially proven`, `archived-electron`, `desktop-required`, `private-evidence-only` | Archived Electron desktop dev-mode proof on **2026-04-29** prepared a copied profile, applied `force_windowed` to the copied executable, launched managed `BEA.exe`, captured frames, sent one bounded scoped input, captured again, and stopped the process. There is no WinUI Game Harness page yet. | Browser preview mode does not prove runtime behavior. Continuous frame streaming, semantic gameplay-state interpretation, open-ended autonomy, packaged-runtime proof, and any native WinUI harness port remain missing. |
| Asset/archive coverage | `player-facing`, `maintainer-facing` | `proven`, `partially proven`, `desktop-required`, `private-evidence-only` | Backend extraction pipeline has private baseline counts: loose textures, loose meshes, embedded packed meshes, packed refs, videos, language rows, and a deduplicated catalog. Media and asset catalog jobs consume this shape. | Extracted assets and generated catalogs under private/ignored areas are not public release content. Public extractor packaging and broader UI objective lookup are still future work. |
| Media playback/transcode | `player-facing` | `partially proven`, `desktop-required`, `private-evidence-only` | Catalog-constrained PNG preview and in-app Bink MP4 cache preparation have desktop dev-mode proof for selected rows; constrained OGG playback is exposed. | Packaged portable-bundle media proof, cold-cache Bink coverage, and broader catalog coverage remain missing. |
| Lore/content | `player-facing`, `maintainer-facing` | `proven`, `browser-preview-only` | Curated content allowlist returns community and maintainer docs; renderer search/filter/outline/markdown reading exists; authored markdown body fidelity is guarded; internal document, heading, external HTTPS, unknown, and unsafe-link cases are covered by renderer smoke. | Broader document/content coverage remains ongoing. Do not rewrite authored markdown to avoid renderer work. |
| Release/public safety | `player-facing`, `maintainer-facing` | `proven`, `partially proven` | Release policy inventory classifies allow/review/conditional/deny families; curated bundle policy excludes private game, media, save attempts, raw proof output, private evidence, and operator directives. Compact non-secret state batons can be tracked in public-primary source. Release-lane strategy and Ralph-loop evidence outputs are complete and public-safe. | Portable app ZIPs, generated source/package exports, and legacy bundle outputs remain gated while local deny paths exist. Packaged runtime proof remains separate. |
| UI action coverage | `player-facing`, `maintainer-facing` | `partially proven`, `winui-native`, `browser-preview-only` | WinUI native UI Automation and visual smoke cover Home, Save Lab (including Save Analyzer / Save Editor / Game Options subtabs), Media, Asset Library, Lore, Windowed & Mods, Settings, and About. Archived Electron renderer smoke and Browser Use history remain reference-only for historical lanes such as RE Lab, Game Harness, Release, and Patch Bench. | The required UI action inventory is a separate output. Archived browser action proof must be labeled preview-only unless a WinUI/native or archived Electron desktop job actually ran. |
| Archived Electron CLI/API lane | `maintainer-facing` | `historical`, `desktop-required` | `archive/electron-workbench/packages/cli` preserves the TypeScript `catalog`, `run`, and `list` automation over the archived Electron job runner; prior smoke coverage proved JSON stdout, progress NDJSON, persisted history, and error behavior. | This lane is not the active product automation path. Revalidate with `npm run archive:electron:test:cli-smoke` only when archived workbench health is explicitly in scope. |
| Portable parser/runtime future | `maintainer-facing` | `missing`, `partially proven` | Save, patch, media catalog, and asset tooling contain portable logic that can be reused later. | A WebGPU/WASM/netcode runtime is not in scope for this map. Future work should first isolate portable parsers/loaders and prove clean-room asset viewers before any runtime port. |

## Highest-Value Next Objectives

1. Prove the WinUI product release lane through manual/visual smoke and future installer/signing proof before any public release claim.
2. Keep WinUI Save Lab subtabs, Media playback, Asset Library preview, and Lore reader smoke current as product workflows evolve.
3. Keep archived Electron RE Lab, Game Harness, and Release samples clearly historical unless a later prompt explicitly reactivates that workbench.
4. Add public-safe schema docs for stabilized `job-run.v1` and core payloads.
5. Add focused Ghidra rename-map Java/name preflight or richer target-name read-back before broader mutation waves.
6. Broaden validated AppCore/WinUI fixtures before retiring C# parity/support surfaces.
7. Keep runtime objectives bounded: one observation, one decision, one action at most, one follow-up observation, then stop and record evidence.

## General Objective Record Shape

Use this compact record for each future Ralph-loop RE task:

```text
Objective:
Audience:
Coverage area:
Starting status:
Expected evidence:
Allowed jobs/tools:
Safety boundaries:
Acceptance criteria:
Stop conditions:
Result:
Remaining gaps:
Evidence paths:
```

The evidence paths may point to private evidence reports when needed, but public summaries must not embed raw screenshots, frame PNGs, base64, copied executable bytes, save contents, extracted assets, or private local paths.

## Objective Template: Asset Lookup

Use for texture, audio, video, language, goodie-media, resource-archive, or cross-surface catalog questions.

| Field | Template |
| --- | --- |
| Objective statement | Identify the catalog rows, source archive/file family, exported preview/playback status, and related save/goodie/mission/language references for one named asset or asset family. |
| Required context to read | `reverse-engineering/game-assets/_index.md`, `reverse-engineering/game-assets/extraction-pipeline.md`, `reverse-engineering/quick-reference/_index.md`, current Media UI code, `archive/electron-workbench/apps/electron/src/media-catalog.ts`, and the relevant asset catalog summary if available. |
| Allowed tools/jobs | `assets.catalogGameFiles`, Media catalog UI/API, read-only `rg`, catalog JSON summaries, `content.readDocument`, and read-only docs. |
| Safety boundaries | Treat game files and extracted assets as bring-your-own/private inputs. Do not copy assets into public docs. Do not publish raw media, screenshots, or local absolute paths. |
| Evidence packet shape | Query, matched catalog ids, row counts, media type, source family, preview/playback availability, linked docs, private/public evidence split, and next recommended task. |
| Acceptance criteria | The answer either identifies the requested asset rows or explains that no catalog match exists, and it labels whether evidence came from public docs, browser preview mode, desktop catalog, or private generated catalog. |
| Stop conditions | Stop if the task requires raw asset redistribution, bulk private catalog publication, unexplained local paths, or a new extractor mutation outside the requested lookup. |

## Objective Template: Model/Mesh Investigation

Use when a question asks how a mesh, embedded `CMSH` body, model export, or FBX output relates to game resources.

| Field | Template |
| --- | --- |
| Objective statement | Trace one model/mesh from resource/archive reference to extracted/exported representation and document confidence plus known conversion limits. |
| Required context to read | `reverse-engineering/game-assets/extraction-pipeline.md`, `reverse-engineering/game-assets/aya-asset-format.md`, quick-reference AYA chunk tables, `tools/export_game_assets.py`, `tools/BeaAssetExportHarness/`, and any relevant manifest summary. |
| Allowed tools/jobs | Read-only manifest/catalog inspection, `assets.catalogGameFiles`, `rg`, and documentation reads. Running the extractor is allowed only as a separate bounded desktop/native task with explicit output root. |
| Safety boundaries | Do not ship FBX or extracted mesh data in public docs. Keep AYAResourceExtractor x86/runtime constraints visible. Do not conflate resource archives with mesh/texture asset files. |
| Evidence packet shape | Mesh identifier, source resource family, loose versus embedded status, export status, material/texture references if available, tool version, private evidence location if used, and unresolved conversion issues. |
| Acceptance criteria | The trace is reproducible from public docs or private manifest evidence, and any uncertain ownership or conversion behavior is marked as uncertain. |
| Stop conditions | Stop on malformed/private assets, extractor crashes that require code changes outside scope, or requests to publish copyrighted output. |

## Objective Template: Function/Decompile Lookup

Use for function naming, source parity, vtable, xref, decompile, or behavior questions.

| Field | Template |
| --- | --- |
| Objective statement | Explain one function or small call chain with address, current symbol, source-parity signals, behavior summary, side effects, confidence, and remaining unknowns. |
| Required context to read | `reverse-engineering/binary-analysis/_index.md`, `reverse-engineering/binary-analysis/functions/FUNCTION_COVERAGE_STATE.md`, relevant per-function docs, `reverse-engineering/source-code/_index.md`, quick-reference source tables, and Ghidra runbook if exports are needed. |
| Allowed tools/jobs | `ghidra.exportAddressDecompile`, `ghidra.exportWeakFunctions`, `file.peAddressConvert`, `file.hexRead`, read-only Ghidra/headless exports, and source/docs reads. |
| Safety boundaries | Default to read-only. Do not mutate Ghidra names unless the objective explicitly asks for a rename-map flow and all dry-run/apply gates are satisfied. Source names are hints, not Steam-retail proof. |
| Evidence packet shape | Address list, current symbols, decompile/export artifact path, xrefs/callers, source evidence, behavior summary, confidence label, and rename recommendation if any. |
| Acceptance criteria | At least two independent signals support any promoted semantic claim; otherwise the result documents uncertainty and next probes. |
| Stop conditions | Stop on Ghidra lock/timeouts, ambiguous ownership, missing decompile, mutation requirement, or a need for runtime proof outside the objective. |

## Objective Template: Patch Investigation

Use for byte patches, display/windowing behavior, specimen classification, or prospective catalog rows.

| Field | Template |
| --- | --- |
| Objective statement | Determine whether a patch concept is cataloged, byte-verified, file-backed, safe for copied-target application, and what proof is still needed for runtime behavior. |
| Required context to read | `patches/catalog/patches.v2.json`, `patches/README.md`, `reverse-engineering/binary-analysis/_index.md`, relevant patch analysis docs, `archive/electron-workbench/apps/electron/src/patch-verifier.ts`, and PE/address conversion notes. |
| Allowed tools/jobs | `patch.verifySpecimen`, `patch.planCatalogPatch`, `patch.prepareExecutableCopy`, `patch.applyCatalogPatch`, `patch.restoreCatalogBackup`, `file.peAddressConvert`, `file.hexRead`. Apply/restore only on copied artifact-root executables with required arm phrases. |
| Safety boundaries | Never patch the original Steam/Program Files executable or repo-local private baseline. Reject BSS/runtime-only addresses as file patches. Verify preimage bytes before writes and post-write bytes after writes. |
| Evidence packet shape | Patch id or candidate name, target hash/specimen, VA/file offset conversion, original/patched bytes, plan/apply/restore artifacts if run, runtime proof status, rollback path, and public/private evidence labels. |
| Acceptance criteria | The investigation ends with a ready/blocked/catalog-update recommendation and states whether runtime proof is proven, partial, missing, or private-evidence-only. |
| Stop conditions | Stop on unknown specimen, mismatched bytes, original executable target, BSS-only address, need for unbounded runtime test, or unclear rollback. |

## Objective Template: Save/Options Investigation

Use for `.bes`, `.bea`, `defaultoptions.bea`, career graph, goodies, ranks, kills, settings, keybinds, or save behavior questions.

| Field | Template |
| --- | --- |
| Objective statement | Prove one save/options field or behavior using real baseline files, true-view offsets, preservation checks, and copied-target patch boundaries. |
| Required context to read | `reverse-engineering/save-file/_index.md`, `reverse-engineering/save-file/save-format.md`, `reverse-engineering/save-file/struct-layouts.md`, quick-reference save tables, Save Lab code, `archive/electron-workbench/apps/electron/src/save-patcher.ts`, and `archive/electron-workbench/apps/electron/src/options-patcher.ts` if writing is involved. |
| Allowed tools/jobs | `save.prepareCopy`, `save.planPatch`, `save.previewPatch`, `save.applyPatch`, `save.restoreBackup`, `settings.planOptionsPatch`, `settings.previewOptionsPatch`, `settings.applyOptionsPatch`, file hex reads, and compare/inspect APIs. |
| Safety boundaries | Start from a valid real file. Do not synthesize saves. Preserve size, unknown regions, padding, options entries, tails, and kill metadata. Write only copied artifact-root targets. |
| Evidence packet shape | Source kind, size/version, inspected fields, offsets, before/after known-region comparison, unknown-region preservation statement, artifact schemas, and whether source stayed unchanged. |
| Acceptance criteria | The source is unchanged unless a copied apply was explicitly armed; field behavior is proven by inspection/preview/compare or documented as unresolved. |
| Stop conditions | Stop on invalid size/version, no real baseline, request to overwrite original, need to clobber unknown bytes, shifted-view offset ambiguity, or private save content that cannot be summarized safely. |

## Objective Template: Runtime Observation

Use for one bounded observe/decide/act/observe/stop task against a copied game profile.

| Field | Template |
| --- | --- |
| Objective statement | Observe one real runtime state, choose at most one safe action, perform it only if targeting is exact, observe once more, stop the managed process, and record evidence. |
| Required context to read | `roadmap/status-current.md`, the current tooling implementation, `reverse-engineering/binary-analysis/windbg-cdb-runbook.md` if debugger work is involved, and the private evidence policy. |
| Allowed tools/jobs | `game.inventoryProfile`, `game.prepareSafeProfile`, copied-target `patch.applyCatalogPatch` for `force_windowed` when needed, `game.planLaunchProfile`, `game.launchProfile`, `game.planWindowCapture`, `game.captureWindowFrame`, `game.captureWindowSequence`, `game.planWindowInput`, `game.sendWindowInput`, `runtime.listManagedProcesses`, `runtime.tailManagedLog`, `runtime.stopManagedProcess`, and CDB jobs when explicitly in scope. |
| Safety boundaries | Desktop shell only. Use copied/safe profiles outside the repo root. No original executable mutation. No open-ended autonomy. Input must be allowlisted, armed, and targeted to the managed `BEA.exe` window/PID/HWND. Stop the managed process before completion. |
| Evidence packet shape | Objective, copied profile status, patch status, launch run id, capture plan/result, selected action and rejected alternatives, input result, second observation, stop result, final registry state, and public/private evidence split. |
| Acceptance criteria | One bounded loop is completed and the process is stopped, or the task reports a clear stop reason without sending input. |
| Stop conditions | Stop on missing copied profile, unpatched fullscreen capture risk, no window, multiple ambiguous windows, stale PID/HWND, focus/target mismatch, unsafe input, raw private evidence leakage, or user request for broad autonomy. |

## Objective Template: UI/Workbench Interaction

Use for button/control/action investigations in Home, Save Lab, Media, Asset Library, Lore, Windowed & Mods, RE Lab, Game Harness, Release, shell navigation, or command/search.

| Field | Template |
| --- | --- |
| Objective statement | Verify one visible action or workflow path and classify it as working, disabled-by-design, planned, broken, or unclear. |
| Required context to read | Owning WinUI XAML/code-behind or AppCore service, `roadmap/status-current.md`, `roadmap/winui-toolchain-and-qa-direction.md`, relevant UI tests, and archive docs only when deliberately inspecting archived Electron reference material. |
| Allowed tools/jobs | Native WinUI UIA/visual checks for active product behavior; AppCore/C# CLI/tools for non-UI behavior; Browser Use or archived renderer smoke only for archived/reference browser-visible behavior. |
| Safety boundaries | Do not bypass typed preload/job APIs. Do not treat browser preview-mode success as native proof. Do not rewrite authored Lore markdown to avoid link-handling work. |
| Evidence packet shape | Action label, component, intended behavior, proof method, status, errors/console output if relevant, and follow-up or fix. |
| Acceptance criteria | The action either works, explains why it is disabled/planned, or has a concrete follow-up. No major action silently does nothing. |
| Stop conditions | Stop on unclear user-destructive behavior, raw privilege request from renderer, fixture/native proof mismatch, or need to run BEA/native tools outside the allowed objective. |

## Maintenance Rules

- Update this map when a coverage status changes materially.
- Keep public-safe summaries here; keep raw runtime/game/media evidence private or ignored.
- Do not add private screenshots, copied executable bytes, save contents, extracted assets, base64 payloads, secrets, or raw local proof JSON to this file.
- When correcting lookup tables, update both `reverse-engineering/quick-reference/` and the canonical detailed doc.
- When browser preview mode is the only proof, say so explicitly.
- When a desktop/native runtime pass proves behavior, record whether it was desktop dev, packaged bundle, or private runtime evidence.
