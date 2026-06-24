# Ghidra Wave900+ Through Wave1093 Recheck Note

Status: aggregate validation passed
Date: 2026-06-04
Scope: `wave900-plus-through-wave1093-recheck`

This note extends the post-Wave900 recheck chain through Wave1093. The intended local validation gate is:

```powershell
npm run test:ghidra-wave900-plus-through-wave1093-recheck
```

Wave1093 (`cengine-core-bootstrap-review-wave1093`) re-read the CEngine core bootstrap, resource, viewpoint, mixer, and deserialize surface with no mutation. The focused readiness note is [`ghidra_cengine_core_bootstrap_review_wave1093_2026-06-04.md`](ghidra_cengine_core_bootstrap_review_wave1093_2026-06-04.md).

Coverage anchors:

- Static function-quality closure remains `6410/6410 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress remains `1560/1560 = 100.00%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Representative rows include `0x00449820 CEngine__ctor`, `0x004499d0 CEngine__Init`, `0x00449dc0 CEngine__LoadAllNamedMeshes`, `0x00449ef0 CEngine__GetViewMatrixFromCamera`, `0x0044a020 CEngine__SetViewpoint`, `0x0044a0d0 CEngine__SelectViewpoint`, `0x0044a1f0 CEngine__LoadMixers`, and `0x0044a6e0 CEngine__Deserialize`.
- Context rows include `0x005290a0 CD3DApplication__Create` and `0x0052af00 CD3DApplication__Initialize3DEnvironment`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-155838_post_wave1093_cengine_core_bootstrap_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime engine boot/resource/camera/render/device behavior, exact CEngine/CDXEngine/Direct3D/layout identity, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Validation result:

- `npm run test:ghidra-wave900-plus-through-wave1093-recheck`: PASS.
- Readiness notes: `196`.
- Covered waves: `194`.
- Package probe scripts: `192`.
- Evidence bases: `192`.
- Backup references: `194`.
- Apply scripts: `70`.
- Wave982-Wave1093 direct probes: result file `subagents/ghidra-static-reaudit/wave900-plus-through-wave1093-recheck/wave982-wave1093-direct-probe-results.tsv`, `resultCount=112`, `passCount=1`, `failCount=111`, `disallowedFailureCount=0`.
- Current queue: `6410` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, PASS.

Probe token anchor: Wave1093; cengine-core-bootstrap-review-wave1093; 0x00449820 CEngine__ctor; 0x004499d0 CEngine__Init; 0x00449dc0 CEngine__LoadAllNamedMeshes; 0x00449ef0 CEngine__GetViewMatrixFromCamera; 0x0044a020 CEngine__SetViewpoint; 0x0044a0d0 CEngine__SelectViewpoint; 0x0044a1f0 CEngine__LoadMixers; 0x0044a6e0 CEngine__Deserialize; 0x005290a0 CD3DApplication__Create; 0x0052af00 CD3DApplication__Initialize3DEnvironment; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-155838_post_wave1093_cengine_core_bootstrap_review_verified; no mutation.
