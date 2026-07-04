# Ghidra Controls Remap Comment Tranche - 2026-05-13

Status: GREEN public-safe static RE evidence.

## Summary

Serialized headless dry/apply/read-back saved proof-boundary comments and tags for `5` already named controls-remap helpers in the Steam `BEA.exe` Ghidra project. The pass preserves the current names/signatures, records remap dispatch, key-remap, device-category, duplicate-binding cleanup, and free-binding-slot evidence, and tags the tranche as `controls-remap-wave372`.

## Saved Targets

| Address | Saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x00453f50` | `Controls__DispatchRemap` | Dispatches remap action codes through a jump-table style path and invokes a write-callback for one or more binding entries. |
| `0x004541e0` | `Controls__RemapKey` | High-level remap path that stores key/remap globals, dispatches remap writes, and calls duplicate-binding cleanup. |
| `0x00454e00` | `Controls__GetDeviceCategory` | Maps device/input codes into category-style values used by remap and duplicate-binding logic. |
| `0x00454e90` | `Controls__ClearDuplicateBinding` | Scans binding entries/slots and clears duplicates by writing sentinel-style values into matched slots. |
| `0x00456650` | `Controls__FindFirstFreeBindingSlot` | Searches the active binding table for an available slot and returns a boolean-style availability result. |

## Validation

| Check | Result |
| --- | --- |
| Focused probe tests | `py -3 tools\ghidra_controls_remap_comment_probe_test.py` passed `2/2`. |
| Python compile | `py -3 -m py_compile tools\ghidra_controls_remap_comment_probe.py tools\ghidra_controls_remap_comment_probe_test.py` passed. |
| Expected red check | `cmd.exe /c npm run test:ghidra-controls-remap-comment` failed before mutation because dry/apply summaries and after-readback files were absent. |
| Headless apply | `ApplyControlsRemapCommentTranche.java` dry/apply both reported `targets=5 changed_or_would_change=5 failed=0`; apply printed `REPORT: Save succeeded`. |
| Read-back exports | Metadata `5`, decompile `5`, xrefs `93`, instruction rows `1305`, and tags `5`. |
| Focused package probe | `cmd.exe /c npm run test:ghidra-controls-remap-comment` passed with targets `5`, xref evidence hits `10`, instruction evidence hits `16`, stale token hits `0`, and overclaim hits `0`. |
| Whole-database queue | `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with `6020` total functions, `1329` commented functions, `4691` commentless functions, `1939` undefined signatures, and `1980` `param_N` signatures. |
| Current proxies | Comment-backed `1329/6020 = 22.08%`; strict clean-signature `1267/6020 = 21.05%`. These are telemetry only, not milestones. |
| Ghidra backup | Live `BEA.gpr`/`BEA.rep` backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_113000_post_wave372_controls_remap_verified` with `19` files, `153455495` bytes, and `HashDiffCount=0`. |

## Claim Boundary

This is saved static retail Ghidra comment/tag refinement for already named controls-remap helpers. It does not prove runtime remap/input behavior, exact Stuart-source method identities, concrete options-entry/controller layouts or field types, raw callback boundary ownership, BEA launch behavior, game patching, or rebuild parity.
