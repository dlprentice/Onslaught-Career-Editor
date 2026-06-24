# Ghidra ComponentBasedOn Copy Helper Signature - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 335 revisited the already named `0x00433390` `CComponentBasedOn__CopyFrom` helper after it was deliberately excluded from the Wave 334 unit/weapon value tranche. Fresh metadata, decompile, xref, instruction, tag, and caller-decompile read-back showed that the old saved signature still carried a stale extra `param_N` argument.

This pass saved a narrower signature, comment, and tags for one target:

| Address | Saved signature | Evidence summary |
| --- | --- | --- |
| `0x00433390` | `void __thiscall CComponentBasedOn__CopyFrom(void * this, void * sourceComponent)` | Deep-copy helper for component-based statement records. It clones scalar fields, owned string/resource pointer fields through `OID__FreeObject` / `OID__AllocObject`, rebuilds linked/list members including `this+0x5c` through `CSPtrSet__AddToTail`, and copies a fixed dword block beginning at `this+0x164`. |

No function was renamed and no new function boundary was created.

## Evidence

- Pre-mutation live Ghidra backup was verified at `G:\GhidraBackups\BEA_20260512_090411_actual_ghidra_project_verified` with `19` files, `152210311` bytes, and `DiffCount=0`.
- `ApplyComponentBasedCopySignatureTranche.java` dry run reported the planned one-target signature change with `renamed=0`, `missing=0`, and `bad=0`.
- `ApplyComponentBasedCopySignatureTranche.java` apply reported `updated=1`, `renamed=0`, `missing=0`, and `bad=0`, with `REPORT: Save succeeded`.
- Final read-back verified `1/1` metadata row, `1/1` decompile export, `4` xref rows, `805` instruction rows, and `1/1` tag row.
- Caller decompile read-back for `CComponentBasedOn__VFunc_01_0043db90` now shows the two call sites passing only `this_00` plus `sourceComponent` or null; the stale third argument is gone from the caller view.
- `cmd.exe /c npm run test:ghidra-component-based-copy-signature` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5904` functions, `928` commented functions, `4976` commentless functions, `1981` undefined signatures, and `2186` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `G:\GhidraBackups\BEA_20260512_091719_post_wave335_verified` with `19` files, `152210311` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra signature/comment/tag evidence only. It does not prove exact source body identity, complete concrete `CComponentBasedOn` layout, local variable recovery, structure typing, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/component-based-copy-wave335/current/`.
