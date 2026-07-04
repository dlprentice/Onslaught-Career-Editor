# Ghidra CDebris Signature / Boundary Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 347 continued the saved-Ghidra static re-audit at the `CDebris` cluster around `0x004411a0..0x00441420`. It saved seven names, signatures, comments, and tags after fresh metadata, decompile, xref, instruction, tag, vtable, and string read-back.

This pass corrected two older labels and recovered four adjacent function boundaries. Stuart's checked source snapshot has only `CDebris` callsite hints, not a full `CDebris` implementation body, so this wave treats the names as static retail behavior labels rather than exact source-body closure.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x004411a0` | `CDebris__Init` | Initializes render-object/resource context, calls base init, registers debris console variables, and links the object into the global debris list. |
| `0x00441320` | `CDebris__dtor_base` | Corrects the stale constructor-like label; unlinks the instance from the global debris list and delegates base destruction. |
| `0x00441360` | `CDebris__GetClassName` | Recovered boundary returning the `CDebris` class-name string. |
| `0x00441370` | `CDebris__GetClassId` | Recovered boundary returning class/OID id `0x1f`. |
| `0x00441380` | `CDebris__scalar_deleting_dtor` | Scalar-deleting destructor wrapper that calls the base destructor body and conditionally frees the object. |
| `0x004413a0` | `CDebris__Render` | Recovered render boundary with visibility/render-object checks and distance-fade alpha context. |
| `0x00441420` | `CDebris__RenderImposter` | Recovered imposter-render boundary with the same distance-fade alpha context. |

## Evidence

- Initial read-only exports covered `3` existing `CDebris` targets with metadata, decompile, xrefs, instructions, tags, vtable slots, and class-string read-back.
- The first instruction export was accidentally overlapped with another export and hit a Ghidra project `LockException`; it was rerun serially and passed. No saved Ghidra data was lost by that failed read-only export.
- Boundary dry-run predicted `4` new local function objects for `0x00441360`, `0x00441370`, `0x004413a0`, and `0x00441420`.
- `tools/ApplyDebrisSignatureBoundaryTranche.java` dry/apply saved the seven target names, signatures, comments, and tags; final apply printed `REPORT: Save succeeded`.
- Final read-back verified `7/7` metadata rows, `7/7` decompile exports, `7` xref rows, `847` instruction rows, `7/7` tag rows, and `4` vtable evidence hits.
- `py -3 tools\ghidra_debris_signature_boundary_tranche_probe_test.py` passed `2/2`; `py -3 -m py_compile tools\ghidra_debris_signature_boundary_tranche_probe.py tools\ghidra_debris_signature_boundary_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-debris-signature-boundary-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database baseline reports `5978` functions and `0` weak functions. The refreshed quality queue reports `1105` commented functions, `4873` commentless functions, `1958` undefined signatures, and `2107` `param_N` signatures.
- The post-mutation live Ghidra backup was verified on `[maintainer-local-backup-volume]` with `19` files, `152734599` bytes, and `HashDiffCount=0`.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag and boundary evidence only. It improves the current `CDebris` cluster, but it does not prove exact Stuart source identity, a certified `CDebris` class layout, local variable recovery, structure typing, runtime debris rendering behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/debris-wave347/current/`.
