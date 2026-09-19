# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree

const Interactive = preload("res://Client/interactive_input.gd")
const Edges = preload("res://Client/platform_input_edges.gd")
const Bindings = preload("res://Client/retail_control_bindings.gd")
const Float32 = preload("res://Core/retail_float24.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var _completed: PackedStringArray = []
var _transport_ok: bool = true


func _initialize() -> void:
	_run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _interactive_checks(oracle: Dictionary) -> void:
	_check("interactive", "nonempty fixtures", not oracle.inputs.is_empty(), true)
	_check("interactive", "idle", Interactive.idle(), oracle.idle)
	_check("interactive", "constructor defaults", Interactive.create(0, 0, false, false, false).get("value"), oracle.idle)
	for row: Dictionary in oracle.inputs:
		var input: Dictionary = row.input
		var before: Dictionary = input.duplicate(true)
		var admitted: Dictionary = Interactive.admit_record(input)
		_check("interactive", row.name + " storage admitted before validation", admitted.get("ok"), true)
		_check("interactive", row.name + " exact value record", admitted.get("value"), input)
		var created: Dictionary = Interactive.create(input.move_x, input.move_z, input.fire_held,
			input.toggle_mode_held, input.reset_held, input.look_x, input.look_y, input.landing_jets_held)
		_check("interactive", row.name + " constructor", created.get("value"), input)
		var validated: Dictionary = Interactive.validate(input)
		_check("interactive", row.name + " semantic admission", validated.get("ok"), row.expected.ok)
		if not row.expected.ok:
			_check("interactive_errors", row.name + " error class", validated.get("error_type"), row.expected.error_type)
			_check("interactive_errors", row.name + " first invalid field", validated.get("parameter"), row.expected.parameter)
			_check("interactive_errors", row.name + " cannot return a usable record", validated.has("value"), false)
		_check("interactive", row.name + " input not mutated", input, before)
		admitted.value.move_x = 99
		_check("interactive", row.name + " detached admitted record", input, before)
	_completed.append("interactive")


func _edge_checks(scenarios: Array) -> void:
	_check("edges", "nonempty scenarios", not scenarios.is_empty(), true)
	var equivalent: Array = []
	for scenario: Dictionary in scenarios:
		var state = Edges.new()
		# Matches the oracle's backing-field seed only for Int64 boundary tests;
		# production exposes no restore API or synthetic frame source.
		state.set("_frame_index", scenario.initial_frame)
		state.set("_reset_generation", scenario.initial_generation)
		var index: int = 0
		for step: Dictionary in scenario.steps:
			var result: Dictionary = _step(state, step)
			_check("edges", scenario.name + "/" + str(index) + " result", result, step.expected)
			_check("edges", scenario.name + "/" + str(index) + " state", state.capture(), step.snapshot)
			_check("edges", scenario.name + "/" + str(index) + " frame getter", state.get_frame_index(), step.snapshot.frame_index)
			_check("edges", scenario.name + "/" + str(index) + " generation getter", state.get_reset_generation(), step.snapshot.reset_generation)
			index += 1
		if scenario.name in ["capture-canonical-order", "capture-reverse-order"]:
			equivalent.append(state.capture())
	_check("edges", "both insertion orders were exercised", equivalent.size(), 2)
	if equivalent.size() == 2:
		_check("edges", "capture order independent of insertion order", equivalent[0], equivalent[1])
	_completed.append("edges")


func _step(state: RefCounted, step: Dictionary) -> Dictionary:
	match step.operation:
		"observe_key": return state.observe_key(step.key_code, step.pressed, step.echo)
		"held_key": return state.get_held_key(step.key_code)
		"consume_key": return state.consume_key_once(step.key_code)
		"observe_joy": return state.observe_joy_button(step.joypad, step.button, step.value)
		"previous_joy": return state.get_previous_joy_button(step.joypad, step.button)
		"current_joy": return state.get_current_joy_button(step.joypad, step.button)
		"rising": return state.is_joy_button_rising(step.joypad, step.button)
		"held_joy": return state.is_joy_button_held(step.joypad, step.button)
		"falling": return state.is_joy_button_falling(step.joypad, step.button)
		"advance": state.advance_frame()
		"reset": state.reset()
		"capture": pass
		_: return {"ok": false, "error": "Unknown fixture operation."}
	return {"ok": true}


func _bindings_checks(oracle: Dictionary) -> void:
	_check("bindings", "all rows in original order", Bindings.rows(), oracle.bindings)
	var actual: Dictionary = {"row_count": Bindings.ROW_COUNT, "row_pitch": Float32.store_word(Bindings.ROW_PITCH),
		"top_pad": Float32.store_word(Bindings.TOP_PAD), "left_column_x": Float32.store_word(Bindings.LEFT_COLUMN_X),
		"right_column_right": Float32.store_word(Bindings.RIGHT_COLUMN_RIGHT), "player1_header": Bindings.PLAYER1_HEADER,
		"player2_header": Bindings.PLAYER2_HEADER}
	_check("bindings", "exact constants and header text", actual, oracle.constants)
	for row: Dictionary in oracle.invert_labels:
		_check("bindings", "deliberate inverted label " + str(row.inverted), Bindings.invert_y_label(row.inverted), {"ok": true, "value": row.value})
	var rows: Array[Dictionary] = Bindings.rows()
	rows[0].label = "caller edit"
	rows[1].action_code = 0
	rows.clear()
	_check("bindings", "callers cannot change production rows", Bindings.rows(), oracle.bindings)
	_completed.append("bindings")


func _admission_checks() -> void:
	var idle: Dictionary = Interactive.idle()
	for field: String in Interactive.FIELDS:
		var missing: Dictionary = idle.duplicate(true)
		missing.erase(field)
		_rejected("missing input " + field, Interactive.admit_record(missing))
	for field: String in ["move_x", "move_z", "look_x", "look_y"]:
		for invalid: Variant in [-129, 128, 0.0, true, null, "0"]:
			var value: Dictionary = idle.duplicate(true)
			value[field] = invalid
			_rejected("input width/type " + field + "/" + str(invalid), Interactive.admit_record(value))
	for field: String in Interactive.BOOLEAN_FIELDS:
		for invalid: Variant in [0, 1, 0.0, "false", null]:
			var value: Dictionary = idle.duplicate(true)
			value[field] = invalid
			_rejected("input bool type " + field + "/" + str(invalid), Interactive.admit_record(value))
	for invalid: Variant in [null, 0, false, [], "input"]:
		_rejected("input carrier " + str(invalid), Interactive.validate(invalid))
	var state = Edges.new()
	state.observe_key(1, true, false)
	state.observe_joy_button(1, 2, 128)
	state.advance_frame()
	state.observe_joy_button(1, 3, 255)
	var before: Dictionary = state.capture()
	for invalid: Variant in [-2147483649, 2147483648, 1.0, true, null, "1"]:
		_rejected("bad observed key", state.observe_key(invalid, true, false))
		_rejected("bad held-key query", state.get_held_key(invalid))
		_rejected("bad key consume", state.consume_key_once(invalid))
		_rejected("bad joypad", state.observe_joy_button(invalid, 2, 1))
		_rejected("bad joy button", state.observe_joy_button(1, invalid, 1))
		for method: String in ["get_previous_joy_button", "get_current_joy_button", "is_joy_button_rising", "is_joy_button_held", "is_joy_button_falling"]:
			_rejected("bad joy query " + method, state.call(method, invalid, 2))
		_check("admission", "invalid IDs cannot mutate input bytes", state.capture(), before)
	for invalid: Variant in [-1, 256, 128.0, true, null, "128"]:
		_rejected("bad joy byte", state.observe_joy_button(1, 2, invalid))
		_check("admission", "invalid joy byte preserves previous/current", state.capture(), before)
	for invalid: Variant in [0, 1, 0.0, null, "false"]:
		_rejected("bad pressed flag", state.observe_key(1, invalid, false))
		_rejected("bad echo flag", state.observe_key(1, false, invalid))
		_rejected("bad invert flag", Bindings.invert_y_label(invalid))
		_check("admission", "invalid flags do not release/consume", state.capture(), before)
	var captured: Dictionary = state.capture()
	captured.held_keys[0].value = 0
	captured.consume_once_keys.clear()
	captured.previous_joy_buttons[0].value = 9
	captured.current_joy_buttons.clear()
	_check("detachment", "captured rows and arrays are detached", state.capture(), before)
	state.observe_joy_button(1, 2, 0)
	_check("detachment", "old captured snapshot remains unchanged by later input", before.current_joy_buttons[0].value, 128)
	_check("detachment", "current mutation does not modify previous frame", state.get_previous_joy_button(1, 2).get("value"), 128)
	_check("admission", "valid key consume still works after refused calls", state.consume_key_once(1).get("value"), 1)
	idle.move_x = 99
	_check("detachment", "Idle is a detached value", Interactive.idle().move_x, 0)
	_completed.append("admission")


func _rejected(name: String, value: Dictionary) -> void:
	_check("admission", name + " refuses", value.get("ok"), false)
	_check("admission", name + " no usable value", value.has("value"), false)
	_check("admission", name + " explicit diagnostic", str(value.get("error", "")).is_empty(), false)


func _decode_transport(value: Variant) -> Variant:
	if value is Dictionary:
		if value.size() == 1 and value.has("$i64"):
			if not value["$i64"] is String:
				_transport_ok = false
				return null
			var raw: String = value["$i64"]
			var integer: int = raw.to_int()
			if str(integer) != raw:
				_transport_ok = false
				return null
			return integer
		var result: Dictionary = {}
		for key: String in value:
			result[key] = _decode_transport(value[key])
		return result
	if value is Array:
		var result: Array = []
		for item: Variant in value:
			result.append(_decode_transport(item))
		return result
	if typeof(value) == TYPE_FLOAT:
		if not is_finite(value) or value != floor(value) or value < -2147483648 or value > 4294967295:
			_transport_ok = false
			return null
		return int(value)
	return value


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or not args[1].is_absolute_path() or FileAccess.file_exists(args[1]):
		push_error("Input checks require existing oracle and new absolute task-owned report paths.")
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary or not parsed.get("clientInput") is Dictionary:
		push_error("Missing clientInput oracle object.")
		quit(2)
		return
	var oracle: Dictionary = _decode_transport(parsed.clientInput)
	for key: String in ["inputs", "scenarios", "bindings", "invert_labels"]:
		if not oracle.get(key) is Array: _transport_ok = false
	if not _transport_ok:
		push_error("Input fixture transport is incomplete or loses exact values.")
		quit(2)
		return
	_interactive_checks(oracle)
	_edge_checks(oracle.scenarios)
	_bindings_checks(oracle)
	_admission_checks()
	for section: String in ["interactive", "edges", "bindings", "admission"]:
		_check("completion", section + " returned", _completed.has(section), true)
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(), "failures": failures,
		"completed": ["client_input"] if _completed.size() == 4 else []}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)
