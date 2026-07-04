# WinUI Safe-Copy Music Selection/Decode Runtime Proof

Status: accepted CDB-backed copied-game music selection/decode proof
Date: 2026-06-18

Scope: validate that a staged copied-game music replacement can be selected by the retail music system, forwarded to the PC async music stream, opened by the Ogg loader, and read for decoded PCM in one managed safe-copy runtime run.

Tracked outcome:

| Area | Result |
| --- | --- |
| Accepted artifact | `subagents/winui-safe-copy-live-runtime/music-selection-decode-level100-20260618-focus2/live-safe-copy-runtime-smoke.json` |
| Diagnostic artifact | `subagents/winui-safe-copy-live-runtime/music-selection-decode-level100-20260618-focus1/live-safe-copy-runtime-smoke.json` attached too late for the music selection/kick proof and remains a diagnostic launch/capture/stop observation only. |
| Staging | Copied `data/Music/BEA_04(Master).ogg` was replaced with shipped `BEA_02(Master).ogg` bytes inside the generated copied game folder only. |
| Launch args | `-skipfmv -level 100`; no `-nomusic` or `-nosound`. |
| Patch keys | `resolution_gate`, `force_windowed` on copied `BEA.exe` only. |
| CDB rows accepted | `CMusic__PlaySelection selection=2`, `PCPlatform__KickAsyncMusicStreamRead path=data\music\BEA_04(Master).ogg`, `COggFileRead__OpenFileAndPrimeDecoder path=data\music\BEA_04(Master).ogg`, `CMusic__UpdateStatus currentPath=data\music\BEA_04(Master).ogg`, and `COggFileRead__ReadDecodedPcm request=524288`. |
| Checker | `tools/winui_safe_copy_music_selection_decode_artifact_check.py` with `--require-ogg-decode` accepted the artifact. |
| Visual/safety | `captureCount=2`, `visualCaptureCount=2`, installed executable hash unchanged, clean override hash unchanged, source music hashes unchanged, managed stop succeeded, no `BEA.exe` process remained after stop. |

This upgrades the music replacement lane from copied-file staging plus launch/stop proof to one bounded runtime selection/decode proof for the staged copied target.

Not claimed:

- No installed-game or original executable mutation.
- No proof that the replacement was audible to the user.
- No volume, mixing, looping, crossfade, menu-state, gameplay-state, or every-track proof.
- No claim that arbitrary external OGG encodings are accepted; this run used shipped replacement bytes.
- No visual parity, rebuild parity, or no-noticeable-difference proof.
- No Ghidra mutation or Ghidra backup; latest verified Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Validation:

- `py -3 tools\winui_safe_copy_music_selection_decode_artifact_check.py subagents\winui-safe-copy-live-runtime\music-selection-decode-level100-20260618-focus2\live-safe-copy-runtime-smoke.json --expected-target "BEA_04(Master).ogg" --expected-replacement "BEA_02(Master).ogg" --expected-level 100 --expected-selection 2 --min-capture-count 2 --require-ogg-decode`
- `npm run test:winui-safe-copy-music-selection-decode-artifact`
- `git diff --check`
