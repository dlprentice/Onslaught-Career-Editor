# Original Binary Host-Authority N-Slot Session-Security Smoke Readiness Note

Status: complete bounded same-workstation session-security message-layer proof
Date: 2026-06-19
Scope: `original-binary-host-authority-n-slot-session-security-smoke`

This slice adds a sibling proof class for the original-binary online ladder: `winui-original-binary-host-authority-n-slot-session-security-smoke.v1`. It does not replace the sequential or concurrent N-slot process smokes. It proves strict host-authority message-layer rejection behavior in an in-memory same-workstation harness while preserving the original-binary runtime boundary at P1/P2.

Accepted private artifact:

| Field | Value |
| --- | --- |
| Artifact class | release-excluded `subagents/` proof bundle |
| Artifact SHA-256 | `4976d01e2bc6f0c4f7f7af58c0c6a9d68e7401c6319b0bbc9eb6b2c358d9c6be` |
| Schema | `winui-original-binary-host-authority-n-slot-session-security-smoke.v1` |
| Protocol | `host-authority-n-slot-input.v1` |
| Security scope | `securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof` |
| Session MAC proof | `sessionScopedMacCoverageProof=true`; `sessionScopedMacCoverageMode=canonical-json-message-excluding-mac`; `sessionScopedMacFieldSensitivityProof=true`; `tickBoundMacFieldsProof=true`; `relayPlanHashMacBound=true` |
| Schema/size proof | `maxJsonLineBytesEnforced=true`; `rawJsonLineByteLimitRejected=true`; `maxJsonLineBytes=4096`; `unknownFieldRejectionProof=true`; `strictMessageSchemaProof=true` |
| Accepted gameplay commands | `acceptedOriginalBinaryGameplayCommandCount=2`; P1/P2 only |
| Metadata gameplay rejections | `metadataGameplayRejectionCount=2`; P3/P4 rejected with `required-for-unproven-original-binary-slots` |
| Security rejection cases | `rejectedSecurityCaseCount=25` |
| Relay hash | `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002` |
| Runtime boundary | `newBeaLaunchCount=0`; `cdbAttachCount=0`; `hostHelperInputSent=false`; `gameInputSentByNSlotScheduler=false` |

The accepted security rejection matrix covers:

- `unknown-field`
- `oversized-message`
- `stale-tick`
- `future-tick`
- `replay-nonce`
- `missing-relayPlanHash`
- `relayPlanHash-mismatch`
- `bad-session-mac`
- `bad-slot-credential`
- `slot-identity-mismatch`
- `slot-changed-on-connection`
- `command-before-session`
- `duplicate-session-on-connection`
- `sequence-not-next`
- `slot-rate-limit`
- `tick-rate-limit`
- `missing-required-field`
- `wrong-field-type`
- `public-matchmaking-not-allowed`
- `direct-input-not-allowed`
- `server-identity-mismatch`
- `unknown-slot`
- `invalid-team-assignment`
- `duplicate-slot-identity`
- `duplicate-client-identity`

What this proves:

- The N-slot host-authority message harness enforces a 4096-byte raw JSON line ceiling before accepting messages (`jsonLineByteMode=raw-line-before-json-parse`; observed oversized row `rawJsonLineBytes=4790`).
- Strict allowlists reject unknown fields and missing or wrong-typed required fields.
- Session-scoped HMAC signs the canonical JSON message excluding only `mac`; `sessionHelloMacFields` and `commandMacFields` are recorded separately, and `macFieldSensitivityCases` proves every listed field changes the HMAC input when mutated.
- Nonce replay, stale/future ticks, sequence gaps, wrong relay hashes, wrong MACs, wrong credentials, and slot identity mismatches are rejected.
- P1/P2 remain the only accepted original-binary gameplay routes.
- P3/P4 are still metadata-only and rejected for original-binary gameplay.
- Public-matchmaking and direct-input claims are rejected at the protocol layer.

What this does not prove:

- `nPlayerOriginalBinaryRuntimeProof=0`.
- `activeP3P4OriginalBinaryGameplayProof=false`.
- This does not prove active P3/P4 original-binary gameplay.
- This does not prove more than two original-binary runtime players.
- This does not prove co-op/versus runtime semantics.
- This does not prove multi-host LAN play.
- This does not prove public matchmaking.
- This does not prove native BEA netcode.
- This does not prove deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

Validation:

- `py -3 tools\winui_safe_copy_online_host_authority_n_slot_session_security_smoke_check_test.py`
- `py -3 tools\winui_safe_copy_online_host_authority_n_slot_session_security_smoke_check.py --self-test`
- `py -3 tools\build_winui_original_binary_host_authority_n_slot_session_security_smoke_bundle.py --output subagents\winui-original-binary-online\n-slot-session-security-smoke-2026-06-19\host-authority-n-slot-session-security-smoke-proof.json`
- `py -3 tools\winui_safe_copy_online_host_authority_n_slot_session_security_smoke_check.py subagents\winui-original-binary-online\n-slot-session-security-smoke-2026-06-19\host-authority-n-slot-session-security-smoke-proof.json`

No Ghidra mutation, no Ghidra backup, no executable-byte mutation, no BEA launch, no CDB attach, no copied-game input, and no Steam install change occurred in this slice.
