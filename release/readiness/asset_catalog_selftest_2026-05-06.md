# Asset Catalog Self-Test - 2026-05-06

Status: public-safe tooling hardening evidence

Source branch: `wip/sandbox`
Source commit under validation: `319bf0d48d0d16598c8ed7e7329d30f6e566d1ba`
Evidence-report commit: `355498ccbc63aa11260dd3f1eadd6fde685a8a10`

## Purpose

Add a private-asset-free regression check for `tools/export_asset_catalog.py`, which assembles the cross-surface asset catalog from packed AYA refs, loose texture exports, loose mesh exports, embedded mesh exports, video manifests, and language rows.

## Change

- Added `py -3 tools/export_asset_catalog.py --self-test`.
- The self-test builds a temporary synthetic corpus and validates:
  - texture catalog assembly
  - loose mesh catalog assembly
  - embedded mesh catalog assembly
  - video catalog assembly
  - language row catalog assembly
  - summary totals and family counts

## Command

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `py -3 tools/export_asset_catalog.py --self-test` | repo root | PASS | `export_asset_catalog self-test: PASS` | The catalog assembler can join representative synthetic manifest shapes without requiring private game assets. |

## Public-Safe Boundaries

- No local game install access.
- No private extracted asset paths, images, models, media, or raw manifests committed.
- No claim that the self-test replaces full-corpus private extraction or WinUI visual preview evidence.

## Remaining Limits

- Full private corpus extraction, texture decode, FBX export, and WinUI preview proof remain covered by separate evidence waves.
- The self-test guards catalog-shape assembly, not extractor correctness or row-by-row media/model/texture playback/rendering.
