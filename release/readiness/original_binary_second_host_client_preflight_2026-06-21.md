# Original Binary Second-Host Client Preflight

Status: complete tooling/readiness follow-up
Date: 2026-06-21

This slice adds a redacted client-side identity/source-safety preflight for the original-binary second-host command-source harness.

The new command:

```powershell
py -3 tools\winui_original_binary_second_host_command_source_client.py --identity-preflight --client-copied-profile-root <client-copied-profile-root> --client-installed-game-root <client-installed-game-root>
```

It outputs the computed `clientIdentityFingerprint`, a server copy/paste argument for `--client-identity-fingerprint`, redacted machine-identity fields, and client copied-profile/source-install hash evidence without serializing raw paths.

2026-06-22 follow-up: live proof guidance now tells operators to omit manual runtime-kind overrides. A real VM client must be classified by auto platform preflight to become live-validation-compatible; manual `vm-guest` labeling remains attempt-only.

Truth boundary:

- This is not live second-host command-source proof.
- This is not runtime causality proof.
- This is not Host/Join enablement.
- This does not launch BEA, attach CDB, open a listener, send game input, or create a private proof bundle.
- Current booleans remain `baseOnlineMultiplayerReady=false`, `hostJoinControlsMayBeEnabled=false`, `acceptedLiveSecondHostCommandSourceProof=false`, `acceptedLiveSecondHostRuntimeDeliveryProof=false`, `acceptedLiveSecondHostRuntimeCausalityProof=false`, `multiHostLanPlayProof=false`, `publicMatchmakingProof=false`, `nativeBeaNetcodeProof=false`, `activeP3P4OriginalBinaryGameplayProof=false`, and `nPlayerOriginalBinaryRuntimeProof=0`.

The same slice adds `roadmap/original-binary-online-multiplayer-feasibility.md#netplay-proof-rung-matrix` as the canonical proof ladder separating same-host, WSL-on-host, VM-labeled private-LAN command source, distinct physical private-LAN command source, live command-source, source-bound runtime causality, Host/Join enablement, P3/P4 scalability, and player-ready netplay.

Validation passed:

- `py -3 -m py_compile tools\winui_original_binary_second_host_command_source_client.py tools\winui_original_binary_second_host_command_source_client_test.py`
- `py -3 tools\winui_original_binary_second_host_command_source_client_test.py`
- `npm run test:winui-original-binary-second-host-command-source-builder`
- `npm run test:winui-original-binary-second-host-command-source`
- `npm run test:winui-copied-profile-runtime`
- `py -3 tools\docsync_check.py`
- `npm run test:doc-commands`
- `npm run test:md-links`
- `py -3 tools\release_profile_snapshot.py --check`
- `py -3 tools\release_curated_manifest.py --check`
- `npm run test:public-allowlist`
- `npm run test:repo-hygiene`
