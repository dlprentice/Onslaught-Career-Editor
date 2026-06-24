# Wave217 Comment Pass1 (Headless)

- Date: 2026-02-27
- Script: `tools/ApplyWave217CommentPass1.java`
- Runner: `tools/run_ghidra_headless_postscript.sh`
- Targets: `10` addresses from `addresses.txt`
- Apply status: `REPORT: Save succeeded`
- Verification: decompile exports include inserted function comment blocks for all 10 targets

Notes:
- Comment pass covered high-risk wave216/217 functions after signature hardening.
- Added behavior summaries for targeting, landscape blit, expression eval, fade-state update, and related runtime helpers.
