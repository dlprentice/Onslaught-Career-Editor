# WinUI ZIP Release v1.0.8 - 2026-07-04

Status: published GitHub Release

This note tracks the v1.0.8 public ZIP release. It is a GitHub Release with the
final ZIP and checksum sidecar uploaded, targeting commit
`6e7bcb42b3849b51a9d14dbb15863c520aa21a4b`. It is not a signing result, MSIX,
Store package, installer, SmartScreen/reputation claim, runtime gameplay proof,
online capability promotion, or rebuild/visual parity claim.

## Reference Audit

Updated current release-prep metadata:

- `package.json` version: `1.0.8`
- `package-lock.json` root package versions: `1.0.8`
- `release/readiness/public_package.json` version: `1.0.8`
- `package.json` release-candidate ZIP script:
  `OnslaughtToolkit-winui-v1.0.8-win-x64.zip`
- `.gitignore` release scratch coverage for generated
  `subagents/winui-zip-release-readiness-current/` output
- `README.RELEASE.md`, `CURRENT_CAPABILITIES.md`, and
  `lore-book/CURRENT_CAPABILITIES.md` distinguish published v1.0.8 truth from
  historical v1.0.7 release records

Historical references intentionally retained:

- `release/readiness/winui_zip_release_v1_0_7_2026-06-25.md` remains the
  historical v1.0.7 release record with its real tag, download, checksum, and
  SHA-256 facts.
- Earlier dated v1.0.3 through v1.0.6 readiness notes remain historical.
- `README.MD` now describes v1.0.8 as the current public download and keeps
  prior releases as historical context.
- Third-party dependency versions such as `@hapi/hoek@11.0.7` and
  `path-parse@1.0.7` remain unchanged.

## Published Artifact

The final v1.0.8 release-candidate probe built the final-named ZIP and passed
the package/layout/Lore/launch/Home/Media/process-cleanup checks. The artifact
below was uploaded to the v1.0.8 GitHub Release.

- Release URL:
  `https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.8`
- ZIP: `OnslaughtToolkit-winui-v1.0.8-win-x64.zip`
- ZIP size: `246803017`
- SHA-256: `f01474cb21624cfb938450911be277937e0e12cd04ff1755d2ff1b87aa6b283a`
- Checksum sidecar: `OnslaughtToolkit-winui-v1.0.8-win-x64.zip.sha256`
- Probe report:
  `subagents/winui-zip-release-candidate-probe/current/zip-package-report.json`
- Lore document count: `949`
- Root layout: `Launch Onslaught Toolkit.cmd`, `README.MD`, `LICENSE`,
  `app/`, `lore-book/`, `lore-pack/`
- Longest ZIP Explorer-relative path: `133` characters within the `180`
  character budget
- Launch smoke: pass
- Home navigation smoke: pass
- Home deep-link smoke: pass
- Lore reader smoke: pass
- Representative Media smoke: pass after `1` attempt
- WinUI process cleanup: pass (`<none>`)

Representative Media smoke repair:

- Classification: probe/test locator and activation bug, with a timing/UIA
  wait contributor.
- Root cause: the Media smoke searched every window descendant for a name prefix
  and clicked the first match. That could target the search box or nested text
  instead of a selectable `TreeItem`, leaving `MediaAudioNowPlaying` at
  `No track selected`.
- Repair: `WinUiMediaInteractionSmokeTests` now scopes representative audio and
  video row lookup to `MediaAudioTreeView` / `MediaVideoTreeView`, requires
  `ControlType.TreeItem`, uses UIA scroll/selection/invoke/click activation,
  and waits until the selected-text AutomationId equals the expected row before
  asserting the existing strict checks.
- The gate still verifies the same representative Media scenario; it was not
  skipped, weakened, or changed to accept `No track selected`.

## Validation

Final validation refreshed in this prep slice:

- Focused extracted-app representative Media smoke:
  `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaInteractionSmokeTests.MediaPage_PlaysRepresentativeAudioAndVideoRowsThroughUi"` with
  `ONSLAUGHT_WINUI_TEST_EXE_PATH` pointing at the extracted v1.0.8 candidate app
  - pass (`1` passed, `0` failed)
- `npm run test:winui-zip-release-candidate-probe` - pass
  - `extracted_media_smoke`: pass after `1` attempt
- `npm run build:winui` - pass
- `npm run test:winui-primary-lane` - pass
  - AppCore tests: `1217` passed, `0` failed
  - UI tests: `132` passed, `2` skipped, `0` failed
- `git diff --check` - pass
- JSON parse for edited JSON - pass
- `npm run test:repo-hygiene` - pass
- `npm run test:public-allowlist` - pass
- `npm run test:hard-payload-safety` - pass
- `npm run test:doc-commands` - pass
- `npm run test:md-links` - pass

Post-publication verification confirmed the release exists, the `v1.0.8` tag
resolves to `6e7bcb42b3849b51a9d14dbb15863c520aa21a4b`, the ZIP and SHA-256
sidecar assets are uploaded, the uploaded ZIP size is `246803017`, and the
uploaded ZIP asset digest is
`sha256:f01474cb21624cfb938450911be277937e0e12cd04ff1755d2ff1b87aa6b283a`.

## Boundaries

- GitHub Release publication, tag creation, and release asset upload occurred
  for `v1.0.8` only.
- No signing, installer, MSIX, Store package, or SmartScreen claim.
- No Battle Engine Aquila game files, copied executables, saves, media payloads,
  raw proof bundles, CDB logs, screenshots, full Ghidra databases, secrets, or
  bulky generated artifacts are committed.
- No installed game folder or original `BEA.exe` mutation.
- No Host/Join enablement, player-ready online claim, gameplay claim, rebuild
  parity claim, or visual parity claim.
