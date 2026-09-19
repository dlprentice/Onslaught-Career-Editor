# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const MessagePanel = preload("res://Client/message_panel.gd")
const Text = preload("res://Core/canonical_json_string.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var completed: Array[String] = []


func _initialize() -> void:
	call_deferred("run_checks")


func check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _lines(value: Variant) -> Variant:
	if value == null:
		return null
	var result: Array[Dictionary] = []
	for line: Dictionary in value:
		result.append({"text": null if line.text == null else PackedInt32Array(line.text),
			"source_length": int(line.source_length)})
	return result


func _shape(result: Dictionary) -> Dictionary:
	if result.get("ok") != true:
		return {"ok": false, "error_type": result.get("error_type"), "parameter": result.get("parameter")}
	if typeof(result.value) != TYPE_ARRAY:
		return result
	var values: Array = []
	for value: Variant in result.value:
		values.append(null if value == null else Array(value))
	return {"ok": true, "value": values}


func _fixture_numbers(value: Variant) -> Variant:
	# Godot JSON transports numbers as doubles. Admit the exact integer words
	# before comparing nested arrays; the codec under test never sees coercion.
	if typeof(value) == TYPE_FLOAT:
		if value == floor(value) and abs(value) <= 9007199254740991.0:
			return int(value)
		return value
	if typeof(value) == TYPE_ARRAY:
		var result: Array = []
		for item: Variant in value:
			result.append(_fixture_numbers(item))
		return result
	if typeof(value) == TYPE_DICTIONARY:
		var result: Dictionary = {}
		for key: String in value:
			result[key] = _fixture_numbers(value[key])
		return result
	return value


func run_checks() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if typeof(data) != TYPE_DICTIONARY or not data.has("message_panel"):
		quit(2)
		return
	var fixtures: Dictionary = _fixture_numbers(data.message_panel)
	var constants: Dictionary = MessagePanel.new().get_script().get_script_constant_map()
	for name: String in fixtures.constants:
		check("constants", name, constants[name.to_upper()], fixtures.constants[name])
	check("wrap_refusal", "null", _shape(MessagePanel.wrap(null)), fixtures.null_wrap)
	for row: Dictionary in fixtures.wrapped:
		var text := PackedInt32Array(row.text)
		var result: Dictionary = MessagePanel.wrap(text)
		check("wrap", row.name, result.ok, true)
		if not result.ok:
			continue
		var expected: Variant = _lines(row.lines)
		check("wrap", row.name, result.value, expected)
		check("source_length", row.name, MessagePanel.source_length(result.value).value, int(row.source_length))
		var native: Dictionary = Text.native_string(text)
		if native.ok:
			check("native_string", row.name, MessagePanel.wrap(native.value).value, expected)
		text.fill(1)
		check("detached_source", row.name, result.value, expected)
		for sample: Dictionary in row.windows:
			check("window", row.name + ":" + str(sample.cursor),
				_shape(MessagePanel.window(result.value, int(sample.cursor))), sample.result)
		var visible: Dictionary = MessagePanel.window(result.value, 2147483647)
		if visible.ok:
			for line: PackedInt32Array in visible.value:
				line.fill(2)
		check("detached_window", row.name, result.value, expected)
	completed.append("wrap_window")
	for row: Dictionary in fixtures.reveal:
		var seconds: float = String(row.bits).hex_decode().decode_double(0)
		check("reveal", row.bits, MessagePanel.revealed_characters(seconds).value, int(row.expected))
	completed.append("reveal")
	for row: Dictionary in fixtures.supplied:
		var lines: Variant = _lines(row.lines)
		check("supplied_length", row.name, _shape(MessagePanel.source_length(lines)), row.length)
		for sample: Dictionary in row.windows:
			check("supplied_window", row.name + ":" + str(sample.cursor),
				_shape(MessagePanel.window(lines, int(sample.cursor))), sample.result)
	for invalid: Variant in [true, 1, 1.0, {}, [], PackedInt32Array([-1]), PackedInt32Array([65536])]:
		check("explicit_admission", "wrap", MessagePanel.wrap(invalid).ok, false)
	for invalid: Variant in [true, null, "0", [], {}]:
		check("explicit_admission", "reveal", MessagePanel.revealed_characters(invalid).ok, false)
	for invalid: Variant in [true, null, "0", [], {}, 0.0, -2147483649, 2147483648]:
		check("explicit_admission", "cursor", MessagePanel.window([], invalid).ok, false)
	completed.append("boundary")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "failures": failures,
		"counts": counts, "completed": completed}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"failure_count": failures.size(), "counts": counts, "first_failures": failures.slice(0, 5)}))
	quit(0 if failures.is_empty() else 1)
