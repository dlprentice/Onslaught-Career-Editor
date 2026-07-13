# Locked Compatibility Base And Readiness Design

**Status:** Approved by the primary task on 2026-07-13 (option A)

## Goal

Make the Windowed & Mods selection state tell the same truth as safe-copy
creation: every safe game copy contains the exact two-row compatibility base,
while optional rows remain independently selectable and invalid optional
combinations prevent confirmation or copying.

## Current Defect

AppCore already fails safely. `GameProfilePreflightService` adds
`resolution_gate` and `force_windowed` to every safe-copy patch request before
it creates the output folder, then validates the effective selection. The
WinUI selection surface does not model that invariant consistently:

- both required rows appear as ordinary check boxes and can be unchecked;
- some preset and clear paths temporarily omit the rows even though creation
  adds them back;
- both Create buttons enable from source/busy state without consulting patch
  selection validity; and
- selection validation can therefore occur only after the user accepts the
  creation confirmation.

No installed-game or copied-target safety boundary is bypassed, but the UI can
misrepresent the plan and ask the user to confirm an action that cannot start.

## Required Compatibility Contract

- `resolution_gate` and `force_windowed` are the only required compatibility
  rows in this slice.
- They remain visible in Lab with their existing row, check-box, and details
  automation IDs.
- Their check boxes remain checked and disabled. Adjacent copy and assistive
  help text state **Required and automatically included in every safe game
  copy** so the disabled state does not look broken.
- Their details expanders remain enabled and reachable for proof, limitations,
  offsets, dependencies, and research use.
- Initialization, every preset, quick action, manual-row change, and **Clear
  optional mods** reassert the exact pair. No UI path may leave either model
  row unselected.
- **Clear optional mods** produces base-only selection and is shown as the
  selected clear/reset action. It does not mean zero patches.

The normal Compatibility base card remains the primary player-facing surface.
Lab retains the two locked rows for technical transparency, stable automation,
and proof discovery.

## Selection And Profile Semantics

The shared visible selection contains the required pair plus zero or more
optional rows. Existing profile IDs and patch catalog rows remain unchanged.

- Compatibility Copy matches the exact required pair.
- Windowed + Graphics Defaults, Enhanced Profile Preview, and Debug Camera
  Preview continue to match their existing exact profile key sets.
- Graphics flag rows only is considered selected when the visible selection is
  the required pair plus exactly the two graphics rows.
- No optional rows is considered selected when the visible selection contains
  only the required pair.
- Player-mod status continues to report only the optional PATCHED marker and
  Goodies wall preview rows.

The advanced BEA.exe-only workflow shares this selection and therefore also
sees the required pair. This is intentional: the page no longer advertises a
state that safe-copy creation would silently expand.

## Continuous Readiness

A small pure WinUI helper owns user-facing safe-copy selection readiness. Its
inputs are source availability, busy/process state, the existing
`BinaryPatchPlanBuilder.ValidateVisibleSelection` result, and optional-row
count. It produces:

- whether Create is enabled; and
- one concise accessible status message.

When valid, the message states that the required compatibility base is ready
and reports the optional-row count. When invalid, it starts with **Review
optional mods:** and includes the existing bounded validation message. When no
source is available, it says selection is valid but a read-only BEA.exe source
is still required. Both the top and main Create buttons use the same readiness
result.

`PrepareCopiedProfileButton_Click` repeats the effective-selection validation
before building the confirmation text. An invalid selection updates the
readiness/operation status and returns without opening confirmation, creating
directories, copying files, or launching anything.

Known mutually exclusive UI groups continue to auto-clear peers. Continuous
validation remains defense in depth for programmatic state, catalog drift, or
future row groups rather than replacing those interactions.

## Architecture

### `BinaryPatchItemModel`

The model exposes key-derived presentation properties:

- `IsRequiredCompatibilityBase`;
- `CanChangeSelection`; and
- required-row accessible help/status copy.

No catalog contents or byte definitions move into the model.

### `BinaryPatchesPage`

The page retains one authoritative required-key set obtained from the existing
Compatibility profile. `SelectOnlyKeys` unions that set into every requested
selection. A small invariant method reselects either required row if future
code or binding state attempts to clear it. Optional-selection comparisons
exclude or explicitly add the required pair as appropriate.

`UpdateControlState` validates the current effective visible selection, feeds
the pure readiness helper, updates the live readiness text, and applies the
same enabled result to both Create buttons.

### `PatchBenchSafeCopySelectionReadiness`

The pure helper is UI text/state projection only. It does not load catalogs,
resolve dependencies, select rows, inspect paths, or perform filesystem work.

### AppCore

`GameProfilePreflightService`, `ApplyWindowedCompatibilityPatch: true`,
`BuildRequestedPatchKeys`, validation ordering, receipts, manifests, catalog
loading, patch specs, dependencies, original/final-byte verification, and
backup/restore behavior remain unchanged.

## Interaction And Accessibility

- Preserve the existing dynamic row, check-box, and details automation IDs.
- Bind required check-box enabled state to `CanChangeSelection`.
- Add one stable `PatchBenchSafeCopySelectionReadiness` automation ID with a
  polite live setting near the main Create action.
- Disabled required check boxes expose checked state, required/automatic copy,
  and their existing proof/help details through UI Automation.
- Native smoke expands Lab, verifies both required rows are checked and
  disabled, opens at least one required-row details expander, selects then
  clears an optional mod, verifies base-only readiness, and does not invoke
  either Create button, launch the game, or write a copy.

## Error Handling

- Invalid optional selection disables both Create buttons immediately.
- The live readiness text names the selection issue without offsets, keys, or
  maintainer jargon.
- A click-handler recheck prevents confirmation if enabled state becomes stale
  between rendering and invocation.
- Backend preflight remains the final authoritative fail-closed guard.

## Verification

- TDD model tests prove only the exact two keys are locked and their accessible
  copy explains the state.
- TDD helper tests cover valid base-only, valid optional rows, missing source,
  busy state, and invalid selection.
- TDD page/source tests prove every preset/reset path retains the pair, both
  Create buttons share readiness, and pre-confirm validation returns early.
- Existing AppCore preflight tests prove the backend still injects and verifies
  the exact pair before output mutation.
- Native UIA and visual checks prove checked/disabled intent, reachable
  details, base-only clear, live readiness, and zero copy/game action.
- Focused patch-engine/safe-copy gates and the WinUI primary lane cover the
  unchanged byte and copied-target contracts.
- Independent Codex and sanitized serial Cursor/Grok normal/adversarial review
  inspect the frozen substantive diff.

## Nonclaims And Scope

This slice does not change patch bytes, catalog rows or profile IDs, backend
compatibility injection, executable identity requirements, receipts, backups,
installed-game files, graphics or widescreen outcomes, runtime/Ghidra evidence,
canonical goal/state, distribution, or release state.
