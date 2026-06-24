# Ghidra Queue-Head Helper Correction Tranche - 2026-05-13

Status: public-safe static RE evidence

## Summary

Wave 388 saved Ghidra name/signature/comment/tag metadata for five queue-head helper targets after metadata, decompile, xref, instruction, callsite-instruction, and tag read-back. The pass preserved already-good labels where appropriate, corrected two over-specific owner labels, and fixed the `Mat34__MultiplyBasisToOut` signature after a dry/apply read-back exposed Ghidra's implicit `this` handling.

This is static Ghidra evidence only. It does not prove runtime behavior, exact Stuart-source method identity, concrete vector/matrix/monitor/line layouts, concrete local types, BEA launch, game patching, or rebuild parity.

## Saved Targets

| Address | Saved name | Saved signature | Evidence boundary |
| --- | --- | --- | --- |
| `0x004098c0` | `CLine__VFunc_01_004098c0` | `int __thiscall CLine__VFunc_01_004098c0(void * this, void * arg0, void * arg1, void * dispatch_target, void * arg3)` | CLine vtable-slot wrapper that forwards the ECX receiver plus four stack arguments to `dispatch_target` vfunc `+0x10`. |
| `0x00409e60` | `CGeneralVolume__ToDoubleIdentity` | `double __stdcall CGeneralVolume__ToDoubleIdentity(float input_value)` | x87 identity-style float-to-double helper used by JetPart turn and GeneralVolume axis-input wrappers. |
| `0x0040d320` | `Mat34__MultiplyBasisToOut` | `void * __thiscall Mat34__MultiplyBasisToOut(void * this, void * out_basis, void * rhs_basis)` | Owner-neutral Mat34-style 3x3 basis multiply; ECX is the left-hand basis, stack args are output basis and right-hand basis, and EAX returns `out_basis`. |
| `0x00414010` | `CMonitor__ClearCurrentTrackedEntryFlag60` | `void __thiscall CMonitor__ClearCurrentTrackedEntryFlag60(void * this)` | Calls `CBattleEngineWalkerPart__GetCurrentWeapon` from the receiver and clears field `+0x60` on the current weapon/tracked entry when present. |
| `0x0041ad10` | `Vec3__AddInPlace` | `void __thiscall Vec3__AddInPlace(void * this, void * add_vec3)` | Owner-neutral Vec3 in-place add helper; ECX is the destination vector and the one stack argument is the source vector to add. |

## Validation

| Check | Result |
| --- | --- |
| Headless `ApplyQueueHeadHelperWave388.java` dry run | PASS: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`. |
| Headless `ApplyQueueHeadHelperWave388.java` apply | PASS: `updated=5 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`. |
| Post-apply read-back exports | PASS: `5` metadata rows, `5` decompile exports, `97` xref rows, `1105` instruction rows, `190` callsite-instruction rows, and `5` tag rows. |
| `py -3 tools\ghidra_queue_head_helper_wave388_probe_test.py` | PASS: `2/2` tests. |
| `cmd.exe /c npm run test:ghidra-queue-head-helper-wave388` | PASS: `status=PASS`, `targets=5`, `commented=5`, `signature_hardened=5`, `xref_hits=12`, `instruction_hits=12`, and `callsite_hits=11`. |
| `py -3 -m py_compile tools\ghidra_queue_head_helper_wave388_probe.py tools\ghidra_queue_head_helper_wave388_probe_test.py` | PASS. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS after refreshing `ExportFunctionQualitySnapshot.java`: `6027` functions, `1444` commented functions, `4583` commentless functions, `1935` undefined signatures, and `1909` `param_N` signatures. |
| Actual Ghidra project backup | PASS: copied `BEA.gpr` and `BEA.rep` to `G:\GhidraBackups\BEA_20260513_200959_post_wave388_queue_head_helper_verified`; verified `19` files, `153947015` bytes, `HashDiffCount=0`. |

The current broad comment-backed proxy is `1444/6027 = 23.96%`. The stricter comment-plus-no-`undefined`-or-`param_N` proxy is `1382/6027 = 22.93%`. These values are telemetry only, not completion milestones.

## Not Proven

- Runtime line, input, monitor, weapon, vector, or matrix behavior.
- Exact source identity for every helper body.
- Concrete `CLine`, `CGeneralVolume`, `CMonitor`, `Vec3`, or `Mat34` layouts.
- Concrete local variable names/types for every decompiler temporary.
- BEA launch, game patching, or runtime proof.
- Rebuild parity or gameplay behavior.
