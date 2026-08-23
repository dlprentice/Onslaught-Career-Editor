# W2 source contract — Thing, Battle Engine, camera, and gameplay interfaces

Status: measured source-first expansion receipt; retail deltas remain explicitly bounded
Date: 2026-08-22
Evidence: MEASURED — deterministic stable-key/authority joins over the pinned SOURCE files, current Generation-32 register/closure, promoted semantics, and named prior receipts; no new retail measurement.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` (not opened by this lane; identity inherited from tracked authorities).

Summary: this receipt covers all 201 omitted definitions in the exact eleven-file W2 cohort from pinned `references/Onslaught@5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. It repairs all 155 macro-ownerless AST labels lexically, promotes 32 rows only through reviewed SOURCE_INLINE/SOURCE_FOLDED semantic authorities, retains five bounded named analogs, leaves two bodies at external-proof-required, and records 162 bounded source-only negatives without claiming binary absence.

## Authority and scope

- Repository parent: `784367bd43f9ec13125521b00fe0c8352670ffdd`.
- Pinned source: `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.
- Retail specimen anchor: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; this lane did not open or write the specimen.
- Exact file set (11, set SHA-256 `e56344ca63a1a1a42b63a39cec9ceb55356e9751a3c1cf83e33ef04707d62837`): `actor.h`, `BattleEngine.h`, `BattleEngineConfigurations.h`, `BattleEngineDataManager.h`, `BattleEngineJetPart.h`, `BattleEngineWalkerPart.h`, `Camera.cpp`, `Camera.h`, `InitThing.cpp`, `InitThing.h`, `thing.h`.
- Canonical `reverse-engineering/source-crosswalk/crosswalk.tsv`, its report, Ghidra, binaries, rebuild source, and all out-of-wave rows were read-only.

## Corpus reuse preflight

Before this tracked root was written, the lane read `local-lab/INDEX.md`, `CORPUS-HYGIENE-2026-08-22.md`, and the updated `source-first-expansion/EXECUTION.md`; it searched tracked owners and `INDEX-CATALOG-2026-08-17.md` by subsystem, representative stable keys, VAs, sealed artifact hashes, and crosswalk tool names. The historical catalog contained 13 subsystem lines but zero representative stable-key, VA, sealed-wave-hash, or crosswalk-tool lines. The relevant predecessor it did identify is `pc-layout-thing-complexthing-20260813-v1/results-g/results.ready.json` (SHA-256 `e788ffde077c9c861d9163a7526964917cc1747c9c69f6287d9e919a1e399efa`), which already settles CThing/CComplexThing fields and selected CActor witnesses; those facts are reused, not remeasured.

- `REUSED`: 46 already owner-qualified definitions reuse the sealed partition readiness/evidence, current tracked authorities, and Generation-32 catalog.
- `EXTENDED`: 155 macro-ownerless definitions add the source-lexical owner repair and rerun qualified semantic/name joins.
- `NEW_MEASUREMENT`: 0 definitions. No pristine bytes, runtime, Ghidra, browser, GUI, PS2 corpus, or raw G: corpus was opened.
- The plan's `PLAN.md`, `partition.tsv`, `sample.tsv`, `manifest.json`, and `EXECUTION.md` are exact reused predecessors. Current Generation 32 is reused through tracked `EVIDENCE-REGISTER.tsv` plus the local `campaign.ready.json` hash recorded in `RECEIPT.json`.
- Deterministic projection used `%LOCALAPPDATA%/Temp/build_w2_expansion.py` (SHA-256 `e744a2786599971716d16ad9e9adcf39ef406b4941347764e6a5741d88516e19`); independent structural/hash validation used `%LOCALAPPDATA%/Temp/validate_w2_expansion.py` (SHA-256 `38e5d9135e0d456f6c79d44788b82eae575776932ece7eca0dfb8c4476f0ba98`). Two fresh projection roots were byte-identical for all five outputs before tracked write.
- No repository or evidence-corpus files were deleted, moved, staged, retired, or written outside the exclusive W2 tracked root; deterministic preflight outputs stayed under `%LOCALAPPDATA%/Temp`. H: retirement and generic PS2 crosswalk work are not part of this lane.

## Stable identity and lexical owner repair

The stable key remains the original `(source_file, source_line, parser function, signature)` tuple. `definitions.tsv` preserves that tuple byte-for-byte and adds a separate `resolved_owner`/`resolved_function`; it never rewrites the parser key.

- `actor.h:13` opens `DECLARE_THING_CLASS(CActor, CComplexThing)` and the declaration closes at line 65: all 11 ownerless definitions at lines 18–55 are `CActor` members.
- `BattleEngine.h:72` opens `DECLARE_THING_CLASS(CBattleEngine, CUnit)` and closes at line 485: all 47 ownerless definitions at lines 96–324 are `CBattleEngine` members.
- `thing.h:65` opens `DECLARE_MULTI_INTERFACE_CLASS(CThing, ...)` and closes at line 252: 83 ownerless definitions are `CThing` members.
- `thing.h:257` opens `DECLARE_THING_CLASS(CComplexThing, CThing)` and closes at line 306: 14 ownerless definitions are `CComplexThing` members.

That resolves the entire 155-row ambiguity subtype without normalizing overloads, punctuation, source lines, or signatures.

## Source architecture and algorithms

### Thing and actor strata

`thing.h:65-252` defines `CThing` as the shared audible/renderable base. Its omitted inline surface supplies conservative render/audio defaults, position and render-owner access, visibility/dying/shutdown flags, type-mask identity, gravity/collision defaults, objective/vulnerability defaults, and script/animation no-op hooks. `thing.h:257-306` adds `CComplexThing` orientation, animation, motion-controller, script, and name state. `actor.h:13-65` then adds velocity, previous pose, current-minus-old movement, stop-to-zero, and last-contact timestamps.

The promoted CThing/CComplexThing/CActor semantic tables prove the 27 exact inline/folded rows in those strata. Three compiler-folded groups are intentional and evidence-backed: `0x004040a0` owns CThing render position plus start and end positions, `0x0043e9f0` owns CThing sound/old position, and `0x0043ea20` owns CComplexThing sound/old orientation. These are not accidental VA collisions.

### Battle Engine state and parts

`BattleEngine.h:20-44` fixes event ordinals, the four morph/walker/jet state names, engine-state names, a 0.5-second transform time, and the 4.0 slow-movement factor. `BattleEngine.h:72-330` layers targeting, locks, zoom, weapon/configuration access, energy/life warnings, cloak/augmentation, render interpolation inputs, player links, and walker/jet parts over `CUnit`. The promoted table proves five omitted inline bodies exactly: max velocity 35, the Battle Engine type mask, infinite-energy refill, sound material, and stealth.

`BattleEngineJetPart.h:23-108` and `BattleEngineWalkerPart.h:16-121` keep mode-specific weapon sets and movement state behind a shared main part. Their five omitted rows each are simple field access/update contracts. `BattleEngineConfigurations.h:9-27` exposes the fixed 20-name table count; `BattleEngineDataManager.h:243-430` owns the ordered configuration set, shutdown/initialise/load/resource walks, index/name lookup, and editor-only mutation surface. The W2 omission is its all-target `CountConfigurations()` accessor at line 270.

### Camera family

`Camera.h:19-235` defines an abstract pose/zoom/HUD interface and attached, third-person, viewpoint, pan, movie, controllable, generic, and interpolated implementations. Default old pose delegates to current pose; pan accessors use a one-valued zoom and hide HUD; controllable/generic/interpolated accessors expose retained fields. `Camera.cpp:344-356` seeds CPanCamera and schedules its first update; `Camera.cpp:717-728` mirrors supplied controllable pose into current/old/temp state.

Five rows remain bounded SOURCE_ANALOG rather than exact: the two out-of-line constructors, CGenericCamera constructor/GetPos, and CInitThing constructor. Full-pass plates establish names, ABI/field shape, and callers, but the receipt does not silently turn those plates into source-body equality. `CCamera::~CCamera` remains RETAIL_UNRESOLVED because a deleting wrapper does not prove the empty source destructor body.

### InitThing defaults

`InitThing.cpp:68-87` seeds base thing initialization; `InitThing.h:72-110` seeds collision policy; `InitThing.h:410-468` seeds spawner counts/timers/strings; and `InitThing.h:939-945` seeds the animal type. These constructors are source contracts only unless a named retail authority is listed.

## Retail delta totals

| Delta status | Rows | Meaning |
| --- | ---: | --- |
| `SOURCE_AGREES` | 32 | Explicit promoted SOURCE_INLINE/SOURCE_FOLDED identity and current name/closure VA presence. |
| `SOURCE_DIVERGES` | 0 | No W2 omitted row has a proved retail divergence. |
| `RETAIL_UNRESOLVED` | 7 | Five named analogs plus two external-proof-required bodies; no exact equality claim. |
| `SOURCE_ONLY` | 162 | Repaired owner and source body are known; the bounded retail search found no supported target. |
| `NOT_SELECTED_TARGET` | 0 | Every W2 definition is outside an enclosing target conditional. |

A `NO_MATCH_FOUND` classification here is a falsifiable search result, never a claim of absence, folding, inlining, or unselected build membership.

## Per-file coverage

| Source file | Definitions |
| --- | ---: |
| `actor.h` | 11 |
| `BattleEngine.h` | 47 |
| `BattleEngineConfigurations.h` | 1 |
| `BattleEngineDataManager.h` | 1 |
| `BattleEngineJetPart.h` | 5 |
| `BattleEngineWalkerPart.h` | 5 |
| `Camera.cpp` | 2 |
| `Camera.h` | 28 |
| `InitThing.cpp` | 1 |
| `InitThing.h` | 3 |
| `thing.h` | 97 |

## Source-drop limits and falsifiers

The drop has no complete build/test system or dependency closure, and it mixes retained target/editor branches. Source analogy is not Steam equality. The cheapest row falsifier is listed in `definitions.tsv` and `RETAIL-DELTA.tsv`: contrary semantic/body evidence for exact rows, ABI/body refutation for analogs, or a named compiler-emitted/folded target for source-only rows. Re-run the deterministic receipt after any promoted semantic-table, name-table, closure, source-commit, or cohort-partition change.
