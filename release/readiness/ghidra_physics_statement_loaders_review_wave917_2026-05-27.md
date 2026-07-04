# Ghidra Wave917 physics statement loaders review (2026-05-27)

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `physics-statement-loaders-review-wave917`

## Scope

Wave917 reviewed top-level physics statement and value-list load helpers from the Wave911 focused correction queue:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x0042f2b0` | `CUnitStatement__LoadFromMemBuffer` | Reviewed; no mutation |
| `0x0042f3d0` | `CPhysicsUnitValueList__LoadFromMemBuffer` | Reviewed; no mutation |
| `0x0042f780` | `CWeaponStatement__LoadFromMemBuffer` | Reviewed; no mutation |
| `0x0042f8a0` | `CPhysicsWeaponValueList__LoadFromMemBuffer` | Reviewed; no mutation |
| `0x0042fca0` | `CWeaponModeStatement__LoadFromMemBuffer` | Reviewed; no mutation |
| `0x0042fdc0` | `CPhysicsWeaponModeValueList__LoadFromMemBuffer` | Reviewed; no mutation |
| `0x00430210` | `CRoundStatement__LoadFromMemBuffer` | Reviewed; no mutation |
| `0x00430330` | `CPhysicsRoundValueList__LoadFromMemBuffer` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave917-physics-statement-loaders-review/metadata.tsv
subagents/ghidra-static-reaudit/wave917-physics-statement-loaders-review/tags.tsv
subagents/ghidra-static-reaudit/wave917-physics-statement-loaders-review/instructions.tsv
subagents/ghidra-static-reaudit/wave917-physics-statement-loaders-review/decompile/
```

Read-back result:

```text
metadata: 8/8 OK
tags: 8/8 OK
instructions: 756 rows
decompile: 8/8 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current static evidence. These loader helpers are coherent with the tracked `CPhysicsScriptStatements.cpp.md` map and current decompile/instruction exports, but exact serialized file format details, concrete value-list layouts, runtime physics behavior, and source identity remain open.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260527-114734_post_wave917_physics_statement_loaders_review_verified
files=19
bytes=173247367
```

## Truth boundary

This review confirms static Ghidra coherence for selected physics statement loaders. It does not prove exact serialized format completeness, concrete layouts, runtime physics-script behavior, BEA patch behavior, or rebuild parity.

## Next

Continue Wave918 with another physics statement/value-list tranche or a source-evidenced gameplay/helper cluster from the Wave911 focused queue.
