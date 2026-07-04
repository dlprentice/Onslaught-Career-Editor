# WinUI Safe-Copy Music Replacement Readiness Note

Status: validated local staging contract and UI wiring
Date: 2026-06-16

Scope: add guarded safe-copy music replacement staging and copied-track swap to WinUI Windowed & Mods.

This slice adds two bounded resource-mod staging paths: swap one copied `.ogg` over another copied `.ogg`, or stage an external replacement `.ogg` over one existing `.ogg` in a generated app-owned safe copied game folder. The installed game folder and original `BEA.exe` remain read-only source material. The implementation writes only inside the generated safe copy, keeps a `.original.backup`, writes a redacted `onslaught-music-replacement-manifest.json`, and restores the copied track from backup.

Tracked outcomes:

| Area | Result |
| --- | --- |
| AppCore staging service | `GameProfileMusicReplacementService` validates the generated safe-copy manifest, app-owned profile root, copied-track inventory, single-file target name under `data\Music`, target existence, replacement `.ogg` extension, replacement `OggS` header, reparse-point boundaries, and hardlink state for mutated files before writing. |
| Backup/restore | Staging creates or reuses a verified original backup, rejects new staging while an active replacement manifest exists, rejects restaging when the current copied target drifted away from that backup, and restore derives target/backup paths from the validated target filename before copying the backup over the copied target and removing the active replacement manifest. |
| Manifest boundary | The music replacement manifest stores package-relative copied paths, target filename, sizes, and hashes without absolute source paths. |
| WinUI surface | Windowed & Mods exposes `Stage copied music bytes` controls under the safe copied game folder flow with quick copied-track swap controls, advanced external OGG staging controls, stable automation IDs, and copy that says staging does not prove playback. |
| Test gate | `npm run test:winui-safe-copy-music-replacement` covers the AppCore staging/restore contract and Patch Bench UI/static accessibility checks. |

Validation run:

- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GameProfileMusicReplacementServiceTests"` - passed, 20/20.
- `npm run test:winui-safe-copy-music-replacement` - passed: AppCore music replacement tests 20/20 and WinUI/static checks 3/3.

Not claimed:

- No live BEA process was launched by this validation run.
- No runtime audio playback proof.
- No Vorbis decoder compatibility proof beyond `OggS` header and file-layout validation.
- No proof that a specific mission/menu cue selects the staged file.
- No desktop/window capture.
- No runtime gameplay proof.
- No installed-game or original executable mutation.
- No Ghidra mutation.
- No new Ghidra backup; latest verified Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.
- No Godot or clean-room rebuild demo.
- No no-noticeable-difference parity claim.
