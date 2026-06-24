# Wave217 Signature Hardening Pass4 (Headless)

- Date: 2026-02-27
- Script: `tools/ApplyWave217SignaturePass4.java`
- Runner: `tools/run_ghidra_headless_postscript.sh`
- Targets: `11` addresses from `addresses.txt`
- Apply status: `REPORT: Save succeeded`
- Verification: `decompile/index.tsv` shows `11/11` rows with `status=OK`
- Residual check: all wave216/217 addresses now have `0` signatures containing `param_*`

Notes:
- This pass closed the remaining wave216/217 generic-parameter signature debt.
- Naming coverage unchanged (`5861` total named; weak-name debt already closed).
