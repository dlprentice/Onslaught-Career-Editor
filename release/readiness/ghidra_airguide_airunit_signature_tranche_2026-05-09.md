# Ghidra AirGuide/AirUnit Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra owner/name/signature/comment evidence

## Objective

Continue the saved-Ghidra static re-audit by reparsing the first commentless high-signal AirGuide/AirUnit cluster. This tranche corrects only the names and signatures backed by current decompile, xref, and instruction read-back, while leaving adjacent base/interpolation helpers deferred until their vtable owner and exact source identity are clearer.

## Saved Ghidra Changes

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00402150` | `CAirGuide__ctor` | Corrected from `ctor_like`; signature set to `void * __thiscall ... (void * this, void * guideTarget)`. |
| `0x00402200` | `CAirGuide__scalar_deleting_dtor` | Corrected from generic vfunc label; signature set to scalar-deleting destructor shape with `byte flags`. |
| `0x004026e0` | `CAirGuide__HandleEvent` | Corrected from generic vfunc label; signature set to `void __thiscall ... (void * this, void * event)`. |
| `0x004027c0` | `CAirGuide__AcquireNearestTargetReader` | Corrected owner prefix from the parent vfunc label and hardened the object-pointer signature. |
| `0x004028e0` | `CAirGuide__UpdateGroundClearanceCache` | Corrected owner prefix from the parent vfunc label and hardened the object-pointer signature. |
| `0x00402ad0` | `CAirUnit__Init` | Kept the saved name and hardened the init pointer signature to `void * init`. |
| `0x00402d30` | `CAirUnit__dtor_base` | Corrected from generic vfunc label; signature set to `void __fastcall ... (void * this)`. |

## Commands

Focused test/probe:

```powershell
py -3 tools\ghidra_airguide_airunit_signature_tranche_probe_test.py
py -3 -m py_compile tools\ghidra_airguide_airunit_signature_tranche_probe.py tools\ghidra_airguide_airunit_signature_tranche_probe_test.py
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\airguide-airunit-signature-tranche\current\rename_map_airguide_airunit.txt
py -3 tools\ghidra_airguide_airunit_signature_tranche_probe.py --check
cmd.exe /c npm run test:ghidra-airguide-airunit-signature-tranche
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Serialized Ghidra mutation/read-back:

```powershell
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/rename_map_airguide_airunit.txt dry
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/rename_map_airguide_airunit.txt apply
bash tools/run_ghidra_headless_postscript.sh ApplyAirGuideAirUnitSignatureTranche.java dry
bash tools/run_ghidra_headless_postscript.sh ApplyAirGuideAirUnitSignatureTranche.java apply
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/comments.tsv dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/comments.tsv apply
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/readback_addresses.txt subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/readback_addresses.txt subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/decompile_readback 220
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/readback_addresses.txt subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/xrefs_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/readback_addresses.txt subagents/ghidra-static-reaudit/airguide-airunit-signature-tranche/current/instructions_readback.tsv 0 320
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
```

## Result

```text
AirGuide/AirUnit signature tranche: PASS
Targets: 7
Renamed targets: 6
Signature-hardened targets: 7
Commented targets: 7
Xref rows: 31
Instruction rows: 2247

Ghidra static re-audit queue probe: PASS
Total functions: 5866
Commentless functions: 5452
Undefined signatures: 2078
Param signatures: 2535
Uncertain owner names: 0
Address-suffixed helpers: 0
Address-suffixed wrappers: 0
```

## Process Notes

- Rename-map preflight accepted `6` rows with `0` findings.
- Rename dry/apply ran serially and saved all `6` target names with `applied=0 skipped=6 missing=0 bad=0` in dry mode and `applied=6 skipped=0 missing=0 bad=0` in apply mode.
- Signature dry/apply ran serially and saved all `7` target signatures with `updated=0 skipped=7 missing=0 bad=0` in dry mode and `updated=7 skipped=0 missing=0 bad=0` in apply mode.
- Comment dry/apply ran serially and saved `7` proof-boundary comments with `applied=0 skipped=7 missing=0 bad=0` in dry mode and `applied=7 skipped=0 missing=0 bad=0` in apply mode.
- Metadata, decompile, xref, and instruction read-back reported `7/7` metadata targets, `7/7` decompile targets, `31` xref rows, and `2247` instruction rows.
- The follow-up quality snapshot increased commented functions from `407` to `414`, reduced commentless functions from `5459` to `5452`, and reduced `param_N` signatures from `2542` to `2535`.

## What This Proves

- The current `0x00402150` body is saved as an AirGuide constructor with one stack argument, not a vague `ctor_like` label with an extra phantom parameter.
- The current `0x00402200` body is saved as the AirGuide scalar-deleting destructor, backed by shutdown/unlink, delete-flag, optional free, and this-return evidence.
- The current `0x004026e0` body is saved as the AirGuide event handler that branches on events `2000` and `0x7d1`, then calls the two adjacent AirGuide refresh helpers and reschedules timers.
- The current `0x004027c0` and `0x004028e0` helper names now carry the AirGuide owner prefix and object-pointer signatures.
- `CAirUnit__Init` and the adjacent destructor-base body now have saved signatures/comments that match the observed init/config/particle-list and cleanup/delegation shapes.

## What This Does Not Prove

- This does not prove concrete `CAirGuide`, `CGuide`, `CAirUnit`, `CUnit`, event, particle, or world-height structure layouts.
- This does not prove exact Stuart-source method identity where no dedicated AirGuide/AirUnit source file is present in the checked source tree.
- This does not add Ghidra tags, recover local variable names, create structure types, or certify every adjacent vtable slot.
- This does not prove runtime AirGuide AI, targeting, ground clearance, flight, particle, or destructor behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Privacy / Release Safety

This note includes repo-relative paths, public addresses, function names, aggregate counts, command summaries, and proof boundaries only. Raw decompile output, screenshots, frame data, copied saves, copied executables, private install paths, and generated JSON remain under ignored `subagents/`.
