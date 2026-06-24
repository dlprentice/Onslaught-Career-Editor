# Retail Specimen Baseline

> Canonical runtime/provenance specimen set for the Steam retail build
> Date: 2026-03-14

## Purpose

This file pins the exact files that future runtime probes should trust first.

It exists to solve two problems:

1. make the retail executable and supporting corpus hash-locked instead of implied,
2. keep runtime/debug sessions tied to a known specimen set instead of ad-hoc local files.

## Canonical Manifest

The current machine-generated manifest is:

- [retail-specimen-manifest-2026-03-14.json](/reverse-engineering/binary-analysis/retail-specimen-manifest-2026-03-14.json)

Regenerate it with:

```powershell
py -3 tools\hash_retail_specimens.py
```

## Baseline Targets

The pinned set currently includes:

| Key | Purpose |
|-----|---------|
| `installed_live_bea_exe` | Installed executable actually used by local runtime sessions |
| `clean_repo_bea_exe` | Clean repo mirror of the retail Steam executable |
| `repo_defaultoptions_bea` | Repo mirror of the boot/global options snapshot |
| `gold_save_haha_cannon` | Gold save baseline used by app/manual regression work |
| `base_res_pc_aya` | Core packed resource archive |
| `level_852_res_pc_aya` | Representative hidden/multiplayer-family resource archive |
| `mesh_m_be_trans_aya` | Representative loose mesh payload |
| `english_dat` | Representative localization table |
| `video_01_vid` | Representative Bink cutscene payload |

## Current Baseline Conclusions

- The clean retail authority is the repo mirror, not the installed executable.
- The installed executable is still important because it is the actual runtime specimen, but it may drift if local patches are applied.
- `defaultoptions.bea` and the gold `.bes` baseline are pinned separately because they serve different roles:
  - `defaultoptions.bea` is the boot/global settings specimen,
  - `haha-cannon-goes-brrrrr.bes` is the career/save regression specimen.
- Representative assets are included so runtime and extraction work can reference known-good payloads across archive, mesh, localization, and video surfaces.

### 2026-03-14 Finding

During this pass, the installed executable was temporarily on a patched local variant and did not match the clean repo mirror.

After the user restored the installed copy, the live install and the clean repo retail baseline match again:

- installed live `BEA.exe`: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- clean repo `BEA.exe`: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

So the current workstation state is back to a clean retail runtime specimen.

## Operational Rule

Before any serious runtime-validation wave:

1. regenerate or re-check the specimen manifest,
2. note whether `installed_live_bea_exe` matches `clean_repo_bea_exe`,
3. record the exact specimen keys used by the probe session,
4. write resulting notes/logs under `subagents/` with a date- and task-scoped filename.
