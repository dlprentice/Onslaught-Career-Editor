# Ghidra Vector / Math Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra signature/comment evidence

## Objective

Continue the saved-Ghidra static re-audit by hardening a low-risk vector/math helper slice. This tranche targets functions where read-back evidence showed stable calling convention and argument shape, without claiming final class layout, source identity, runtime behavior, or rebuild parity.

## Saved Ghidra Changes

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00401b50` | `CMCMine__ComputeClampedScaleFactor` | Hardened to `double __fastcall CMCMine__ComputeClampedScaleFactor(void * this)`. |
| `0x00401ec0` | `Vec3__SetXYZ` | Hardened from stale no-parameter shape to `void __thiscall Vec3__SetXYZ(void * this, float x, float y, float z)`. |
| `0x00401ee0` | `Vec3__Add` | Hardened from stale extra-parameter shape to `void __thiscall Vec3__Add(void * this, void * outVec, void * rhs)`. |
| `0x00401f10` | `Mat34__SetRows` | Hardened from stale no-parameter shape to `void __thiscall Mat34__SetRows(void * this, void * row0, void * row1, void * row2)`. |
| `0x00401fa0` | `HeightDelta__Below025_D0` | Hardened to `bool __fastcall HeightDelta__Below025_D0(void * this)`. |
| `0x00401fd0` | `HeightDelta__Below015_D4` | Hardened to `bool __fastcall HeightDelta__Below015_D4(void * this)`. |

## Commands

Focused test/probe:

```powershell
py -3 tools\ghidra_vector_math_signature_tranche_probe_test.py
py -3 tools\ghidra_vector_math_signature_tranche_probe.py --check
py -3 -m py_compile tools\ghidra_vector_math_signature_tranche_probe.py tools\ghidra_vector_math_signature_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-vector-math-signature-tranche
```

Serialized Ghidra read-back and mutation:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/signature-debt-tranche5/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche5/current/metadata.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/signature-debt-tranche5/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche5/current/decompile 120
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/signature-debt-tranche5/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche5/current/xrefs.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/signature-debt-tranche5/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche5/current/instructions.tsv 0 80
bash tools/run_ghidra_headless_postscript.sh ApplyVectorMathSignatureTranche.java dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/signature-debt-tranche5/current/comments.tsv dry
bash tools/run_ghidra_headless_postscript.sh ApplyVectorMathSignatureTranche.java apply
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/signature-debt-tranche5/current/comments.tsv apply
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/signature-debt-tranche5/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche5/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/signature-debt-tranche5/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche5/current/decompile_readback 120
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
```

## Result

```text
Ghidra vector/math signature tranche probe
Status: PASS
Targets: 6; hardened: 6; xref rows: 784; instruction rows: 486

Ghidra static re-audit queue probe
Status: PASS
Total functions: 5866
Commentless functions: 5476
Undefined signatures: 2078
Param signatures: 2559
Uncertain owner names: 0
Address-suffixed helpers: 0
Address-suffixed wrappers: 0
```

## Process Notes

- Signature dry/apply ran serially and saved all six target signatures with `updated=0 skipped=6 missing=0 bad=0` in dry mode and `updated=6 skipped=0 missing=0 bad=0` in apply mode.
- The initial comment TSV dry-run used the wrong two-column shape and failed with bad rows before apply; the TSV was corrected to include address, expected name, and comment columns, then dry/apply passed with `applied=0 skipped=6 missing=0 bad=0` and `applied=6 skipped=0 missing=0 bad=0`.

## What This Proves

- The saved vector helper signatures now match the observed stack cleanup and argument shapes for `Vec3__SetXYZ`, `Vec3__Add`, and `Mat34__SetRows`.
- The two height-delta helpers now have boolean return signatures and object-pointer parameters matching the checked field-read/threshold predicate shape.
- `CMCMine__ComputeClampedScaleFactor` now has an explicit object-pointer parameter and double return signature matching the checked FPU clamp path.
- The refreshed queue increased commented functions from `384` to `390`, reduced commentless functions from `5482` to `5476`, and reduced `param_N` signatures from `2563` to `2559`.

## What This Does Not Prove

- This does not prove concrete `Vec3`, `Mat34`, `HeightDelta`, or `CMCMine` structure layouts.
- This does not prove exact Stuart-source identity or rebuild parity.
- This does not add tags, recover local names, or finalize all caller semantics.
- This does not prove runtime behavior, patch or launch `BEA.exe`, or mutate the installed game.
- This does not close broader signature, comment, tag, type, local-name, structure, source-identity, or runtime-proof debt.

## Privacy / Release Safety

This note includes repo-relative paths, public addresses, function names, aggregate counts, command summaries, and proof boundaries only. Raw decompile output, screenshots, frame data, copied saves, copied executables, private install paths, and generated JSON remain under ignored `subagents/`.
