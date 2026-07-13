# Ghidra Actor/ComplexThing Signature Tranche - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe saved-Ghidra owner/name/signature/comment evidence

## Objective

Continue the saved-Ghidra static re-audit by correcting a small `CActor` / `CComplexThing` cluster where the current names and signatures were too generic or stale. This tranche treats existing Ghidra names as hypotheses, reparses source-parity and instruction evidence, then saves only bounded corrections with explicit proof boundaries.

## Saved Ghidra Changes

| Address | Saved name | Result |
| --- | --- | --- |
| `0x004011e0` | `CActor__Init` | Promoted from generic vfunc label; signature set to `void __thiscall ... (void * this, void * init)`. |
| `0x004013d0` | `CActor__dtor_base` | Corrected from `ctor_like`; body resets Actor vtable pointers and delegates to the ComplexThing destructor base. |
| `0x004015c0` | `CActor__scalar_deleting_dtor` | Promoted from generic vfunc label; signature set to scalar-deleting destructor shape with `byte flags`. |
| `0x004015e0` | `CActor__Move` | Corrected stale `CUnit__IntegrateVelocityAndResolveGroundCollision` owner/name to source-aligned Actor move behavior. |
| `0x004019b0` | `CActor__TeleportOrientation` | Promoted from generic vfunc label; copies old-orientation storage and delegates to ComplexThing orientation setter. |
| `0x004019e0` | `CActor__HandleEvent` | Promoted from generic vfunc label; handles Actor move events `3000` and `0xbb9`. |
| `0x004f3ee0` | `CComplexThing__scalar_deleting_dtor` | Promoted from generic vfunc label; signature set to scalar-deleting destructor shape with `byte flags`. |
| `0x004f3f00` | `CComplexThing__dtor_base` | Corrected from `ctor_like`; body tears down script/animation/motion/mapwho/monitor-owned state. |
| `0x004f3fd0` | `CComplexThing__Init` | Promoted from generic vfunc label; signature set to source-aligned init shape. |
| `0x004f4300` | `CComplexThing__HandleEvent` | Promoted from generic vfunc label; handles shutdown/init-script/ready-script events. |
| `0x004f4460` | `CComplexThing__TeleportOrientation` | Promoted from generic vfunc label; copies 12 dwords into current orientation storage. |

## Commands

Focused test/probe:

```powershell
py -3 tools\ghidra_actor_complex_signature_tranche_probe_test.py
py -3 tools\ghidra_actor_complex_signature_tranche_probe.py --check
py -3 -m py_compile tools\ghidra_actor_complex_signature_tranche_probe.py tools\ghidra_actor_complex_signature_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-actor-complex-signature-tranche
```

Serialized Ghidra mutation/read-back:

```powershell
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\signature-debt-tranche7\current\rename_map_actor_complex.txt
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/signature-debt-tranche7/current/rename_map_actor_complex.txt dry
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/signature-debt-tranche7/current/rename_map_actor_complex.txt apply
bash tools/run_ghidra_headless_postscript.sh ApplyActorComplexSignatureTranche.java dry
bash tools/run_ghidra_headless_postscript.sh ApplyActorComplexSignatureTranche.java apply
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/signature-debt-tranche7/current/comments.tsv dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/signature-debt-tranche7/current/comments.tsv apply
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/signature-debt-tranche7/current/readback_addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche7/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/signature-debt-tranche7/current/readback_addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche7/current/decompile_readback 180
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/signature-debt-tranche7/current/readback_addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche7/current/xrefs_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/signature-debt-tranche7/current/readback_addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche7/current/instructions_readback.tsv 0 320
```

## Result

```text
Actor/ComplexThing signature tranche: PASS
Targets: 11
Renamed targets: 11
Signature-hardened targets: 11
Comment overclaims: 0
Xref rows: 137
Instruction rows: 3531

Ghidra static re-audit queue probe: PASS
Total functions: 5866
Commentless functions: 5459
Undefined signatures: 2078
Param signatures: 2542
Uncertain owner names: 0
Address-suffixed helpers: 0
Address-suffixed wrappers: 0
```

## Process Notes

- Rename-map preflight accepted `11` rows with `0` findings.
- Rename dry/apply ran serially and saved all `11` target names with `applied=0 skipped=11 missing=0 bad=0` in dry mode and `applied=11 skipped=0 missing=0 bad=0` in apply mode.
- Signature dry/apply ran serially and saved all `11` target signatures with `updated=0 skipped=11 missing=0 bad=0` in dry mode and `updated=11 skipped=0 missing=0 bad=0` in apply mode.
- Comment dry/apply ran serially and saved `11` proof-boundary comments with `applied=0 skipped=11 missing=0 bad=0` in dry mode and `applied=11 skipped=0 missing=0 bad=0` in apply mode.
- The follow-up queue snapshot increased commented functions from `396` to `407`, reduced commentless functions from `5470` to `5459`, and reduced `param_N` signatures from `2553` to `2542`.

## What This Proves

- The old `0x004015e0` `CUnit__IntegrateVelocityAndResolveGroundCollision` label was too narrow for the checked body; saved Ghidra now records it as `CActor__Move` with a source-aligned no-arg object-pointer signature.
- The `CActor` init, move, handle-event, orientation, destructor-base, and scalar-deleting destructor cluster now has saved names, signatures, and comments backed by source-parity, decompile, xref, and instruction read-back.
- The directly delegated `CComplexThing` init, handle-event, orientation, destructor-base, and scalar-deleting destructor functions now have saved base-class names, signatures, and comments.
- The saved comments explicitly preserve the difference between static/source-parity evidence and runtime behavior.

## What This Does Not Prove

- This does not prove concrete `CActor`, `CComplexThing`, `CInitThing`, `CEvent`, or `FMatrix` structure layouts.
- This does not prove runtime movement, scheduler, script, destruction, allocation, or orientation behavior.
- This does not add Ghidra tags, recover local variable names, or finalize every adjacent Actor/ComplexThing vtable slot.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.
- This does not close broader signature, comment, tag, type, local-name, structure, exact source-identity, or runtime-proof debt.

## Privacy / Release Safety

This note includes repo-relative paths, public addresses, function names, aggregate counts, command summaries, and proof boundaries only. Raw decompile output, screenshots, frame data, copied saves, copied executables, private install paths, and generated JSON remain under ignored `subagents/`.
