# What We Can Do Now (With Current Knowledge)

> **SUPERSEDED — archived/historical (2026-05-26):** Electron is **not** the active product surface. WinUI 3 is the primary product lane; `archive/electron-workbench/` is archived/reference only. Do not treat WinUI-centered priorities below—or any Electron-first wording elsewhere in this file—as current product direction.

Status: deprecated / archived/historical
Last updated: 2026-05-01
Replacement: `CURRENT_CAPABILITIES.md`, `roadmap/status-current.md`, and `roadmap/repo-structure-and-archive-map.md`

This archived note is a historical priority snapshot from an intermediate planning pass. Do not treat the WinUI-centered app priorities below as current product direction.

This is a short, practical list of things we can implement or validate right now based on what we've already mapped in `BEA.exe` and the `.bes`/`.bea` format docs/tools in this repo.

Source caveat: internal source references remain useful for parity and naming, but retail/Steam `BEA.exe` plus real save behavior are authoritative when they differ.

Canonical references:
- `CURRENT_CAPABILITIES.md`
- `reverse-engineering/binary-analysis/functions/FUNCTION_COVERAGE_STATE.md`
- `reverse-engineering/binary-analysis/functions/_index.md`

## App Development Priorities (Historical)

- This section records a superseded WinUI-centered plan. **Historical wording:** an intermediate revision named Electron as the product surface; that direction was superseded. The current product surface is WinUI 3, with AppCore, AppCore.Host, and the C# CLI retained as parity/reference bridges; Electron remains archived under `archive/electron-workbench/`.
- Keep WPF and Python app surfaces archived or shelved unless explicitly revived for historical reference work.
- Keep `Goodie Viewer` and `Asset Browser` prototypes shelved from active UI scope unless explicitly re-prioritized.
- Keep asset workflow integration limited to extraction/tooling pathways for now (no active in-app viewer surface in this tranche).
- Raise release quality through clearer status messages, better file-selection ergonomics, safer defaults for `.bea` vs `.bes`, and final package/public validation.
- Add or expand regression coverage around release-critical behaviors such as options-copy, keybind overrides, compare/analyze formatting, save/options discovery, and binary patch verify/apply/restore flows.

## Save Editor Improvements

- Integrate and **display** the save's persisted control bindings ("options entries" block) and tail snapshot fields in GUI/CLI output, while reserving "reserved/unmapped" wording only for bytes that remain semantically undecoded.
- Keep patching/analyze output safer by preserving any **packed metadata bits** we've observed in `BEA.exe`. Kill counters already preserve `meta`; extend the same pattern if and when other packed fields are discovered.
- Add "explain why" analyzer output for kill-driven unlocks and combined thresholds by tying the C#/CLI analyzers to the thresholds and the observed binary logic.

Relevant files:
- `tools/options_entries_decode.py`
- `reverse-engineering/save-file/save-format.md`
- `reverse-engineering/save-file/kill-tracking.md`
- `reverse-engineering/save-file/goodies-system.md`

## Localization / Text Tooling

- Decode `data/LANGUAGE/*.DAT` and resolve IDs using `text.stf`.
- Use that mapping to make RE docs, and later UI surfaces, show real strings instead of numeric IDs.
- Accelerate function renaming by extracting the actual text IDs passed to `CText__GetStringById`.

Relevant files:
- `tools/language_dat_decode.py`
- `reverse-engineering/binary-analysis/functions/text.cpp/_index.md`

## Game Patching / Modding Footholds

- Turn cheat-gated or debug-only features into normal toggles, such as free camera, by patching cheat checks.
- Alternatively, force the relevant globals or paths to behave as if the cheat is active.
- Expose and/or enable the existing console commands (`con_*`) and debug input actions so mod workflows do not require a dev build.

Relevant files:
- `reverse-engineering/game-mechanics/cheat-codes.md`
- `reverse-engineering/binary-analysis/functions/game.cpp/_index.md`
