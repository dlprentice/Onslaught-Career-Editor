# Wave217 Signature Hardening Pass2 (Headless)

- Date: 2026-02-27
- Script: `tools/ApplyWave217SignaturePass2.java`
- Runner: `tools/run_ghidra_headless_postscript.sh`
- Targets: `16` addresses from `addresses.txt`
- Apply status: `REPORT: Save succeeded`
- Verification: `decompile/index.tsv` shows `16/16` rows with `status=OK`

Notes:
- This pass normalized high-risk unknown/fastcall method signatures to explicit `__thiscall`/`__cdecl` contracts where behavior evidence supported it.
- Naming coverage unchanged (`5861` total named; weak-name debt already closed).
