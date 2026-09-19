# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Timing = preload("res://Core/mission_timing.gd")
var counts: Dictionary = {}
var failures: Array[Dictionary] = []


func _initialize() -> void:
	_run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _integers(value: Variant) -> Variant:
	if typeof(value) == TYPE_FLOAT:
		if not is_finite(value) or value != floor(value) or value < -2147483648 or value > 4294967295:
			_check("transport", "exact integer", false, true)
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


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary or not parsed.get("missionTiming") is Dictionary:
		push_error("Missing mission-timing oracle.")
		quit(2)
		return
	var data: Dictionary = _integers(parsed.missionTiming)
	var script: GDScript = load("res://Core/mission_timing.gd")
	var constants: Dictionary = script.get_script_constant_map()
	for key: String in data.constants:
		_check("constants", key, constants.get(key), data.constants[key])
	var owner: RefCounted = Timing.new()
	for index: int in range(data.cases.size()):
		var row: Dictionary = data.cases[index]
		var result: Variant = owner.callv(row.method, row.arguments)
		if not result is Dictionary:
			_check("completion", row.method, "Missing result", "Dictionary")
			continue
		var name: String = row.method + ":" + str(index)
		_check(row.method, name + " admission", result.ok, row.expected.ok)
		if result.ok and row.expected.ok:
			_check(row.method, name + " value", result, row.expected)
		elif not result.ok and not row.expected.ok:
			_check(row.method, name + " type", result.error_type, row.expected.error_type)
			_check(row.method, name + " parameter", result.parameter, row.expected.parameter)
			if row.expected.message != null:
				_check(row.method, name + " message", result.error, row.expected.message)
	for invalid: Variant in [null, true, 1.0, "1", [], {}, -2147483649, 2147483648]:
		_check("admission", "typed reason", Timing.failure_terminal_ticks(invalid).error_type, "ArgumentException")
	for invalid: Variant in [null, true, 1.0, "1", [], {}, -1, 4294967296]:
		_check("admission", "typed seconds", Timing.pause_ticks(invalid).error_type, "ArgumentException")
	var position: Dictionary = Timing.trigger_position(1).value
	var expected: Dictionary = position.duplicate()
	position.x += 1
	_check("ownership", "trigger positions detached", Timing.trigger_position(1).value, expected)
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"completed": ["mission_timing"], "failures": failures}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 4)}))
	quit(0 if failures.is_empty() else 1)
