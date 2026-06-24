# Ghidra TokenArchive Wave518 Readiness

Status: static read-back complete
Date: 2026-05-17

## Scope

Wave518 saved signature/comment/tag hardening for 9 TokenArchive parser, writer, and reference-resolution helpers:

- `0x004f52b0` `CTokenArchive__GetTokenName`
- `0x004f57b0` `CTokenArchive__ReadNextToken`
- `0x004f5b80` `CTokenArchive__RegisterReferenceFixup`
- `0x004f5ba0` `CTokenArchive__ResolveReferences`
- `0x004f5c90` `CTokenArchive__WriteInt`
- `0x004f5cd0` `CTokenArchive__WriteFloat`
- `0x004f5d10` `CTokenArchive__WriteString`
- `0x004f5d50` `CTokenArchive__WritePointer`
- `0x004f5dc0` `CTokenArchive__WriteFloatPointer`

The pass corrected 8 `undefined` signatures and one stale `param_N` signature. It also removes the stale fourth parameter from `CTokenArchive__RegisterReferenceFixup`; instruction read-back shows `ret 0x0c`, and the body uses only `ref_value`, `slot_index`, and `fixup_record`.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave518-tokenarchive-004f52b0/pre_*`.
- Mutation script: `tools/ApplyTokenArchiveWave518.java`.
- Dry run: `updated=0 skipped=9 missing=0 bad=0`.
- Apply run: `updated=9 skipped=0 missing=0 bad=0`.
- Verify dry run: `updated=0 skipped=9 missing=0 bad=0`.
- Post read-back: `9` metadata rows, `9` tag rows, `178` xref rows, `2565` instruction rows, and `9` decompile exports.
- Focused probe: `tools/ghidra_tokenarchive_wave518_probe.py --check`.
- Queue refresh after Wave518: `6078` functions, `2452` commented, `3626` commentless, `1600` exact-undefined signatures, and `1395` `param_N` signatures.
- Current whole-project telemetry proxy: comment-backed `2452/6078 = 40.34%`; strict comment-plus-clean-signature proxy `2397/6078 = 39.44%`.
- Backup verified at `G:\GhidraBackups\BEA_20260517-215239_post_wave518_tokenarchive_verified` with `19` files, `158567303` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Claim Boundary

This is static Ghidra metadata evidence only. It improves particle-configuration token parsing and writer readability around `CTokenArchive__ReadNextToken`, `CTokenArchive__ResolveReferences`, and `CTokenArchive__WriteFloatPointer`. It does not prove runtime particle parsing, runtime write coverage, concrete TokenArchive layout, final token enum names, BEA patching, source-body identity, or rebuild parity.
