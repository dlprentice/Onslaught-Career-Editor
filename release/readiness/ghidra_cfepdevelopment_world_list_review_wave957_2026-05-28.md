# Ghidra CFEPDevelopment World-List Review Wave957 Readiness Note

Status: read-only static review
Date: 2026-05-28
Scope: `cfepdevelopment-world-list-review-wave957`

Wave957 re-reviewed the `CFEPDevelopment` world-list/storage-device slice after fresh serialized headless Ghidra exports. No mutation was needed in Ghidra; anchor phrase: no mutation. The prior Wave384 boundary, signature, comment, and tag corrections still match the current saved database.

Primary Wave911 targets:

| Address | Result |
| --- | --- |
| `0x004584d0 CFEPDevelopment__Render` | Still reads as `void __thiscall CFEPDevelopment__Render(void * this, float transition, int dest)`, uses `ECX` as the page object, and returns with `RET 0x8`. The body sets frontend/D3D render state and calls `0x004583c0 CFEPDevelopment__RenderWorldListEntries`. |
| `0x00458ce0 CFEPDevelopment__ResolveActiveStorageDevice` | Still reads as `void __thiscall CFEPDevelopment__ResolveActiveStorageDevice(void * this, int unused_refresh_arg)`, returns with `RET 0x4`, and has callers that push `0` before calling it. The current body updates storage-device fields at `this+0x08/+0x0c/+0x10`, can set `this+0x14`, and clears the global dialog/message gate for selected frontend pages. |

Context anchors:

- `0x00458050 CFEPDevelopment__CompareWorldFileNamePtrs` remains a standalone qsort comparator used by `0x00458090 CFEPDevelopment__EnumerateWorldFiles`.
- `0x00458090 CFEPDevelopment__EnumerateWorldFiles` remains the true world-file enumeration prologue. The stale `0x00458100` boundary is still intentionally absent; instruction evidence at `0x00458100` is a `PUSH 0x62921c` inside the `0x00458090` body, not a function prologue.
- `0x004583c0 CFEPDevelopment__RenderWorldListEntries` still owns the visible world-list row draw path reached by `CFEPDevelopment__Render`.
- `0x00458710 CFEPDevelopment__RefreshWorldListCore` remains the storage/save refresh and dialog-routing core. It calls `PCPlatform__GetStorageDeviceInfo`, `EnumerateSaveFiles_1`, `CFrontEnd__PlaySound`, and `CFrontEnd__SetPage(&DAT_0089d758, page, 0x46)`.
- `0x004589f0 CFEPDevelopment__RefreshWorldList` and `0x00459580 CFEPDevelopment__ScheduleWorldListRefresh` both push zero before calling `CFEPDevelopment__ResolveActiveStorageDevice`.
- `0x004623e0 CFEPMain__DoAction` reaches `CFEPDevelopment__RefreshWorldList` on selected main-menu action paths; `0x00466ae0 CFrontEnd__SetPage` and `0x00468770 CFrontEnd__PlaySound` are the frontend transition/sound context.

Normalization note:

The same `CFEPDevelopment` offsets participate in more than one static mode: world-file listing, storage/save refresh, and refresh timing. This review does not publish a single concrete `CFEPDevelopment` struct layout. In particular, `this+0x04` is pointer-array state in the world-file enumeration/shutdown path but timer state in `CFEPDevelopment__ScheduleWorldListRefresh`; field names remain mode-qualified until stronger layout evidence exists.

Read-back evidence:

- Exports: 13 metadata rows, 13 tag rows, 221 xref rows, 877 instruction rows, and 13 decompile-index rows.
- Expected stale-boundary guard: `0x00458100` is `MISSING`.
- Existing continuity probe: `test:ghidra-fepdevelopment-wave384` still passes against current saved Ghidra state.
- Verified backup: `G:\GhidraBackups\BEA_20260528-111610_post_wave957_cfepdevelopment_world_list_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.
- Static function-quality closure remains `6151/6151 = 100.00%`.
- Wave911 focused re-audit progress after Wave957 is `292/1408 = 20.74%`.

What this proves:

- The saved Ghidra function rows for the `CFEPDevelopment` world-list/storage-device slice remain coherent with fresh metadata, tags, xrefs, instruction, and decompile evidence.
- The Wave384 boundary correction that removed the stale `0x00458100` function object still holds.
- The Wave384 calling-convention corrections for `CFEPDevelopment__Render`, `CFEPDevelopment__ResolveActiveStorageDevice`, and `CFEPDevelopment__ScheduleWorldListRefresh` still hold.
- The static bridge from main-menu actions to development-page refresh, storage-device query, dialog routing, frontend page transitions, and list rendering is documented with read-back evidence.

What remains unproven:

- Runtime development-menu reachability.
- Runtime world-list/storage-device/save-dialog behavior.
- Runtime frontend navigation/rendering behavior.
- Concrete `CFEPDevelopment` layout names.
- Exact `FEPDevelopment.cpp` source-body identity.
- BEA patching behavior.
- Rebuild parity.
