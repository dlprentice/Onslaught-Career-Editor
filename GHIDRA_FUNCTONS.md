# Battle Engine Aquila's 7,555-function Ghidra corpus is deeply mapped, not atom-complete

Status: active canonical synthesis of the current executable-analysis state; raw
machine exports remain the address-level evidence behind this human-readable
master
Last updated: 2026-07-29
Verdict: **The Steam executable is no longer a black box: its current maintainer
database contains 7,555 function entries, every one of 2,127 RTTI vtable targets
is a function start, the major game/runtime subsystems have been mapped, and
several finite registries are completely decoded. It is not yet atom-complete.
Of 6,376 human-namable functions, the current pinned-source grader still places
1,867 (29.3%) in its three weak/unsupported naming cohorts; 1,144 current
functions never passed through the 2026 fullpass; the
function-note corpus gives a clear identity entry to only 1,027 functions; and
86 shipped MissionScript handlers are not functions in Ghidra at all. This file
is the integrated master truth and work queue, not a claim that those measured
gaps are solved.**
Evidence: MEASURED — read-only inspection of the repo-designated unpatched
executable baseline, current
7,555-row Ghidra readback, tracked Ghidra snapshot, all 322 function-note
documents, all 514 fullpass shards and 18 closeouts, current grading/tooling
code, pinned source, finite shipped registries, copied-runtime captures, D3D9
proxy evidence, and the Level 100 TTD trace. SOURCE-backed and INFERRED claims
are labelled where they carry less authority than shipped bytes or controlled
runtime observation.
Specimen: `BEA.exe.original.backup`, 2,506,752 bytes, MD5
`3b456964020070efe696d2cc09464a55`, SHA-256
`74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`
(`local-lab/safe-copy-bea-pristine/`, read-only). Runtime observations name the
separate force-windowed copied target and hash when used. The installed retail
executable is locally patched and is never the static specimen.

“Baseline” here means the repository-designated unpatched retail specimen. It
is pristine only relative to the project's patch catalog; this research does
not establish its Steam depot identity.

---

## Purpose and reading contract

This is the single narrative master for Ghidra and executable reverse
engineering. It combines the useful conclusions currently distributed across
the database, exports, ledgers, function notes, source crosswalks, static
contracts, runtime traces, and reconstruction investigations. The distinctions
between those stores appear here only when they change what may safely be
claimed.

The address is the primary key. Names move, and six current names are duplicated
at two addresses. A name without an address and an evidence grade is not a
durable fact.

This file deliberately does not paste the 7,555-row raw inventory or millions
of bytes of debugger/proxy output into prose. Doing so would create a stale
second database and bury the actual reasoning. Instead it records every global
denominator, all known conflict classes, the important finite tables, the
system-level address atlas, measured runtime behavior, exact open questions, and
the raw evidence location needed to reproduce an individual row.

The companion [`BEA_DATA.md`](BEA_DATA.md) is the canonical reconnaissance map
of the 5,515-file installed corpus. This file explains the executable that
loads, interprets, simulates, and renders that corpus.

### Evidence vocabulary

| Grade | Meaning here |
| --- | --- |
| **MEASURED / STATIC** | Read from the repo-designated unpatched baseline image, current Ghidra readback, shipped data, byte comparison, or controlled copied-runtime capture. |
| **RTTI-backed** | Owner/class identity follows MSVC RTTI in the shipped image. Strong for class ownership, not automatically the original method name. |
| **SHIPPED-DATA** | A shipped registry/string binds a developer-authored token to an exact address. This is stronger naming evidence than behavior alone. |
| **SOURCE** | Pinned GPL reference source establishes architecture, ownership, algorithm, or intent. The Steam image/runtime decides released behavior. |
| **RUNTIME** | Observed on the named copied target and bounded to the captured path, level, frame, or call population. |
| **INFERRED** | Best current interpretation of stronger facts; requires a stated falsifier. |
| **UNKNOWN** | Not established. The needed static read, capture, or test is stated where material. |
| **HISTORICAL** | Correct only for a dated database/export or retained as provenance; not current identity authority. |

### Current authority in one sentence

Use the 2026-07-28 7,555-row readback for current function metadata, the
unpatched baseline image for bytes and shipped tables, RTTI/source strings for identity evidence,
controlled copied-runtime work for behavior, and this document for the reviewed
synthesis and open queue.

### Master map

- [Executive state](#executive-state)
- [Specimens, projects, and database state](#specimens-projects-and-database-state)
- [Function population and audit history](#function-population-and-audit-history)
- [Current naming evidence](#current-naming-evidence)
- [System architecture and address atlas](#system-architecture-and-address-atlas)
- [Controlled Level 100 runtime evidence](#controlled-level-100-runtime-evidence)
- [D3D9 proxy and visual-state findings](#d3d9-proxy-and-visual-state-findings)
- [Executable patch atlas](#executable-patch-atlas)
- [Function-note corpus](#function-note-corpus-depth-coverage-and-contradictions)
- [Ghidra tooling and mutation safety](#ghidra-tooling-and-mutation-safety)
- [Canonical progress queue](#canonical-progress-queue)
- [MissionScript registry](#appendix-a-complete-144-entry-missionscript-native-registry)
- [PhysicsScript value maps](#appendix-b-complete-physicsscript-value-maps)
- [Function-note owner census](#appendix-c-function-note-owner-census)
- [Superseded claims](#appendix-d-superseded-claims-that-must-not-return)
- [Evidence map](#appendix-e-evidence-map)

## Executive state

| Question | Current exact answer |
| --- | --- |
| Static retail specimen | 2,506,752-byte x86 PE, SHA-256 `74154bfa…e7750`; D3D9 retail build |
| Latest readback | 7,555 functions; 3,181,359-byte TSV; SHA-256 `45cba656…0a462` |
| Current distinct function names | 7,549; six names occur at two addresses |
| Explicit `FUN_*` names | 366 |
| MSVC `Unwind@*` funclets | 1,179 |
| Thunks | 98 |
| Functions with plate comments | 6,947 |
| Functions without a plate comment | 608 |
| Functions with at least one tag | 5,919 |
| Current human-namable denominator | 6,376, excluding the 1,179 compiler EH funclets |
| Pinned-source grader's three-cohort weak/unsupported naming residual | 1,867 / 6,376 = 29.3% |
| RTTI vtable target coverage | 2,127 / 2,127 targets are current function starts |
| Fullpass population | 6,411 functions reviewed in W001–W018 |
| Current functions never in that fullpass | 1,144 / 7,555 = 15.1% |
| Clear identity coverage in the 322 function notes | 1,027 / 7,555 = 13.594% |
| Any exact entry-address mention in those notes | 1,285 / 7,555 = 17.009% |
| MissionScript native registry | 144 / 144 names and 144 distinct handlers recovered |
| Mission handlers absent as Ghidra functions | 86 |
| PhysicsScript corpus | 777 statements; every used value id closes against its factory |
| Level 100 unit-factory calls in the valid TTD trace | 33 = 28 structures + 2 ambient aircraft + 3 Target Tanks |
| Current honest conclusion | Broad architectural recovery; deep islands of exact semantics; substantial address-level work remains |

Nothing in the table equates `USER_DEFINED`, a comment, a tag, a fullpass
`confirm`, or a matching source token with semantic correctness. Those are
different measurements.

## Specimens, projects, and database state

### Executable identities

| Role | Path / identity | Size | SHA-256 | Use |
| --- | --- | ---: | --- | --- |
| Unpatched static baseline | `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` | 2,506,752 | `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750` | Static bytes, PE, strings, tables, disassembly |
| Runtime capture target | `local-lab/safe-copy-bea-pristine/BEA.exe` | 2,506,752 | `E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4` | Baseline plus the four-byte force-windowed patch |
| Live installed executable | `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe` | 2,506,752 | `E78818292A1DBE31DC6987C71665857DE3A8CF3E7619745689D74C7DA829C918` | Never use for static truth; intentionally patched |
| Installed unpatched backup | same installation, `BEA.exe.original.backup` | 2,506,752 | `74154BFA…E7750` | Hash-equivalent baseline; read-only |

The live installed executable differs from the baseline at 28 bytes across four
catalogued patch sites. A screenshot or byte claim from it can therefore be a
faithful measurement of a local modification rather than retail behavior.
[`retail-specimen-baseline.md`](reverse-engineering/binary-analysis/retail-specimen-baseline.md)
and
[`retail-capture-provenance-2026-07-25.md`](reverse-engineering/binary-analysis/retail-capture-provenance-2026-07-25.md)
own the durable specimen warning.

### Ghidra stores

| Store | Exact state | Correct use |
| --- | --- | --- |
| Tracked project | `reverse-engineering/ghidra/BEA.gpr` + `BEA.rep/`; snapshot 2026-07-18; 19 payload files, 177,064,839 bytes; reviewed with Ghidra 12.0.3 | Distributable reviewed snapshot; may lag current work |
| Tracked Program objects | `BEA.exe` and `BEA_Widescreen.exe` | Do not silently assume an export came from the unpatched baseline Program |
| Live maintainer project | `C:\Users\david\Ghidra\Projects`, active Ghidra 12.1.2 | Current working database; mutation requires separate authority |
| Latest live readback | `local-lab/ghidra-from-trace-2026-07-28/inv-AFTER-functions.tsv` | Current function metadata used by this document |
| Promoted tracked name table | `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv`, 7,555 rows, SHA-256 `2dfe0b97…f0b84` | Durable address/name table, one rename behind live |
| Fullpass discovery corpus | `reverse-engineering/binary-analysis/ghidra-fullpass-findings/` | Dated 6,411-function reviews; never a live name oracle |
| Function-note corpus | `reverse-engineering/binary-analysis/functions/` | Deep sparse semantic notes; not complete population coverage |

Fresh read-only exports in this research pass remove an important ambiguity:

- The tracked snapshot contains exactly 6,411 functions, 546,729 instructions,
  48,581 defined-data items, 3,922,085 undefined-data items, and 5,223
  user-defined symbols. Its exported function TSV has SHA-256
  `8BBB7444893E174F36CBC0766D4CD8F0B965CFEC4E8C55B944C100E71BF381D9`.
- Its 6,411 address/name pairs are exactly the W001–W018 population.
- All 91 accepted rows in the July 13 reviewed-correction plan match their
  corrected name, full signature, and full comment in the tracked snapshot.
  The rejected `0x004dac90` row matches its retained current values. The July
  13 corrections are therefore demonstrably present in the tracked snapshot.
- The current live export is byte-identical to the July 28 saved readback:
  SHA-256 `45CBA656E73DAB3E1033256F2B6B7B5BCA08E4FE34FD5D1CC401B34F53D0A462`.
  There has been no later live-database drift.
- Relative to the tracked snapshot, live adds 1,144 functions and removes none.
  Across their common 6,411 addresses there are no body-range, byte-count,
  instruction-count, ABI, parameter-count, or boundary differences. There are
  370 name/signature-string differences, one `nameSource` difference, at least
  1,175 changed comment lengths, and 793 changed tag sets.

The tracked name table differs from the latest live readback at one known row:
`0x00536cd0 FUN_00536cd0` became `IScript__SpawnThing` on 2026-07-28. The
whole-database before/after diff reports zero created functions, zero destroyed
functions, zero moved bounds, one changed name, and one changed rendered
signature—the signature change is only the embedded function name. Seventeen
comments were also applied and read back exactly.

The historical `BEA_Widescreen.exe` Program corresponds to a 2,506,752-byte
patched image described as SHA-256
`67994E5F5F418CCA2ED253AB643112AC3A82EA1647E8172027EB9C9CC7B37F61`,
191 changed bytes across 28 regions. That association is documented by the
widescreen analysis; its import hash was not freshly re-read from the Ghidra
database in this pass.

### PE and listing shape

The current Ghidra program report contains:

| Metric | Value |
| --- | ---: |
| Functions | 7,555 |
| Listing instructions | 549,864 |
| Defined data items | 48,586 |
| Undefined data items | 3,912,368 |
| User-defined symbols | 5,999 |
| Analysis symbols | 18,006 |
| Imported symbols | 907 |
| Other/default symbols | 61,692 |
| Relocations | 0 |

Memory blocks:

| Block | Range | Size | Executable |
| --- | --- | ---: | --- |
| Headers | `0x00400000–0x00400fff` | 4,096 | no |
| `.text` | `0x00401000–0x005d7fff` | 1,929,216 mapped bytes | yes |
| `.rdata` | `0x005d8000–0x00621fff` | 303,104 | no |
| `.data` | `0x00622000–0x009d4613` | 3,876,372 | no |
| `.rsrc` | `0x009d5000–0x009d7fff` | 12,288 | no |
| `tdb` | `0xffdff000–0xffdfffff` | 4,096 | no |

The older coverage calculation uses the PE `.text` virtual-size denominator
1,929,117, not the mapped block's page-rounded 1,929,216. Do not mix those two
denominators.

The function inventory's summed memberships are 1,704,494 body bytes and
519,698 function-owned instruction rows. Ghidra's program report counts 549,864
listing instructions. None of those three figures is a fresh exact `.text`
coverage percentage: function bodies can be fragmented or overlap, listing
instructions include code outside functions, and the current 7,555-function
population has not been re-exported through the old byte-coverage proof.

Body topology is:

| Body ranges per function | Functions |
| ---: | ---: |
| 1 contiguous range | 7,488 |
| 2 ranges | 53 |
| 3 ranges | 12 |
| 21 ranges | 2 |

Thus 67 functions are non-contiguous. Any tool that treats `[bodyMin, bodyMax]`
as continuous can falsely assign an address in a gap to that function.

Metadata-source and calling-convention distributions:

| Dimension | Exact current distribution |
| --- | --- |
| Name source | USER_DEFINED 5,918; ANALYSIS 1,230; DEFAULT 406; IMPORTED 1 |
| Signature source | USER_DEFINED 6,394; ANALYSIS 1,139; IMPORTED 22 |
| Calling convention | `__thiscall` 2,777; `__cdecl` 1,949; `__fastcall` 1,391; `__stdcall` 1,088; unknown 350 |

### Six duplicate current names

Names are not unique keys:

| Current name | Addresses |
| --- | --- |
| `CActor__SetFieldD0ToNow_00402010` | `0x00402010`, `0x00447b50` |
| `CDXTexture__EnsureLoaded` | `0x0053a040`, `0x00557060` |
| `CDXTexture__InitMappedFileContext` | `0x0057cc53`, `0x0058864a` |
| `CSPtrSet__Clear` | `0x0042f220`, `0x004e5c60` |
| `PCPlatform__ResetAsyncMusicStream` | `0x00515360`, `0x005285b0` |
| `Vec3__NormalizeInPlace` | `0x00406d50`, `0x004c7900` |

Some are real shared/duplicate implementations; some are owner conflicts. They
must be adjudicated by bytes, references, RTTI, and behavior, never collapsed by
name.

## Function population and audit history

### Population timeline

| Date / wave | Population | What changed | What the number proves |
| --- | ---: | --- | --- |
| Before July re-audit | 5,771 was quoted in older documentation | Undated historical inventory | Nothing current |
| 2026-07-13 closeout | 6,411 | Trusted exports reconciled; 92 correction targets reviewed | Complete accounting of that inventory |
| R4 boundary work | 6,433 | 22 functions created | Confirmed missing entries |
| Gap recovery | 6,969 | 536 aligned `INSTRUCTION_NO_FUNCTION` candidates created | Static classifier and Ghidra listing agreed |
| RTTI vtable recovery | 7,549 | 580 vtable targets created | Every recovered address is a real dispatch target |
| Aggressive Instruction Finder | 7,555 | 6 functions created | Six additional analyzer-supported entries |
| Decompiler Parameter ID | 7,555 | No function-count change; 1,139 DEFAULT signature sources became ANALYSIS | Analysis metadata only |
| 2026-07-28 trace apply | 7,555 | One rename, 17 comments | No body or boundary change |

The 2026-07-13 correction review found a 459-address metadata delta, reduced it
to 92 unique correction targets, applied 91, and rejected one proposed ABI
change. `0x004dac90` ends in `RET 0x4`, not `RET 0x8`. The accepted write
changed 26 names, 88 comments, and nine rendered signatures. Only
`0x0050b9c0 CWorld__LoadWorld` received a structured prototype change: three
stack arguments, confirmed by `RET 0x0c`.

Two hashes in that evidence describe different moments:
`c61ced…` in the JSON is the pre-apply live-snapshot input hashed while the plan
was built; `0fc346…` in the closeout is the final post-apply readback. They are
not conflicting claims.

### The 6,411-function fullpass

W001–W018 reviewed every function in the 2026-07-23 population twice: 257
primary shards and 257 adversarial shards, plus 18 closeouts.

Primary findings:

| Verdict | Count |
| --- | ---: |
| `ok` | 5,004 |
| `needs_tags` | 274 |
| `needs_name` | 171 |
| `needs_comment` | 194 |
| `possible_missing_neighbor` | 275 |
| `needs_signature` | 466 |
| `overclaim` | 15 |
| `inconclusive` | 3 |
| `needs_boundary` | 9 |
| **Total** | **6,411** |

Adversarial dispositions:

| Disposition | Count |
| --- | ---: |
| `confirm` | 5,702 |
| `dispute` | 121 |
| `upgrade_severity` | 508 |
| `downgrade` | 80 |
| **Total** | **6,411** |

There is no official reconciled post-adversarial verdict total. The primary and
adversarial tables answer different questions and must not be added or
substituted for one another.

The pass exported 468,804 instruction rows and verified every row against the
unpatched baseline executable with zero byte mismatches. It found 6,351 fully clean
functions, 60 flagged functions, six overlapping bodies, and the `_strchr`
anomaly whose body begins below its recorded entry. This is strong proof of the
exported bytes and modeled bodies, not of the semantic names.

At that time, function-body instruction bytes covered 1,539,953 of the
1,929,117-byte PE `.text` virtual size: 79.8268327%. That is a dated 6,411-body
measurement, not current coverage.

The uncovered-run classifier then measured 2,924 runs of at least eight bytes:

| Class | Runs | Bytes |
| --- | ---: | ---: |
| CODE | 643 | 300,307 |
| UNKNOWN | 621 | 51,189 |
| PAD | 1,536 | 17,736 |
| PTR_TABLE | 37 | 9,403 |
| DATA | 87 | 5,053 |
| **Total** | **2,924** | **383,688** |

Of 568 aligned code candidates, Ghidra independently reported 536 as
`INSTRUCTION_NO_FUNCTION`, 20 already present from R4, nine undefined, and
three defined-data starts. The 536 agreed candidates were created. The 621
UNKNOWN runs were deliberately left alone: good linear decode without an entry
reference does not prove a function boundary.

Current drift matters:

- All 6,411 fullpass addresses still exist.
- 370 of their names differed from the live 2026-07-27 readback.
- 247 of those stale names had received the strongest `ok` + `confirm`
  combination.
- 1,144 current functions never appeared in W001–W018.
- 107 adversarial shards name no export root.
- 110 adversarial shards do not identify their paired primary shard.

All 370 name drifts are now attributable when both historical map owners are
joined, rather than only the maps under `local-lab/re-ledger/`:

| Mutation source | Distinct original-fullpass addresses |
| --- | ---: |
| RTTI reprefix wave | 330 |
| Rename wave 13/14 union | 13 |
| Proven-false demotions | 2 |
| Fullbreadth `t3_name_renames_28.map` | 24 |
| R1 map (`0x004062d0`) | 1 |
| **Total, disjoint** | **370** |

The older fullpass README's “25 UNKNOWN” means “not found in one map
directory,” not globally unexplained. That residual is fully reconciled by the
fullbreadth maps and apply evidence.

The fullpass is therefore a deep dated discovery record, not current identity
authority. See its corrected
[`README.md`](reverse-engineering/binary-analysis/ghidra-fullpass-findings/README.md).

The later fullbreadth correction campaign closed the following reviewed lane
populations. A lane count is not necessarily a mutation count:

| Lane | Reviewed population | Exact closeout |
| --- | ---: | --- |
| `needs_signature` | 511 | Live dual-CLEAR comment/tag outcomes; not 511 structured-signature rewrites |
| `needs_name` | 228 | 228 live comments; a separately counted 28-name rename map was applied live under dual CLEAR |
| `needs_tags` | 234 | 20 live process-tag scrubs + 214 reviewed `KEEP` outcomes |
| `overclaim` | 25 | 24 live plate rewrites + one name-level quarantine later resolved by the `0x004062d0` R1 rename |
| `needs_comment` | 52 | 52 live comment outcomes |
| `needs_boundary` | 12 | 12 live dual-CLEAR comment/tag outcomes |
| `possible_missing_neighbor` | 322 | Plan dual CLEAR: 250 `QUARANTINE`, 72 `KEEP`, zero rewrites/functions invented |
| `T0` | 3 | Plan dual CLEAR: all three quarantined as inconclusive |

These are historical campaign outcomes, not current queues or standing
authorization. The campaign changed metadata, not executable bytes or function
bodies.

### Aggressive analyzer result

Seven of the nine analyzers proposed for recovery were already enabled. Isolated
canaries tested Aggressive Instruction Finder, Decompiler Parameter ID,
address/switch-table aggression, external-parameter propagation, a variadic
override, and a combined pass.

- Address/switch aggression was a no-op.
- In the promoted RTTI→Aggressive Instruction Finder order, Aggressive
  Instruction Finder created six functions totaling exactly 1,259 body bytes
  (596, 14, 518, 42, 42, and 47); those functions entered `UNNAMED`. The earlier
  canary's 4,404-byte result covered 14 application loose-code runs and is a
  different population.
- Decompiler Parameter ID changed exactly 1,139 DEFAULT signature-source rows
  to ANALYSIS and touched none of 6,394 USER_DEFINED signature rows.
- Propagate External Parameters correctly exposed `0x00516ed0` as the DirectSound
  enumeration callback `pDSEnumCallback_00516ed0`, but polluted 69
  USER_DEFINED symbols and was rejected for promotion.
- No tested pass reduced the pinned-source grader's three-cohort naming
  residual.

This experiment is complete. Re-running “aggressive analysis” as if it were an
untried lever would repeat measured work.

### RTTI vtable recovery and naming wave

The 580-function creation wave was deliberately run before the analyzer passes:

- 574 targets were listing instructions with no function;
- six were undefined bytes with valid entry evidence/prologues;
- total new body membership was 85,006 bytes;
- median body size was 46 bytes;
- none was shorter than four bytes;
- owner grading immediately after creation found 545 resolved owners, 33
  ambiguous owners, and two conflicts.

The subsequent owner-prefix wave named 533 of those 580 with the honest form
`Owner__VFunc_slot_address`. Forty-seven were held:

| Hold reason | Rows |
| --- | ---: |
| Ambiguous RTTI owner | 33 |
| Conflict thunk | 2 |
| Secondary-vtable slot whose primary slot number would mislead | 9 |
| Duplicate/unstable table reading | 1 |
| Identical-body collision | 2 |

Of the 533 names, 497 use the uniquely resolved owner directly and 36 use an
inherited owner resolution. Forty-six have independent exact `__FILE__`
agreement in their own bodies. The other 487 do not have independent
developer-method-name evidence; their suffix explicitly preserves that
unknown.

The 533-row increase in `RTTI_CONFIRMED` is tautological because the names were
constructed from the same RTTI oracle the grader checks. Only the 46
`__FILE__` agreements are independent corroboration. A byte-level duplicate
check found 34 identical-body groups / 87 functions program-wide; the two
wave candidates involved were withheld.

## Current naming evidence

The current grading command is:

```powershell
py -3 tools/re_ledger.py `
  --binary local-lab/safe-copy-bea-pristine/BEA.exe.original.backup `
  --inventory local-lab/ghidra-from-trace-2026-07-28/inv-AFTER-functions.tsv `
  --reference-source references/Onslaught
```

The `--reference-source references/Onslaught` flag is part of the measurement.
Without it, the residual has a different meaning and value.

### Current grade distribution

| Grade | Functions | Meaning / caution |
| --- | ---: | --- |
| `RTTI_CONFIRMED` | 1,933 | Prefix agrees with a resolved RTTI vtable owner; method token may still be inferred |
| `RTTI_CONFLICT` | 27 | Current prefix conflicts with the resolved owner |
| `RTTI_AMBIGUOUS` | 100 | More than one plausible RTTI owner |
| `OWNER_PREFIX_MISSING` | 14 | Owner evidence exists but current label lacks it |
| `BINARY_STRING` | 218 | Name/token exists in shipped image |
| `SOURCE_BACKED` | 528 | Exact source token under the pinned source rules |
| `UNNAMED_RTTI_OWNER` | 12 | `FUN_*` with one resolved owner |
| `UNNAMED_RTTI_TARGET` | 41 | Unnamed vtable target without one resolved owner |
| `UNNAMED` | 313 | Other explicit `FUN_*` entries |
| `COMPILER_EH_FUNCLET` | 1,179 | MSVC unwind machinery; excluded from human-namable denominator |
| `PE_IMPORT` | 36 | Import boundary |
| `RESIDUAL_FREEFORM` | 98 | Unsupported free-form label |
| `VTABLE_VA_IN_BODY` | 188 | Label evidence comes from a vtable VA found inside the body, not proven ownership |
| `IMAGE_TYPE_TOKEN` | 1,099 | Type token appears in image, method relation unproven |
| `IMAGE_TYPE_SUBSTRING` | 668 | Weaker substring relation |
| `INVENTED_PREFIX` | 1,101 | Prefix has no accepted local evidence under the grader |
| **Total** | **7,555** |  |

The `UNBACKED` aggregate is 4,369, but 1,179 are compiler EH funclets and 36 are
imports. The pinned-source grader's deliberately conservative three-cohort
residual is:

```text
6,376 human-namable functions
- 4,509 carrying accepted image/source evidence or an explicit unresolved RTTI/unnamed grade
= 1,867 in INVENTED_PREFIX (1,101) + IMAGE_TYPE_SUBSTRING (668) + RESIDUAL_FREEFORM (98)
= 29.3%
```

That is not equivalent to “no image-local evidence.” `IMAGE_TYPE_SUBSTRING`
does carry weak occurrence evidence, while a source-backed row may lack an
image-local token and still fall outside this residual. The number is meaningful
only under the exact grader command and pinned-source run above.

The 2026-07-28 `SpawnThing` rename moved one row from `UNNAMED` to
`IMAGE_TYPE_TOKEN`. It did **not** reduce the 1,867-function three-cohort
residual. The trace-apply
note predicted `1,867 → 1,866` arithmetically without rerunning the grader; the
fresh grader disproves that prediction.

`USER_DEFINED` is a Ghidra source flag. It means a human/script wrote the row,
not that the row is correct. `bodyDigest` in
`ExportFullFunctionInventory.java` hashes the address-range description, not
function bytes; equal digests do not prove identical code.

### RTTI and shipped source-path ground truth

Direct pristine-image scanning finds:

| Item | Count |
| --- | ---: |
| MSVC RTTI type descriptors | 667 |
| Classes with recovered hierarchy | 656 |
| Complete Object Locators | 724 |
| Vtables | 733 |
| Vtable slots | 11,777 |
| Distinct `.text` slot targets | 2,127 |
| Targets that are current function starts | 2,127 |
| Targets with a resolved owner | 1,982 |
| Ambiguous owner targets | 145 |
| Shipped source-path strings | 166 paths / 164 basenames |
| Source-path references | 1,870 references across 969 functions |

The PE debug directory is stripped and no PDB is present. That does not mean
“the binary has no symbols”: RTTI, class tokens, command registries, diagnostic
strings, and `__FILE__` paths are substantial shipped identity evidence.

The pinned source is commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`, containing 52 `.cpp` and 54 `.h`
files. It is incomplete and not independently buildable: 202 quoted includes
among 254 distinct names are absent. It remains valuable architecture and
algorithm evidence; it is not a substitute for the Steam binary.

The apparent library region above `0x00555000` is mixed application, compiler,
CRT, codec, math, and rendering code. It is not a clean authorship boundary.

### RTTI conflict queue: all 27 current rows

| Address | Current name | Resolved RTTI owner |
| --- | --- | --- |
| `0x00404110` | `CAnimal__SetThingTypeMask80000001` | `CComplexThing` |
| `0x00426900` | `CCollisionSeekingRound__CheckCollisionFlags` | `CCollisionSeekingThing` |
| `0x00426a00` | `CCollisionSeekingRound__ProcessMapWhoCollisionSweep` | `CCSPersistentThing` |
| `0x00426a20` | `CCollisionSeekingRound__MarkDelayedCollisionReady` | `CCSPersistentThing` |
| `0x004439c0` | `CDestroyableSegment__SharedVFunc_08_HandleChildBreak` | `CDestroyableExtraSegment` |
| `0x00447b50` | `CActor__SetFieldD0ToNow_00402010` | `CDropship` |
| `0x004599a0` | `CFEPMultiplayerStart__SubObj8848__Init` | `CFEPE3LevelSelect` |
| `0x00459a60` | `CFEPMultiplayerStart__SubObj8848__ActiveNotification` | `CFEPE3LevelSelect` |
| `0x00459aa0` | `CFEPMultiplayerStart__SubObj8848__TransitionNotification` | `CFEPE3LevelSelect` |
| `0x00459b00` | `CFEPMultiplayerStart__SubObj8848__Process` | `CFEPE3LevelSelect` |
| `0x00459c10` | `CFEPMultiplayerStart__SubObj8848__ButtonPressed` | `CFEPE3LevelSelect` |
| `0x00459e50` | `CFEPMultiplayerStart__SubObj8848__RenderPreCommon` | `CFEPE3LevelSelect` |
| `0x00459ee0` | `CFEPMultiplayerStart__SubObj8848__Render` | `CFEPE3LevelSelect` |
| `0x004bb450` | `CMusic__Play` | `CPCMusic` |
| `0x004dfa40` | `CUnit__VFunc08_InitAndAddToWorld` | `CSimpleBuilding` |
| `0x004e9600` | `CSquadNormal__VFunc_20_004e9600` | `CNormalSquad` |
| `0x004e96f0` | `CSquadNormal__VFunc_21_004e96f0` | `CNormalSquad` |
| `0x004e9f00` | `CSquadNormal__VFunc_52_004e9f00` | `CNormalSquad` |
| `0x004ef100` | `CUnit__VFunc64_SpawnConfiguredPickupThreeTimes` | `CSubmarine` |
| `0x00515360` | `PCPlatform__ResetAsyncMusicStream` | `CPCMusic` |
| `0x0051b640` | `CFEPMultiplayerStart__SubObj4034__Init` | `CFEPIntro` |
| `0x0051b660` | `CFEPMultiplayerStart__SubObj4034__ButtonPressed` | `CFEPIntro` |
| `0x0051b6b0` | `CFEPMultiplayerStart__SubObj4034__Process` | `CFEPIntro` |
| `0x0051be70` | `CFEPMultiplayerStart__SubObj4034__InitRuntimeState` | `CFEPIntro` |
| `0x00527d00` | `CReconnectInterface__VFunc_07_00527d00` | `CRenderMethod` |
| `0x0053a040` | `CDXTexture__EnsureLoaded` | `CBLTexture` |
| `0x00555600` | `CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay` | `CSnow` |

These are review targets, not automatic renames. A vtable can legitimately
point to an inherited/shared implementation whose current conceptual owner is
different from the table owner.

### Six byte- or RTTI-refuted names still live

These are not merely weak names; the current evidence contradicts them.
They remain unchanged because renaming graded rows is a separately reviewed
ledger mutation.

| Address | Current live name | Refutation / safer interpretation |
| --- | --- | --- |
| `0x004e9600` | `CSquadNormal__VFunc_20_004e9600` | `CSquadNormal` has no image RTTI; vtable owner is `CNormalSquad` |
| `0x004e96f0` | `CSquadNormal__VFunc_21_004e96f0` | Same transposed/invented owner |
| `0x004e9f00` | `CSquadNormal__VFunc_52_004e9f00` | Same transposed/invented owner |
| `0x00527d00` | `CReconnectInterface__VFunc_07_00527d00` | Only owning vtable is `CRenderMethod` |
| `0x004eaae0` | `CRelaxedSquad__VFunc_07_004eaae0` | Owner is real, but the primary-vtable slot is 52, not 7; the grader validates prefixes, not slot suffixes |
| `0x004e36c0` | `CSpawnerThng__FindSpawnerByName` | One-argument `__cdecl`; walks the thing-definition registry at `DAT_008553fc`, compares record `+0xb0`, and returns ordinal/`-1`. It has no `CSpawnerThng` receiver. Proposed semantic name: `ResolveThingDefinitionOrdinalByName`. |

This is direct proof that “graded,” `RTTI_CONFIRMED`, and even a plausible
semantic name do not mean “correct.”

### Unnamed RTTI-owner queue

Twelve `FUN_*` rows have a uniquely resolved class owner:

| Address | Owner |
| --- | --- |
| `0x00405960` | `CCockpit` |
| `0x004060b0` | `CBattleEngine` |
| `0x0041a1f0` | `CViewPointCamera` |
| `0x0041a980` | `CControllableCamera` |
| `0x0041b0a0` | `CControllableCamera` |
| `0x00425430` | `CCockpit` |
| `0x004254f0` | `CCockpit` |
| `0x0043ea70` | `CCutscene` |
| `0x0043ea80` | `CCutscene` |
| `0x004c4a00` | `CParticleDescriptor` |
| `0x004f6540` | `CTree` |
| `0x0050f5f0` | `CRelaxedSquad` |

Forty-one additional unnamed vtable targets remain owner-ambiguous or
unresolved:

```text
004098b0 0040ac30 00415a90 004164b0 00418410 00418eb0 00418ed0
004198b0 0041b040 0041b060 00432af0 00432b00 00434120 0043ea50
0044fd70 0048dbe0 004c4a40 004ceed0 004df500 004e8cd0 004ead60
004f4820 0050e8b0 0050e8c0 0050e960 0050ea20 0050eaf0 0050ffc0
0052d950 0052d990 0052da00 0052dac0 0052db10 0052dbf0 0052dc80
0052dcd0 0052dd20 0052de00 0052de90 0052f410 0052f660
```

### Highest-value large unnamed application bodies

| Address | Bytes / instructions | Current evidence / next action |
| --- | ---: | --- |
| `0x00456190` | 1,056 / 357 | Remap-capture callback; already has a 661-character comment. Recover owner/name from frontend/control callsites. |
| `0x00470cc0` | 1,009 / 176 | No plate comment. Trace callers and dominant globals first. |
| `0x0041a980` | 841 / 257 | RTTI owner `CControllableCamera`. Slot semantics and callsites should name it. |
| `0x00516ed0` | 774 / 235 | External-parameter canary identified a DirectSound enumeration callback; promote only with a bounded manual prototype. |
| `0x004254f0` | 621 / 194 | RTTI owner `CCockpit`. |
| `0x004595b0` | 596 / 184 | Frontend region; no plate comment. |
| `0x004060b0` | 531 / 168 | RTTI owner `CBattleEngine`. |
| `0x00537ad0` | 344 / 113 | Shipped command `Print`; one of 15 exact weak MissionScript rows. |
| `0x00536070` | 300 / 92 | Shipped command `GetDistToObj`. |
| `0x005365c0` | 250 / 77 | Shipped command `GetSquad`. |
| `0x00537c70` | 249 / 63 | Shipped command `Pause`. |
| `0x005353a0` | 215 / 71 | Shipped command `GetRatioBattleLineNodes`. |

The 55 current functions prefixed `CHud`, `CDXCompass`, `CDXBattleLine`, or
`CHudComponent` fall under `INVENTED_PREFIX` because those exact class names
lack RTTI type descriptors. That proves only that no polymorphic RTTI owner by
those spellings exists; it does not prove the functional labels are false.

## System architecture and address atlas

This atlas records the strongest current model of how the executable is
organized. A row means “this address is the best current join point,” not “the
entire body, every field, and every branch is understood.”

### Platform, startup, and game loop

The retail executable is a 32-bit x86 PE linked against D3D9, DirectInput 8,
DirectSound, Bink, Ogg/Vorbis, zlib, AVI, and Winsock-era APIs. The pinned source
is D3D8-era and cannot be copied mechanically into a D3D9 behavior claim.

| Address | Current identity | Measured role |
| --- | --- | --- |
| `0x00423bc0` | `CLIParams__ParseCommandLine` | 1,504-byte / 465-instruction command-line parser |
| `0x0046c360` | `CGame__Init` | Game initialization |
| `0x0046c990` | `CGame__Shutdown` | Game teardown |
| `0x0046cdf0` | `CGame__LoadLevel` | Level-selection/load entry |
| `0x0046dc30` | `CGame__RestartLoopRunLevel` | 1,531-byte restart/run loop |
| `0x0046e910` | `CGame__Update` | 1,382-byte update path |
| `0x0046e460` | `CGame__Render` | 1,196-byte render coordinator |
| `0x0053e220` | `CDXEngine__PreRender` | Per-view/render preparation |
| `0x0053e2e0` | `CDXEngine__Render` | 2,519-byte / 646-instruction render body |
| `0x0053ecc0` | `CDXEngine__PostRender` | Post-render HUD/UI/battleline/briefing overlay coordination and cleanup |

Static call relationships establish these owners; exact scheduling, timestep,
thread behavior, and all branch effects remain runtime questions unless a
capture below states otherwise.

### Core object model

The simplified gameplay inheritance spine is:

```text
CMonitor
  └─ CThing
      └─ CComplexThing
          └─ CActor
              └─ CUnit
                  └─ CBattleEngine
```

`CMonitor` and active-reader/deletion-event machinery provide lifetime
observation. `CSPtrSet` containers are pervasive non-owning/owning registries.
`CThing__Init` registers each thing in the global set at `0x00855090`;
`CComplexThing__SetName` uses the named-thing noticeboard at `0x00855130`.

Important base operations:

| Address | Identity | Exact current facts |
| --- | --- | --- |
| `0x00401000` | `CGenericActiveReader__SetReader` | 52 bytes; monitored-reader assignment |
| `0x00401040` | `CMonitor__AddDeletionEvent` | 126 bytes; deletion-event linkage |
| `0x00406d20` | `CSPtrSet__First` | Set `+0` head, node `+0` element, node `+4` next, cursor `+8` |
| `0x004e5a80` | `CSPtrSet__AddToHead` | Global object registration helper |
| `0x004f34a0` | `CThing__Init` | Base initialization; 301 bytes / 106 instructions |
| `0x004f3fd0` | `CComplexThing__Init` | Two orientation branches into `CThing__Init` |
| `0x004f4120` | `CComplexThing__SetName` | Registers named things |
| `0x004f4230` | `CComplexThing__SetScript` | Attaches an authored script token |
| `0x004f86d0` | `CUnit__Init` | 2,850 bytes / 825 instructions |

Runtime call counts must not be divided across this inheritance chain as though
they counted the same population. The Level 100 trace's 1,579
`CThing__Init` calls include 1,481 trees and 30 waypoints, while the 33 unit
factory calls count physics-definition units only.

### World loading and creation

`CWorld__LoadWorldFile` reaches `CWorld__LoadWorld` `0x0050b9c0`, which owns
header/chunk loading, LOD initialization, authored world objects, and waypoint
loading. The function is 6,898 bytes / 2,023 instructions and has the reviewed
prototype:

```c
bool __thiscall CWorld__LoadWorld(
    void *this,
    void *mem_buffer,
    int is_base_world,
    int initialize_world_state); // RET 0x0c
```

| Address | Identity | Current conclusion |
| --- | --- | --- |
| `0x0050b9c0` | `CWorld__LoadWorld` | Executes twice in the Level 100 trace; base-world then level-world is a strong content/timing inference |
| `0x0050dcb0` | `CWorld__SpawnInitialThings` | Runs once / 14 instruction steps and makes zero factory calls; an empty world-mesh-list head is the strong inference explaining that path |
| `0x0050df80` | `CWorldPhysicsManager__CreateThingByType` | `__cdecl`, one argument: zero-based definition-registry ordinal |
| `0x004e36c0` | currently misnamed `CSpawnerThng__FindSpawnerByName` | Resolves a definition name to that ordinal |
| `0x004e5e70` | `CSquad__Init` | Makes two captured Target Tank factory calls |
| `0x005057b0` | `CWaypoint__InitAndLink` | Runs 30 times, matching 30 serialized waypoint markers |

The factory does **not** receive the class selector directly. It:

1. indexes the definition registry at `DAT_008553fc` with the caller's ordinal;
2. reads the class selector at record `+0xe0`;
3. bounds it to `0..25`;
4. dispatches through the 26-entry jump table at `0x0050e7f4`.

The related resolver/caller paths at `0x0050dd04`, `0x004e36e7`, and
`0x00536d81` read the definition-name pointer at record `+0xb0`; the factory at
`0x0050df80` itself reads `+0xe0`, not `+0xb0`. Both field offsets and those
specific read sites are measured. The total definition-record size is unknown.
Applying a large Ghidra structure with
invented filler would launder ignorance into a type and is explicitly rejected.

#### Complete CreateThing selector table

Every allocation uses the shipped source literal
`C:\dev\ONSLAUGHT2\WorldPhysicsManager.cpp`.

| Selector | Alloc | Primary vptr | Secondary vptr at `obj+8` | Base construction | `__LINE__` | RTTI class |
| ---: | ---: | --- | --- | --- | ---: | --- |
| 0 | `0x26c` | `0x005e3074` | `0x005e2ffc` | `CGroundUnit__Constructor` | 75 | `CMech` |
| 1 | `0x288` | `0x005e1930` | `0x005e18b8` | `CAirUnit__ctor_base` | 87 | `CPlane` |
| 2 | `0x264` | `0x005e297c` | `0x005e2904` | `CUnit__ctor_base` | 78 | `CGroundVehicle` |
| 3 | `0x278` | `0x005e272c` | `0x005e26b4` | `CGroundUnit__Constructor`; particle link init | 79 | `CInfantryUnit` |
| 4 | `0x268` | `0x005e24dc` | `0x005e2464` | `CUnit__ctor_base` | 80 | `CCannon` |
| 5 | `0x26c` | `0x005e228c` | `0x005e2214` | `CUnit__ctor_base` | 81 | `CBoat` |
| 6 | `0x27c` | `0x005e2038` | `0x005e1fc0` | `CAirUnit__ctor_base` | 82 | `CCarrier` |
| 7 | `0x26c` | `0x005d8eb4` | `0x005d8e3c` | `CUnit__ctor_base` | 83 | `CBuilding` |
| 8 | `0x288` | `0x005e1930` | `0x005e18b8` | `CAirUnit__ctor_base` | 87 | `CPlane` |
| 9 | `0x27c` | `0x005e2e20` | `0x005e2da8` | `CBigAirUnit__ctor_base` | 76 | `CBomber` |
| 10 | `0x288` | `0x005e2bcc` | `0x005e2b54` | `CAirUnit__ctor_base` | 77 | `CGroundAttackAircraft` |
| 11 | — | — | — | — | — | No case; returns `NULL` |
| 12 | `0x2ac` | `0x005e1dd8` | `0x005e1d60` | `CAirUnit__ctor_base` | 85 | `CDropship` |
| 13 | `0x268` | `0x005e1b84` | `0x005e1b0c` | `CUnit__ctor_base` | 86 | `CMine` |
| 14 | `0x2a8` | `0x005e16e0` | `0x005e1668` | `CUnit__ctor_base` | 88 | `CHiveBoss` |
| 15 | `0x254` | `0x005e1490` | `0x005e1418` | `CUnit__ctor_base` | 89 | `CSubmarine` |
| 16 | `0x288` | `0x005e123c` | `0x005e11c4` | `CAirUnit__ctor_base` | 90 | `CDiveBomber` |
| 17 | `0x274` | `0x005e0fe0` | `0x005e0f68` | `CGroundUnit__Constructor` | 91 | `CThunderHead` |
| 18 | `0x28c` | `0x005e0d8c` | `0x005e0d14` | `CAirUnit__ctor_base` | 92 | `CCarver` |
| 19 | `0x288` | `0x005e0b30` | `0x005e0ab8` | `CGroundUnit__Constructor` | 93 | `CGillM` |
| 20 | `0x264` | `0x005e08e0` | `0x005e0868` | `CUnit__ctor_base` | 94 | `CSentinel` |
| 21 | `0x26c` | `0x005e0684` | `0x005e060c` | `CGroundUnit__Constructor` | 95 | `CWarspite` |
| 22 | `0x290` | `0x005e0430` | `0x005e03b8` | `CBigAirUnit__ctor_base` | 96 | `CFenrir` |
| 23 | `0x2b8` | `0x005e01dc` | `0x005e0164` | `CUnit__ctor_base` | 97 | `CWarspiteDome` |
| 24 | `0x268` | `0x005dff8c` | `0x005dff14` | `CUnit__ctor_base` | 98 | `CPod` |
| 25 | `0x254` | `0x005dfd3c` | `0x005dfcc4` | `CUnit__ctor_base` | 99 | `CSimpleBuilding` |

### Battle Engine, player, and motion

| Address | Identity | Evidence boundary |
| --- | --- | --- |
| `0x004081c0` | `CBattleEngine__Move` | 5,522 bytes / 1,487 instructions; static high confidence |
| `0x0040a890` | Current identity `CBattleEngine__VFunc_40_0040a890`; reviewed target `CBattleEngine__Damage` | Vtable/body/prototype measured; live rename and runtime outcomes remain open |
| `0x00410c50` | `CBattleEngineJetPart__Move` | 2,171 bytes / 635 instructions |
| `0x00411630` | `CBattleEngineJetPart__HandleGroundEffect` | 1,057 bytes / 275 instructions |
| `0x00411aa0` | `CBattleEngineJetPart__GetFriction` | Returns a float tuning term |
| `0x00411b70` | `CBattleEngineJetPart__GetIsDoingSpecialAirMove` | Special-air-move predicate |
| `0x00412900` | `CBattleEngineJetPart__AutoLevel` | Auto-level path |
| `0x00412ad0` | `CBattleEngineWalkerPart__UpdateWalkCycle` | Walker-cycle update |

The missing damage entry is now explicit without pretending the live analyst
database has already changed. `CBattleEngine` vtable `0x005D89C4`, slot 40,
points to `0x0040A890`; the reviewed body runs through `0x0040AC24` and contains
`RET 0x10` at `0x0040AC22`. The reviewed prototype target is:

```cpp
void __thiscall CBattleEngine__Damage(
    CBattleEngine *this,
    float amount,
    CThing *source,
    BOOL damageShields,
    int meshPartNo);
```

The current Ghidra identity remains
`CBattleEngine__VFunc_40_0040a890`; applying the semantic rename/prototype to
the live maintainer database requires a separately reviewed mutation. Runtime
damage outcomes are not established by this static entry.

The movement crosswalk is strong static/source correspondence. Exact Steam
handling parity, morph progression, and player-input causality are not closed:
several runtime canaries failed to produce valid observations. The project must
not turn a source-shaped function into a released-behavior claim without a
capture or focused byte-tested law.

### MissionScript virtual machine

The MissionScript system is one of the best-understood finite islands.

| Component | Address / layout | Current truth |
| --- | --- | --- |
| Instruction factory | `0x0052d3d0 CAsmInstruction__SpawnFromOpcode` | Serialized opcode `0x00..0x1a`; allocation `0x0c` |
| Data-type factory | `0x0052ec60 CDataType__CreateFromType` | Type ids 1..6 |
| Native-command initializer | `0x0052ff30 ScriptCommandRegistry__InitBuiltins` | 13,429 bytes / 2,456 instructions; populates records 1..143 and writes record 0's handler at `0x0052ff74`; record 0's name/small fields are disk-initialized |
| Native dispatch | `0x0052ea40 CInstructionOP_CALL__ExecuteCall` | Index byte masked to `0xff`, record stride `0x40`, handler call |
| Script run loop | `0x00539b00 CScriptObjectCode__Run` | 10,000-operation safety limit; returns/stops under measured state rules |
| Native table | base `0x0064ce20`, stride `0x40` | name pointer `+0x00`, handler `+0x30`; fields `+0x34/+0x38/+0x3c` forwarded |

The older tracked interpretation at `0x0064ce50` was the handler-field view
mistaken for the record base. The complete current geometry is
`record = 0x0064ce20 + index*0x40`, first record `0x0064ce20`, last record
`0x0064f1e0`, table end `0x0064f21f`; the following string pool starts at
`0x0064f220`.

All 144 records have distinct shipped names, distinct non-zero handlers, and a
recoverable developer-authored binding. Against the current database:

| Status | Rows | Meaning |
| --- | ---: | --- |
| `MATCH` | 19 | Curated semantic agreement, including `GetPlayer` → `IScript__GetPlayerBattleEngine` and `GetSlot` → `IScript__GetSlotBitValue` |
| `WEAK` | 15 | Handler exists under `FUN_*`; shipped name is an exact recovery lever |
| `CONTRADICTED` | 24 | Current label differs from shipped command token; requires per-body adjudication |
| `NO_FUNCTION` | 86 | Provably called handler entry is absent as a Ghidra function |

`MATCH` is semantic, not strict string equality. A naive
`IScript__<shippedName>` comparison produces a wrong 17/26 split.

The exact 15 weak rows are:

| Index | Shipped name | Handler |
| ---: | --- | --- |
| 4 | `Pause` | `0x00537c70` |
| 10 | `PlaySample` | `0x005381f0` |
| 11 | `Print` | `0x00537ad0` |
| 20 | `GetDistToObj` | `0x00536070` |
| 27 | `PlayCutscene` | `0x00535890` |
| 47 | `GetRatioBattleLineNodes` | `0x005353a0` |
| 56 | `GetWaterHeight` | `0x00534b30` |
| 60 | `SetX` | `0x00534d30` |
| 69 | `Damage` | `0x005348c0` |
| 78 | `ShutdownVariable` | `0x00536330` |
| 102 | `GetSquad` | `0x005365c0` |
| 118 | `AddHelpMessage` | `0x00533b30` |
| 121 | `MPDeclarePlayerWon` | `0x00533a40` |
| 127 | `Launch` | `0x005344a0` |
| 136 | `SetLockable` | `0x00533950` |

The `CONTRADICTED` grade does not automatically mean the current behavioral
label is false. Record 2 `SetSpeed` points to `0x00453ac0`, the shared
three-byte `RET 0x0c` stub. The correct conclusion is “the retail SetSpeed
native is a no-op,” not “the shared stub's one true name is SetSpeed.”

`0x00536cd0` is the strongest completed example:

- record 3 at `0x0064cee0`;
- `+0x00 → 0x0064f9fc → "SpawnThing"`;
- `+0x30 → 0x00536cd0`;
- exactly one image dword reference binds that handler;
- the runtime factory call creates ordinal 87 `Target Tank`;
- `TankFactory.msl:25` spawns one `Target Tank`;
- the current function ends immediately before the next handler
  `SpawnEscapePod` at `0x005371e0`.

`IScript__SpawnThing` is therefore shipped-data and runtime corroborated. The
`IScript` class prefix exists in RTTI, but exact ownership of this handler by
that class remains unproved; this is why the current grader places it in
`IMAGE_TYPE_TOKEN`, not `BINARY_STRING` or `RTTI_CONFIRMED`.

#### Complete opcode table

There are 27 serialized instruction classes/vtables and 26 distinct slot-0
executor addresses because NOP and LABEL share the no-op stub. All 27 targets
now exist as functions. The older JSON's eight “unpromoted” cases are stale.

| Op | RTTI instruction class | Vtable | Slot-0 executor | Current Ghidra name |
| ---: | --- | --- | --- | --- |
| `0x00` | `CInstructionOP_NOP` | `0x005e4d40` | `0x00453ac0` | `SharedVFunc__NoOp_Ret0C` |
| `0x01` | `CInstructionOP_PLUS` | `0x005e4d30` | `0x0052e180` | `CInstructionOP_PLUS__VFunc_00_0052e180` |
| `0x02` | `CInstructionOP_MINUS` | `0x005e4d20` | `0x0052e1d0` | `CInstructionOP_MINUS__VFunc_00_0052e1d0` |
| `0x03` | `CInstructionOP_MULTIPLY` | `0x005e4d10` | `0x0052e220` | `CInstructionOP_MULTIPLY__VFunc_00_0052e220` |
| `0x04` | `CInstructionOP_DIVIDE` | `0x005e4d00` | `0x0052e270` | `CInstructionOP_DIVIDE__VFunc_00_0052e270` |
| `0x05` | `CInstructionOP_PUSH` | `0x005e4cf0` | `0x0052e2c0` | `CInstructionOP_PUSH__VFunc_00_0052e2c0` |
| `0x06` | `CInstructionOP_POP` | `0x005e4ce0` | `0x0052e2f0` | `CInstructionOP_POP__VFunc_0_0052e2f0` |
| `0x07` | `CInstructionOP_OR` | `0x005e4cd0` | `0x0052e4d0` | `CInstructionOP_OR__ExecuteOr` |
| `0x08` | `CInstructionOP_AND` | `0x005e4cc0` | `0x0052e580` | `CInstructionOP_AND__ExecuteAnd` |
| `0x09` | `CInstructionOP_GREAT_THAN` | `0x005e4cb0` | `0x0052e630` | `CInstructionOP_GREAT_THAN__ExecuteGreaterThan` |
| `0x0a` | `CInstructionOP_LESS_THAN` | `0x005e4ca0` | `0x0052e6d0` | `CInstructionOP_LESS_THAN__ExecuteLessThan` |
| `0x0b` | `CInstructionOP_GREAT_EQ_THAN` | `0x005e4c90` | `0x0052e770` | `CInstructionOP_GREAT_EQ_THAN__ExecuteGreaterOrEqual` |
| `0x0c` | `CInstructionOP_LESS_EQ_THAN` | `0x005e4c80` | `0x0052e810` | `CInstructionOP_LESS_EQ_THAN__ExecuteLessOrEqual` |
| `0x0d` | `CInstructionOP_LABEL` | `0x005e4c70` | `0x00453ac0` | `SharedVFunc__NoOp_Ret0C` |
| `0x0e` | `CInstructionOP_REMOVE_TOP` | `0x005e4c60` | `0x0052e320` | `CInstructionOP_REMOVE_TOP__VFunc_0_0052e320` |
| `0x0f` | `CInstructionOP_CMP` | `0x005e4c50` | `0x0052e330` | `CInstructionOP_CMP__VFunc_00_0052e330` |
| `0x10` | `CInstructionOP_CMPB` | `0x005e4c40` | `0x0052e380` | `CInstructionOP_CMPB__ExecuteCompareEqual` |
| `0x11` | `CInstructionOP_CMPNEB` | `0x005e4c30` | `0x0052e8b0` | `CInstructionOP_CMPNEB__ExecuteCompareNotEqual` |
| `0x12` | `CInstructionOP_JMPNE` | `0x005e4c20` | `0x0052e990` | `CInstructionOP_JMPNE__VFunc_0_0052e990` |
| `0x13` | `CInstructionOP_JMPFALSE` | `0x005e4c10` | `0x0052e950` | `CInstructionOP_JMPFALSE__VFunc_00_0052e950` |
| `0x14` | `CInstructionOP_JMP` | `0x005e4c00` | `0x0052e9b0` | `CInstructionOP_JMP__VFunc_0_0052e9b0` |
| `0x15` | `CInstructionOP_GETTOP` | `0x005e4bf0` | `0x0052e9c0` | `CInstructionOP_GETTOP__VFunc_0_0052e9c0` |
| `0x16` | `CInstructionOP_POINTER` | `0x005e4be0` | `0x0052ea10` | `CInstructionOP_POINTER__VFunc_0_0052ea10` |
| `0x17` | `CInstructionOP_RETURN` | `0x005e4bd0` | `0x0052e0f0` | `CInstructionOP_RETURN__ExecutePop` |
| `0x18` | `CInstructionOP_CALL` | `0x005e4bc0` | `0x0052ea40` | `CInstructionOP_CALL__ExecuteCall` |
| `0x19` | `CInstructionOP_CALLLOCAL` | `0x005e4bb0` | `0x0052ec40` | `CInstructionOP_CALLLOCAL__VFunc_0_0052ec40` |
| `0x1a` | `CInstructionOP_PUSHPC` | `0x005e4ba0` | `0x0052e0a0` | `CInstructionOP_PUSHPC__VFunc_0_0052e0a0` |

RTTI proves opcode `0x0d` is LABEL, not an anonymous second NOP. Likewise the
current `CInstructionOP_RETURN__ExecutePop` behavioral suffix must not obscure
that opcode `0x17` is RETURN; POP is opcode `0x06`.

#### Complete datatype table

| Id | RTTI class | Vtable | Allocation | Measured payload | Getter slot |
| ---: | --- | --- | ---: | --- | --- |
| 1 | `CIntDataType` | `0x005e4af8` | 8 | dword at `+0x04` | `+0x30` |
| 2 | `CFloatDataType` | `0x005e4ea4` | 8 | float/dword at `+0x04` | `+0x34` |
| 3 | `CStringDataType` | `0x005e4e4c` | 8 | owned heap pointer at `+0x04`; serialized length + bytes + NUL | `+0x38` |
| 4 | `CBoolDataType` | `0x005e4d50` | 8 | dword/bool-like at `+0x04` | `+0x3c` |
| 5 | `CThingPtrDataType` | `0x005e4df8` | 8 | runtime pointer at `+0x04`, initialized zero; local token read | `+0x40` |
| 6 | `CPositionDataType` | `0x005e4da4` | 20 | floats at `+0x04/+0x08/+0x0c`; field at `+0x10` | `+0x44` |

Open: the type-5 serialized token-to-runtime-pointer law and the role of
position `+0x10`. The factory does not initialize the latter.

#### Script run-state layout

Measured from `CScriptObjectCode__Run`:

| Runtime-state offset | Role |
| --- | --- |
| `+0x08` | context |
| `+0x0c` | data stack base |
| `+0x20c` | stack/count field |
| `+0x210` | running guard |
| `+0x214` | instruction pointer |
| `+0x218` | flags |
| `+0x21c` | expected/saved stack size |
| `+0x220` | abort |
| `+0x224` | call depth |

Script-object offsets used by the run path:

| Offset | Role |
| --- | --- |
| `+0x04` | instruction array |
| `+0x58` | executor context |
| `+0x60` | debug flag |
| `+0x68` | `IScript` backpointer |

Opcode `0x17` stops when call depth is non-positive. The loop limit is 10,000.
The Level 100 trace saw 1,188 calls to the run function and 1,203 native CALL
executions; neither count is the total executed instruction count.

### PhysicsScript

The manager singleton is at `0x0066e99c`.

| Address | Identity |
| --- | --- |
| `0x0042e880` | `CPhysicsScript__Create` |
| `0x0042e8f0` | `CPhysicsScript__Destroy` |
| `0x0042e950` | `CPhysicsScript__Load` |
| `0x0042ea60` | `CPhysicsScript__Update` |
| `0x0042eb90` | `CPhysicsScript__CreateStatement` |

Top-level factory:

| Type | RTTI statement class | Vtable | Allocation | Allocator line |
| ---: | --- | --- | ---: | ---: |
| 1 | `CUnitStatement` | `0x005d9878` | `0x110` | `0x11` |
| 2 | `CWeaponStatement` | `0x005d9850` | `0x110` | `0x13` |
| 3 | `CWeaponModeStatement` | `0x005d9864` | `0x110` | `0x12` |
| 4 | `CRoundStatement` | `0x005d983c` | `0x110` | `0x14` |
| 5 | `CSpawnerStatement` | `0x005d9828` | `0x110` | `0x15` |
| 6 | `CExplosionStatement` | `0x005d9814` | `0x110` | `0x16` |
| 7 | `CComponentStatement` | `0x005d9800` | `0x110` | `0x17` |
| 8 | `CFeatureStatement` | `0x005d97ec` | `0x110` | `0x18` |
| 9 | `CHazardStatement` | `0x005d97d8` | `0x110` | `0x19` |

Every statement initializes `+0x04=type`, `+0x08=0`, byte `+0x0c=0`, and
`+0x10c=0`. Unknown types return null.

Registry globals:

| Address | Registry |
| --- | --- |
| `0x008553f4` | Spawner |
| `0x008553f8` | Explosion |
| `0x008553fc` | Unit/definition records |
| `0x00855400` | Component |
| `0x00855404` | Feature |
| `0x00855408` | Hazard |

The pristine `default physics.dat` is 175,603 bytes, SHA-256
`e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`.
Its framing is:

```text
file      := u16 0x0012, statement*
statement := u32 tag, u32 declaredSize, cstring name, node*
node      := u32 valueId, u32 payloadLen, payload bytes, u32 link
link      := 0 -> another node; 0xffffffff -> statement end
```

The link sentinel, not `declaredSize`, is authoritative. Walking it consumes
777 statements plus a final four-byte sentinel:

| Shipped tag | Statements | Semantic family | Value-factory type | Factory address |
| ---: | ---: | --- | --- | --- |
| 1 | 160 | Unit | Type 2 | `0x00431bb0` |
| 2 | 139 | Weapon | Type 3 | `0x00434300` |
| 3 | 145 | WeaponMode | Type 4 | `0x00435010` |
| 4 | 91 | Round | Type 5 | `0x00437490` |
| 5 | 38 | Spawner | Type 6 | `0x00439b40` |
| 6 | 118 | Explosion | Type 7 | `0x0043a860` |
| 7 | 39 | Component | Type 10 | `0x0043c500` |
| 8 | 43 | Feature | Type 8 | `0x0043b990` |
| 9 | 4 | Hazard | Type 9 | `0x0043c0b0` |
| **Total** | **777** |  |  |  |

Every value id used by all 777 shipped statements is present in the
corresponding factory. Unknown used ids: zero. The tag-to-factory mapping is not
uniform `tag+1` for tags 7–9.

The Round and WeaponMode maps are completely closed by RTTI, vtable, factory
case, apply body, and destination write. Round has 38 ids, record size `0xa8`,
name at `+0x18`; WeaponMode has 37 ids, record size `0xc0`, name at `+0x30`;
WeaponMode id `0x07` is genuinely absent. The complete field tables appear in
the appendices below.

Two concrete chains:

```text
Pulse Cannon Pod
  charge 0 -> Mech Pulse Cannon Charged
  reload 0.1 s; power 0.03
  round -> Mech Pulse Bolt Medium
    velocity 35; damage 0.8; life 6; radius 0.07
    explosion -> Mech Pulse Hit Medium
      radius 0.5; damage 1.0

Mech Twin Vulcan Cannon
  consumption 2.0
  reload 0.05 s; volley 4; predictive 1
  inaccuracy 0.006981317 rad = 0.4°
  round -> Mech Bullet
    velocity 60; damage 0.08; life 1
    explosion -> Mech Bullet Hit
      radius 0.2; damage 0.001
```

Runtime establishes a 20 Hz released update and 1.75 world units per update for
the speed-35 pulse, so velocity is units/second and 0.1 seconds is two updates.
The damage-combination law remains open. Direct pulse observations fit
`0.8 + 1.0 = 1.8`, but the static consumer of both fields has not been found.
The sharp discriminant is a direct Twin Vulcan hit: additive predicts `0.081`,
round-only `0.08`, explosion-only `0.001`.

### Career save and options

The supported retail `.bes`/default-options container is fixed at 10,004 bytes
(`0x2714`) with version `0x4bd1`:

```text
0x0000  version u16 = 0x4bd1
0x0002  CCareer fixed copy, 0x24bc bytes
0x0006  CCareerNode[100]
0x1906  CCareerNodeLink[200]
0x1f46  CGoodie[300]
0x23f6  five packed kill-counter dwords
0x240a  mSlots[32]
0x248a  career/options scalar fields
0x24be  16 options entries, 0x20 bytes each
0x26be  options tail, 0x56 bytes
0x2714  end
```

| Address | Current identity | Role |
| --- | --- | --- |
| `0x00421200` | `CCareer__Load` | `flag=0` boot/defaultoptions path applies entries/tail; nonzero career path preserves pre-load sound/music and skips their apply |
| `0x00421350` | `CCareer__Save` | Fixed career serialization |
| `0x004213c0` | `CCareer__SaveWithFlag` | Retail save-path helper; exact flag semantics not fully named |
| `0x00421430` | `CCareer__GetSaveSize` | Returns/calculates supported size |
| `0x00420b10` | `OptionsTail_Write` | Writes 0x56-byte tail |
| `0x00420d70` | `OptionsTail_Read` | Reads 0x56-byte tail |
| `0x00514f80` | `PCPlatform__WriteSaveFile` | Platform file wrapper |
| `0x00515080` | `PCPlatform__ReadSaveFile` | Platform file wrapper |
| `0x00464c50` | `CFEPSaveGame__CreateSave` | Save-menu serialization/write path |
| `0x00461e20` | `CFEPLoadGame__DoLoad` | Load-menu path |

Static call chains:

- load UI → `CCareer__Load` → conditional default-options write;
- main-menu save → career save + options write + optional platform save;
- pause resume/exit → career save + optional platform save + options write;
- debrief initialization prepares state but is not itself the save write.

The rebuild/editor safety rule follows the binary: start from a real baseline,
preserve all unknown bytes and exact size, and never synthesize a save from
scratch.

### Frontend, HUD, and overlays

The frontend is a page/state system with Direct3D immediate-mode composition,
localized text, controller remapping, saves/options, goodies, FMV, and level
handoff. Static notes establish ownership; the D3D9 proxy establishes draw
behavior for captured pages.

Measured frontend facts:

- Frontend pages use pretransformed XYZRHW vertices, principally FVF `0x144`;
  selected configuration also emits 183 lit-mesh draws with FVF `0x152`.
- A settled main-menu sample at proxy frame 3000 has exactly 39 draws. Frame
  3500 has 35, so 39 is a sample state, not a universal invariant.
- Main-menu ordering includes darkener/guides, three scrolling columns, flag,
  visible and alpha-zero chevrons, selector, seven text shadow/body pairs,
  arcs/icons, version/title, additive emblems, and cursor last.
- One proxy capture observed 131 render frames between transition landmarks.
  This is not the semantic duration: render and Process are decoupled, while the
  click handler explicitly requests 50 Process ticks. Decoration clocks are
  delta-time driven.
- `-skipfmv` suppresses the animated video background and is not a valid oracle
  for every normal frontend composite.

Measured Level 100 HUD facts for each sampled tick:

| Property | Result |
| --- | --- |
| XYZRHW HUD draws | 74 |
| Alpha test | enabled on all 74; ref 8; `GREATEREQUAL` |
| Stage 1 | disabled on all 74 |
| Texture factor | `0x4cffffff` |
| Stage 0 color op | 66 `MODULATE2X`, 8 `MODULATE` |
| Z | off on 66 |
| Blend | 68 SRCALPHA/INVSRCALPHA, 5 additive, 1 ZERO/ONE |
| Stable rectangle+diffuse+texture identity | 64 / 74 |

The compass consists of two ring strips. FVF `0x102` has XYZ + TEX1 and no
diffuse. Sampler U/V clamp is used. Ring 2 has identity world; ring 1 carries a
pure Z rotation; view is identity; projection maps 320 pixels per model unit.
With blend ONE/INVSRCALPHA, the measured RGB composition is
`out = texel.rgb + (1-texel.a)*background`. The gauge texture is sampled.
Ring-1 tape color remains unresolved because the sampled rows were zero/likely
the wrong lock. The scanner's bounded candidate population is 33 non-player
units.

### Rendering state, math, terrain, cockpit, and trees

#### Default D3D9 state block

`0x004eb1e0 D3DStateCache__UseDefaultRenderState` spans
`[0x004eb1e0,0x004eb99d)`, 1,981 bytes / 569 instructions, and has seven
callers. It sets:

- alpha blending on: SRCALPHA / INVSRCALPHA;
- alpha test on with `GREATEREQUAL`;
- solid fill; requests D3DCULL_CCW, with CW↔CCW swapped by both state setters
  while mirror flag `0x0089d680` is nonzero;
- Z enabled, Z writes enabled, compare LEQUAL;
- lighting enabled and Gouraud shading;
- diffuse and ambient material sources = COLOR1;
- specular and emissive sources = MATERIAL;
- normal normalization disabled;
- stage 0 texture × diffuse via MODULATE;
- texture stages 1–3 disabled.

The block also sets `FOGENABLE` conditionally: zero while the mirror flag is
nonzero, otherwise one.

`COLORVERTEX` is render-state id `0x8d`, not 60, and no executable instruction
writes it. `0xf0ccface` values in the state arrays are dirty-cache sentinels,
not colors.

Cache arrays:

| Address | Role |
| --- | --- |
| `0x00855bb0` | D3D state-cache object |
| engine `+0x32ea0` / `0x00888a50` | current device pointer |
| `0x00855540` | render-state shadow, `state*4` |
| `0x008557f0` | stage/sampler shadow, `(type + stage*30)*4` |
| `0x008554d0` | texture shadow |

Confirmed `IDirect3DDevice9` slots used by this binary:

| Device offset | API |
| ---: | --- |
| `+0xb0` | `SetTransform` |
| `+0xdc` | `SetClipPlane` |
| `+0xe4` | `SetRenderState` |
| `+0x104` | `SetTexture` |
| `+0x10c` | `SetTextureStageState` |
| `+0x114` | `SetSamplerState` |
| `+0x134` | `SetSoftwareVertexProcessing` |
| `+0x164` | `SetFVF` |
| `+0x170` | `SetVertexShader` |

The cached render-state setter at `0x00513bc0` has 440 direct calls and the
forced setter at `0x00513c20` has 50: 490 render-state calls, not 547. The
misquoted 547 combined those 490 with 57 `SetTexture` calls. The default block's
seven exact callers are loading screen `0x0042c8b4`, FEPGoodies `0x0045edda`,
debug draw `0x0047065e`, PreRender `0x0053e22b`, Render `0x0053e4d0`, FMV
vfunc `0x0053f25f`, and frontend RenderStart `0x00540f78`.

The cache invalidation token is `0xfedcba98` at `0x00513600`. The distinct
`0xf0ccface` token forces cache misses for ambient/fog/texture-factor fields.

Several current names are contradicted by byte/API-slot evidence:

| Address | Current live name/problem | Measured correction |
| --- | --- | --- |
| `0x00513a50` | `CEngine__SetRenderStateCached` | Calls D3D9 vtable `+0x104` = `SetTexture`; shadows an eight-entry texture table |
| `0x00513820`, `0x00513870` | Generic state labels | Cached/raw `SetTextureStageState`, device slot `+0x10c` |
| `0x005138b0`, `0x00513930` | Generic state labels | Cached/raw `SetSamplerState`, device slot `+0x114` |
| `0x004eb9a0` | `CUnit__InitDefaultTuningBlock` | Writes exactly 0x88 bytes: two 0x44-byte `D3DMATERIAL9` records at `0x0083d248` and `0x0083d28c`; runtime `SetMaterial` consumes them |
| `0x004eba30` | `CEngine__SetVertexShaderPathEnabled` | Uses device `+0xdc = SetClipPlane` and `D3DRS_CLIPPLANEENABLE (0x98)` under mirror flag `0x0089d680` |
| `0x005513d0` | `SetVertexFormatDeferred` | Stores `this+0x2f0`, marks dirty `+0xe2d`, and flushes as `D3DRS_FOGDENSITY`; exact class owner remains to be adjudicated |
| `0x00514030` | `RenderState_Set_23_8C_Compat` | Fog-mode selector: RasterCaps `0x100` chooses table EXP / vertex NONE; fallback table NONE / vertex EXP; disable clears both |

The material initializer correction is exact:

| Material | Address | Diffuse | Ambient | Specular / emissive | Power |
| --- | --- | --- | --- | --- | ---: |
| Generic | `0x0083d248` | `(1,1,1,1)` | zero | zero | 0.1 |
| Terrain | `0x0083d28c` | zero | `(0.8,0.8,0.8,0.8)` | zero | 0 |

#### Fog

The far world clip used by released rendering is 700. The pinned source's
`DEFAULT_Z_FAR=256` is dead for this path. Fog parameters and enablement are
set through the D3D9 state cache; only the enabled lighting state among several
default-state conclusions has a direct runtime capture, so static defaults
must not be over-promoted to every draw.

`CDXEngine__Render 0x0053e2e0` writes `FOGCOLOR [0x006fbe40]` and deferred
density `[0x006fbe60]`; Level 100 supplied `#D8D8FC` and `0.0084`.
`ApplyPendingRenderState 0x00550d50` flushes enable, start, end, and density.
`RANGEFOGENABLE` is never written, so this is depth-based fog. Terrain inherits
the global state. The water path at `0x0055b6c0` forces density, enable=1,
start=0, end=10, color, and fog mode. Mirror flag `0x0089d680` swaps culling
and forces fog off; the exact mirror/reflection-pass identity remains inferred
and open.

#### Vector and matrix conventions

| Address | Law |
| --- | --- |
| `0x00411a60 Vec3__Cross` | Standard right-handed `a × b`, with `this` as left operand; 36 callers |
| `0x0040d2c0` | Uses the 3×3 basis at offsets 00/04/08, 10/14/18, and 20/24/28 inside three 16-byte-stride Mat34 rows; computes row-dot `M*v`, so basis axes are columns; 56 callers |

The remaining ground-effect roll-sign question depends on the horizontal sign
and handedness of the ground normal; it is still unknown.

#### Terrain

- The terrain shade plane is the MMAP byte plane with the corrected axis order.
- The exact sampler is an 8.8 fixed-point bilinear stepper.
- All 67 shipped heightfields have a null per-node colored-light array.
- The sun color does not directly multiply terrain vertices.
- A proposed third terrain light was falsified; terrain draws are dominated by
  the two-light setup.
- Terrain material at `0x0083d28c` has black diffuse and ambient 0.8.
- `LANDSCAPE_LIGHTING` defaults on.
- Captured enabled lights are sun `(189,177,121)/256` and anti-sun
  `(35,35,56)/256`.
- The measured ambient law is
  `2 * 0.8 * (sun + anti-sun) = (1.4, 1.325, 1.10625)`.
- Cloud-shadow scroll is 0.02 / 0.01 per second. Zero-phase extrapolation lands
  near the first level frame (INFERRED); no reset write was observed. The
  `.rdata` values 0.001 / 0.0005 are per-advance increments and were previously
  misread as per-second rates.
- In the measured Level 100 comparison, spectral analysis found no missing
  high-frequency terrain term. Adding a `+0.5,+0.5` sample offset, consistent
  with the D3D9 fixed-function pixel-center convention, improved reconstruction
  correlation from 0.295 to 0.836; this is reconstruction/inference evidence,
  not a direct binary observation.

The active path is more specific:

- `LANDSCAPE_LIGHTING` is at `0x008aa940`, value at `0x008aa94c`, default 1.
- `USE_MODULATE_2X` value `0x008554fc` defaults 1.
- `Landscape__Render 0x00545410` selects MODULATE2X for stages 0/1, zeroes
  ambient render state, installs the terrain material, converts each enabled
  cached light's diffuse color into D3D light ambient via
  `ApplyCachedLight(i,1)`, calls `RenderTerrain 0x00545590`, then restores the
  HFLD light form with `ApplyCachedLight(i,0)`.
- Terrain vertices have 0x14-byte stride: position + UV only, no normal and no
  vertex color.
- At actual Level 100 draw setup, the enable vector is `[1,1,0,…]`. Five
  observations were byte-identical across the complete 736-byte light records
  plus eight enable bytes: run 1 draws 300/1200/2100 spanning 15.688 seconds and
  run 2 draws 200/2600 spanning 17.981 seconds.
- The prior “terrain is unlit” conclusion came from a pre-call/cache read and
  is withdrawn. The MODULATE-versus-MODULATE2X-only explanation was also
  incomplete because it omitted live material/light state.

MMAP construction:

- global `CMixerMap` at `0x0089bd80`, shade-plane pointer at `0x0089bd84`;
- initializer `0x005232b0` allocates 4,096 slots × `0x14` plus 0x40000 bytes for
  the 512×512 shade plane;
- MSHD follows MCEL and is copied verbatim; no runtime writer/bake path was
  found;
- address law `shade[y*512+x]`, while tile flags use
  `cellY*64+cellX`;
- non-zero support: rows 144–368, columns 136–432;
- 3,582 cells are all zero; island distribution mean 22.06, median 22, p10 15,
  p90 32, maximum 63;
- the 64-entry gradient table is at `0x0047e8e0`;
- loader `0x0047f750` doubles/clamps RGB565 masks; blue saturates at 14,
  red/green at 29;
- blitter `0x0047eff0` uses signed arithmetic shift and pre-increment 8.8
  stepping; a Level 0 reconstruction matched 33,600 samples with zero
  mismatches.

The per-node color builder at `0x00541f50` belongs to a dead offline PS2 path
at `0x00547860`; no shipped PC cache loader reaches it.

#### Cockpit

The cockpit lighting law is:

```text
COLOR1 * (ambient register + Σ max(0, N·L) * diffuse_i)
```

Sampled cockpit draws use `D3DRS_AMBIENT 0x000D0F2B`, the generic material,
the two HFLD lights, specular disabled, stage 0 MODULATE, and stage 1 disabled.
The wrapper enables `NORMALIZENORMALS`; helper `0x0044a650` sets
SRCALPHA/INVSRCALPHA and ZWRITE=0, but sampled mesh texture/vertex alpha is
opaque, so blending is identity.

Seven world matrices are uploaded per cockpit render. The root tracks the camera
within `1.4e-4`; mesh node `Camera01`/CPOS is not the attachment transform. Two
mirrored batches are authored geometry. Projection is 90° horizontal at 4:3,
near plane 0.1.

The seven batches are hood, `Rsidebit01` (determinant -1), `Rsidebit02`,
`Lsidebit02` (determinant -1), `Lsidebit01`, `Object03`, and `Object01`. All
1,340 normals transform with maximum `N·L` discrepancy zero under the recovered
world transforms. A prior “cockpit normals face the wrong way” conclusion was
contaminated by later HUD overlays and is withdrawn.

A sampled root matrix was bit-identical at frames 0, 2048, and 2400 across four
launches. This proves repeatability for that Level 100 pose, not that the
cockpit never tracks movement. The residual factorization is
`W0 = Sᵀ · Bᵀ` within `1.209e-7`, where `S` is the matrix at cockpit `+0x2c`
and `B` the BattleEngine yaw matrix at `+0x3c`. The write provenance of `S`
still needs a write-watch.

Current cockpit names contain a substantial wrong-owner cluster:

| Address | Current problem | Measured owner/role |
| --- | --- | --- |
| `0x0053bb50` | `CDXEngine__RenderOptionalFullscreenEffectPass` | `CCockpit__Render`; sole call at `0x0053ec6a`, immediately after `mov ecx,[esi+0x528]` at `0x0053ec64` |
| `0x004247a0` | `CGeneralVolume` owner | `CCockpit` randomized shake offsets; receiver is `[CBattleEngine+0x528]` |
| `0x00424920`, `0x00424990` | `CGeneralVolume` owner | `CCockpit` fly↔walk morph starters called by `CBattleEngine__Morph` |
| `0x00424a00` | `CUnitAI` owner | `CCockpit` virtual event handler; checks event ids `0x7d0`/`0x7d1` and dispatches `0x00424a20` for `0x7d1` |
| `0x00424a20`, `0x00424be0`, `0x00424ca0`, `0x004250f0` | `CUnitAI` owner | `CCockpit` event/update/morph/shake tracking helpers operating the same fields |
| `0x004254f0` | still `FUN_*` | RTTI-owned `CCockpit` secondary-vtable slot 1; composes cockpit `+0x2c` with battle-engine `+0x3c`, an orientation getter/composer |

`0x004244b0` is the constructor evidence tying the cockpit object to
`CBattleEngine+0x528`.

#### Trees

Trees use a separate lighting rig:

- ambient `0x0039293e`, runtime-measured and constant across 438/436 close-pine
  draws in two launches; it is absent as an image literal and its composing
  writer/source remains unresolved;
- downward sun at 10% intensity;
- full anti-sun upward;
- foliage undersides are therefore brighter/bluer;
- an earlier reconstruction used the wrong normal/sign reading.

Mode 4's lighting/material/stage state makes the lit vertex result exactly
black. Its visible framebuffer contribution remains unknown because blend state
was not captured.

Across three launches, 4,393 sampled mesh draws included close-pine CRTTree
draws `589+442`, static CRTMesh `493+134`, mode-4 draws `27+19`, and seven
cockpit mode-0 draws. Modes 2/6/8 did not occur; branches `0x0054a423` and
`0x0054a466` never fired. All 2,269 sampled `pinesnow0..3` vertices are exactly
white, closing the vertex-color caveat. Keep three similarly named systems
separate:

```text
CThing-derived CTree::Init       0x004f6080
CRTTree renderer/build           0x004dd7b0 / 0x004dd960
CDXTrees::Render                 0x0055aa10
```

The live database still names `0x004f6080`
`CTree__VFunc_9_004f6080`; the direct callsite plus the exact 1,481-call TTD
partition establish `CTree__Init`.

### Audio, video, localization, and retail resources

The executable connects Bink FMV, Ogg/Vorbis, DirectSound, language DATs,
MissionScript text, AYA resources, textures, meshes, effects, and physics data.
The finite installed corpus and format census is in [`BEA_DATA.md`](BEA_DATA.md):
5,515 files, including 1,361 AYA-family files, 3,057 Ogg files, 66 Bink videos,
six language DATs, and 95 numbered mission trees.

Current boundaries:

- Bink video playback, frontend FMV flow, Ogg music/voice, and DirectSound
  backend ownership are statically mapped.
- The reconstruction's startup videos remain silent because their Bink audio
  streams have not been decoded/assigned to language; this is a rebuild
  boundary, not evidence that retail videos are silent.
- `CText__Init`, `CText__GetStringById`, and
  `CText__GetStringByIdAfter` establish versioned language-table lookup and
  fallback behavior.
- Parser success proves the decoded framing/fields exercised by that parser,
  not visual/audio parity or universal format support.

## Controlled Level 100 runtime evidence

### Trace boundary and debugger trap

The first valid time-travel trace is:

```text
G:\bea-ttd\play-level100\play-level100.run
34,359,738,368 bytes
target SHA-256 E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4
arguments: -skipfmv -level 100
guest outcome: alive at stop
```

The runtime image differs from pristine only at the force-windowed site:
file offset `0x12a644` / VA `0x0052a644`, bytes
`a1 f0 2d 66 → b8 01 00 00` with the following instruction byte unchanged.
Evidence at unrelated addresses remains usable, but the image must never be
called pristine.

The trace covers load, fly-in, and briefing. It does not reach later combat or
the 19 later scripted actor beats.

The trace has no TTD index. On this trace, `dd`/`da` of a cold runtime-written
BSS global after an arbitrary `!tt <percent>` can silently return zero or
file-backed bytes with no error. Valid memory observations must either:

1. seek to a call/access position where the program just touched that memory;
2. derive positions from `TTD.Memory` access scans; or
3. build `!ttdext.index`.

Every query needs a same-run positive control. `CThing__Init = 1,579` is useful;
a zero `FatalError` count is not. `dx -g` displays at most 100 rows unless the
query explicitly groups/counts them, and projecting a multimillion-entry memory
collection can exhaust the debugger.

### Exact 33 factory creations

Every factory call returned a distinct non-null object:

| # | Caller | Ordinal | Selector | RTTI class | Definition name |
| ---: | --- | ---: | ---: | --- | --- |
| 0 | `CWorld__LoadWorld` | 120 | 7 | `CBuilding` | Control Tower |
| 1 | `CWorld__LoadWorld` | 141 | 7 | `CBuilding` | Forseti Pulse Tank Factory |
| 2 | `CWorld__LoadWorld` | 7 | 7 | `CBuilding` | Forseti Repair Pad |
| 3 | `CWorld__LoadWorld` | 58 | 4 | `CCannon` | SAT Turret |
| 4 | `CWorld__LoadWorld` | 60 | 4 | `CCannon` | Blaster Turret |
| 5 | `CWorld__LoadWorld` | 60 | 4 | `CCannon` | Blaster Turret |
| 6 | `CWorld__LoadWorld` | 61 | 4 | `CCannon` | Pulse Turret |
| 7 | `CWorld__LoadWorld` | 121 | 7 | `CBuilding` | Forseti Research Building |
| 8 | `CWorld__LoadWorld` | 104 | 7 | `CBuilding` | Forseti Building 1 |
| 9 | `CWorld__LoadWorld` | 105 | 7 | `CBuilding` | Forseti Building 2 |
| 10 | `CWorld__LoadWorld` | 105 | 7 | `CBuilding` | Forseti Building 2 |
| 11 | `CWorld__LoadWorld` | 110 | 7 | `CBuilding` | Forseti Solar Pod |
| 12 | `CWorld__LoadWorld` | 106 | 7 | `CBuilding` | Forseti Building 3 |
| 13 | `CWorld__LoadWorld` | 106 | 7 | `CBuilding` | Forseti Building 3 |
| 14 | `CWorld__LoadWorld` | 113 | 7 | `CBuilding` | Forseti Radar Station |
| 15 | `CWorld__LoadWorld` | 137 | 7 | `CBuilding` | Forseti Light Fighter Airfield |
| 16 | `CWorld__LoadWorld` | 114 | 7 | `CBuilding` | Forseti Docks |
| 17 | `CWorld__LoadWorld` | 119 | 7 | `CBuilding` | Hangar |
| 18 | `CWorld__LoadWorld` | 107 | 7 | `CBuilding` | Forseti Tall Building 1 |
| 19 | `CWorld__LoadWorld` | 109 | 7 | `CBuilding` | Forseti Tall Building 3 |
| 20 | `CWorld__LoadWorld` | 107 | 7 | `CBuilding` | Forseti Tall Building 1 |
| 21 | `CWorld__LoadWorld` | 109 | 7 | `CBuilding` | Forseti Tall Building 3 |
| 22 | `CWorld__LoadWorld` | 156 | 25 | `CSimpleBuilding` | Forseti City Building 1 |
| 23 | `CWorld__LoadWorld` | 157 | 25 | `CSimpleBuilding` | Forseti City Building 2 |
| 24 | `CWorld__LoadWorld` | 158 | 25 | `CSimpleBuilding` | Forseti City Building 3 |
| 25 | `CWorld__LoadWorld` | 157 | 25 | `CSimpleBuilding` | Forseti City Building 2 |
| 26 | `CWorld__LoadWorld` | 157 | 25 | `CSimpleBuilding` | Forseti City Building 2 |
| 27 | `CWorld__LoadWorld` | 117 | 7 | `CBuilding` | Warehouse |
| 28 | `CWorld__LoadWorld` | 66 | 12 | `CDropship` | U-17 Highside Transporter |
| 29 | `CWorld__LoadWorld` | 31 | 8 | `CPlane` | Air Trainer |
| 30 | `CSquad__Init` | 87 | 2 | `CGroundVehicle` | Target Tank |
| 31 | `CSquad__Init` | 87 | 2 | `CGroundVehicle` | Target Tank |
| 32 | `SpawnThing` native | 87 | 2 | `CGroundVehicle` | Target Tank |

Histograms:

```text
callers: CWorld__LoadWorld 30; CSquad__Init 2; SpawnThing 1
classes: CBuilding 19; CSimpleBuilding 5; CCannon 4;
         CGroundVehicle 3; CDropship 1; CPlane 1
```

Calls 0–26 are the base-world structure burst. Calls 27–29 are the level-world
burst: Warehouse plus both ambient aircraft. The BSWD/RLWD labels for those
bursts are a strong inference from the two `LoadWorld` executions and world
content, not a direct chunk-tag runtime read.

The old equality “33 calls = 33 static world objects” was coincidental. The
actual 33 are 28 structures, two ambient aircraft, and three Target Tanks.
Icebergs and other feature objects use a different path.

The `Air Trainer` class selector is 8. A prior report's “behavior id 9” confused
the serialized physics value with the internal selector; selector 9 is
`CBomber`.

### Initialization populations

| Function/path | Calls | Exact interpretation |
| --- | ---: | --- |
| `CThing__Init` | 1,579 | All observed thing descendants at load |
| from `CTree__Init` return `0x004f6368` | 1,481 | Exactly the pinned pine-instance count |
| from `CComplexThing__Init` Euler branch `0x004f40e3` | 68 | Every captured complex thing |
| from authored-basis branch `0x004f4107` | 0 | No Level 100 complex thing used it in this trace |
| from `CWaypoint__InitAndLink` return `0x005057c6` | 30 | Exactly the serialized waypoint count |
| `CUnit__Init` | 34 | Strong inference: 33 factory objects plus player |
| `CComplexThing__SetName` | 68 | Every captured complex thing receives a name argument, possibly `""` |
| `CComplexThing__SetScript` | 79 | Assignments, not unique-scripted-object count |
| `CSpawnerThng__DoSpawn` | 0 | Bounded absence before briefing |
| `CWorld__SpawnInitialThings` | 1 call / 14 instructions | Zero factory calls; an empty world-mesh-list head is the strong static+trace inference explaining the short path |

`SetScript = 79` exceeds 68 complex things because an object can receive an
empty then a real binding. It is not a unique-object census.

Observed script attachments include:

- `Transporter` → the CDropship returned for U-17 Highside Transporter;
- `Flyby` → the CPlane returned for Air Trainer;
- `BattleEngine` → player object `0x0811a660`;
- `LevelScript`, `Setup`;
- `Turret` ×4;
- `Facilities` ×4;
- `TankFactory`;
- `Hangar` attached to the Forseti Light Fighter Airfield, not the separate
  Hangar building;
- `StaticTarget` on Warehouse and two Target Tanks;
- `TargetTank1` on the third Target Tank;
- `TargetZone1` through `TargetZone4`;
- `FiringRange` triggers.

Attachment proves a binding. It does not by itself prove movement, rendering,
audio, or that a later scripted beat executed.

### Other exact trace counts

| Event | Count / boundary |
| --- | --- |
| `CScriptObjectCode__Run` | 1,188 calls |
| `CInstructionOP_CALL__ExecuteCall` | 1,203 calls |
| Compass render | 389 |
| D3D `SetTransform` uploads | 287,364 whole-trace events |
| World-matrix dword writes | 7,779,632 whole-trace events |

The last two totals have no defensible frame denominator and must not be
reported “per frame.”

## D3D9 proxy and visual-state findings

The passive proxy captures draw order, vertices, textures, selected state, and
calls on a copied target. Nine new frames matched promoted retail references
with mean absolute difference roughly 0.2068–0.2503 and material disagreement
roughly 0.76–1.20%. That demonstrates proxy capture fidelity, not rebuild
parity. Instrumentation is timing-nonneutral and does not yet shadow every
transform, sampler, texture-content, or clear/viewport detail.

### Frontend draw census

| Captured page/state | Draw count |
| --- | ---: |
| Boot samples | 8 / 4 / 9 / 10 |
| Click-to-start | 14 |
| Main page | 39 on 381/500 sampled frames; 35 on 119/500 while four chevrons blink |
| Options root | 30 |
| Controller page | 168 |
| Sound page | 74 |
| Video page | 74 |
| Credits | 8 → 24 |
| Choose | 67 |
| Select level | 83 |
| Mission briefing | 42 |
| Configuration | 293 = 110 screen + 183 lit mesh |
| Loading | 8 |

Counts include the cursor except boot/loading.

Main-menu clear is `#1f1f3f`; a black alpha-`0x3e` overhang from
`(-40,-3)` to `(680,483)` produces the measured final background near
`(23,23,48)`. Thirty-seven of 39 draws use MODULATE2X; darkener and cursor use
MODULATE. Alpha test is `GREATEREQUAL 8`.

The cursor renderer at `0x00523a70` resolves `mouse.tga`, whose runtime texture
is 128×128 A8R8G8B8 even though the disk AYA uses DXT2. It draws a 32×32 quad at
the pointer and is the last interactive draw. Whether the OS cursor is
separately hidden remains unproved.

Across six pages, 63 text shadow/body pairs place the shadow first and the body
at `(-1,-1)`, with the same alpha and a black shadow. Example selector geometry:
New Game 117×32 centered near `(219,304)` and Options 92×32 near `(219,404)`;
width is ink width +31. Live-label alpha is `0xfd`, disabled `0x7d`, version
`0xff`, not one global opacity.

Decoration shadows use fixed scale 1.05 and shared translation ellipse
`u=5+6*cos(theta)`, `v=10+3*sin(theta)`. A 1,795.2-render-frame fit is
timing-contaminated; the absolute wall-time/phase is not established.

The click-to-start action handler `0x0051b660` (RTTI owner `CFEPIntro`) pushes
`0x32` and then `SetPage(0)`: a click-to-start → `FEP_MAIN` transition of 50
**Process ticks**, not 131 render frames. `MAINTIME=70` belongs to the
FEPGoodies Back-to-main path. The observed 131-frame reveal reflects
render/process decoupling.

### HUD corrections and exact composition

- Crosshair draw order uses alpha 64 / 128 / 64 with pure white diffuse, not
  the older order/color.
- The left resource bar is horizontal and left-anchored; a mirrored right bar
  exists.
- Both WeaponOutline sides use diffuse `0xff574737`; under MODULATE2X this is
  `#ae8e6e`. The old “left grey” claim is false.
- The objective panel has nine pieces.
- CircleMask is a depth stamp at `(471,320)`, 192×192, UV
  `-0.25..1.25`, Z `0.005`, blend ZERO/ONE, Z test/write on.
- Six portrait draws occupy `(519,368)`, 96×96—not 128×128.
- Noise is `(503,352)`, 128×128; portrait outline begins `(519,368)`.
- Noise alpha is about 0.235–0.290 with a portrait and 0.424–0.455 without.
- Message text appears at 40 characters/second, wraps at 25 columns, shows
  three lines, scrolls one line, and has pitch 15.
- `CHud__RenderBattleline 0x00487d10` branches on
  `CInfluenceMap__IsEmpty 0x0048c2d0`, not merely “message active.”

### Compass and scanner

`Compass__Init 0x0053be40` calls `BuildRingGeometry 0x0053c1d0` twice:

| Ring | Segments | Radius | Vertices | Texture |
| --- | ---: | ---: | ---: | --- |
| 1 | 50 | 31% | 102 | 512×32 A4R4G4B4 tape |
| 2 | 40 | 27% | 82 | dynamic 256×8 A4R4G4B4 gauge |

`Compass__Render 0x0053cd30` draws ring 2 first (80 triangles), then ring 1
(100), each as one strip. FVF `0x102` contains XYZ + TEX1 and no diffuse.
Sampler U/V is CLAMP; alpha test off; blend ONE/INVSRCALPHA; lighting, fog, Z,
and Z writes off. The compositing law is
`out = texel.rgb + (1-alpha)*background`.

Ring 2 world is identity; ring 1 world is pure Z heading. The private
projection is:

```text
m00=1
m11=1.333333
m22=1.0050251
m23=1
m32=-0.5025126
```

At 640×480 this is 320 pixels/model unit. Geometry predicts ring-1 radii
95.6–101.6 pixels and ring-2 80–92.8, matching measured 95–101 and 80–92.

Gauge column 224 exact A4R4G4B4 rows:

```text
0000 4118 3006 2005 2004 1002 0001 0000
```

The ring-1 tape is **not** proven empty. The 416 sampled texels were zero, but
its ink is spatially localized; a full texel census remains open.

The scanner path `0x00484c50` uses runtime range 96. Constants include scale
numerator 40, clamp 46, cull `92²`, fade `1/46`, and center `(68,417)`.
Contacts use SRCALPHA/INVSRCALPHA, not additive. The bounded candidate set is
33 non-player units, including the dropship and plane. Exact membership
semantics remain open across vcall/flag/allegiance gates.

## Executable patch atlas

These are reverse-engineered byte contracts for **verified copied
executables only**. They are not permission to modify the Steam installation,
and no patch was applied during this research pass.

| Feature | VA / file offset | Clean bytes / value | Patched behavior | Evidence boundary |
| --- | --- | --- | --- | --- |
| Force-windowed startup | `0x0052a644` / `0x12a644` | `a1 f0 2d 66` | `b8 01 00 00` | Stable copied-target path; runtime trace uses it |
| Resolution gate | file `0x129696` | Catalog is byte authority | Allows selected windowed resolution path | Copied-profile only |
| Optional later fullscreen flip | file `0x12bb97` | Catalog is byte authority | Experimental follow-up | Use only after stable windowed row |
| Extra graphics default | `0x004cdd40` / `0x0cdd40` | `6a 00` | `6a 01`, `GEFORCE_FX_POWER` default on | Visible effect parity not proved |
| Ignore `cardid.txt` override call | `0x0052af3f` / `0x12af3f` | `e8 9c d7 ff ff` | five NOPs | Broad vendor-tweak bypass; optional |
| Frontend clear color | `0x00540f88` / `0x140f88` | `3f 1f 1f 00` = `0x001f1f3f` | Red `1f 1f bf 00`, green `1f bf 1f 00`, or black | Clear color only |
| Goodies display override | `0x0045d7f4` / `0x05d7f4` | `e8 97 7c 00 00 f7 d8 1b c0` | `83 c4 04 83 c8 ff 90 90 90` | Forces display flag; does not change save progression |
| Pause default O-key experiment | `0x005144cd` / `0x1144cd` | `01` | `18` | O opened pause; Enter resumed in one controlled session |
| Free-camera cheat gate | `0x0046f83c` / `0x06f83c` | `0f 84 58 02 00 00` | six NOPs | Toggle proved; broad safety not proved |
| Version format pointer | file `0x06416f` | Catalog is authority | Redirect to cave string | Paired with next row |
| Version cave payload | file `0x1aa444` | clean cave | `V%1d.%02d - PATCHED` | One title/menu smoke |
| Widescreen main hook | `0x004506ce` plus 27 other regions | Historical 28-region / 191-byte patch | Config/FOV/cave logic | Historical patched Program; validate each region before reuse |

### The corrected `-forcewindowed` mechanism

`DAT_00662f3e` is **not a file byte**. It lies in the uninitialized tail of
`.data` and starts at zero. File offset `0x262f3e` is unrelated `.rsrc` data;
editing it corrupts a resource and cannot affect the parser.

The guard is `CCLIParams+0x186`. Its only writer is:

```asm
00423c7d  c6 83 86 01 00 00 01   mov byte ptr [ebx+0x186],1
```

That path recognizes `-testeur`. The later `-forcewindowed` comparison reads
the guard at `0x00424150`, then writes `mForceWindowed` at object `+0x38`.
Arguments are processed in order, so an unpatched invocation must be:

```text
-testeur -forcewindowed
```

with `-testeur` first. This ordering was observed to produce a 640×480 client
window on the unpatched baseline image. The startup-flow patch remains the deterministic
copied-profile route.

### Patch doctrine

- Hash and size-gate the clean target.
- Patch only an app-owned safe copy.
- Verify exact original bytes before writing.
- Read back exact intended bytes.
- Keep mutually exclusive rows mutually exclusive.
- Treat a runtime smoke as proof only of the exercised screen/path.
- Roll back from the verified pristine backup, never by guessing bytes.

## Function-note corpus: depth, coverage, and contradictions

The per-function notes are substantial but sparse:

| Measure | Value |
| --- | ---: |
| Markdown files under `functions/` | 323 |
| Function-note documents | 322, plus `_index.md` |
| Lines | 18,000 across the 322 notes; `_index.md` adds 157, for 18,157 across all 323 Markdown files |
| Approximate bytes | 996,882 |
| Inferred source/owner groups | 77 |
| Documents in the legacy header backlog | 315 / 323 |
| Documents with explicit `Last updated:` metadata | 21 |

### Three different coverage measures

| Definition | Current functions covered | Percent of 7,555 |
| --- | ---: | ---: |
| Extracted by the current strict checker | 974 | 12.892% |
| Clear identity assertions after also recognizing supported heading/property forms | 1,027 | 13.594% |
| Entry address mentioned anywhere, including callers/context | 1,285 | 17.009% |

Therefore 6,528 current functions lack a clear identity entry, and 6,270 have
no exact entry-address mention anywhere in the corpus.

The current strict run reports:

```text
documents scanned      322
table rows             7,555
assertions resolved    1,200
  current              1,193
  accepted supersede   7
  drifted              0
  unresolved           0
skipped non-.text      241
zero-assertion docs    0
```

That PASS does not mean the prose is current or semantically consistent:

- It reads the tracked name table, which is one live rename behind.
- It requires at least one extracted assertion, not complete extraction.
- `DXFrontEndVideo.cpp.md`, `globals.md`, and `string-locations-index.md` can
  pass entirely through non-text assertions.
- Fourteen `Address:`/`Ghidra Name:` blocks in DXFrontEndVideo were outside the
  old coverage interpretation.
- Thirty-one current function-address headings are not gated: 13 in
  DXBattleLine, nine in DXParticleTexture, and eight in DXTrees, plus another
  current heading in the measured set.
- Thirty-one accepted assertions are interior addresses rather than function
  starts.
- For 67 non-contiguous bodies, a min/max-envelope lookup can assign an address
  in a body gap to the wrong function.

### Hand-verified live contradictions that evade the checker

| Note | Contradiction |
| --- | --- |
| `DXBattleLine.cpp.md` | `0x0053a120` is written as `CDXBattleLine__scalar_deleting_dtor`, current live is `CBLTexture__scalar_deleting_dtor`; `0x005572c0` is written `CTextureSequence__ReleaseIfLoaded`, live is `CDXTexture__ReleaseIfLoaded`; `0x00556fc0` is written `CDXSurf__SetupSurface`, live is `CDXTexture__SetupSurface`. Active prose also retains multiple superseded `FUN_*` labels. |
| `Sentinel.cpp.md` | Its correction table assigns `0x004dec00` to `CSentinelAI__ScalarDeletingDestructor`; its secondary-vtable table and summary still call it `CSentinel__ScalarDeletingDestructor`. |
| `MissionScript/ScriptEventNB.cpp.md` | Correction/current list says `0x005385e0 IScript__HandleMessage` and demotes `0x005386d0` to `DestructorBody_005386d0`; later headings/pseudocode still present `CScriptEventNB__HandleMessage` and `CScriptEventNB__Destructor`. |
| `HeightField.cpp/CHeightField__Load.md` | Live relation table uses `CMemoryManager::Free/Alloc` instead of `CDXMemoryManager__Free/Alloc`, and `StreamReader::GetTag/Read` instead of `CChunkReader__GetNext/Read`; pseudocode also retains `DebugPrint` where current correction says `DebugTrace`. |
| `MissionScript/DataType.cpp.md` | `0x0052f430` is corrected to `CThingPtrDataType__Print`, but the main table places it under `CStringDataType` and describes a string value. |
| `MissionScript/IScript.cpp.md` | `0x005362a0` is current `IScript__GetWorldTextSlotTimerValue`; purpose prose still says text-width calculation. The shipped command table now identifies the handler binding as `GetVariable`, requiring adjudication rather than either description being accepted. |
| `AsmInstruction.cpp.md` | Current identity `CInstructionOP_RETURN__ExecutePop` is described as the POP executor; RTTI proves opcode `0x17` is RETURN and `0x06` is POP. |
| `Carver.cpp.md` | Predicate was corrected from Above to AtOrBelow, while active prose still says the above-threshold path returns 1; `OnHit` and `Fire` moved from `CCarverAI` to `CCarver`, but active rows retain the old owner. |
| `DXSurf.cpp.md` and DXBattleLine | Corrections put `0x00556d90` and `0x00556e70` inside `CDXTexture__Destructor`; active text still presents `0x00556d90` as a real `CDXSurf__dtor`. |
| `DXParticleTexture.cpp.md` | Active prose retains superseded `FUN_00501310`, `FUN_00513a50`, `FUN_00513e20`, `FUN_00514010`, `FUN_00515970`, `FUN_00558690`, and `OID__FreeObject`. |
| Symtab / FrontEnd / ThunderHead | Current allocator identity is `CDXMemoryManager__Alloc`; pseudocode uses `OID__AllocObject` or `MemoryManager_Alloc`. These may be conceptual aliases, but they are unsafe canonical identities. |
| `string-locations-index.md` | Claims 196 paths early and 169 later; its tables actually contain 150 rows: 124 alphabetical, seven MissionScript, 19 DX. “10 processed / ~159 remaining” is a stale 2025 snapshot. |
| `DXFrontEndVideo.cpp.md` | Heading says 12 functions; there are 14 address/name property blocks, all matching the current table. |

Intentional historical sections in DXFMV, DXPatchManager, ScriptObjectCode, and
Bomber are not live contradictions when they are explicitly marked historical.
The DXSnow interior split at `0x0055515e` is also documented history, not a
current function entry.

### Canonical note representation

Future consolidation should remain address-keyed and distinguish:

```text
kind: entry | interior | data | string | callsite
evidence: retail-static | RTTI | shipped-data | source | runtime | inference
status: measured | source-aligned | inferred | unknown | contradicted | historical
```

Superseded labels belong in an alias/history field, never in the current-name
cell. Relationships, globals, and constants are sparse documented facts, not a
claim of a complete call graph or memory model.

## Ghidra tooling and mutation safety

The repository contains 28 Java Ghidra scripts, three Ghidra-oriented Python
utilities, and two shell wrappers. Root package tests do not exercise these
scripts, so each run must carry its own canary/readback evidence.

### Principal read/export scripts

| Script | Purpose / caveat |
| --- | --- |
| `DiagnoseAddressListingState.java` | Classifies candidate address as function, instruction/no-function, undefined, or defined data |
| `DumpAsciiNeedleXrefs.java` | Finds shipped string references |
| `DumpCStringAtAddress.java` | Reads a bounded C string |
| `DumpDisassemblyRange.java` | Exact instruction window |
| `DumpPointerTable.java` | Bounded pointer-table read |
| `ExportFullFunctionInventory.java` | Full metadata; `bodyDigest` is range-text digest, not byte digest |
| `ExportFunctionBodyInstructionsByAddress.java` | Function-owned instruction export |
| `ExportFunctionMetadataByAddress.java` | Exact selected-row readback |
| `ExportFunctionsByAddressDecompile.java` | Selected decompile; 60-second timeout |
| `ExportFunctionsByPrefixDecompile.java` | Prefix decompile; 45-second timeout |
| `ExportFunctionTagsByAddress.java` | Selected tag readback |
| `ExportWeakFunctionList.java` | Weak/default-name queue |
| `ExportInstructionsAroundAddresses.java` | Context windows |
| `ExportInstructionsByOperandToken.java` | Operand/token search |
| `ExportLooseInstructions.java` | Listing instructions outside functions |
| `ExportRenderStateCallSites.java` | D3D state callsite census |
| `ExportScalarReferences.java` | Immediate/scalar references |
| `ExportVtableSlots.java` | Vtable targets |
| `ExportXrefsForAddresses.java` | Selected xrefs |
| `ResolveVtableTypeNames.java` | MSVC RTTI owner resolution |
| `GhidraProjectOpenProbe.java` | Read-only project-open verification |
| `ListAnalysisOptions.java` | Analyzer-state inventory |

### Mutators and sharp edges

| Tool | Safety issue |
| --- | --- |
| `CreateFunctionsFromAddressList.java` | An absent mode defaults to **apply**, not dry-run |
| `GhidraBatchRename.java` | Java script defaults dry, but the map has no built-in old-name/specimen/project binding |
| Comment/tag appliers | Default dry and can require expected name, but an apply can partially complete a batch |
| `GhidraApplyReviewedCorrections.java` | Hard-bound to its historical plan; not a generic current mutator |
| `RunIsolatedAnalyzer.java` | Mutates; use only on a disposable canary |
| `run_ghidra_headless_postscript.sh` | Does not add `-readOnly` |
| `run_ghidra_batch_rename_headless.sh` | Wrapper defaults to apply and lacks `-readOnly` |
| `ghidra_rename_map_preflight.py` | Checks syntax only; does not bind map rows to current database state |
| `ghidra_inventory_diff.py` | Has a hard-coded image base and uses `USER_DEFINED` as a danger proxy; review its assumptions |

`ghidra_project_backup.py` is the strongest safety owner: it checks disjoint
source/destination paths, validates project structure, hashes every file, and
performs a read-only open verification.

### Required safe workflow

1. Identify the exact Program object, specimen hash, database/export hash, and
   target addresses.
2. Stop Ghidra/Java processes and confirm no project lock.
3. Copy to an explicit disposable directory; never experiment on the live
   project or tracked snapshot.
4. Export baseline with `analyzeHeadless ... -process BEA.exe -noanalysis
   -readOnly`.
5. Run syntax/precondition checks and a dry pass.
6. Apply a small canary to the disposable project.
7. Reopen read-only and compare address, bounds, name, signature, comment,
   tags, sources, program counts, and danger classes.
8. Take a verified pre-live backup.
9. Apply only the reviewed map to live; no opportunistic nearby edits.
10. Read back every intended field exactly and run a whole-database diff.
11. Take a verified post-live backup.
12. Treat promotion from live into `reverse-engineering/ghidra/` as a separate
    authorized action.

The July 28 trace apply is the model: one rename and 17 comments were dry-run,
applied, read back byte-for-byte, and compared across the whole database. It
changed no functions, boundaries, or danger-graded rows.

### Historical provenance gaps

- Of the old raw 257-address R4 queue, 33 are now function starts and 224 are
  not. Thirty-two of the 33 predate the July 27 creation waves, but the exact
  creator run/apply log does not survive. This is a real provenance gap.
- A separate loose-AIF queue retains 58 starts, of which 18 are EH-shaped.
- These queues can overlap current MissionScript, gap, or RTTI cohorts. Never
  add them together without address-set joins.
- Historical `state/correction-ops.json` contains an old
  `mutation.authorized=true,target=none`. It is spent state, not current
  authorization.
- Fullbreadth handoff/queue tokens are historical outcomes, not standing work
  or permission.

## Canonical progress queue

This queue is discrete. Counts are address-set counts from the dated current
inventory unless labelled historical. Cohorts may overlap and must be joined by
address before rollup.

### P0: establish current executable coverage

The only byte/body coverage proof is for 6,411 functions. Since then 1,144
functions were added. Current `.text` body coverage is **UNKNOWN**.

Completion bar:

1. fresh read-only full function+instruction export from the live 7,555+ DB;
2. every exported instruction byte checked against the unpatched baseline image;
3. interval-union coverage over the PE `.text` virtual-size denominator;
4. overlaps and fragmented bodies reported separately;
5. uncovered runs reclassified after subtracting current bodies;
6. old 79.8268%, 284,815 non-padding bytes, 621 UNKNOWN runs, and 51,189
   UNKNOWN bytes retained only as dated baselines.

### P0: adjudicate the shipped MissionScript registry

| Cohort | Count | Completion bar |
| --- | ---: | --- |
| Handler entry absent as a function | 86 | Create on disposable canary, prove non-overlap and valid extent, apply/read back, then name from exact shipped binding |
| Existing `FUN_*` with shipped name | 15 | Per-row prototype/body check, reviewed rename, exact readback |
| Current name differs from shipped command | 24 | Determine handler identity vs command binding; do not rename shared stubs or erase stronger behavioral names |

This is the cleanest currently known shipped-name recovery surface. It is not
“101 automatic renames”: the 24 mismatches need semantic adjudication, and
`SetSpeed` proves why.

### P0: repair known false live identities

- the six byte/RTTI-refuted names listed above;
- D3D setters/material/fog/clip functions at `0x00513a50`, `0x00513820`,
  `0x00513870`, `0x005138b0`, `0x00513930`, `0x004eb9a0`, `0x004eba30`,
  `0x005513d0`, and `0x00514030`;
- `CCockpit__Render 0x0053bb50` and the wrong-owner cockpit cluster
  `0x004247a0`, `0x00424920`, `0x00424990`, `0x00424a00`,
  `0x00424a20`, `0x00424be0`, `0x00424ca0`, `0x004250f0`,
  `0x004254f0`;
- stale `CTree__VFunc_9_004f6080` → evidence-backed `CTree__Init` at
  `0x004f6080`;
- stale active prose in the 13 note families catalogued above.

Completion requires individual bytes/xrefs/receiver evidence, a reviewed old→new
map, canary, live apply, exact readback, grader rerun, and note correction.

### P1: RTTI/name residual

| Queue | Current count |
| --- | ---: |
| `RTTI_CONFLICT` | 27 |
| `RTTI_AMBIGUOUS` | 100 |
| `OWNER_PREFIX_MISSING` | 14 |
| `UNNAMED_RTTI_OWNER` | 12 |
| `UNNAMED_RTTI_TARGET` | 41 |
| other `UNNAMED` | 313 |
| no-comment functions | 608 |
| pinned-source grader's three-cohort weak/unsupported naming residual | 1,867 |

Do not optimize the 29.3% percentage mechanically. Recover evidence: shipped
registries, exact `__FILE__` callsites, RTTI slot ownership, unique strings,
source definitions, imports, controlled behavior, or a principled anonymous
label. A bucket reclassification is not knowledge gained.

### P1: review the 1,144 post-fullpass functions

Run an address-current primary+adversarial review over the exact set difference
between a fresh live export and the original 6,411 addresses. The termination
bar is 1,144/1,144 reviewed with:

- current address/name/bounds;
- body bytes verified;
- naming evidence grade;
- prototype/calling-convention check;
- comment and tag check;
- explicit dispute resolution;
- no reliance on old shard names.

Do not rerun W001–W018 or use their 5,004 `ok` count as a final correctness
score.

### P1: repair semantic-note coverage

Current clear identity-note coverage is 1,027/7,555. The next bar should be
address-ledger completeness, not more prose volume:

1. checker recognizes every supported address/name form;
2. entry, interior, data, string, and callsite addresses are distinct;
3. non-contiguous-body membership is exact;
4. current live export, not the one-name-stale table, is the comparison target;
5. the 13 known contradiction families are clean;
6. each system's finite tables and core functions have an explicit current
   row;
7. coverage counts are regenerated from the ledger.

### P1: runtime questions with sharp falsifiers

| Question | Next decisive instrument |
| --- | --- |
| Physics round + explosion damage combination | Twin Vulcan direct-hit discrimination: 0.081 vs 0.08 vs 0.001, or static consumers of Round `+0x1c` and Explosion `+0x38` |
| Cockpit residual matrix `+0x2c` provenance | Write-watch the field from construction through render |
| Tree mode-4 visibility | Capture exact blend state and texture around the second pass |
| Compass ring-1 tape | Complete non-zero texel census / correct lock |
| Scanner membership semantics | Log each vcall/flag/allegiance gate for all 34 units |
| Normal frontend background | No-`-skipfmv` capture that actually reaches main menu |
| Mirror pass identity | Trace mirror flag, clip plane, cull/fog changes to exact draws |
| Authored-basis initialization | Capture another level with the branch exercised, or prove corpus-wide absence |
| Ambient aircraft behavior | Trace movement, render, sound, and waypoint/script execution after briefing |
| Later mission beats/combat | Extend or record a trace beyond briefing |
| Whole-trace D3D totals | Establish a defensible frame/present denominator before normalization |
| TTD cold-global reliability | Build and validate `!ttdext.index` |

### P2: source and data integration

- Recover the missing pinned-source include graph or explicitly scope each
  source-derived claim to the 106 available files.
- Cross-link every installed resource family in `BEA_DATA.md` to its executable
  loader/registry and parser confidence.
- Complete unit/spawner/component/feature/hazard value-offset maps to the same
  standard as Round/WeaponMode.
- Resolve type-5 MissionScript pointer tokens and position `+0x10`.
- Measure the total thing-definition record size before applying a Ghidra type.
- Reconcile audio/video stream ownership and Bink audio language mapping.

### Progress update protocol

When this master changes:

1. refresh current database/export and specimen hashes;
2. state the exact dated denominator;
3. update finite-table status counts by address join;
4. preserve withdrawn claims only in a short supersession note;
5. keep unknowns and falsifiers explicit;
6. never roll a historical coverage percentage forward;
7. never use `USER_DEFINED`, fullpass `confirm`, source similarity, or
   reconstruction agreement as a substitute for released-behavior evidence.

## Appendix A: complete 144-entry MissionScript native registry

Source: `local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv`,
SHA-256
`42027AF22E1D4A0611BF7286FD1EA0DF17ADF01F7BF54AD5A2196F8484F40D86`.
Name/handler bindings are pristine-image evidence; the Ghidra/status columns
describe the current 2026-07-28 live readback and will move after adjudication.

| Index | Record | Handler | Shipped name | Current Ghidra name | Status |
| ---: | --- | --- | --- | --- | --- |
| 0 | `0x0064ce20` | `0x00537d70` | `FollowWaypoint` | — | `NO_FUNCTION` |
| 1 | `0x0064ce60` | `0x00537e40` | `FollowWaypointWait` | — | `NO_FUNCTION` |
| 2 | `0x0064cea0` | `0x00453ac0` | `SetSpeed` | `SharedVFunc__NoOp_Ret0C` | `CONTRADICTED` |
| 3 | `0x0064cee0` | `0x00536cd0` | `SpawnThing` | `IScript__SpawnThing` | `MATCH` |
| 4 | `0x0064cf20` | `0x00537c70` | `Pause` | `FUN_00537c70` | `WEAK` |
| 5 | `0x0064cf60` | `0x005383c0` | `PostEvent` | `IScript__ScheduleEvent` | `CONTRADICTED` |
| 6 | `0x0064cfa0` | `0x00538230` | `Rand` | — | `NO_FUNCTION` |
| 7 | `0x0064cfe0` | `0x00537fd0` | `IsFriendly` | `IScript__IsFriendly` | `MATCH` |
| 8 | `0x0064d020` | `0x005381a0` | `LevelLost` | `IScript__LevelLost` | `MATCH` |
| 9 | `0x0064d060` | `0x005381e0` | `LevelWon` | `IScript__LevelWon` | `MATCH` |
| 10 | `0x0064d0a0` | `0x005381f0` | `PlaySample` | `FUN_005381f0` | `WEAK` |
| 11 | `0x0064d0e0` | `0x00537ad0` | `Print` | `FUN_00537ad0` | `WEAK` |
| 12 | `0x0064d120` | `0x00536920` | `Exists` | — | `NO_FUNCTION` |
| 13 | `0x0064d160` | `0x00535cd0` | `Die` | — | `NO_FUNCTION` |
| 14 | `0x0064d1a0` | `0x005367c0` | `GetThingRef` | — | `NO_FUNCTION` |
| 15 | `0x0064d1e0` | `0x00535d50` | `Activate` | — | `NO_FUNCTION` |
| 16 | `0x0064d220` | `0x00537c40` | `PrintText` | `IScript__PrintText` | `MATCH` |
| 17 | `0x0064d260` | `0x00537410` | `AddMessage` | `IScript__PlaySound` | `CONTRADICTED` |
| 18 | `0x0064d2a0` | `0x00535920` | `GetHealth` | — | `NO_FUNCTION` |
| 19 | `0x0064d2e0` | `0x005358e0` | `SetTimer` | — | `NO_FUNCTION` |
| 20 | `0x0064d320` | `0x00536070` | `GetDistToObj` | `FUN_00536070` | `WEAK` |
| 21 | `0x0064d360` | `0x005363e0` | `GetPlayer` | `IScript__GetPlayerBattleEngine` | `MATCH` |
| 22 | `0x0064d3a0` | `0x00535ea0` | `SetVisible` | — | `NO_FUNCTION` |
| 23 | `0x0064d3e0` | `0x00535ed0` | `SetObjective` | — | `NO_FUNCTION` |
| 24 | `0x0064d420` | `0x005361a0` | `SetAIState` | — | `NO_FUNCTION` |
| 25 | `0x0064d460` | `0x00536350` | `IsA` | — | `NO_FUNCTION` |
| 26 | `0x0064d4a0` | `0x005369b0` | `Teleport` | — | `NO_FUNCTION` |
| 27 | `0x0064d4e0` | `0x00535890` | `PlayCutscene` | `FUN_00535890` | `WEAK` |
| 28 | `0x0064d520` | `0x00537500` | `PlayCharMessage` | `IScript__PlaySoundWithCallback` | `CONTRADICTED` |
| 29 | `0x0064d560` | `0x00535d60` | `Deactivate` | — | `NO_FUNCTION` |
| 30 | `0x0064d5a0` | `0x00535ee0` | `UnsetObjective` | — | `NO_FUNCTION` |
| 31 | `0x0064d5e0` | `0x00535ef0` | `IsObjective` | — | `NO_FUNCTION` |
| 32 | `0x0064d620` | `0x00535f70` | `SetVulnerable` | — | `NO_FUNCTION` |
| 33 | `0x0064d660` | `0x00535d70` | `NumContained` | — | `NO_FUNCTION` |
| 34 | `0x0064d6a0` | `0x00535e60` | `HighlightHudPart` | — | `NO_FUNCTION` |
| 35 | `0x0064d6e0` | `0x00535e80` | `UnHighlightHudPart` | — | `NO_FUNCTION` |
| 36 | `0x0064d720` | `0x005375f0` | `PlayCharMessageWait` | `IScript__PlaySoundWithFade` | `CONTRADICTED` |
| 37 | `0x0064d760` | `0x00535610` | `GetWeaponAmmo` | — | `NO_FUNCTION` |
| 38 | `0x0064d7a0` | `0x00535670` | `GetWeaponName` | `IScript__GetThingName` | `CONTRADICTED` |
| 39 | `0x0064d7e0` | `0x00535750` | `GetWeaponCharge` | — | `NO_FUNCTION` |
| 40 | `0x0064d820` | `0x00535590` | `GetNumUnits` | — | `NO_FUNCTION` |
| 41 | `0x0064d860` | `0x00535560` | `SetAllegiance` | `IScript__SetFactionForHierarchy_FromArg` | `CONTRADICTED` |
| 42 | `0x0064d8a0` | `0x00538300` | `SetWindVector` | — | `NO_FUNCTION` |
| 43 | `0x0064d8e0` | `0x00538360` | `SetRainDensity` | — | `NO_FUNCTION` |
| 44 | `0x0064d920` | `0x00538380` | `SetSnowDensity` | — | `NO_FUNCTION` |
| 45 | `0x0064d960` | `0x005383a0` | `SetLightningDensity` | — | `NO_FUNCTION` |
| 46 | `0x0064d9a0` | `0x00535c10` | `SetHealth` | — | `NO_FUNCTION` |
| 47 | `0x0064d9e0` | `0x005353a0` | `GetRatioBattleLineNodes` | `FUN_005353a0` | `WEAK` |
| 48 | `0x0064da20` | `0x00535c50` | `SetScript` | — | `NO_FUNCTION` |
| 49 | `0x0064da60` | `0x00536c00` | `GetPos` | — | `NO_FUNCTION` |
| 50 | `0x0064daa0` | `0x00536b70` | `SpawnParticle` | — | `NO_FUNCTION` |
| 51 | `0x0064dae0` | `0x00535480` | `SetSegmentHealth` | — | `NO_FUNCTION` |
| 52 | `0x0064db20` | `0x00535500` | `SetAllSegmentsHealth` | — | `NO_FUNCTION` |
| 53 | `0x0064db60` | `0x00535160` | `PlayAnimation` | — | `NO_FUNCTION` |
| 54 | `0x0064dba0` | `0x005351d0` | `PlayAnimationWait` | — | `NO_FUNCTION` |
| 55 | `0x0064dbe0` | `0x00534ac0` | `GetMapHeight` | `ScriptCommand__SampleStaticShadowHeight_00534ac0` | `CONTRADICTED` |
| 56 | `0x0064dc20` | `0x00534b30` | `GetWaterHeight` | `FUN_00534b30` | `WEAK` |
| 57 | `0x0064dc60` | `0x00534b80` | `GetX` | `IScript__GetVectorX` | `CONTRADICTED` |
| 58 | `0x0064dca0` | `0x00534c10` | `GetY` | `IScript__GetVectorY` | `CONTRADICTED` |
| 59 | `0x0064dce0` | `0x00534ca0` | `GetZ` | `IScript__GetVectorZ` | `CONTRADICTED` |
| 60 | `0x0064dd20` | `0x00534d30` | `SetX` | `FUN_00534d30` | `WEAK` |
| 61 | `0x0064dd60` | `0x00534dc0` | `SetY` | — | `NO_FUNCTION` |
| 62 | `0x0064dda0` | `0x00534e50` | `SetZ` | — | `NO_FUNCTION` |
| 63 | `0x0064dde0` | `0x00534ee0` | `SetGoalPoint` | — | `NO_FUNCTION` |
| 64 | `0x0064de20` | `0x005350b0` | `GetSafePos` | — | `NO_FUNCTION` |
| 65 | `0x0064de60` | `0x005349b0` | `GetComponent` | — | `NO_FUNCTION` |
| 66 | `0x0064dea0` | `0x00534910` | `CreatePosition` | — | `NO_FUNCTION` |
| 67 | `0x0064dee0` | `0x00538290` | `GetFloatRand` | — | `NO_FUNCTION` |
| 68 | `0x0064df20` | `0x005348f0` | `SetVar` | — | `NO_FUNCTION` |
| 69 | `0x0064df60` | `0x005348c0` | `Damage` | `FUN_005348c0` | `WEAK` |
| 70 | `0x0064dfa0` | `0x00534770` | `GameTime` | — | `NO_FUNCTION` |
| 71 | `0x0064dfe0` | `0x00538060` | `IsEnemy` | — | `NO_FUNCTION` |
| 72 | `0x0064e020` | `0x005361d0` | `Land` | — | `NO_FUNCTION` |
| 73 | `0x0064e060` | `0x00535a90` | `SpawnersEmpty` | — | `NO_FUNCTION` |
| 74 | `0x0064e0a0` | `0x005361f0` | `Dive` | — | `NO_FUNCTION` |
| 75 | `0x0064e0e0` | `0x00536210` | `Surface` | — | `NO_FUNCTION` |
| 76 | `0x0064e120` | `0x00536230` | `InitVariable` | — | `NO_FUNCTION` |
| 77 | `0x0064e160` | `0x00536260` | `SetVariable` | — | `NO_FUNCTION` |
| 78 | `0x0064e1a0` | `0x00536330` | `ShutdownVariable` | `FUN_00536330` | `WEAK` |
| 79 | `0x0064e1e0` | `0x00535d00` | `Shutdown` | — | `NO_FUNCTION` |
| 80 | `0x0064e220` | `0x00535bb0` | `GetEnergy` | — | `NO_FUNCTION` |
| 81 | `0x0064e260` | `0x005362a0` | `GetVariable` | `IScript__GetWorldTextSlotTimerValue` | `CONTRADICTED` |
| 82 | `0x0064e2a0` | `0x00535d30` | `Retreat` | — | `NO_FUNCTION` |
| 83 | `0x0064e2e0` | `0x005343e0` | `PrimaryObjectiveComplete` | `IScript__PrimaryObjectiveComplete` | `MATCH` |
| 84 | `0x0064e320` | `0x00534410` | `SecondaryObjectiveComplete` | `IScript__SecondaryObjectiveComplete` | `MATCH` |
| 85 | `0x0064e360` | `0x005343c0` | `AddScore` | — | `NO_FUNCTION` |
| 86 | `0x0064e3a0` | `0x00535fa0` | `Attack` | `IScript__Attack` | `MATCH` |
| 87 | `0x0064e3e0` | `0x00534440` | `PrimaryObjectiveFailed` | `IScript__PrimaryObjectiveFailed` | `MATCH` |
| 88 | `0x0064e420` | `0x00534470` | `SecondaryObjectiveFailed` | `IScript__SecondaryObjectiveFailed` | `MATCH` |
| 89 | `0x0064e460` | `0x00534680` | `GetAngle` | — | `NO_FUNCTION` |
| 90 | `0x0064e4a0` | `0x005377e0` | `PlayPCharMessage` | `IScript__PlaySoundWithPriority` | `CONTRADICTED` |
| 91 | `0x0064e4e0` | `0x005378e0` | `PlayPCharMessageWait` | `IScript__PlaySoundWithFadeAndPriority` | `CONTRADICTED` |
| 92 | `0x0064e520` | `0x00535a30` | `GetInitialHealth` | — | `NO_FUNCTION` |
| 93 | `0x0064e560` | `0x00535af0` | `SpawnersInUse` | — | `NO_FUNCTION` |
| 94 | `0x0064e5a0` | `0x00535ca0` | `SetSpawnScript` | — | `NO_FUNCTION` |
| 95 | `0x0064e5e0` | `0x00534f30` | `Stop` | — | `NO_FUNCTION` |
| 96 | `0x0064e620` | `0x00534f70` | `Deploy` | — | `NO_FUNCTION` |
| 97 | `0x0064e660` | `0x00534f90` | `Undeploy` | — | `NO_FUNCTION` |
| 98 | `0x0064e6a0` | `0x00534fb0` | `EnableWeapon` | `IScript__SetThingValueViaVFunc198_FromArg` | `CONTRADICTED` |
| 99 | `0x0064e6e0` | `0x00534fe0` | `DisableWeapon` | `IScript__SetThingValueViaVFunc19C_FromArg` | `CONTRADICTED` |
| 100 | `0x0064e720` | `0x00535070` | `EnableFlightMode` | — | `NO_FUNCTION` |
| 101 | `0x0064e760` | `0x00535090` | `DisableFlightMode` | — | `NO_FUNCTION` |
| 102 | `0x0064e7a0` | `0x005365c0` | `GetSquad` | `FUN_005365c0` | `WEAK` |
| 103 | `0x0064e7e0` | `0x005366c0` | `GetTarget` | — | `NO_FUNCTION` |
| 104 | `0x0064e820` | `0x00534500` | `Normalise` | — | `NO_FUNCTION` |
| 105 | `0x0064e860` | `0x005345d0` | `Magnitude` | `IScript__GetVectorLength` | `CONTRADICTED` |
| 106 | `0x0064e8a0` | `0x005381c0` | `LevelLostString` | `IScript__LevelLostString` | `MATCH` |
| 107 | `0x0064e8e0` | `0x00535b50` | `IsFiring` | — | `NO_FUNCTION` |
| 108 | `0x0064e920` | `0x005347b0` | `IsNumberBetween` | `IScript__CheckValueInRange` | `CONTRADICTED` |
| 109 | `0x0064e960` | `0x00534300` | `SetSegmentVulnerable` | — | `NO_FUNCTION` |
| 110 | `0x0064e9a0` | `0x00534390` | `SetAllSegmentsVulnerable` | — | `NO_FUNCTION` |
| 111 | `0x0064e9e0` | `0x005359d0` | `GetRealHealth` | — | `NO_FUNCTION` |
| 112 | `0x0064ea20` | `0x005342c0` | `SwitchMessagesOn` | — | `NO_FUNCTION` |
| 113 | `0x0064ea60` | `0x005342e0` | `SwitchMessagesOff` | — | `NO_FUNCTION` |
| 114 | `0x0064eaa0` | `0x00533b70` | `Goto3PointPanCamera` | `IScript__Create3PointPanCamera` | `CONTRADICTED` |
| 115 | `0x0064eae0` | `0x00533eb0` | `Goto4PointPanCamera` | `IScript__Create4PointPanCamera` | `CONTRADICTED` |
| 116 | `0x0064eb20` | `0x005342b0` | `GotoPlayerCamera` | — | `NO_FUNCTION` |
| 117 | `0x0064eb60` | `0x005357b0` | `GetConfiguration` | `IScript__GetThingTypeName` | `CONTRADICTED` |
| 118 | `0x0064eba0` | `0x00533b30` | `AddHelpMessage` | `FUN_00533b30` | `WEAK` |
| 119 | `0x0064ebe0` | `0x00533a70` | `SetGoodieState` | `IScript__SetGoodieState` | `MATCH` |
| 120 | `0x0064ec20` | `0x00533aa0` | `GetGoodieState` | `IScript__GetGoodieState` | `MATCH` |
| 121 | `0x0064ec60` | `0x00533a40` | `MPDeclarePlayerWon` | `FUN_00533a40` | `WEAK` |
| 122 | `0x0064eca0` | `0x00533a60` | `MPDeclareGameDrawn` | — | `NO_FUNCTION` |
| 123 | `0x0064ece0` | `0x005338d0` | `SetSlot` | `IScript__SetSlot` | `MATCH` |
| 124 | `0x0064ed20` | `0x005339a0` | `GetSlot` | `IScript__GetSlotBitValue` | `MATCH` |
| 125 | `0x0064ed60` | `0x005380f0` | `InJetMode` | — | `NO_FUNCTION` |
| 126 | `0x0064eda0` | `0x005338a0` | `SetPlayerLives` | `IScript__SetPlayerLives` | `MATCH` |
| 127 | `0x0064ede0` | `0x005344a0` | `Launch` | `FUN_005344a0` | `WEAK` |
| 128 | `0x0064ee20` | `0x00534370` | `HalfDestroy` | — | `NO_FUNCTION` |
| 129 | `0x0064ee60` | `0x00534340` | `SetVelocity` | — | `NO_FUNCTION` |
| 130 | `0x0064eea0` | `0x00536ca0` | `TriggerHitEffect` | `IScript__TriggerHitEffect` | `MATCH` |
| 131 | `0x0064eee0` | `0x00535980` | `GetNumber` | — | `NO_FUNCTION` |
| 132 | `0x0064ef20` | `0x005371e0` | `SpawnEscapePod` | — | `NO_FUNCTION` |
| 133 | `0x0064ef60` | `0x00533900` | `SetSlotSave` | `IScript__SetSlotSave` | `MATCH` |
| 134 | `0x0064efa0` | `0x005354c0` | `ResetSegmentHealth` | — | `NO_FUNCTION` |
| 135 | `0x0064efe0` | `0x00536c70` | `SetPos` | — | `NO_FUNCTION` |
| 136 | `0x0064f020` | `0x00533950` | `SetLockable` | `FUN_00533950` | `WEAK` |
| 137 | `0x0064f060` | `0x00533980` | `ToggleCockpit` | — | `NO_FUNCTION` |
| 138 | `0x0064f0a0` | `0x00535530` | `SetStealth` | `IScript__SetThingFloatViaVFunc1C8_FromArg` | `CONTRADICTED` |
| 139 | `0x0064f0e0` | `0x00536a60` | `TeleportOrientation` | — | `NO_FUNCTION` |
| 140 | `0x0064f120` | `0x00535010` | `EnableSpawner` | `IScript__SetThingValueViaEngineHelper4FE390_FromArg` | `CONTRADICTED` |
| 141 | `0x0064f160` | `0x00535040` | `DisableSpawner` | `IScript__SetThingValueViaEngineHelper4FE3F0_FromArg` | `CONTRADICTED` |
| 142 | `0x0064f1a0` | `0x00535c70` | `SetName` | — | `NO_FUNCTION` |
| 143 | `0x0064f1e0` | `0x00538150` | `IsOverWater` | — | `NO_FUNCTION` |

## Appendix B: complete PhysicsScript value maps

These 104 rows close the Round (38), WeaponMode (37), Explosion (15), and
Weapon (14) value registries. They were revalidated against current functions
with zero RTTI class/vtable mismatches and zero missing apply bodies. Durable
Round/WeaponMode source:
[`physics-round-value-ids-2026-07-25.md`](reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md),
SHA-256
`81C435E1DA0F2DC120480E3BFCCFCB45E98A45A5AAB6D3DB5EAA984FCAE57946`.
The cross-family mechanical source is
`local-lab/physics-value-ids-2026-07-25/all_ids.tsv`, SHA-256
`3A682381E570B70481DCB47A09CEA5F19630CB9A07865F6AF0C54089C49DD766`.

### Round: 38 ids, record size `0xa8`, name at `+0x18`

| Id | RTTI class | Vtable | Apply body | Destination |
| ---: | --- | --- | --- | --- |
| `0x01` | `CRoundLifeSpan` | `0x005da570` | `0x004382e0` | `+0x24` |
| `0x02` | `CRoundDamage` | `0x005da548` | `0x004381b0` | `+0x1c` |
| `0x03` | `CRoundVelocity` | `0x005da55c` | `0x00438370` | `+0x2c` |
| `0x04` | `CRoundSeek` | `0x005da534` | `0x004394e0` | `+0x48`, nested |
| `0x05` | `CRoundTurnRate` | `0x005da520` | `0x00438420` | `+0x28` |
| `0x06` | `CRoundGravity` | `0x005da50c` | `0x004384b0` | `+0x3c`; terminal `FSTP 0x00438540` |
| `0x07` | `CRoundBounce` | `0x005da4f8` | `0x00438550` | `+0x30` |
| `0x08` | `CRoundEffect` | `0x005da4e4` | `0x00439710` | `+0x10`, owned string |
| `0x09` | `CRoundExplosion` | `0x005da4bc` | `0x00439910` | `+0x08`, owned string |
| `0x0a` | `CRoundSeekDelay` | `0x005da4a8` | `0x004388f0` | `+0x34` |
| `0x0b` | `CRoundWiggle` | `0x005da480` | `0x00438680` | `+0x38` |
| `0x0c` | `CRoundRadius` | `0x005da3a4` | `0x004385e0` | `+0x8c` |
| `0x0d` | `CRoundFlak` | `0x005da46c` | `0x00438710` | `+0x4c` |
| `0x0e` | `CRoundFlakInaccuracy` | `0x005da458` | `0x004387b0` | `+0x7c`; terminal `FSTP 0x00438840` |
| `0x0f` | `CRoundSeekAngle` | `0x005da494` | `0x00438a20` | `+0x40` |
| `0x10` | `CRoundBeam` | `0x005da444` | `0x00438850` | `+0x50` |
| `0x11` | `CRoundSoundMaterial` | `0x005da430` | `0x00438100` | `+0x80` |
| `0x12` | `CRoundWeirdoSeek` | `0x005da41c` | `0x00439440` | `+0x54` |
| `0x13` | `CRoundRearm` | `0x005da408` | `0x00438240` | `+0x20`; terminal `FSTP 0x004382d0` |
| `0x14` | `CRoundBasedOn` | `0x005da3f4` | `0x00437d00` | bulk field copy |
| `0x15` | `CRoundSeekTerminationTime` | `0x005da3e0` | `0x00438ab0` | `+0x44` |
| `0x16` | `CRoundMissile` | `0x005da2c8` | `0x00438e10` | `+0x70`, flag |
| `0x17` | `CRoundProximity` | `0x005da3cc` | `0x00438980` | `+0x88` |
| `0x18` | `CRoundGridOfFear` | `0x005da3b8` | `0x00438b40` | `+0x58` |
| `0x19` | `CRoundUnderWater` | `0x005da390` | `0x00438bf0` | `+0x5c` |
| `0x1a` | `CRoundGroundHugging` | `0x005da37c` | `0x00438ca0` | `+0x68` |
| `0x1b` | `CRoundPassiveCollision` | `0x005da354` | `0x00439050` | `+0x64` |
| `0x1c` | `CRoundJumps` | `0x005da340` | `0x00439100` | `+0x84` |
| `0x1d` | `CRoundJumpRange` | `0x005da32c` | `0x004391b0` | `+0x90` |
| `0x1e` | `CRoundJumpDelay` | `0x005da318` | `0x00439250` | `+0x94` |
| `0x1f` | `CRoundExplode` | `0x005da304` | `0x00439390` | `+0x74`, flag |
| `0x20` | `CRoundTorpedo` | `0x005da368` | `0x00438d50` | `+0x6c`, flag |
| `0x21` | `CRoundWaterEffect` | `0x005da4d0` | `0x00439800` | `+0x14`, owned string |
| `0x22` | `CRoundFire` | `0x005da2f0` | `0x00438ed0` | `+0x60`, flag |
| `0x23` | `CRoundTreeCollision` | `0x005da2dc` | `0x00439a00` | `+0xa4`, nested |
| `0x24` | `CRoundMesh` | `0x005da2b4` | `0x00439620` | `+0x0c`, owned string |
| `0x25` | `CRoundSmart` | `0x005da2a0` | `0x00438f90` | `+0x78`, flag |
| `0x26` | `CRoundLength` | `0x005da28c` | `0x004392f0` | `+0x98` |

### WeaponMode: 37 ids, record size `0xc0`, name at `+0x30`

Id `0x07` has no factory case.

| Id | RTTI class | Vtable | Apply body | Destination |
| ---: | --- | --- | --- | --- |
| `0x01` | `CWeaponInaccuracy` | `0x005da250` | `0x00435cd0` | `+0x34` |
| `0x02` | `CWeaponRound` | `0x005da1ec` | `0x004370a0` | round reader/index |
| `0x03` | `CWeaponReloadTime` | `0x005da200` | `0x004365f0` | `+0x38` |
| `0x04` | `CWeaponBurstSize` | `0x005da23c` | `0x00435ff0` | `+0x44` |
| `0x05` | `CWeaponBurstDelay` | `0x005da228` | `0x004360a0` | `+0x3c` |
| `0x06` | `CWeaponMuzzleEffect` | `0x005da1d8` | `0x00436410` | `+0x1c`, owned string |
| `0x08` | `CWeaponLaunchSequence` | `0x005da1c4` | `0x00435a00` | list append |
| `0x09` | `CWeaponMinRange` | `0x005da19c` | `0x00436800` | `+0x74` |
| `0x0a` | `CWeaponMaxRange` | `0x005da188` | `0x00436890` | `+0x78` |
| `0x0b` | `CWeaponMinDeflection` | `0x005da174` | `0x00436920` | `+0x7c` |
| `0x0c` | `CWeaponMaxDeflection` | `0x005da160` | `0x004369b0` | `+0x80` |
| `0x0d` | `CWeaponPreFireDelay` | `0x005da138` | `0x004361e0` | `+0x88` |
| `0x0e` | `CWeaponPostFireDelay` | `0x005da124` | `0x00436280` | `+0x8c` |
| `0x0f` | `CWeaponClip` | `0x005da0fc` | `0x00436500` | `+0x00`, owned string |
| `0x10` | `CWeaponLockTime` | `0x005da0e8` | `0x00436c10` | `+0x94` |
| `0x11` | `CWeaponLockDeflection` | `0x005da0d4` | `0x00436cb0` | `+0x98` |
| `0x12` | `CWeaponPreFireEffect` | `0x005da110` | `0x00436320` | `+0x20`, owned string |
| `0x13` | `CWeaponLockMode` | `0x005da0c0` | `0x00436d50` | `+0xa8` |
| `0x14` | `CWeaponLockUnit` | `0x005da0ac` | `0x00436df0` | `+0xa4` |
| `0x15` | `CWeaponLockRange` | `0x005da098` | `0x00436e90` | `+0x9c` |
| `0x16` | `CWeaponMaxLocks` | `0x005da070` | `0x00436fd0` | `+0x90` |
| `0x17` | `CWeaponLockRadius` | `0x005da084` | `0x00436f30` | `+0xa0` |
| `0x18` | `CWeaponLaunchSound` | `0x005da048` | `0x004371c0` | `+0x24`, owned string |
| `0x19` | `CWeaponBasedOn` | `0x005da00c` | `0x00435840` | bulk field copy |
| `0x1a` | `CWeaponMinTargetHeight` | `0x005d9ff8` | `0x00436a50` | `+0x6c` |
| `0x1b` | `CWeaponMaxTargetHeight` | `0x005d9fe4` | `0x00436ae0` | `+0x70` |
| `0x1c` | `CWeaponVolleySize` | `0x005da214` | `0x00436130` | `+0x48` |
| `0x1d` | `CWeaponTrack` | `0x005d9fd0` | `0x00436680` | `+0xac` |
| `0x1e` | `CWeaponYawTolerance` | `0x005da14c` | `0x00436b70` | `+0x84` |
| `0x1f` | `CWeaponLaunchAngle` | `0x005da1b0` | `0x00435b50` | angle triple/list |
| `0x20` | `CWeaponPower` | `0x005d9fbc` | `0x00435d60` | `+0x40` |
| `0x21` | `CWeaponPredictive` | `0x005da264` | `0x00435f30` | `+0xb0`, flag |
| `0x22` | `CWeaponPreFireSound` | `0x005da034` | `0x004372b0` | `+0x28`, owned string |
| `0x23` | `CWeaponSoundPerBurst` | `0x005da05c` | `0x00436740` | `+0xb4` |
| `0x24` | `CWeaponPostFireSound` | `0x005da020` | `0x004373a0` | `+0x2c`, owned string |
| `0x25` | `CWeaponMuzzleLight` | `0x005d9fa8` | `0x00435df0` | `+0xb8` |
| `0x26` | `CWeaponMuzzleLightRadius` | `0x005d9f94` | `0x00435e90` | `+0xbc` |

### Explosion: 15 ids, record size `0x50`, tag 6 → Type 7

Factory: `0x0043a860`.

| Id | RTTI class | Vtable | Apply body | Destination / exact role |
| ---: | --- | --- | --- | --- |
| `0x01` | `CExplosionBasedOn` | `0x005da7dc` | `0x0043abd0` | Bulk/copy path; recovered writes include `+0x48`, `+0x28`, `+0x2c` |
| `0x02` | `CExplosionAirEffect` | `0x005da7c8` | `0x0043afc0` | `+0x18`, owned string |
| `0x03` | `CExplosionRadius` | `0x005da764` | `0x0043b3a0` | `+0x34` |
| `0x04` | `CExplosionDamage` | `0x005da778` | `0x0043b430` | `+0x38` |
| `0x05` | `CExplosionGroundEffect` | `0x005da7b4` | `0x0043b0b0` | `+0x20`, owned string |
| `0x06` | `CExplosionWaterEffect` | `0x005da7a0` | `0x0043b1c0` | `+0x1c`, owned string |
| `0x07` | `CExplosionUnitEffect` | `0x005da78c` | `0x0043b2b0` | `+0x24`, owned string |
| `0x08` | `CExplosionVolumetric` | `0x005da750` | `0x0043b4c0` | `+0x3c` |
| `0x09` | `CExplosionTime` | `0x005da73c` | `0x0043b700` | `+0x40` |
| `0x0a` | `CExplosionSound` | `0x005da728` | `0x0043b790` | `+0x28`, owned string |
| `0x0b` | `CExplosionSmart` | `0x005da714` | `0x0043b550` | `+0x44` |
| `0x0c` | `CExplosionLight` | `0x005da700` | `0x0043b670` | `+0x4c` |
| `0x0d` | `CExplosionOriented` | `0x005da6ec` | `0x0043b5e0` | `+0x48` |
| `0x0e` | `CExplosionShockwave` | `0x005da6d8` | `0x004014c0` | Shared no-op/default slot; no settled explosion-record destination |
| `0x0f` | `CExplosionWaterSound` | `0x005da6c4` | `0x0043b880` | `+0x2c`, owned string |

### Weapon: 14 ids, tag 2 → Type 3

Factory: `0x00434300`.

| Id | RTTI class | Vtable | Apply body | Destination / exact role |
| ---: | --- | --- | --- | --- |
| `0x01` | `CWeaponChargeLevel` | `0x005d9f6c` | `0x00434610` | Complex payload `[i32 chargeLevel][cstring weaponModeName]` |
| `0x02` | `CWeaponChargeRate` | `0x005d9f58` | `0x004347e0` | `+0x08` |
| `0x03` | `CWeaponAmmoStore` | `0x005d9f44` | `0x00434870` | Owned store object at `+0x24`; initializes nested `+0x08` to 5 |
| `0x04` | `CWeaponConsumption` | `0x005d9f30` | `0x00434930` | `+0x20` |
| `0x05` | `CWeaponIconName` | `0x005d9f1c` | `0x00434f20` | String apply; terminal field-object writes at `+0x04/+0x08` |
| `0x06` | `CWeaponSmart` | `0x005d9ecc` | `0x00434aa0` | `+0x30`, boolean |
| `0x07` | `CWeaponAdjustAim` | `0x005d9f08` | `0x004349c0` | `+0x28`, boolean |
| `0x08` | `CWeaponZoomMode` | `0x005d9ef4` | `0x00434b80` | `+0x34` |
| `0x09` | `CWeaponAllowMovement` | `0x005d9ee0` | `0x00434e70` | `+0x2c`, boolean |
| `0x0a` | `CWeaponPlacement` | `0x005d9eb8` | `0x00434c20` | `+0x38` |
| `0x0b` | `CWeaponLanguageName` | `0x005d9ea4` | `0x0043e660` | No single direct terminal store in the mechanical write summary |
| `0x0c` | `CWeaponVersusInfantry` | `0x005d9e90` | `0x00434cc0` | `+0x40` |
| `0x0d` | `CWeaponVersusTanks` | `0x005d9e7c` | `0x00434d50` | `+0x44` |
| `0x0e` | `CWeaponVersusAir` | `0x005d9e68` | `0x00434de0` | `+0x48` |

## Appendix C: function-note owner census

`Gated` means unique current function entries reached by the existing strict
checker. `Mentioned` means current entry addresses appearing anywhere,
including context/callers. Neither column proves full semantic understanding.

| Owner/group | Docs | Lines | Gated | Mentioned |
| --- | ---: | ---: | ---: | ---: |
| AirUnit | 1 | 106 | 2 | 7 |
| AsmInstruction | 1 | 102 | 19 | 20 |
| BattleEngine | 10 | 638 | 10 | 10 |
| BattleEngineConfigurations | 1 | 29 | 1 | 1 |
| BattleEngineJetPart | 11 | 326 | 11 | 11 |
| BattleEngineWalkerPart | 1 | 29 | 1 | 1 |
| Bomber | 1 | 210 | 0 | 7 |
| Career | 40 | 1,471 | 36 | 45 |
| Carrier | 1 | 74 | 2 | 7 |
| Carver | 1 | 129 | 30 | 39 |
| CLIParams | 1 | 135 | 1 | 1 |
| Cockpit | 1 | 32 | 1 | 6 |
| collisionseekingthing | 1 | 82 | 8 | 16 |
| console | 1 | 21 | 1 | 1 |
| Controller | 4 | 213 | 22 | 29 |
| CPhysicsScript | 1 | 72 | 5 | 26 |
| CPhysicsScriptStatements | 1 | 329 | 179 | 266 |
| Credits | 3 | 70 | 3 | 4 |
| DataType | 1 | 301 | 43 | 45 |
| display-settings | 1 | 216 | 17 | 22 |
| DiveBomber | 1 | 65 | 2 | 2 |
| DXBattleLine | 1 | 412 | 19 | 50 |
| DXClouds | 1 | 27 | 2 | 2 |
| DXFMV | 1 | 79 | 6 | 7 |
| DXFrontEndVideo | 1 | 470 | 0 | 31 |
| DXKempyCube | 1 | 88 | 6 | 10 |
| DXMemBuffer | 1 | 176 | 17 | 19 |
| DXPalletizer | 1 | 355 | 9 | 10 |
| DXParticleTexture | 1 | 357 | 15 | 28 |
| DXPatchManager | 1 | 278 | 14 | 27 |
| DXShadows | 1 | 93 | 4 | 3 |
| DXSnow | 1 | 96 | 11 | 13 |
| DXSurf nested notes | 1 | 52 | 4 | 5 |
| DXSurf aggregate | 1 | 103 | 18 | 24 |
| DXTrees | 1 | 394 | 2 | 21 |
| EndLevelData | 1 | 23 | 1 | 4 |
| engine | 7 | 157 | 7 | 27 |
| EventFunction | 1 | 81 | 5 | 5 |
| FEPDebriefing | 1 | 134 | 1 | 1 |
| FEPDemoMain | 1 | 58 | 4 | 7 |
| FEPDevelopment | 1 | 60 | 9 | 12 |
| FEPGoodies | 10 | 430 | 9 | 9 |
| FEPLevelSelect | 1 | 22 | 1 | 1 |
| FEPLoadGame | 5 | 199 | 5 | 8 |
| FEPMain | 1 | 112 | 11 | 14 |
| FEPOptions | 1 | 70 | 1 | 4 |
| FEPSaveGame | 9 | 309 | 9 | 10 |
| flexarray | 1 | 259 | 9 | 10 |
| FrontEnd | 34 | 932 | 52 | 54 |
| game | 62 | 1,507 | 62 | 99 |
| gcgamut | 1 | 252 | 4 | 4 |
| GeneralVolume | 3 | 90 | 3 | 3 |
| globals | 1 | 124 | 0 | 1 |
| GroundUnit | 1 | 57 | 1 | 1 |
| Hazard | 1 | 24 | 1 | 1 |
| HeightField | 3 | 278 | 6 | 9 |
| import-thunks | 1 | 74 | 34 | 39 |
| Infantry | 1 | 106 | 1 | 1 |
| IScript | 1 | 200 | 45 | 48 |
| MCMech | 1 | 158 | 21 | 27 |
| MCTentacle | 1 | 154 | 19 | 22 |
| Mech | 3 | 120 | 3 | 3 |
| monitor.h | 2 | 79 | 2 | 2 |
| PauseMenu | 6 | 234 | 6 | 6 |
| Plane | 3 | 107 | 7 | 7 |
| Platform | 7 | 166 | 7 | 16 |
| Player | 6 | 245 | 13 | 15 |
| Pod | 1 | 23 | 1 | 1 |
| scheduledevent | 2 | 48 | 2 | 5 |
| Script | 2 | 87 | 2 | 7 |
| ScriptEventNB | 1 | 555 | 19 | 22 |
| ScriptObjectCode | 1 | 323 | 31 | 32 |
| Sentinel | 1 | 121 | 12 | 13 |
| SoundManager | 3 | 80 | 3 | 4 |
| string-helpers | 1 | 53 | 15 | 9 |
| string-locations-index | 1 | 298 | 0 | 0 |
| Symtab | 1 | 281 | 11 | 11 |
| text | 9 | 541 | 9 | 10 |
| texture | 3 | 266 | 5 | 9 |
| ThunderHead | 5 | 416 | 10 | 11 |
| tree | 8 | 104 | 8 | 9 |
| Unit | 6 | 251 | 7 | 13 |
| World | 1 | 102 | 1 | 2 |

The apparent cases where `Gated > Mentioned` reflect how the two scans classify
accepted aliases, interior addresses, and aggregate/nested documents; they are
another reason not to treat either column as a semantic completion score.

## Appendix D: superseded claims that must not return

Later evidence has resolved these disagreements. They are listed once here so
the old and new statements are not presented as coequal truth.

| Retired claim | Current verdict |
| --- | --- |
| The `E143…` capture executable is pristine | False; it is pristine plus the force-windowed patch |
| The Ghidra project is never tracked | False as a general statement; `reverse-engineering/ghidra/` is the reviewed tracked exception. Live DBs, backups, and alternates remain untracked. |
| The current function population is 5,771, 6,411, or 6,969 | Historical counts; current live is 7,555 |
| The tracked Ghidra snapshot contains current 7,555-function truth | False; tracked snapshot is 6,411, while the tracked name projection is 7,555 and one rename behind live |
| Current `.text` function coverage is 79.8% | Unknown; 79.8268% is the old 6,411-body baseline |
| Twenty-five fullpass name drifts are unexplained | False after joining both map stores; all 370 are attributed |
| `SpawnThing` reduced the residual to 1,866 | False; fresh current grader remains 1,867 / 6,376 |
| RTTI-confirmed means the whole virtual-method name is correct | False; grader checks prefix ownership, not method suffix or slot number |
| All virtual methods can receive correct names from RTTI | False; multiple inheritance, shared targets, 11/667 types without standalone vftables, and upper-bound-affected targets prevent that |
| `bodyDigest` proves identical function code | False; it hashes address-range text |
| Mission opcode `0x0d` is anonymous `NOOP_0D` | RTTI proves `CInstructionOP_LABEL`; it shares the NOP executor |
| Eight Mission opcode executors remain unpromoted | False; all 27 targets are current functions |
| Type-4/Type-5 PhysicsScript value classes/layouts remain unknown | Superseded by the complete WeaponMode/Round maps |
| Terrain is unlit / receives no live light contribution | False; actual draw state has two enabled lights and measured material law |
| A third light is needed for terrain | Falsified; the three-light rig belongs to a frontend page |
| MMAP per-node colored lighting is active on PC | False; shipped heightfields have null arrays and the builder is a dead offline PS2 path |
| Cloud scroll is 0.001/0.0005 per second and has a 1,000-second cycle | False; measured 0.02/0.01 per second, about 50 seconds |
| Tree modes 2/6/8 or “unlit tree flags” were observed | Not observed in three Level 100 launches; captured paths showed modes 0/4, and `0x0054a423`/`0x0054a466` never fired |
| Cockpit normals face the wrong way | Refuted; contamination came from later HUD overlays |
| Main menu always has 39 draws | False; 39/35 blink states are both measured |
| Click-to-start transition lasts 131 frames or `MAINTIME=70` | False as semantic law; the click-to-start action handler requests the `FEP_MAIN` transition over 50 Process ticks; 131 is a proxy render observation; 70 belongs to a different page path |
| Compass ring-1 tape is empty | Unknown; sparse sampling missed localized ink |
| `0x00513a50` is a cached render-state setter | False; it is cached `SetTexture` |
| `0x004eb9a0` initializes CUnit tuning | False; it initializes two D3DMATERIAL9 records |
| `0x004eba30` configures the vertex-shader path | False; it is mirror clip-plane/enable state |
| `0x005513d0` defers vertex format | False; it defers fog density |
| `0x0053bb50` is a CDXEngine fullscreen-effect helper | False; receiver/caller prove `CCockpit__Render` |
| The cockpit helper cluster belongs to CGeneralVolume/CUnitAI | False; receiver layout and calls prove CCockpit ownership |
| File offset `0x262f3e` is the windowed guard byte | False and harmful; it is `.rsrc`; the guard is BSS and has no file byte |

## Appendix E: evidence map

These are the principal durable or machine-local inputs integrated above.
They remain useful for per-address reproduction; none needs to be read merely
to understand the current verdicts in this master.

### Durable tracked evidence

| Area | Entry point |
| --- | --- |
| RE evidence contract | [`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) |
| Tracked Ghidra snapshot | [`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md) |
| Binary-analysis index | [`reverse-engineering/binary-analysis/_index.md`](reverse-engineering/binary-analysis/_index.md) |
| Current tracked name projection | [`ghidra-function-name-table-2026-07-27.tsv`](reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv) |
| July 13 reviewed plan | [`ghidra-reviewed-correction-plan-2026-07-13.json`](reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json) |
| July 13 closeout | [`ghidra-full-reaudit-closeout-2026-07-13.md`](reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md) |
| Fullpass corpus | [`ghidra-fullpass-findings/README.md`](reverse-engineering/binary-analysis/ghidra-fullpass-findings/README.md) |
| Dated coverage proof | [`re-coverage-baseline-2026-07-25.md`](reverse-engineering/binary-analysis/re-coverage-baseline-2026-07-25.md) |
| Current grading method/history | [`name-grading-ledger-2026-07-26.md`](reverse-engineering/binary-analysis/name-grading-ledger-2026-07-26.md), [`demotion 2`](reverse-engineering/binary-analysis/name-grading-ledger-2026-07-27-demotion2.md) |
| RTTI/source paths | [`rtti-and-source-path-evidence-2026-07-25.md`](reverse-engineering/binary-analysis/rtti-and-source-path-evidence-2026-07-25.md) |
| Function notes | [`functions/_index.md`](reverse-engineering/binary-analysis/functions/_index.md) |
| MissionScript static contract | [`missionscript-iscript-static-contract.md`](reverse-engineering/binary-analysis/missionscript-iscript-static-contract.md) |
| PhysicsScript static contract | [`physics-script-static-contract.md`](reverse-engineering/binary-analysis/physics-script-static-contract.md) |
| Round/WeaponMode map | [`physics-round-value-ids-2026-07-25.md`](reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md) |
| Save format | [`reverse-engineering/save-file/_index.md`](reverse-engineering/save-file/_index.md) |
| Game/system router | [`mapped-systems.md`](reverse-engineering/binary-analysis/mapped-systems.md) |
| High-impact chains | [`high-impact-call-chain-appendix.md`](reverse-engineering/binary-analysis/high-impact-call-chain-appendix.md) |
| BattleEngine movement | [`battleengine-movement-static-crosswalk-2026-07-12.md`](reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md) |
| D3D9 defaults | [`d3d-default-render-state-block-2026-07-27.md`](reverse-engineering/binary-analysis/d3d-default-render-state-block-2026-07-27.md) |
| Fog | [`d3d-fog-render-state-static-contract-2026-07-25.md`](reverse-engineering/binary-analysis/d3d-fog-render-state-static-contract-2026-07-25.md) |
| Terrain evidence | [`terrain-ambient-light-applied-2026-07-26.md`](reverse-engineering/binary-analysis/terrain-ambient-light-applied-2026-07-26.md) and neighboring terrain findings |
| Cockpit lighting/matrix | [`cockpit-lighting-law-2026-07-26.md`](reverse-engineering/binary-analysis/cockpit-lighting-law-2026-07-26.md), [`cockpit-world-matrix-static-2026-07-26.md`](reverse-engineering/binary-analysis/cockpit-world-matrix-static-2026-07-26.md) |
| Camera/FOV | [`player-camera-attach-and-mesh-hfov-2026-07-26.md`](reverse-engineering/binary-analysis/player-camera-attach-and-mesh-hfov-2026-07-26.md) |
| Patch contracts | Focused `*-patch.md` documents in `reverse-engineering/binary-analysis/` and `patches/catalog/patches.v2.json` |

### Machine-local measured evidence

| Area | Path |
| --- | --- |
| Current live Ghidra readback | `local-lab/ghidra-from-trace-2026-07-28/inv-AFTER-functions.tsv` |
| Trace-to-Ghidra apply/readback | `local-lab/GHIDRA-FROM-TRACE-2026-07-28.md` |
| 144 native table | `local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv` |
| Current grader artifacts | `local-lab/re-ledger/` |
| Analyzer canaries | `local-lab/GHIDRA-AGGRESSIVE-ANALYSIS-2026-07-27.md` |
| Mutation-wave evidence | `local-lab/agent-notes-2026-07-27/ghidra-mutation-waves.md` and naming-wave notes |
| Level 100 TTD synthesis | `local-lab/TTD-LEVEL100-FINDINGS-2026-07-28.md` |
| D3D9 sweep | `local-lab/D3D9-FULL-SWEEP-2026-07-27.md` |
| HUD/compass | `local-lab/HUD-BLIND-SPOTS-2026-07-28.md`, `local-lab/COMPASS-GAUGE-BLEND-2026-07-26.md` |
| Frontend corrections | `local-lab/FRONTEND-DRAW-CORRECTIONS-2026-07-27.md` |
| Terrain runtime light | `local-lab/TERRAIN-LIGHT-STATE-RUNTIME-2026-07-26.md` |
| Tree/mesh/terrain lighting | `local-lab/TREE-LIGHTING-RIG-2026-07-26.md`, `local-lab/MESH-LIGHTING-MODE-RUNTIME-2026-07-26.md`, `local-lab/LIT-MESH-LIGHT-STATE-2026-07-26.md` |
| Cockpit runtime/composition | `local-lab/COCKPIT-WORLD-MATRIX-RUNTIME-2026-07-26.md`, `local-lab/COMPOSITION-RESIDUAL-2026-07-26.md` |

Machine-local paths are reproducibility pointers for this workstation, not
publicly distributable artifacts.

## Closing state

The project has crossed from exploratory reverse engineering into a measured
reconstruction corpus: the main architecture, object factories, save container,
script VM, physics registries, D3D9 state machine, terrain law, cockpit
composition, frontend/HUD draw behavior, and one complete Level 100 load path
are all recoverable at useful precision.

The remaining work is not “look at everything again.” It is a finite set of
address-keyed gaps:

```text
current body coverage remeasurement
86 missing shipped-native functions
15 exact weak shipped-native names
24 native/name adjudications
6 known false general names
render/cockpit correction cluster
1,144 post-fullpass functions
1,867-function pinned-source grader residual across its three weak/unsupported cohorts
6,528 functions without a clear semantic note
bounded runtime questions with explicit falsifiers
```

That is the canonical baseline for the next Ghidra campaign.
