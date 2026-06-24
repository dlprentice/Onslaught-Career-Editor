# WinUI Control Causality Contract Readiness Note

Status: complete public-safe aggregate validation
Date: 2026-06-19
Scope: `winui-control-causality-contract`

`tools/winui_control_causality_contract_check.py --check` validates `schema=winui-control-causality-contract.v1` over already accepted ignored exact-PID level-850 copied-runtime artifacts. It performs no BEA launch, no CDB attach, no Ghidra mutation, no executable-byte change, no installed-game mutation, and no original `BEA.exe` mutation.

Accepted aggregate:

| Field | Value |
| --- | --- |
| Movement-state causality artifacts | `7` |
| Movement-state controller configurations | `1, 2, 3, 4` |
| Visible movement causality artifacts | `4` |
| Visible movement controller configurations | `1, 2` |
| CDB correlation model | `cdb-byte-window-ordered-correlation` |
| Wall-clock latency proven | `false` |
| New BEA launches | `0` |
| New CDB attaches | `0` |

Machine-checked claims:

- `waitWindowsClean=true`
- `inputWindowButton31ReceiveRowsPositive=true`
- `inputWindowForwardStateStoreRowsPositive=true`
- `inputWindowOrderedSendReceiveStateStore=true`
- `wallClockLatencyProven=false`
- `movementStateTargetDiffersFromAdjacentBaseline=true`
- `visibleSubsetOnly=true`
- `acceptedOriginalBinaryGameplaySlots=P1,P2`
- `metadataOnlySlots=P3,P4`
- `rejectedGameplayRouteSlots=P3,P4`
- `gameInputSentByNSlotScheduler=false`
- `hostHelperInputSent=false`
- `nPlayerOriginalBinaryRuntimeProof=0`
- `activeP3P4OriginalBinaryGameplayProof=false`
- `controlFeelImprovementProof=false`
- `physicalGamepadProof=false`

Proof boundary:

This contract revalidates existing exact-PID level-850 copied-runtime artifacts and proves a bounded keyboard-input-to-CDB-state/render-window causality chain for Movement/Forward across controller configs `1-4`, with a stricter visible movement subset for configs `1-2`. The ordering proof is CDB byte-window correlation only: controller send occurs before player receive, and player receive occurs before the matching nonzero WalkerPart/JetPart state-store row inside the same scoped input window.

This is not improved control-feel proof, not physical gamepad proof, not wall-clock latency proof, not true online multiplayer proof, not multi-host LAN proof, not public matchmaking proof, not native BEA netcode proof, not active P3/P4 original-binary gameplay proof, not deterministic sync proof, not broad controller coverage proof, not rebuild parity, and not no-noticeable-difference proof.
