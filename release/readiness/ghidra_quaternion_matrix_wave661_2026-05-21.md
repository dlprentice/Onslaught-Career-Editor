# Ghidra Quaternion Matrix Wave661 Readiness Note

Status: complete
Date: 2026-05-21

## Scope

Wave661 quaternion/matrix correction saved static Ghidra metadata for seven math/dispatch rows:

- `0x00577a0a Math__BuildQuaternionFromEulerAngles_Dispatch`
- `0x00577a38 Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk`
- `0x00577a3e Math__BuildQuaternionFromEulerAngles`
- `0x00579184 CFastVB__NormalizeQuaternionCopy`
- `0x0057923a Math__BuildMatrix4x4FromEulerAngles`
- `0x00579527 Math__BuildProjectiveMatrix4x4FromPlane`
- `0x00579601 Math__BuildMatrix4x4FromQuaternion`

The pass corrected the earlier Wave660 slot-25 Euler-matrix wording: `0x00577a3e Math__BuildQuaternionFromEulerAngles` writes four quaternion-like lanes, not a 4x4 matrix. It also moved two stale `CTexture` labels at `0x0057923a` and `0x00579527` into owner-neutral `Math__*` names, hardened `0x00579184 CFastVB__NormalizeQuaternionCopy`, and made no executable-byte changes.

## Evidence

- Ghidra dry run: `updated=0 skipped=7 renamed=0 would_rename=6 signature_updated=7 missing=0 bad=0`.
- Ghidra apply: `updated=7 skipped=0 renamed=6 would_rename=0 signature_updated=6 missing=0 bad=0`, with seven read-back `OK` rows.
- Final Ghidra dry run: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Post exports verified `7` metadata rows, `7` tag rows, `9` xref rows, `651` instruction rows, `7` clean decompile rows, and two `71`-row dispatch-table snapshots.
- Queue after Wave661: `6098` total functions, `3623` commented, `2475` commentless, `1217` exact-undefined signatures, `694` `param_N` signatures, comment-backed proxy `3623/6098 = 59.41%`, strict clean-signature proxy `3573/6098 = 58.59%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-234153_post_wave661_quaternion_matrix_verified`, `19` files, `163416967` bytes, `DiffCount=0`.
- Next queue head: `0x00579b39 CDXTexture__LookupNamedFormatDescriptor`.

## Boundaries

This is static retail Ghidra metadata evidence only. Exact angle units, quaternion convention, plane equation convention, slot-21 fourth-lane behavior, matrix layout, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain deferred. The `quaternion-matrix-wave661` tag marks the saved static evidence set and does not certify runtime behavior.
