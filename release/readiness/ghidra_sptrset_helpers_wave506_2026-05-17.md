# Ghidra SPtrSet Helpers Wave506 Readiness Note

Date: 2026-05-17

Wave506 saved static Ghidra name/signature/comment/tag updates for six SPtrSet helper functions:

| Address | Saved state |
| --- | --- |
| `0x004e5850` | `void * __thiscall CSPtrSet__CopyCtorFromSource(void * this, void * source_set)` |
| `0x004e59f0` | `void __cdecl CSPtrSet__Initialise(int numNodes)` |
| `0x004e5a80` | `void __thiscall CSPtrSet__AddToHead(void * this, void * item)` |
| `0x004e5b20` | `void __thiscall CSPtrSet__AddToTail(void * this, void * item)` |
| `0x004e5c30` | `bool __thiscall CSPtrSet__Contains(void * this, void * item)` |
| `0x004e5c90` | `void * __thiscall CSPtrSet__At(void * this, int index)` |

Evidence:

- Fresh metadata, tags, xrefs, instruction, decompile, and `references/Onslaught/SPtrSet.cpp` / `.h` review.
- `ApplySPtrSetHelpersWave506.java` dry run: `updated=0 skipped=6 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply: `updated=6 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`.
- Final verify dry: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`.
- Post-readback exports: `6` metadata rows, `6` tag rows, `202` xref rows, `1470` instruction rows, `6` decompile exports.
- Probe: `py -3 tools\ghidra_sptrset_helpers_wave506_probe.py --check` PASS.
- npm probe: `cmd.exe /c npm run test:ghidra-sptrset-helpers-wave506` PASS.
- Queue refresh: `6078` total functions, `2323` commented functions, `3755` commentless functions, `1636` exact-undefined signatures, `1483` `param_N` signatures.
- Backup: `G:\GhidraBackups\BEA_20260517-154737_post_wave506_sptrset_helpers_verified`, `19` files, `158043015` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

This is static saved-Ghidra evidence only. It does not prove exact template-instantiation ownership, all caller preconditions, runtime pool behavior, BEA launch behavior, game patching, or rebuild parity.
