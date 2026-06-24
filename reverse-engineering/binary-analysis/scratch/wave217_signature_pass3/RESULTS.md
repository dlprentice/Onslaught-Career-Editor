# Wave217 Signature Hardening Pass3 (Headless)

- Date: 2026-02-27
- Script: `tools/ApplyWave217SignaturePass3.java`
- Runner: `tools/run_ghidra_headless_postscript.sh`
- Targets: `20` addresses from `addresses.txt`
- Apply status: `REPORT: Save succeeded`
- Verification: `decompile/index.tsv` shows `20/20` rows with `status=OK`

Notes:
- This pass focused on parameter-name normalization and calling-convention cleanup for remaining wave216/217 methods that still had generic `param_*` names.
- Naming coverage unchanged (`5861` total named; weak-name debt already closed).
