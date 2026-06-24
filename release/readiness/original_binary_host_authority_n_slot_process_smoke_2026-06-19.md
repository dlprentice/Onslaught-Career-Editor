# Original Binary Host-Authority N-Slot Process Smoke Readiness Note

Status: complete bounded process/scheduler proof
Date: 2026-06-19
Scope: `original-binary-host-authority-n-slot-process-smoke`

This slice adds one same-workstation sequential four-client N-slot process smoke for the original-binary online feasibility ladder. It does not launch BEA, does not attach CDB, does not patch any executable, and does not mutate the installed Steam game. The accepted private proof bundle was generated under the ignored `subagents/` evidence root by `tools\build_winui_original_binary_host_authority_n_slot_process_smoke_bundle.py` and validated by `tools\winui_safe_copy_online_host_authority_n_slot_process_smoke_check.py`.

## Accepted Evidence

- Schema: `winui-original-binary-host-authority-n-slot-process-smoke.v1`
- Protocol: `host-authority-n-slot-input.v1`
- Transport: `host-authority-n-slot-tcp-jsonl-process-smoke`
- Process model: `four-separate-python-client-processes`
- `processConcurrencyModel=sequential-distinct-client-processes`
- `simultaneousClientProcessesProven=1`
- `clientProcessCount=4`
- `clientProcessIdsDistinctFromBuilder=true`
- `clientProcessIdsDistinctFromEachOther=true`
- `credentialTransportToClientProcesses=stdin-ephemeral-not-serialized-to-artifact`
- `clientEnvSensitiveKeyCount=0`
- `slotCapacity=4`
- `acceptedSessionParticipantCount=4`
- `arrivalOrder=P4,P2,P3,P1`
- `deterministicParticipantOrder=P1,P2,P3,P4`
- `deterministicOriginalBinaryRelayOrder=P1,P2`
- `acceptedOriginalBinaryGameplaySlots=P1,P2`
- `metadataOnlySlots=P3,P4`
- `rejectedGameplayRouteSlots=P3,P4`
- `acceptedOriginalBinaryGameplayCommandCount=2`
- `rejectedOriginalBinaryGameplayCommandCount=2`
- `extraSlotRejectionPolicy=required-for-unproven-original-binary-slots`
- N-slot relay hash: `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002`
- Runtime-compatible P1/P2 relay hash: `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`
- `gameInputSentByNSlotScheduler=false`
- `hostHelperInputSent=false`
- `newBeaLaunchCount=0`
- `cdbAttachCount=0`
- `nPlayerOriginalBinaryRuntimeProof=0`
- `activeP3P4OriginalBinaryGameplayProof=false`
- `permanentImpossibilityClaim=false`

## Boundary

This proves that four slot-scoped client processes can participate sequentially in the host-authority scheduler/process layer while only P1/P2 enter the original-binary relay plan. It does not prove four concurrent client processes, does not prove active P3/P4 original-binary gameplay, does not prove multi-host LAN play, does not prove public matchmaking, does not prove native BEA netcode, does not prove co-op/versus runtime semantics, does not prove deterministic sync, does not prove rollback, does not prove anti-cheat, does not prove physical gamepad behavior, does not prove rebuild parity, and does not prove no-noticeable-difference online parity.

## Validation

- `py -3 tools\winui_safe_copy_online_host_authority_n_slot_process_smoke_check.py --self-test`
- `py -3 tools\winui_safe_copy_online_host_authority_n_slot_process_smoke_check.py subagents\winui-safe-copy-live-runtime\online-host-authority-n-slot-process-smoke-20260619-focus1\host-authority-n-slot-process-smoke-proof.json`
- `npm run test:winui-original-binary-host-authority-n-slot-process-smoke`
