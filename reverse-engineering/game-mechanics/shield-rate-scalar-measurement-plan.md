# Shield regen/drain scalar plan

Status: **closed blocked after two capped live observations**; no accepted
pair, measured value, or behavior contract accepted
Scaffold: `tools/battleengine_shield_scaffold.py`
Live command: `--measure shield --vehicle walker`

## Steam-static shields offset

| Field | Candidate offset | Evidence class |
|-------|------------------|----------------|
| Current shields float | `BattleEngine+0x100` | Steam static (walker recharge mirror) |
| Current energy float | `BattleEngine+0xFC` | paired with shields mirror |

Walker recharge decompile (after energy update) writes shields at
`main+0x100` from the energy path (source `mShields=mEnergy` in walker).
Jet mode source zeros shields.

Sampler constant: `BATTLE_ENGINE_SHIELDS_OFFSET = 0x100`. The live mode records
paired energy/shield fields under receipt and foreground guards without owning
Q input or invoking motion/velocity acceptance. It enforces the full QPC phase
schedule, walker state, and neutral control on every sample. Its deterministic
scaffold requires symmetric positive correlation over the union of active
energy/shield edges and rejects any material wrong-direction edge in the
no-damage setup. Its pair producer requires attempts 1 and 2 with fresh
receipt/run digests. The cleanup owner records input as not owned and never
sends backup Q for shield, including on failure. This readiness is not runtime
proof.

## Capped live closeout

On 2026-07-15, exactly two separately closed, receipt-bound copied-runtime
observations ran after the focused sampler, measurement-orchestrator, and
shield-scaffold gates passed 30/30, 45/45, and 18/18. Both attempts reached
`ready` in walker mode under the neutral, input-free protocol. Both then failed
closed at the same acceptance gate: each produced zero active shield edges,
below the required five. The canonical pair producer did not accept or
materialize a pair, and no rate or public projection was accepted.

Both copied targets and their source inputs retained their before-run hashes;
the observer handles and managed processes closed, and the final owned-process
census was zero. The installed game and original executable were not mutated.
The two-attempt cap is exhausted: do not publish a shield behavior contract,
infer a retail rate from the source mirror, map a value into Core, or run a
third attempt under this authorization. A future measurement would require an
explicitly reopened slice with a materially revised protocol and fresh
authority.
