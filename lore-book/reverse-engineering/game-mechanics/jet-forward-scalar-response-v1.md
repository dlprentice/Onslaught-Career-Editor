# Jet-forward scalar thrust response (v1)

Status: measured (two accepted copied-runtime attempts)  
Schema: `battleengine-jet-forward-scalar-response.v1`  
Projection: [jet-forward-scalar-response-v1.json](jet-forward-scalar-response-v1.json)  
Private evidence label: `jet-p06` (compact under ignored `local-proofs/wt/`)

## Claim boundary

Scalar **jet-mode** forward/thrust motion response only, in **retail world
coordinate units**.

Measured under:

- copied BEA only (installed Steam / original `BEA.exe` untouched)
- level 850, configuration 2
- Transform/morph bound to T; Forward bound to Q on the safe-copy
  `defaultoptions.bea`
- harness morph handshake until vehicle state raw `3` (jet)
- receipt-bound process / module / HWND identity
- 10 ms QPC sampling, 2.0 s hold, 0.75 s release
- mid-hold steady window (jet thrust peaks then may collapse late)

## Envelope (pair jet-p06)

| Metric | Lower | Upper | Units |
|--------|-------|-------|-------|
| Steady speed | 10.860 | 12.003 | retail-world units / second |
| Response latency | 0 | 100 | ms |
| Release latency | 0 | 90 | ms |

Per-attempt mid-hold cruise was ≈ **11.431** u/s on both accepts (relative
speed delta ≪ 0.01%). Response-latency midpoints differ more than walker
because the threshold is relative to residual thruster cruise, not near-static
baseline.

## Evidence class separation

| Class | This measurement |
|-------|------------------|
| Source hypothesis | Jet part forward/thrust path; morph gate to jet state |
| Steam static | Jet control / state chain offsets used by the sampler |
| Copied-runtime | Two accepted attempts, mid-hold steady ≈ 11.43 u/s |
| Rebuild contract | Separate retail→Core translation policy required |

## Non-claims

- No walker, terrain, turning, or full vehicle parity
- No morph dynamics characterization beyond state-gate setup
- No physical SI units
- No deterministic-Core constant until translation policy is accepted
- Physics-update period (~50 ms) is inferred from position edges
- Late-hold collapse is excluded from the steady window

## Next gate

Accept
[jet-forward-retail-to-core-translation-policy.md](jet-forward-retail-to-core-translation-policy.md)
before editing `JetSpeedPerTick` in Core.
