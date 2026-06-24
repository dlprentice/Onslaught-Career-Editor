# Original-Binary Second-Host Mapped P2 Host-Helper Receipt Readiness Note

Status: proof-boundary hardening complete
Date: 2026-06-21
Scope: `host-runtime-delivery-from-source-bound-distinct-command-source`

This slice hardens the online multiplayer proof ladder before any Host/Join enablement. It makes mapped P2 sequence and host-helper receipt binding explicit in the second-host runtime executor, runtime promotion guard, runtime causality gate, readiness contract, and Host/Join composite gate.

Accepted receipt boundary:

| Field | Required value |
| --- | --- |
| `hostHelperInputBoundToSecondHostCommandSource` | `true` |
| `requiresMappedP2SequenceReceipt` | `true` |
| `hostHelperMappedInputSequence` / `p2MappedInputSequence` | `down:E,wait:500,up:E` |
| `hostHelperRuntimeRoute` / `p2RuntimeRoute` | `P2/inputDevice1/bottom-split-half` |
| `hostHelperInputDevice` / `inputDevice` | `1` |
| `gameInputSentBySecondHostClient` | `false` |
| `gameInputSentByHostAuthorityScheduler` | `false` |

What changed:

- The second-host runtime executor proof now emits source-binding and runtime-evidence fields for the accepted second-host P2 command, the host-authority P2 command, the mapped P2 sequence hash, runtime route, input device, and host-helper delivery authority.
- The runtime executor checker recomputes those fields from the source artifacts instead of trusting the proof JSON.
- The promotion guard now rejects future promotion candidates that omit `mappedP2SequenceReceipt` / `hostHelperDeliveryReceipt` or carry the wrong mapped P2 sequence, but it remains shape preflight only.
- The runtime causality checker now file-backs `mappedP2SequenceReceipt` against the runtime input-window artifact and `hostHelperDeliveryReceipt` against the exact-PID CDB artifact, then requires those raw bodies to carry the mapped P2 sequence, route, input device, host-helper input flag, and positive P2 input/state-store row counts.
- The command-source, readiness, bridge, and Host/Join contracts now use canonical proof id `host-runtime-delivery-from-source-bound-distinct-command-source`.

Non-claims:

- No player-ready online multiplayer.
- No Host/Join enablement.
- No public matchmaking.
- No native BEA netcode.
- No active P3/P4 original-binary gameplay.
- No 4+ player runtime proof.
- No live distinct physical host proof.
- No live VM-labeled runtime causality proof.
