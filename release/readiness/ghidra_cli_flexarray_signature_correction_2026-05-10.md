# Ghidra CLIParams / FlexArray Signature Correction - 2026-05-10

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0044b290` → `CFlexArray__Free_thunk` (was `CFlexArray__Free`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe static RE evidence
Scope: saved Ghidra signature/comment correction only
Privacy: no raw decompile excerpts, screenshots, runtime logs, copied executables, private game payloads, or private absolute paths are included.

## Summary

Wave 320 revisited the next static re-audit queue slice after the Platform/CFrameTimer/ChunkReader correction. Fresh Ghidra metadata, decompile, xref, and instruction read-back covered `CLIParams__ParseCommandLine` plus the pointer-sized `CFlexArray` helper family.

The serialized headless correction saved `10` non-undefined signatures/comments and made `0` renames:

- `0x00423bc0`: `CLIParams__ParseCommandLine`
- `0x004241a0`, `0x004241e0`, `0x004241f0`, `0x00424260`, and `0x00424360`: `CFlexArray` init-with-growth, clear, add, insert, and remove-range helpers
- `0x00465530`, `0x00465570`, and `0x00465580`: `CFlexArray` init, free, and resize helpers
- `0x0044b290`: `CFlexArray__Free_thunk`

## Validation

Headless dry/apply results:

- `ApplyCliFlexArraySignatureCorrection.java dry`: `updated=0 skipped=10 renamed=0 missing=0 bad=0`
- `ApplyCliFlexArraySignatureCorrection.java apply`: `updated=10 skipped=0 renamed=0 missing=0 bad=0`
- Ghidra reported `REPORT: Save succeeded` for the apply run.

Read-back and focused checks:

- Metadata read-back: `10/10` targets
- Decompile read-back: `10/10` targets
- Xref read-back: `28` rows
- Instruction read-back: `890` rows
- Focused probe: `PASS`, classification `ghidra-cli-flexarray-signature-correction.v1`
- Queue snapshot after correction: `5876` functions, `715` with comments, `5161` commentless, `2013` undefined signatures, and `2319` `param_N` signatures
- Ghidra project backup: copied `BEA.gpr` and `BEA.rep` to an out-of-repo local `[maintainer-local-backup-volume]` drive backup folder, with matching `18` repository files, `151391111` bytes, and matching `.gpr` SHA-256

Raw machine-readable evidence remains under ignored repo-relative paths such as `subagents/ghidra-static-reaudit/cli-flexarray-wave320/current/`.

## Proven

- Saved Ghidra metadata now carries non-undefined signatures and bounded comments for the CLI command-line parser and pointer-sized `CFlexArray` helper family.
- `CLIParams__ParseCommandLine` takes a command-line string, tokenizes it into local `0x100`-byte slots, and scans the observed retail flag branches, including the guarded `-forcewindowed` path.
- The `CFlexArray` helpers operate on a 4-dword dynamic array layout with data pointer, capacity, count, and growth fields, and store 4-byte element slots.
- The generic static re-audit queue no longer lists this CLI/FlexArray slice as commentless or undefined-signature debt.

## Not Proven

- This does not prove every retail command-line flag works at runtime.
- This does not prove every `CFlexArray` call-site element type or owner.
- This does not prove source-to-retail identity for source bodies absent from the current Stuart source snapshot.
- This does not prove concrete layouts beyond the observed field offsets, local variable names, tags, runtime behavior, or rebuild parity.
- This does not launch, patch, or mutate `BEA.exe`.
