# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Existing Level100MissionTiming, RetailGameEndCountdown and InJetMode laws.
## Provenance remains in those retained comparison sources and PROVENANCE.md:
## admitted LevelScript object 73eb349b…ed6fb1, readable script d51f8864…c04a4.
## Lost is the released two-second store (0046f4a8), unlike the GPL five-second
## source. Won is five seconds except worlds 741/742. Death pause is nominal
## 15 seconds; the retail strict event edge (300 versus 301) remains unresolved.
## No event, filesystem, clock, audio or physics owner is introduced here.

const Constants = preload("res://Core/simulation_constants.gd")
const Float32 = preload("res://Core/retail_float24.gd")
const AUTHORED_TRIGGER_RADIUS_MILLIMETERS: int = 5000
const HEALTH_POLL_CADENCE_TICKS: int = Constants.TICKS_PER_SECOND
const LOST_COUNTDOWN_BITS: int = 0x40000000
const WON_COUNTDOWN_BITS: int = 0x40a00000
const SUCCESS_COUNTDOWN_TICKS: int = 5 * Constants.TICKS_PER_SECOND
const FAILURE_COUNTDOWN_TICKS: int = 2 * Constants.TICKS_PER_SECOND
@warning_ignore("integer_division")
const FAILURE_MENU_DELAY_TICKS: int = Constants.TICKS_PER_SECOND / 2
const DEATH_PAUSE_DELAY_TICKS: int = 15 * Constants.TICKS_PER_SECOND
const DEATH_GAMEPLAY_FADE_STEP_BITS: int = 0x3b449ba6
@warning_ignore("integer_division")
const GROUND_CONTACT_RECENCY_TICKS: int = Constants.TICKS_PER_SECOND / 2
@warning_ignore("integer_division")
const RELEASED_EVENT_FRAME_TICKS: int = (Constants.TICKS_PER_SECOND + Constants.RETAIL_TICKS_PER_SECOND - 1) / Constants.RETAIL_TICKS_PER_SECOND
const MESSAGE_BOX_ALLOWED_TICK: int = Constants.LEVEL100_OPENING_PAN_TICKS + RELEASED_EVENT_FRAME_TICKS
@warning_ignore("integer_division")
const MESSAGE_ADVANCE_DELAY_TICKS: int = Constants.TICKS_PER_SECOND / 5
const IN_JET_MODE_HANDLER_ADDRESS: int = 0x005380f0
const RECENTLY_GROUNDED_WALKER_ADDRESS: int = 0x00408120
const BATTLE_ENGINE_TYPE_BIT: int = 8


static func failure_terminal_ticks(reason: Variant) -> Dictionary:
	if not _i32(reason):
		return _carrier("reason")
	match reason:
		1: return _success(FAILURE_COUNTDOWN_TICKS)
		2, 3: return _success(DEATH_PAUSE_DELAY_TICKS)
		_: return _failure("ArgumentOutOfRangeException", "reason")


static func failure_overlay_ticks_remaining(reason: Variant, terminal_ticks_remaining: Variant) -> Dictionary:
	if not _i32(reason) or not _i32(terminal_ticks_remaining):
		return _carrier("reason/terminalTicksRemaining")
	# Negative remaining time is rejected before the reason switch.
	if terminal_ticks_remaining < 0:
		return _failure("ArgumentOutOfRangeException", "terminalTicksRemaining")
	var terminal: Dictionary = failure_terminal_ticks(reason)
	if not terminal.ok:
		return terminal
	return _success(clampi(terminal_ticks_remaining - (terminal.value - FAILURE_COUNTDOWN_TICKS), 0, FAILURE_COUNTDOWN_TICKS))


static func gameplay_paused(outcome: Variant, reason: Variant, terminal_ticks_remaining: Variant) -> Dictionary:
	if not _i32(outcome) or not _i32(reason) or not _i32(terminal_ticks_remaining):
		return _carrier("outcome/reason/terminalTicksRemaining")
	return _success(outcome == 2 and (reason == 1 or (reason in [2, 3] and terminal_ticks_remaining == 0)))


static func gameplay_pauses_on_next_tick(outcome: Variant, reason: Variant, terminal_ticks_remaining: Variant) -> Dictionary:
	var paused: Dictionary = gameplay_paused(outcome, reason, terminal_ticks_remaining)
	if not paused.ok:
		return paused
	return _success(paused.value or (outcome == 2 and reason in [2, 3] and terminal_ticks_remaining == 1))


static func gameplay_mix(outcome: Variant, reason: Variant, terminal_ticks_remaining: Variant) -> Dictionary:
	if not _i32(outcome) or not _i32(reason) or not _i32(terminal_ticks_remaining):
		return _carrier("outcome/reason/terminalTicksRemaining")
	var mix: float = 1.0
	if outcome == 2 and reason in [2, 3]:
		var elapsed: int = clampi(_wrap_i32(DEATH_PAUSE_DELAY_TICKS - terminal_ticks_remaining), 0, DEATH_PAUSE_DELAY_TICKS)
		var step: float = Float32.read_word(DEATH_GAMEPLAY_FADE_STEP_BITS)
		for tick: int in range(elapsed):
			# Repeated float subtraction is observable; 1-elapsed*step differs.
			mix = Float32.read_word(Float32.store_word(mix - step))
	return {"ok": true, "bits": Float32.store_word(mix)}


static func trigger_position(trigger: Variant) -> Dictionary:
	if not _i32(trigger):
		return _carrier("trigger")
	match trigger:
		1: return _success(Constants.LEVEL100_TARGET_ZONE1_POSITION.duplicate())
		2: return _success(Constants.LEVEL100_FIRING_RANGE_POSITION.duplicate())
		3: return _success({"x": -56688, "z": -62250})
		4: return _success({"x": -57938, "z": 2625})
		5: return _success({"x": 0, "z": -31})
		_: return _failure("ArgumentOutOfRangeException", "trigger")


static func requires_not_in_jet_mode(trigger: Variant) -> Dictionary:
	return _success(trigger in [3, 4, 5]) if _i32(trigger) else _carrier("trigger")


static func jet_mode_state(mode: Variant, transition: Variant, ticks_since_ground_contact: Variant) -> Dictionary:
	if not _i32(mode) or not _i32(transition) or not _i32(ticks_since_ground_contact):
		return _carrier("mode/transition/ticksSinceGroundContact")
	# This is the negation of a recently grounded walker, not mode==Jet.
	return _success(0 if mode == 0 and transition == 0 and ticks_since_ground_contact < GROUND_CONTACT_RECENCY_TICKS else 1)


static func iscript_in_jet_mode(thing_type_mask: Variant, mode: Variant, transition: Variant, ticks_since_ground_contact: Variant) -> Dictionary:
	if not _u32(thing_type_mask) or not _i32(mode) or not _i32(transition) or not _i32(ticks_since_ground_contact):
		return _carrier("thingTypeMask/mode/transition/ticksSinceGroundContact")
	return _success((thing_type_mask & BATTLE_ENGINE_TYPE_BIT) != 0 and jet_mode_state(mode, transition, ticks_since_ground_contact).value == 1)


static func pause_ticks(seconds_bits: Variant) -> Dictionary:
	if not _u32(seconds_bits):
		return _carrier("secondsBits")
	var seconds: float = Float32.read_word(seconds_bits)
	if not is_finite(seconds) or seconds < 0.0:
		return _failure("InvalidOperationException", "", "The released LevelScript requested an invalid pause.")
	var product: float = Float32.read_word(Float32.store_word(seconds * float(Constants.TICKS_PER_SECOND)))
	var rounded: float = floor(product + 0.5)
	if not is_finite(rounded) or rounded < -2147483648.0 or rounded >= 2147483648.0:
		return _failure("OverflowException")
	return _success(int(rounded))


static func uses_zero_won_countdown(world_id: Variant) -> Dictionary:
	return _success(world_id == 741 or world_id == 742) if _i32(world_id) else _carrier("worldId")


static func message_playback_ticks(message_id: Variant) -> Dictionary:
	if not _i32(message_id):
		return _carrier("messageId")
	if MESSAGE_PLAYBACK_TICKS.has(message_id):
		return _success(MESSAGE_PLAYBACK_TICKS[message_id])
	return _failure("InvalidOperationException", "", "Released Level 100 message id %d has no evidenced wait duration." % message_id)


static func _success(value: Variant) -> Dictionary:
	return {"ok": true, "value": value}


static func _failure(kind: String, parameter: String = "", message: String = "") -> Dictionary:
	return {"ok": false, "error_type": kind, "parameter": parameter, "error": message}


static func _carrier(parameter: String) -> Dictionary:
	return _failure("ArgumentException", parameter, "A typed integer carrier is required.")


static func _i32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


static func _u32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= 0 and value <= 0xffffffff


static func _wrap_i32(value: int) -> int:
	var word: int = value & 0xffffffff
	return word - 0x100000000 if word > 0x7fffffff else word


# Shipped Ogg granules at 20 Hz plus the existing 12.02-tick overhead, carried
# unchanged from Level100MissionTiming.MessagePlaybackTicks. These are whole
# on-screen durations, not a post-roll to subtract. The remaining ~0.1-second
# residual beyond the two explained waits is still unidentified. Only the
# already admitted World 110 message is included; no new route is inferred.
const MESSAGE_PLAYBACK_TICKS: Dictionary = {
	8444036: 90, # _110_PROTECT
	292562: 113, # HUD_01
	293386: 140, # HUD_02
	294210: 176, # HUD_03
	295034: 176, # HUD_04
	295858: 174, # HUD_05  (knife-edge: 12.00 would give 173)
	296682: 122, # HUD_06
	297506: 157, # HUD_07
	-1575499396: 109, # TUTORIAL_MESSAGE_LOG
	-257967449: 44, # TUTORIAL_TECHNICIAN_01 (knife-edge: 12.00 -> 43)
	82987417: 143, # TUTORIAL_13_MOD
	4422830: 106, # TUTORIAL_01
	175347826: 92, # TUTORIAL_SCANNER
	4458134: 120, # TUTORIAL_02
	4493438: 65, # TUTORIAL_03
	1339691000: 147, # TUTORIAL_PULSE_CANNON
	669198996: 75, # TUTORIAL_OPEN_FIRE
	-1715818922: 162, # TUTORIAL_PULSE_CANNON_2
	-1616775312: 159, # TUTORIAL_VULCAN_CANNON
	-1860407443: 81, # TUTORIAL_OPEN_FIRE_2
	864965454: 121, # TUTORIAL_VULCAN_CANNON_2
	4564046: 187, # TUTORIAL_05
	22775962: 127, # TUTORIAL_ZOOM
	667656903: 134, # TUTORIAL_DODGE_MOD
	150647733: 110, # TUTORIAL_DODGE_2
	151778876: 163, # TUTORIAL_DODGE_3
	623538785: 91, # TUTORIAL_DODGE_BAD
	1326027769: 86, # TUTORIAL_DODGE_GOOD
	4528742: 175, # TUTORIAL_04
	165861931: 152, # TUTORIAL_LANDING
	4599350: 151, # TUTORIAL_06
	1062059777: 87, # TUTORIAL_THROTTLE_MOD
	4475837: 89, # TUTORIAL_12
	4705262: 142, # TUTORIAL_09
	4634654: 112, # TUTORIAL_07
	80260569: 132, # TUTORIAL_STRAFE
	4669958: 151, # TUTORIAL_08
	4440532: 150, # TUTORIAL_11
	162342028: 112, # TUTORIAL_ABORTED
	150940633: 73, # TUTORIAL_BROKE_1
	152071864: 81, # TUTORIAL_BROKE_2
	153203095: 85, # TUTORIAL_BROKE_3
	-1455850811: 76, # TUTORIAL_HELP_PLAYER
	4405227: 133, # TUTORIAL_10
}
