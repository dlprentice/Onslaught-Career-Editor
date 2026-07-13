# Patch Bench Narrow Action Labels Design

**Status:** Approved by the primary task on 2026-07-13 under standing recommended-option authority

## Goal

Keep the normal Compatibility actions fully readable at the existing 760-pixel
native test width without changing what either action does.

## Observed Defect

The authoritative native visual check for the locked compatibility base showed
the labels **Reset to Compatibility Copy** and **Clear optional mods** truncated
inside their side-by-side buttons at 760 pixels. UI Automation could still find
and invoke the controls, but a first-time user could not read the complete
visible actions.

## Considered Approaches

1. Shorten the labels. This would fit but remove useful distinctions between
   restoring the named Compatibility profile and clearing only optional mods.
2. Stack both actions at every width. This is robust but consumes unnecessary
   vertical space at normal desktop widths.
3. Keep the compact two-column layout and use centered, wrapping label content
   with equal minimum button height. This preserves the exact wording and is the
   approved approach.

## Interaction And Layout Contract

- Preserve the exact visible labels **Reset to Compatibility Copy** and
  **Clear optional mods**.
- Preserve `PatchBenchWindowedPresetButton` and
  `PatchBenchClearSelectionButton`, their automation IDs, accessible names,
  click handlers, selection behavior, and placement in the normal
  Compatibility card.
- Replace truncation-prone plain string content with centered text content that
  wraps whole words within each existing column.
- Give both actions the same minimum height so one wrapped label does not make
  the pair look accidental or uneven.
- Keep the two-column desktop layout; do not add page-wide responsive states or
  change other Lab/preset action grids in this slice.

## Verification

- Write a focused source contract test first. It must fail against the current
  plain-string button content and then prove exact labels, whole-word wrapping,
  centered text, equal minimum height, stable IDs, and unchanged handlers.
- Rebuild WinUI before native verification.
- Run an authoritative hands-off native UIA/visual check at 760 pixels. UIA must
  find both existing buttons without invoking them, and the screenshot must show
  both complete labels without ellipsis, overlap, or clipping.
- Record an empty pre-run and post-run census for Toolkit, BEA, and test
  processes. The native check must not create a copied game or launch BEA.
- Run the focused WinUI tests and proportionate primary-lane verification. A
  substantive-scope review envelope is unnecessary unless implementation grows
  beyond this XAML-only presentation contract.

## Nonclaims And Scope

This slice does not change selection semantics, readiness, confirmation,
safe-copy behavior, AppCore, catalogs, profiles, patch bytes, receipts,
installed-game files, runtime or Ghidra evidence, Asset Library behavior,
canonical goal/state, distribution, or release state.
