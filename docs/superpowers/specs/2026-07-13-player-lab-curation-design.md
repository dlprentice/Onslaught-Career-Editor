# Player Mods And Lab Curation Design

**Status:** Approved by the primary task on 2026-07-13 (option B)

## Goal

Make the normal Windowed & Mods path understandable and trustworthy for a first-time player without deleting the specialist recipes and diagnostics that researchers still need.

## Normal Player Contract

The normal path describes one exact base rather than presenting several peer presets:

- Every safe game copy always applies `resolution_gate` and `force_windowed`.
- The base allows non-4:3 display-mode candidates and prefers windowed startup. It does not claim field-of-view parity, universal windowing success, or an installed-game change.
- The two normal optional mods start unselected:
  - **PATCHED identity marker** adds the word `PATCHED` on the proven title/menu path so a copied executable can be distinguished from the original. It does not claim gameplay visibility or every overlay path.
  - **Goodies wall preview** changes the bounded Goodies-wall display-state path in the copied executable. It does not edit a save, award or persist Goodies, prove every entry, or prove model/FMV playback.
- Recovery remains prominent: recreate the safe copy or restore its app-owned backup. The installed game remains read-only.

Normal actions must remain reachable without opening Lab: source selection, create, receipt, launch, stop, save-copy choice, compatibility explanation, recovery explanation, marker toggle, and Goodies preview toggle.

## Lab Contract

Lab is collapsed by default and is not the old flat page hidden behind one click. Its contents are divided by user intent:

1. **Legacy and research recipes** — Windowed + Graphics Defaults, Enhanced Profile Preview, Debug Camera Preview, manual graphics-row selection, and clear optional rows. Existing profile IDs remain selectable and discoverable for receipts, regression work, and old instructions.
2. **Visual and executable experiments** — frontend margin colors and the detailed grouped patch-row list, including graphics flags, fullscreen fallback, pause, and camera rows. Every row retains its own proof and nonclaim details.
3. **Launch and control diagnostics** — launch flags, copied-options diagnostics, music staging, and technical online/research controls. These remain explicitly experimental or diagnostic and do not become player recommendations.

The advanced BEA.exe-only workflow remains a separate technical surface after the safe-game-copy workflow.

## Catalog Semantics

- Preserve `compatibility-copy`, `recommended-safe-copy`, `enhanced-edition-preview`, `debug-camera-preview`, and `custom` IDs.
- Preserve all patch keys and patch bytes.
- Rename user-facing legacy recipe labels only where needed to state `Lab` or `legacy` status truthfully.
- Do not silently add the marker or Goodies preview to compatibility. Both remain opt-in and unselected when Compatibility Copy is selected.
- Do not change Enhanced recipe contents in this slice. Its copied controller/sensitivity behavior remains documented in its Lab details because changing old recipe behavior would require a separate compatibility decision.

## Interaction And Accessibility

- Preserve existing automation IDs for moved controls.
- Add a stable automation ID for the Lab expander and meaningful group headings.
- Dynamic patch checkboxes are absent from the initial normal accessibility tree while Lab is collapsed; the two normal mod actions remain available as dedicated buttons.
- Selecting a Lab recipe may update the shared selected-profile status and options exactly as before.
- Selecting Compatibility Copy or clearing optional mods restores the exact base and leaves both normal mods unselected.

## Verification

- Static UI contract tests prove the information hierarchy, copy boundaries, stable IDs, and catalog ID retention.
- Existing profile/patch tests prove unchanged patch planning and copied-target safety.
- Native UIA proves Lab is collapsed initially, normal actions are reachable, Lab expands, and retained legacy recipes remain actionable.
- Native screenshots at a compact desktop size prove the normal page is concise and the expanded Lab has clear internal grouping.

## Nonclaims

This slice does not add or alter executable patches, prove widescreen gameplay parity, improve controller feel, unlock save data, validate every Goodies entry, make camera experiments gameplay-safe, enable online play, or repair integration-owned observer docsync drift.
