# WinUI Safe-Copy Music Swap Presets Readiness Note

Status: validated local contract and UI wiring
Date: 2026-06-17

Supersession note (2026-06-22): this is historical evidence for the first two
music-swap presets. Current preset accounting is three named presets, with
`use-bea02-for-bea04` covered by the later level-100 selection/decode proof and
the music audible-output contract. Use `CURRENT_CAPABILITIES.md` and
`roadmap/mod-patch-runtime-rebuild-register.md` for current truth.

Scope: add named copied-track music swap presets for generated safe game copies without adding executable patch bytes or runtime playback claims.

Tracked outcomes:

| Area | Result |
| --- | --- |
| AppCore preset contract | `GameProfileMusicReplacementService` now exposes two named copied-track presets: `use-bea02-for-bea01` and `use-bea01-for-bea02`. |
| Mutation boundary | Presets resolve only to existing `.ogg` files under the generated safe copy's `data\Music` folder, then reuse the existing staging/backup/restore manifest path. |
| WinUI surface | Patch Bench has two direct post-create staging buttons and a create-time safe-copy selector for `BEA_02 over BEA_01` and `BEA_01 over BEA_02`. |
| Safety behavior | The installed game, original `BEA.exe`, source music files, and source save/options are not touched. Restore still uses the safe-copy backup and manifest, including after unrelated safe-copy selections make Play stale. Preset target and replacement copied tracks must exist and pass `OggS` header validation before staging. |
| Launch guard | Safe-copy launch planning now validates any active copied-music manifest and rejects target drift, backup drift, replacement-hash drift, invalid package-relative paths, and size drift before Play. |
| Proof boundary | This is staging/file-layout and launch-guard proof only. It does not prove Vorbis decode, cue selection, volume, audible playback, gameplay behavior, or no-noticeable-difference parity. |

Preset rows:

| Preset id | Target copied track | Replacement copied track |
| --- | --- | --- |
| `use-bea02-for-bea01` | `BEA_01(Master).ogg` | `BEA_02(Master).ogg` |
| `use-bea01-for-bea02` | `BEA_02(Master).ogg` | `BEA_01(Master).ogg` |

Not claimed:

- No new executable patch row.
- No runtime audio playback proof.
- No cue/mission/music-selection proof.
- No installed-game or original executable mutation.
- No Enhanced Profile Preview default inclusion.
- No `profilePreset.modules` music module in the Enhanced Profile Preview manifest.
- No sequential multi-target music staging without restore; an active copied-music manifest blocks new staging and is revalidated before Play.
- No Ghidra mutation.

Validation:

- `npm run test:winui-safe-copy-music-swap-presets`: PASS, 6 AppCore tests and 4 UI/profile/accessibility tests. Coverage includes post-create staging, create-time transactional staging, launch manifest drift rejection, runtime launch revalidation, WinUI wiring, profile policy, and accessibility IDs.
- `npm run test:winui-safe-copy-music-replacement`: PASS, 26 AppCore tests and 3 WinUI/accessibility tests.
- `npm run test:winui-safe-copy-music-swap-runtime-artifact-checker`: PASS.
- `npm run test:winui-safe-copy-live-runtime-smoke-helper`: PASS, 4 helper tests.
- `py -3 tools\winui_enhanced_preview_runtime_artifact_check.py --self-test`: PASS.
- `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo`: PASS, 0 warnings, 0 errors.
- `python tools\docsync_check.py`: PASS.
- `npm run test:doc-commands`: PASS, 3925 documented command references checked.
- `npm run test:md-links`: PASS.
- `python tools\release_profile_snapshot.py --check`: PASS, R0=6082 R2=0 R3=2 R4=18397.
- `python tools\release_curated_manifest.py --check`: PASS, selected/public allowlist 4896.
- `npm run test:public-allowlist`: PASS, 4896 rows checked.
- `npm run test:repo-hygiene`: PASS, explicit text files checked 19008.
- `git diff --check`: PASS.
- State JSON parse: PASS.
- `Get-Process BEA`: no BEA process running.
