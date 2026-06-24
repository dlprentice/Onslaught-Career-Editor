# Lane 05 Binary Patch Alignment Audit (Read-Only)

## Scope
- `BinaryPatchEngine.cs`
- `Views/BinaryPatchesView.xaml.cs`
- `patches/README.md`
- `patches/patch_display_mode_flow.py`
- `reverse-engineering/binary-analysis/windowed-mode-analysis.md`
- `reverse-engineering/binary-analysis/display-modernization-plan.md`
- `README.MD` (binary patch section)

## Alignment Summary
- Address + byte-pair definitions for the three display patches are aligned between C# engine, Python patch script, and `patches/README.md`.
- Backup suffix and restore implementation behavior are aligned between C# and Python (`.original.backup`, full-file restore by copy-overwrite).
- Contradictions found are documentation guidance/terminology level, not byte spec drift.

## Findings (Contradictions / Misalignment)

### 1) Medium - Backup creation is documented as unconditional on "first apply", but code creates backup only when a write is needed
- `README.MD:65` says first apply creates `BEA.exe.original.backup`.
- `BinaryPatchEngine.cs:126-135` returns early when all selected patches are already applied, so no backup is created in that path.
- `patches/patch_display_mode_flow.py:143-150` has the same behavior (`No changes needed.` before backup creation).
- Practical effect: restore can be unavailable after "apply" on already-patched binaries (`Views/BinaryPatchesView.xaml.cs:193-199`, `patches/patch_display_mode_flow.py:170-172`).

### 2) Medium - `windowed-mode-analysis.md` has conflicting operational guidance
- `reverse-engineering/binary-analysis/windowed-mode-analysis.md:107` states primary operational guidance is the startup-flow patch set (`0x12A644`, optional `0x12BB97`) exposed by Binary Patches.
- `reverse-engineering/binary-analysis/windowed-mode-analysis.md:143-145` concludes with "Recommended" path as DxWnd/dgVoodoo2, plus guard-byte normalization alternative, omitting the Binary Patches path in the final action list.
- Practical effect: readers get two different "recommended/primary" paths in the same doc.

### 3) Low - Track terminology is overloaded across docs
- `patches/README.md:17-24` defines patch tracks as `Stable`/`Experimental`.
- `reverse-engineering/binary-analysis/display-modernization-plan.md:10-18` uses `Track A`/`Track B` for strategic implementation approaches.
- This is not a byte-level contradiction, but the shared word "Track" for different taxonomies can be misread as one unified labeling system.

## Verified Aligned Items (No Contradiction)
- Patch 1 (resolution gate):
  - `BinaryPatchEngine.cs:41-43`
  - `patches/patch_display_mode_flow.py:68-70`
  - `patches/README.md:48`
- Patch 2 (force windowed startup):
  - `BinaryPatchEngine.cs:48-50`
  - `patches/patch_display_mode_flow.py:74-76`
  - `patches/README.md:49`
- Patch 3 (optional skip auto toggle):
  - `BinaryPatchEngine.cs:55-58`
  - `patches/patch_display_mode_flow.py:82-85`
  - `patches/README.md:50`
- Backup suffix naming:
  - `BinaryPatchEngine.cs:33`
  - `patches/patch_display_mode_flow.py:53`
  - `patches/README.md:219-222`
  - `README.MD:65`
- Restore behavior (full executable copy from backup):
  - `BinaryPatchEngine.cs:164-172`
  - `Views/BinaryPatchesView.xaml.cs:193-220`
  - `patches/patch_display_mode_flow.py:168-175`
  - `README.MD:65`
