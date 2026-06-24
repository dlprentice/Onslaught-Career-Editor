# Ghidra Platform / Chunk Reader / Timer Signature Correction - 2026-05-10

Status: public-safe static RE evidence
Scope: saved Ghidra name/signature/comment correction only
Privacy: no raw decompile excerpts, screenshots, runtime logs, copied executables, private game payloads, or private absolute paths are included.

## Summary

Wave 319 revisited the queue head around `0x00423510` through `0x004239f0` plus the related PCPlatform and CDXMemBuffer call targets. Fresh source, decompile, xref, and instruction review showed several saved labels were stale. The serialized headless correction saved `22` signatures/comments and `20` name corrections.

This wave corrects the nearby retail evidence into four bounded clusters:

- `0x00423510`: `CCarverGuide__AcquireNearestTargetReader`
- `0x00423650` through `0x00423720`: `CFrameTimer__ctor`, `CFrameTimer__Start`, and `CFrameTimer__Frame`
- `0x004237d0` through `0x00423990`: `CChunkReader` constructor, destructor-base, open, close, chunk-header read, data read, and skip helpers
- `0x005158f0`, `0x00515950`, and `0x00547d70` through `0x00548c00`: `PCPlatform__DeviceFlip`, `PCPlatform__GetFPS`, and `CDXMemBuffer` constructor/destructor/read-buffer helpers

The pass also refreshed comments/signatures for `CWorld__GetSubstateField_12C` at `0x004239b0` and `CUnitAI__InitDefaults_AutoConfigTestPath` at `0x004239f0`.

## Validation

Headless dry/apply results:

- `ApplyPlatformChunkerTimerSignatureCorrection.java dry`: `updated=0 skipped=22 renamed=0 missing=0 bad=0`
- `ApplyPlatformChunkerTimerSignatureCorrection.java apply`: `updated=22 skipped=0 renamed=20 missing=0 bad=0`
- Ghidra reported `REPORT: Save succeeded` for the apply run.

Read-back and focused checks:

- Metadata read-back: `22/22` targets
- Decompile read-back: `22/22` targets
- Xref read-back: `1075` rows
- Instruction read-back: `1078` rows
- Focused probe: `PASS`, classification `platform-frametimer-chunkreader-signature-correction`
- Queue snapshot after correction: `5876` functions, `705` with comments, `5171` commentless, `2023` undefined signatures, and `2319` `param_N` signatures

Raw machine-readable evidence remains under ignored repo-relative paths such as `subagents/ghidra-static-reaudit/platform-chunker-wave319/current/`.

## Proven

- Saved Ghidra metadata now carries source/decompile/xref-backed names, signatures, and comments for the Platform/CFrameTimer/CChunkReader/CDXMemBuffer correction cluster.
- The generic static re-audit queue no longer lists this `0x00423510` through `0x004239f0` target cluster as commentless high-signal debt.
- The stale labels that treated shared reader/buffer helpers as CChunker, CMeshPart, CResourceAccumulator, or unrelated PCPlatform helpers are superseded by the saved correction.

## Not Proven

- This does not prove runtime timing, display, resource I/O, AI, target-reader, or world behavior.
- This does not prove concrete class layouts, local variable names, tags, rebuild parity, or exhaustive source identity for source-absent bodies.
- This does not launch, patch, or mutate `BEA.exe`.
- This does not change the remaining weapon-fired stealth, cloak activation, packaged runtime, or WinUI release-signing gaps.
