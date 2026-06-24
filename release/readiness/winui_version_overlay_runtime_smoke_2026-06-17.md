# WinUI Version Overlay Runtime Smoke Readiness Note

Status: validated bounded copied-game title/menu marker proof
Date: 2026-06-17

Scope: prove the opt-in copied-executable `version_overlay_use_patched_format_pointer` row can visibly redirect the retail title/menu version-format path to the patch-owned `V1.00 - PATCHED` string in one copied-game run. WinUI Windowed & Mods now has Proof quick-pick controls that select or clear this existing visible marker row without manually selecting its hidden companion payload and without touching other selected safe-copy mods.

Patch pair:

| Patch Id | File offset | Role |
| --- | ---: | --- |
| `version_overlay_use_patched_format_pointer` | `0x06416F` | Redirect the retail version-format pointer to the cave-hosted patched string |
| `version_overlay_patched_format_cave_string` | `0x1AA444` | Install `V%1d.%02d - PATCHED` payload bytes |

Runtime evidence:

| Area | Result |
| --- | --- |
| Tool | `tools/winui_safe_copy_live_runtime_smoke.py --arm-live-bea "LAUNCH SAFE COPY BEA" --extra-patch-key version_overlay_use_patched_format_pointer` |
| Artifact | `subagents/winui-safe-copy-live-runtime/version-overlay-patched-20260617/live-safe-copy-runtime-smoke.json` |
| Patch keys applied | `resolution_gate`, `force_windowed`, `version_overlay_use_patched_format_pointer`, `version_overlay_patched_format_cave_string` |
| Capture count | 8 bounded screen-region frames at verified target-window bounds |
| Visible frame | `capture/safe-copy-frame.png` |
| Visible frame SHA-256 | `5d0ef44202001dfb9bcf5fdf4fc743d632a5a6b06329199d71958b76fd037c44` |
| Manual visual signoff | Frame review observed title/menu bottom-left text `V1.00 - PATCHED` |
| Source safety | Installed `BEA.exe`, `BEA.exe.original.backup`, source `defaultoptions.bea`, and source `savegames` hashes stayed unchanged |
| Stop gate | Managed copied process stopped and no BEA process remained |

Claim boundary:

- This is one copied-game title/menu marker proof only.
- It proves visible output for the selected marker row on the exercised title/menu path.
- The helper success status is launch/capture/stop/source-safety proof; the `V1.00 - PATCHED` text claim is a manual visual signoff tied to the exact frame hash above, not an automated OCR gate.
- It does not prove every overlay path, the version-cheat path, gameplay behavior, long-session stability, rendering correctness, rebuild parity, or no-noticeable-difference parity.
- It does not mutate the installed Steam game, installed `BEA.exe`, clean backup executable, source `defaultoptions.bea`, or source `savegames`.
- The playable copied game folder created expected local runtime state; that is not source mutation.
