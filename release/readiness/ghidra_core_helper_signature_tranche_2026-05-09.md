# Ghidra Core Helper Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra signature/comment evidence

## Objective

Continue the saved-Ghidra static re-audit by hardening a small core-helper slice. This tranche targets functions where read-back evidence showed object-pointer use, timestamp/global-field updates, cleanup flow, or vector magnitude behavior, without claiming final class layout, source identity, runtime behavior, or rebuild parity.

## Saved Ghidra Changes

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00402000` | `CUnitAI__SetStateTimestampCCToNow` | Hardened from `int param_1` to `void * this`. |
| `0x00402010` | `CUnit__ResetFieldD0ToGlobalThreshold` | Hardened from `int param_1` to `void * this`. |
| `0x00402020` | `CGeneralVolume__ResetCooldownTimestamp` | Hardened from `int param_1` to `void * this`. |
| `0x00402220` | `CAirGuide__ShutdownAndUnlink` | Hardened from `void * param_1` to `void * this`. |
| `0x004026b0` | `Vec3__Magnitude` | Hardened from `void * param_1` to `void * this`. |
| `0x00403690` | `CUnit__ReleaseAllAttachedParticleNodes` | Hardened from `int __fastcall ... (int param_1)` to `bool __fastcall ... (void * this)`. |

## Commands

Focused test/probe:

```powershell
py -3 tools\ghidra_core_helper_signature_tranche_probe_test.py
py -3 tools\ghidra_core_helper_signature_tranche_probe.py --check
py -3 -m py_compile tools\ghidra_core_helper_signature_tranche_probe.py tools\ghidra_core_helper_signature_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-core-helper-signature-tranche
```

Serialized Ghidra read-back and mutation:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/signature-debt-tranche6/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche6/current/metadata.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/signature-debt-tranche6/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche6/current/decompile 120
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/signature-debt-tranche6/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche6/current/xrefs.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/signature-debt-tranche6/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche6/current/instructions.tsv 0 80
bash tools/run_ghidra_headless_postscript.sh ApplyCoreHelperSignatureTranche.java dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/signature-debt-tranche6/current/comments.tsv dry
bash tools/run_ghidra_headless_postscript.sh ApplyCoreHelperSignatureTranche.java apply
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/signature-debt-tranche6/current/comments.tsv apply
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/signature-debt-tranche6/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche6/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/signature-debt-tranche6/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche6/current/decompile_readback 120
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
```

## Result

```text
Ghidra core-helper signature tranche probe
Status: PASS
Targets: 6; hardened: 6; xref rows: 149; instruction rows: 486

Ghidra static re-audit queue probe
Status: PASS
Total functions: 5866
Commentless functions: 5470
Undefined signatures: 2078
Param signatures: 2553
Uncertain owner names: 0
Address-suffixed helpers: 0
Address-suffixed wrappers: 0
```

## Process Notes

- Signature dry/apply ran serially and saved all six target signatures with `updated=0 skipped=6 missing=0 bad=0` in dry mode and `updated=6 skipped=0 missing=0 bad=0` in apply mode.
- Comment dry/apply ran serially and saved six proof-boundary comments with `applied=0 skipped=6 missing=0 bad=0` in dry mode and `applied=6 skipped=0 missing=0 bad=0` in apply mode.
- The focused checker uses raw instruction-export operands and post-signature decompile tokens, so symbolic source labels are not treated as instruction read-back evidence unless the exporter actually emits them.

## What This Proves

- The three timestamp/reset helpers now have explicit object-pointer parameters matching the checked `DAT_00672fd0`-adjacent field-write shape.
- `CAirGuide__ShutdownAndUnlink` now has an explicit object-pointer parameter matching the checked unlink/shutdown read-back.
- `Vec3__Magnitude` now has an explicit object-pointer parameter with double return matching the checked three-float square-root path.
- `CUnit__ReleaseAllAttachedParticleNodes` now has a boolean return and object-pointer parameter matching the checked cleanup-loop success/failure shape.
- The refreshed queue increased commented functions from `390` to `396`, reduced commentless functions from `5476` to `5470`, and reduced `param_N` signatures from `2559` to `2553`.

## What This Does Not Prove

- This does not prove concrete `CUnitAI`, `CUnit`, `CGeneralVolume`, `CAirGuide`, or `Vec3` structure layouts.
- This does not prove exact Stuart-source identity or rebuild parity.
- This does not add tags, recover local names, or finalize all caller semantics.
- This does not prove runtime behavior, patch or launch `BEA.exe`, or mutate the installed game.
- This does not close broader signature, comment, tag, type, local-name, structure, source-identity, or runtime-proof debt.

## Privacy / Release Safety

This note includes repo-relative paths, public addresses, function names, aggregate counts, command summaries, and proof boundaries only. Raw decompile output, screenshots, frame data, copied saves, copied executables, private install paths, and generated JSON remain under ignored `subagents/`.
