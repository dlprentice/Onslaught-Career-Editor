# Prompt 4/5 media proof evidence

Status: compact tracked runtime evidence summary; raw proof payloads excluded
Last updated: 2026-04-29
Release posture: excluded from portable app ZIPs and legacy curated exports

This report preserves the Prompt 4 and Prompt 5 media proof facts without embedding raw game media, screenshots, data URLs, or base64 payloads. The referenced screenshots and proof JSON remain ignored/local evidence because they can contain rendered game asset evidence.

## Scope

- Branch: `wip/sandbox`
- Source commit: `663ed2993086f7ce52097e874c23dd7a4db26fd0`
- Evidence-report commit: `e2e90e56ca688790dc4ce87f71580d1ee53ffff2`
- Repo root: `[maintainer-private-checkout]`
- Runtime surface: Electron desktop dev mode against Vite renderer
- Game profile source: stored local game profile at `[maintainer-private-checkout]\game`
- No Game Harness runtime proof was started in this evidence pass.

## Commands and proof runs

- `git status --short --branch`
- `git rev-parse HEAD`
- `node subagents/2026-04-29-prompt4-texture-proof.cjs`
- `node subagents/2026-04-29-prompt5-video-proof.cjs`
- `npm run typecheck`
- `npm run test:renderer-smoke`
- `npm run test:bundle-policy`
- `py -3 tools\release_curated_manifest.py --check`
- `node -e "<parse state/proof JSON files>"`
- `git diff --check`

Prompt 4 proof artifacts were last written at 2026-04-29 12:50:52 America/New_York. Prompt 5 accepted proof artifacts were last written at 2026-04-29 14:17:41 America/New_York.

## Prompt 4 texture preview proof

- Local proof JSON: `[maintainer-private-checkout]\subagents\2026-04-29-prompt4-texture-preview-proof.json`
- Local screenshot: `[maintainer-private-checkout]\subagents\2026-04-29-prompt4-texture-preview.png`
- Screenshot dimensions and size: 1440x940, 178683 bytes
- Catalog path: `[maintainer-private-checkout]\subagents\asset_catalog_wave1_2026-03-14\catalog.json`
- Catalog schema: `media-catalog.v1`
- Query: `cloud.tga`
- LTLogo texture matches: 0
- Texture row id: `texture:atmospherics\clouds\cloud.tga`
- Texture label: `atmospherics\clouds\cloud.tga`
- Group: `dxtntextures`
- Source path: `game\data\resources\dxtntextures\Atmospherics%Clouds%Cloud.tga(0)A8R8G8B8.aya`
- Export path: `[maintainer-private-checkout]\subagents\asset_export_wave1_2026-03-13\loose_textures\dxtntextures\Atmospherics%Clouds%Cloud.tga(0)A8R8G8B8.png`
- Preview payload schema: `media-preview.v1`
- Preview MIME: `image/png`
- Preview byte size: 904
- PNG dimensions: 64x64
- Renderer proof: image complete, natural dimensions 64x64, rendered dimensions 64x64, visible label present

The preview path was repo-contained and resolved through the generated catalog. The committed report intentionally omits the preview data URL and any base64 payload.

## Prompt 5 in-app Bink playback proof

- Local proof JSON: `[maintainer-private-checkout]\subagents\2026-04-29-prompt5-video-proof.json`
- Local screenshot: `[maintainer-private-checkout]\subagents\2026-04-29-prompt5-video-panel.png`
- Screenshot dimensions and size: 1440x940, 179128 bytes
- Catalog path: `[maintainer-private-checkout]\subagents\asset_catalog_wave1_2026-03-14\catalog.json`
- Catalog schema: `media-catalog.v1`
- Query: `LTLogo`
- Video row id: `video:ltlogo.vid`
- Video label: `LTLogo.vid`
- Group: `Root/menu clips`
- Playback id: `video:video:ltlogo.vid`
- Codec/status metadata: `BIKi`, `needs-transcode`
- Source path: `[maintainer-private-checkout]\game\data\video\LTLogo.vid`
- Source byte size: 1838068
- Source SHA-256: `2f2819b52b696b2feec5b9bbd60e2d0a1e3f95e48d455ecdc1f3152e06e32b34`
- Playback payload schema: `video-playback.v1`
- Playback mode: `inline-transcoded`
- Cache status: `hit`
- MIME: `video/mp4`
- VLC backend: `C:\Program Files\VideoLAN\VLC\vlc.exe`
- MP4 cache path: `[maintainer-local-appdata]\media-cache\video\aa3a4af92c9ce56f4a904159.mp4`
- MP4 cache byte size: 1716516
- Cache location proof: under `%APPDATA%\Electron\media-cache\video`, outside the repo root
- Renderer proof: `<video>` present, `readyState=4`, `duration=9.16585`, `videoWidth=480`, `videoHeight=300`, playback attempt returned `played`, `currentTime=0.258679`, no media error code, visible `HIT` and `IN APP` badges present

The final accepted Prompt 5 proof used a cache hit. A prior failed proof harness run appears to have created the cold cache, so this report does not claim that the final accepted run created the cache from cold state.

## Privacy and release posture

- The screenshots and proof JSON under `subagents/` remain local ignored evidence.
- The MP4 cache path is under the user app-data media cache, outside the repo.
- This report is sanitized text only and does not contain raw PNG/MP4 bytes, `.vid` bytes, data URLs, or base64 payloads.
- `release/readiness/private_runtime_evidence/**` is explicitly excluded from portable app ZIPs and legacy curated exports.
- `onslaught_codex_directive.md` is historical/operator project context and is excluded from portable app ZIPs and legacy curated exports.

## What is proven

- Electron desktop dev mode can render a catalog-constrained PNG texture preview through `media-preview.v1`.
- Electron desktop dev mode can prepare and render catalog-constrained `LTLogo.vid` in the in-app video panel through `video-playback.v1`, VLC backend transcode infrastructure, and an app-owned MP4 cache.
- The renderer does not receive arbitrary file paths or raw process control for these flows; it requests catalog IDs/playback IDs and receives typed payloads.

## Remaining media proof gaps

- Packaged portable-bundle texture preview and video playback have not been separately proven.
- The final accepted Prompt 5 proof used `cacheStatus=hit`; cold-cache creation occurred during an earlier failed harness run and is not claimed as the accepted proof state.
- Screenshots and proof JSON remain local ignored private evidence, not release artifacts.
- Broader coverage across more texture/video rows is still pending.
