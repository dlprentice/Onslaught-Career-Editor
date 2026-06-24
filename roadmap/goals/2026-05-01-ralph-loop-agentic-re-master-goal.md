# Ralph Loop Agentic RE Master Goal

Status: completed goal prompt
Last updated: 2026-05-01

> Build the operating model for sustained agentic reverse-engineering progress. Do not use this goal to port Battle Engine Aquila to WASM/WebGPU.
> Completed evidence is recorded in `release/readiness/ralph_loop_goal_evidence_2026-05-01.md`; this file remains as the historical goal contract, not as the current active prompt.

## How To Invoke

Use this file as a Codex `/goal` target:

```text
Use roadmap/goals/2026-05-01-ralph-loop-agentic-re-master-goal.md as the Goal.

Work until every acceptance criterion in that file is satisfied.

Do not mark the goal complete until the evidence packet required by the file is produced, all required checks pass, and the working tree is clean after commit/push.
```

The goal agent owns implementation, tests, docs, evidence, and final cleanup for this goal. A setup agent may prepare this file, but must not claim the goal complete.

## Strategic Direction

The Mario Party-style loop is useful here as a disciplined operating model:

```text
Use a persistent objective file.
Let the agent loop against that file.
Make progress measurable.
Force evidence after every slice.
Keep unfinished items explicit.
```

Apply that loop to structured RE progress, not a premature browser runtime port.

The architecture posture for this goal is:

```text
Layer 1 - RE Workbench
Electron + typed backend.
Used for filesystem, Ghidra, debugger/CDB, VLC, Win32 capture, process launch/stop, private evidence, and packaged runtime proof.

Layer 2 - Portable Knowledge / Asset Core
Format parsers, asset loaders, texture/model/audio/video/language tooling, dependency graphs, save/config parsers.
Write these so selected pieces can later run in Node, Electron, or browser contexts.

Layer 3 - Web Runtime Prototype
Future WASM/WebGPU renderer, user-provided assets, clean-room runtime, and possible netcode.
This goal only scopes feasibility and prerequisites for that layer.
```

Key call: **WASM later, Electron backend now.**

Bad version:

```text
Goal: RE the entire game and port it to WebGPU.
```

Good version:

```text
Goal: Build a Ralph-loop RE operating model.
Fix all broken app interactions.
Make every button/action understandable.
Fix Lore markdown links.
Create the RE coverage map.
Create objective templates for texture/model/function investigations.
Create a WebGPU/WASM feasibility dossier.
Keep release docs and private evidence safe.
```

The current repo is explicitly an Electron workspace with typed backend boundaries, renderer smoke tests, CLI smoke tests, bundle policy checks, and bundle smoke checks. A browser port does not remove the native backend need because the active workflows require capabilities a normal browser app cannot directly provide: launching `BEA.exe`, capturing a Win32 game window, running Ghidra/CDB/PowerShell helpers, using VLC to prepare Bink video playback, and managing private local artifacts.

Use this goal to build the RE operating system first. The long-term order is:

```text
1. Fix the app's broken interactions.
2. Make every action understandable.
3. Build a persistent RE objective model.
4. Build asset/code/runtime coverage maps.
5. Use the agentic loop to fill coverage domain by domain.
6. Build portable parsers/loaders.
7. Prototype a clean-room renderer.
8. Only then explore WASM/WebGPU/netcode seriously.
```

## Ralph Loop Rhythm

Every work slice should follow this rhythm:

1. Select one measurable objective from this file or the coverage map.
2. Read the owning code/docs/state before changing anything.
3. Define the expected evidence before implementation.
4. Make the smallest coherent code/doc/test change.
5. Run the targeted check that proves or disproves the slice.
6. Record what changed, what was proven, what remains unknown, and where evidence lives.
7. Update state files for meaningful progress.
8. Continue to the next objective until acceptance criteria are complete, then produce the final evidence packet.

Stop and report instead of improvising if a slice requires destructive filesystem changes, original executable mutation, unclear private-data handling, unsafe renderer privileges, or user approval for commit/push.

## Non-Negotiable Boundaries

- Read `AGENTS.md`, `developer_agent_state.json`, and `documentation_agent_state.json` before making changes.
- Preserve user changes. Never reset or revert unrelated work.
- Do not patch or mutate the original Steam/Program Files `BEA.exe`.
- Do not synthesize `.bes` saves from scratch. Always copy a real baseline first.
- Keep native/game/debug/Ghidra work behind typed IPC/job boundaries.
- Renderer code must never receive raw Node, shell, debugger, Ghidra, filesystem, or input privileges.
- Browser preview-mode success is not proof of real native behavior. Label preview-mode, desktop shell, packaged bundle, and real runtime proof separately.
- Keep private/runtime evidence, raw game assets, screenshots with private imagery, `game/**`, `media/**`, `save-attempts/**`, `subagents/**`, state files, and operator directives out of public/community release surfaces.
- Do not remove the curated release lane casually. `.gitignore` is not sufficient protection for tracked files.
- Do not rewrite authored Lore markdown content to make renderer behavior easier. Fix the renderer/link handling instead.
- Do not begin a full game port, WebGPU renderer, netcode layer, or clean-room runtime implementation under this goal.

## Required Output Files

Produce these files before marking the goal complete:

```text
roadmap/interaction-audit/2026-05-01-ui-action-inventory.md
roadmap/reverse-engineering/coverage-map.md
roadmap/web-runtime/webgpu-wasm-netcode-feasibility.md
release/readiness/release_lane_strategy_2026-05-01.md
release/readiness/ralph_loop_goal_evidence_2026-05-01.md
```

Update existing docs, release manifest files, generated allowlists, and state files as needed so these outputs are discoverable and public-safe.

## Workstream 1 - Baseline Intake

Start by establishing the current state.

Required actions:

- Inspect `git status --short` and identify unrelated dirty work.
- Read active roadmap/release docs before editing:
  - `roadmap/ROADMAP-INDEX.md`
  - `roadmap/status-current.md`
  - `roadmap/electron-workbench-migration.md`
  - `roadmap/repo-structure-and-archive-map.md`
  - `release/readiness/release_readiness_checklist.md`
  - `release/readiness/curated_release_manifest.json`
- Inspect existing UI, renderer smoke, and Lore markdown rendering paths.
- Update repo state files early once the implementation plan is concrete.

Do not start broad refactors until you know which files currently own the relevant behavior.

## Workstream 2 - Lore Markdown Links

Fix the current markdown link behavior without rewriting authored markdown.

Acceptance criteria:

- Internal markdown document links select the matching Lore document inside the Lore reader.
- Heading links scroll within the current article.
- External links open externally or through the app's existing safe external-link boundary.
- Unknown links do not navigate Home or dump the user to a default route.
- Unsafe or unsupported links fail closed with clear user-facing behavior.
- Renderer smoke proves the internal-document, heading, external-link, and unknown-link cases.
- Tests prove authored markdown body fidelity is preserved.

Implementation guidance:

- Prefer a small resolver for content-document paths/slugs/headings over ad hoc URL string handling in JSX.
- Keep browser preview-mode and native content behavior aligned.
- Use existing typed preload/Electron boundaries for external opening if available; add a narrow typed boundary only if one does not exist.

## Workstream 3 - UI Action Inventory And Fixes

Create a comprehensive action inventory:

```text
roadmap/interaction-audit/2026-05-01-ui-action-inventory.md
```

The inventory must cover at least:

- Home
- Save Lab
- Media
- Lore
- Patch Bench
- RE Lab
- Game Harness
- Release
- App shell navigation and command/search surfaces

For each major button/control/action, record:

- label or visible affordance
- owning screen/component
- intended behavior
- current status: works, disabled-by-design, planned, broken, or unclear
- proof method: renderer smoke, Browser Use, native job smoke, code inspection, or intentionally untested
- follow-up or fix applied

Fix all broken or misleading major interactions found during the inventory.

Acceptance criteria:

- Every major action either works, is intentionally disabled with a clear explanation, or is explicitly marked planned with honest copy.
- Disabled-state explanations are visible where users need them.
- Tooltips/help text are added where they reduce confusion.
- No major button silently does nothing.
- No unsafe mutation path bypasses typed job policy, arm phrases, copied-profile/copy-target restrictions, or artifact-root containment.
- Renderer smoke covers the important interaction outcomes, not just static rendering.

## Workstream 4 - Agentic RE Objective Model

Build a persistent RE objective model that future Ralph-loop goals can reuse.

Required output:

```text
roadmap/reverse-engineering/coverage-map.md
```

The coverage map must track, at minimum:

- save/options format coverage
- executable patch coverage
- Ghidra/function naming coverage
- runtime debugger/probe coverage
- game harness/capture/input coverage
- asset/archive coverage
- media playback/transcode coverage
- Lore/content coverage
- release/public-safety coverage
- unknowns and next high-value objectives

Include objective templates for future investigations:

- texture investigation
- model/mesh investigation
- function/decompile investigation
- runtime behavior/probe investigation
- save/options behavior investigation
- UI/workbench interaction investigation

Each template should define:

- objective statement
- required context to read
- allowed tools/jobs
- safety boundaries
- evidence packet shape
- acceptance criteria
- stop conditions

Acceptance criteria:

- Coverage status is honest about fixture proof versus real runtime proof.
- The map is useful for choosing the next domain-by-domain Ralph-loop goal.
- The map does not claim "100% RE" or completed runtime semantics unless evidence exists.

## Workstream 5 - WASM/WebGPU/Netcode Feasibility Dossier

Create:

```text
roadmap/web-runtime/webgpu-wasm-netcode-feasibility.md
```

The dossier must make the strategic call explicit:

- WASM/WebGPU/netcode are future runtime/rebuild concerns, not the replacement for the current Electron typed backend.
- WebAssembly is plausible later for clean-room loaders, parsers, asset viewers, simulation cores, and possibly rebuilt gameplay/runtime pieces.
- WebGPU remains a future renderer target with browser support and secure-context constraints.
- Browser ports involve real work around filesystems, multimedia, audio, networking, pthreads, SIMD, debugging, and runtime environment differences.

Use current sources where practical, including:

- MDN WebAssembly documentation: <https://developer.mozilla.org/docs/WebAssembly>
- MDN WebGPU API documentation: <https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API>
- Emscripten porting documentation: <https://emscripten.org/docs/porting/index.html>

Acceptance criteria:

- The document compares near-term Electron workbench needs against future browser/runtime possibilities.
- It names prerequisites before any web runtime prototype should start.
- It includes a staged roadmap from portable parsers/loaders to clean-room renderer/runtime prototypes.
- It does not instruct the current goal agent to implement a WebGPU renderer, WASM runtime, or netcode.

## Workstream 6 - Release Lane Strategy

Create:

```text
release/readiness/release_lane_strategy_2026-05-01.md
```

Compare:

```text
Option A - keep curated release lane
Option B - repo-as-release minus .gitignore
```

The likely conclusion should be to keep the curated release lane for now while simplifying names/docs so it feels less mysterious.

The strategy must discuss:

- why `.gitignore` does not protect already tracked files
- current deny families such as `game/**`, `media/**`, `save-attempts/**`, `subagents/**`, private runtime evidence, binary/save suffixes, state files, and operator directives
- what would have to be true before a repo-as-release approach became safe
- how the curated manifest, public allowlist, private inventory, and bundle policy fit together
- which docs should be renamed, simplified, or made more obvious

Acceptance criteria:

- The strategy is public-safe.
- The required new evidence/strategy docs are included in release policy/manifest handling.
- Release checks are run and any generated release artifacts are refreshed when needed.

## Workstream 7 - Evidence Packet

Create the final public-safe evidence packet:

```text
release/readiness/ralph_loop_goal_evidence_2026-05-01.md
```

It must include:

- goal file path and invocation summary
- start commit and final commit
- branch name and remote status
- summary of changes by workstream
- required output file checklist
- tests/checks run, with pass/fail results
- Browser Use or renderer-smoke evidence for key UI flows
- Lore link proof summary
- release policy proof summary
- private/sensitive artifact handling statement
- known remaining gaps
- explicit statement that no original Steam/Program Files executable was patched
- explicit statement that no `.bes` save was synthesized from scratch
- final git status
- commit and push evidence, if the operator authorized commit/push for this goal

Do not include raw private screenshots, raw game assets, private local paths beyond sanitized summaries, base64 images, copied executable bytes, save contents, or secrets.

## Required Checks

Run the smallest sufficient set while developing, then run the full relevant closeout gate before final evidence.

Expected closeout commands:

```powershell
npm run typecheck
npm run archive:electron:build:main
npm run archive:electron:test:parity
npm run test:cli-smoke
npm run build
npm run archive:electron:test:renderer-smoke
npm run archive:electron:test:bundle-policy
npm run archive:electron:test:bundle-smoke
python tools/docsync_check.py
python tools/release_profile_snapshot.py --check
python tools/release_curated_manifest.py --check
dotnet build OnslaughtCareerEditor.Release.slnx --nologo
dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
```

If a check is not relevant or is blocked by local prerequisites, record the reason in the evidence packet and do not hide the gap.

## Completion Criteria

The goal is complete only when all of these are true:

- All required output files exist.
- Lore markdown link behavior is fixed and tested.
- Every major app action is inventoried, and broken/misleading actions are fixed or honestly disabled/planned.
- RE coverage map and objective templates exist and are usable for future loop goals.
- WASM/WebGPU/netcode feasibility is documented as future work with clear prerequisites.
- Release lane strategy is documented and release policy files are updated as needed.
- Renderer smoke and relevant gates pass.
- State files are updated with factual, compact notes.
- The final evidence packet exists and is public-safe.
- The working tree is clean after commit/push, if the operator's goal invocation authorized commit/push.

If local agent policy requires explicit approval before commit or push and that approval has not been granted, stop at the approval checkpoint with all evidence prepared and a clear list of remaining commit/push steps.

## Do Not Claim Complete If

- Any required output file is missing.
- Lore internal links still navigate Home/default route.
- A major button silently does nothing.
- UI copy implies real runtime proof where only browser preview-mode proof exists.
- Release evidence docs are created but not covered by release manifest/policy handling.
- Private/runtime evidence leaks into public-safe docs.
- Tests are skipped without a recorded reason.
- The branch has uncommitted goal changes after the commit/push checkpoint.
