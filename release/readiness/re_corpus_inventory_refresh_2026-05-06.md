# RE Corpus Inventory Refresh - 2026-05-06

Status: public-safe read-only RE evidence

Source branch: `wip/sandbox`
Source commit under validation: `dedcb951fd2f6b222ff438d2c3f82a19dec6d81e`
Evidence-report commit: `91f6e1cbf64eb97b8b08932760578a6e3bd02548`

## Purpose

Refresh read-only corpus inventory evidence against the local Battle Engine Aquila install without mutating the installed game, executable, save files, media, or extracted assets. Raw manifests stay under ignored `subagents/`; this report records only public-safe counts and command outcomes.

## Raw Private Outputs

Raw output files were written under ignored local evidence storage:

```text
subagents/re-corpus-refresh-2026-05-06/
```

These files are not release artifacts and were not committed.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `py -3 tools/aya_archive_inventory.py --resource-root <install>/data/Resources --resolve-assets --json-out <ignored>/aya-inventory.json --asset-manifest-out <ignored>/packed-asset-manifest.json <install>/data/Resources` | repo root | PASS | 301 resource archives scanned. | The resource archive parser can enumerate the current local install read-only and resolve packed asset references against the configured resource root. |
| `py -3 tools/export_video_manifest.py --video-root <install>/data/videos --out-dir <ignored>/video-manifest` | repo root | PASS with correction needed | Produced a zero-row manifest because the local install uses `data/video`, singular. | This proves the command completed, but not video coverage; the path assumption was corrected before recording video evidence. |
| `py -3 tools/export_video_manifest.py --video-root <install>/data/video --out-dir <ignored>/video-manifest-corrected` | repo root | PASS | 66 video files inventoried. | The video manifest tool can enumerate the current local install's Bink video corpus read-only. |

## Resource Archive Findings

- Resource archives scanned: 301.
- Aggregate raw archive bytes parsed: 231,846,299.
- Largest parsed raw archive size: 4,768,222 bytes.
- Top parsed chunk tags by count:
  - `TEXT`: 18,857
  - `MESH`: 3,492
  - `AYAD`: 301
  - `LVLR`: 301
  - `TARG`: 301
  - `GDIE`: 232
  - `ERES`, `IMPS`, `LNDS`, `SSHD`, `SURF`, `WRES`: 66 each
- Packed reference resolution summary:
  - `TEXT` texture refs: 601/601 resolved.
  - Reference mesh refs: 209/209 resolved.
  - `GDIE` texture refs: 206/206 resolved.
  - `GDIE` mesh refs: 42/42 resolved.
  - `GDIE` families: 232 total; 149 texture-only, 45 texture+mesh, 38 metadata-only.

## Video Findings

- Video files inventoried from the corrected `data/video` root: 66.
- Aggregate video bytes: 353,110,648.
- Families:
  - briefing: 28
  - numeric cutscene: 32
  - named root: 6
- Bink magic values: 66/66 reported `BIKi`.
- Numeric cutscene range: 1-33, with cutscene 32 absent from the local corpus.
- Smallest video: 998,708 bytes.
- Largest video: 32,067,000 bytes.

## Public-Safe Boundaries

- No `BEA.exe` launch.
- No original executable mutation.
- No save or options file mutation.
- No private game paths, raw manifests, screenshots, frame captures, asset bytes, or media files committed.
- No rebuild/parity claim.

## Remaining Work

- This is inventory and reference-resolution evidence, not full extraction/render/playback coverage for every row.
- Texture decode, mesh FBX export, language matrix export, and catalog assembly are covered by separate evidence waves and should continue to be refreshed when those pipelines change.
- Recreating the game from scratch remains far beyond this inventory proof; this pass only strengthens corpus accounting.
