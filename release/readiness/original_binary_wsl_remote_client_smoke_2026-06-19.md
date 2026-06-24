# Original Binary WSL Remote-Client Smoke Readiness Note

Status: complete same-physical-machine command-source smoke
Date: 2026-06-19
Scope: `original-binary-wsl-remote-client-smoke`

This slice adds one WSL2 remote-client command-source proof for the original-binary online ladder. It chains to the accepted private-LAN transport artifact, starts a Windows private-interface listener, launches a WSL2 Linux Python client with a sanitized environment, passes the ephemeral credential through stdin only, and accepts one P2 command envelope that would forward to the already-proven private LAN transport command.

Measured evidence:

| Field | Value |
| --- | --- |
| Schema | `winui-original-binary-wsl-remote-client-smoke.v1` |
| Transport | `wsl2-remote-client-tcp-jsonl-auth-smoke` |
| Network scope | `wsl2-to-windows-host-private-interface-smoke` |
| Client boundary | same-physical-machine WSL2 client; Windows host `<windows-wsl-gateway>`, WSL client `<wsl-client-address>` |
| Accepted command | `acceptedCommandId=wsl-remote-client-p2-forward-0001` |
| Upstream target | `private-lan-p2-forward-0001` |
| Gameplay slot boundary | `acceptedOriginalBinaryGameplaySlots=P1,P2`; `metadataOnlySlots=P3,P4`; `rejectedGameplayRouteSlots=P3,P4` |
| Negative routing | P3 gameplay command rejected with `metadata-slot-gameplay-not-allowed`; rate-limit command rejected |
| Safety counters | `newBeaLaunchCount=0`; `cdbAttachCount=0`; `gameInputSentByWslClient=false`; `hostHelperInputSent=false` |

Non-claims:

- `secondPhysicalHostProof=false`
- `publicMatchmakingProof=false`
- `multiHostLanProof=false`
- `nativeBeaNetcodeProof=false`
- `nPlayerOriginalBinaryRuntimeProof=0`
- `activeP3P4OriginalBinaryGameplayProof=false`

Validation:

```powershell
py -3 tools\build_winui_original_binary_wsl_remote_client_smoke_bundle.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-lan-transport-smoke-proof.json --bind-host <windows-wsl-gateway> --output subagents\winui-original-binary-online\wsl-remote-client-smoke-20260619\wsl-remote-client-smoke-proof.json
py -3 tools\winui_safe_copy_online_wsl_remote_client_smoke_check.py subagents\winui-original-binary-online\wsl-remote-client-smoke-20260619\wsl-remote-client-smoke-proof.json
npm run test:winui-original-binary-wsl-remote-client-smoke
```

This is not a second physical host proof, not multi-host LAN play, not public matchmaking, not public relay/server behavior, not native BEA netcode, not NAT traversal, not deterministic sync, not rollback, not anti-cheat, not active P3/P4 original-binary gameplay, not physical gamepad behavior, not rebuild parity, and not no-noticeable-difference online parity.
