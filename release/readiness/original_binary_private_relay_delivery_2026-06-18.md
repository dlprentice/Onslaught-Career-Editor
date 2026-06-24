# Original Binary Private Relay Delivery Proof

Status: accepted local/private relay-delivery adapter proof
Date: 2026-06-18
Scope: WinUI/AppCore safe copied original-binary online-feasibility proof

This slice adds the third original-binary-online-shaped proof without claiming real online play. It consumes the accepted localhost relay/session proof, uses a fresh safe copied `BEA.exe` level-850/config-1 runtime artifact, and validates that one relay-delivered P2 Movement/Forward command is accepted by the safe-copy host-helper delivery adapter and mapped to the same P2 input route proven by exact-PID CDB.

The private relay-delivery proof bundle uses schema `winui-original-binary-private-relay-delivery.v1` with helper version `private-relay-delivery-helper.v1`, protocol version `private-relay-delivery.v1`, adapter version `host-helper-delivery-adapter.v1`, and delivery transport `localhost-relay-host-helper-adapter`.

Accepted checker result:

| Field | Value |
| --- | --- |
| Private command | `private-relay-p2-forward-0001` |
| Local relay command | `local-relay-p2-forward-0001` |
| Upstream loopback command | `loopback-p2-forward-0001` |
| Remote slot | `P2` |
| Mapped input | `down:E,wait:500,up:E` |
| Relay-side game input | `false` |
| Host-helper input | `true` |
| Host-helper evidence | `fresh-live-runtime-cdb-proof` |
| Fresh visual captures | `5` |
| Runtime player pointers | `p0=0472b090`, `p1=04742890` |
| P2 CDB rows | `12` button-31 receive rows, `12` Walker forward entry rows, `12` Walker forward state-store rows |
| Transcript | `8` adapter messages/events |
| Negative rows | malformed delivery, P1/wrong-slot delivery, and compatibility-mismatch delivery rejected |

Validation:

```powershell
py -3 tools\winui_safe_copy_live_runtime_smoke.py --artifact-root subagents\winui-safe-copy-live-runtime\online-private-relay-delivery-20260618-focus1 --timeout-seconds 25 --capture-count 4 --pre-input-capture-count 1 --focus-before-pre-input-capture --post-window-delay-seconds 8 --level-id 850 --controller-configuration 1 --persist-controller-config-in-options --bind-forward-qe-for-input-isolation --enable-cdb-observer --arm-cdb-observer "ATTACH CDB TO SAFE COPY BEA" --cdb-command-file tools\runtime-probes\local-multiplayer-level850-input-state-delta-observer.cdb.txt --cdb-log-ready-timeout-ms 30000 --cdb-post-attach-wait-seconds 3 --input-sequence "wait:300" --input-sequence "down:E,wait:500,up:E" --arm-live-bea "LAUNCH SAFE COPY BEA"
py -3 tools\build_winui_original_binary_loopback_p2_input_bundle.py <private-live-runtime-artifact>
py -3 tools\build_winui_original_binary_local_relay_session_bundle.py <private-loopback-proof-bundle>
py -3 tools\build_winui_original_binary_private_relay_delivery_bundle.py <private-local-relay-proof-bundle>
py -3 tools\winui_safe_copy_online_private_relay_delivery_check.py <private-relay-delivery-proof-bundle> --expected-controller-configuration 1
npm run test:winui-original-binary-private-relay-delivery
```

Claim boundary:

- This proves a local/private relay-delivery adapter contract chained to a localhost relay proof and a fresh copied original-BEA exact-PID CDB P2 input proof.
- This proves the relay did not inject game input directly; the safe-copy host helper sent focused input into the managed copied BEA window.
- This does not prove LAN transport, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, anti-cheat, deterministic sync, rollback, two-client parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.
- The generated live runtime, loopback, relay, and delivery proof bundles remain private/local because they reference private proof paths, copied-profile metadata, CDB logs, captures, and process identifiers. Public release material may summarize the bounded proof class and checker names only.

Next proof class:

Build a private/LAN transport smoke only after per-session authorization, nonce/expiry, replay protection, command sequencing/rate limiting, server identity, and private relay boundary rules are designed outside git. Do not expose public matchmaking until private relay delivery, physical gamepad/device routing, state/authority design, and abuse-control posture are stable.
