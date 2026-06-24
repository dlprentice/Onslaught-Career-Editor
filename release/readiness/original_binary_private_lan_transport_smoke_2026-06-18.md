# Original Binary Private LAN Transport Smoke Readiness Note

Status: complete bounded transport/auth smoke
Date: 2026-06-18
Scope: `winui-original-binary-private-lan-transport-smoke`

This slice adds a single-host private LAN-interface transport/auth smoke chained to the existing original-binary private relay-delivery proof. It does not launch BEA again, does not mutate the installed Steam game, does not mutate the original `BEA.exe`, and does not claim multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, deterministic sync, rollback, anti-cheat, dual-client parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Accepted Evidence

| Field | Accepted value |
| --- | --- |
| Schema | `winui-original-binary-private-lan-transport-smoke.v1` |
| Helper | `winui-original-binary-private-lan-transport-smoke-helper` / `private-lan-transport-smoke-helper.v1` |
| Protocol | `private-lan-transport-input.v1` |
| Transport | `private-lan-tcp-jsonl-auth-smoke` |
| Bound host | `<private-non-loopback-host>` private non-loopback interface |
| Accepted command | `private-lan-p2-forward-0001` |
| Forward target | `private-relay-p2-forward-0001` |
| Authorization | `HMAC-SHA256`, `ephemeral-not-serialized`, pinned server identity |
| Replay controls | `nonceWindowSeconds=30`, `replayCacheEnabled=true`, `sequenceEnforced=true` |
| Rate limit | `maxAcceptedCommandsPerSession=1`, `maxCommandsPerSecond=1` |
| Transcript | `25` wire messages, `27` events |
| Transport game input | `gameInputSentByTransport=false` |
| New host-helper input | `hostHelperInputSent=false` |
| Upstream delivery evidence | private relay-delivery proof still records `hostHelperInputSent=true` and `fresh-host-helper-cdb-proof` |

Negative rows cover missing authentication, bad HMAC, replayed nonce, expired timestamp, sequence gap, wrong command id, wrong server identity, rate limit, compatibility mismatch, P1/wrong slot, loopback-positive claim, public-bind claim, and direct-input claim.

## Commands

Focused self-test:

```powershell
npm run test:winui-original-binary-private-lan-transport-smoke
```

Live ignored proof regeneration/check:

```powershell
py -3 tools\build_winui_original_binary_private_lan_transport_smoke_bundle.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-relay-delivery-proof.json --bind-host <private-non-loopback-host> --output subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-lan-transport-smoke-proof.json
py -3 tools\winui_safe_copy_online_private_lan_transport_smoke_check.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-lan-transport-smoke-proof.json --expected-controller-configuration 1
```

The generated proof bundle stays under ignored `subagents/` evidence and is excluded from public release scope.

## Boundary

This is a transport-envelope proof, not real online multiplayer. It proves only that one signed P2 command envelope can be accepted on a private non-loopback interface and bounded before handoff to the already-proven private relay-delivery path. The retail game still runs as a local split-screen host in prior proof slices; multi-host session state, public matchmaking, native BEA networking, sync strategy, and gameplay parity remain future work.
