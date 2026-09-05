# Tools

Status: active — the reusable support surface, not a product lane
Last updated: 2026-08-31
Summary: what each tool in `tools/` is for, and which of them are gates.

`tools/` contains the small reusable support surface for the WinUI product,
release packaging, guarded asset extraction, format inspection, Ghidra work,
and controlled copied-runtime research. It is not a product GUI or a historical
probe archive.

Root [`package.json`](../package.json) is the command authority. On Omarchy,
start with:

```bash
npm run test:docs
npm run test:safety
```

`npm test` and Windows-bound runtime/release tools run only inside the isolated
Windows VM. Current root commands and reusable examples use `python` and
forward-slash paths on both hosts. Dated receipts and historical evidence may
retain the literal Windows commands and drive letters that produced them; a
tool can also have an explicitly documented Windows evidence dependency.

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
- `cmsh_animation_usage_census.py` performs a read-only, optionally
  mirror-hash-verified join across loose CMSH pose/skeleton lanes, numeric-LVLR
  `MESH` membership, and authored MSL animation calls. Its JSON output is
  restricted to ignored `local-lab` or `.artifacts` paths.
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

## Campaign replay

Current complete-RE verification is selected only by `developer_state.json` →
`current_re_authority.verify`. On this Linux host that command uses
`re_campaign_gen32_host_attestation.py`; its focused fail-closed and real-data
replay coverage lives in `re_campaign_gen32_host_attestation_tests.py`. The
adapter binds the exact historical Windows namespace to the exact canonical Git
checkout and its real repo-local `local-lab/`, prevalidates the reachable frozen
reducer graph, verifies the canonical/replica authority, and performs a
temporary full replay without rewriting frozen bytes. It also requires the
retired ProjectData lab path to remain absent and keeps durable host-attestation
output independently pinned under the ignored repo-local `local-data/host-attestations`.

`re_campaign_historical_source_projection_v2.py` is the historical
Generation-24 launcher for an immutable campaign whose rebuild inputs were
later strengthened. For Generation 24 it first pins and tests the current player-damage and weapon-
scatter owners, then exposes exactly three historical source identities to the
frozen verifier in memory. Both `Path.open` and built-in file reads are covered,
including recursive parent replays; writes to projected paths are refused. The
launcher does not repin or modify Generation 24, and its focused test exercises
the retained full replay when the machine-local campaign evidence is present.
`re_campaign.py` admits that campaign as Generation 25 carry only from the
literal canonical path, READY, external authority selector, reducer, outputs,
and counts. The carry gate invokes the same projected full replay with current
focused rebuild checks; a replica, moved root, changed selector, or generic
Generation 24 bundle is refused.

## Ghidra and runtime research

### Cohort promotion framework

`GhidraApplyCohortManifest.java` is the single reusable promotion applier. A
cohort is a **manifest plus a spec**, not a new program: `cohort-specs/*.spec.tsv`
declares the program identity, the PRE/POST metric pins, the manifest integrity
pins, the manifest-column-to-verb binding, and the opt-in verb set
(`SET_NAME`, `SET_PROTOTYPE`, `SET_BODY`, `DISASSEMBLE_BOUNDED`,
`CLEAR_BOUNDED`, `REMOVE_STALE_BOOKMARK`). A verb the spec does not declare is
structurally unreachable, so a name cohort cannot touch a body and a signature
cohort cannot touch a name. Modes are `census`, `identity`, `dry`/`predict`,
`apply`, `readback`, `collateral`, `plan`, and the adverse `probe-*` modes,
which can never commit.

It is `LIVE_FORBIDDEN` by construction and refuses any project path outside a
`cohort-rehearsal` segment. `GhidraApplyCohortManifestLive.java` is its
live-capable twin, derived by the reviewed allowlist in
`ghidra_cohort_framework_tests.py` — one gate inverted, plus a compiled
per-cohort authorization allowlist. Regenerate it with
`python tools/ghidra_cohort_framework_tests.py --emit-live`; never hand-edit it.

Reversibility is a **ceremony-level** property. In this Ghidra 12.1.2 headless
build `endTransaction(id, false)` does not revert `Function.updateFunction`,
`Program.canUndo()` is false, and a new db version is written even when the
script throws. Every non-mutating gate for every row therefore runs before the
first write, and no receipt claims transaction-level atomicity.

**`varargs` is a manifest field of `SET_PROTOTYPE`, and its default is
PRESERVE.** The three superseded appliers all cleared varargs unconditionally and
then asserted `POST`/readback `varargs == false`, so a variadic prototype could
not be expressed at all, and a target that already carried `varargs=true` would
have been silently stripped with its own POST gate certifying the strip.
Measured 2026-08-17 on db.18622: **10 of the 8,329 functions carry
`varargs=true`**, so that second failure mode was one manifest row away rather
than hypothetical. In the framework the value comes from the column bound by
`col.varArgs` — `true`, `false`, or empty for preserve — and an absent binding
means preserve for every row *and* keeps `varArgs` a frozen collateral column, so
a strip by omission is a refusal on any of the 8,329 rows. `POST` and readback
compare against the manifest value, never a literal. `probe-fault-varargsflip`
writes the opposite of the resolved decision so those gates can be provoked in
both directions; like every fault mode it can never commit.

**Every run records which applier produced it.** `COHORT_APPLIER` and the
receipt's `applier` object carry this script's own source SHA-256, measured before
the spec is read, because otherwise the only way to tell which framework version
wrote a receipt is file mtimes plus re-deriving the twin — inference, not a chain
of custody. A spec may also pin `applierSha256`, repeated to admit both the
instrument and its live twin (their digests necessarily differ); a pin that
matches nothing refuses with `APPLIER SHA PIN` before any write.

`ghidra_cohort_replay.py` has no current drive-letter or database default. Every
database-consuming mode requires an explicit Linux `analyzeHeadless`, a root of
catalog-restored historical backup trees, and a contained scratch lane whose
path has an exact `cohort-rehearsal` segment. Restore the selected aliases from
`/srv/archive-a/Onslaught-Ghidra-Recovery/` into that separate root first; the
tool refuses the sealed package in place, the mutable `local-lab/ghidra-projects/BEA`
owner, and the tracked checkpoint. It rebuilds only scratch replicas, runs the
ceremony modes, and writes receipts below the selected lane. A `rehearsalOnly`
cohort has no archived ceremony to reproduce, so a clean run is reported as
`REHEARSED_NOT_PROMOTED` and authorizes nothing. It can also build a noncanonical
sandbox (`--sandbox`), run the framework's provoked gate matrix
(`--probes core|fault|all`), and run the varargs controls (`--probes varargs`).
Sandbox builds and core/all containment probes additionally require an explicit
`--sandbox-root` whose path contains an exact `ghidra-noncanonical-sandbox`
segment and no `cohort-rehearsal` segment; this preserves the negative
containment test instead of accidentally turning the sandbox into a permitted
rehearsal project.

```bash
python tools/ghidra_cohort_replay.py \
  --cohort boundary-cohort41 \
  --ghidra /home/xsniper80/.local/opt/ghidra_12.1.3_PUBLIC/support/analyzeHeadless \
  --restored-backups /absolute/path/to/restored-cohort-backups \
  --lane /absolute/path/to/local-lab/cohort-rehearsal/run-id

python tools/ghidra_cohort_replay.py \
  --verdict \
  --receipts /absolute/path/to/local-lab/cohort-rehearsal/run-id/receipts
```

Historical `C:`, `D:`, and `H:` strings retained inside the harness are frozen
receipt identities only. They are never translated or selected as Linux paths.
The focused framework gate is:

```powershell
python -m unittest \
  tools.ghidra_cohort_replay_routing_tests \
  tools.ghidra_cohort_framework_tests
```

The three superseded one-shot appliers (`GhidraApplyBoundaryCohort41V4.java`,
`GhidraApplyNameCohort160V2.java`, `GhidraApplyAbiSignaturesV2.java`) and their
mutator suites stay in place as the receipt-pinned owners of their completed
ceremonies. Do not repin or revive them; new cohorts use the framework. In
particular, **do not add varargs support to the superseded appliers**: each one's
source SHA-256 is pinned by its own mutator suite, which also proves it is the
reviewed one-gate-inverted derivation of its rehearsal instrument, so even a
comment at the defect site would repin a completed owner. The defect is recorded
here and in the framework banner instead, and
`test_v2_is_left_exactly_as_its_receipts_pinned_it` fails if `V2` is edited at
all.

[`../reverse-engineering/parity-lab.md`](../reverse-engineering/parity-lab.md) is the engine-neutral function-discovery
and parity-pipeline authority. `parity_lab.py` joins repeated `drcov` or TTD
Replay coverage to exact Ghidra ranges, emits queryable evidence bundles, and
generates RVA-safe debugger symbols. `ExportParityLabGraph.java` publishes its
range/call pair only with a final hash-bound READY receipt;
`ExportBSimCandidates.java` is a read-only, identity-bound Stuart-source
candidate exporter. The matching focused gate is:

```powershell
python ./tools/parity_lab_tests.py
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

### Function-triage packets (P4)

`tools/export_packets.py` is the batch function-triage packet exporter: it
takes a VA list file and an output directory, invokes headless Ghidra **once**
(`-readOnly -noanalysis`) over the whole list, and emits one stable-schema
JSON packet per VA (`bea.re.triage-packet.v1`) — decompile slice, callers and
callees (STATIC_DIRECT instruction flows), referenced defined strings with
their referring functions, observed vtable-pointer evidence (slot-0 dword,
executable-target test, data-referring functions, slot-minus-4 dword), and the
campaign grade joined from the tracked closure TSV when present — plus a run
manifest with per-packet SHA-256s and a `triage-ready.json` receipt published
last as the commit marker. Every packet header carries the source image
SHA-256; the specimen identity is `74154bfa…7750`.

Read-only posture: the historical Windows H: POST backup
(`H:\BEA-Ghidra-Backups\2026-08-17-vftable65-post-live`, db.18627) is provenance,
not a current default or Omarchy route. Current runs require both an explicit
prepared project root and an explicit Ghidra executable. The sole mutable Linux
PC project is `local-lab/ghidra-projects/BEA/` at `db.18635`; ordinary exporter
runs still use it read-only. Pointing at the historical live maintainer
project is refused unless `--allow-live-project` is passed, and every invocation
stays `-readOnly -noanalysis`. Incremental: a re-run over
the same output directory skips VAs whose packets already exist with the same
image hash (and a live READY receipt) without launching Ghidra at all;
`--force` removes matching-image packets first and re-cuts them, while a packet
cut from a *different* image refuses rather than being silently overwritten.

```powershell
python ./tools/export_packets.py ./tools/packet-va-cgame-level-flow.txt `
  ./local-lab/packet-runs/cgame-level-flow `
  --project-root <prepared-read-only-project-directory> `
  --ghidra <path-to-analyzeHeadless.bat>
python ./tools/export_packets.py <addresses.txt> <out-dir> `
  --project-root <prepared-read-only-project-directory> `
  --ghidra <path-to-analyzeHeadless.bat> --dry-run
```

The named 5-VA smoke list `tools/packet-va-cgame-level-flow.txt` carries the
tracked CGame level-flow identities from
[`../reverse-engineering/ghidra-functions.md`](../reverse-engineering/ghidra-functions.md);
it is the gate's example list and the smoke suite's fixture. The focused gate
is:

```powershell
python ./tools/export_packets_tests.py
```

The smoke suite needs no Ghidra: it drives the real driver against a fake
headless that emits the same markers and file shapes, asserting the ONE-run
gate, the `-readOnly -noanalysis` flags, post-run hash verification, skip/
force/foreign-image incremental behavior, the live-project refusal, and the
Java exporter's static contract (usage arity, READY marker, no mutation APIs).

A requested VA with no function yields a `status=NOT_FUNCTION` packet rather
than a silent skip; missing evidence inside a packet (failed decompile, absent
closure row) is recorded as null/false fields, never omitted. Consumers reject
a whole output directory until its `triage-ready.json` exists and all manifest
hashes verify.

> **Historical Ghidra ceremony boundary.** The one-shot boundary, preparation,
> and live-authority tools documented below are Windows-era provenance for
> completed, receipt-bound ceremonies. Their command lines are reproduction
> records, not current launch recipes. Never point them at
> `local-lab/ghidra-projects/BEA/`, translate their drive-letter paths, or repin
> their frozen identities to make them run. A deliberate historical replay must
> restore the exact catalog-selected disposable tree and use the procedure's
> frozen inputs. Current mutation remains paused and is governed by
> `reverse-engineering/ghidra/README.md`.

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
python ./tools/ghidra_text_gap_boundary_mutator_tests.py
python ./tools/ghidra_text_gap_boundary_scratch_authority_tests.py
python ./tools/ghidra_text_gap_boundary_scratch_authority.py verify
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
python -I -B ./tools/ghidra_external_table_gap_boundary_mutator_tests.py
python -I -B ./tools/ghidra_external_table_gap_boundary_scratch_authority_tests.py
python -I -B ./tools/ghidra_external_table_gap_boundary_scratch_authority.py verify
python -I -B ./tools/ghidra_external_table_gap_boundary_live_authority_tests.py
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
python -I -B ./tools/ghidra_jpeg_callback_boundary_mutator_tests.py
python -I -B ./tools/ghidra_jpeg_callback_boundary_scratch_authority_tests.py
python -I -B ./tools/ghidra_jpeg_callback_boundary_scratch_authority.py verify
python -I -B ./tools/ghidra_jpeg_callback_boundary_live_authority_tests.py
```

See the
[scratch report](../reverse-engineering/binary-analysis/jpeg-ijg-callback-ghidra-scratch-admission-2026-08-14.md)
and its
[24-row evidence manifest](../reverse-engineering/binary-analysis/jpeg-ijg-callback-function-boundaries-2026-08-14.tsv).
The separate
[live-promotion preparation](../reverse-engineering/binary-analysis/jpeg-ijg-callback-ghidra-live-promotion-preparation-2026-08-14.md)
uses `GhidraApplyJpegCallbackBoundariesV2.java` and
`ghidra_jpeg_callback_boundary_live_authority.py` to pin the exact then-current
db.18614 PRE, reproduce two fresh disposable 8,304-function prospective POST
replicas, and bind `0x005B6900` listing ownership. After the separately
authorized one-save ceremony, `check-live` proved PRE/POST recovery while
tracked remained PRE; `seal` then proved the tracked refresh/restore,
8,304-row projection, and exact 1,810,287-byte body accounting. `verify` now
reproduces the immutable aggregate receipt without opening or writing Ghidra.
See the completed
[live-promotion report](../reverse-engineering/binary-analysis/jpeg-ijg-callback-ghidra-live-promotion-2026-08-14.md).

`GhidraApplyD3dxGapBoundaries.java` is the structural-only runner for the two
complete D3DX-compatible loose bodies at `0x00595FC9` and `0x00596028`. It pins
the expected 8,280-function PRE counts, both body/range hashes, and the
function/instruction/reference counts. Its only allowed change is creation of
the two default-source functions; semantic names and all other metadata remain
forbidden. The scratch authority and recovery proof own the exact 19-file
db.18613 project identity.

`ghidra_d3dx_gap_boundary_scratch_authority.py` verifies the sealed ignored
campaign from its packaged copy. It rejoins all 8,280 PRE rows against two
independent 8,282-function readbacks, checks the after-one rollback and
post-inner-commit compensation probes plus both containment controls, rehashes
the retained recovery project, and authorizes no live or tracked mutation.

`GhidraApplyD3dxGapBoundariesV2.java` and
`ghidra_d3dx_gap_boundary_current_preparation_authority.py` re-ground that exact
two-function shape against then-current db.18617 without opening live Ghidra. The
preparation authority rejoins all 8,327 PRE rows against two independent
8,329-function readbacks, pins the two positive and four control project trees,
rehashes the now-historical scratch tree, and records the consumed
`PREPARATION_ONLY` state. The old
scratch verifier intentionally self-expires against later tracked Ghidra state;
the preparation replicas, not an overridden historical current-root assertion, own
the db.18617 proof.

`ghidra_d3dx_gap_boundary_live_authority.py` verifies the completed one-save
live ceremony without mutating Ghidra. It binds the exact PRE and db.18618 POST
project trees, all nine run directories, the tracked-still-PRE phase, retained
PRE/POST/tracked restore probes, exact 8,327-to-8,329 function join, unchanged
instruction/reference counts, rolling-database rotation, current name
projection, and 1,811,691-byte body union. Its create-new aggregate receipt is
portable; repeated `verify` runs are read-only.

```powershell
python -I -B ./tools/ghidra_d3dx_gap_boundary_mutator_tests.py
python -I -B ./tools/ghidra_d3dx_gap_boundary_scratch_authority_tests.py
python -I -B ./tools/ghidra_d3dx_gap_boundary_current_preparation_authority_tests.py
python -I -B ./tools/ghidra_d3dx_gap_boundary_live_authority_tests.py
```

See the
[scratch report](../reverse-engineering/binary-analysis/d3dx-gap-two-function-ghidra-scratch-admission-2026-08-14.md)
and its
[two-row manifest](../reverse-engineering/binary-analysis/d3dx-gap-two-function-scratch-manifest-2026-08-14.tsv),
plus the historical
[db.18617 preparation report](../reverse-engineering/binary-analysis/d3dx-gap-two-function-ghidra-live-promotion-preparation-2026-08-14.md)
and completed
[db.18618 live-promotion report](../reverse-engineering/binary-analysis/d3dx-gap-two-function-ghidra-live-promotion-2026-08-14.md).

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
python -I -B ./tools/ghidra_crt_p0_boundary_mutator_tests.py
python -I -B ./tools/ghidra_crt_p0_boundary_scratch_authority_tests.py
python -I -B ./tools/ghidra_crt_p0_boundary_scratch_authority.py verify
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
python -I -B ./tools/ghidra_crt_p0_boundary_v2_mutator_tests.py
python -I -B ./tools/ghidra_crt_p0_boundary_scratch_authority_v2_tests.py
python -I -B ./tools/ghidra_crt_p0_boundary_scratch_authority_v2.py verify
```

Use the
[corrected v2 report](../reverse-engineering/binary-analysis/crt-runtime-p0-ghidra-scratch-admission-v2-2026-08-14.md);
the v1 report and sealed lane remain historical audit evidence.

`GhidraApplyCrtP0BoundariesV3.java` changed only the schema identity and exact
db.18614 PRE/POST counters needed to replay that corrected cohort on the
pre-JPEG 8,396-range project. The read-only
`ghidra_crt_p0_boundary_live_preparation.py` replays the v2 scratch authority,
rehashes two fresh current-state replicas, independently totals their body
ranges, proves all 8,280 PRE function rows unchanged, and requires live and
tracked Ghidra to be byte-identical at db.18614. This preparation is historical;
the later v2 preparation re-grounded it against then-current db.18615. It granted
no mutation authority.

```powershell
python -I -B ./tools/ghidra_crt_p0_boundary_live_preparation_tests.py
python -I -B ./tools/ghidra_crt_p0_boundary_live_preparation.py preflight `
  --repo <repository-root> --scratch-repo <repository-root> `
  --live-project <maintainer-project-root> --live-lane <future-live-lane> `
  --pre-backup <future-pre-backup> --post-backup <future-post-backup>
```

See the
[live-promotion preparation](../reverse-engineering/binary-analysis/crt-runtime-p0-ghidra-live-promotion-preparation-2026-08-14.md).
Its policy is `PREPARATION_ONLY`; it opens no Ghidra project and performs no
live or tracked write.

`GhidraApplyCrtP0BoundariesV4.java` is the exact current-state counter rebase
for db.18615: 8,304 functions, 8,434 ranges, 551,055 instructions, and 234,467
references. The read-only
`ghidra_crt_p0_boundary_live_preparation_v2.py` replays the corrected scratch
authority and validates two fresh disposable prospective POST saves. It proves
all 8,304 PRE rows exact, 23 created default-metadata functions, 1,131 newly
owned bytes, and byte-identical semantic exports. It also binds the exact
53-byte physical variance between the two newly written db.18616 files rather
than claiming false database-byte determinism. Its policy remains
`PREPARATION_ONLY`; it refused until the separately authorized ceremony paths
were created and is now retained as consumed preparation evidence.

```powershell
python -I -B ./tools/ghidra_crt_p0_boundary_live_preparation_v2_tests.py
python -I -B ./tools/ghidra_crt_p0_boundary_live_preparation_v2.py preflight `
  --repo <repository-root> --scratch-repo <repository-root> `
  --live-project <maintainer-project-root> --live-lane <future-live-lane> `
  --pre-backup <future-pre-backup> --post-backup <future-post-backup>
```

See the
[consumed db.18615 preparation](../reverse-engineering/binary-analysis/crt-runtime-p0-ghidra-live-promotion-preparation-v2-2026-08-14.md).

`ghidra_crt_p0_boundary_live_authority_v2.py` is the read-only aggregate owner
for the completed db.18615 ceremony. It proves the sole writable live save,
separate PRE/POST readbacks, all 8,304 unchanged PRE rows and the exact 23-row
addition, the db.18614-to-db.18616 rotation with stable db.18615, retained
read-only PRE/POST/tracked restores, live/tracked/POST-backup equality, the
mechanical 8,327-row name projection, and 1,811,418-byte body union. `seal`
create-writes only the ignored aggregate receipt; `verify` is entirely
read-only.

```powershell
python -I -B ./tools/ghidra_crt_p0_boundary_live_authority_v2_tests.py
python -I -B ./tools/ghidra_crt_p0_boundary_live_authority_v2.py verify `
  --repo <repository-root> --live-project <maintainer-project-root> `
  --pre-backup <retained-pre-backup> --post-backup <retained-post-backup> `
  --output <repository-root>/local-lab/ghidra-crt23-p0-boundary-live-promotion-db18615-20260814-v2/live-promotion.ready.json
```

See the
[completed live-promotion report](../reverse-engineering/binary-analysis/crt-runtime-p0-ghidra-live-promotion-2026-08-14.md).

`GhidraApplyCrtEhParentRange.java` is the scratch-only follow-on for the one
existing CRT parent deliberately excluded from that 23-function promotion. It
adds only `0x005D0AD6..0x005D0AEF` to `CRT__LongJmpProbe_NoOp`, requires the
exact db.18616 PRE/POST counters, forbids new filter/handler entries, and
preserves all non-body state. `ghidra_crt_eh_parent_range_scratch_authority.py`
replays the sealed two-replica, failure-control, inventory, backup, and
relocation evidence without opening Ghidra. Its reusable mode is read-only and
the campaign remains `LIVE_FORBIDDEN`.

```powershell
python -I -B ./tools/ghidra_crt_eh_parent_range_mutator_tests.py
python -I -B ./tools/ghidra_crt_eh_parent_range_scratch_authority_tests.py
python -I -B ./tools/ghidra_crt_eh_parent_range_scratch_authority.py verify
```

See the
[scratch report](../reverse-engineering/binary-analysis/crt-eh-parent-range-ghidra-scratch-admission-2026-08-14.md)
and exact
[one-row manifest](../reverse-engineering/binary-analysis/crt-eh-parent-range-repair-2026-08-14.tsv).

`ghidra_crt_eh_parent_range_live_authority.py` is the four-mode, read-only
outer authority used by the completed one-save promotion. At preparation time,
`preflight` reproduced the 283-file scratch package, exact live/tracked
db.18616 PRE, projection, body ranges, and direct-call graph while requiring
every ceremony root to be absent. `check-live` required the separately created
PRE/POST backups and restores, one writable apply between read-only
dry/readback runs, and a durable tracked-still-PRE inspection. `seal`
additionally required the exact tracked refresh/restore and mechanical
projection/accounting; its only write was a new ignored receipt. `verify`
remains fully read-only and is the reusable current gate. None of those modes
grants action-specific authority to mutate live or tracked Ghidra.

```powershell
python -I -B ./tools/ghidra_crt_eh_parent_range_live_authority_tests.py
python -I -B ./tools/ghidra_crt_eh_parent_range_live_authority.py preflight `
  --repo <repository-root> --evidence-repo <evidence-repository-root> `
  --live-project <maintainer-project-root> --live-lane <future-live-lane> `
  --pre-backup <future-pre-backup> --post-backup <future-post-backup>
```

See the historical
[live-promotion preparation](../reverse-engineering/binary-analysis/crt-eh-parent-range-ghidra-live-promotion-preparation-2026-08-14.md)
and completed
[live-promotion report](../reverse-engineering/binary-analysis/crt-eh-parent-range-ghidra-live-promotion-2026-08-14.md).

`re_pc_function_body_fragments.py` proves the exhaustive five-gap class inside
five existing PC functions, including unique normalized demo twins and the
deliberate 12-byte FEP NOP exclusion. `GhidraApplyFunctionFragmentRanges.java`
can add only those exact body ranges and bounded disassembly on the sealed
isolated db.18613 scratch copies; it creates no function and changes no metadata
or data.
`ghidra_function_fragment_range_scratch_authority.py` verifies the sealed
two-replica package without opening Ghidra; its only write is a new contained
receipt, and its policy remains `LIVE_FORBIDDEN`.

```powershell
python -I -B ./tools/re_pc_function_body_fragments_tests.py
python -I -B ./tools/ghidra_function_fragment_range_mutator_tests.py
python -I -B ./tools/ghidra_function_fragment_range_scratch_authority_tests.py
python -I -B ./tools/ghidra_function_fragment_range_live_authority_tests.py
```

See the
[scratch report](../reverse-engineering/binary-analysis/pc-function-body-fragment-ghidra-scratch-admission-2026-08-14.md)
and exact
[five-row manifest](../reverse-engineering/binary-analysis/pc-function-body-fragment-repairs-2026-08-14.tsv).

`ghidra_function_fragment_range_live_authority.py` is the completed read-only,
preparation-policy authority for that exact five-row cohort. Its historical
`preflight` proved live/tracked db.18613 PRE and the complete retained scratch
tree without opening Ghidra. After the separately authorized one-save ceremony,
`check-live` proved PRE/POST recovery while tracked was still PRE; `seal` then
proved the tracked refresh/restore, projection, and exact 1,795,470-byte body
accounting. `verify` now reproduces the immutable aggregate receipt without
opening or writing Ghidra. See the historical
[preparation runbook](../reverse-engineering/binary-analysis/pc-function-body-fragment-ghidra-live-promotion-preparation-2026-08-14.md)
and completed
[live-promotion report](../reverse-engineering/binary-analysis/pc-function-body-fragment-ghidra-live-promotion-2026-08-14.md).

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
python ./tools/re_pc_native_source_coordinates_v3_tests.py
python ./tools/re_pc_native_source_coordinates_v3_tests.py --prove-can-fail
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
  **Standing caveat: TTD recording is Windows-only and requires an elevated
  token.** The current Omarchy host cannot record, and the prepared Windows VM
  is not yet activated. Once activated and provisioned with TTD, start an
  unattended campaign from one elevated guest shell; the manual attach helper
  raises UAC for an individual capture.
- `ttd_coverage_index.py` (P5) — the offline cross-trace query root over the
  retained exec-coverage receipts. `build` walks an explicitly supplied
  receipts root. `G:\bea-ttd` is the historical Windows corpus path, not a
  current Linux route; recovered evidence subsets live under the canonical
  repo-local `local-lab/`, and no claim is made here that the full historical
  corpus is present. The tool validates every `coverage.jsonl`
  fail-closed (per-row byte/VA/RVA arithmetic, module-span domain bounds,
  exact gap accounting and required controls, full module identity, summary
  agreement, assertion re-derivation, trace-name and module-base uniqueness,
  and unreadable-subtree refusal), and emits one deterministic, byte-stable
  index whose `receipt_set_sha256` binds every consumed receipt file hash and
  whose `content_sha256` binds the complete readback. Every per-trace receipt
  path in an index is canonically validated before membership — relative,
  forward-slash, normalized, no Windows drive/UNC/rooted or parent syntax,
  basename exactly `coverage.jsonl` — so a re-bound path cannot redirect an
  answer to bytes the index's hashes do not describe. `query` deeply
  revalidates that index before answering arbitrary VA/RVA lists with
  per-address trace membership plus must-hit / must-miss controls; it launches
  no debugger and never records. The preregistered first question (which
  retained traces contain any of the nine FireLock PCs, with ApplyDamage as
  must-hit and current-time BSS as must-miss) is answered in PROGRAM.md P5.
  Focused gate: `python ./tools/ttd_coverage_index_tests.py` (registered in
  `npm run test:tools`).
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
