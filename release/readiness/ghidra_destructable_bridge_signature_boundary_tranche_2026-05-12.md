# Ghidra Destructable Bridge Signature Boundary Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 351 continued the saved-Ghidra static re-audit at the destructable bridge/component boundary cluster around `0x00444620..0x00444c00`. It saved five names, signatures, comments, and tags after fresh metadata, decompile, xref, instruction, tag, and vtable read-back.

Stuart's checked source snapshot does not currently include a full `DestructableSegmentsController.cpp` body, so this wave treats the names as behavior-backed retail static labels rather than exact source-body closure.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x00444620` | `CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric` | Corrects the older `CExplosionInitThing` owner label; the body walks the tracked segment array, writes the active flag to segment field `+0x1c`, and refreshes cached active-value context from the root segment when present. |
| `0x00444940` | `CDestroyableSegmentComponent__scalar_deleting_dtor` | Component scalar-deleting destructor wrapper that calls the component destructor body, frees through `OID__FreeObject` when flags bit `0` is set, and returns `this`. |
| `0x00444960` | `CDestroyableSegmentComponent__dtor_base` | Component destructor body that removes the owner-link cell at `this+0x40`, then chains directly to canonical `CDestroyableSegment__dtor_base` at `0x00442660`. |
| `0x00444be0` | `CDestroyableSegmentVariant__scalar_deleting_dtor` | Recovered shared scalar-deleting destructor boundary used by vtable slot-1 entries `0x005db0e4`, `0x005db118`, and `0x005db14c`; concrete variant class names remain unproven. |
| `0x00444c00` | `CDestroyableSegment__dtor_base_thunk` | Small tail thunk that jumps to the canonical base destructor at `0x00442660`; instruction read-back proves the thunk even though decompile may render the target body through it. |

## Evidence

- Initial read-only exports covered metadata, decompile, xrefs, instructions, tags, and vtable-slot evidence for the target cluster and adjacent missing boundary.
- `tools/ApplyDestructableBridgeSignatureBoundaryTranche.java` dry/apply saved the five target names, signatures, comments, and tags; final apply printed `REPORT: Save succeeded`.
- Final read-back verified `5/5` metadata rows, `5/5` decompile exports, `7` xref rows, `555` instruction rows, `5/5` tag rows, `20` vtable-slot rows, `4` vtable evidence hits, `7` xref evidence hits, `8` instruction evidence hits, `0` stale-token hits, and `0` comment overclaims.
- The focused probe caught and corrected an initial over-specific comment expectation: `0x00444960` chains directly to canonical `0x00442660`, not through the `0x00444c00` thunk.
- `py -3 tools\ghidra_destructable_bridge_signature_boundary_tranche_probe_test.py` passed `2/2`; `py -3 -m py_compile tools\ghidra_destructable_bridge_signature_boundary_tranche_probe.py tools\ghidra_destructable_bridge_signature_boundary_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-destructable-bridge-signature-boundary-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database baseline reports `5979` functions, `0` weak functions, `1951` undefined signatures, and `2075` `param_N` signatures.
- The refreshed quality queue reports `1148` commented functions, `4831` commentless functions, `1951` undefined signatures, and `2075` `param_N` signatures.
- The current comment-backed static RE proxy is still below `20%`: `1148/5979 = 19.20%`; the stricter comment-plus-clean-signature proxy is `1085/5979 = 18.15%`.
- The post-mutation live Ghidra backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_211919_post_wave351_destructable_bridge_verified` with `19` files, `152865671` bytes, and `HashDiffCount=0`.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag evidence only. It improves the current destructable bridge/component boundary cluster, but it does not prove exact Stuart source identity, certified class layouts, local variable recovery, structure typing, runtime destruction, cascade, random-damage, rubble, mesh behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/destructable-bridge-wave351/current/`.
