# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Reads only the explicitly supplied tracked fixture and oracle. All malformed
## byte probes stay in memory; only the report is written to owned test output.
const Codec = preload("res://Core/retail_career_save.gd")
var counts: Dictionary = {}
var failures: Array[Dictionary] = []
var completed: Array[String] = []


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


func _hash(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 3:
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary or not parsed.get("careerSave") is Dictionary:
		push_error("Missing career reader oracle.")
		quit(2)
		return
	var data: Dictionary = _integers(parsed.careerSave)
	var original: PackedByteArray = FileAccess.get_file_as_bytes(args[2])
	_check("fixture", "original identity", _hash(original), data.fixture_sha256)
	if original.size() != 10004:
		quit(2)
		return
	for row: Dictionary in data.cases:
		var source: PackedByteArray = original.duplicate()
		if row.length != null:
			source.resize(row.length)
		for patch: Dictionary in row.patches:
			match patch.width:
				1: source[patch.offset] = patch.word
				2: source.encode_u16(patch.offset, patch.word)
				4: source.encode_u32(patch.offset, patch.word)
				_: _check("transport", "known patch width", patch.width, "1, 2, 4")
		var before: PackedByteArray = source.duplicate()
		var result: Dictionary = Codec.read(source)
		_check("admission", row.name, result.ok, row.expected.ok)
		_check("read_only", row.name + " input unchanged", source, before)
		if result.ok and row.expected.ok:
			var save: Codec.Save = result.value
			_check("projection", row.name, save.snapshot(), row.expected.value)
			_check("summary", row.name, save.progression_summary(), row.expected.summary)
			_check("frontend", row.name, save.project(), row.expected.project)
			_check("bytes", row.name + " exact container", save.container_bytes(), before)
			_check("bytes", row.name + " reference digest", _hash(save.container_bytes()), row.expected.bytes_sha256)
			for selection: Dictionary in row.expected.selection:
				_check("selection", row.name + ":" + str(selection.world), save.is_world_selectable(selection.world), {"ok": true, "value": selection.selectable})
		elif not result.ok and not row.expected.ok:
			_check("refusals", row.name, result, row.expected)
	completed.append("reader")
	_ownership(original)
	completed.append("ownership")
	_check("read_only", "real fixture unchanged", FileAccess.get_file_as_bytes(args[2]), original)
	completed.append("read_only")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"completed": completed, "failures": failures}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)


func _ownership(original: PackedByteArray) -> void:
	var source: PackedByteArray = original.duplicate()
	var save: Codec.Save = Codec.read(source).value
	var expected: Dictionary = save.snapshot()
	var project: Dictionary = save.project()
	var summary: Dictionary = save.progression_summary()
	source[0x249a] ^= 255
	var returned: PackedByteArray = save.container_bytes()
	returned[0x249a] ^= 255
	save.snapshot().campaign_nodes[0].complete = 123
	save.snapshot().selectable_world_numbers.clear()
	save.project().selectable_world_numbers.clear()
	save.progression_summary().career_in_progress = 0
	_check("ownership", "input and returned bytes detached", save.container_bytes(), original)
	_check("ownership", "all read facts detached", save.snapshot(), expected)
	_check("ownership", "frontend facts detached", save.project(), project)
	_check("ownership", "summary detached", save.progression_summary(), summary)
	_check("fixture", "gold completed worlds", expected.completed_world_count, 43)
	_check("fixture", "gold unlocked goodies", expected.unlocked_goodie_count, 232)
	_check("fixture", "gold latest world", expected.suggested_world_number, 800)
	for invalid: Variant in [null, [], {}, false, "", 10004]:
		_check("host_types", "byte carrier", Codec.read(invalid).error_type, "ArgumentException")
	for invalid: Variant in [null, [], {}, false, "100", 100.0, -2147483649, 2147483648]:
		_check("host_types", "world carrier", save.is_world_selectable(invalid).error_type, "ArgumentException")
