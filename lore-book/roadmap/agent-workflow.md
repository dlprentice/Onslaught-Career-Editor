# Agent workflow

Status: active
Last updated: 2026-05-26

AI/agent session patterns for the three-lane Onslaught Toolkit and Battle Engine Aquila reverse-engineering work.

Long-running operating lessons live in [agent-lessons-learned.md](/roadmap/agent-lessons-learned.md). Read that file after this workflow note when doing WinUI product work, native UIA/visual proof, release work, or RE work.

## Active stack rule

The active product focus is WinUI 3, with archived app detours and active script/tooling support:

- `OnslaughtCareerEditor.WinUI` owns the primary user-facing Windows product lane.
- `OnslaughtCareerEditor.AppCore` owns shared correctness/core support for the Windows lane.
- `archive/electron-workbench/` preserves the former Electron/React/TypeScript workbench and TypeScript CLI as reference material.
- `OnslaughtCareerEditor.AppCore.Host` and `OnslaughtCareerEditor.Cli` remain support/parity surfaces while useful.
- Active Python scripts are RE/tooling/lab support; the old Python GUI/CLI parity app is archived/reference, not a shipping product lane.
- WPF is archived/reference only.

Do not keep adding product polish to Electron, WPF, or the old Python GUI/CLI app. Focus product UX on WinUI 3.

## Session structure

For WinUI product work:

```text
1. CONTEXT: Read AGENTS.md, CURRENT_CAPABILITIES.md, state files, and roadmap/three-lane-product-strategy.md.
2. GOAL: State the user-facing Windows product workflow being improved.
3. METHOD: Prefer AppCore-backed behavior, native Windows UX, and focused build/test validation.
4. DOCUMENT: Update state files and active roadmap/release docs in the same pass.
5. VERIFY: Run the relevant WinUI/AppCore build/tests; do not claim UI proof without a real Windows app check.
```

WinUI testing lessons from the long product/RE campaign:

- Maximize the native app before screenshot or interaction evidence unless the test is intentionally proving narrow-window behavior.
- Treat offscreen controls as normal on laptop-sized displays. Use automation IDs plus `ScrollIntoView`, explicit section navigation, or targeted control invocation instead of assuming everything is in the first viewport.
- Test startup/deep-link states separately from clicked-through states. The Asset Library Goodies route once showed a visible row with a stale zero-count status until the visual smoke asserted the initial screen text directly.
- Keep UIA assertions tied to user-facing claims: if a screen says extraction/model/Goodies coverage is real, prove the visible text and at least one representative interaction path.
- Rebuild `OnslaughtCareerEditor.WinUI` before filtered native UIA smoke after app-code changes. A filtered `dotnet test` can rebuild the test assembly while still launching an older WinUI executable.
- For cross-page handoffs, assert the destination's settled state. The source button and search text are not enough; the Goodie video handoff only became trustworthy after the Media page selected `Credits Video` and preserved `UsTheMovie.vid`.
- Do not clear a selected media/player panel on transient TreeView group/null selection events. Group focus and tree refreshes should not erase the user-visible active item.
- Inspect generated screenshots after meaningful UI work. UIA can prove accessible control state while still missing trust-breaking copy/layout issues visible to the user.
- Do not use browser-preview evidence for native WinUI behavior. The archived Electron browser path is reference material, not proof of the Windows app.
- In this Windows/Codex lane, `rg` has repeatedly been unreliable. Prefer `git ls-files` plus targeted Node/Python scans for repo text search unless a fresh local check proves `rg` is healthy.

For archived Electron workbench inspection:

```text
1. CONTEXT: Read AGENTS.md, CURRENT_CAPABILITIES.md, state files, `archive/electron-workbench/README.md`, and `roadmap/electron-workbench-migration.md`.
2. GOAL: State the archive question or narrow extraction target.
3. METHOD: Prefer read-only inspection or porting narrow logic into active WinUI/AppCore/tools paths.
4. DOCUMENT: Update active docs only when the archive posture or extracted behavior changes.
5. VERIFY: Run `archive:electron:*` commands only when archive health itself is in scope.
```

For RE sessions:

```text
1. CONTEXT: Read CURRENT_CAPABILITIES.md, reverse-engineering/RE-INDEX.md, and relevant source/reference docs.
2. GOAL: State the exact binary/save/runtime question.
3. METHOD: Use read-only evidence first; gate mutations behind explicit job/artifact boundaries.
4. DOCUMENT: Add findings to reverse-engineering/ and roadmap/status-current.md when they change operating truth.
5. VERIFY: Use real retail saves, BEA.exe, Ghidra exports, CDB logs, or game harness evidence before calling a claim proven.
```

For release work:

```text
1. CONTEXT: Read RELEASE_SCOPE_AND_TEST_COMMANDS.md and release/readiness/release_readiness_checklist.md.
2. GOAL: Decide whether the target is WinUI product health, Electron workbench validation, active Python script/tooling work, public safety/export, or legacy-reference validation.
3. METHOD: Keep `.codex/`, game/media/save-attempts/subagents/state files out of community outputs.
4. DOCUMENT: Update release docs and generated manifests together.
5. VERIFY: Run the lane-specific gates plus public safety/export checks.
```

For delegated subagent work:

```text
1. SCOPE: Delegate only independent, bounded work with a clear file or question boundary.
2. MODEL: Worker subagents must run with effective gpt-5.5 and xhigh reasoning unless a higher-priority instruction forbids it; do not downshift workers for speed or routine implementation.
3. COORDINATION: Workers are not alone in the codebase; they must not revert unrelated edits and must report changed paths.
4. STATE: The main agent owns developer_agent_state.json and documentation_agent_state.json.
5. EVIDENCE: Put temporary subagent outputs under subagents/ and summarize durable truth in canonical docs/state.
```

## Patterns that still matter

1. **Baseline-first saves**: always start with a valid game-generated save or options file.
2. **True dword view**: retail save data starts at `file + 2`; avoid legacy aligned-view offsets.
3. **Packed metadata preservation**: preserve kill counter high metadata bytes and unknown regions.
4. **Source-as-reference**: Stuart's source helps with names and logic, but retail bytes win when layouts differ.
5. **Artifact trails**: every job that reads, previews, copies, patches, launches, or probes should leave a typed artifact.
6. **Catalog is not runtime proof**: extracted texture/model/Goodies rows prove static catalog coverage. Runtime Goodies wall behavior, unlock criteria, animation, and in-game viewer behavior need separate copied-profile/runtime evidence.
7. **Search fallback**: use `git ls-files` plus targeted Node/Python scans when `rg` is unavailable or unreliable in the current Windows shell.

## Cross-referencing

- **Source to save**: when source names a field, calculate and verify the retail file offset.
- **Binary to source**: use decompile behavior, xrefs, constants, and source naming together before semantic promotion.
- **Patch to read-back**: mutation is not done until byte read-back and artifact evidence exist.
- **Docs to app**: when a lane gains or loses a workflow, update `CURRENT_CAPABILITIES.md`, `roadmap/three-lane-product-strategy.md` if strategy changes, and `roadmap/status-current.md`.

## Common pitfalls

1. Do not synthesize `.bes` files from scratch.
2. Do not patch original user/game files when a copied target workflow exists.
3. Do not let renderer code reach raw Node, shell, debugger, Ghidra, or filesystem APIs.
4. Do not treat the old Python GUI/CLI app or WPF as parity obligations.
5. Do not treat Electron as the product backlog target.
6. Do not ship `.codex/`, private `game/`, `media/`, `save-attempts/`, `subagents/`, or state files in community outputs.

See [CURRENT_CAPABILITIES.md](/CURRENT_CAPABILITIES.md), [electron-workbench-migration.md](/roadmap/electron-workbench-migration.md), and [RE-INDEX.md](/reverse-engineering/RE-INDEX.md).
