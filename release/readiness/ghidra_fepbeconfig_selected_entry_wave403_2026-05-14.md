# Ghidra FEPBEConfig Selected Entry Correction Tranche - 2026-05-14

Status: public-safe static evidence note

This note records a serialized static Ghidra correction wave for one frontend Battle Engine configuration helper. It documents saved Ghidra metadata only. It does not include private decompile excerpts, private screenshots, copied executables, copied saves, raw runtime evidence, or private asset payloads.

## What Changed

| Address | Saved state | Public-safe evidence summary |
| --- | --- | --- |
| `0x00451a40` | `int * __fastcall FEPBEConfig__FindSelectedEntryByGlobalId(void * list_state)` | Corrected the stale `CUnitAI__FindLinkedNodeByGlobalId` owner label to a `FEPBEConfig` selected-entry list helper. Static read-back shows the helper seeds an iterator cursor at `+0x28` from list head `+0x20`, walks link nodes through `+0x4`, and returns the first entry whose leading id matches `DAT_0089d94c`. |

## Caller Context

Fresh xref read-back shows three callers, all from `CFEPBEConfig__Render` at `0x00450da1`, `0x0045139b`, and `0x00451638`. Caller decompile read-back spells the argument as `&DAT_0089da14`, the global list-state rooted at `0x0089da14`.

The previous `CUnitAI` owner label is superseded by this caller/context evidence. This does not prove a concrete list-state structure or entry layout.

## Source Boundary

FEPBEConfig source file is present only as page-shell evidence in the current Stuart source snapshot. The current source snapshot does not provide a direct implementation body for this helper, so the saved name is a conservative retail-binary owner correction from xrefs, globals, and list-iterator behavior rather than exact source-body identity.

## Validation

- `ApplyFEPBEConfigSelectedEntryWave403.java` dry run: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`.
- `ApplyFEPBEConfigSelectedEntryWave403.java` apply run: `updated=1 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Metadata/decompile/xref/tag/instruction/caller read-back is stored under ignored `subagents/`.
- Focused probe: `tools/ghidra_fepbeconfig_selected_entry_wave403_probe.py --check`.
- Self-test: `tools/ghidra_fepbeconfig_selected_entry_wave403_probe_test.py`.
- Read-back verified `1` metadata row, `1` decompile export, `3` xref rows, `1` tag row, post-signature caller spelling through `CFEPBEConfig__Render`, and instruction evidence for the `+0x20`, `DAT_0089d94c`, `+0x4`, and return path.
- Refreshed queue reports `6028` functions, `1556` commented functions, `4472` commentless functions, `1910` undefined signatures, and `1859` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1556/6028 = 25.81%`, strict clean-signature `1491/6028 = 24.73%`.
- The live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_053055_post_wave403_fepbeconfig_selected_entry_verified` with `19` files, `154798983` bytes, and `HashDiffCount=0`.

## Claim Boundary

This tranche improves saved static Ghidra name, signature, comment, and tags for one `FEPBEConfig` selected-entry helper. It records that the `CUnitAI owner label superseded` claim is now saved in Ghidra and public docs. It does not prove runtime frontend behavior, does not prove exact source identity, does not recover concrete structure types/locals, does not launch or patch `BEA.exe`, and does not prove rebuild parity.
