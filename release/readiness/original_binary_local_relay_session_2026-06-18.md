# Original Binary Local Relay Session Proof

Status: accepted localhost relay/session descriptor proof
Date: 2026-06-18
Scope: WinUI/AppCore safe copied original-binary online-feasibility proof

This slice adds the second original-binary-online-shaped proof without claiming real online play. It consumes the accepted loopback P2 proof bundle and opens a localhost-only TCP JSONL relay bound to `127.0.0.1`. The relay accepts one P2 Movement/Forward command that is compatible with the prior copied-BEA loopback proof, rejects malformed and P1-targeted commands, and records a replayable transcript.

The local relay proof bundle uses schema `winui-original-binary-local-relay-session.v1` with helper version `local-relay-helper.v1` and protocol version `local-relay-input.v1`. It references the prior loopback proof hash, records a session descriptor compatibility key, and preserves exact launch/session compatibility fields: clean retail specimen SHA-256, copied profile manifest hash, patch keys, launch arguments `-skipfmv -level 850 -configuration 1`, level `850`, controller configuration `1`, remote player slot `P2`, and upstream loopback command `loopback-p2-forward-0001`.

Accepted checker result:

| Field | Value |
| --- | --- |
| Transport | `localhost-tcp-jsonl` |
| Bind host | `127.0.0.1` |
| Relay helper | `local-relay-helper.v1` |
| Relay protocol | `local-relay-input.v1` |
| Accepted command | `local-relay-p2-forward-0001` |
| Upstream loopback command | `loopback-p2-forward-0001` |
| Transcript | `9` JSONL wire messages, `11` recorded events |
| Rejections | malformed command and P1/wrong-slot command rejected |
| Relay-side game input | `false`; delivery remains proven by the upstream loopback/CDB artifact |

Validation:

```powershell
py -3 tools\build_winui_original_binary_local_relay_session_bundle.py <private-loopback-proof-bundle>
py -3 tools\winui_safe_copy_online_local_relay_session_check.py <private-local-relay-proof-bundle> --expected-controller-configuration 1
npm run test:winui-original-binary-local-relay-session
```

Claim boundary:

- This proves a localhost TCP JSONL relay/session descriptor and command-acceptance boundary chained to an existing safe copied original-BEA loopback P2 input proof.
- This does not prove LAN transport, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, anti-cheat, deterministic sync, rollback, two-client parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.
- The generated relay proof bundle remains private/local because it references private proof paths and copied-profile metadata. Public release material may summarize the bounded proof class and checker names only.

Next proof class:

Build a private relay-delivery proof over the same command shape. That proof should demonstrate that a relay-delivered P2 command reaches the same host-helper/game-input path before any LAN, public matchmaking, or native BEA networking work is claimed.
