# Original Binary Host-Authority Runtime Delivery Replayability Readiness Note

Status: complete bounded replayability proof
Date: 2026-06-18
Scope: `winui-original-binary-host-authority-runtime-delivery-replayability`

This slice adds a second same-workstation host-authority scheduler-to-host-helper runtime-delivery proof for the copied original BEA binary and validates both runtime-delivery bundles as a replayability pair. It keeps the original-binary runtime claim bounded to P1/P2 in one copied level-850/config-1 split-screen host per proof.

Accepted pair:

| Proof | Runtime artifact | Runtime players | Evidence |
| --- | --- | --- | --- |
| First | `subagents/winui-safe-copy-live-runtime/online-host-authority-runtime-delivery-20260618-focus1/host-authority-runtime-delivery-proof.json` | P1 `04815090`, P2 `0482c890` | `visualCaptureCount=7`, `deliveredOriginalBinaryCommandCount=2` |
| Replay | `subagents/winui-safe-copy-live-runtime/online-host-authority-runtime-delivery-replay-20260618-focus1/host-authority-runtime-delivery-proof.json` | P1 `047fb090`, P2 `04812890` | `visualCaptureCount=7`, `deliveredOriginalBinaryCommandCount=2` |

Replayability invariants:

| Field | Value |
| --- | --- |
| Bundle count | `2` |
| Role invariant | P1 -> `down:Q,wait:500,up:Q` -> `inputDevice0`; P2 -> `down:E,wait:500,up:E` -> `inputDevice1` |
| Host relay plan hash | `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376` |
| N-slot relay plan hash | `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002` |
| Per-proof delivery | `deliveredOriginalBinaryCommandCount=2`, `hostHelperInputSent=true`, `gameInputSentByScheduler=false` |
| N-player runtime proof | `nPlayerOriginalBinaryRuntimeProof=0` |
| P3/P4 status | `P3/P4 metadata-only`; gameplay commands rejected as `required-for-unproven-original-binary-slots` |

The replayability checker requires distinct bundle paths, live runtime artifact hashes, exact-PID CDB log paths, process IDs, and runtime player/controller/BattleEngine/Walker tuples. It does not require exact row counts because CDB row counts vary by run; it requires positive P1/P2 button-31 receive and forward state-store rows.

Validation commands:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_runtime_delivery_replayability_check.py --self-test
py -3 tools\winui_safe_copy_online_host_authority_runtime_delivery_replayability_check.py subagents\winui-safe-copy-live-runtime\online-host-authority-runtime-delivery-20260618-focus1\host-authority-runtime-delivery-proof.json subagents\winui-safe-copy-live-runtime\online-host-authority-runtime-delivery-replay-20260618-focus1\host-authority-runtime-delivery-proof.json
npm run test:winui-original-binary-host-authority-runtime-delivery-replayability
```

Boundary:

- This proves the accepted host-authority P1/P2 scheduler relay plan can be delivered through the safe-copy host-helper input path across two distinct copied original-BEA level-850/config-1 runtime artifacts.
- This does not prove more than two original-binary runtime players.
- This does not prove active P3/P4 original-binary gameplay.
- This does not prove co-op or versus online mode semantics.
- This does not prove multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic simulation sync, rollback, anti-cheat, physical gamepad behavior, improved control feel, rebuild parity, or no-noticeable-difference online parity.
- No Ghidra mutation was performed and no Ghidra backup was created for this slice.
