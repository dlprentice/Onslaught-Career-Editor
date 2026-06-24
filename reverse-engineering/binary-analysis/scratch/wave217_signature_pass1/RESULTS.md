# Wave217 Signature Hardening Pass1 (Headless)

- Date: 2026-02-27
- Script: `tools/ApplyWave217SignaturePass1.java`
- Runner: `tools/run_ghidra_headless_postscript.sh`
- Targets: `18` addresses from `addresses.txt`
- Apply status: `REPORT: Save succeeded`
- Verification: `decompile/index.tsv` shows `18/18` rows with `status=OK`

Notes:
- This pass normalized calling conventions, return types, and parameter names for high-risk wave216/217 semantic renames.
- Naming coverage is unchanged (`5861` total named; weak-name debt already closed).
