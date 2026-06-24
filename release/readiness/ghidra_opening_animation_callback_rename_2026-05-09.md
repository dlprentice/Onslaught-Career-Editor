# Ghidra Opening Animation Callback Rename - 2026-05-09

Status: public-safe saved-Ghidra rename/comment evidence, not final owner/source/signature/runtime proof

## Objective

Consume the last current name-confidence wrapper tail at `0x00418090` without overclaiming the unresolved DATA table owner. The saved Ghidra name now reflects observed behavior instead of a generic `FindAnimationIndex` wrapper label.

## Inputs

- Target: `0x00418090`
- Previous saved name: `FindAnimationIndex__Wrapper_00418090`
- New saved name: `OpeningAnimationStateCallback__StartOpeningIfPending`
- Raw evidence root: `subagents/ghidra-static-reaudit/opening-animation-callback-rename/current/`
- Probe: `tools/ghidra_opening_animation_callback_rename_probe.py`
- Probe test: `tools/ghidra_opening_animation_callback_rename_probe_test.py`

## Commands

Focused validation:

```powershell
py -3 tools\ghidra_opening_animation_callback_rename_probe_test.py
py -3 tools\ghidra_opening_animation_callback_rename_probe.py --check
py -3 -m py_compile tools\ghidra_opening_animation_callback_rename_probe.py tools\ghidra_opening_animation_callback_rename_probe_test.py
cmd.exe /c npm run test:ghidra-opening-animation-callback-rename
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Mutation/read-back summary:

- Rename-map preflight accepted `1` row.
- Headless rename dry/apply renamed `0x00418090` from `FindAnimationIndex__Wrapper_00418090` to `OpeningAnimationStateCallback__StartOpeningIfPending`.
- The first comment dry run caught a malformed TSV row before apply. The TSV was fixed, rerun in dry mode, and only then applied.
- Metadata, decompile, xref, mixed-table, unresolved type-name, and resolved CCockpit RTTI table read-back verified the saved state.

## Result

```text
Ghidra opening-animation callback rename probe
Status: PASS
Target: 0x00418090 FindAnimationIndex__Wrapper_00418090 -> OpeningAnimationStateCallback__StartOpeningIfPending
Classification: saved-opening-animation-callback-rename-owner-unproven
```

Read-back summary:

- Metadata and decompile read-back show the new saved name and not the stale wrapper name.
- The proof-boundary comment records the behavior-backed semantic rename and owner/table caveat.
- The checked body still carries the `opening` string token, `FindAnimationIndex` call, state field `+0x254`, timer field `+0x25c`, and animation-start vcall `+0xf0`.
- Xref read-back still shows a DATA xref from mixed slot `0x005d9080`.
- Type-name read-back leaves `0x005d9080` unresolved.
- Resolved CCockpit RTTI vtables at `0x005d94ac` and `0x005d9524` were checked and do not prove that `0x00418090` belongs to CCockpit.
- The refreshed static re-audit queue reports `5866` functions, `372` commented functions, `5494` commentless functions, `0` broad uncertain-owner names, `0` address-suffixed helper names, and `0` address-suffixed wrapper names.

## What This Proves

- `0x00418090` is no longer saved as a generic `FindAnimationIndex` wrapper.
- The new saved name is a conservative behavior label for starting the opening animation when the pending state path resolves the `opening` animation.
- The current name-confidence helper/wrapper/uncertain-owner tail is zero in the refreshed queue snapshot.

## What This Does Not Prove

- This does not prove exact table or class owner for slot `0x005d9080`.
- This does not prove exact source method identity.
- This does not harden signatures, parameter names, local names, structures, data types, or tags.
- This does not prove runtime opening-animation behavior.
- This does not prove adjacent historical `CCockpit` names are correct.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.
- This does not complete the broader static RE campaign; signature, comment, type, tag, local-name, structure, source-identity, and runtime-proof debt remain broad.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
