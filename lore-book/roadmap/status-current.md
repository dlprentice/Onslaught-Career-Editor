# Current Status

Status: active
Last updated: 2026-06-24

## Development Focus

The repo is now WinUI-first.

- primary product: `OnslaughtCareerEditor.WinUI`
- shared core: `OnslaughtCareerEditor.AppCore`
- C# support CLI: `OnslaughtCareerEditor.Cli`
- active tests: `OnslaughtCareerEditor.AppCore.Tests`, `OnslaughtCareerEditor.UiTests`
- active utility/tooling scripts: tracked public-primary `tools/` source, with hard payload inputs supplied through ignored local overlays
- archived Electron detour: tracked reference source under `archive/electron-workbench/`; not shipped as the active app payload
- archived Python GUI/CLI parity app: tracked reference source under `archive/legacy-python/`; not an active product lane
- archived WPF app: tracked reference source under `archive/legacy-wpf/`; not an active product lane

Electron, WPF, and the old Python GUI/CLI app remain tracked in this public-primary repo for reference, provenance, and selective inspection. They are not active product lanes and are not part of the default shipped WinUI app ZIP. Active Python work is limited to RE/tooling/lab scripts, not a shipping GUI/product lane.

Repo cleanup and archive decisions are tracked in `roadmap/repo-structure-and-archive-map.md`; use that map before moving or deleting legacy, local-overlay, or release-excluded surfaces.

## Ghidra Static RE Posture (Steam retail)

- Loaded Ghidra function-quality queue: **6411/6411 = 100.00%** with `0 / 0 / 0` commentless / exact-undefined / `param_N` debt.
- Wave1220 aggregate static closeout acceptance validates active current-risk focused accounting at **1179/1179 = 100.00%** with remaining active focused work `0`.
- This is rebuild-grade static-contract posture, not runtime gameplay proof, exact layout proof, rebuild parity, or no-noticeable-difference proof.
- Detailed static-measurement ledgers and RE contracts are tracked in this public-primary repo. Full Ghidra project databases/backups remain local overlays; the repo carries deterministic exports, ledgers, docs, scripts, and compact proof summaries.
- Static summary front door: `reverse-engineering/public-static-contracts.md` plus `reverse-engineering/RE-INDEX.md`.

## Current WinUI Product Features

- Primary nav surfaces: Home, Save Lab, Media, Asset Library, Lore, Windowed & Mods, Settings, and About.
- Save Lab has three subtabs: **Save Analyzer**, **Save Editor** (`.bes`), and **Game Options** (`defaultoptions.bea` / global options), with copy-first patching and a built-in task guide.
- Save Lab and settings/options editing are backed by AppCore.
- Media, Asset Library, Lore, Settings, About, and Windowed & Mods surfaces in the WinUI app.
- Home page primary task buttons and setup status expose stable UI Automation IDs. Every WinUI page button and every named page-level input is guarded by source-level automation ID audits, duplicate automation IDs are checked in source XAML, and interactive controls are guarded for human accessible-name sources.
- AppCore normalizes malformed local config before WinUI uses it, and the WinUI shell persists clamped native window dimensions between launches.
- Focused WinUI Media smoke proves desktop UI selection plus inline audio and video playback against a read-only local install; broader-family playback now samples Music, Tutorial, Status Messages, Mission voice, Racing, Main Videos, Cutscenes, and Mission Briefings through the native UI.
- Focused WinUI Media catalog coverage smoke proves broader read-only catalog enumeration across 629 audio rows and 66 video rows; a catalog-wide decodability/header smoke proves 629/629 audio rows have parsed duration labels and 66/66 video rows have readable Bink headers. Playback is proven for selected focused and broader-family sample rows, not every row.
- Focused WinUI Lore smoke proves native UI Automation can search the curated lore library, select a filtered document, show the in-app reader, and capture private visual evidence without exposing full local paths in the primary UI.
- Focused WinUI Settings smoke proves native UI Automation can auto-detect the read-only local install in isolated app state, keep the primary install summary path-safe, and expose the full path only through explicit details.
- Current WinUI visual QA refresh captures Home, Save Lab, Media, Asset Library, Lore, Windowed & Mods, Settings, and About from the native desktop app and records a public-safe screenshot review.
- Maximized scrolled-section WinUI visual smoke captures lower workflow regions for Home, Save Lab, Asset Library, Windowed & Mods, Settings, and About.
- Windowed & Mods creates app-owned playable copied game folders and separated BEA.exe-only technical copies before verifying, applying, restoring, launching, stopping, or staging copied-game music. The original `BEA.exe` remains read-only source material.
- Windowed & Mods now shows sanitized safe-copy profile catalog source/schema/hash-prefix metadata beside the selected preset, and packaged WinUI output includes `patches/catalog/safe-copy-profiles.v1.json` beside `patches.v2.json` so the app can load tracked safe-copy profiles after extraction. This is UI/accounting and package-content clarity only; it does not add a BEA launch, byte patch, Host/Join enablement, online proof, music audible-output proof, or installed-game mutation.
- Windowed & Mods/runtime proof is the active post-static lane. Current proof accounting lives in `roadmap/mod-patch-runtime-rebuild-register.md`; raw copied-runtime bundles, screenshots/frame dumps, and raw CDB logs remain local overlays.
- Windowed & Mods now includes the bounded `Debug Camera Preview` safe-copy profile for copied executable testing. It combines resolution/windowed/free-camera/Q-forward patch rows on the copied target only; it is a debug/control profile, not a player-ready camera system or online proof.
- Second-host readiness/run-kit artifact intake now fails closed for oversized local JSON, missing/non-false proof keys, nested truthy Host/Join/online overclaims, private/sensitive strings, unsupported statuses, out-of-range counters, and ready-to-run prerequisite mismatches. Host/Join remains disabled until accepted distinct-endpoint command-source and source-bound copied-runtime causality proofs exist.
- Current safe-copy music support includes copied-track and external-OGG staging plus three named shipped-track presets: `BEA_02 over BEA_01`, `BEA_01 over BEA_02`, and `BEA_02 over BEA_04`. The latest bounded proof ties `use-bea02-for-bea04` to a level-100 CDB selection/decode path with two visual captures, one async music kick, one Ogg open, one Ogg read, and no installed-game mutation. The music audible-proof contract preserves `runtimeAudibleOutputProof=false`; a private audio-loopback backend preflight proved bounded WASAPI capture can observe an explicitly armed calibration tone, but not BEA output. Real audible playback still requires bounded audio capture plus a clean same-level baseline comparison and CDB correlation. Audible playback, looping, volume/mixing, arbitrary OGG compatibility, and all-cue coverage remain unproven.
- Current online/multiplayer work has strong same-workstation P1/P2 host-authority and N-slot protocol/process/socket proof, but still has `0` true multi-host LAN gameplay, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, 4+ original-binary runtime players, deterministic sync, rollback, or anti-cheat proof.
- Bounded asset backend smoke proves the Python/.NET extraction pipeline can inventory AYA resources, export one texture, export one loose mesh, export one embedded mesh, export language rows, export a video manifest, and build a catalog from the read-only local install.
- Full-corpus asset backend smoke plus split-lane orchestrator hardening proves the read-only local install can drive catalog generation and bulk export lanes for textures, loose meshes, embedded meshes, language rows, and videos; in-app playback and packaged-bundle media proof remain separate.
- WinUI Asset Library loads generated local asset catalogs and browses texture, loose-mesh, and embedded-mesh rows while keeping private paths collapsed.
- WinUI Asset Library now auto-selects a generated row and offers scoped open/copy actions for exported `.png` and `.fbx` files.
- WinUI Asset Library reads lightweight binary FBX metadata for generated model exports and shows visible model facts in the selected-row detail view.
- WinUI Asset Library renders a bounded in-app wireframe preview from generated binary FBX vertices and polygon indices; the current private full-corpus catalog reports 352/352 generated model rows with preview data after bounded zlib-array support, a focused real-catalog native visual smoke proves one real texture preview plus one real FBX wireframe preview, a catalog-wide readability probe reports 828/828 readable PNG texture exports plus 352/352 readable model exports, and a native row-breadth smoke now cycles representative texture, loose-mesh, and embedded-mesh rows through search/select preview state.
- WinUI dependency/license review inventories current NuGet package posture; WinUI notice drafting and LGPL binary-release checklist are now public-safe release evidence.
- Current WinUI NuGet vulnerability check reports no vulnerable packages from configured sources.
- WinUI non-major runtime/media dependency refresh is proven for LibVLCSharp, WebView2, NAudio, and VideoLAN.LibVLC.Windows.
- WinUI Windows App SDK 2.x migration is proven at source, automation, disposable publish, launch/visual, and focused published-output Media interaction level.
- WinUI disposable publish output includes `THIRD_PARTY_NOTICES.md`.
- Disposable published-output WinUI Media playback now proves the representative Music, Tutorial, Main Videos, and Cutscenes sample from the publish folder; the same sample also passes after ZIP README inclusion, packaging, SHA-256 sidecar generation, and clean extraction. Trusted install/launch/uninstall remains unproven.
- WinUI installer/signing preflight guards the current release posture as `guarded-not-ready`; disposable unpackaged publish, ZIP README/package/checksum/extract launch smoke, dated ZIP RC naming, unsigned MSIX assembly, local MSIX signing, and untrusted install blocking are proven. The explicit trusted-install probe now records that unattended CurrentUser Root trust is refused and TrustedPeople-only trust still leaves install blocked, so trusted install/launch/uninstall and installer-grade release are still unproven.
- WinUI product-lane tests cover launch smoke, product copy hygiene, contrast/static checks, and archived-WPF regression references.
- A post-hardening primary-lane validation run passed the WinUI solution build, AppCore tests, and active UiTests.
- `npm run test:winui-primary-lane` now wraps the same primary validation sequence and shuts down build servers afterward to reduce idle local process leftovers.

## Remaining Product Gaps

- Broader manual WinUI exploratory smoke beyond the current automated visual/contact-sheet review.
- Disposable unpackaged WinUI publish, ZIP README/package/checksum/extract launch smoke, dated ZIP RC naming, unsigned MSIX assembly, local MSIX signing, untrusted install blocking, and the blocked trusted-install probe are recorded; trusted install/launch/uninstall and installer-grade Windows release remain unproven.
- LGPL legal/compliance approval and installer-grade redistribution review remain unproven for public WinUI binary packaging.
- All-row playback coverage beyond the broader-family Media sample remains future work; broader catalog enumeration, catalog-wide decodability/header checks, and selected broader-family playback are recorded.
- Full native in-app 3D model rendering for generated FBX exports remains unproven; current model inspection uses lightweight in-app model facts, focused real-catalog visual smoke, full-corpus bounded wireframe geometry preview coverage, catalog-wide export readability checks, and scoped external open/copy actions.
- BattleEngine logic reconstruction has a read-only source-anchor coverage probe for selected damage, shield, transform, energy, configuration, and god-mode source mechanics; Steam retail binary identity and runtime gameplay-state interpretation remain unproven.
- A historical source-to-binary gap probe classified all 12 selected mechanics anchors as source-only at that time. Later static work now identifies selected retail rows, including `0x0040a580 CBattleEngine__Morph`, `0x004081c0 CBattleEngine__Move`, and `0x00410c50 CBattleEngineJetPart__Move`; complete anchor coverage, ABI recovery, copied-runtime behavior, measured constants, and rebuild parity remain open.
- A config-defaults binary-doc probe adds value-level support for selected `CBattleEngineData__Initialise` defaults, and a fresh headless Ghidra read-back probe now validates selected `CBattleEngineData__Initialise`, `CBattleEngine__Init`, and `CPlayer__Init` tokens. Broader exact retail identity for individual gameplay mechanics and runtime interpretation remain unproven.
- A fresh Unit/Mech mechanics read-back probe validates selected `CUnit__ApplyDamage`, `CUnit__Init`, `CUnit__UpdateTransform`, `CMech__InitCockpit`, and `CMech__InitTargeting` decompile tokens. Runtime gameplay-state interpretation, exact identity for every selected source anchor, and rebuild parity remain unproven.
- A fresh BattleEngine helper read-back probe validates selected transform/target/projectile helper tokens for `CBattleEngine__SwapPrimarySecondaryPartReadersForState`, `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`, `CBattleEngine__SelectNearestForwardTargetFromGlobalSet`, and `CBattleEngine__IsCurrentResolvedEntry`. Runtime gameplay-state interpretation and rebuild parity remain unproven.
- A historical transform-string xref probe validates `flytowalk`/`walktofly` references under the names saved at that time. The HUD-warning references occur inside the body now identified as `0x004081c0 CBattleEngine__Move`; the xrefs alone do not prove runtime playback or trigger behavior.
- The transition/HUD helper read-back remains useful body and call-chain evidence, but the 2026-07-12 movement crosswalk supersedes its affected Monitor owner labels. Runtime transform/HUD behavior, measured values, and rebuild parity remain unproven.
- Static event, state-gate, animation, reader-swap, and source-order evidence identifies `0x0040a580` as `CBattleEngine__Morph`. Copied-runtime transform timing, rejection behavior, camera response, energy behavior, and rebuild parity remain unproven.
- A fresh HUD warning source/xref bridge ties source low-armour/low-energy HUD warning sample anchors to existing retail string-xref evidence without claiming live HUD playback.
- A fresh damage source/read-back bridge ties selected source damage anchors to existing `CUnit__ApplyDamage` read-back evidence without claiming exact `CBattleEngine::Damage` control-flow identity or runtime behavior.
- Ghidra rename-map local preflight now rejects malformed rows before headless dry/apply; live Ghidra dry/apply/read-back remains future mutation-enabled work.
- Copied-profile Game Harness proof completed on **2026-04-29** in the **archived Electron workbench** (prepare profile, `force_windowed` on copied `BEA.exe`, launch, capture, bounded scoped input, capture again, stop). There is no WinUI Game Harness page yet; continuous streaming, broader gameplay-state observation, packaged/runtime coverage, and any native WinUI harness port remain future RE/tooling work, not current product proof.
- Exhaustive Asset Library row-by-row native UI render/preview coverage remains future work; representative native row-breadth interaction and catalog-wide exported PNG/FBX readability are now recorded.

## Release Direction

Current release work is focused on:

1. WinUI 3 lane hardening, visual/run smoke, and future packaging/signing proof
2. AppCore/C# CLI support while the Windows lane stabilizes
3. framework-neutral public-primary hard-payload and release ZIP policy
4. keeping archived app detours out of default shipped WinUI release outputs

## Active Host Shape

| Surface | Status | Notes |
|---|---|---|
| `OnslaughtCareerEditor.WinUI` | Active | Primary product direction, including Windowed & Mods |
| `OnslaughtCareerEditor.AppCore` | Active | Shared correctness/core support |
| `OnslaughtCareerEditor.Cli` | Active support | C# analyzer/patcher CLI |
| `OnslaughtCareerEditor.AppCore.Host` | Support/reference | JSON/stdio diagnostics |
| `OnslaughtCareerEditor.AppCore.Tests` | Active | Core regression tests |
| `OnslaughtCareerEditor.UiTests` | Active | WinUI/static/contrast/launch-smoke tests |
| `archive/electron-workbench` | Tracked archived reference | Former Electron/React/TypeScript app and CLI; not shipped app payload |
| `archive/legacy-python` | Tracked archived reference | Historical Python GUI/CLI parity app; not active product payload |
| `archive/legacy-wpf` | Tracked archived reference | Historical WPF app; not active product payload |
