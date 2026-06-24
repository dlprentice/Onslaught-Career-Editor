# PhysicsScript Copied-Corpus Parser Proof

Status: copied-corpus parser/census proof complete, not runtime proof
Last updated: 2026-06-08
Scope: Public-safe aggregate proof from copied/app-owned `data/default physics.dat`

This result turns the [PhysicsScript Schema/Parser Proof Plan](physics-script-schema-parser-proof-plan.md) into a shallow framed parser/census proof over copied corpus evidence. It is not a new static re-audit wave, not a Ghidra mutation, not a runtime launch, not mission outcome proof, and not rebuild parity.

Follow-up scalar/string fixture result: [PhysicsScript Scalar/String Value Decoder Fixture Proof Plan](physics-script-scalar-string-value-decoder-fixture-proof-plan.md), backed by [physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json](physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-scalar-string-value-decoder-fixture-complete-static-decode-roundtrip-not-runtime-proof; fixtureClassCounts=3912/1737/361/132/661; syntheticFixtureCaseCount=13; selectedNextSlice=PhysicsScript Value-ID Semantic Crosswalk Proof Plan; physicsScriptTopLevelStatementCount=777; physicsScriptValueListNodeCount=6803; publicLeakCheck=PASS; runtimeExecution=false; godotWork=false; ghidraMutation=false; rebuildImplementation=false. It proves deterministic public-safe scalar/string/two-scalar/three-scalar/rounded-scalar fixtures and copied-corpus aggregate payload shape counts only; runtime PhysicsScript behavior, serialized completeness, exact layouts, complete value-id semantics, rebuild parity, and no-noticeable-difference parity remain separate proof.

Follow-up value-id semantic crosswalk result: [PhysicsScript Value-ID Semantic Crosswalk Proof Plan](physics-script-value-id-semantic-crosswalk-proof-plan.md), backed by [physics-script-value-id-semantic-crosswalk.v1.json](physics-script-value-id-semantic-crosswalk.v1.json), records crosswalkStatus=physics-script-value-id-semantic-crosswalk-complete-bounded-static-crosswalk-not-runtime-proof; boundedCrosswalkRowCount=87; observedSelectedRowCount=72; factoryOnlySelectedRowCount=15; selectedNextSlice=PhysicsScript Rebuild Interface Rollup Proof Plan; physicsScriptTopLevelStatementCount=777; physicsScriptValueListNodeCount=6803; physicsScriptStatementValuePairCount=185; completeValueIdSemanticsProven=false; all185PairsSemanticallyNamed=false; publicLeakCheck=PASS; runtimeExecution=false; godotWork=false; ghidraMutation=false; rebuildImplementation=false. It records selected rebuild-facing field names only where static factory/apply evidence is strong enough; runtime PhysicsScript behavior, serialized completeness, exact layouts, complete value-id semantics, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |

Remaining active focused work remains `0`; this proof does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the static percentages.

## Generated Evidence

Private ignored artifact:

- `subagents/physics_script_schema_parser_proof_2026-06-08/physics-script-copied-corpus-summary.json`

Public-safe parser schema:

- `physics-script-copied-corpus-parser.v1`

The generator consumes copied/app-owned corpus input under `game/` and excludes `MissionScripts/*.msl` from PhysicsScript binary parser input. It writes private SHA-256 and detailed value-pair counts only to ignored evidence. Tracked docs intentionally publish aggregate counts, not raw bytes, raw strings, AST dumps, absolute paths, or private hashes.

## Corpus Result

| Metric | Result |
| --- | --- |
| Parsed copied corpus files | `1` |
| Parsed copied filename | `data/default physics.dat` |
| Parsed byte count | `175603` |
| Stream header | `0x12` |
| Top-level statements | `777` |
| Top-level type counts `1..9` | `160 / 139 / 145 / 91 / 38 / 118 / 39 / 43 / 4` |
| Unknown top-level ids | `0` |
| Value-list nodes | `6803` |
| Unique statement/value id pairs | `185` |
| Raw value payload bytes preserved | `73796` |
| Continuation markers | `6026` zero/continue markers and `777` terminating `-1` markers |
| Stop reason | terminating `-1` marker at EOF |

The parser validates the saved `CPhysicsScript__Load` stream shape: a 2-byte `0x12` header, repeated top-level `int32 statement_type` and `int32 declared payload size` rows, known statement ids routed through the saved `1..9` factory range, statement-name byte spans, shallow value-list `int32 value_type` plus `int32 payload_size` records, raw payload skip/preservation, and continuation markers where `0` continues and nonzero stops.

The aggregate includes `0` unknown top-level ids.

Known top-level payload sizes are retained as declared-size evidence and skip authority for unknown top-level ids. For known top-level ids, the parser follows the saved loader shape and consumes through the value-chain terminator rather than treating declared size as a hard body boundary. This distinction is why the proof is a shallow framed parser/census proof only.

## What This Proves

- The copied PhysicsScript corpus candidate can be shallow-framed with the saved static `CPhysicsScript__Load` contract.
- The parsed copied corpus uses top-level statement ids within the saved `1..9` factory range.
- The parser reaches a clean top-level terminator at EOF with no unknown top-level ids.
- Value-list records can be counted and raw-preserved without decoding semantic value fields.
- The evidence is public-safe when reduced to aggregate counts.

## Not Claimed

This does not prove runtime PhysicsScript behavior, mission outcomes, resource-script outcomes, serialized physics-script file-format completeness, exact statement/value-list/concrete record layouts, complete nested enum semantics, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.

## Follow-Up Static-To-Proof Result

The follow-up PhysicsScript slice completed a semantic schema ledger for selected high-confidence value families: [PhysicsScript Semantic Value-Field Schema Ledger Proof Plan](physics-script-semantic-value-field-schema-ledger-proof-plan.md), backed by [physics-script-semantic-value-field-schema-ledger.v1.json](physics-script-semantic-value-field-schema-ledger.v1.json). It records ledgerStatus=physics-script-semantic-value-field-schema-ledger-complete-static-semantic-ledger-not-runtime-proof; semanticBucketCount=10; familyCoverageRows=9; valueFamilyCoverageRows=9; physicsScriptTopLevelStatementCount=777; physicsScriptValueListNodeCount=6803; physicsScriptStatementValuePairCount=185; physicsScriptRawValuePayloadBytesPreserved=73796; publicLeakCheck=PASS; runtimeExecution=false; godotWork=false; ghidraMutation=false; rebuildImplementation=false; and selectedNextSlice=PhysicsScript Scalar/String Value Decoder Fixture Proof Plan. It remains a static semantic ledger, not runtime PhysicsScript behavior, serialized completeness, exact layout, complete nested enum, patching, visual, rebuild, or no-noticeable-difference proof.
