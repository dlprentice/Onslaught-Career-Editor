# Ghidra SIMD Gate Dual Profile Wave892 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `simd-gate-dual-profile-wave892`

Wave892 SIMD gate dual profile saved comments/tags for three raw commentless CFastVB/CDXTexture SIMD, MMX, and dual-profile interpolation rows after serialized headless dry/apply/read-back/final dry with the `simd-gate-dual-profile-wave892` and `wave892-readback-verified` tags. Existing names and signature displays were preserved. The pass made no renames, no function-boundary changes, no executable-byte changes, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005888bc CFastVB__InterpolateDualProfileStreams` | DATA xref dispatch slot `0x00657164`; `RET 0x30`; handles single-profile and multi-profile modes, accumulates weighted vector triples after `__ftol` phase reduction against `DAT_005e6a3c`, calls `CFastVB__DispatchIndirectByGlobalTable` and `CFastVB__DispatchIndirect_00656f48`, copies payload bytes before or after vector writes depending on stack flag `+0x30`, advances output pointer arrays/strides, and returns the last advanced pointer context. |
| `0x00589116 CDXTexture__IsMmxEnabledBySystemConfig` | Called by `CDXTexture__DecodeJpegFromMemory`, `CWaypointManager__InitMmxDispatchAndRun`, and `CDXTexture__InitMmxDispatchAndRun`; checks `Software\\Microsoft\\Direct3D` / `DisableMMX`, updates cache global `DAT_00657a80`, and otherwise gates enablement through `GetSystemInfo` plus `CDXTexture__CpuHasMmxFeature`. |
| `0x005891c6 CDXTexture__InitCpuVendorAndSimdFlags` | Called by `CFastVB__InitDispatchTableByCpuFeature` at `0x00589327`; initializes a local SEH frame, seeds `GenuineIntel`, captures `cpuid_basic_info(0)` vendor/leaf values, and jumps into the Wave679 split continuation `0x0058920c CDXTexture__DetectCpuSimdFlags`, tied to CPUID feature bits `0x02000000` and `0x04000000`. |

Read-back evidence:

- `ApplySimdGateDualProfileWave892.java dry`: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplySimdGateDualProfileWave892.java apply`: `updated=3 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplySimdGateDualProfileWave892.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 3 metadata rows, 3 tag rows, 5 xref rows, 443 instruction rows, and 3 decompile rows.
- Queue after Wave892: 6113 total, 6065 commented, 48 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `6065/6113 = 99.21%`.
- Next raw commentless row: `0x0058aacf CTexture__HandleDirective_If`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260526-052708_post_wave892_simd_gate_dual_profile_verified`, 19 files, 173149063 bytes, `DiffCount=0`.

What this proves:

- The three target function rows exist in the saved Ghidra project.
- The saved comments and tags include `simd-gate-dual-profile-wave892` and `wave892-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to metadata, tags, xrefs, instruction exports, decompile exports, and the refreshed queue.

What remains unproven:

- Exact stream/profile descriptor layout.
- Exact hidden stack ABI and dispatch-slot ownership.
- Exact Windows registry policy or CPU-feature dispatch policy.
- Runtime SIMD/MMX selection, interpolation, upload, or render behavior.
- BEA patching behavior.
- Rebuild parity.
