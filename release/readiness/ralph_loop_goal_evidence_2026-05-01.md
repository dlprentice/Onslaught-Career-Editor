# Ralph-loop Goal Evidence - 2026-05-01

Status: public-safe evidence packet
Date: 2026-05-01
Branch: `wip/sandbox`

## Goal

Goal file:

- `roadmap/goals/2026-05-01-ralph-loop-agentic-re-master-goal.md`

Invocation summary:

- Use the Ralph-loop goal as the controlling objective.
- Fix Lore markdown link behavior without rewriting authored markdown.
- Inventory major UI actions and fix misleading or broken major actions.
- Create an RE coverage map and reusable objective templates.
- Create a WebGPU/WASM/netcode feasibility dossier that keeps browser runtime work scoped to future prerequisites.
- Create a release-lane strategy comparing curated release output with repo-as-release.
- Update release policy evidence and state files.
- Run the required closeout gates.
- Commit and push the completed goal work.

Start commit:

- `de5e929c09b37bae9f9510cdf5a218565784c7e1`

Evidence-report commit: `1456dc2324ffe263df8fcc7f6f48f5d94d4a5fcc`

## Required Output Checklist

| Required output | Status |
| --- | --- |
| `roadmap/interaction-audit/2026-05-01-ui-action-inventory.md` | Complete |
| `roadmap/reverse-engineering/coverage-map.md` | Complete |
| `roadmap/web-runtime/webgpu-wasm-netcode-feasibility.md` | Complete |
| `release/readiness/release_lane_strategy_2026-05-01.md` | Complete |
| `release/readiness/ralph_loop_goal_evidence_2026-05-01.md` | Complete |

## Workstream Summary

### Baseline Intake

- Read the repo operating contract, state files, active roadmap documents, release readiness docs, curated release manifest, UI/Lore code, renderer smoke logic, and release evidence.
- Confirmed the active work should stay inside the Electron typed-backend model, with browser proof clearly labeled as renderer/UI proof rather than native runtime proof.
- Updated state files early to record the goal while it was active.
- Corrected the global agent policy separately so future worker subagents must use `gpt-5.5` with `reasoning_effort = "xhigh"`.

### Lore Markdown Links

Changed files:

- `packages/ui/src/components/lore/MarkdownRenderer.tsx`
- `packages/ui/src/components/lore/LoreSection.tsx`
- `packages/ui/src/components/lore/ArticleReader.tsx`
- `apps/electron/src/content-browser.ts`
- `packages/ui/src/lib/bridge.ts`
- `packages/ui/src/lib/mock-data.ts`
- `packages/ui/src/App.tsx`
- `apps/electron/src/main.ts`

Proof summary:

- Authored markdown is still rendered as authored.
- Markdown links are intercepted by the renderer instead of allowing the browser to navigate away from the workbench.
- Internal curated document links select the matching Lore document.
- Heading links scroll within the current article.
- External HTTPS links use the existing `shell:openExternal` boundary.
- Unknown links stay inside the reader and show a clear notice.
- Unsafe link schemes are blocked in code.
- Renderer smoke now covers internal document links, heading links, external links, unknown links, and authored markdown fidelity.

### UI Action Inventory And Fixes

Output:

- `roadmap/interaction-audit/2026-05-01-ui-action-inventory.md`

Fixes applied:

- RE Lab sample search/filter/result selection now updates local UI state instead of looking static.
- RE Lab `Create bounded plan` now creates a visible local plan-ready state without starting automation.
- RE Lab remains honest that current Hawk/example rows are sample investigation rows, not live extracted game results.
- Game Harness scoped input send now requires a visible exact-target confirmation and a launched managed process before the button can run.
- Game Harness custom investigation planning is intentionally disabled with honest future-feature copy instead of appearing to be a no-op.

Proof summary:

- Renderer smoke checks the new RE Lab bounded-plan state.
- Renderer smoke checks Game Harness launch wiring and exact-target input arming.
- The inventory classifies actions as working, disabled-by-design, planned, preview-only, desktop-required, or needing future follow-up.

### Agentic RE Objective Model

Output:

- `roadmap/reverse-engineering/coverage-map.md`

Summary:

- Tracks save/options, executable patching, Ghidra/function naming, source-to-binary mapping, runtime probes, Game Harness capture/input, assets, media, Lore/content, release/public safety, UI action coverage, CLI/API lane, and web-runtime future work.
- Separates `proven`, `partially proven`, `missing`, `browser-preview-only`, `desktop-required`, and `private-evidence-only`.
- Adds reusable objective templates for asset lookup, model/mesh investigation, function/decompile lookup, patch investigation, save/options investigation, runtime observation, and UI/workbench interaction.

### WebGPU / WASM / Netcode Feasibility

Output:

- `roadmap/web-runtime/webgpu-wasm-netcode-feasibility.md`

Summary:

- Keeps the near-term product direction on Electron + typed backend + CLI.
- Scopes WebAssembly to future portable parsers, validators, asset loaders, simulation kernels, and browser-safe viewers.
- Scopes WebGPU to future asset/scene viewer and clean-room renderer prototypes after loaders and semantics are proven.
- Defers netcode until deterministic or server-authoritative clean-room runtime slices exist.
- Uses current official source families from MDN and Emscripten, plus repo RE docs.

### Release Lane Strategy

Output:

- `release/readiness/release_lane_strategy_2026-05-01.md`

Summary:

- Recommends keeping the curated release lane for now.
- Explains why `.gitignore` is not a release boundary for tracked files.
- Defines player/community, maintainer/private, and public release lanes.
- Lists deny families and the generated release artifacts that prove inclusion/exclusion.
- States that signed/installer-grade readiness is not proven.
- Keeps packaged runtime media/Game Harness proof as the next substantive release gap.

## Verification

| Command | Result | Important output |
| --- | --- | --- |
| `npm run typecheck` | PASS | Contracts, Electron, CLI, and UI typechecks passed. |
| `npm run build:electron` | PASS | Contracts and Electron built. |
| `npm run test:electron-parity` | PASS | Electron parity passed against save/options fixtures and executable fixture. |
| `npm run test:cli-smoke` | PASS | CLI smoke passed with catalog/run/list behavior. |
| `npm run build` | PASS | Contracts, Electron, CLI, and UI build passed. |
| `npm run test:renderer-smoke` | PASS | Renderer smoke returned `ok: true`; includes visible-copy audit, Media, Lore link handling, RE Lab plan state, Game Harness input arming, Patch Bench, and Release. |
| `npm run test:bundle-policy` | PASS | Electron bundle policy smoke passed. |
| `npm run test:bundle-smoke` | PASS | Portable bundle smoke passed and launched packaged renderer smoke successfully. |
| `py -3 tools\docsync_check.py` | PASS | Dsync policy check passed. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS after regeneration | Release profile snapshot check passed. |
| `py -3 tools\release_curated_manifest.py --check` | PASS after regeneration | Curated allowlist check passed. |
| Public allowlist deny-family scan | PASS | No top-level private/runtime deny families or denied binary/save suffixes appeared in the public allowlist scan. |
| `dotnet build ".\OnslaughtCareerEditor.Release.slnx" --nologo` | PASS | Build succeeded with 0 warnings and 0 errors; .NET preview SDK notice only. |
| `dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo` | PASS | 19/19 tests passed. |
| `dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 21/21 filtered tests passed. |

## Renderer-Smoke Evidence

Renderer smoke now proves these key UI outcomes:

- Home task routing renders.
- Save Lab inspection flow renders fixture save data and goodie media lookup.
- Media audio player stays inside the active row.
- Media video selected panel shows human status and hides backend details by default.
- Media texture preview still renders.
- Lore search/select still renders `roadmap/electron-workbench-migration.md` and preserves authored `durable artifacts` text.
- Lore markdown internal document, heading, external, and unknown links behave inside the reader/safe boundary.
- Patch Bench presents the guided copy/patch/review flow and hides raw patch offsets by default.
- RE Lab labels sample data honestly and creates a bounded-plan visible state.
- Game Harness launch is wired to `game.launchProfile`, input send is wired to `game.sendWindowInput`, and scoped input send requires visible exact-target confirmation.
- Release shows public-safe posture and packaged-runtime gaps.
- Default visible chrome passes the banned internal-copy audit, while authored markdown body content remains excluded from that chrome audit.

## Release Policy Proof

- `release/readiness/curated_release_manifest.json` already included the release strategy and final Ralph-loop evidence paths.
- `release/readiness/public_candidate_allowlist.tsv` was regenerated after new public docs were added.
- `roadmap/release-allowlist-classification.tsv`, `lore-book/roadmap/release-allowlist-classification.tsv`, `roadmap/release-allowlist-profile.md`, `lore-book/roadmap/release-allowlist-profile.md`, and `release/readiness/private_only_inventory.tsv` were regenerated.
- Curated manifest check passed after regeneration.
- Release profile snapshot check passed after regeneration.
- A direct public allowlist scan found no top-level `game/`, `media/`, `save-attempts/`, `subagents/`, private runtime evidence, operator directive, state files, or denied binary/save suffix entries.

## Private / Sensitive Artifact Handling

- No raw screenshots were committed.
- No raw frame PNGs were committed.
- No raw proof JSON was committed.
- No private game assets or media were committed.
- No data URLs or base64 media were embedded in public-safe docs.
- No copied executable bytes were committed.
- No save contents were committed or synthesized.
- Private runtime evidence remains excluded from the public release surface.
- `game/**`, `media/**`, `save-attempts/**`, `subagents/**`, state files, and `onslaught_codex_directive.md` remain outside public/community release scope.

## Safety Statements

- No original Steam or Program Files `BEA.exe` was patched or mutated in this goal.
- No repo-local `game/BEA.exe` was patched or mutated in this goal.
- No `.bes` save was synthesized from scratch.
- No BEA runtime proof was rerun in this goal.
- No Game Harness runtime launch, frame capture, or input send was performed in this goal.
- No Ghidra mutation was performed in this goal.
- Renderer changes preserve typed IPC/preload/job boundaries and do not add raw Node, shell, debugger, Ghidra, filesystem, process, capture, or input privileges to the renderer.

## Known Remaining Gaps

- Packaged portable-bundle runtime media playback is not separately clicked/proven beyond packaged renderer smoke.
- Packaged portable-bundle Game Harness runtime behavior is not separately proven.
- Continuous frame streaming remains future work.
- Semantic gameplay-state interpretation remains future work.
- Open-ended autonomy remains out of scope; only bounded observe/decide/act/observe/stop proof exists from prior private runtime evidence.
- RE Lab still uses clearly labeled sample rows until real catalog/function-backed search is wired.
- Broader real-media row coverage remains future work.
- Ghidra rename-map Java/name preflight/read-back hardening remains useful future work.
- Full C# parity-oracle retirement remains future work.
- Signed/installer-grade release readiness is not proven.

## Final Git Status

Final `git status --short --branch` is recorded in the closeout response after commit and push.
