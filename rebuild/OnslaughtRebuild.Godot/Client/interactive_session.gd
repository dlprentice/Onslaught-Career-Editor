# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Real-time adapter port of Client/InteractiveSession.cs: held levels, queued
## edges and pulses, whole-pixel pointer easing, pause/focus suspension, the
## fixed-step phase accumulator and metrics. Each 20 Hz step hands its exact
## consumed input to the C# simulation bridge (Bridge/SimulationBridge.cs), which
## owns Core, recording and hashing. The platform-input owner is borrowed.
## Mutating calls return {ok} or an explicit C# exception type and message.

const SimInput = preload("res://Core/sim_input.gd")
const InteractiveInput = preload("res://Client/interactive_input.gd")

const PHASE_UNITS_PER_STEP: int = 10_000_000
const MAXIMUM_FRAME_ELAPSED_TICKS: int = 2_500_000
const TICKS_PER_SECOND: int = 20
const POINTER_OFFSET_SCALE: int = 1_000
const POINTER_OFFSET_RETENTION_NUMERATOR: int = 10
const POINTER_OFFSET_RETENTION_DENOMINATOR: int = 17
const DEFAULT_POINTER_AXIS_NUMERATOR: int = 91
const POINTER_AXIS_DENOMINATOR: int = 3_000
const POINTER_AXIS_PER_SENSITIVITY_NUMERATOR: int = 13
const MAXIMUM_POINTER_OFFSET_MILLI_PIXELS: int = 1_000_000
const PAUSE_AUTHENTIC_MENU: int = 1

var _bridge: RefCounted
var _platform_input: RefCounted
var _input: Dictionary = InteractiveInput.idle()
var _toggle_edge_pending: bool = false
var _reset_edge_pending: bool = false
var _fire_pulse_pending: bool = false
var _skip_panning_edge_pending: bool = false
var _change_weapon_edge_pending: bool = false
var _zoom_in_edge_pending: bool = false
var _zoom_out_edge_pending: bool = false
var _movement_pulse_x: int = 0
var _movement_pulse_z: int = 0
var _look_pulse_x: int = 0
var _look_pulse_y: int = 0
var _pointer_offset_x_milli_pixels: int = 0
var _pointer_offset_y_milli_pixels: int = 0
var _pointer_axis_numerator: int = DEFAULT_POINTER_AXIS_NUMERATOR
var _pause_reasons: int = 0
var _input_suspended_until_released: bool = false
var _interpolation_phase: int = 0
var _total_steps: int = 0
var _toggle_edges_consumed: int = 0
var _reset_edges_consumed: int = 0
var _fire_held_ticks_sampled: int = 0
var _fire_pulse_edges_consumed: int = 0
var _change_weapon_edges_consumed: int = 0
var _movement_pulse_edges_consumed: int = 0
var _capped_frame_count: int = 0
var _dropped_elapsed_ticks: int = 0
var _f32 := PackedFloat32Array([0.0])


## The platform input owner is borrowed; the caller keeps and releases it.
func _init(bridge: RefCounted, platform_input: RefCounted) -> void:
	_bridge = bridge
	_platform_input = platform_input


## Starts the bridge's Level 100 simulation from verified manifest bytes.
func start(seed: int, manifest_bytes: PackedByteArray) -> Dictionary:
	return _bridge.Start(seed, manifest_bytes)


func bridge() -> RefCounted:
	return _bridge


func platform_input() -> RefCounted:
	return _platform_input


func is_paused() -> bool:
	return _pause_reasons != 0


func is_authentic_menu_paused() -> bool:
	return (_pause_reasons & PAUSE_AUTHENTIC_MENU) != 0


func input_suspended_until_released() -> bool:
	return _input_suspended_until_released


func interpolation_phase() -> int:
	return _interpolation_phase


func has_held_or_pending_input() -> bool:
	return _input != InteractiveInput.idle() or _toggle_edge_pending or _reset_edge_pending \
		or _fire_pulse_pending or _skip_panning_edge_pending or _change_weapon_edge_pending \
		or _zoom_in_edge_pending or _zoom_out_edge_pending or _movement_pulse_x != 0 \
		or _movement_pulse_z != 0 or _look_pulse_x != 0 or _look_pulse_y != 0 \
		or _pointer_offset_x_milli_pixels != 0 or _pointer_offset_y_milli_pixels != 0 \
		or _input.look_x != 0 or _input.look_y != 0


## InteractiveSessionMetrics; ResetGeneration mirrors the reset edge count.
func metrics() -> Dictionary:
	return {"total_steps": _total_steps, "toggle_edges_consumed": _toggle_edges_consumed,
		"reset_edges_consumed": _reset_edges_consumed, "reset_generation": _reset_edges_consumed,
		"fire_held_ticks_sampled": _fire_held_ticks_sampled, "fire_pulse_edges_consumed": _fire_pulse_edges_consumed,
		"change_weapon_edges_consumed": _change_weapon_edges_consumed,
		"movement_pulse_edges_consumed": _movement_pulse_edges_consumed,
		"capped_frame_count": _capped_frame_count, "dropped_elapsed_ticks": _dropped_elapsed_ticks}


## CPCController's Once/On/Release truth table applied to sampled levels. Gun
## fire is BUTTON_RELEASE in the shipped mapping.
func observe_input(input: Dictionary) -> Dictionary:
	var valid: Dictionary = InteractiveInput.validate(input)
	if not valid.ok:
		return valid
	var sampled: Dictionary = InteractiveInput.admit_record(input).value
	if is_paused():
		return {"ok": true}
	if _input_suspended_until_released:
		if sampled != InteractiveInput.idle():
			return {"ok": true}
		_input_suspended_until_released = false
	if _input.fire_held and not sampled.fire_held:
		_fire_pulse_pending = true
	if sampled.toggle_mode_held and not _input.toggle_mode_held:
		_toggle_edge_pending = true
	if sampled.reset_held and not _input.reset_held:
		_reset_edge_pending = true
	_input = sampled
	return {"ok": true}


func queue_toggle_mode() -> void:
	if not _blocked():
		_toggle_edge_pending = true


func queue_reset() -> void:
	if not _blocked():
		_reset_edge_pending = true


## One BUTTON_SKIP_PANNING (0x3a) KEY_ONCE edge; Core ignores it outside the pan.
func queue_skip_panning() -> void:
	if not _blocked():
		_skip_panning_edge_pending = true


func queue_fire_pulse() -> void:
	if not _blocked():
		_fire_pulse_pending = true


func queue_change_weapon() -> void:
	if not _blocked():
		_change_weapon_edge_pending = true


func queue_zoom_in() -> void:
	if not _blocked():
		_zoom_out_edge_pending = false
		_zoom_in_edge_pending = true


func queue_zoom_out() -> void:
	if not _blocked():
		_zoom_in_edge_pending = false
		_zoom_out_edge_pending = true


func queue_movement_pulse(move_x: int, move_z: int) -> Dictionary:
	var axes: Dictionary = SimInput.create(move_x, move_z)
	if not axes.ok:
		return axes
	var valid: Dictionary = SimInput.validate(axes.value)
	if not valid.ok:
		return valid
	if move_x == 0 and move_z == 0:
		return _argument("A movement pulse must contain a nonzero axis.")
	if _blocked():
		return {"ok": true}
	if move_x != 0:
		_movement_pulse_x = move_x
	if move_z != 0:
		_movement_pulse_z = move_z
	return {"ok": true}


func queue_look_pulse(look_x: int, look_y: int) -> Dictionary:
	var axes: Dictionary = SimInput.create(0, 0, 0, look_x, look_y)
	if not axes.ok:
		return axes
	var valid: Dictionary = SimInput.validate(axes.value)
	if not valid.ok:
		return valid
	if look_x == 0 and look_y == 0:
		return _argument("A look pulse must contain a nonzero axis.")
	if _blocked():
		return {"ok": true}
	if look_x != 0:
		_look_pulse_x = look_x
	if look_y != 0:
		_look_pulse_y = look_y
	return {"ok": true}


func queue_pointer_motion_milli_pixels(delta_x: int, delta_y: int) -> Dictionary:
	if delta_x == 0 and delta_y == 0:
		return _argument("Pointer motion must contain a nonzero axis.")
	if _blocked():
		return {"ok": true}
	_pointer_offset_x_milli_pixels = _add_pointer_offset(_pointer_offset_x_milli_pixels, delta_x)
	_pointer_offset_y_milli_pixels = _add_pointer_offset(_pointer_offset_y_milli_pixels, delta_y)
	return {"ok": true}


func release_all_input() -> void:
	_clear_input_state()
	_input_suspended_until_released = false


func set_authentic_menu_paused(paused: bool) -> void:
	var updated: int = (_pause_reasons | PAUSE_AUTHENTIC_MENU) if paused else (_pause_reasons & ~PAUSE_AUTHENTIC_MENU)
	if updated == _pause_reasons:
		return
	_pause_reasons = updated
	suspend_input_until_released()


func suspend_input_until_released() -> void:
	_clear_input_state()
	_input_suspended_until_released = true


## Advances whole 20 Hz steps covered by the elapsed .NET ticks (100 ns). The
## first step alone consumes queued edges and pulses. Returns the frame facts;
## events and snapshots stay with the bridge until the host takes them.
func advance_frame_ticks(elapsed_ticks: int) -> Dictionary:
	if elapsed_ticks < 0:
		return {"ok": false, "error_type": "ArgumentOutOfRangeException", "error": "Elapsed time cannot be negative."}
	if is_paused():
		_platform_input.advance_frame()
		return {"ok": true, "value": _frame(0, false)}
	var frame_time_capped: bool = elapsed_ticks > MAXIMUM_FRAME_ELAPSED_TICKS
	if frame_time_capped:
		_capped_frame_count += 1
		_dropped_elapsed_ticks += elapsed_ticks - MAXIMUM_FRAME_ELAPSED_TICKS
		elapsed_ticks = MAXIMUM_FRAME_ELAPSED_TICKS
	_interpolation_phase += elapsed_ticks * TICKS_PER_SECOND
	var steps_advanced: int = 0
	while _interpolation_phase >= PHASE_UNITS_PER_STEP:
		var first_step: bool = steps_advanced == 0
		var fire_pulse: bool = first_step and _fire_pulse_pending
		var move_x: int = _input.move_x
		var move_z: int = _input.move_z
		var look_x: int = _input.look_x
		var look_y: int = _input.look_y
		# CController::DoMappings reads the whole-pixel cursor, then the recentre
		# (0x0042DA00) eases it: quantise, read, then ease.
		var cursor_x: int = _whole_pixels_of(_pointer_offset_x_milli_pixels)
		var cursor_y: int = _whole_pixels_of(_pointer_offset_y_milli_pixels)
		var pointer_look_x: int = _to_pointer_axis_permille(cursor_x)
		var pointer_look_y: int = _to_pointer_axis_permille(cursor_y)
		_pointer_offset_x_milli_pixels = _recenter_pointer_offset(cursor_x) + (_pointer_offset_x_milli_pixels - cursor_x)
		_pointer_offset_y_milli_pixels = _recenter_pointer_offset(cursor_y) + (_pointer_offset_y_milli_pixels - cursor_y)
		if first_step:
			if move_x == 0:
				move_x = _movement_pulse_x
			if move_z == 0:
				move_z = _movement_pulse_z
			if look_x == 0:
				look_x = _look_pulse_x
			if look_y == 0:
				look_y = _look_pulse_y
		var actions: int = SimInput.Actions.FIRE if fire_pulse else SimInput.Actions.NONE
		# Row 10 samples the held mouse level as CHARGE; row 11 fires on release.
		if _input.fire_held:
			actions |= SimInput.Actions.CHARGE_WEAPON
		if _input.landing_jets_held:
			actions |= SimInput.Actions.LANDING_JETS
		if first_step:
			if _toggle_edge_pending:
				actions |= SimInput.Actions.TOGGLE_MODE
				_toggle_edges_consumed += 1
			if _reset_edge_pending:
				actions |= SimInput.Actions.RESET
				_reset_edges_consumed += 1
			if _skip_panning_edge_pending:
				actions |= SimInput.Actions.SKIP_PANNING
			if _change_weapon_edge_pending:
				actions |= SimInput.Actions.CHANGE_WEAPON
				_change_weapon_edges_consumed += 1
			if _zoom_in_edge_pending:
				actions |= SimInput.Actions.ZOOM_IN
			if _zoom_out_edge_pending:
				actions |= SimInput.Actions.ZOOM_OUT
			if _fire_pulse_pending:
				_fire_pulse_edges_consumed += 1
			if _movement_pulse_x != 0 or _movement_pulse_z != 0:
				_movement_pulse_edges_consumed += 1
			_toggle_edge_pending = false
			_reset_edge_pending = false
			_fire_pulse_pending = false
			_skip_panning_edge_pending = false
			_change_weapon_edge_pending = false
			_zoom_in_edge_pending = false
			_zoom_out_edge_pending = false
			_movement_pulse_x = 0
			_movement_pulse_z = 0
			_look_pulse_x = 0
			_look_pulse_y = 0
		if _input.fire_held:
			_fire_held_ticks_sampled += 1
		var stepped: Dictionary = _bridge.Step(move_x, move_z, actions, look_x, look_y, pointer_look_x, pointer_look_y)
		if not stepped.ok:
			return stepped
		_interpolation_phase -= PHASE_UNITS_PER_STEP
		_total_steps += 1
		steps_advanced += 1
	_platform_input.advance_frame()
	return {"ok": true, "value": _frame(steps_advanced, frame_time_capped)}


## The options slider's only consumer: (index + 1) * 3 reaches 91/3000 at the
## image default 7.0. The C# float32 product is rounded half away from zero.
func set_mouse_sensitivity(sensitivity: float) -> Dictionary:
	if not is_finite(sensitivity) or sensitivity <= 0.0:
		return {"ok": false, "error_type": "ArgumentOutOfRangeException", "error": "sensitivity"}
	_f32[0] = sensitivity
	_f32[0] = _f32[0] * POINTER_AXIS_PER_SENSITIVITY_NUMERATOR
	var product: float = _f32[0]
	_pointer_axis_numerator = int(signf(product) * floorf(absf(product) + 0.5))
	return {"ok": true}


func _frame(steps_advanced: int, frame_time_capped: bool) -> Dictionary:
	return {"steps_advanced": steps_advanced, "frame_time_capped": frame_time_capped,
		"interpolation_phase": _interpolation_phase, "interpolation_phase_scale": PHASE_UNITS_PER_STEP,
		"interpolation_alpha": float(_interpolation_phase) / float(PHASE_UNITS_PER_STEP)}


func _blocked() -> bool:
	return is_paused() or _input_suspended_until_released


func _clear_input_state() -> void:
	_platform_input.reset()
	_input = InteractiveInput.idle()
	_toggle_edge_pending = false
	_reset_edge_pending = false
	_fire_pulse_pending = false
	_skip_panning_edge_pending = false
	_change_weapon_edge_pending = false
	_zoom_in_edge_pending = false
	_zoom_out_edge_pending = false
	_movement_pulse_x = 0
	_movement_pulse_z = 0
	_look_pulse_x = 0
	_look_pulse_y = 0
	_pointer_offset_x_milli_pixels = 0
	_pointer_offset_y_milli_pixels = 0


static func _add_pointer_offset(current: int, delta: int) -> int:
	return clampi(current + delta, -MAXIMUM_POINTER_OFFSET_MILLI_PIXELS, MAXIMUM_POINTER_OFFSET_MILLI_PIXELS)


## Retail has no look dead zone: the axis reads only the whole-pixel cursor;
## the fraction stays in the accumulator and is carried, never read.
@warning_ignore("integer_division")
static func _whole_pixels_of(value: int) -> int:
	return value / POINTER_OFFSET_SCALE * POINTER_OFFSET_SCALE


## Input__UpdateCursorCenterWithWindowScale (0x0042DA00) eases by 10/17 per
## update and forces one pixel toward centre when the eased step is zero.
@warning_ignore("integer_division")
static func _recenter_pointer_offset(whole_pixel_value: int) -> int:
	var pixels: int = whole_pixel_value / POINTER_OFFSET_SCALE
	if pixels == 0:
		return 0
	var scaled: int = pixels * POINTER_OFFSET_RETENTION_NUMERATOR
	var half: int = POINTER_OFFSET_RETENTION_DENOMINATOR / 2
	var eased: int = (scaled + half) / POINTER_OFFSET_RETENTION_DENOMINATOR if scaled >= 0 \
		else (scaled - half) / POINTER_OFFSET_RETENTION_DENOMINATOR
	if eased == pixels:
		eased = pixels - signi(pixels)
	return eased * POINTER_OFFSET_SCALE


@warning_ignore("integer_division")
func _to_pointer_axis_permille(offset_milli_pixels: int) -> int:
	var scaled: int = offset_milli_pixels * _pointer_axis_numerator
	var half: int = POINTER_AXIS_DENOMINATOR / 2
	var rounded: int = (scaled + half) / POINTER_AXIS_DENOMINATOR if scaled >= 0 \
		else (scaled - half) / POINTER_AXIS_DENOMINATOR
	return clampi(rounded, -1_000, 1_000)


static func _argument(message: String) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException", "error": message}
