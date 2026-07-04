# Ghidra Physics Statement Load Review Wave1043

Status: complete static read-only evidence
Date: 2026-06-01
Scope: `physics-statement-load-review-wave1043`

Wave1043 re-read the full eighteen-row PhysicsScript statement/value-list load surface that Wave917 and Wave933 had previously reviewed in two focused tranches. The pass was a consolidation review with no mutation: no rename, no signature change, no comment/tag write, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation. Because the same rows were already counted by earlier Wave911 re-audit slices, Wave1043 does not advance the unique re-audit coverage counters.

Reviewed rows:

| Address | Evidence |
| --- | --- |
| `0x0042f2b0 CUnitStatement__LoadFromMemBuffer` | Vtable DATA ref `0x005d9884`; reads the statement name through `CDXMemBuffer__Read`, allocates the first `CPhysicsUnitValueList`, dispatches `CPhysicsScriptStatements__CreateStatementType2`, skips unknown payload bytes, and recurses through the value-list chain. |
| `0x0042f780 CWeaponStatement__LoadFromMemBuffer` | Vtable DATA ref `0x005d985c`; same top-level load shape for type-3 weapon values. |
| `0x0042fca0 CWeaponModeStatement__LoadFromMemBuffer` | Vtable DATA ref `0x005d9870`; same top-level load shape for type-4 weapon-mode values. |
| `0x00430210 CRoundStatement__LoadFromMemBuffer` | Vtable DATA ref `0x005d9848`; same top-level load shape for type-5 round values. |
| `0x004306e0 CSpawnerStatement__LoadFromMemBuffer` | Vtable DATA ref `0x005d9834`; same top-level load shape for type-6 spawner values. |
| `0x00430b60 CExplosionStatement__LoadFromMemBuffer` | Vtable DATA ref `0x005d9820`; same top-level load shape for type-7 explosion values. |
| `0x00431050 CComponentStatement__LoadFromMemBuffer` | Vtable DATA ref `0x005d980c`; same top-level load shape for type-10 component values. |
| `0x004314a0 CFeatureStatement__LoadFromMemBuffer` | Vtable DATA ref `0x005d97f8`; same top-level load shape for type-8 feature values. |
| `0x004318f0 CHazardStatement__LoadFromMemBuffer` | Vtable DATA ref `0x005d97e4`; same top-level load shape for type-9 hazard values. |
| `0x0042f3d0`, `0x0042f8a0`, `0x0042fdc0`, `0x00430330`, `0x00430800`, `0x00430c80`, `0x00431170`, `0x004315c0`, `0x00431a10` | Recursive `CPhysics*ValueList__LoadFromMemBuffer` helpers read child type and serialized-size dwords, dispatch their matching `CPhysicsScriptStatements__CreateStatementTypeN` factory, skip unknown payload bytes otherwise, allocate a next node when the terminator permits, and recurse. |

Context anchors:

- `0x0042e950 CPhysicsScript__Load` reads the outer script stream, dispatches statement factories, and skips unknown statement payload bytes.
- `0x0042eb90 CPhysicsScript__CreateStatement` allocates top-level statement families.
- `0x0042ede0 CUnitStatement__CreateUnitAndRecurse` ties the unit statement family back into runtime object creation/update context.
- `0x0042f4b0`, `0x0042f980`, `0x0042fea0`, and `0x00430410` value-list scalar-deleting destructors carry the Wave1040 `CDXMemoryManager__Free(&DAT_009c3df0, this)` correction context.
- `0x00549220 CDXMemoryManager__Free` remains the memory-manager free context for value-list lifetime review.

Shared body anchors across the target set include `CDXMemBuffer__Read`, `CDXMemoryManager__Alloc`, `CPhysicsScriptStatements__CreateStatementType2`, and `CPhysicsScriptStatements__CreateStatementType10`.

Read-back evidence:

- Primary exports: 18 metadata rows, 18 tag rows, 45 xref rows, 1701 body-instruction rows, and 18 decompile rows.
- Context exports: 8 metadata rows, 8 tag rows, 862 xref rows, 421 body-instruction rows, and 8 decompile rows.
- Queue after Wave1043: 6238 total, 6238 commented, 0 commentless, 0 exact-undefined signatures, 0 `param_N`, strict clean-signature proxy `6238/6238 = 100.00%`.
- Re-audit progress after Wave1043 remains Wave911 focused `735/1408 = 52.20%`, expanded static surface `968/1493 = 64.84%`, top-500 risk-ranked `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-100128_post_wave1043_physics_statement_load_review_verified`, 19 files, 174263175 bytes, `DiffCount=0`, `HashDiffCount=0`.

What remains separate proof:

- Runtime PhysicsScript behavior.
- Serialized physics-script file-format completeness.
- Concrete statement/value-list/value-object layouts beyond observed offsets.
- Mission-script outcomes.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.
