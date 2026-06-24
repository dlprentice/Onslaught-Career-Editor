# Original Binary Private Remote-Client Smoke Readiness Note

Status: complete process-separated smoke evidence
Date: 2026-06-18
Scope: `winui-original-binary-private-remote-client-smoke`

This slice hardened the prior private LAN transport smoke and added a process-separated private remote-client command-source proof on top of it. It does not launch BEA again and does not mutate the installed Steam game, the clean override executable, Ghidra, saves, or source assets.

Accepted live artifact:

```powershell
py -3 tools\build_winui_original_binary_private_lan_transport_smoke_bundle.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-relay-delivery-proof.json --bind-host <private-non-loopback-host> --output subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-lan-transport-smoke-proof.json
py -3 tools\winui_safe_copy_online_private_lan_transport_smoke_check.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-lan-transport-smoke-proof.json --expected-controller-configuration 1
py -3 tools\build_winui_original_binary_private_remote_client_smoke_bundle.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-lan-transport-smoke-proof.json --bind-host <private-non-loopback-host> --output subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-remote-client-smoke-proof.json
py -3 tools\winui_safe_copy_online_private_remote_client_smoke_check.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-remote-client-smoke-proof.json --expected-controller-configuration 1
```

Hardened upstream LAN transport result:

- `transport=private-lan-tcp-jsonl-auth-smoke`
- `bindHost=<private-non-loopback-host>`
- accepted command `private-lan-p2-forward-0001`
- forward target `private-relay-p2-forward-0001`
- exact command-id allowlist is now enforced before accepting any signed command
- `gameInputSentByTransport=false`
- `hostHelperInputSent=false`
- upstream private relay-delivery still supplies the prior `hostHelperInputSent=true` / `fresh-host-helper-cdb-proof` evidence

New remote-client result:

- schema `winui-original-binary-private-remote-client-smoke.v1`
- helper `private-remote-client-smoke-helper.v1`
- protocol `private-remote-client-input.v1`
- transport `private-remote-client-tcp-jsonl-auth-smoke`
- private non-loopback bind host `<private-non-loopback-host>`
- process model `separate-python-process`
- `clientProcessDifferentFromBuilder=true`
- `clientVerifiedServerIdentity=true`
- `credentialTransportToClientProcess=stdin-ephemeral-not-serialized-to-artifact`
- HMAC-SHA256 authorization with `credentialStorage=ephemeral-not-serialized`
- pinned smoke server/client identity fingerprints
- `replayCacheEnabled=true`
- `sequenceEnforced=true`
- one-command rate limit
- accepted command `private-remote-client-p2-forward-0001`
- forward target `private-lan-p2-forward-0001`
- `11` wire messages and `15` transcript events
- `gameInputSentByRemoteClient=false`
- `hostHelperInputSent=false`
- `sameWorkstationOnly=true`

Negative coverage includes missing auth, wrong slot, rate-limit rejection, same-process positive-claim rejection, multi-host positive-claim rejection, public-matchmaking claim rejection, direct-input claim rejection, serialized credential rejection in the checker fixture, and direct-input positive-claim rejection.

Claim boundary:

This proves only that a separate local client process can source one authenticated P2 command envelope over a private non-loopback interface and that the host-side smoke would forward it to the already-proven private LAN transport command. It is not real online multiplayer, not multi-host LAN play, not public matchmaking, not public relay/server behavior, not native BEA networking, not NAT traversal, not deterministic sync, not rollback, not anti-cheat, not dual-client parity, not physical gamepad behavior, not rebuild parity, and not no-noticeable-difference online parity.

Validation:

- `npm run test:winui-original-binary-private-lan-transport-smoke`
- `npm run test:winui-original-binary-private-remote-client-smoke`
- `py -3 tools\winui_safe_copy_online_private_lan_transport_smoke_check.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-lan-transport-smoke-proof.json --expected-controller-configuration 1`
- `py -3 tools\winui_safe_copy_online_private_remote_client_smoke_check.py subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1\private-remote-client-smoke-proof.json --expected-controller-configuration 1`

No Ghidra mutation occurred, so no Ghidra backup was created for this slice. The latest Ghidra review backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`; future Ghidra backups should use `D:\GhidraBackups` while external drives are detached.
