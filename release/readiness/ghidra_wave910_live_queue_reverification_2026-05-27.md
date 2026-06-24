# Ghidra Wave910 live queue re-verification (2026-05-27)

Status: read-only Ghidra verification
Date: 2026-05-27
Branch: `main`
Tag: `wave910-live-queue-reverification`

## Scope

Wave910 re-verified the live Ghidra function-quality queue after the WinUI-on-main promotion and Composer/Codex closeout work.

This was a **read-only export/probe** wave:

- no Ghidra renames
- no signature changes
- no comments changed
- no function-boundary changes
- no executable-byte changes
- no game runtime proof

## Commands

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
npm run test:ghidra-static-reaudit-queue
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
```

## Result

The fresh live export reported:

```text
total_functions=6113
commented_functions=6113
```

The queue probe passed:

```text
Status: PASS
Total functions: 6113
Commentless functions: 0
Undefined signatures: 0
Param signatures: 0
Uncertain owner names: 0
Address-suffixed helpers: 0
Address-suffixed wrappers: 0
```

Release/public checks also passed:

```text
R0=4022 R2=0 R3=2 R4=18188
Curated manifest selected files: 3451
```

## Notes

Headless Ghidra emitted known `GhydraMCP` extension manifest warnings. The script completed and exported `subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv` successfully. Treat the manifest warnings as tool-environment noise for this read-only queue export.

## Truth boundary

This re-verifies the **static export-contract queue** for the loaded Steam retail Ghidra project. It does **not** prove runtime gameplay behavior, exact source-layout identity, patch behavior, or rebuild parity.

## Next Wave

The next useful continuation is a full static-reaudit planning pass over all `6113` functions to rank likely correction candidates by evidence risk, not by comment presence. Candidate risk signals include stale owner names, weak evidence comments, broad CRT/source-owner ambiguity, review slices that explicitly deferred exact layout/source identity, and functions with high runtime importance but low static evidence density.
