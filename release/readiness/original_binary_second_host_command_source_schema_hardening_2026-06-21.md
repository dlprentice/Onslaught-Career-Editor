# Original Binary Second-Host Command-Source Schema Hardening

Status: protocol/proof hardening, not live netplay proof
Date: 2026-06-21
Scope: `second-host-command-source-proof-gate-not-live-runtime-proof`

This slice tightens the second-host command-source proof gate before a real VM or physical second-host run is promoted.

What changed:

| Item | Evidence |
| --- | --- |
| Strict incoming live message schema | `tools/build_winui_original_binary_second_host_command_source_bundle.py` rejects unknown top-level command fields, unknown nested session identity fields, missing required fields, and unknown command ids as `message-schema-mismatch`. |
| Strict proof artifact shape | `tools/winui_safe_copy_online_second_host_command_source_check.py` now rejects extra accepted-command, rejected-command, and transcript-event fields. |
| Required rejection count | `requiredRejectedCaseCount=16`; added `message-schema-mismatch` / `unknownFieldLiveRejected`. |
| Transcript events | Added `client_command_unknown_field` and `server_command_rejected_unknown_field`. |
| Public gate contract | `roadmap/original-binary-online-second-host-command-source.v1.json` regenerated from the validator fixture and passes `--check`. |

Validation targets:

```powershell
py -3 tools\build_winui_original_binary_second_host_command_source_bundle_test.py
py -3 tools\winui_safe_copy_online_second_host_command_source_check_test.py
py -3 tools\build_winui_original_binary_second_host_command_source_bundle.py --self-test
py -3 tools\winui_safe_copy_online_second_host_command_source_check.py --self-test
py -3 tools\winui_safe_copy_online_second_host_command_source_check.py --check
npm run test:winui-original-binary-second-host-command-source
npm run test:winui-original-binary-second-host-command-source-builder
```

Non-claims:

- `acceptedLiveSecondHostCommandSourceProof=false`
- `acceptedLiveSecondHostRuntimeDeliveryProof=false`
- `acceptedLiveSecondHostRuntimeCausalityProof=false`
- `hostJoinControlsMayBeEnabled=false`
- `baseOnlineMultiplayerReady=false`
- `multiHostLanPlayProof=false`
- `publicMatchmakingProof=false`
- `nativeBeaNetcodeProof=false`
- `newBeaLaunchCount=0`
- `cdbAttachCount=0`
- No BEA launch, CDB attach, game input, Host/Join enablement, public endpoint, or player-ready netplay is added by this slice.
