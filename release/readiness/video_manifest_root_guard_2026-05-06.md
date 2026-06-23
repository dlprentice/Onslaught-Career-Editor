# Video Manifest Root Guard - 2026-05-06

Status: public-safe tooling hardening evidence

Source branch: `wip/sandbox`
Source commit under validation: `d9934219b8bf00aa6438016846ea8a2842af3956`
Evidence-report commit: `4c6e68167fdd37525f0721b5d77f9895b1a4c22e`

## Purpose

Fix a false-evidence risk found during the read-only RE corpus inventory refresh: `tools/export_video_manifest.py` previously returned success with a zero-row manifest when the caller supplied a missing video root. The local install uses `data/video`, singular, so a mistaken `data/videos` argument could look like a valid empty corpus.

## Change

- `export_video_manifest.py` now fails fast when `--video-root` does not point at an existing directory.
- Added a built-in `--self-test` that exercises the Bink manifest classifier on a temporary synthetic corpus without private game assets.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `py -3 tools/export_video_manifest.py --self-test` | repo root | PASS | `export_video_manifest self-test: PASS` | The parser/classifier still handles synthetic briefing, numeric cutscene, and named-root `.vid` rows. |
| `py -3 tools/export_video_manifest.py --video-root <ignored-missing-root> --out-dir <ignored>` | repo root | EXPECTED FAIL | Exit code 1 and `ERROR: video root does not exist or is not a directory`. | Missing roots no longer produce successful empty manifests. |
| `py -3 tools/export_video_manifest.py --video-root <install>/data/video --out-dir <ignored>` | repo root | PASS | Manifest paths written under ignored `subagents/`. | The hardened tool still inventories the real read-only local video corpus when the correct root exists. |

## Public-Safe Boundaries

- No game executable launch.
- No game install mutation.
- No raw manifest, media file, private path, screenshot, or frame committed.
- No claim of row-by-row playback; this is manifest tooling correctness only.
