# Lane 06 - Binary Patch Gap Findings

Date: 2026-03-04
Owner lane: `subagents/depth2/lane06_binary_patch_gap_findings.md`

## Scope audited

- Binary patch infrastructure (script/core/UI/test surfaces).
- Documentation alignment for:
  - stable vs experimental tracks,
  - `cardid` / extra-graphics gate,
  - startup/windowed/resolution behavior.
- Candidate patch opportunities with confidence and blockers.

## Evidence snapshot (current implementation reality)

- Active display/windowing patch lane is 3 offsets only (`0x129696`, `0x12A644`, `0x12BB97`) in script, Python core, WPF UI, and PyQt UI.
  - `patches/README.md:27-49`
  - `patches/patch_display_mode_flow.py:60-81`
  - `onslaught/core/binary_patches.py:32-55`
  - `Views/BinaryPatchesView.xaml.cs:34-54`
  - `onslaught/gui/tabs/binary_patches.py:76-101`
- Dev-mode goodies patch is separate and script-only (`0x5D819`), documented as advanced/dev-mode-only.
  - `patches/README.md:51-73`
  - `patches/patch_devmode_goodies_logic_fix.py:1-31`
- Current capability docs describe only display/windowing + dev-mode goodies patch lanes (no cardid/extra-graphics patch lane).
  - `CURRENT_CAPABILITIES.md:45-48`
- RE docs include a fully mapped 28-region widescreen diff, but that track is not exposed in active patch tooling.
  - `reverse-engineering/binary-analysis/widescreen-patch-analysis.md:7-23`
  - `reverse-engineering/binary-analysis/widescreen-patch-analysis.md:47-91`
  - `reverse-engineering/binary-analysis/widescreen-diff-regions-28.tsv:1`

## Byte reality check (repo binaries, 2026-03-04)

Observed with `xxd` on repo binaries:

| File | Offset | Observed bytes | Meaning against active patch specs |
|---|---:|---|---|
| `game/BEA.exe` | `0x129696` | `CC` | Resolution gate patch not applied. |
| `game/BEA.exe` | `0x12A644` | `A1 F0 2D 66 00` | Force-windowed patch not applied. |
| `game/BEA.exe` | `0x12BB97` | `75 20` | Optional skip-auto-toggle patch not applied. |
| `game/BEA.exe` | `0x262F3E` | `01` | `-forcewindowed` guard currently enabled in this binary. |
| `BEA_Widescreen.exe` | `0x129696` | `00` | Region 3 applied (non-4:3 reject neutralized). |
| `BEA_Widescreen.exe` | `0x12A644` | `A1 F0 2D 66 00` | Active windowed-startup patch 2 is not part of this widescreen binary. |
| `BEA_Widescreen.exe` | `0x12BB97` | `75 20` | Active optional patch 3 is not part of this widescreen binary. |
| `BEA_Widescreen.exe` | `0x262F3E` | `01` | Guard enabled here too. |

## Gaps vs requested scope

### 1) Stable vs experimental tracks are not explicit in tooling

- Planning doc has a clear 2-track model (Track A internal patching vs Track B wrappers), but active patch tooling does not represent this model.
  - `reverse-engineering/binary-analysis/display-modernization-plan.md:10-37`
- UI and script present one flat display patch set with one optional checkbox/flag; no "stable"/"experimental" grouping or guardrails.
  - `Views/BinaryPatchesView.xaml:44-77`
  - `onslaught/gui/tabs/binary_patches.py:67-101`
  - `patches/patch_display_mode_flow.py:84-99`
- Docs use mixed labels (`Supported`, `DEV MODE ONLY`, `Archived`) but not a canonical stable/experimental taxonomy.
  - `patches/README.md:27-76`

Gap: requested track model exists in planning but is not encoded in executable patch UX or ops docs.

### 2) cardid / extra-graphics gate is doc-heavy, tooling-light

- `cardid.txt` and tweak keys (`GEFORCE_FX_POWER`, `SRT_ENABLE`, `IMPOSTOR_ENABLE`, `LANDSCAPE_LIGHTING`) are documented as manual edits only.
  - `reverse-engineering/game-assets/modding-reference.md:42-127`
- CLI docs list `-cardid`, but effect is still untested and no patch lane is attached.
  - `reverse-engineering/binary-analysis/functions/CLIParams.cpp/_index.md:33`
  - `reverse-engineering/binary-analysis/functions/CLIParams.cpp/_index.md:75-82`
- No active patch specs (WPF/PyQt/Python-core/script) target cardid/graphics gates.
  - `onslaught/core/binary_patches.py:32-55`
  - `patches/patch_display_mode_flow.py:60-81`

Gap: requested cardid/extra-graphics scope has no integrated patch track (binary or companion flow), only manual doc guidance.

### 3) startup/windowed/resolution lane is useful but still partial

- Active patch set explicitly acknowledges optional patch 3 is partial and environment-dependent.
  - `Views/BinaryPatchesView.xaml:75-77`
  - `patches/patch_display_mode_flow.py:20-25`
- RE docs confirm startup behavior is multi-gate and may still need wrappers.
  - `reverse-engineering/binary-analysis/windowed-mode-analysis.md:20`
  - `reverse-engineering/binary-analysis/windowed-mode-analysis.md:80-97`
- Wider widescreen internals (code-cave path + FOV/aspect hooks) are mapped but not surfaced in active tooling.
  - `reverse-engineering/binary-analysis/widescreen-patch-analysis.md:52-91`

Gap: current startup/windowed/resolution implementation is a minimal subset, not a full track with explicit phase boundary.

### 4) Doc drift on guard-default narrative creates operator ambiguity

- One canonical doc states current hash has guard `0x01` and historical variants may be `0x00`.
  - `reverse-engineering/binary-analysis/windowed-mode-analysis.md:11`
- CLI function index still says "Retail default is 0x00" while also noting current repo binaries are `0x01`.
  - `reverse-engineering/binary-analysis/functions/CLIParams.cpp/_index.md:47`

Gap: startup/windowed guidance has contradictory default framing across docs.

### 5) Verification/testing depth is uneven across stacks

- Python has focused unit tests for core apply/restore and mismatch abort.
  - `tests_pyqt/test_binary_patches_unittest.py:22-79`
- WPF automation currently checks tab presence only; no patch verify/apply/restore behavior coverage.
  - `OnslaughtCareerEditor.UiTests/SmokeTests.cs:67-77`
- No test coverage for script CLI modes (`--resolution-only`, `--windowed-only`, `--skip-auto-toggle`) or hash-profile gating.
  - `patches/patch_display_mode_flow.py:182-233`

Gap: stable-track confidence currently leans on byte checks + manual testing, not complete automated cross-stack behavior tests.

## Candidate patch opportunities

| Candidate | Track fit | Confidence | Why this is a candidate | Primary blockers |
|---|---|---|---|---|
| Add `-forcewindowed` guard-normalization patch (`0x262F3E: 00->01`) as a **separate compatibility patch** in active UI/core/script | Stable | High | Already documented and low-risk single-byte normalization for variant binaries. Evidence exists in windowed docs and current bytes. | In canonical repo binaries this is already `01`, so value is variant support only; requires clean variant messaging and no-op handling. |
| Introduce **profiled hash manifests** (canonical hash + known variants) and make patch operations profile-aware | Stable | High | Docs already define canonical SHA256; active tooling currently validates only selected offsets, not full target profile. | Need governance for variant list and explicit override path for unknown-but-safe binaries. |
| Promote current 3-patch display lane as explicit **Stable Track A-minimal** with one-click preset + documented rollback | Stable | High | Infrastructure already exists across WPF/PyQt/script/core; mostly classification/UX hardening. | Requires doc + UI wording alignment and expected-behavior matrix signoff. |
| Add **experimental widescreen code-cave track** from the 28-region map (`widescreen-diff-regions-28.tsv`) | Experimental | Medium | Region map is complete with high-confidence classifications; can be implemented as deterministic byte-set apply/verify/restore. | High regression risk (FOV/UI/render path), larger QA surface, binary artifact governance, and interaction with stable patches must be defined. |
| Extend startup flow patching beyond `0x12BB97` by mapping additional fullscreen re-entry gates in `ToggleFullscreen/ForceWindowed/Resize3DEnvironment` | Experimental | Medium | RE function ownership for these paths is known; current docs call existing optional gate partial. | Missing byte-level target list and safety proof for additional sites; requires focused RE + runtime validation. |
| Add patch option to force `ALLOW_WIDESCREEN_MODES` default-on behavior in binary (instead of relying on config/manual edits) | Experimental | Low-Medium | CVar globals and string key are identified; could reduce config friction. | Initializer/write-site offsets and side effects are not documented in current patch manifests; risk of options drift. |
| Add patch lane for `cardid`/extra-graphics gate bypass (defaulting high-quality toggles) | Experimental | Low | Requested scope explicitly calls this out; docs identify relevant tweak family and CLI switch. | No mapped retail decision points/byte targets for these gates; current evidence is conceptual/manual only. |
| Add **companion non-binary lane**: managed `cardid.txt` preset generator/merger with backup/restore | Stable companion (not exe patch) | High | Directly addresses the `cardid`/extra-graphics problem with concrete existing syntax and known tweak keys. | Needs merge safety rules (vendor/device block insertion), conflict handling, and UX placement next to binary patches. |

## Recommended next sequencing (if this lane is actioned)

1. Canonicalize track taxonomy first (Stable vs Experimental labels in docs/UI/script help) and resolve guard-default drift.
2. Implement low-risk stable additions first: profile/hash manifests and optional guard-normalization compatibility patch.
3. Treat widescreen code-cave and cardid-gate bypass as explicit experimental waves with test matrix + rollback criteria.
4. In parallel, consider the non-binary `cardid.txt` companion lane to cover extra-graphics scope quickly without risky exe surgery.
