# Ghidra Rename Map Preflight

Status: public-safe reverse-engineering tooling evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `c27dbbe5`
Evidence-report commit: cd9efd3d0db86a823300e7e4c4c7244641c72d2f

## Purpose

This pass adds local read-only validation for Ghidra batch rename maps before a map reaches headless Ghidra dry/apply workflows. It closes the known formatting footgun where a malformed three-column row could be interpreted as a bad target name.

No Ghidra project was opened, no Ghidra mutation occurred, no game runtime was launched, and no executable or installed-game file was read or changed.

## Commands

```powershell
npm run test:ghidra-rename-map-preflight
```

Result: PASS.

Important output summary:

```text
Ghidra rename map preflight self-test: PASS
```

Malformed-row guard smoke:

```powershell
py -3 tools\ghidra_rename_map_preflight.py <bad three-column map>
```

Result: expected nonzero rejection.

Important output summary:

```text
Ghidra rename map preflight
Rows accepted: 0
Findings: 1
- line 1: BAD_COLUMN_COUNT: rename map rows must be exactly two columns: <address> <new_name>
bad map rejected as expected
```

## What Changed

- `tools/ghidra_rename_map_preflight.py` validates local rename maps without launching Ghidra.
- The preflight rejects rows that are not exactly two columns.
- The preflight validates hex addresses, single-token target names, duplicate addresses, duplicate names, and weak `FUN_` / `__Unk_` target prefixes.
- `tools/run_ghidra_batch_rename_headless.sh` now runs the preflight before invoking Ghidra.
- `tools/GhidraBatchRename.java` now parses exact two-column rows and records malformed non-comment rows as `BADROW` instead of silently accepting trailing text as part of the target name.

## What This Proves

- The repo now has a repeatable local guard for rename-map formatting before dry/apply workflows.
- A representative malformed three-column row is rejected before Ghidra mutation tooling can run.
- The headless wrapper and Java postscript are aligned with the repo rule that map rows must be exactly `<address> <new_name>`.

## What This Does Not Prove

- A live Ghidra headless dry run.
- A live Ghidra apply run.
- Ghidra project read-back after mutation.
- Java-side symbol-name validity beyond the local token policy.
- Any Battle Engine runtime behavior.

## Privacy / Release Safety

This evidence is public-safe. It does not include private paths, binaries, Ghidra project data, source excerpts, screenshots, runtime captures, or mutation logs.

## Recommended Next Step

For a later mutation-enabled Ghidra pass, run the local preflight first, then headless dry mode, then apply only after a clean dry artifact, save success, no lock errors, no `MISSING` / `BADADDR` / `BADROW` / `FAIL`, and immediate read-back of the changed names.
