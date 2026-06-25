# WinUI UI/UX Redesign Radar

Status: active
Last updated: 2026-06-25

This document tracks UI/UX debt that is too broad for a release-candidate polish patch but important enough to keep visible. It is grounded in maintainer review and UI/UX critique; implementation and verification remain maintainer-owned.

## Release-Candidate Baseline

- Keep normal-player surfaces calm and plain: safe copy, game options, local split-screen, music swap, and patch rows should explain what the user can do now.
- Keep proof vocabulary one level deeper in Details, Advanced, Diagnostics, readiness notes, or maintainer docs.
- Do not imply online multiplayer, matchmaking, audible music replacement proof, or rebuild parity is complete.
- Keep the installed Steam game folder and original `BEA.exe` read-only. The UI should repeat this where a user is about to copy, patch, launch, or stop a game process.
- Current platform decision: keep WinUI 3 as the flagship and improve agent-driven inspection/visual QA before considering any rewrite. See `roadmap/winui-agentic-ui-hardening-plan.md`.

## Redesign Radar

1. **Windowed & Mods is doing too many jobs.**
   - Current page combines source selection, profile presets, patch/mod selection, safe-copy creation, play/stop, launch options, control tweaks, music swapping, online-readiness diagnostics, and BEA.exe-only byte-patch lab.
   - Future design should split the page into a clear 90% path: Find game -> Choose preset/mods -> Create safe copy -> Play. Mods, Music, Advanced Launch, Online Research, and BEA.exe-only Diagnostics should become separate tabs, steps, or pages.

2. **Advanced BEA.exe-only patching should not compete with the safe-copy path.**
   - The safe-copy workflow is the player product path.
   - BEA.exe-only copy/verify/apply/restore is a technical diagnostics lane and should eventually move behind an explicit Advanced/Maintainer surface.

3. **Online-readiness research should stay out of the normal player path.**
   - Default UI should say only that online play is not available yet and local split-screen is available in a safe copy.
   - Artifact loaders, readiness counters, source-bound runtime delivery language, and second-machine proof details belong in diagnostics.

4. **Game Options should become friendlier than raw configuration editing.**
   - `defaultoptions.bea` editing is useful, but raw key tokens, controller config numbers, and screen-shape values are power-user details.
   - Future work should provide friendly common controls first, then expose raw bindings under an Advanced section.

5. **Preset controls need clearer selected state.**
   - Initial fix landed for Windowed & Mods safe-copy profile and menu-background choice grids: selected buttons now have visible state, selected-status text, and UIA selected names.
   - Remaining broader redesign: a shared selected-chip/radio-style component should cover launch presets and other repeated choice grids without changing patch semantics.

6. **Save Lab has duplicate navigation.**
   - The quick-action cards and tab strip both navigate the same three flows.
   - Future design should make one of them primary, or make the quick-action cards drive the tabs with clearer selected state.

## Current Release-Slice Fixes

- Default copy now uses player-facing language for safe copies, game options, online unavailable status, music staging, and patch/mod limits.
- Windowed & Mods patch rows now expose stable patch-key-derived row, checkbox,
  and details AutomationIds for agent/UIA targeting; the normal debug-camera,
  online-unavailable, music-staging, and preset-detail copy no longer puts CDB,
  proof-boundary, key-census, raw-offset, or evidence jargon in the primary path.
- Windowed & Mods safe-copy profile and menu-background choice grids now show
  selected state visibly, update plain selected-status text, and expose selected
  UIA names for focused runtime smoke coverage.
- Windowed & Mods selected-choice state now uses a small WinUI model/helper for
  selected/normal UIA names and styling, while the page keeps patch-selection
  and safe-copy semantics unchanged.
- Windowed & Mods selected-profile status/details text now uses a small WinUI
  presentation model/helper, while the page keeps profile matching, selected
  patch keys, `ProfilePresetId`, safe-copy manifests, launch, music, and online
  logic unchanged.
- Windowed & Mods copied-profile launch status/modifier copy now uses small
  WinUI presentation models plus a helper, while the page keeps launch presets,
  launch argument construction, launch-plan validation, safe-copy launch,
  manifest handling, music, and online logic unchanged.
- Lore now distinguishes packaged offline chapters from GitHub source links in
  the visible UI and rendered Markdown. Full offline Lore is tracked as a
  generated content-pack plan instead of raw long-path ZIP extraction.
- Game Options patching is guarded by try/catch/finally and runs off the UI thread.
- File-picker/readiness-loader failures report user-visible status instead of relying on an app-level crash net.
- Major result/status surfaces use polite live-region hints for accessibility.
