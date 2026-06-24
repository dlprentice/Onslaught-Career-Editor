# Ghidra Render Validation Tail Wave570 Readiness Note

Date: 2026-05-19
Status: PASS

## Scope

Wave570 hardened five saved Ghidra rows:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00527cc0` | `bool __thiscall CWaterRenderSystem__ValidateVBufferAndMarkReady(void * this, int expected_valid_so_far)` | `RET 0x4` confirms one stack argument after `this`; the helper compares it to `this+0x0c`, logs first-attempt text when `this+0x10` is clear, and returns a boolean. |
| `0x00527d20` | `bool __thiscall CDXLandscape__ValidateDeviceAndUpdateValidSoFar(void * this)` | Plain `RET` confirms no stack arguments; the helper calls `CEngine__DeviceCall118_WithZeroOut(&DAT_00855bb0)` while validation is pending, logs `ValidSoFar` failures, and decrements `this+0x0c` only on the false-return path. |
| `0x00527da0` | `void __thiscall CVBufTexture__MarkAccepted(void * this)` | Plain `RET` confirms no stack arguments; if `this+0x10` is clear, it logs `RM: Accepting %s %d` and sets `this+0x10` to `1`. |
| `0x00527dd0` | `int __thiscall CDXEngine__GetRenderQueueSortKeyAt0C(void * this)` | ECX-only field reader for `this+0x0c`, used by landscape, render queue, engine multipass, and water render callers. |
| `0x00527e00` | `bool __thiscall CWaterRenderSystem__CheckVBufValidAndHandleFailure(void * this)` | ECX-only failure helper around `DAT_00854dd8`; it logs `CheckVBufValid` failures, accepts the zero-count case, otherwise decrements `this+0x0c` and returns false. |

No `source-parity` tag was applied. No owner rename was made because the xrefs span battle-line, landscape, mesh, surf, water, render-queue, and engine render paths. This tranche is bounded to retail binary evidence.

## Verification

- Dry pass: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`
- Apply pass: `updated=5 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `5` metadata rows, `5` tag rows, `51` xref rows, `515` target instruction rows, and `5` target decompiles
- Focused probe: `py -3 tools\ghidra_render_validation_tail_wave570_probe.py --check` PASS
- Npm wrapper: `cmd.exe /c npm run test:ghidra-render-validation-tail-wave570` PASS
- Queue refresh: `6093` total functions, `2837` commented, `3256` commentless, `1494` exact-undefined signatures, `1158` `param_N` signatures
- Post-Wave570 comment-backed proxy: `2837 / 6093 = 46.56%`
- Post-Wave570 strict clean-signature proxy: `2783 / 6093 = 45.68%`
- Backup: `G:\GhidraBackups\BEA_20260518-234439_post_wave570_render_validation_tail_verified`
- Backup verification: `19` files, `160074631` bytes, source/destination manifest hash `615C53DAACECA6A54B94D5ABBB379A80211AD349F75ACE4E3CAD7AFB7AFB7006`

## Limits

This is saved static Ghidra evidence only. No runtime D3D behavior was claimed. Exact render validation record class/layout, exact source identity, BEA launch, game patching, and rebuild parity remain unproven.
