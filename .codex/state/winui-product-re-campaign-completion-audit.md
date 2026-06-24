# WinUI Product / RE Campaign Completion Audit

Status: active audit, not complete
Last updated: 2026-05-22

This audit maps the active goal to concrete repo evidence. It is intentionally conservative: a GREEN row means the named requirement has current evidence; a YELLOW row means useful progress exists but the requirement is not fully closed.

## Objective Restated

Concrete success criteria from the active goal:

1. WinUI 3 is the primary polished Windows app in code, docs, tests, and release posture.
2. Electron, WPF, and the old Python GUI/CLI app are archived/reference only, without destructive deletion.
3. WinUI product quality is improved through UI, accessibility, automation, visual QA, and release checks.
4. Docs, lore indexes, release cycle docs, manifests, and state files reflect current reality.
5. Real RE progress is advanced for assets, media, logic, and rebuild coverage.
6. The local game install stays read-only; mutation/runtime proof uses copied profiles or app-owned roots.
7. Private assets, screenshots, raw logs, copied executables, saves, and proof outputs stay out of public release scope.
8. Work proceeds in green, reviewable waves with validation, state/evidence updates, commit, and push.

## Prompt-To-Artifact Checklist

| Requirement | Evidence inspected | Status | Notes / remaining gap |
| --- | --- | --- | --- |
| WinUI 3 is primary product lane | `AGENTS.md`, README, `CURRENT_CAPABILITIES.md`, `.codex/goals/winui-product-re-campaign.md`, state JSON files | GREEN | Current docs and state consistently name WinUI as the user-facing product lane. |
| Electron archived/reference | `AGENTS.md`, `archive/electron-workbench/`, release readiness checklist | GREEN | Electron is under archive and public release posture treats it as optional archive-reference, not product. |
| WPF archived/reference | `AGENTS.md`, release readiness checklist | GREEN | WPF is reference-only in active docs. |
| Old Python GUI/CLI archived/reference | `AGENTS.md`, state JSON files | GREEN | Active Python is limited to `tools/`-style RE/tooling/lab support; old GUI/CLI parity app is not product lane. |
| WinUI automated checks cover major workflows | `.codex/state/winui-product-re-campaign-evidence.md`, `release/readiness/release_readiness_checklist.md` | GREEN with breadth caveat | `cmd.exe /c npm run test:winui-primary-lane` passed on 2026-05-22: WinUI solution build green, AppCore `86/86`, UI `50/52` with the two catalog-dependent Asset Library tests skipped. Evidence also covers media, asset library, visual smoke, accessibility IDs, publish/ZIP probes. It does not prove every row/action in the product. |
| WinUI visual QA captured and summarized safely | `release/readiness/winui_visual_qa_2026-05-05.md`, visual-smoke readiness notes, campaign evidence | GREEN with representativeness caveat | Primary and scrolled/native visual smokes exist, with private screenshots ignored. Not a claim of perfect visual design or full manual review. |
| Release posture current and WinUI-centered | README, `CURRENT_CAPABILITIES.md`, `release/readiness/curated_release_manifest.json`, profile checks in Wave750 plus the 2026-05-22 installer-preflight wave | YELLOW | Release accounting is current at `R0=3489 R2=0 R3=2 R4=18188` with curated/public allowlist `3118`. ZIP/unpackaged, unsigned MSIX, local signing, untrusted-install blocking, and TrustedPeople-only cleanup/blocker evidence exist, but installer-grade trusted install/package-identity launch/uninstall-after-install, SmartScreen, and final legal release approval remain unproven. |
| Docs/lore/release/state match current reality | `roadmap/agent-lessons-learned.md`, lore-book mirror, state JSON, `.codex/state`, docsync/doc-command/md-link gates | GREEN with state-repair note | Canonical docs and repo state are current through Wave750 plus the 2026-05-22 WinUI installer blocker and Goodies observer state repairs. This audit/progress/evidence state set was repaired after lagging at the Wave653 repair snapshot and then corrected for the existing Goodies copied-profile proof. |
| Private/public release exclusions intact | `release/readiness/curated_release_manifest.json`, `release/readiness/public_candidate_allowlist.tsv`, profile snapshots | GREEN | `subagents/`, `.codex/`, private game/media/save/proof families are excluded from public outputs. Latest public allowlist checked `3118` rows after release artifact regeneration. |
| Local game install read-only | Goal file, AGENTS, recent static Ghidra wave evidence, copied-profile policy notes | GREEN for current waves | Recent Wave750 work mutated only saved Ghidra metadata and docs; it did not launch or mutate the installed game. Installed game remains read-only by policy. |
| Asset RE progressed beyond function names | Asset catalog/readability/model texture link/Goodies evidence notes and campaign state | GREEN with scope caveat | Real retail-install catalog/extraction evidence exists for textures, models, media, and Goodies rows. Full material/animation/rebuild parity remains open. |
| Media RE/product playback progressed | Media playback/readability/decodability readiness notes | GREEN with breadth caveat | Representative and broader-family playback/catalog checks exist. All-row playback and installer-grade packaged playback remain unclaimed. |
| Logic RE progressed beyond function names | BattleEngine Ghidra read-back, morph/damage/HUD evidence notes, static re-audit campaign through Wave750 | YELLOW | Meaningful read-back and source/binary bridges exist, and Wave573-Wave750 materially advanced saved Ghidra evidence through MissionScript/datatype/render/media/resource/CDX/CRT/CFastVB/SEH unwind islands. Rebuild coverage and runtime gameplay-state interpretation remain incomplete. |
| Goodies 71-73 static/runtime question advanced | Goodies CLI state override, focused input-observer runtime proof, race-row guard, CDB observer, parser | GREEN with hidden-path caveat | `release/readiness/goodies_input_observer_runtime_proof_2026-05-08.md` proves copied-profile focused CDB input-path observation of the ordinary wall sequence `66, 67, 68, 69, 70, 74` with no `71`, `72`, or `73` returns on that normal path. Hidden, cheat, developer, direct-selection, or non-wall reachability remains open. |
| Commit/push after green waves | Pushed Wave750 and installer-blocker commits plus current state-repair evidence | GREEN with current-wave handoff | Recent waves were validated, committed, and pushed through installer blocker commit `1226986e`; the Goodies observer audit repair adds no runtime mutation and keeps the next open Goodies question scoped to hidden/non-grid reachability. |

## Current Verdict

Goal is not complete.

The repo is materially advanced and structurally aligned with the WinUI-first plan, but the campaign still has real open work:

- Hidden/non-grid Goodies 71-73 reachability remains unproven beyond the copied-profile normal-wall skip proof.
- Installer-grade WinUI release trust/install/uninstall remains unproven.
- Full material/animation/model rendering and row-by-row asset/media coverage remain incomplete.
- Logic RE has strong source/binary read-back islands but not rebuild-level coverage.
- Runtime gameplay-state interpretation and broader runtime RE are still future work.
- Static Ghidra coverage is still partial: after Wave750, `1486` functions remain commentless, `963` signatures remain exact-undefined, and `27` signatures still contain `param_N`.

## Next Concrete Action

Continue from the high-signal static RE queue head, `0x005d2730 Unwind@005d2730`, or the raw commentless head, `0x0042f220 CSPtrSet__Clear`, unless the next product wave deliberately switches to installer-grade WinUI release proof or a hidden/non-grid Goodies 71-73 runtime/static selector investigation. Any runtime work must launch only from a copied profile, keep raw logs/screenshots under ignored `subagents/`, parse private logs locally, and publish only sanitized summaries.
