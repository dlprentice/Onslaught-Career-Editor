# Transform morph timing (M1.5) — harness landed

Status: **harness landed** (offline unit-tested); live dual-accept pending  
Tools: `tools/battleengine_transform_timing_measurement.py`  
Tests: `tools/battleengine_transform_timing_measurement_test.py`

Measures latency from morph-request tick to sustained jet state (5 consecutive
state==3 samples). Live pair can feed state series from the existing morph
handshake path.
