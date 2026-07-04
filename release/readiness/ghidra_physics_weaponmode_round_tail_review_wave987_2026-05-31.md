# Ghidra PhysicsScript Weapon-Mode / Round-Tail Review Wave987 Readiness Note

Status: complete static read-back evidence with one tag-only correction
Date: 2026-05-31
Scope: `physics-weaponmode-round-tail-review-wave987`

Wave987 re-reviewed twenty-six PhysicsScript weapon-mode and round-tail helpers after the Wave900-Wave986 recheck gate. The pass made one saved Ghidra tag-only correction: it removed the stale `constructor` tag from `0x004359c0 CPhysicsWeaponModeValue__dtor_base` while keeping `destructor` and `supersedes-wave336-ctor-label`, then added `physics-weaponmode-round-tail-review-wave987`, `wave987-readback-verified`, and `tag-corrected`. It made no rename, signature change, comment change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004359c0 CPhysicsWeaponModeValue__dtor_base` | Base destructor body restores vtable `0x005da278`; post tags no longer include `constructor`; sole call xref is `0x00437083` from `CPhysicsWeaponModeValue__scalar_deleting_dtor`. |
| `0x00435b20 CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer` | Shared two-scalar mem-buffer load helper for fields at `this+0x8` and `this+0xc`. |
| `0x00437080 CPhysicsWeaponModeValue__scalar_deleting_dtor` | Vtable-backed scalar-deleting wrapper that calls `0x004359c0`, then optionally calls `OID__FreeObject`. |
| `0x00437490 CPhysicsScriptStatements__CreateStatementType5` | Round-value factory context; xrefs include `CRoundStatement__LoadFromMemBuffer` and `CPhysicsRoundValueList__LoadFromMemBuffer`. |
| `0x004380c0 CPhysicsRoundValue__dtor_base` and `0x00438400 CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor` | Round-value base destructor plus shared leaf wrapper; wrapper calls the base body before optional free. |
| `0x004395b0 CRoundSeek__scalar_deleting_dtor` and `0x004395d0 CRoundSeek__dtor_base` | Seek nested round-value destructor pair; base body destroys the owned child value at `this+0x8`. |
| `0x00439ad0 CRoundTreeCollision__scalar_deleting_dtor` and `0x00439af0 CRoundTreeCollision__dtor_base` | Tree-collision nested round-value destructor pair; base body destroys the owned child value at `this+0x8`. |

Read-back evidence:

- `ApplyPhysicsWeaponModeRoundTailWave987.java` dry: `updated=0 skipped=1 tag_removed=0 would_remove_tag=1 tags_added=3 missing=0 bad=0`
- Apply: `updated=1 skipped=0 tag_removed=1 would_remove_tag=0 tags_added=3 missing=0 bad=0`
- Final dry: `updated=0 skipped=1 tag_removed=0 would_remove_tag=0 tags_added=0 missing=0 bad=0`
- Post exports: `26` metadata rows, `26` tag rows, `102` xref rows, `1703` body-instruction rows, and `26` decompile rows.
- Queue after Wave987 remains `6222/6222 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused re-audit progress: `432/1408 = 30.68%`.
- Expanded static surface progress: `492/1478 = 33.29%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-023543_post_wave987_physics_weaponmode_round_tail_review_verified`, `19` files, `173837191` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The current Ghidra project no longer contradicts the saved destructor name/comment for `0x004359c0` with a stale constructor tag.
- The selected weapon-mode and round-tail rows still have saved names, signatures, comments, tags, xrefs, instruction bodies, and decompile exports matching the bounded static evidence.
- The correction is limited to Ghidra metadata tags.

What remains separate:

- Exact PhysicsScript value/record layouts.
- Exact source-body identity.
- Runtime physics-script loading/application/lifetime behavior.
- MSL asset behavior.
- BEA patching.
- Rebuild parity.
