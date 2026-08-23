# Source-to-binary crosswalk — existing-row integrity remediation

Status: complete — wave-1 remediation corrected after independent semantic re-audit
Date: 2026-08-22

Summary: the crosswalk now contains 1,149 source-definition rows: 139 SOURCE_EXACT (12.1%), 320 SOURCE_ANALOG (27.9%), 650 NO_MATCH_FOUND (56.6%), and 40 NOT_IN_RETAIL (3.5%). Wave 1 removed all 15 audited non-function extras, eliminated every populated-VA collision, and leaves the independently inventoried 634-definition omission backlog unchanged. A correction re-audited all 24 original unsupported-analog downgrades, reversed nine false negatives, and confirmed the remaining 15 bounded negative searches.

Evidence: MEASURED — the approved independent audit at commit `906452399d8fda9c1549859a66492ab72761a8f3`, fresh tree-sitter inventory replay, current tracked name table/static closure, precise promoted notes/semantics, and the row-level [`audit/remediation-wave1.tsv`](audit/remediation-wave1.tsv) decision receipt. The correction cold-read every original downgrade against promoted semantic tables, exact function notes, and bounded owner aliases; no classification is promoted from name similarity alone.

Specimen: `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, 2,506,752 bytes. Wave 1 used tracked authorities only; it did not open or write the pristine specimen or a Ghidra project.

## Scope and denominators

This is the existing-row remediation wave. It does not add the 634 source definitions omitted by the original calibration; that work remains a later subsystem-based expansion backlog rather than guessed wave-1 classifications.

| Measure | Baseline audit | Current |
| --- | ---: | ---: |
| AST function definitions | 1,783 | 1,783 |
| Crosswalk rows | 1,164 | 1,149 |
| Valid source-definition joins | 1,149 | 1,149 |
| Non-function extras | 15 | 0 |
| Omitted source definitions | 634 | 634 |

The reconciliation is now direct: `1,783 = 1,149 classified rows + 634 omitted definitions`. The former alternative `1,164 = 1,149 valid rows + 15 extras` is preserved only as the parent-audit baseline.

## Classification contract

| Class | Wave-1 gate |
| --- | --- |
| `SOURCE_EXACT` | Explicit same-function source-body identity at the cited source line and retail VA. Current name similarity is insufficient. |
| `SOURCE_ANALOG` | A named retail candidate plus a precise existing authority target and a bounded analogy reason. The receipt states what is and is not claimed. |
| `NO_MATCH_FOUND` | Empty VA after the baseline exact/prefix/variant/name-note search or a wave-1 row receipt. It does not claim binary absence. |
| `NOT_IN_RETAIL` | Direct Xbox-only source guard against the PC retail specimen, with an empty VA. |

Repeated source labels remain distinct by source line and AST signature. This preserves overloads and conditional definitions instead of collapsing normalized names.

Unchanged negative rows retain the original calibration's shared bounded search surface (exact, prefix, variant, and tracked-note candidates). Rows newly downgraded by wave 1 cite the per-row remediation receipt. An empty `evidence_path` on an unchanged negative therefore means the documented shared baseline search, not an unbounded assertion of absence.

## Audit-code deltas

Raw replay counts use the approved audit instrument unchanged. The receipt separately adjudicates its known shared-label and stale-name false positives.

| Finding code | Baseline | Batch 1 | Current | Baseline → current |
| --- | ---: | ---: | ---: | ---: |
| `ANALOG_EVIDENCE_PATH_MISSING` | 168 | 108 | 0 | -168 |
| `ANALOG_REASON_EVIDENCE_WEAK` | 190 | 108 | 0 | -190 |
| `ANALOG_RETAIL_ANALOG_UNNAMED` | 2 | 0 | 0 | -2 |
| `EVIDENCE_TARGET_UNRESOLVED` | 11 | 0 | 0 | -11 |
| `EXACT_IDENTITY_EVIDENCE_WEAK` | 1 | 0 | 0 | -1 |
| `CROSSWALK_VA_COLLISION` | 34 | 0 | 0 | -34 |
| `CROSSWALK_EXTRA_ROW` | 15 | 0 | 0 | -15 |
| `NO_MATCH_NAME_TABLE_HIT` | 3 | 4 | 4 | +1 |
| `AUTHORITY_SIZE_RANGE_DISAGREEMENT` | 1 | 1 | 1 | +0 |
| `SOURCE_NAME_AMBIGUOUS` | 54 | 48 | 48 | -6 |

### Raw findings retained with explicit dispositions

- Four raw `NO_MATCH_NAME_TABLE_HIT` rows are adjudicated, not open defects: the table's stale `CMusic__Play` label is superseded by the tracked `DeviceChangeTrack` identity, and three shared source labels are owned by different line/signature rows (`CCareer::Load`, `CCareer::Save`, and the `CComplexThing::SetAnimMode(EAnimMode,...)` overload). Their losing branches keep empty VAs.
- The one raw `AUTHORITY_SIZE_RANGE_DISAGREEMENT` is retained for `CFEPGoodies::TransitionNotification @ 0x0045ffa0`. The external-gap receipt identifies a continuation after the static-closure endpoint; wave 1 records the authority disagreement without editing either read-only authority or discarding the named analog.
- The 48 raw `SOURCE_NAME_AMBIGUOUS` row findings are informational line/signature-distinct source identities. Every surviving group is sealed in the remediation receipt.

### Semantic correction re-audit

The rejected `f6d6d6ad` tip had mechanically valid counts but used a name-table-only search that missed promoted source-body records and bounded owner aliases. The correction re-audited all 24 `DOWNGRADE_UNSUPPORTED_ANALOG` decisions and marks every receipt row with `COLD_REAUDIT_CORRECTED` or `COLD_REAUDIT_CONFIRMED`.

- Nine downgrades were reversed: `CActor::MoveTo` is `SOURCE_EXACT @ 0x00401900`; four tracked scalar-deleting destructor wrappers remain bounded `SOURCE_ANALOG`; `CCareer::GetNodeFromWorldNo`, `CPCPlatform::DeviceFlip`, and `CPCPlatform::GetScreenWidth` retain bounded aliases; and `CDXMemBuffer::ReadString` is reassigned to the tracked `CDXMemBuffer__ReadLine @ 0x00548820` release analog.
- Fifteen downgrades remain `NO_MATCH_FOUND` only after owner-specific semantic/note/alias review refuted the old VA and found no separate named retail body. Their receipts explicitly avoid claims of binary absence, folding, or inlining.

## Wave-1 decision receipt

[`audit/remediation-wave1.tsv`](audit/remediation-wave1.tsv) contains 271 cumulative row decisions. It names the before/after class and VA, retail analog where applicable, precise authority targets, bounded analogy ceiling, original raw finding codes, and the remediation disposition.

| Action | Receipt rows |
| --- | ---: |
| `DOWNGRADE_STALE_EXACT_IDENTITY` | 1 |
| `DOWNGRADE_UNSHIPPED_PC_BRANCH` | 2 |
| `DOWNGRADE_UNSUPPORTED_ANALOG` | 15 |
| `DROP_UNRELATED_BEGINSCENE_CITATION` | 1 |
| `DROP_UNRESOLVED_SECONDARY_CITATION` | 5 |
| `PROMOTE_EXPLICIT_SOURCE_BODY_IDENTITY` | 3 |
| `PROMOTE_NAMED_SOURCE_ANALOG` | 1 |
| `REASSIGN_CORRECTED_SOURCE_EXACT` | 2 |
| `REASSIGN_NAMED_SOURCE_ANALOG` | 1 |
| `REMOVE_NON_FUNCTION_EXTRA` | 15 |
| `RETAIN_LINE_DISAMBIGUATED_SOURCE_IDENTITY` | 48 |
| `RETAIN_UNIQUE_VA_OWNER` | 16 |
| `STRENGTHEN_BOUNDED_OWNER_ALIAS` | 3 |
| `STRENGTHEN_COMPILER_WRAPPER_ANALOG` | 4 |
| `STRENGTHEN_NAME_ONLY_ANALOG` | 166 |

Key identity corrections:

- `CMusic::DeviceChangeTrack` now owns `0x004bb450` as `SOURCE_EXACT`; the prior `CMusic::Play` exact row is downgraded under the tracked corrected-identity semantics.
- `CThing::AddShutdownEvent` and `CThing::StartDieProcess` are `SOURCE_EXACT` only because the tracked CThing semantics explicitly assert `SOURCE_BODY` identity; the current name hit alone was not used for promotion.
- `CActor::MoveTo` now owns `0x00401900` as `SOURCE_EXACT` under the tracked CActor `SOURCE_BODY` record; `0x004015e0` remains the distinct `CActor::Move` owner.
- The CActor, CBattleEngine, CThing, and CComplexThing scalar-deleting destructors remain `SOURCE_ANALOG`, bounded to the compiler-wrapper relationship explicitly recorded in their promoted vtable semantics.
- `CCareer__GetNodeFromWorld`, `PCPlatform__DeviceFlip`, and `PLATFORM__GetWindowWidth` are bounded aliases, not exact-name promotions; independent notes establish their source roles and the receipt preserves the analogy ceilings.
- Retail `CDXMemBuffer__ReadLine @ 0x00548820` is the tracked release analog for source `CDXMemBuffer::ReadString`; the previous `CDXMemBuffer__Read @ 0x00548570` collision is removed.
- `CDXEngine::ShutDown` is only `SOURCE_ANALOG`: the named vtable-slot owner and shutdown shape are bounded, while source-body equality and the adjacent unlabeled SetGammaBias stub remain unclaimed.
- Colliding prefix/neighbor guesses lost their VAs. The evidence-supported named owner keeps each VA; no source row was deleted merely because its normalized name matched a sibling.

## Per-file coverage

| File | Rows | EXACT | ANALOG | NO_MATCH | NOT_IN_RETAIL |
| --- | ---: | ---: | ---: | ---: | ---: |
| `activereader.cpp` | 1 | 0 | 1 | 0 | 0 |
| `actor.cpp` | 19 | 1 | 9 | 9 | 0 |
| `Array.h` | 2 | 0 | 0 | 2 | 0 |
| `BattleEngine.cpp` | 114 | 1 | 40 | 73 | 0 |
| `BattleEngine.h` | 2 | 0 | 0 | 2 | 0 |
| `BattleEngineConfigurations.cpp` | 5 | 0 | 0 | 5 | 0 |
| `BattleEngineDataManager.cpp` | 8 | 0 | 3 | 5 | 0 |
| `BattleEngineDataManager.h` | 25 | 0 | 0 | 25 | 0 |
| `BattleEngineJetPart.cpp` | 39 | 0 | 25 | 14 | 0 |
| `BattleEngineWalkerPart.cpp` | 41 | 0 | 26 | 15 | 0 |
| `Camera.cpp` | 45 | 0 | 20 | 25 | 0 |
| `Career.cpp` | 41 | 20 | 3 | 18 | 0 |
| `chunker.cpp` | 17 | 0 | 5 | 12 | 0 |
| `CLIParams.cpp` | 3 | 0 | 0 | 3 | 0 |
| `Controller.cpp` | 18 | 10 | 3 | 5 | 0 |
| `Controller.h` | 4 | 0 | 0 | 4 | 0 |
| `d3dapp.cpp` | 17 | 0 | 11 | 6 | 0 |
| `DXEngine.cpp` | 23 | 2 | 4 | 14 | 3 |
| `DXEngine.h` | 1 | 0 | 0 | 1 | 0 |
| `DXFrontend.cpp` | 4 | 0 | 1 | 3 | 0 |
| `DXGame.cpp` | 2 | 0 | 0 | 2 | 0 |
| `DXMemBuffer.cpp` | 19 | 6 | 1 | 12 | 0 |
| `DXMemoryManager.cpp` | 17 | 5 | 4 | 7 | 1 |
| `DXMemoryManager.h` | 2 | 0 | 0 | 2 | 0 |
| `EditorD3DApp.cpp` | 17 | 0 | 0 | 17 | 0 |
| `EndLevelData.cpp` | 2 | 0 | 1 | 1 | 0 |
| `engine.cpp` | 34 | 1 | 15 | 18 | 0 |
| `event.cpp` | 1 | 0 | 0 | 1 | 0 |
| `eventmanager.cpp` | 14 | 8 | 0 | 6 | 0 |
| `FEPGoodies.cpp` | 38 | 0 | 11 | 27 | 0 |
| `FEPGoodies.h` | 1 | 0 | 0 | 1 | 0 |
| `FEPLoadGame.cpp` | 8 | 0 | 4 | 4 | 0 |
| `FEPSaveGame.cpp` | 12 | 0 | 7 | 5 | 0 |
| `FrontEnd.cpp` | 37 | 0 | 23 | 14 | 0 |
| `game.cpp` | 72 | 38 | 21 | 13 | 0 |
| `game.h` | 3 | 0 | 0 | 3 | 0 |
| `InitThing.cpp` | 17 | 0 | 0 | 17 | 0 |
| `InitThing.h` | 31 | 0 | 0 | 31 | 0 |
| `ltshell.cpp` | 43 | 0 | 1 | 42 | 0 |
| `ltshell.h` | 2 | 0 | 0 | 2 | 0 |
| `MemoryCard.cpp` | 1 | 0 | 0 | 1 | 0 |
| `MemoryCard.h` | 1 | 0 | 0 | 1 | 0 |
| `MemoryManager.cpp` | 39 | 0 | 17 | 22 | 0 |
| `MemoryManager.h` | 4 | 0 | 0 | 4 | 0 |
| `Music.cpp` | 27 | 5 | 4 | 18 | 0 |
| `Music.h` | 2 | 0 | 0 | 2 | 0 |
| `PCController.cpp` | 6 | 0 | 6 | 0 | 0 |
| `PCEngine.cpp` | 18 | 0 | 0 | 18 | 0 |
| `PCFrontend.cpp` | 6 | 0 | 0 | 6 | 0 |
| `PCGame.cpp` | 3 | 0 | 0 | 3 | 0 |
| `PCMemoryCard.cpp` | 1 | 0 | 0 | 1 | 0 |
| `PCMemoryCard.h` | 14 | 0 | 0 | 14 | 0 |
| `PCPlatform.cpp` | 32 | 0 | 7 | 25 | 0 |
| `PCPlatform.h` | 1 | 0 | 0 | 1 | 0 |
| `pcsoundmanager.cpp` | 17 | 11 | 1 | 5 | 0 |
| `pcsoundmanager.h` | 2 | 0 | 0 | 2 | 0 |
| `Platform.cpp` | 1 | 0 | 0 | 1 | 0 |
| `Player.cpp` | 17 | 1 | 11 | 5 | 0 |
| `ResourceAccumulator.cpp` | 9 | 0 | 0 | 9 | 0 |
| `scheduledevent.cpp` | 2 | 2 | 0 | 0 | 0 |
| `SoundManager.cpp` | 48 | 26 | 3 | 19 | 0 |
| `SoundManager.h` | 3 | 0 | 0 | 3 | 0 |
| `SPtrSet.cpp` | 10 | 0 | 0 | 10 | 0 |
| `thing.cpp` | 47 | 2 | 32 | 13 | 0 |
| `thing.h` | 1 | 0 | 0 | 1 | 0 |
| `XBoxMemoryCard.cpp` | 36 | 0 | 0 | 0 | 36 |

## Validation state

- Fresh approved-auditor replay: 1,149 rows; 1,783 AST definitions; 634 omissions; 0 extras.
- Structural status: `PASS` 1101, `PASS_AMBIGUOUS_NAME` 48.
- Evidence status: `FAIL` 4, `PASS` 499, `PASS_SHARED_METHOD` 646.
- Authority status: `DISAGREEMENT` 1, `NOT_APPLICABLE` 695, `PASS` 453.
- PASS: deterministic receipt validator covers row/classification counts, exact source keys, documented repeated labels, VA format/range/uniqueness, negative/EXACT VA polarity, evidence-path existence, sealed raw exceptions, the unchanged 634-omission denominator, and 24/24 original downgrade re-audit dispositions.
- PASS: `npm run test` — AppCore 1,549/1,549, UI 893/893, CLI 125/125; build stage succeeded with one pre-existing NUnit analyzer warning.
- PASS: `npm run build` — 0 warnings, 0 errors.
- PASS: `npm run test:doc-headers` — 0 violations; `git diff --check` — clean.
- Repository-wide link check still reports only the pre-existing unrelated `tools/probe/README.md` link to ignored `../../local-lab/SCRIPT-FORMAT-SPEC-2026-08-02.md`; neither changed report link is among the failures.

## Evidence boundaries

- Name-table and closure joins prove only the tracked named candidate and function boundary they contain. They do not prove source-body equality.
- `NO_MATCH_FOUND` remains a falsifiable search result. Renamed, merged, split, or inlined bodies can still exist.
- Raw authority disagreements and parser-shared-label warnings are not silently suppressed; the receipt states why each surviving raw code is adjudicated.
- Function notes, contracts, Ghidra, source files, rebuild, app code, campaign ledgers, and tracked authorities were read-only in this wave.
