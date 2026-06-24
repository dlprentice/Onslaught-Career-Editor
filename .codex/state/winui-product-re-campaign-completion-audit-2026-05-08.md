# WinUI Product / RE Campaign Completion Audit - 2026-05-08

## Objective Restated

Execute a long-running WinUI 3 product advancement and reverse-engineering campaign:

- Make WinUI 3 the primary polished Windows app.
- Keep Electron, WPF, and the old Python GUI/CLI lanes archived/reference-only without destructive deletion.
- Improve WinUI product quality, automation, desktop visual QA, docs, release posture, and repo organization.
- Advance real reverse-engineering evidence for assets, media, logic, and rebuild coverage.
- Treat `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila` as read-only source material only.
- Use copied profiles or app-owned artifact roots for mutation/proof outputs.
- Keep private assets and private proof out of public release scope.
- Iterate Ralph-style with inspect, patch, validate, visual critique, docs/state/evidence updates, and green-wave commit/push.

## Prompt-To-Artifact Checklist

| Requirement | Current artifact/evidence | Status | Notes |
| --- | --- | --- | --- |
| WinUI 3 is primary app lane | `README.MD`, `AGENTS.md`, `roadmap/repo-structure-and-archive-map.md`, `OnslaughtCareerEditor.WinUI.slnx` | GREEN | Active docs and solution structure point to WinUI as primary product. |
| Electron archived/reference-only | `archive/electron-workbench/`, `README.MD`, `roadmap/repo-structure-and-archive-map.md`, repo hygiene rules | GREEN | Electron commands are namespaced as archive health checks, not product gates. |
| WPF archived/reference-only | `archive/legacy-wpf/`, repo map, UiTests reference notes | GREEN | Kept available because tests still inspect historical XAML resources. |
| Old Python GUI/CLI archived/reference-only | `archive/legacy-python/`, repo map | GREEN | Active Python remains `tools/`-style RE/release/docs tooling, not a product GUI lane. |
| WinUI product quality improved | Recent WinUI app commits and evidence under `release/readiness/`, especially Asset Library, Goodies, Save/Patch/Media/Lore evidence | GREEN with remaining polish | Product lane has material improvements, but "objectively superb" is still visual/manual breadth-dependent. |
| Automated code checks improved | `OnslaughtCareerEditor.UiTests`, `OnslaughtCareerEditor.AppCore.Tests`, `npm run test:winui-primary-lane`, focused source guards | GREEN | Latest wave added AppCore.Host model slot coverage guard. |
| Desktop visual QA exists | `WinUiVisualSmokeTests`, ignored screenshots under `subagents/`, maximized/scrolling lessons in docs | GREEN with ongoing need | Visual QA exists and should continue for new UI-affecting waves. |
| Docs up to date with lane reality | `README.MD`, `AGENTS.md`, `CURRENT_CAPABILITIES.md`, `RELEASE_SCOPE_AND_TEST_COMMANDS.md`, repo map, release readiness docs | GREEN | Repo hygiene/doc gates are passing; continue updating after every meaningful wave. |
| Release posture public-safe | `release/readiness/curated_release_manifest.json`, `public_candidate_allowlist.tsv`, release profile artifacts | GREEN | Latest check selected 1420 curated public files; profile counts `R0=1485`, `R2=0`, `R3=2`, `R4=18188`. |
| Current WinUI ZIP package smoke | `release/readiness/winui_zip_current_runtime_smoke_2026-05-08.md` | GREEN for non-cert ZIP lane | Current branch head publishes, zips, writes checksum sidecar, extracts, launches the extracted executable, passes representative Media smoke, and leaves no WinUI process behind. |
| Current unsigned MSIX candidate assembly | `release/readiness/winui_msix_current_candidate_probe_2026-05-08.md` | GREEN for unsigned candidate assembly | Current branch head publishes, stages a scratch package root, assembles an unsigned `.msix` with `makeappx`, verifies contents, and records the package checksum while leaving signing/install unproven. |
| Current local MSIX signing | `release/readiness/winui_msix_current_signing_probe_2026-05-08.md` | GREEN for disposable local signing | Current branch head generates an ignored local PFX, signs a disposable MSIX with `signtool`, verifies `AppxSignature.p7x`, and records the signed-package checksum while leaving trust/install unproven. |
| Current untrusted MSIX install blocker | `release/readiness/winui_msix_current_untrusted_install_probe_2026-05-08.md` | GREEN for safe blocked install proof | Current signed local candidate reaches Windows package deployment and is blocked with untrusted certificate `0x800B0109`; cleanup verifies no local probe package or WinUI process remains. |
| Current installer preflight guard | `release/readiness/winui_installer_preflight_current_msix_evidence_2026-05-08.md`, `tools/winui_installer_preflight.py` | GREEN for guarded-not-ready posture | Preflight now requires current 2026-05-08 unsigned candidate, local signing, and untrusted-install blocker evidence while preserving trusted install/launch/uninstall as blockers. |
| Repo organization supports WinUI focus | `archive/` layout, active root docs, solution split, release deny policy | GREEN | No need to reopen Electron-first structure. |
| Real asset extraction evidence | Full-install catalog evidence, `goodies_preview_coverage_2026-05-07.md`, model texture/material/connection/slot evidence, UV mapping evidence, normal mapping evidence, vertex-color metadata evidence, host diagnostics | GREEN for static extraction | Full-install evidence shows extracted textures/models/Goodies coverage. Static FBX metadata now covers vertices, polygons, normals, UVs, vertex-color layers when present, material mappings, object/property connections, texture bindings, and texture sidecar/catalog linkage. Private raw catalogs stay under `subagents/`. |
| Representative Goodies model-viewer runtime proof | `release/readiness/goodies_model_viewer_runtime_proof_2026-05-08.md` | GREEN for one copied-profile model Goodie | Copied-profile runtime proof selected `BE:A Unit-01 'Pulsar'`, opened the in-game model viewer, accepted bounded input, captured private before/after frames, and stopped with no `BEA`, CDB, Ghidra, or headless Ghidra process remaining. |
| Media evidence | WinUI media/readiness docs and prior playback evidence | YELLOW | Static/catalog and dev evidence exists; broader packaged/media playback proof remains future work. |
| Logic RE evidence | BattleEngine and Goodies evidence reports under `release/readiness/` and `reverse-engineering/` | YELLOW | Many source/Ghidra/runtime bridge probes exist, but rebuild-complete behavior coverage is not proven. |
| Rebuild coverage evidence | Current RE docs and mapped systems | YELLOW/RED | We have useful subsystem mapping and source-to-binary bridges, not enough to claim a scratch rebuild or full gameplay parity. |
| Installed game/original BEA read-only | `AGENTS.md`, release evidence boundaries, copied-profile proof reports | GREEN | Recent evidence states no original executable/game mutation. |
| Private assets/proof excluded | Release profile/curated manifest/public allowlist checks | GREEN | `game/`, `media/`, `save-attempts/`, `subagents/`, `.codex/`, and private runtime evidence remain excluded. |
| Ralph-style wave loop | `.codex/state/winui-product-re-campaign-progress.md`, evidence ledger, pushed commits | GREEN | Recent waves are inspect/fix/validate/evidence/commit/push cycles. |

## Current Completion Verdict

Not complete.

The repo is structurally aligned with the WinUI-first goal and recent asset/Goodies work is evidence-backed, but the full objective still contains open product and RE fronts:

- Static Ghidra RE has advanced into evidence-backed saved mutation tranches rather than name-only coverage. As of Wave 347 on 2026-05-12, the saved database has `5978` function objects, `0` legacy weak names, `1105` commented functions, `4873` commentless functions, `1958` undefined signatures, and `2107` `param_N` signatures. Wave 347 recovered four local `CDebris` boundaries and saved seven `CDebris` names/signatures/comments/tags. This is progress toward function-by-function confirmation, not completion.
- Native textured 3D model rendering is not proven; current WinUI model display is metadata plus wireframe/export-based preview.
- Static FBX renderer-readiness metadata is materially stronger than it was at the start of the audit: UV mapping modes, normal mapping modes, material mapping modes, texture links, and vertex-color absence/presence are now captured and release-documented.
- Material-to-texture visual correctness, shader/material parity, animation, skeletons, camera controls, and lighting are not proven.
- Representative runtime Goodies model-viewer playback is now proven for one copied-profile `BE:A Unit-01 'Pulsar'` path; exhaustive all-45 model coverage, WinUI renderer parity, and material/animation parity are still not proven.
- Current non-cert ZIP package launch/media smoke, unsigned MSIX candidate assembly, disposable local MSIX signing, and untrusted-certificate install blocking are proven; certificate trust, successful install, package-identity launch, uninstall, and installer-grade release proof are still future work.
- Broader media playback proof and packaged media behavior remain future work.
- Logic and rebuild coverage are still partial; source-to-binary bridges do not equal a rebuildable game.

## Next Non-Speculative Options

1. **Native textured/lit model viewer design spike**: create a short design/spec for a minimal WinUI renderer proof before code. This needs user approval because it is new UI/rendering behavior.
2. **Broader representative model runtime coverage**: if runtime breadth is the priority, repeat the copied-profile model-viewer proof for a small representative set rather than all 45 at once.
3. **Packaged WinUI proof**: shift to packaging/release proof for the current WinUI app state.
4. **Targeted static parser gap**: continue read-only AppCore/Ghidra/source analysis only if a concrete unverified FBX/resource field is identified. Do not keep expanding metadata merely because another field might exist.

## Recommended Next Target

Current user direction prioritizes the full static Ghidra function re-audit. Continue in small serialized Ghidra tranches with dry/apply/read-back, state/docs/evidence, actual project backups, and green-wave commit/push discipline; after pushed Wave 347, inspect the refreshed queue for the next coherent high-debt cluster with `param_N` or undefined signature debt.
