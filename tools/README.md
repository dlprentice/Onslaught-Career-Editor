# Tools

`tools/` contains the small reusable support surface for the WinUI product,
release packaging, guarded asset extraction, format inspection, Ghidra work,
and controlled copied-runtime research. It is not a product GUI or a historical
probe archive.

Root [`package.json`](../package.json) is the command authority. Start with:

```powershell
npm test
npm run test:docs
npm run test:safety
```

## Product and release

- `winui_lore_pack_builder.py` builds the short-path offline pack from the
  canonical `lore/` tree and the single `lore-book/BOOK.md` entry guide.
- `winui_zip_package_probe.py` builds the disposable publish and inspects the
  portable ZIP candidate.
- `generate_winui_third_party_notices.py` keeps the tracked notice draft aligned
  with restored project dependencies.

Use [`release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`](../release/readiness/PUBLIC_SIGNOFF_COMMANDS.md)
for release-specific command selection. These tools do not publish, sign, or
install anything by themselves.

## Payload and output safety

- `public_allowlist_safety_check.py` rejects tracked game/runtime payloads,
  build output, raw debugger scripts, common secret patterns, and unsafe
  submodule payloads while preserving the two reviewed fixture exceptions.
- `safe_generated_output.py` provides guarded local publication for Python
  exporters.
- `runtime_process_identity.psm1` and `runtime_proof_lab_hygiene.py` provide
  process/path identity and cleanup primitives for copied-runtime helpers.

## Assets and formats

- `aya_archive_inventory.py`, `export_game_assets.py`,
  `export_asset_catalog.py`, `export_language_corpus.py`, and
  `export_video_manifest.py` operate on user-supplied local inputs and write to
  a separate local output root.
- `rebuild/tools/materialize_retail_assets.py` verifies one supported retail
  installation and reproduces the exact current rebuild inputs at ignored
  runtime paths. Existing rebuild build/run/smoke commands invoke it directly.
- `BeaAssetExportHarness/` is the bounded C# AYA/FBX export bridge.
- `language_dat_decode.py`, `options_entries_decode.py`,
  `cheat_table_decode.py`, and `cardid_preset_manager.py` are focused format
  inspection utilities.

Generated catalogs, retail assets, conversions, and bulk exports remain ignored
local material. Source retains only the bounded recipe and implementation.
Passing an output safety test proves neither format completeness nor visual
fidelity.

## Ghidra and runtime research

The retained Java scripts are generic address, metadata, tag, disassembly,
xref, scalar, vtable, and reviewed-correction helpers. Applied wave-specific
mutations live in Git history. `ghidra_project_backup.py` and the provenance/
rename guards operate only on explicitly selected local project roots.

PowerShell CDB/input/profile helpers are for controlled copied targets. They
must preserve their explicit-arm, process-identity, and installed-game safety
checks. Full Ghidra stores, backups, raw CDB transcripts, frames, copied
executables, and bulk retail exports never belong in Git.
