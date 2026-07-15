# Walker-forward scalar response (v2)

Status: measured (two accepted copied-runtime attempts)  
Schema: `battleengine-walker-forward-scalar-response.v2`  
Projection: [walker-forward-scalar-response-v2.json](walker-forward-scalar-response-v2.json)

## Claim boundary

Scalar walker-forward motion response only, in **retail world coordinate units**.

Measured under:

- copied BEA only (installed Steam / original `BEA.exe` untouched)
- level 850, configuration 2
- Forward bound to Q on the safe-copy `defaultoptions.bea`
- receipt-bound process / module / HWND identity
- 10 ms QPC sampling, 2.0 s hold, 0.75 s release

## Envelope (pair p27)

| Metric | Lower | Upper | Units |
|--------|-------|-------|-------|
| Steady speed | 2.850 | 3.150 | retail-world units / second |
| Response latency | 0 | 80 | ms |
| Release latency | 0 | 140 | ms |
| Steady slope | −0.305 | −0.216 | retail-world units / s² |

Normalized response nodes at 100/200/350/500 ms stay near 1.0 after the control-proven edge (see projection JSON).

## Evidence class separation

| Class | This measurement |
|-------|------------------|
| Source hypothesis | `CBattleEngineWalkerPart::Forward` → `AddVelocity`; `Move` applies walk friction |
| Steam static | Walker control store at part+0x40; `PlatformInput__GetKeyOn` / `DAT_00888c94` |
| Copied-runtime | Two accepted attempts, steady ≈ 3.0 u/s, hold displacement ≈ 6.0 over 2 s |
| Rebuild contract | **Not yet** — requires a separate retail→Core translation policy |

## Non-claims

- No directional / camera / terrain / jet / morph parity
- No physical SI units
- No deterministic-Core constant change until translation policy is accepted
- Physics-update period (~50 ms) is inferred from position edges, not proven tick identity
- Input path for continuous Forward used focused Q/Up plus KeyDown table re-latch; this measures walker scalar response under that delivery, not every OS input stack variant

## Next gate

Accept a retail→Core translation policy covering coordinate scale, tick response, rounding, quantization error, and overflow **before** editing `OnslaughtRebuild.Core`.
