# Onslaught Career Editor — GPT Director + Codex Execution Directive

> Status: superseded historical directive
> Last reviewed: 2026-05-07
> Current authority: `AGENTS.md`, `roadmap/three-lane-product-strategy.md`, active `/goal` text, and current repo evidence.
>
> Do not execute the historical Electron-first work orders below as an active plan. This file is retained as private operator provenance for how the Electron detour was directed and reviewed. The current product truth is WinUI 3 first: Electron, WPF, and the old Python GUI/CLI parity app are archived/reference surfaces unless a later explicit strategy decision reactivates them.

Use this as the operating system for the next work session. Do not paste the angry prompt into Codex. It is emotionally accurate but operationally bad: it asks for every outcome at once, gives no evidence format, and makes it easy for Codex to produce a huge unreviewable diff.

The goal is to use GPT Pro / local GPT 5.5 xhigh as the technical director and reviewer, while Codex executes one bounded slice at a time.

---

## MASTER PROMPT FOR GPT PRO / LOCAL GPT 5.5 XHIGH

You are the technical director, release reviewer, and prompt writer for `dlprentice/Onslaught-Career-Editor-private`.

You are not the code executor. Codex is the code executor. Your job is to:
1. Convert broad product goals into small, ordered Codex tasks.
2. Prevent giant unreviewable diffs.
3. Evaluate Codex outputs against hard evidence.
4. Reject incomplete work even when it sounds confident.
5. Produce the next Codex prompt only after the previous slice is proven.

Repository context:
- Active branch: `main`.
- Current product direction: WinUI 3 + Windows App SDK over AppCore.
- Electron/React/TypeScript, WPF, and the old Python GUI/CLI parity app are archived/reference surfaces, not active product lanes.
- Active Python work is RE/tooling/lab support under `tools/`, not a shipping GUI/product lane.
- Current command-line support is the C# CLI plus focused tools unless a later explicit prompt reactivates archived TypeScript CLI work.
- Root scripts include WinUI primary-lane validation, AppCore tests, C# CLI smoke, release/profile safety checks, markdown/link checks, and archived Electron checks only when archive health is explicitly in scope.
- `CURRENT_CAPABILITIES.md`, `roadmap/status-current.md`, `roadmap/three-lane-product-strategy.md`, and `roadmap/repo-structure-and-archive-map.md` are the active strategy/docs anchors.
- `release/readiness/curated_release_manifest.json` must include every public-safe first-class release evidence surface and must keep private/runtime/operator material excluded.
- Media, asset, save/options, and patch workflows should advance through the WinUI product lane and AppCore/tooling support while preserving copied-target and read-only-source safety gates.
- Game Harness/Electron typed job-runner evidence remains archived/reference unless explicitly reactivated; do not use it to define the current community product UX.
- The active product quality problem is WinUI completeness, stability, accessibility, visual polish, release packaging, and real RE-backed coverage without reviving archived app lanes.

Non-negotiable operating rules for Codex:
- Always start with `git status --short --branch`.
- Read repo instructions before modifying anything.
- Never claim a feature is done without a command log, screenshot, artifact path, or runtime proof.
- Never modify game installation files directly.
- Any executable/save/options mutation must happen only in copied artifact-root targets.
- Do not change IPC contract names, job IDs, schema IDs, or artifact schema names unless the task explicitly requires it.
- Do not “modernize” unrelated files.
- Use `git mv` for archiving/moves.
- Do not delete RE evidence, release evidence, manifests, or state files unless the task explicitly asks and the reason is documented.
- Do not update docs to say “done” before proof exists.
- If a runtime proof cannot be run because BEA.exe/VLC/game root/display permissions are unavailable, report the exact missing precondition and stop. Do not fake the proof.
- Every Codex response must end with this evidence packet:

```
BRANCH
- ...

FILES CHANGED
- ...

COMMANDS RUN
- command
  result: pass/fail
  important output:

PROOFS / ARTIFACTS
- screenshots:
- generated files:
- job run ids:
- cache paths:
- frame captures:

WHAT IS NOW PROVEN
- ...

WHAT IS NOT YET PROVEN
- ...

RISKS / FOLLOW-UP
- ...
```

Reviewer policy:
- Green only if the task’s acceptance checks pass.
- Yellow if implementation looks plausible but evidence is incomplete.
- Red if tests were skipped, docs were updated without proof, unrelated files changed, or claims exceed evidence.

Your output after reviewing Codex must be:
1. Verdict: GREEN / YELLOW / RED.
2. Evidence accepted.
3. Evidence rejected.
4. Required fix prompt, or next slice prompt.

---

## WORK ORDER

Historical note: this ordered work plan reflects the superseded Electron-first phase. Do not run it as the active plan. Current active work should follow the WinUI-first goal/state files and current repo evidence.

Do not start with visual redesign. Start by making the repo truthful and release-safe, because stale docs and release manifests are already wrong.

Order:
1. Docs + release manifest alignment.
2. UI/UX shell and language refactor.
3. CLI first-class completion and release inclusion.
4. Texture/media viewing proof.
5. Desktop in-app video proof.
6. Game Harness runtime proof.
7. Agentic RE loop proof.
8. Repo cleanup / old app archiving.
9. Release-candidate proof bundle.

---

# CODEX PROMPT 1 — Docs + Release Manifest Truth Pass

You are working in `dlprentice/Onslaught-Career-Editor-private` on branch `main`.

Objective:
Make the repo documentation and release manifest match the current implementation. This is a truth/alignment pass, not a feature pass.

Start:
1. Run `git status --short --branch`.
2. Read repo rules/instructions.
3. Inspect:
   - `package.json`
   - `packages/cli/package.json`
   - `packages/cli/scripts/cli-smoke.cjs`
   - `CURRENT_CAPABILITIES.md`
   - `roadmap/status-current.md`
   - `roadmap/electron-workbench-migration.md`
   - `release/readiness/curated_release_manifest.json`
   - any release/readiness docs that list test commands or active surfaces.

Required edits:
1. Add `packages/cli/**` to `release/readiness/curated_release_manifest.json` as a first-class active TypeScript surface.
2. Update current capability/status docs so `packages/cli` is listed as active, not implied absent.
3. Add `npm run test:cli-smoke` anywhere the active verification commands are listed.
4. Correct stale video wording:
   - Do not describe inline MP4 cache as future-only if implementation already has `prepareVideoPlayback`.
   - State the truth: cataloged `.vid` rows can be prepared into an app-owned MP4 cache using VLC as transcode infrastructure, then rendered by the in-app video panel where the returned payload/cache supports it.
   - Keep external VLC launch described only as a separate/fallback/legacy-supported path if still present.
5. Correct stale Game Harness wording:
   - State that typed launch/capture/input/stop building blocks exist.
   - State that full runtime proof still requires a real local copied-profile/game run unless already executed in this slice.
   - Do not claim continuous streaming if it is not implemented.
6. Do not touch app code unless you discover the docs are blocked by an obviously broken manifest parser.
7. Do not rewrite the docs stylistically. Make precise corrections.

Commands to run:
- `npm run test:cli-smoke`
- `npm run test:bundle-policy`
- Run any focused release manifest/check command if present.

Acceptance:
- Manifest includes `packages/cli/**`.
- Docs no longer omit the active CLI.
- Docs no longer falsely claim inline MP4 cache is future-only.
- Docs do not overclaim Game Harness runtime proof.
- Test output is included in the evidence packet.
- Git diff is small and explainable.

End with the standard evidence packet.

---

# CODEX PROMPT 2 — UI/UX Shell + Language Refactor

Objective:
Improve the app’s default UI/UX without breaking functionality. This is not a redesign from scratch. It is a shell, structure, and language cleanup that makes the community-facing product stop exposing internal implementation language by default.

Start:
1. Run `git status --short --branch`.
2. Confirm Prompt 1 changes are either committed or intentionally present.
3. Inspect:
   - `packages/ui/src/App.tsx`
   - adjacent UI files/components
   - styles/Tailwind setup
   - renderer smoke script
   - contracts used by the renderer.

Constraints:
- Do not change IPC job IDs, IPC method names, schema versions, preload contracts, job-run payload shapes, or artifact shape.
- Do not remove diagnostics; hide or collapse them behind a diagnostics affordance.
- Preserve all existing workflows.
- Avoid a broad visual rewrite.
- Prefer extraction and naming cleanup.

Required edits:
1. Extract shell/navigation metadata out of `App.tsx`.
   Suggested files:
   - `packages/ui/src/workbenchNav.ts`
   - `packages/ui/src/components/WorkbenchShell.tsx`
   - `packages/ui/src/components/SectionHeader.tsx`
   - `packages/ui/src/components/DiagnosticsPanel.tsx` or equivalent.
2. Reduce `App.tsx` responsibility:
   - Keep app state/orchestration there only where necessary.
   - Move static nav/section labels and repeated header/chrome markup out.
3. Replace default user-facing internal labels with product-friendly labels, while keeping exact technical data visible in diagnostics/details.
   Suggested mappings:
   - `IPC connected` -> `Desktop connection ready`
   - `browser-mock` -> `Browser preview mode`
   - `desktop-dev` -> `Desktop development mode`
   - `fixture` -> `sample data` or show only in diagnostics
   - `artifact` -> `evidence file`
   - `schemaVersion` -> `evidence type`
   - `job-run.v1` -> `job history record`
   - `allowlisted job catalog` -> `available safe tools`
   - `mutation-gated` -> `requires explicit confirmation`
   - `Agentic loop readiness` -> `automation readiness`
   - `typed desktop-app job boundary` -> hide under diagnostics or reword as `safe desktop job runner`.
4. Add real visible labels for path/address inputs that currently rely mainly on placeholders.
5. Improve empty states:
   - Tell the user what to do next.
   - Avoid implementation jargon in primary copy.
6. Keep technical values accessible in a collapsed “Diagnostics” / “Details” area.
7. Add or update renderer smoke assertions only if needed to keep the smoke meaningful after label changes.

Commands:
- `npm run typecheck`
- `npm run test:renderer-smoke`
- `npm run build`

Acceptance:
- App still builds.
- Renderer smoke passes.
- Default UI language is less internal.
- Diagnostics still expose technical details when needed.
- `App.tsx` is smaller or at least less structurally overloaded.
- No IPC/job/contract breakage.

End with the standard evidence packet, including before/after screenshots if the local environment can launch the renderer.

---

# CODEX PROMPT 3 — CLI First-Class Completion

Objective:
Make the TypeScript CLI a first-class active surface for the current workbench engine. Do not invent an unrelated CLI. Complete the current CLI as a job-runner gateway.

Start:
1. Run `git status --short --branch`.
2. Inspect:
   - `packages/cli/src/index.ts`
   - `packages/cli/package.json`
   - `packages/cli/scripts/cli-smoke.cjs`
   - root `package.json`
   - docs that mention commands/tests/release scope.

Required audit:
- Commands currently expected:
  - `catalog`
  - `run`
  - `list`
- Expected behavior:
  - stdout is parseable JSON.
  - progress is stderr NDJSON when `--progress` is used.
  - `run` accepts `WorkbenchJobRunRequest` JSON from `--input` or stdin.
  - repo root defaults to current working directory.
  - artifact root defaults to `$env:ONSLAUGHT_ARTIFACT_ROOT` or `~/.onslaught-workbench`.
  - persisted history can be listed.

Required edits:
1. Ensure help/usage output is clear and useful.
2. Ensure error output does not corrupt stdout JSON for successful commands.
3. Add focused smoke coverage if gaps exist:
   - catalog includes `release.inspectPolicy`
   - run via stdin
   - run via `--input` if supported
   - `--progress` emits parseable stderr NDJSON
   - list sees persisted run
   - invalid command/error path exits non-zero without pretending success.
4. Ensure docs call the CLI active and include examples.
5. Ensure release manifest includes `packages/cli/**` if not already done.
6. Do not expand the CLI beyond the current job runner unless a missing command is clearly required by docs.

Commands:
- `npm run build:cli`
- `npm run test:cli-smoke`
- `npm run typecheck`

Acceptance:
- CLI is documented as an active TypeScript surface.
- CLI behavior is proven by smoke tests.
- stdout/stderr behavior is preserved.
- No unrelated app changes.

End with the standard evidence packet.

---

# CODEX PROMPT 4 — Texture / Media Viewing Proof

Objective:
Prove that textures can be viewed in the app. This is a proof task. Do not merely point at code.

Start:
1. Run `git status --short --branch`.
2. Inspect media code paths:
   - renderer Media section
   - Electron IPC media handlers
   - `apps/electron/src/media-catalog.ts`
   - renderer smoke tests.
3. Determine whether a real selected game folder and exported PNG texture catalog are available locally.

Required proof:
1. Launch the renderer/Electron environment.
2. Select or use the configured game/app root that contains media catalog data.
3. In Media:
   - filter to textures
   - query a known texture such as `LTLogo` if available, otherwise the first cataloged texture with a `previewId`.
   - open the preview.
4. Capture evidence:
   - screenshot of the texture preview in-app
   - label/id of texture row
   - preview payload type
   - image dimensions if available
   - source/export path, constrained to app workspace.
5. If no real preview data exists locally, do not claim success. Instead:
   - add or run a deterministic renderer/media smoke using a safe packaged fixture if already supported;
   - or report the exact missing precondition and the smallest required fixture addition.
6. Do not loosen path containment or file type checks.

Commands:
- `npm run typecheck`
- `npm run test:renderer-smoke`
- Any focused media preview smoke/test available.

Acceptance:
- Evidence shows an actual texture preview rendered in-app, or a clear failing precondition is reported.
- No unsafe file path broadening.
- No fake screenshots or generated placeholders claimed as game textures unless explicitly marked as fixtures.

End with the standard evidence packet.

---

# CODEX PROMPT 5 — Desktop In-App Video Proof

Objective:
Prove cataloged Bink `.vid` playback preparation and in-app video rendering path.

Start:
1. Run `git status --short --branch`.
2. Inspect:
   - `prepareVideoPlayback`
   - Electron IPC handler for `media:prepareVideoPlayback`
   - renderer video panel
   - VLC path resolution
   - selected game root handling.

Required proof:
1. Ensure VLC is available or set `ONSLAUGHT_VLC_PATH`.
2. Select a real game root with `data/video`.
3. Pick a cataloged `.vid` row, preferably `LTLogo` or another short/root/menu clip if available.
4. Run the in-app prepare flow, not just external VLC open.
5. Verify:
   - `video-playback.v1` payload
   - mode is `inline-transcoded`
   - cache status is `hit` or `created`
   - cache path exists under app/user artifact storage
   - MIME type is `video/mp4`
   - renderer shows the `<video>` panel.
6. Capture screenshot and artifact/cache path.
7. Do not claim proof if VLC/game root/video file is missing; report exact missing precondition.

Commands:
- `npm run typecheck`
- `npm run test:renderer-smoke`
- any focused media smoke if present.

Acceptance:
- In-app MP4 cache path is real and app-owned.
- Renderer shows the video panel.
- External VLC launch alone does not count.

End with the standard evidence packet.

---

# CODEX PROMPT 6 — Game Harness Runtime Proof

Objective:
Prove the real Game Harness loop can operate safely inside the app using copied profile/executable artifacts only.

Start:
1. Run `git status --short --branch`.
2. Inspect job definitions and UI for:
   - `game.prepareSafeProfile`
   - `patch.applyCatalogPatch`
   - `game.launchProfile`
   - `game.planWindowCapture`
   - `game.captureWindowFrame`
   - `game.planWindowInput`
   - `game.sendWindowInput`
   - `runtime.stopManagedProcess`.

Safety rules:
- Never patch retail `BEA.exe`.
- Never mutate installed game files.
- Never use a real user save/profile as the mutation target.
- Use copied profile/executable under the artifact root.
- Apply only catalog patch `force_windowed` unless another explicit safe patch is already documented.
- Stop the managed process at the end.

Required proof sequence:
1. Prepare safe copied profile.
2. Apply `force_windowed` to copied executable.
3. Launch copied profile/executable through the app/job runner.
4. Plan capture.
5. Capture one frame.
6. Plan one bounded/scoped input action.
7. Send the input.
8. Capture a second frame.
9. Stop managed process.
10. Verify process registry/log-tail/stop state.

Evidence:
- job run IDs
- copied profile path
- copied executable path
- patch verification result
- process ID
- frame capture paths
- frame dimensions/timestamps
- input plan payload
- stopped process confirmation
- screenshots where possible.

Acceptance:
- Two captured frames exist.
- Input was sent only to the scoped/planned target.
- Managed process stopped.
- All mutated targets are artifact-root copies.
- Missing local game/display preconditions are reported instead of papered over.

End with the standard evidence packet.

---

# CODEX PROMPT 7 — Agentic RE Loop Proof

Objective:
Prove an agentic reverse-engineering loop exists that can observe app/game state, choose a bounded action, execute it, collect evidence, and stop cleanly.

Definition of “agentic RE loop” for this repo:
- Observe: capture game/app frame or state artifact.
- Decide: produce a bounded next action from a documented plan.
- Act: send scoped input or run a safe read-only/allowed job.
- Observe again: capture new frame/artifact.
- Record: persist a loop evidence artifact.
- Stop: clean up managed process/resources.

Start:
1. Run `git status --short --branch`.
2. Inspect Game Harness and RE Lab UI/job flows.
3. Decide whether this can be proven with existing jobs or needs a tiny orchestration wrapper/UI affordance.

Required implementation/proof:
1. Prefer no new job IDs if existing jobs can prove the loop.
2. If a wrapper is needed, keep it small and typed.
3. Add a visible “Automation proof” / “RE loop proof” panel only if it improves usability.
4. The proof artifact must include:
   - initial observation
   - planned action
   - action execution result
   - second observation
   - cleanup result
   - all job run IDs / artifact paths.
5. Do not implement open-ended autonomous control.
6. Keep every action bounded and reviewable.

Commands:
- `npm run typecheck`
- `npm run test:renderer-smoke`
- focused job/CLI smoke if added.

Acceptance:
- A real loop evidence artifact exists, or exact missing runtime preconditions are reported.
- No open-ended uncontrolled input loop.
- User can understand what happened without reading raw schema fields.

End with the standard evidence packet.

---

# CODEX PROMPT 8 — Repo Cleanup + Old App Archiving

Objective:
Clean up repo structure without destroying useful parity/reference material.

Start:
1. Run `git status --short --branch`.
2. Inventory active vs parity vs archived surfaces:
   - active: `apps/electron`, `packages/ui`, `packages/contracts`, `packages/cli`
   - parity/reference: AppCore, AppCore.Host, AppCore.Tests, old C# CLI if still used
   - archive/non-expanding: WinUI, WPF, Python, legacy top-level app files.
3. Inspect release manifest and docs before moving anything.

Rules:
- Use `git mv`.
- Do not delete evidence.
- Do not move files that build/test scripts still require unless scripts are updated and proven.
- Do not break release manifest policy.
- Do not collapse unrelated docs just because names look similar.
- Create an explicit archive map before moving.

Required output/edit:
1. Add/update a repo structure doc that names:
   - shipping surfaces
   - parity surfaces
   - archived surfaces
   - private/non-release surfaces.
2. Move only clearly historical files/directories into `archive/` if safe.
3. Update references/manifests/tests accordingly.
4. If a move is risky, leave it and document why.

Commands:
- `npm run typecheck`
- `npm run test:cli-smoke`
- `npm run test:renderer-smoke`
- `npm run test:bundle-policy`
- `dotnet build ".\OnslaughtCareerEditor.Release.slnx" --nologo` if C# surfaces are touched.
- relevant dotnet tests if C# project references changed.

Acceptance:
- Repo structure is clearer.
- Active release surfaces are explicit.
- Historical app files are archived or intentionally documented.
- Builds/tests still pass.
- No evidence loss.

End with the standard evidence packet.

---

# CODEX PROMPT 9 — Release Candidate Proof

Objective:
Produce a release-candidate proof packet for the current Electron-first state.

Start:
1. Run `git status --short --branch`.
2. Confirm all previous slices are green or documented as blocked by local runtime preconditions.
3. Inspect release docs/manifests.

Commands:
- `npm run build`
- `npm run typecheck`
- `npm run test:cli-smoke`
- `npm run test:renderer-smoke`
- `npm run test:electron-parity`
- `npm run test:bundle-policy`
- `npm run test:bundle-smoke`
- `dotnet build ".\OnslaughtCareerEditor.Release.slnx" --nologo`
- `dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo`
- `dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo`

Required proof doc:
Create or update a release readiness evidence file under `release/readiness/` with:
- date/time
- branch/commit
- changed files
- command results
- runtime proofs completed
- runtime proofs blocked and why
- screenshots/artifacts/cache/frame paths
- remaining blockers
- exact next command for the user, if any.

Acceptance:
- Every automated check is run or the reason it cannot run is documented.
- Release manifest includes active surfaces.
- Runtime proof claims are tied to artifacts.
- No “done” claims without proof.

End with the standard evidence packet.

---

## REVIEWER PROMPT TO USE AFTER EVERY CODEX RUN

Paste Codex output and diff summary into GPT Pro/local GPT 5.5 xhigh with this:

```
Review this Codex run as release director for Onslaught Career Editor.

Task prompt:
[paste task]

Codex evidence packet:
[paste packet]

Diff summary:
[paste git diff --stat and relevant diff excerpts]

Judge:
- Did it follow scope?
- Did it change unrelated files?
- Are claims backed by command output/artifacts/screenshots?
- Did docs overclaim?
- Did tests actually run?
- Are there unsafe file/game mutations?
- Should this be GREEN, YELLOW, or RED?

Output:
1. Verdict: GREEN/YELLOW/RED
2. Accepted evidence
3. Rejected/insufficient evidence
4. Required fix prompt if not green
5. Next Codex prompt if green
```

---

## FIRST THING TO RUN RIGHT NOW

Use Codex Prompt 1 first.

Reason:
The implementation has already moved ahead of the docs. Fixing docs/release truth first prevents later work from being evaluated against stale status files and prevents the active CLI from being omitted from release accounting.
