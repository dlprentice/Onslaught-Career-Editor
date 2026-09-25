# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## The scripted First Flight smoke input, per simulation tick.
##
## Begin after each objective is active, then follow the bounded left/forward
## routes used by the copied-retail observer. Each forward hold stops at Core's
## trigger. The final fixed yaw and four-shot sequence exercises the bounded
## full-hit lifecycle demonstrated against retail Target Tank 1.
##
## Re-flown for the 20 Hz migration, not rescaled: every leg was re-measured by
## flying candidate tapes and reading the objective timeline, and the observables
## the smoke gates on were checked against the 30 Hz run (Walker mode, zero
## targets destroyed, Target Tank 1 alive at 6,000 hull, four fire-held ticks,
## pulse enabled, Vulcan and flight disabled, one help message). The route starts
## walking at 708, before the first-run LevelScript makes Target Zone 1 the
## objective at 812; the trigger is a volume, so walking early costs nothing.
##
## DURATION_TICKS is 2148, not the faithful two-thirds 2152 of the 30 Hz 3228:
## the report samples three audio-mixer fields that advance in wall-clock time,
## and the gate's "playback available implies playing message" implication only
## holds while the schedule shows nothing. 2148 sits in the quiet window after
## TUTORIAL_OPEN_FIRE clears (2143) and before TUTORIAL_PULSE_CANNON_2 (2150);
## it also returns the delivered message count to 13 (2152 delivered 14).

const InteractiveInput = preload("res://Client/interactive_input.gd")

const TARGET_ZONE_INPUT_START_TICK: int = 708
const LEFT_TICKS: int = 144
const FORWARD_TICKS: int = 313
const FIRING_RANGE_INPUT_START_TICK: int = 1_330
const FIRING_RANGE_LEFT_TICKS: int = 30
const FIRING_RANGE_FORWARD_TICKS: int = 306
const PULSE_CANNON_PROOF_TICKS: Array[int] = [2_104, 2_109, 2_115, 2_123]
const DURATION_TICKS: int = 2_148


## Returns {ok, value: InteractiveInput record}; a negative tick is refused.
static func input_for_tick(tick: int) -> Dictionary:
	if tick < 0:
		return {"ok": false, "error_type": "ArgumentOutOfRangeException", "error": "tick"}
	if tick < TARGET_ZONE_INPUT_START_TICK:
		return {"ok": true, "value": InteractiveInput.idle()}
	var route_tick: int = tick - TARGET_ZONE_INPUT_START_TICK
	if route_tick < LEFT_TICKS:
		return InteractiveInput.create(-1, 0, false, false, false)
	if route_tick < LEFT_TICKS + FORWARD_TICKS:
		return InteractiveInput.create(0, 1, false, false, false)
	if tick >= FIRING_RANGE_INPUT_START_TICK and tick < FIRING_RANGE_INPUT_START_TICK + FIRING_RANGE_LEFT_TICKS:
		return InteractiveInput.create(-1, 0, false, false, false)
	var forward_start: int = FIRING_RANGE_INPUT_START_TICK + FIRING_RANGE_LEFT_TICKS
	if tick >= forward_start and tick < forward_start + FIRING_RANGE_FORWARD_TICKS:
		return InteractiveInput.create(0, 1, false, false, false)
	var look: int = 0
	if tick >= 2_093 and tick <= 2_097:
		look = -1
	elif tick in [2_099, 2_103, 2_122]:
		look = 1
	elif tick == 2_120:
		look = -1
	if look != 0:
		return InteractiveInput.create(0, 0, false, false, false, look)
	if tick in PULSE_CANNON_PROOF_TICKS:
		return InteractiveInput.create(0, 0, true, false, false)
	return {"ok": true, "value": InteractiveInput.idle()}
