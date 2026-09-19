# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Numbers = preload("res://Core/invariant_number.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}


func _initialize() -> void:
	_run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _result(group: String, name: String, actual: Dictionary, expected: Dictionary) -> void:
	_check(group, name + ":completion", actual.get("ok"), expected.ok)
	if expected.ok:
		var key: String = "bits" if expected.has("bits") else "value"
		_check(group, name + ":exact", actual.get(key), expected[key])
	else:
		_check(group, name + ":class", actual.get("error_type"), expected.error_type)
		_check(group, name + ":parameter", actual.get("parameter"), expected.parameter)


func _parsing(rows: Array) -> bool:
	_check("input", "nonempty", not rows.is_empty(), true)
	for index: int in range(rows.size()):
		var row: Dictionary = rows[index]
		var units: Variant = null if row.units == null else PackedInt32Array(row.units)
		_result("integer", str(index), Numbers.parse_int32(units), row.integer)
		_result("single", str(index), Numbers.parse_float32(units), row.single)
	return true


func _formatting(rows: Array) -> bool:
	_check("format", "nonempty", not rows.is_empty(), true)
	for row: Dictionary in rows:
		var result: Dictionary = Numbers.format_float32(int(row.bits))
		_check("format", str(row.bits) + ":completion", result.get("ok"), true)
		_check("format", str(row.bits) + ":text", result.get("value"), row.text)
		if result.ok:
			var parsed: Dictionary = Numbers.parse_float32(result.value)
			var expected: int = 0xffc00000 if (int(row.bits) & 0x7fffffff) > 0x7f800000 else int(row.bits)
			_check("format", str(row.bits) + ":roundtrip", parsed.get("bits"), expected)
	return true


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var document: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var completed: Array[String] = []
	if document is Dictionary and document.get("invariantNumber") is Dictionary:
		var parsed: bool = _parsing(document.invariantNumber.parsing)
		var formatted: bool = _formatting(document.invariantNumber.formatting)
		if parsed and formatted:
			completed.append("invariant_number")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"failures": failures, "completed": completed}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 5)}))
	quit(0 if failures.is_empty() and completed == ["invariant_number"] else 1)
