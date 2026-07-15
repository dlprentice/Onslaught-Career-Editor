# Transform morph timing (M1.5) — harness landed

Status: **landed** — live dual-accept `xform-p03` + Core `MorphToJetSettleTicks=148`  
Tools: `tools/battleengine_transform_timing_measurement.py`, `--measure transform`  
Contract: `walker-transform-morph-timing-v1.json`  
Policy: `walker-transform-morph-retail-to-core-translation-policy.md`

Measures latency from morph-request tick to sustained jet state (5 consecutive
state==3 samples). Live path stamps request before Transform/T handshake.
