# Ghidra CShell / CUnit Tail Wave507 Readiness Note

Date: 2026-05-17

Wave507 saved static Ghidra name/signature/comment/tag updates for five shell/unit-tail helpers:

| Address | Saved state |
| --- | --- |
| `0x004df4c0` | `void * __thiscall CShell__Constructor(void * this)` |
| `0x004df530` | `void __thiscall CShell__CopyResourceNameToInlineBuffer(void * this, char * resource_name)` |
| `0x004df550` | `void __thiscall CShell__Init(void * this, void * init)` |
| `0x004dfce0` | `bool __thiscall CUnit__TryActivateAndEnableShadows(void * this)` |
| `0x004dfd10` | `void __thiscall CUnit__VFunc18_SyncOldVectorAndClampHeight(void * this)` |

Evidence:

- Fresh metadata, tags, xrefs, instruction, decompile, and vtable review.
- `ApplyShellUnitTailWave507.java` dry run: `updated=0 skipped=5 renamed=0 would_rename=4 missing=0 bad=0`.
- Apply: `updated=5 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`.
- Final verify dry: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`.
- Post-readback exports: `5` metadata rows, `5` tag rows, `6` xref rows, `2505` instruction rows, `5` decompile exports, `200` vtable-slot rows.
- Probe: `py -3 tools\ghidra_shell_unit_tail_wave507_probe.py --check` PASS.
- npm probe: `cmd.exe /c npm run test:ghidra-shell-unit-tail-wave507` PASS.
- Queue refresh: `6078` total functions, `2328` commented functions, `3750` commentless functions, `1636` exact-undefined signatures, `1478` `param_N` signatures.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-161531_post_wave507_shell_unit_tail_verified`, `19` files, `158043015` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

This is static saved-Ghidra evidence only. It does not prove exact CShell source file, event semantics, render-object type, full CShell/CUnit/static-shadow layouts, runtime projectile-shell/shadow/movement behavior, BEA launch behavior, game patching, or rebuild parity.
