# Lane 08 Patch Catalog Audit

Scope: patch catalog, binary patch docs, binary patch UI/CLI surfaces, stable vs experimental gating, backup/restore semantics, and wording clarity.

## Findings

1. Medium - The repo documents `patches/catalog/patches.v2.json` as canonical, but the supported patch surfaces still have silent alternate authorities.
- Docs call the catalog canonical at `patches/README.md:27-38`.
- The C# engine silently falls back to duplicated hard-coded specs if the catalog is missing or invalid: `BinaryPatchEngine.cs:35-91`, `BinaryPatchEngine.cs:97-128`.
- The Python core does the same: `onslaught/core/binary_patches.py:15-17`, `onslaught/core/binary_patches.py:35-93`, `onslaught/core/binary_patches.py:147-199`.
- The script CLI is also hard-coded instead of catalog-driven: `patches/patch_display_mode_flow.py:89-156`.
- Impact: catalog packaging/parsing failures and spec drift can stay invisible while docs continue to imply a single source of truth.

2. Medium - Stable-vs-experimental policy is advisory in the GUIs, not enforced.
- The catalog and UI copy say the experimental patch should be used only after stable patches are verified and still prove insufficient: `patches/catalog/patches.v2.json:170-177`, `Views/BinaryPatchesView.xaml:46-54`, `onslaught/gui/tabs/binary_patches.py:104-145`.
- Both GUI selection paths still allow the experimental checkbox to be the only user-visible choice left enabled: `Views/BinaryPatchesView.xaml.cs:66-100`, `Views/BinaryPatchesView.xaml.cs:126-133`, `onslaught/gui/tabs/binary_patches.py:193-221`.
- Impact: the primary app surfaces permit an experimental-only apply path even though the documented track policy says “stable first.”

3. Medium - Restore flows are stricter than the user-facing restore contract and block recovery if `BEA.exe` is missing.
- Docs and UI wording present restore as a backup-based revert flow: `README.MD:65`, `README.RELEASE.md:42`, `Views/BinaryPatchesView.xaml:111-127`.
- WPF restore first rejects a missing target path via `TryGetExePath`: `Views/BinaryPatchesView.xaml.cs:103-114`, `Views/BinaryPatchesView.xaml.cs:221-236`.
- The C# engine itself also requires the target file to exist: `BinaryPatchEngine.cs:373-380`.
- PyQt restore is gated the same way: `onslaught/gui/tabs/binary_patches.py:223-236`, `onslaught/gui/tabs/binary_patches.py:285-294`.
- The script CLI exits before `--restore` if the target exe path does not exist: `patches/patch_display_mode_flow.py:264-269`, `patches/patch_display_mode_flow.py:283-288`.
- By contrast, the Python core restore can recreate the target path from backup: `onslaught/core/binary_patches.py:297-303`.
- Impact: the exact “file missing/damaged” case where users most need restore is blocked on most public surfaces.

4. Low - `Verify Selected` / `Apply Selected` is not literal because hidden watermark patches are auto-added.
- Both GUI surfaces disclose the watermark in prose, but only as a note: `Views/BinaryPatchesView.xaml:52-54`, `onslaught/gui/tabs/binary_patches.py:110-112`.
- The actual selection code injects the two version-overlay specs whenever any patch is selected, including verify flows: `Views/BinaryPatchesView.xaml.cs:92-99`, `onslaught/gui/tabs/binary_patches.py:205-209`.
- The docs also frame the watermark as an auto companion, not a visible checkbox: `patches/README.md:22-25`.
- Impact: reports can include unexpected rows or failures for patches the user never explicitly checked, which weakens wording clarity around “Selected.”

5. Low - Backup wording is inconsistent about whether rollback always returns to the first pre-patch snapshot or to the latest pre-apply state.
- WPF is explicit that the backup is created once: `Views/BinaryPatchesView.xaml:125-127`.
- PyQt omits that qualifier: `onslaught/gui/tabs/binary_patches.py:165-168`.
- Release docs say backups are generated before in-place writes, but do not say the snapshot is reused: `README.RELEASE.md:54-58`.
- The engines and script only create the backup if it does not already exist: `BinaryPatchEngine.cs:345-349`, `onslaught/core/binary_patches.py:278-280`, `patches/patch_display_mode_flow.py:199-204`.
- Impact: users can reasonably read some surfaces as “each apply gives me a fresh rollback point,” while actual restore semantics are “return to the first captured baseline.”

## Residual Test Gaps

- C# regression coverage currently checks apply/restore round-trip, abort-on-mismatch, and track labels, but not catalog-load failure behavior, experimental-only GUI selection, or missing-target restore: `OnslaughtCareerEditor.UiTests/BinaryPatchRegressionTests.cs:39-131`.
- Python regression coverage has the same gap profile: `tests_pyqt/test_binary_patches_unittest.py:29-95`.

## Audit Summary

- The current stable patch set and backup suffix are internally consistent across the catalog, engines, and docs.
- The main issues are policy enforcement and authority/wording clarity rather than bad byte definitions.
- Highest-value fixes would be: surface catalog-load failures, tighten experimental gating in the GUIs, and make restore work when the target exe is absent.
