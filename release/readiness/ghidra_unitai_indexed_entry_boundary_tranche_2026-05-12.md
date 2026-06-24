# Ghidra UnitAI Indexed Entry Boundary Tranche - 2026-05-12

Status: GREEN public-safe static Ghidra correction evidence.

This wave continued the saved-Ghidra static re-audit around `CUnitAI` indexed-entry helpers and adjacent `CMCBuggy` / `CMCHiveBoss` vtable slots. It hardened two existing `CUnitAI` signatures and recovered three previously missing function starts after serialized dry/apply/read-back. The shared vtable-slot names are behavior-bounded retail labels, not exact source virtual-method closure.

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00444f00` | `CUnitAI__CallIndexedEntryVFunc10` | Hardened to one `entryIndex` stack argument; resolves an indexed entry and dispatches entry vfunc slot `+0x10` when present. |
| `0x00444f20` | `CUnitAI__CanUseIndexedSegmentEntry` | Hardened to one `entryIndex` stack argument; checks indexed entry, linked segment/core-child gates, and active segment value context. |
| `0x00494fa0` | `SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag` | Recovered function boundary shared by `CMCBuggy` slot `17` and `CMCHiveBoss` slot `6`; updates output bit `0` through the `CUnitAI__CanUseIndexedSegmentEntry` path. |
| `0x00494ff0` | `SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10` | Recovered function boundary shared by `CMCBuggy` slot `18` and `CMCHiveBoss` slot `7`; returns `0` while the state-context gate is set, otherwise calls `CUnitAI__CallIndexedEntryVFunc10`. |
| `0x00495020` | `CMCBuggy__VFunc_GetUnitAIEntryTableRoot` | Recovered `CMCBuggy` slot `19` getter that follows the controller-owned entry-table root pointer. |

Evidence:

- `tools/ApplyUnitAIIndexedEntryBoundaryTranche.java` dry/apply passed with `targets=5 changed_or_would_change=5 failed=0`; the apply reported `REPORT: Save succeeded`.
- Read-back verified `5` metadata rows, `5` decompile exports, `7` xref rows, `455` instruction rows, `5` tag rows, `72` vtable-slot rows, and `3` vtable owner rows for `CMCBuggy`, `CMCCannon`, and `CMCHiveBoss` context.
- Focused validation passed: `py -3 tools\ghidra_unitai_indexed_entry_boundary_probe_test.py`, `py -3 -m py_compile tools\ghidra_unitai_indexed_entry_boundary_probe.py tools\ghidra_unitai_indexed_entry_boundary_probe_test.py`, `py -3 tools\ghidra_unitai_indexed_entry_boundary_probe.py --check`, and `cmd.exe /c npm run test:ghidra-unitai-indexed-entry-boundary`.
- The refreshed all-functions baseline reports `6002` total functions, `0` legacy weak names, `1951` undefined signatures, and `2073` `param_N` signatures.
- The refreshed quality queue reports `6002` functions, `1173` commented functions, `4829` commentless functions, `1951` undefined signatures, and `2073` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1173/6002 = 19.54%`, strict clean-signature `1110/6002 = 18.49%`. The `20%` value is not a milestone or acceptance gate.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260512_230703_post_wave354_unitai_indexed_entry_verified` with `18` files, `152931207` bytes, and `HashDiffCount=0`.

Raw proof remains ignored under `subagents/ghidra-static-reaudit/unitai-indexed-entry-wave354/current/`.

Claim boundary: this is static retail Ghidra evidence only. It corrects saved function boundaries, names, signatures, comments, and tags for five indexed-entry/vtable-slot targets, but it does not prove exact source virtual names, concrete class layout, local/type recovery, runtime UnitAI or motion-controller behavior, BEA launch, game patching, or rebuild parity.
