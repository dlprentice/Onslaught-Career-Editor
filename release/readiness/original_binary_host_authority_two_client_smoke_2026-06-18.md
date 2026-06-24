# Original Binary Host-Authority Two-Client Smoke Readiness Note

Status: complete bounded scheduler proof
Date: 2026-06-18
Scope: `winui-original-binary-host-authority-two-client-smoke`

This slice adds a same-workstation host-authority scheduler proof on top of the accepted private remote-client smoke. It does not launch BEA, does not send game input, does not mutate any executable, does not mutate Ghidra, and does not touch the installed Steam folder.

## Accepted Evidence

The generated private proof is stored under ignored runtime evidence:

```text
subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\host-authority-two-client-smoke-proof.json
```

The proof records:

- schema `winui-original-binary-host-authority-two-client-smoke.v1`
- helper `host-authority-two-client-smoke-helper.v1`
- protocol `host-authority-two-client-input.v1`
- transport `host-authority-two-client-tcp-jsonl-smoke`
- private bind host `<private-non-loopback-host>`
- process model `two-separate-python-client-processes`
- `clientProcessIdsDistinctFromBuilder=true`
- `clientProcessIdsDistinctFromEachOther=true`
- `credentialTransportToClientProcesses=stdin-ephemeral-not-serialized-to-artifact`
- `HMAC-SHA256` authorization with `ephemeral-not-serialized` slot credentials
- `serverIdentityMode=pinned-fingerprint`
- `clientIdentityMode=pinned-slot-fingerprint`
- `replayCacheEnabled=true`
- `sequenceEnforced=true`
- one accepted P2 command `host-authority-p2-forward-0001`
- one accepted P1 command `host-authority-p1-forward-0001`
- arrival order `P2`, then `P1`
- deterministic schedule order `P1`, then `P2`
- relay plan hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`
- transcript `22` observed wire messages / `26` observed events
- `gameInputSentByScheduler=false`
- `hostHelperInputSent=false`
- `sameWorkstationOnly=true`

The checker requires rejection rows for missing authentication, public-matchmaking claim, direct-input claim, wrong command id, replay nonce, and slot rate limit.

## Commands

```powershell
py -3 tools\build_winui_original_binary_host_authority_two_client_smoke_bundle.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-remote-client-smoke-proof.json --bind-host <private-non-loopback-host> --output subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\host-authority-two-client-smoke-proof.json
py -3 tools\winui_safe_copy_online_host_authority_two_client_smoke_check.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\host-authority-two-client-smoke-proof.json --expected-controller-configuration 1
npm run test:winui-original-binary-host-authority-two-client-smoke
```

## Boundary

This is a same-workstation two-client host-authority scheduler smoke only. It proves two separate local client processes can authenticate with slot-scoped ephemeral HMAC credentials, source one P1 and one P2 movement command, and be deterministically scheduled into a host input plan.

It does not prove multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic simulation sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, no-noticeable-difference online parity, or improved control feel.

No Ghidra backup was created because no Ghidra mutation occurred. The latest verified Ghidra review backup remains:

```text
G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified
```
