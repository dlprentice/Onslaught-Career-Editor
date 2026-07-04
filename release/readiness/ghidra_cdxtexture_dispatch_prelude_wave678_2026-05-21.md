# Ghidra CDXTexture Dispatch Prelude Wave678 Readiness Note

Date: 2026-05-21

## Scope

Wave678 CDXTexture dispatch prelude saved static Ghidra metadata for four CDXTexture/CFastVB helpers: `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale`, `0x00589094 CDXTexture__RegistryValueEqualsDword`, `0x005890f1 CDXTexture__CpuHasMmxFeature`, and `0x0058926b CFastVB__InitDispatchTableByCpuFeature`.

The pass used the `cdxtexture-dispatch-prelude-wave678` and `wave678-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime CPU/registry/dispatch claim.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0`
  - `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0`
  - `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `4` metadata rows, `4` tag rows, `71` xref rows, `148` instruction rows, and `4` clean decompile rows.
- Queue after Wave678: `6098` total, `3839` commented, `2259` commentless, `1217` exact-undefined signatures, `478` `param_N` signatures, strict clean-signature proxy `3789/6098 = 62.14%`.
- Next queue head: `0x00589200 Catch@00589200`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-071055_post_wave678_cdxtexture_dispatch_prelude_verified`, `19` files, `164367239` bytes, `DiffCount=0`.

## Boundaries

Wave678 proves saved static retail Ghidra name/signature/comment/tag evidence for the observed vector projection, registry query/type-check, MMX CPUID, and dispatch-table initializer tranche. Exact vector storage, plane-normal assumptions, registry policy/caller buffer contract, runtime Direct3D override behavior, CPU dispatch policy, OS feature gating, exact mode enum, dispatch ABI, runtime CPU behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave678 CDXTexture dispatch prelude`, `cdxtexture-dispatch-prelude-wave678`, `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale`, `0x0058926b CFastVB__InitDispatchTableByCpuFeature`, `0x00589200 Catch@00589200`.
