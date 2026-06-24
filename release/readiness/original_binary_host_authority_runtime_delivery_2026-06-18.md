# Original Binary Host-Authority Runtime Delivery Readiness Note

Status: complete bounded runtime-delivery proof
Date: 2026-06-18
Scope: `winui-original-binary-host-authority-runtime-delivery`

This slice adds one same-workstation host-authority scheduler-to-host-helper runtime-delivery proof for the copied original BEA binary. It validates schema `winui-original-binary-host-authority-runtime-delivery.v1`, helper version `host-authority-runtime-delivery-helper.v1`, protocol `host-authority-runtime-delivery.v1`, and delivery mode `host-authority-deterministic-p1-p2-relay-plan-to-safe-copy-host-helper`.

The proof consumes the earlier host-authority two-client scheduler artifact and a fresh copied level-850/config-1 runtime artifact. The accepted scheduler plan hash is `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`; the canonical N-slot relay-plan hash is `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002`.

Accepted positive rows:

| Command | Runtime route | Input | Evidence |
| --- | --- | --- | --- |
| `host-authority-p1-forward-0001` | P1 / `inputDevice0` / top split-screen half | `down:Q,wait:500,up:Q` | `button31ReceiveRows=10`, `forwardStateStoreRows=10` |
| `host-authority-p2-forward-0001` | P2 / `inputDevice1` / bottom split-screen half | `down:E,wait:500,up:E` | `button31ReceiveRows=8`, `forwardStateStoreRows=7` |

Runtime-delivery fields:

| Field | Value |
| --- | --- |
| `deliveredOriginalBinaryCommandCount` | `2` |
| `gameInputSentByScheduler` | `false` |
| `hostHelperInputSent` | `true` |
| `visualCaptureCount` | `7` |
| `nPlayerOriginalBinaryRuntimeProof` | `0` |
| P3/P4 status | `P3/P4 metadata-only` |
| P3/P4 gameplay rejection | `required-for-unproven-original-binary-slots` |

Validation commands:

```powershell
py -3 tools\build_winui_original_binary_host_authority_runtime_delivery_bundle.py <host-authority-two-client-smoke-proof-bundle> <live-runtime-artifact> --output <host-authority-runtime-delivery-proof-bundle>
py -3 tools\winui_safe_copy_online_host_authority_runtime_delivery_check.py <host-authority-runtime-delivery-proof-bundle>
npm run test:winui-original-binary-host-authority-runtime-delivery
```

The focused checker is `tools\winui_safe_copy_online_host_authority_runtime_delivery_check.py`; the bundle builder is `tools\build_winui_original_binary_host_authority_runtime_delivery_bundle.py`.

Boundary:

- This proves one same-workstation P1/P2 host-authority relay plan delivered into one copied original-BEA level-850/config-1 host-helper runtime artifact.
- This does not prove more than two original-binary runtime players.
- This does not prove active P3/P4 original-binary gameplay.
- This does not prove co-op or versus online mode semantics.
- This does not prove multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic simulation sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.
- No Ghidra mutation was performed and no Ghidra backup was created for this slice.
