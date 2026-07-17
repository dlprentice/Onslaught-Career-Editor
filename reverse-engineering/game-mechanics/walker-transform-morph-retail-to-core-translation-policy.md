# Walker morph-to-jet settle observation

Status: measured retail observation; Core mapping not accepted
Evidence: `walker-transform-morph-timing.v1` pair xform-p03

The captured midpoint from morph input to the measured settle condition is
approximately 4.92 seconds, or 148 ticks at Core's 30 Hz rate. This conversion
is arithmetic only. The capture's settle condition has not yet been mapped to
specific retail transition states, input lock, animation completion, control
handoff, or Core fields.

Do not map 148 directly to `TransformDurationTicks`. The current 15-tick Core
lock is synthetic. A future implementation must first identify the retail
transition phases in source/static evidence and compare a matching input
sequence before choosing which state, if any, owns the measured interval.
