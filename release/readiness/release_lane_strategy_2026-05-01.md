# Release Lane Strategy - 2026-05-01

Status: active public-safe strategy
Last updated: 2026-05-26

This document defines the release lanes required by the Ralph-loop goal. It is public-safe: it does not include private absolute paths, raw game assets, raw screenshots, raw frame captures, save contents, executable bytes, data URLs, secrets, or private runtime proof payloads.

## Recommendation

Keep the curated public safety/export lane for now, centered on the WinUI-first source candidate.

The private working repository is not shaped like a public release repository yet. It intentionally mixes active WinUI product code, archived Electron/Python/WPF app code, active Python utility/tooling scripts, shared AppCore/C# support, reverse-engineering documentation, generated release evidence, private/local runtime evidence, operator directives, and state files. A broad "publish the repo except ignored paths" model would make release safety depend on every private or historical family being perfectly denied across a mixed workspace.

The near-term release model should therefore remain explicit:

- Player/community deliverables are WinUI-first.
- The curated source candidate includes reviewed WinUI/AppCore/C# CLI/docs/tooling support and excludes archived app surfaces by default.
- Electron is archived/reference under `archive/electron-workbench/`, not an active product or release lane.
- Active Python scripts remain RE/tooling/lab support; the old Python GUI/CLI parity app remains archived/reference, not a shipping GUI/product lane.
- Maintainer/private workflows stay in the private workspace and require typed job boundaries, copied targets, policy gates, and private evidence handling.
- Public release/export artifacts are generated from the curated manifest, generated allowlist, generated private inventory, and relevant bundle/export policy checks, not from a raw repository copy.

Do not claim signed installer readiness from this strategy. The current evidence supports review of a public-safe source/bundle candidate, not signed or installer-grade release readiness.

## Lane Definitions

| Lane | Audience | What ships | What stays private | Required gates | Current proof gaps |
| --- | --- | --- | --- | --- | --- |
| WinUI product lane | Players and community modders using the primary Windows desktop app | Reviewed WinUI/AppCore/CLI/docs/tooling source in the curated candidate; future installer/MSIX deliverables after separate packaging/signing proof. | Bundled game payloads, private `media/**`, private saves, runtime proof captures, raw screenshots, copied executables, local proof JSON, agent/operator directives, state files, and unreviewed dependencies/assets. | WinUI/AppCore build/tests, native Media interaction smoke when runtime media posture is in scope, disposable unpackaged publish smoke when packaging posture is in scope, plus public safety/export checks before any public release. | Signed/installer readiness is not proven; unpackaged publish, focused Media interaction, and published-output Media interaction smoke exist, but installer/MSIX/install-uninstall proof remains future work. |
| Archived Electron workbench lane | Future maintainers inspecting historical Electron/React/TypeScript work | Nothing from this lane ships by default. Narrow ideas may be ported into WinUI/AppCore/tools only after review. | Entire `archive/electron-workbench/**` tree, private runtime proof, generated catalogs with private paths, and old package outputs. | Optional `archive:electron:*` checks only when archive health is deliberately in scope. | It is archived; no active runtime proof is required for product release. |
| Python script/tooling lane | Maintainers doing RE/tooling/lab work | Script outputs or tools ship only if explicitly reviewed and included by policy. | Python GUI/product work, revived archived Python app outputs, private extraction outputs, private asset paths, scratch data, and unreviewed generated artifacts. | Script-specific validation plus docs/public-safety gates. | Active Python tool inventory and validation commands still need a focused pass. |
| Public safety/export lane | Reviewers and future public source/bundle consumers | Curated public source candidate from `release/readiness/curated_release_manifest.json`, generated `release/readiness/public_candidate_allowlist.tsv`, release/readiness evidence summaries, bundle/export policy metadata, and public-safe docs/tests/tools allowed by policy. | All hard-deny families, conditional reference corpora until approved, archived/non-shipping surfaces unless explicitly allowed, and any evidence that exposes private local/runtime material. | `py -3 tools\docsync_check.py`, `py -3 tools\release_profile_snapshot.py --check`, `py -3 tools\release_curated_manifest.py --check`, path-aware allowlist scan for deny families, and lane-specific gates for changed surfaces. | The generated allowlist must be refreshed whenever new public release evidence files are added. A clean public clone/archive review is still required before moving to repo-as-release. |

## Option Comparison

| Option | Summary | Strengths | Risks | Decision |
| --- | --- | --- | --- | --- |
| Option A - keep curated public safety/export lane | Public source candidates come from `release/readiness/curated_release_manifest.json`; the release tooling generates `release/readiness/public_candidate_allowlist.tsv` and `release/readiness/private_only_inventory.tsv`; bundle/export policy separately checks packaged outputs when relevant. | Explicit source surface, reviewable generated evidence, works while private/reference/evidence files remain in the private repo, supports public-safe summaries without publishing raw proof. | More files and terminology for maintainers to understand; generated artifacts can drift if checks are not run after release-surface changes. | Keep now. Simplify names/docs in a coordinated cleanup later. |
| Option B - repo-as-release minus `.gitignore` | Treat the repository itself as publishable, excluding ignored paths and a small denylist. | Simpler once the repo is genuinely public-shaped and private material has been moved or removed. | Unsafe now because ignored rules do not protect tracked files, and this private repo still contains tracked operator/state/reference/evidence surfaces with different release postures. | Do not use yet. Revisit only after the prerequisites below are true. |

## Why `.gitignore` Is Not A Release Boundary

`.gitignore` is workspace hygiene. It prevents matching untracked files from being added accidentally, but it does not remove, hide, or protect files that are already tracked by git.

That distinction matters in this repository. A file can remain tracked and publishable through a clone, archive, branch push, or raw tree export even if a later ignore rule matches it. Removing a tracked file from the public surface requires deliberate index/history/release-policy work; adding an ignore pattern is not enough.

For this project, release safety must be allowlist-first until the repository is public-shaped. The release path should prove what is included, prove what is excluded, and fail when generated release evidence drifts.

## Current Deny Families

These families stay out of public/community release outputs unless a later review sanitizes and reclassifies a narrow subset:

- `game/**`: private local game mirror and retail payloads.
- `media/**`: private/reference media and raw game media.
- `save-attempts/**`: local save experiments, proof saves, and unsanitized fixtures.
- `subagents/**`: agent scratch, local screenshots, generated catalogs, proof JSON, and private run artifacts.
- `release/readiness/private_runtime_evidence/**`: private runtime evidence summaries and related local proof references.
- Binary/save/runtime payload suffixes: `*.exe`, `*.dll`, `*.bes`, `*.bea`, `*.gzf`, plus generated build/test payloads unless an explicit public-safe fixture policy allows a specific file.
- Agent operating state: `.codex/**`, `developer_agent_state.json`, `documentation_agent_state.json`, and `re_orchestrator_state.json`.
- Operator/private prompt contracts, especially `onslaught_codex_directive.md`.
- Ghidra/CDB mutation logs, scratch exports, private debugger evidence, and runtime-only proof material.
- Archived/non-shipping app surfaces unless they are intentionally retained as public parity/reference material.
- Conditional reference corpora such as Stuart source or extractor references until provenance, license, and publication scope are explicitly approved.

The deny policy is family-based because filenames change. Release checks should catch new members of these families, not only today known paths.

## How The Release Pieces Fit Together

`release/readiness/curated_release_manifest.json` is the source candidate policy. It names include patterns for the public candidate and exclude patterns for private, volatile, archived, legacy, and ops-sensitive paths. It includes WinUI/AppCore/C# CLI/docs/tooling support and excludes archived app surfaces by default. It already includes the Ralph-loop strategy/evidence report paths as release-readiness summaries, so those files are intended to be public-safe.

`release/readiness/public_candidate_allowlist.tsv` is generated evidence from the manifest. It is the reviewable file list for the source candidate. It must be regenerated by `py -3 tools\release_curated_manifest.py`, not hand-edited. After generation, run `npm run test:public-allowlist`; it scans path-aware for deny families such as `.codex/`, top-level `game/`, top-level `media/`, `save-attempts/`, `subagents/`, `private_runtime_evidence`, operator directives, state files, denied binary/save suffixes, private absolute user paths, sandbox attachment paths, and embedded base64 data URLs. Run `npm run test:doc-commands` and `npm run test:repo-hygiene` with it to catch stale documented npm commands, tracked stale evidence placeholders, sandbox attachment links, renderer preview-mode wording regressions, and generated build/test output tracked outside private hard-excluded families.

`release/readiness/private_only_inventory.tsv` is generated evidence for excluded or conditional paths. It is useful because it proves the release tooling still sees private-only material as private. It is not a publication list.

`py -3 tools\release_profile_snapshot.py --check` verifies the release profile snapshot artifacts are current. `py -3 tools\release_curated_manifest.py --check` verifies the generated allowlist/private inventory match the manifest and current tree.

`npm run archive:electron:test:bundle-policy` and `npm run archive:electron:test:bundle-smoke` are archived Electron reference checks. They are not WinUI product release gates.

The source lane and bundle lane are complementary:

- curated manifest plus generated allowlist controls source candidate contents
- private inventory records what stayed out
- release profile snapshots catch classification drift
- archive checks can still prove the archived Electron workbench hydrates if a future archive-health task explicitly requires it

## Required Gates By Release Decision

Use the smallest relevant gate for routine documentation edits, but do not call a public release candidate ready until the full relevant gate passes.

| Decision | Required checks |
| --- | --- |
| Strategy/doc-only update | `git diff --check`; targeted read-through of linked release docs; `py -3 tools\release_curated_manifest.py --check` if manifest/allowlist coverage is affected. |
| Public source candidate refresh | `py -3 tools\docsync_check.py`; `npm run test:doc-commands`; `npm run test:md-links`; `py -3 tools\release_profile_snapshot.py --check`; `py -3 tools\release_curated_manifest.py --check`; `npm run test:public-allowlist`; `npm run test:repo-hygiene`. |
| WinUI product lane health | `dotnet build ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj" --nologo`; `dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo`; `dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo --filter "FullyQualifiedName!~LegacyWpf"` where applicable. |
| Archived Electron workbench | Optional `archive:electron:*` checks only when deliberately inspecting archived Electron health. |
| Temporary parity oracle retention | `dotnet build ".\OnslaughtCareerEditor.Release.slnx" --nologo`; `dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo`; `dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo`. |
| Signed or installer-grade release | All above gates plus explicit installer/signing implementation, signing proof, installer install/uninstall smoke, Windows trust/smart-screen posture review, and packaged runtime media/Game Harness proof. This has not been proven. |

## Packaging And Runtime Proof Gaps

The public-safe evidence through 2026-05-01 supports Electron workbench validation, but it no longer decides the primary product lane. The 2026-05-04 through 2026-05-06 WinUI health/product sprint work proved the active WinUI build, focused AppCore/UiTests gates, disposable unpackaged publish launch/visual smoke, focused debug-build Media audio/video interaction, and native generated-catalog Asset Library browsing in the local private tree; signed/installer readiness still needs a separate lane.

Proven:

- Archived Electron build/typecheck/test lanes have prior public-safe evidence.
- Archived renderer smoke has prior public-safe evidence.
- Archived TypeScript CLI smoke has prior public-safe evidence.
- Archived Electron parity and bundle policy/smoke have prior public-safe evidence.
- Desktop dev-mode media preparation/playback proof exists for focused rows, summarized publicly without raw private media.
- Desktop dev-mode Game Harness copied-profile launch/capture/input/capture/stop proof exists, summarized publicly without raw private evidence.
- The UX reset across Home, Save Lab, Media, Lore, Patch Bench, RE Lab, Game Harness, and Release has public-safe evidence.
- Disposable unpackaged WinUI publish smoke and primary-screen launch/visual proof are recorded in `release/readiness/winui_publish_smoke_2026-05-05.md`.
- Focused native WinUI Media audio/video interaction proof is recorded in `release/readiness/winui_media_interaction_smoke_2026-05-06.md`.
- Bounded asset backend smoke is recorded in `release/readiness/asset_backend_smoke_2026-05-06.md`.
- Full-corpus asset backend smoke is recorded in `release/readiness/asset_full_corpus_smoke_2026-05-06.md`, with follow-up hardening recorded in `release/readiness/asset_export_orchestrator_hardening_2026-05-06.md`: full texture, loose mesh, embedded mesh, language, video, and catalog generation now pass when asset export lanes run as separate serial harness processes.
- WinUI Asset Library integration is recorded in `release/readiness/winui_asset_library_integration_2026-05-06.md`: the primary app loads generated local asset catalogs and browses texture, loose-mesh, and embedded-mesh rows without bundling private extracted assets.
- WinUI Asset Library export actions are recorded in `release/readiness/winui_asset_library_export_actions_2026-05-06.md`: selected generated `.png` and `.fbx` exports can be opened/copied through scoped UI actions while native in-app 3D rendering remains unclaimed.
- WinUI model metadata preview is recorded in `release/readiness/winui_model_metadata_preview_2026-05-06.md`: selected generated model exports now show lightweight binary FBX facts in the native Asset Library while full 3D rendering remains unclaimed.
- WinUI dependency/license inventory and current NuGet advisory review are recorded in `release/readiness/winui_dependency_license_review_2026-05-06.md`.
- WinUI dependency compatibility refresh is recorded in `release/readiness/winui_dependency_compatibility_update_2026-05-06.md`: non-major LibVLCSharp, WebView2, NAudio, and VideoLAN.LibVLC.Windows updates build and pass AppCore, active UiTests, and native Media interaction smoke.
- WinUI Windows App SDK 2.x migration is recorded in `release/readiness/winui_windows_appsdk2_migration_2026-05-06.md`: Windows App SDK `2.0.1` builds, active tests pass, disposable publish output launches/renders, and focused published-output Media interaction passes.
- WinUI published notice inclusion is recorded in `release/readiness/winui_published_notice_inclusion_2026-05-06.md`: disposable publish output includes `THIRD_PARTY_NOTICES.md` and still launches.
- WinUI third-party notice drafting and LGPL redistribution posture are recorded in `release/readiness/THIRD_PARTY_NOTICES.winui-draft.md` and `release/readiness/winui_lgpl_redistribution_review_2026-05-06.md`.

Not proven:

- Signed or installer-grade release readiness.
- WinUI signed/installer-grade packaging, MSIX, install/uninstall, trust/SmartScreen posture.
- Legal/compliance approval for LGPL redistribution and final notice text.
- Continuous frame streaming.
- Broader gameplay-state observation or semantic runtime interpretation.
- Open-ended autonomy beyond the bounded observe/decide/act/observe/stop proof.
- Broader real-media row coverage.
- Native 3D model preview for generated FBX exports.
- Full retirement of C# parity oracles.

These gaps should remain visible in release evidence. Browser preview-mode success and renderer smoke are useful UI proof, but they are not proof of native/game/debug/Ghidra runtime behavior.

## When Repo-As-Release Becomes Safe

Revisit Option B only when all of these are true:

1. Hard-deny families are untracked, moved outside the public repository, or replaced by explicitly public-safe fixtures.
2. Operator directives, repo state files, private runtime evidence, and local proof artifacts are absent from the public-shaped repo.
3. Conditional reference corpora have documented provenance, license, and publication decisions.
4. The active product surface is small and obvious: WinUI product, AppCore support, C# CLI, explicitly reviewed Python tools selected for publication, curated docs/lore, release tooling, tests, and still-needed parity oracles only; archived Electron/Python/WPF app source is absent from the public-shaped repo.
5. Archived WPF surfaces and unreviewed Python GUI/product material are removed from the public-shaped repo or isolated outside default release packaging.
6. Release checks prove tracked-file safety and generated-bundle safety, not just ignored-file safety.
7. A clean public clone/archive review finds no private paths, payload suffixes, state files, operator docs, raw runtime evidence, or accidental private media.
8. Public docs explain one release path in plain language, with legacy diagnostics clearly marked as legacy.

Until those conditions are met, a raw repository release is less safe than the curated lane.

## Documentation Cleanup Targets

Do not rename release files casually in this slice. The cleanup should be coordinated so scripts, docs, and references change together.

Recommended naming direction:

- `release/readiness/curated_release_manifest.json` -> consider `source_release_manifest.json`
- `release/readiness/public_candidate_allowlist.tsv` -> consider `source_release_allowlist.tsv`
- `release/readiness/private_only_inventory.tsv` -> consider `release_exclusion_inventory.tsv`
- `release/readiness/redaction_notes.md` -> consider `PUBLIC_SAFETY_NOTES.md`
- `release/readiness/LOCAL_SIGNOFF_COMMANDS.md` -> consider `RELEASE_SIGNOFF_COMMANDS.md`
- `RELEASE_SCOPE_AND_TEST_COMMANDS.md` -> consider `RELEASE_GATES.md` or merge into `release/readiness/release_readiness_checklist.md`

Plain language should be:

- "source release" for curated tree/export policy
- "bundle release" for Electron portable bundle policy
- "private exclusions" for deny families
- "signoff" for local validation commands

## Next Recommended Action

Keep Option A active. Continue WinUI product hardening with deliberate native in-app 3D renderer planning, installer/MSIX planning, and deeper RE reconstruction. Keep Electron packaged/runtime proof as archived maintainer-workbench validation, not as the primary product release gate. Signed/installer readiness should remain out of scope until a signing/installer lane exists and is proven.
