# Player Mods And Lab Curation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development for each behavior change and superpowers:verification-before-completion before claiming the slice complete.

**Goal:** Replace the flat patch/profile selection surface with a concise normal player path and a structured, collapsed Lab while preserving all recipe IDs, patch bytes, and copied-target safety behavior.

**Architecture:** Recompose the existing `BinaryPatchesPage.xaml` controls without adding a second state model. Existing buttons, event handlers, profile matching, dynamic patch models, and automation IDs remain authoritative. A new static contract test protects the cross-cutting information hierarchy and exact copy boundaries; existing interaction smoke is extended only for native collapsed/expanded behavior.

**Tech Stack:** C#/.NET 10, WinUI 3 XAML, NUnit/FlaUI UI tests, xUnit AppCore tests, JSON catalog.

**Global constraints:** No patch-byte changes, installed-game mutation, live runtime/Ghidra work, canonical goal/state edits, observer-doc repair, release, merge, or primary-lane overlap.

---

### Task 1: Pin the player/Lab surface contract

**Files:**
- Create: `OnslaughtCareerEditor.UiTests/PatchBenchPlayerLabCurationTests.cs`
- Test: `OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj`

1. Add focused static tests that require: one collapsed `PatchBenchLabExpander`; exact compatibility-base copy; dedicated marker and Goodies buttons before Lab; three named Lab groups; retained legacy automation IDs inside Lab; truthful Goodies nonclaims; and unchanged catalog IDs/keys.
2. Run only `PatchBenchPlayerLabCurationTests` and confirm it fails because the Lab boundary is absent.

### Task 2: Recompose the WinUI selection surface

**Files:**
- Modify: `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml`
- Modify: `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`

1. Replace the broad “Choose game changes” introduction/profile card with a normal compatibility/recovery card and the two existing optional-mod quick actions.
2. Add a collapsed Lab expander containing separate legacy recipes, visual/executable experiments, and a signpost to the already separated launch/control diagnostics.
3. Move existing controls without changing their automation IDs or handlers.
4. Update superseded presentation assertions in the broad product-lane test while retaining behavior/safety assertions.
5. Run the focused static tests and the PatchBench product-lane test to green.

### Task 3: Prove catalog compatibility and native behavior

**Files:**
- Modify: `OnslaughtCareerEditor.UiTests/WinUiPatchBenchInteractionSmokeTests.cs` only if the existing smoke cannot establish the new boundary without it.
- Evidence only: ignored/generated screenshot output outside tracked source.

1. Add a native assertion that Lab begins collapsed, normal marker/Goodies actions are reachable, expanding Lab exposes retained Enhanced and Debug recipes, and selecting a retained recipe still updates state.
2. Build WinUI once, then run the focused native interaction smoke.
3. Capture normal and expanded-Lab screenshots and inspect them for hierarchy, clipping, wrapping, and compact-window reachability.
4. Run AppCore/profile and patch-safety gates because profile semantics and bytes must remain unchanged.

### Task 4: Review and handoff

**Files:**
- Update: `subagents/player-value-ux-mods-patch-audit-2026-07-13.md` only if the implemented disposition changes the audit’s current recommendation.

1. Obtain independent Codex normal and adversarial review of the exact diff and verification evidence.
2. Resolve blocking findings, rerun affected gates, and run `git diff --check` plus `git status --short`.
3. Record the known observer docsync failure as integration-owned and do not modify it.
4. Commit and push the bounded green slice to `codex/player-value-ux-patch-quality`.
5. Send the primary task the commit, changed paths, exact validation, skipped gates, nonclaims, and integration note.
