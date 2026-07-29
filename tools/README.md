# Tools

Status: active — the reusable support surface, not a product lane
Last updated: 2026-07-29
Summary: what each tool in `tools/` is for, and which of them are gates.

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

## Documentation integrity

- `md_link_check.py` validates local link **targets**; `md_reachability_check.py`
  answers the different question of whether a document is linked from anywhere.
- `doc_header_check.py` enforces the header contract in
  [`DOCUMENTATION.md`](../DOCUMENTATION.md) — Status, Date, Verdict/Summary
  everywhere, plus Evidence and Specimen on findings. It rejects a byte claim
  that names no specimen, and a specimen that cites the deliberately patched
  Steam install. `doc_header_backlog.txt` holds the pre-standard documents and
  may only shrink; `--self-test` runs 44 cases with no repository present, and
  exit `2` means the check could not run rather than that it found nothing.
- `re_function_doc_names_check.py` re-resolves every per-function note's name
  assertion against a dated Ghidra name table.

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

## Parity measurement

- `compare_capture.py` compares one reconstruction frame against one retail
  frame per region. It refuses mismatched sizes rather than resampling.
- `pair_gameplay_capture.py` and `score_frontend_capture.py` pair whole capture
  runs against the retail reference by offset. `score_frontend_capture.py` is a
  **gate**: `rebuild/tools/Capture-Frontend.ps1` folds its verdict into `Status`,
  so a frontend regression fails the capture. Its thresholds live in
  `rebuild/tools/frontend-parity-plan.json` and are regression ceilings, not
  parity claims. The plan stores each measured value plus the single
  `marginPp: 2.0` regression allowance used to derive its ceiling.

A run that can score nothing reports `UNSCORED`, never `PASS`. Reference frames
are retail-derived and live under ignored local paths, so a fresh clone scores
nothing and must say so.

## Ghidra and runtime research

[`../PARITY_LAB.md`](../PARITY_LAB.md) is the engine-neutral function-discovery
and parity-pipeline authority. `parity_lab.py` joins repeated `drcov` or TTD
Replay coverage to exact Ghidra ranges, emits queryable evidence bundles, and
generates RVA-safe debugger symbols. `ExportParityLabGraph.java` publishes its
range/call pair only with a final hash-bound READY receipt;
`ExportBSimCandidates.java` is a read-only, identity-bound Stuart-source
candidate exporter. The matching focused gate is:

```powershell
py -3 tools\parity_lab_tests.py
```

The retained Java scripts are generic address, metadata, tag, disassembly,
xref, scalar, vtable, analysis-attribution, and reviewed-correction helpers.
`ListAnalysisOptions.java` reads a program's saved analyser state,
`RunIsolatedAnalyzer.java` runs one analyser with the rest switched off so a
database delta is attributable, and `ExportFullFunctionInventory.java` plus
`ghidra_inventory_diff.py` measure what a pass did to work that was already
correct. `RunIsolatedAnalyzer.java` mutates and belongs only on a disposable
canary copy. Applied wave-specific
mutations live in Git history. `ghidra_project_backup.py` and the provenance/
rename guards operate only on explicitly selected local project roots.

PowerShell CDB/input/profile helpers are for controlled copied targets. They
must preserve their explicit-arm, process-identity, and installed-game safety
checks. Full Ghidra stores, backups, raw CDB transcripts, frames, copied
executables, and bulk retail exports never belong in Git.

### The two wholesale instruments

Both were built on 2026-07-27 to replace one-question-per-launch probing, and
both were missing from this index until 2026-07-28. Detail belongs in each
tool's own documentation, not here.

- [`d3d9-proxy/`](d3d9-proxy/README.md) — a passive Direct3D 9 draw-call
  recorder for a **copied** target. It records, per frame and in draw order,
  every accounted draw call with the render state in force. Vertex/index bytes
  are present only where the configured cap and implemented extraction path
  cover them; refusals and omissions remain explicit rather than being called
  complete geometry. It exists because there is no HUD element *position* table
  in the shipped data, so positions were previously recovered by fitting
  pixels. It modifies no executable: `d3d9` is not a `KnownDLL`, so a `d3d9.dll`
  beside the application wins the load.
  `Run-D3D9Capture.ps1` and `Run-FrontendPageCapture.ps1` drive it.
- `ttd_record.ps1` / `ttd_query.ps1` / `Record-GameMoment.ps1` — Time Travel
  Debugging. `ttd_record.ps1` records a bounded launch or attach interval until
  the requested duration, guest exit, free-space stop, or configured file cap.
  `ttd_query.ps1` answers later offline questions against the resulting trace.
  `Record-GameMoment.ps1` attaches to an already-running copied target, records
  the requested interval, and normally leaves the target running.
  **Standing caveat: TTD recording requires an elevated token**, and this
  machine has no `TTDService`, so each recording raises a UAC prompt.

See also [`../patches/README.md`](../patches/README.md) for the patch-catalog
boundary that the copied-runtime helpers operate inside.

*(Added 2026-07-28. This section previously named neither instrument: a
case-insensitive search of this file for `d3d9`, `ttd`, `proxy` and
`Record-GameMoment` returned nothing, while the opening paragraph claims to
index "controlled copied-runtime research". `git grep -n d3d9-proxy -- '*.md'`
returned exactly one hit, the proxy README's own title line, so nothing in
tracked documentation led a reader to a 267-line README; on a fresh clone it
was reachable only by listing the directory. Nothing else in this file
changed.)*
