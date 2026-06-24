# Original Binary Second-Host Readiness Guard

Status: public-safe readiness guard, not runtime proof
Date: 2026-06-20

This slice adds `roadmap/original-binary-online-second-host-readiness.v1.json` and `tools/winui_safe_copy_online_second_host_readiness_check.py` to define the next original-binary online proof boundary before any Host/Join surface is enabled.

Accepted guard tokens:

| Token | Value |
| --- | --- |
| `schemaVersion` | `winui-original-binary-second-host-readiness.v1` |
| `readinessScope` | `second-host-command-source-readiness-not-runtime-proof` |
| `baseOnlineMultiplayerReady` | `false` |
| `secondHostProof` | `false` |
| `multiHostLanProof` | `false` |
| `publicMatchmakingProof` | `false` |
| `nativeBeaNetcodeProof` | `false` |
| `activeP3P4OriginalBinaryGameplayProof` | `false` |
| `hostJoinControlsMayBeEnabled` | `false` |
| `acceptedOriginalBinaryGameplaySlots` | `P1,P2` |
| `metadataOnlySlots` | `P3,P4` |

The next evidence must prove `distinct-private-host-command-source-proof` and `host-runtime-delivery-from-source-bound-distinct-command-source`. The guard rejects `loopback`, `same-workstation-process`, `wsl-on-host`, `public-internet-host`, and `unknown-peer` command sources as second-host proof.

Before promotion, the next proof must also provide different host identity, non-loopback private address evidence assigned to an interface, sanitized host/client interface evidence, pinned host identity, session-scoped authentication, copied-profile hashes on both sides, installed-game pre/post hashes on both sides, and Program Files mutation rejection.

Validation:

```powershell
py -3 tools\winui_safe_copy_online_second_host_readiness_check_test.py
py -3 tools\winui_safe_copy_online_second_host_readiness_check.py --self-test
py -3 tools\winui_safe_copy_online_second_host_readiness_check.py --check
npm run test:winui-original-binary-second-host-readiness
```

Non-claims:

- No BEA launch is added by this guard.
- No CDB attach is added by this guard.
- No second-host LAN play is proven.
- No public matchmaking or public endpoint is implemented.
- No native BEA netcode is proven or implemented.
- No Host/Join/Matchmaking WinUI button is enabled.
- No active P3/P4 original-binary gameplay is proven.
- No deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity is proven.
