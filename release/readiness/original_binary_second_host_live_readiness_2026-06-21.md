# Original Binary Second-Host Live Readiness Preflight

Status: public-safe host preflight; no live proof accepted
Date: 2026-06-21

This slice adds `tools/winui_original_binary_second_host_live_readiness.py` and package script `test:winui-original-binary-second-host-live-readiness` as the host-side preflight immediately before a real distinct-host or explicitly VM-labeled command-source run.

Current workstation result:

| Field | Value |
| --- | --- |
| `schemaVersion` | `winui-original-binary-second-host-live-readiness.v1` |
| `scope` | `host-live-run-readiness-preflight-not-command-source-proof` |
| `candidatePrivateBindAddressCount` | `1` |
| `wslOnHostInterfaceCount` | `1` |
| `serverCommandInputsComplete` | `false` |
| `acceptedLiveSecondHostCommandSourceProof` | `false` |
| `baseOnlineMultiplayerReady` | `false` |
| `hostJoinControlsMayBeEnabled` | `false` |

The preflight classifies usable non-WSL private bind interfaces, rejects WSL-on-host as second-host proof, separates contract-allowed source kinds from host-topology-ready source kinds, and keeps physical-host mode unavailable unless a distinct physical private host topology is explicitly present. VM-labeled mode remains same-physical-machine-only and is not physical multi-host proof.

Live proof still requires a private proof bundle validated with:

```powershell
py -3 tools\winui_safe_copy_online_second_host_command_source_check.py <private-bundle> --live
```

Non-claims:

- No listener is opened by this preflight.
- No invitation is created.
- No BEA launch occurs.
- No CDB attach occurs.
- No game input is sent.
- No Host/Join control is enabled.
- No live second-host command-source proof, runtime delivery proof, public matchmaking, native BEA netcode, or player-ready netplay is proven.

Focused gates:

```powershell
py -3 tools\winui_original_binary_second_host_live_readiness_test.py
py -3 tools\winui_original_binary_second_host_live_readiness.py --self-test
py -3 tools\winui_original_binary_second_host_live_readiness.py --check
npm run test:winui-original-binary-second-host-live-readiness
```
