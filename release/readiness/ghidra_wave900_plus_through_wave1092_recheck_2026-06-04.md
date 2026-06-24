# Ghidra Wave900+ Through Wave1092 Recheck Note

Status: aggregate validation passed
Date: 2026-06-04
Scope: `wave900-plus-through-wave1092-recheck`

This note extends the post-Wave900 recheck chain through Wave1092. The intended local validation gate is:

```powershell
npm run test:ghidra-wave900-plus-through-wave1092-recheck
```

Wave1092 (`d3d-application-shell-review-wave1092`) re-read the Wave572 D3D application shell with no mutation. The focused readiness note is [`ghidra_d3d_application_shell_review_wave1092_2026-06-04.md`](ghidra_d3d_application_shell_review_wave1092_2026-06-04.md).

Coverage anchors:

- Static function-quality closure remains `6410/6410 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress reaches `1560/1560 = 100.00%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- CD3DApplication vtable `0x005e4ad0` exports `6` OK slots; key rows include `CD3DApplication__Create` and `CD3DApplication__MsgProc`.
- Representative rows include `0x00528f80 CD3DApplication__Init`, `0x005290a0 CD3DApplication__Create`, `0x00529350 CD3DApplication__BuildDeviceList`, `0x0052af00 CD3DApplication__Initialize3DEnvironment`, `0x0052b840 CD3DApplication__ToggleFullscreen`, `0x0052ba50 CD3DApplication__ForceWindowed`, `0x0052bc80 CD3DApplication__SelectDeviceProc`, and `0x0052cd20 CD3DApplication__PerfTimerCommand`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-152017_post_wave1092_d3d_application_shell_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime Direct3D device creation/reset/window/dialog behavior, exact `CD3DApplication` and Direct3D layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Validation result:

- `npm run test:ghidra-wave900-plus-through-wave1092-recheck`: PASS.
- Readiness notes: `195`.
- Covered waves: `193`.
- Package probe scripts: `191`.
- Evidence bases: `191`.
- Backup references: `193`.
- Apply scripts: `70`.
- Wave982-Wave1092 direct probes: result file `subagents/ghidra-static-reaudit/wave900-plus-through-wave1092-recheck/wave982-wave1092-direct-probe-results.tsv`, `resultCount=111`, `passCount=1`, `failCount=110`, `disallowedFailureCount=0`.
- Current queue: `6410` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, PASS.

Probe token anchor: Wave1092; d3d-application-shell-review-wave1092; 0x00528f80 CD3DApplication__Init; 0x005290a0 CD3DApplication__Create; 0x00529350 CD3DApplication__BuildDeviceList; 0x0052af00 CD3DApplication__Initialize3DEnvironment; 0x0052b840 CD3DApplication__ToggleFullscreen; 0x0052ba50 CD3DApplication__ForceWindowed; 0x0052bc80 CD3DApplication__SelectDeviceProc; 0x0052cd20 CD3DApplication__PerfTimerCommand; 0x005e4ad0; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-152017_post_wave1092_d3d_application_shell_review_verified; no mutation.
