# Ghidra Platform/Shell Wave561 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00512630` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-18

Wave561 saved static Ghidra signature/comment/tag evidence for a ten-target platform/shell, PCLTShell, input, CShaderBase, and DeviceObject tranche from `0x00512130` through `0x00512fc0`. The bounded probe label for this tranche is `platform/shell`.

## Saved Scope

- Entry and shell: `CLTShell__WinMain`, `PCLTShell__ctor`, and `PCLTShell__ConfirmDevice`.
- Platform/input: `PlatformInput__ClearTransientKeyStateTable`, `PLATFORM__ProcessSystemMessages`, `Platform__HandleDeviceLostAndRestore`, and `PlatformInput__ClearAllKeyStateTables`.
- Device-object base: `CShaderBase__Init`, `CShaderBase__UnlinkFromRenderObjectLists`, and `DeviceObject__scalar_deleting_dtor`.

## Evidence

- `ApplyPlatformShellWave561.java` dry run: `updated=0 skipped=10 renamed=0 would_rename=4 missing=0 bad=0`.
- Apply: `updated=10 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`.
- Final dry verification: `updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0`.
- Read-back exports: `10` metadata rows, `10` tag rows, `30` xref rows, `650` target instruction rows, `16` vtable-slot rows, and `10` decompile rows.
- Focused probe: `tools/ghidra_platform_shell_wave561_probe.py`.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-191114_post_wave561_platform_shell_verified` with `19` files, `159812487` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Queue Telemetry

Post-Wave561 queue refresh:

- Total functions: `6089`
- Commented: `2782`
- Commentless: `3307`
- Exact-undefined signatures: `1512`
- `param_N` signatures: `1185`
- Comment-backed proxy: `2782/6089 = 45.69%`
- Strict clean-signature proxy: `2728/6089 = 44.80%`

## Limits

This is static retail-binary evidence only. Runtime launch/message-pump/input/device-loss/render-list behavior, concrete CLTShell/PLATFORM/PCLTShell/CShaderBase/DeviceObject layouts, exact source identities, BEA launch, patching, and rebuild parity remain unproven.
