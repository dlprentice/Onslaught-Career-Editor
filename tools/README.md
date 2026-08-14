# Tools

Status: active — the reusable support surface, not a product lane
Last updated: 2026-08-14
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

- `aya_archive_inventory.py`, `aya_cross_platform_compare.py`, and
  `aya_texture_fidelity_census.py` provide fail-closed AYA inventory,
  cross-platform pairing, and stored-texture geometry/block comparison.
- `export_game_assets.py`, `export_asset_catalog.py`,
  `export_language_corpus.py`, and `export_video_manifest.py` operate on
  user-supplied local inputs and write to a separate local output root.
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

[`../reverse-engineering/parity-lab.md`](../reverse-engineering/parity-lab.md) is the engine-neutral function-discovery
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

`GhidraApplyTextGapBoundaries.java` is the narrow disposable-project owner for
the reviewed 31-row PC `.text` gap manifest. It restricts disassembly and
derived reference sources to the exact preregistered bodies, creates only
default functions, and supports dry, apply, separate readback, and two forced
rollback probes. It does not authorize live or tracked Ghidra mutation.
`ghidra_text_gap_boundary_scratch_authority.py verify` reproduces the sealed
scratch decision without opening Ghidra. Mutator READY receipts use only
repository-relative POSIX paths. The globally registered authority test skips
only its saved-evidence reproduction when the ignored campaign is absent;
explicit `verify` still requires that complete saved evidence. Their focused
gates are:

```powershell
py -3 tools\ghidra_text_gap_boundary_mutator_tests.py
py -3 tools\ghidra_text_gap_boundary_scratch_authority_tests.py
py -3 tools\ghidra_text_gap_boundary_scratch_authority.py verify
```

`GhidraApplyExternalTableGapBoundaries.java` is the fail-closed structural
runner for the reviewed 79-row external-table gap manifest. It validates the
exact retail specimen, sealed 8,201-function PRE counters, manifest/proof
hashes, P0/P1/P2 partition, body bytes, demo evidence, disjoint ranges, the
corrected YUV-family row, and the existing Vec4Cross proof before admitting
default `FUN_` boundaries on an isolated db.18612 copy. It may replace
instruction decoding only when the complete old and new instruction ranges
remain inside an authorized body; names, signatures, comments, tags, data, and
bytes are outside its contract.

`ghidra_external_table_gap_boundary_scratch_authority.py` reproduces the saved
two-replica ceremony, the pinned 19-file PRE-project inventory, and its full
8,201-row equality gate. It independently rehashes the actual base and retained
restore trees, binds the detailed read-only probe log and safe command flags,
and treats inner backup receipts as absolute execution history rather than
portable paths. The ignored evidence is optional in a fresh clone: the
registered authority unit test skips when absent, while an explicit saved
verify refuses to pass without it.

```powershell
python -I -B tools\ghidra_external_table_gap_boundary_mutator_tests.py
python -I -B tools\ghidra_external_table_gap_boundary_scratch_authority_tests.py
python -I -B tools\ghidra_external_table_gap_boundary_scratch_authority.py verify
python -I -B tools\ghidra_external_table_gap_boundary_live_authority_tests.py
```

The resulting verdict is `SCRATCH_READY_LIVE_FORBIDDEN`; see the
[scratch report](../reverse-engineering/binary-analysis/external-table-gap-ghidra-scratch-admission-2026-08-14.md).

`GhidraApplyJpegCallbackBoundaries.java` is the structural-only runner for the
corrected 24-function IJG callback cohort. It is scoped to and fail-closes on
the expected 8,280-function PRE counts, all 38 body ranges and hashes, both
table/padding classifications, and the correction that `0x005B6900` is the
last byte of the instruction at `0x005B68FE`, not a function or data boundary.
Its only allowed mutation is creation of default `FUN_` bodies inside those
ranges. The scratch authority and backup ceremony own the exact 19-file project
and `db.18613` identity.

`ghidra_jpeg_callback_boundary_scratch_authority.py` reproduces the two saved
positive replicas, exact preservation of all 8,280 PRE rows, both rollback
readbacks, both external-path controls, and the read-only backup/restore/open
proof. Aggregate receipt paths are portable; an explicit verify requires the
complete ignored lane and authorizes neither live nor tracked mutation.

```powershell
python -I -B tools\ghidra_jpeg_callback_boundary_mutator_tests.py
python -I -B tools\ghidra_jpeg_callback_boundary_scratch_authority_tests.py
python -I -B tools\ghidra_jpeg_callback_boundary_scratch_authority.py verify
python -I -B tools\ghidra_jpeg_callback_boundary_live_authority_tests.py
```

See the
[scratch report](../reverse-engineering/binary-analysis/jpeg-ijg-callback-ghidra-scratch-admission-2026-08-14.md)
and its
[24-row evidence manifest](../reverse-engineering/binary-analysis/jpeg-ijg-callback-function-boundaries-2026-08-14.tsv).
The separate
[live-promotion preparation](../reverse-engineering/binary-analysis/jpeg-ijg-callback-ghidra-live-promotion-preparation-2026-08-14.md)
uses `ghidra_jpeg_callback_boundary_live_authority.py` to pin exact current
db.18613 PRE bytes, the 8,304-function prospective POST, one-save
backup/readback/restore chronology, `0x005B6900` listing ownership, and the
future projection/accounting. Its policy is `PREPARATION_ONLY`; the authority
never launches Ghidra and the preparation creates no future ceremony root.

`GhidraApplyD3dxGapBoundaries.java` is the structural-only runner for the two
complete D3DX-compatible loose bodies at `0x00595FC9` and `0x00596028`. It pins
the expected 8,280-function PRE counts, both body/range hashes, and the
function/instruction/reference counts. Its only allowed change is creation of
the two default-source functions; semantic names and all other metadata remain
forbidden. The scratch authority and recovery proof own the exact 19-file
db.18613 project identity.

`ghidra_d3dx_gap_boundary_scratch_authority.py` verifies the sealed ignored
campaign from its packaged copy. It rejoins all 8,280 PRE rows against two
independent 8,282-function readbacks, checks both rollback and both containment
controls, rehashes the retained recovery project, and authorizes no live or
tracked mutation.

```powershell
python -I -B tools\ghidra_d3dx_gap_boundary_mutator_tests.py
python -I -B tools\ghidra_d3dx_gap_boundary_scratch_authority_tests.py
```

See the
[scratch report](../reverse-engineering/binary-analysis/d3dx-gap-two-function-ghidra-scratch-admission-2026-08-14.md)
and its
[two-row manifest](../reverse-engineering/binary-analysis/d3dx-gap-two-function-scratch-manifest-2026-08-14.tsv).

`GhidraApplyCrtP0Boundaries.java` is the structural-only runner for the 23 P0
boundaries from corrected CRT22 run-c. It pins the exact 8,280-function /
8,400-range db.18613 PRE state, all 24 authorized body ranges and hashes, the
three forbidden entries, the excluded P1 canary, and the five-byte thunk from
`0x0045AC20` to `0x0045AC30`. Its only mutation is bounded instruction repair
and creation of default-source function boundaries inside those bodies.

`ghidra_crt_p0_boundary_scratch_authority.py` rehashes and rejoins run-c, two
byte-identical fresh derivations, pristine and demo specimens, current body
ownership, two saved positive replicas, two rollback readbacks, two containment
controls, and the read-only backup/restore/open proof. It publishes or verifies
only a portable ignored aggregate receipt and authorizes neither live nor
tracked mutation.

```powershell
python -I -B tools\ghidra_crt_p0_boundary_mutator_tests.py
python -I -B tools\ghidra_crt_p0_boundary_scratch_authority_tests.py
python -I -B tools\ghidra_crt_p0_boundary_scratch_authority.py verify
```

See the
[scratch report](../reverse-engineering/binary-analysis/crt-runtime-p0-ghidra-scratch-admission-2026-08-14.md)
and its
[23-row evidence manifest](../reverse-engineering/binary-analysis/crt-runtime-p0-function-boundaries-2026-08-14.tsv).

Hostile audit superseded that v1 receipt shape because it copied unpopulated
JPEG identity/CFG/demo columns. `GhidraApplyCrtP0BoundariesV2.java` emits only
structural fields it measures or validates. The versioned v2 authority checks
every retained TSV/READY field, revalidates the exact run-c demo owner, reruns
both replicas and all adverse controls, and preserves v1 evidence unchanged.

```powershell
python -I -B tools\ghidra_crt_p0_boundary_v2_mutator_tests.py
python -I -B tools\ghidra_crt_p0_boundary_scratch_authority_v2_tests.py
python -I -B tools\ghidra_crt_p0_boundary_scratch_authority_v2.py verify
```

Use the
[corrected v2 report](../reverse-engineering/binary-analysis/crt-runtime-p0-ghidra-scratch-admission-v2-2026-08-14.md);
the v1 report and sealed lane remain historical audit evidence.

`re_pc_function_body_fragments.py` proves the exhaustive five-gap class inside
five existing PC functions, including unique normalized demo twins and the
deliberate 12-byte FEP NOP exclusion. `GhidraApplyFunctionFragmentRanges.java`
can add only those exact body ranges and bounded disassembly on an isolated
db.18613 copy; it creates no function and changes no metadata or data.
`ghidra_function_fragment_range_scratch_authority.py` verifies the sealed
two-replica package without opening Ghidra; its only write is a new contained
receipt, and its policy remains `LIVE_FORBIDDEN`.

```powershell
python -I -B tools\re_pc_function_body_fragments_tests.py
python -I -B tools\ghidra_function_fragment_range_mutator_tests.py
python -I -B tools\ghidra_function_fragment_range_scratch_authority_tests.py
python -I -B tools\ghidra_function_fragment_range_live_authority_tests.py
```

See the
[scratch report](../reverse-engineering/binary-analysis/pc-function-body-fragment-ghidra-scratch-admission-2026-08-14.md)
and exact
[five-row manifest](../reverse-engineering/binary-analysis/pc-function-body-fragment-repairs-2026-08-14.tsv).

`ghidra_function_fragment_range_live_authority.py` is the read-only,
preparation-only owner for a possible later promotion of that exact five-row
cohort. `preflight` rehashes live/tracked db.18613 PRE and the complete retained
scratch tree without opening Ghidra. Future `check-live`, `seal`, and `verify`
phases fail closed until the separately authorized one-save ceremony, PRE/POST
recovery, tracked refresh/restore, projection, and exact body accounting exist.
The current blocker is intentional: no canonical ceremony or backup root has
been created. See the
[preparation and prospective runbook](../reverse-engineering/binary-analysis/pc-function-body-fragment-ghidra-live-promotion-preparation-2026-08-14.md).

`ghidra_external_table_gap_boundary_live_authority.py` is the completed
read-only promotion authority. Its historical `preflight` mode proved the
scratch authority and then-current live/tracked PRE before ceremony roots
existed. After a
separately authorized live write, `check-live` proves both fresh replicas, the
single live save, exact semantic/collateral deltas, and PRE/POST recovery while
requiring a create-new, exact-root inspection to prove tracked Ghidra remains
PRE after POST recovery. A separately authorized tracked refresh then satisfied
`seal`; `verify` now reproduces the immutable portable aggregate receipt. The
authority never launches Ghidra; `verify` is the present reusable mode. The historical
[preparation and runbook](../reverse-engineering/binary-analysis/external-table-gap-ghidra-live-promotion-preparation-2026-08-14.md)
is settled by the completed
[live-promotion report](../reverse-engineering/binary-analysis/external-table-gap-ghidra-live-promotion-2026-08-14.md).

PowerShell CDB/input/profile helpers are for controlled copied targets. They
must preserve their explicit-arm, process-identity, and installed-game safety
checks. Full Ghidra stores, backups, raw CDB transcripts, frames, copied
executables, and bulk retail exports never belong in Git.

### PC-native source-coordinate instruments

`re_pc_native_source_coordinates.py` is the receipt-pinned 2026-08-12
adjacency-only instrument. Its bytes are historical evidence and must not be
rewritten. `re_pc_native_source_coordinates_v3.py` is the versioned successor:
it consumes the frozen owner and the reviewed
[`1,840-row stack-stable intermediate`](../reverse-engineering/binary-analysis/pc-native-source-coordinates-stack-stable-2026-08-13.tsv),
then proves FILE/line call arguments over bounded concrete predecessor paths
with exact NUL-terminated path identity. It writes immutable local manifests
or checks an existing output directory without opening Ghidra or modifying the
specimen. Both coordinate inputs are exact hash/schema/row/function-count
pinned; substituted or truncated owners fail before scanning or publication.
The [merged report](../reverse-engineering/binary-analysis/pc-native-source-coordinates-2026-08-13.md)
owns the population distinctions, exact hashes, falsifiers, and current
1,863-coordinate result. Its focused gates are:

```powershell
py -3 tools\re_pc_native_source_coordinates_v3_tests.py
py -3 tools\re_pc_native_source_coordinates_v3_tests.py --prove-can-fail
```

### External-tool pilots

Third-party catalogs and model recommendations are discovery indexes, not
evidence or installation checklists. Prefer extending an existing owner. Adopt
a dependency only against one named bottleneck and measured baseline, using
disposable inputs and a local output root. Record exact answers, elapsed and
operator effort, reproducibility, and database/output drift; stop when the
candidate provides no material advantage or cannot stay inside project safety
and evidence boundaries.

For agentic Ghidra interfaces, the live and tracked projects are forbidden
pilot targets. Use an exact disposable copy, expose the smallest read-only
surface, compare consequential answers with existing headless exports, and
require project-tree equality afterward. Broad rename/comment/save/delete
surfaces are a rejection condition. For format tools, first reproduce the same
offsets and values as the existing parser on a known fixture; add an interactive
schema or generated parser only when it reduces repeated work across real
consumers. Consequential results need two reproducible runs, but no tool or
pilot is mandatory.

Measured pilot decisions (2026-08-13; full receipts remain machine-local under
`D:\bea-ps2-crossbuild-tool-pilot-20260813-v1`):

1. This repository's bounded AYA observer now distinguishes the proved PC
   chunked-zlib envelope from raw console tag streams while retaining complete
   byte accounting and fail-closed framing. Logical cross-platform comparison
   remains a repository-owned parser task, not a reason to add another format
   framework.
2. [EmotionEngine Reloaded v2.1.36](https://github.com/chaoticgd/ghidra-emotionengine-reloaded/releases/tag/v2.1.36)
   is **approved only for isolated PS2 analysis projects**. Across 969
   scanner-bounded SDK ranges it decoded 49,723/49,723 words, versus
   42,553/49,723 under stock MIPS, and made 640 additional ranges fully
   decodable. This establishes a materially better R5900/MMI/COP2-VU0 `.text`
   decoder, not reachability or VU microcode recovery. The constant-reference
   analyzer is conditional: sampled READ/WRITE references were 19/19 valid,
   while generic DATA references produced 10 false positives and one unresolved
   result in a 17-row purposive sample. Quarantine every DATA result for manual
   review. The zero-byte retail `.mdebug.eabi64` still contains no symbols.
3. [sce-symbol-scanner v0.0.1](https://github.com/LostTemplarRH/sce-symbol-scanner/releases/tag/v0.0.1)
   is **approved as reviewed SDK boundary/name candidate evidence**, never as a
   blind import. Each PS2 build produced 1,006 rows over 969 addresses and 16
   libraries, with the same 967 address-free signatures across demo, EU, and US
   builds. Twenty-nine addresses carried competing names (37 excess rows); reject
   all collision rows until independently adjudicated. Its prototype also writes
   a deterministic 46,143,832-byte `tests.log` into the process working
   directory, so every wrapper must set an explicit disposable working directory.
   Do not install either pilot into canonical Ghidra or track its binaries,
   disposable projects, raw CSVs, or debug log.

Do not treat broad Ghidra MCP access as an acceleration on the live project.
Current candidates expose writable rename/comment/function/assembly/byte-patch
surfaces; a future evaluation belongs only on a cloud-disabled, localhost-only
replica with mutations disabled and exact before/after tree equality.

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
- `ttd_record.ps1` / `ttd_query.ps1` / `Record-GameMoment.ps1` /
  `Record-LevelOpeningCampaign.ps1` — Time Travel Debugging. `ttd_record.ps1`
  records a bounded launch or attach interval until the requested duration,
  guest exit, free-space stop, or configured file cap. `ttd_query.ps1` answers
  later offline questions against the resulting trace. `Record-GameMoment.ps1`
  attaches to an already-running copied target, records the requested interval,
  and normally leaves the target running. `Record-LevelOpeningCampaign.ps1`
  discovers the 66 shipped IDs that have a world header, mission scripts, and a
  world archive, then records one resumable opening trace per level from a
  single elevated shell.
  **Standing caveat: TTD recording requires an elevated token**, and this
  machine has no `TTDService`. Start an unattended campaign from one elevated
  shell; the manual attach helper raises UAC for an individual capture.
- `Record-Level521Session.ps1` / `Test-Level521NativeCoverage.ps1` —
  a played, attach-recorded session on level 521 and its verification.
  Seventeen MissionScript natives are authored in level 521's shipped scripts
  and were executed by none of the sixty-six recorded level openings; **none of
  them fires from merely starting the level**, and twelve hang off a single
  player action. The record helper launches the copied target at level 521,
  waits for you, and records one bounded take; the test helper drives the
  landed coverage collector and prints a per-native checklist, deciding from
  each per-trace receipt rather than the runner's status labels (task #155).
  **A human at the keyboard is required — start at
  [`RUNBOOK-level521-native-capture.md`](RUNBOOK-level521-native-capture.md),
  which needs no code reading.**

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
