# Ghidra CFEPDevelopment Boundary / Signature Correction Tranche - 2026-05-13

Status: public-safe static RE evidence

## Summary

Wave 384 corrected the saved Ghidra `CFEPDevelopment` cluster after fresh metadata, decompile, instruction, xref, tag, and callsite review. The pass created the missing file-name comparator at `0x00458050`, moved the world-file enumerator boundary from the stale mid-body `0x00458100` label back to the true prologue at `0x00458090`, and hardened seven adjacent `CFEPDevelopment` helper signatures/comments/tags.

This is static retail-binary evidence only. It does not prove runtime development-menu behavior, storage-device behavior, exact source body recovery, concrete `CFEPDevelopment` layout recovery, local-variable typing, BEA launch behavior, game patching, or rebuild parity. Stuart's checked source snapshot does not currently provide a matching `FEPDevelopment.cpp` source body, so retail Ghidra read-back remains the authority for this tranche.

## Saved Targets

| Address | Saved signature | Evidence boundary |
| --- | --- | --- |
| `0x00458050` | `int __cdecl CFEPDevelopment__CompareWorldFileNamePtrs(char * * left, char * * right)` | Created comparator passed to the generic quick-sort wrapper during world-file list ordering. |
| `0x00458090` | `bool __fastcall CFEPDevelopment__EnumerateWorldFiles(void * this)` | Corrected true function boundary; owns the world-file enumeration/allocation/sort body previously started mid-body at `0x00458100`. |
| `0x004581e0` | `void __fastcall CFEPDevelopment__Shutdown(void * this)` | Releases the world-file list state and resets list fields. |
| `0x004583c0` | `void __fastcall CFEPDevelopment__RenderWorldListEntries(void * this)` | Renders the enumerated world-list rows for the development frontend page. |
| `0x004584d0` | `void __thiscall CFEPDevelopment__Render(void * this, float transition, int dest)` | Corrected calling convention from the stale stdcall interpretation; body renders the development page and delegates world-list rows. |
| `0x00458710` | `bool __fastcall CFEPDevelopment__RefreshWorldListCore(void * this)` | Core world-list refresh helper after storage-device resolution. |
| `0x004589f0` | `void __fastcall CFEPDevelopment__RefreshWorldList(void * this)` | Wrapper that pushes a zero resolver argument, calls device resolution, then refreshes the list core. |
| `0x00458ce0` | `void __thiscall CFEPDevelopment__ResolveActiveStorageDevice(void * this, int unused_refresh_arg)` | Corrected from fastcall-style stale signature to `ret 0x4` thiscall shape; observed caller pushes zero, and the current body does not consume the argument. |
| `0x00459580` | `void __thiscall CFEPDevelopment__ScheduleWorldListRefresh(void * this, int ignored_arg)` | Corrected from fastcall-style stale signature to `ret 0x4` thiscall shape; schedules or triggers the development world-list refresh path. |

The old `0x00458100` function object is intentionally absent after the boundary repair; read-back keeps it as a guard for the stale mid-body entry.

## Validation

| Check | Result |
| --- | --- |
| `tools/ApplyFepDevelopmentWave384.java` dry run | PASS; `updated=0 skipped=8 created=0 would_create=1 boundary_moved=0 would_boundary_move=1 renamed=0 would_rename=0 missing=0 bad=0`; `REPORT: Save succeeded`. |
| `tools/ApplyFepDevelopmentWave384.java` apply run | PASS; `updated=9 skipped=0 created=1 would_create=0 boundary_moved=1 would_boundary_move=0 renamed=0 would_rename=0 missing=0 bad=0`; `REPORT: Save succeeded`. |
| Metadata/decompile/xref/instruction/callsite/tag read-back | PASS; `9` current saved targets plus stale-boundary guard read back, `10` decompile exports, `17` xref rows, `2210` instruction rows, `1413` callsite-instruction rows, and `10` tag rows. |
| `py -3 tools\ghidra_fepdevelopment_wave384_probe_test.py` | PASS; unit tests `2/2`. |
| `cmd.exe /c npm run test:ghidra-fepdevelopment-wave384` | PASS; focused probe status `PASS`, `9` targets, `1` boundary guard, `7` callsite evidence hits, and `13` instruction evidence hits. |
| `py -3 -m py_compile tools\ghidra_fepdevelopment_wave384_probe.py tools\ghidra_fepdevelopment_wave384_probe_test.py` | PASS after serial rerun; the first compile overlapped an importer/cache write and hit a transient `__pycache__` access denial. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS after refreshing `ExportFunctionQualitySnapshot.java`; `6027` total functions, `1423` commented functions, `4604` commentless functions, `1935` undefined signatures, and `1917` `param_N` signatures. |
| Live Ghidra project backup | PASS; `G:\GhidraBackups\BEA_20260513_175250_post_wave384_fepdevelopment_verified`, `19` files, `153783175` bytes, `HashDiffCount=0`. |

Current confirmation proxies are telemetry only: comment-backed `1423/6027 = 23.61%`, strict clean-signature `1361/6027 = 22.58%`. They are not milestones and do not mark the RE campaign complete.

## Not Proven

- Runtime development-menu world-list behavior, storage-device behavior, or frontend render behavior.
- Exact source body recovery for `FEPDevelopment.cpp`; the checked Stuart source snapshot lacks this source body.
- Concrete `CFEPDevelopment` structure layout, local variable types, or exact semantics for every field touched by this cluster.
- BEA launch behavior, patching behavior, packaged-app behavior, or rebuildable gameplay parity.
