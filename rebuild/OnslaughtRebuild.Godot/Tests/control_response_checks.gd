# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Response = preload("res://Core/control_response.gd")
var counts: Dictionary = {}
var failures: Array[Dictionary] = []


func _initialize() -> void:
	_run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary or not parsed.get("controlResponse") is Dictionary:
		push_error("Missing control-response oracle.")
		quit(2)
		return
	var data: Dictionary = parsed.controlResponse
	var source: GDScript = load("res://Core/simulation_constants.gd")
	if source == null or not source.can_instantiate():
		push_error("Simulation constants could not be loaded.")
		quit(2)
		return
	var definitions: Dictionary = source.get_script_constant_map()
	_check("simulation_constants", "exact definition keys", definitions.size(), data.simulation_constants.size())
	for key: String in data.simulation_constants:
		_check("simulation_constants", key, definitions.get(key), _integers(data.simulation_constants[key]))
	var constants: Dictionary = {"axis_scale": Response.AXIS_SCALE_BITS,
		"right_y_centre": Response.RIGHT_Y_CENTRE_BITS, "right_y_scale": Response.RIGHT_Y_SCALE_BITS,
		"digital_threshold": Response.DIGITAL_THRESHOLD_BITS, "initial_repeat_delay": Response.INITIAL_REPEAT_DELAY_BITS,
		"repeat_delay": Response.REPEAT_DELAY_BITS, "absent_pad_axis": Response.ABSENT_PAD_AXIS_BITS}
	for key: String in constants:
		_check("constants", key, constants[key], int(data.constants[key]))
	for row: Dictionary in data.look:
		var result: Dictionary = Response.apply_look_permille(int(row.input))
		_check("look", str(row.input), result.ok, row.result.ok)
		if result.ok and row.result.ok:
			_check("look", str(row.input) + " value", result.value, int(row.result.value))
		elif not result.ok and not row.result.ok:
			_check("look", str(row.input) + " error", result.error_type, row.result.error_type)
	for row: Dictionary in data.normalized:
		var normalized: Dictionary = {"left_x": Response.normalize_left_x(int(row.input)),
			"left_y": Response.normalize_left_y(int(row.input)), "right_x": Response.normalize_right_x(int(row.input)),
			"right_y": Response.normalize_right_y(int(row.input))}
		for name: String in ["left_x", "left_y", "right_x", "right_y"]:
			_check("axis", name + ":" + str(row.input), normalized[name], {"ok": true, "bits": int(row[name])})
	for row: Dictionary in data.gates:
		_check("mapping", str(row.bits), Response.mapping_gates(int(row.bits)), {"ok": true, "value": row.value})
	for invalid: Variant in [null, false, true, 1.0, "1", [], {}, -2147483649, 2147483648]:
		_check("admission", "look Int32", Response.apply_look_permille(invalid).error_type, "ArgumentException")
		_check("admission", "signed axis Int32", Response.normalize_left_x(invalid).error_type, "ArgumentException")
		_check("admission", "right Y Int32", Response.normalize_right_y(invalid).error_type, "ArgumentException")
	for invalid: Variant in [null, false, true, 1.0, "1", [], {}, -1, 4294967296]:
		_check("admission", "mapping UInt32", Response.mapping_gates(invalid).error_type, "ArgumentException")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"completed": ["control_response"], "failures": failures}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)


func _integers(value: Variant) -> Variant:
	if typeof(value) == TYPE_FLOAT:
		_check("transport", "exact definition integer", is_finite(value) and value == floor(value)
			and value >= -2147483648 and value <= 4294967295, true)
		return int(value)
	if value is Array:
		var result: Array = []
		for item: Variant in value:
			result.append(_integers(item))
		return result
	if value is Dictionary:
		var result: Dictionary = {}
		for key: String in value:
			result[key] = _integers(value[key])
		return result
	return value
