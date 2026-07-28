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

### 2026-07-27 — the installed executable is patched ON PURPOSE

**This is not drift and it is not a problem to be escalated. The maintainer
patches his own retail install deliberately, because it is easier for him to test
with, and keeps the pristine original beside it as
`BEA.exe.original.backup` in the same Steam folder. Do not raise it again.**

What *is* a problem is that
`retail-specimen-manifest-2026-03-14.json` still records
`installed_live_exe_matches_clean_repo: true`. That is stale. The manifest is a
dated snapshot, so it is left as history rather than rewritten, and the standing
state is recorded here instead.

Measured today:

- installed live `BEA.exe`: `e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`
- pristine specimen: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
  (`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, and identically
  `local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`)

Same size, **28 bytes differ across exactly four sites**, and all four are this
repository's own catalogued patches:

| File offset | Change | Catalogue entry |
|---|---|---|
| `0x06416F` | pushed string pointer `0x00629454` → `0x005AA444` | `BinaryPatchEngine.cs:162` version-overlay marker pointer |
| `0x129696` | `jne` rel32 displacement `0xCC` → `0x00` | `BinaryPatchEngine.cs:114` aspect/4:3 reject gate |
| `0x12A644` | `a1 f0 2d 66 00` → `b8 01 00 00 00` (`mov eax,[0x662df0]` → `mov eax,1`) | `BinaryPatchEngine.cs:127` `force_windowed` |
| `0x1AA444` | 20 bytes of `cc` padding → `"V%1d.%02d - PATCHED\0"` | `BinaryPatchEngine.cs:177` version-overlay cave payload |

**Scope of the damage to existing findings: none identified, and the reason is
specific rather than reassuring.** 2,506,724 of 2,506,752 bytes are identical, so
a byte finding is only at risk if its bounded scan overlapped one of those four
sites — and those sites *are* the patches, which no analysis pass has targeted.
The exposure is prospective, not retrospective: any future scan run against the
Steam path reads a different binary from the one the Ghidra project was imported
from.

**The capture lane is unaffected and was already doing the right thing.**
`Capture-Retail.ps1` targets `local-lab/safe-copy-bea-pristine`, which carries
`force_windowed` **only** — 4 bytes at `0x12A644`, verified — and deliberately
leaves the version overlay and the 4:3 gate pristine so nothing cosmetic leaks
into a reference capture. The two are different builds and must not be confused:
copied capture target `e1436ef7…`, installed live `e7881829…`.

**Standing consequence.** Every byte finding must state the specimen file and its
hash, not just an address. "Read from the binary" is ambiguous on this
workstation and has been since at least 2026-03-14.

> ### 2026-07-28 — the trap this rule is meant to stop, and it has already been sprung
>
> **`e1436ef7…` is not pristine. Do not call it pristine.** It is the *capture
> target*: pristine plus `force_windowed` and nothing else. The pristine
> specimen is `BEA.exe.original.backup`, `74154bfa…`. The directory
> `local-lab/safe-copy-bea-pristine/` is named after its purpose, not its
> contents, and the file named `BEA.exe` inside it is the **patched** one — the
> names are inverted, as
> [`retail-capture-provenance-2026-07-25.md`](retail-capture-provenance-2026-07-25.md)
> recorded and did not fix.
>
> On 2026-07-28, **nine** tracked notes were found attaching the word "pristine"
> to `e1436ef7…` in a `Specimen:` header or in the body sentence "linear decode
> of the pristine file": the seven `2026-07-26` terrain and cockpit notes, plus
> `cockpit-world-matrix-static-2026-07-26.md` (which also carried **no hash at
> all**) and one body sentence in
> `terrain-gain-frame-global-falsified-2026-07-26.md`. All nine were corrected in
> place. **No conclusion changed** — the two builds differ at exactly four bytes,
> `0x12a644`–`0x12a647` = VA `0x0052a644`–`0x0052a647`, and no address cited in
> any of the nine falls in that range.
>
> Three sentences make a `Specimen:` line safe, and all three are required:
>
> 1. **Name the file, not the directory.** `BEA.exe.original.backup` and
>    `BEA.exe` live side by side.
> 2. **Carry the hash**, and check which of `74154bfa…` / `e1436ef7…` /
>    `e7881829…` it is before writing an adjective.
> 3. **Say which role it plays** — pristine, capture target, or the deliberately
>    patched Steam install — because "safe copy" does not distinguish them.
>
> This is now gated for new documents: [`DOCUMENTATION.md`](../../DOCUMENTATION.md)
> makes `Specimen:` mandatory on any finding quoting a retail address, and
> `tools/doc_header_check.py` enforces it. The checker validates **shape, not
> truth** — it cannot tell `e1436ef7` from `74154bfa`. That check is still a
> reader's job, which is why the three rules above are written out here.

Restoring the install is a mutation of an installed game directory and is
therefore separately authorized; the pristine bytes are held in two places above,
so it is reversible whenever the user wants it done.

## Operational Rule

Before any serious runtime-validation wave:

1. regenerate or re-check the specimen manifest,
2. note whether `installed_live_bea_exe` matches `clean_repo_bea_exe`,
3. record the exact specimen keys used by the probe session,
4. write resulting notes/logs under ignored `.artifacts/` with a date- and task-scoped filename.
