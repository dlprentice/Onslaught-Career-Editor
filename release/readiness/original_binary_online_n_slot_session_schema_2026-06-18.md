# Original Binary Online N-Slot Session Schema Readiness Note

Status: complete public-safe N-slot session schema proof
Date: 2026-06-18
Scope: `original-binary-online-n-slot-session-schema`

This slice makes the online multiplayer lane slot-general at the session/schema level while preserving the original-binary runtime boundary. It does not launch BEA, does not send game input, does not mutate any executable, does not mutate Ghidra, and does not touch the installed Steam folder.

## Accepted Schema

The public-safe schema proof is:

```text
roadmap\original-binary-online-n-slot-session-schema.v1.json
```

The schema records:

- schema `winui-original-binary-online-n-slot-session-schema.v1`
- session schema `winui-original-binary-host-authority-n-slot-session.v1`
- protocol `host-authority-n-slot-input.v1`
- `slotCapacity=4`
- `acceptedSessionParticipantCount=4`
- `originalBinaryPlayerSlotsProven=P1,P2`
- `maxOriginalBinaryActiveSlots=2`
- `maxRetailPlayersProven=2`
- `retailSlotsProven=P1,P2`
- `retailViewpointsProven=2`
- `moreThanTwoOriginalBinaryRuntimeProofSlices=0`
- `nPlayerOriginalBinaryRuntimeProof=0`
- `coOpVersusModeRuntimeProofSlices=0`
- `nativeBeaNetcodeProofSlices=0`
- `P1/P2` active original-binary routes only
- `P3/P4 metadata-only` session participants
- `unsupported-original-binary-active-slot` runtime route for `P3/P4`
- extra-slot rejection policy `required-for-unproven-original-binary-slots`
- `rejectedOriginalBinaryGameplayCommandCount=2`
- schema rejection case `missing-relayPlanHash`
- deterministic participant order `P1`, `P2`, `P3`, `P4`
- deterministic original-binary relay order `P1`, `P2`
- planned mode profiles `cooperative`, `versus-free-for-all`, `team-versus`, and `spectator-admin`

The checker requires `P3/P4` to be admitted as session participants while rejecting their original-binary gameplay commands. That proves the host-authority session model is not hardcoded to two participants, without claiming the copied retail executable can run more than two active players.

Security/protocol checks require pinned slot identity, ephemeral credentials, session-scoped HMAC fields, replay-cache and sequence enforcement, max message bytes, unknown-field rejection, `publicBind=false`, and operator secrets outside git.

## Commands

```powershell
py -3 tools\winui_safe_copy_online_n_slot_session_schema_check.py --check
py -3 tools\winui_safe_copy_online_n_slot_session_schema_check.py --self-test
npm run test:winui-original-binary-online-n-slot-session-schema
```

## Boundary

This is not a BEA launch/capture/stop run, not runtime proof for more than two original-binary players, not co-op mode proof, not versus mode proof, not team-versus proof, not multi-host LAN play, not public matchmaking, not native BEA netcode, not deterministic sync, not rollback, not anti-cheat, not physical gamepad behavior, not rebuild parity, and not no-noticeable-difference online parity.

No Ghidra backup was created because no Ghidra mutation occurred. The latest verified Ghidra review backup remains Wave1219 backup id `BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`; exact local backup roots stay in private state/evidence.
