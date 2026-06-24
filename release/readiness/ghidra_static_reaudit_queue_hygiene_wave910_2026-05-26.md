# Ghidra static re-audit queue hygiene (Wave910) — 2026-05-26

Status: current queue snapshot hygiene (post–Wave900 closure)

## What ran

1. Compared `functions_quality_headless_refresh_20260526.tsv` to `functions_quality.tsv`.
2. Copied refresh → `functions_quality.tsv` (content-equivalent).
3. Ran `py -3 tools/ghidra_static_reaudit_queue_probe.py --check`.

## TSV comparison

| Check | Result |
| --- | --- |
| File size | Both 3,343,999 bytes |
| SHA-256 | `51349C64D644CC7FDED7FF7D89C8648E6906BDA662601ED391E2BAB2BD1DF25E` (identical) |
| Line count | 6114 lines each (header + 6113 functions) |
| Row-wise diff | None (byte-identical before copy) |

The headless refresh export did not change queue truth relative to the morning `functions_quality.tsv`; copy refreshed the canonical filename timestamp only.

## Probe output (2026-05-26)

```text
Ghidra static re-audit queue probe
Status: PASS
Output: subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json
Total functions: 6113
Commentless functions: 0
Undefined signatures: 0
Param signatures: 0
Uncertain owner names: 0
Address-suffixed helpers: 0
Address-suffixed wrappers: 0
```

Exit code: `0`.

## JSON rebuild

`--check` always rewrites `subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json` from the TSV. This run changed the file hash (`generatedAt` and file mtime); aggregate counts and seed weapon/burst rows match the closed **6113/6113** static campaign (no debt buckets).

## References

- Campaign closure: `reverse-engineering/binary-analysis/static-reaudit-campaign.md`
- Wave900 tail: `release/readiness/ghidra_final_static_tail_wave900_2026-05-26.md` (if present)
- Historical queue note (superseded counts): `release/readiness/ghidra_static_reaudit_queue_2026-05-09.md`
