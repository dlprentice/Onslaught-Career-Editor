# Ghidra Wave918 physics statement factories review (2026-05-27)

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `physics-statement-factories-review-wave918`

## Scope

Wave918 reviewed the PhysicsScript statement/value factory family from the Wave911 focused correction queue:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00431bb0` | `CPhysicsScriptStatements__CreateStatementType2` | Reviewed; no mutation |
| `0x00434300` | `CPhysicsScriptStatements__CreateStatementType3` | Reviewed; no mutation |
| `0x00435010` | `CPhysicsScriptStatements__CreateStatementType4` | Reviewed; no mutation |
| `0x00437490` | `CPhysicsScriptStatements__CreateStatementType5` | Reviewed; no mutation |
| `0x00439b40` | `CPhysicsScriptStatements__CreateStatementType6` | Reviewed; no mutation |
| `0x0043a860` | `CPhysicsScriptStatements__CreateStatementType7` | Reviewed; no mutation |
| `0x0043b990` | `CPhysicsScriptStatements__CreateStatementType8` | Reviewed; no mutation |
| `0x0043c0b0` | `CPhysicsScriptStatements__CreateStatementType9` | Reviewed; no mutation |
| `0x0043c500` | `CPhysicsScriptStatements__CreateStatementType10` | Reviewed; no mutation |
| `0x0043dcd0` | `CPhysicsScriptStatements__CreateStatementType11` | Reviewed; no mutation |
| `0x0043ddc0` | `CPhysicsScriptStatements__CreateStatementType12` | Reviewed; no mutation |
| `0x0043e310` | `CPhysicsScriptStatements__CreateStatementType13` | Reviewed; no mutation |
| `0x0043e400` | `CPhysicsScriptStatements__CreateStatementType14` | Reviewed; no mutation |
| `0x0043e540` | `CPhysicsScriptStatements__CreateStatementType15` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave918-physics-statement-factories-review/metadata.tsv
subagents/ghidra-static-reaudit/wave918-physics-statement-factories-review/tags.tsv
subagents/ghidra-static-reaudit/wave918-physics-statement-factories-review/instructions.tsv
subagents/ghidra-static-reaudit/wave918-physics-statement-factories-review/decompile/
```

Read-back result:

```text
metadata: 14/14 OK
tags: 14/14 OK
instructions: 3318 rows
decompile: 14/14 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current evidence. The functions are coherent with the tracked `CPhysicsScriptStatements.cpp.md` type-2 through type-15 factory map. They allocate typed value nodes, install observed vtables, and return null for unsupported ids. No source-backed correction or signature drift was found.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
G:\GhidraBackups\BEA_20260527-121244_post_wave918_physics_statement_factories_review_verified
files=19
bytes=173247367
```

## Truth boundary

This review confirms static Ghidra coherence for selected PhysicsScript factory helpers. It does not prove exact value semantics, concrete class layouts, serialized format completeness, runtime physics-script behavior, BEA patch behavior, or rebuild parity.

## Next

Continue Wave919 with additional PhysicsScript value-family helpers, collision-seeking round helpers, or another Wave911 focused cluster that has stronger source/body evidence.
