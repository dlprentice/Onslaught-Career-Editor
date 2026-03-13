# Binary Analysis - Navigation Index

> Ghidra reverse engineering documentation for BEA.exe (Battle Engine Aquila)

## Functions Documentation

| Document | Description |
|----------|-------------|
| [functions/_index.md](functions/_index.md) | **Master index** - per-source-file mappings (see current corpus counts in `FUNCTION_COVERAGE_STATE.md`) |
| [functions/FUNCTION_COVERAGE_STATE.md](functions/FUNCTION_COVERAGE_STATE.md) | **Master coverage state** - binary-wide `% mapped`, remaining `FUN_`, and corpus counters |
| [GHIDRA-REFERENCE.md](GHIDRA-REFERENCE.md) | Ghidra workspace reference, project notes |

The functions folder contains per-source-file documentation organized by original Lost Toys source file names (Career.cpp, Unit.cpp, etc.). Each source file has an index with function addresses, parameters, and cross-references.

## Analysis Documents

| Document | Description |
|----------|-------------|
| [windowed-mode-analysis.md](windowed-mode-analysis.md) | Investigation of `-forcewindowed` parser/startup-flow gating behavior across Steam baselines |
| [widescreen-patch-analysis.md](widescreen-patch-analysis.md) | Reverse engineering of community widescreen patch, FOV and resolution hacks |
| [widescreen-diff-regions-28.tsv](widescreen-diff-regions-28.tsv) | Canonical machine-readable map of all 28 `BEA.exe` vs `BEA_Widescreen.exe` binary diff regions |
| [widescreen-diff-unresolved.md](widescreen-diff-unresolved.md) | Canonical unresolved-region queue for widescreen diff attribution (bounded unknown set) |
| [widescreen-regions-8-11-validation.md](widescreen-regions-8-11-validation.md) | Deep validation evidence for the former unknown 8-11 hook cluster (now closed) |
| [capture-menu-behavior.md](capture-menu-behavior.md) | File/Capture menu behavior mapping (DX8 sample framework commands and AVI capture path evidence) |
| [deep-validation-status.md](deep-validation-status.md) | Static RE gate tracker for ownership/type/behavior contract completion by subsystem |
| [high-impact-subsystem-contracts.md](high-impact-subsystem-contracts.md) | Phase-5 pass-2 contract sheet for remaining high-impact subsystems |
| [high-impact-call-chain-appendix.md](high-impact-call-chain-appendix.md) | Phase-5 call-chain depth appendix for frontend/world/text side effects and signature verification snapshot |
| [display-modernization-plan.md](display-modernization-plan.md) | Post-validation modernization decision matrix and test-matrix plan (no implementation) |
| [executable-analysis.md](executable-analysis.md) | BEA.exe PE metadata, file hashes, DLL dependencies, embedded strings |
| [extra-graphics-feature-gate-patch.md](extra-graphics-feature-gate-patch.md) | Retail extra-graphics unlock patch evidence (`0x0CDD40: 6A 00 -> 6A 01`) |
| [version-overlay-patch.md](version-overlay-patch.md) | Companion patch note for the shipped `V1.00 - PATCHED` watermark behavior |

## Reference Files

| Document | Description |
|----------|-------------|
| [functions/display-settings.md](functions/display-settings.md) | Screen mode handling, resolution settings, CD3DApplication class |
| [functions/string-locations-index.md](functions/string-locations-index.md) | Historical 196-address debug-path snapshot used during early function discovery (see file header notes) |
| [functions/globals.md](functions/globals.md) | Global variables - g_bDevModeEnabled, cheat table, singletons |

## Quick Stats

- For canonical live coverage metrics (total function objects, strong semantic coverage, helper-placeholder residuals), use:
  - [`functions/FUNCTION_COVERAGE_STATE.md`](functions/FUNCTION_COVERAGE_STATE.md)
- This index intentionally avoids embedding fast-changing totals to reduce stale duplication.

## Tools

Analysis performed using:
- **Ghidra 12.0.3** - Primary disassembler/decompiler
- **GhydraMCP** - MCP-assisted bridge for scripted Ghidra analysis (active endpoint values are workstation-specific)

Release note:
- Internal mutation/runbook notes are maintained privately and are not required for public app/docs use.
- Operational mutation journals and audit byproducts are intentionally kept out of reader-facing navigation and the public release tree.

## See Also

- [README.md](README.md) - Detailed overview with verified binary hashes
- [../source-code/](../source-code/) - Stuart's source code analysis
- [../save-file/](../save-file/) - .BES save file format documentation

---

*Index refreshed: 2026-03-01.*
