# Patch Catalog Contract

Status: active normative contract
Last reviewed: 2026-07-12

This contract defines what the active executable patch catalog means and what
must be true before a row can appear in Onslaught Toolkit. It replaces
historical convention as the authority for catalog shape. Older plans,
readiness notes, and agent-authored policy are evidence only: rewrite or remove
them when they conflict with current code, tests, or accepted proof.

## Authority Order

For executable mutation, resolve disagreements in this order:

1. accepted specimen identity and exact byte evidence;
2. AppCore apply, verify, and restore behavior plus passing regression tests;
3. `patches/catalog/patches.v2.json` and
   `patches/catalog/safe-copy-profiles.v1.json`;
4. this contract and current `patches/README.md` boundaries;
5. historical proof notes, plans, wave reports, and archived scripts.

Historical text never widens a runtime claim. A rejected diagnostic remains
useful evidence about what did not work, but it is not accepted proof.

## Safety Boundary

- Every active row targets the one supported clean Steam specimen recorded in
  the catalog by SHA-256 and file size.
- Product mutation is limited to an app-owned copied `BEA.exe`. The installed
  game and original executable remain read-only.
- Original bytes are verified before mutation and patched bytes after mutation.
- AppCore publishes the backup snapshot, checksum sidecar, patched copy, and
  restored copy from flushed, byte-verified same-directory staging files. A
  failed staged write leaves the previous copied executable intact.
- Restore verifies backup integrity and clean-specimen provenance before
  replacing the copied target. A verified full-file backup can recover a copy
  with unexpected patch bytes or truncation. Per-row restoration is not
  supported because a hook and its companion can become unsafe when restored
  separately.
- Static byte agreement does not prove launch, visible behavior, gameplay
  safety, compatibility across machines, online play, or rebuild parity.

The copied-target rule is retained because it protects user-owned source data.
Its current path and transaction implementation is reviewable and may be
replaced by a stronger capability-based design; the safety outcome is the
requirement, not the current ceremony.

## Row Schema

Every row must provide:

- identity: `id`, `title`, `track`, and `optional`;
- target: `target_binary_hashes`, `target_binary_size`, `file_offset`,
  `expected_original_bytes`, and `patched_bytes`;
- behavior boundary: `purpose`, `preconditions`, at least one of
  `side_effects` or `postconditions`, `rollback_strategy`, and
  `verification_probe`;
- evidence: `confidence`, `evidence_refs`, and `proof_level`;
- planning policy: `dependencies`, `conflicts`, `exclusive_group`,
  `selectability`, `preset_eligibility`, and `requires_windowed_pair`.

`evidence_refs` contains accepted static or bounded runtime evidence only.
`diagnostic_refs`, when present, contains rejected, negative, or exploratory
evidence that narrows a claim. The legacy `references` alias is invalid.
References must be repository-relative existing files and must not point to
private runtime artifacts.

`confidence` describes confidence in the bounded claim, not general product
safety. `track` describes release posture (`stable` or `experimental`), not
proof depth. `proof_level` names the strongest accepted evidence class for the
row:

| Evidence class | Meaning |
| --- | --- |
| `byte_verified_*` or `companion_payload_byte_verified` | Exact bytes and static interpretation are accepted; any named copied-launch suffix is also bounded launch evidence. |
| `title_screen_runtime_visual_smoke` or `goodies_wall_runtime_visual_smoke` | Exact bytes plus the named bounded copied-runtime visual observation are accepted. |
| `experimental_byte_verified_*` | Exact bytes are accepted; user-visible runtime benefit remains unproven. |
| `experimental_copied_runtime_cdb_*` | Exact bytes plus the specifically named copied-runtime debugger observation are accepted. |

The checker owns the row-to-`proof_level` mapping and each runtime class's
required direct evidence. Adding or promoting a row requires evidence, checker
coverage, AppCore parity, and user-copy review; changing prose alone cannot
promote a row.

## Graph Rules

- IDs are unique and dependency/conflict targets must exist.
- Dependencies are acyclic and may not include the row itself.
- Conflicts are symmetric and may not include the row itself.
- Overlapping rows must have the same complete span and identical before/after
  bytes, or be protected by a symmetric conflict.
- Every pair of rows in one `exclusive_group` must also carry a symmetric
  conflict. The group is a user-facing selection label, not a substitute for
  executable conflict policy.
- A `hidden_companion` cannot be directly selected or named by a profile. It
  must be reachable from at least one visible row through dependencies.
- Profiles may name only visible, preset-eligible rows. Expansion must include
  all transitive dependencies and reject every conflict.
- A row marked `requires_windowed_pair` is tested with both `resolution_gate`
  and `force_windowed` in its effective selection. Safe-copy creation injects
  that pair before dependency expansion and apply; the pair is not misreported
  as an ordinary row dependency.

## AppCore Boundary

The JSON catalog is the contributor-facing source of truth. AppCore pins its
supported catalog hash and keeps a compiled fallback snapshot for explicit
test/recovery paths. Catalog acceptance must compare all mutation-policy fields,
not only bytes and titles. A changed hash is not permission to accept policy
drift.

Fallback use must not silently authorize product mutation. The current
fallback design may be removed if fail-closed packaged-catalog loading proves
simpler and safer; this contract does not require preserving it.

## User Copy

Patch Bench must keep three ideas separate:

- bytes checked: the supported specimen and exact before/after bytes match;
- runtime evidence: the particular launch, visual, or debugger observation
  named by the row was accepted;
- limits: everything not established by that bounded evidence remains
  unproven.

Labels such as stable, preview, unlock, camera, or pause must not imply broader
gameplay behavior. Hidden companion rows and required compatibility rows must
be disclosed in the apply summary even though users do not select them
directly.

## Change Gate

A catalog change is accepted only when focused tests prove the intended failure
first, the catalog/accounting and AppCore parity checks pass, user copy remains
within evidence, and payload-safety gates show that no executable or private
runtime artifact entered Git. Runtime proof and release publication remain
separate authorized operations.
