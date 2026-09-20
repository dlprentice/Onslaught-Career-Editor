# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Standard-Godot exact comparison with the unchanged C# algebra. Two absolute
## owned paths: the object-free fixture and a fresh JSON report. No assets,
## simulation, mutable pose cache or rendered/physical input are involved.
const Pose = preload("res://Core/retail_mesh_part_pose.gd")
const OPERATIONS: Array[String] = ["interpolate_single_frame", "compose_hierarchy", "apply_owner", "to_local_sphere_query"]
const REQUIRED: Array[String] = ["reference", "interpolate_single_frame", "compose_hierarchy", "apply_owner", "to_local_sphere_query", "detachment", "carrier_admission", "ownership"]
var _completed: Array[String] = []
var _counts: Dictionary = {}
var _failures: Array[Dictionary] = []
var _report: String = ""
var _source_hashes: Dictionary = {}
var _words: int = 0
var _finished: bool = false


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or Engine.is_editor_hint() or DisplayServer.get_name() != "headless": quit(2); return
	if not _owned_path(args[0]) or not _owned_path(args[1]) or args[0] == args[1] or FileAccess.file_exists(args[1]): quit(2); return
	_report = args[1]
	create_timer(60).timeout.connect(func() -> void:
		if not _finished: _failures.append({"group": "completion", "name": "timeout"}); _finish())
	var pointer: int = Input.mouse_mode
	var fixture_hash: String = FileAccess.get_sha256(args[0])
	for path: String in ["res://Core/retail_mesh_part_pose.gd", "res://Core/retail_float24.gd"]:
		_source_hashes[path] = FileAccess.get_sha256(path)
	var fixture: Dictionary = _read(args[0])
	if not _reference(fixture): _finish(); return
	_completed.append("reference")
	for operation: String in OPERATIONS:
		if _operation(fixture.cases, operation): _completed.append(operation)
	if _detachment(fixture.cases): _completed.append("detachment")
	if _carrier_admission(): _completed.append("carrier_admission")
	_check("ownership", "fixture remained read-only", FileAccess.get_sha256(args[0]), fixture_hash)
	_check("ownership", "pointer unchanged", Input.mouse_mode, pointer)
	for path: String in _source_hashes: _check("ownership", "unchanged source " + path, FileAccess.get_sha256(path), _source_hashes[path])
	_completed.append("ownership")
	fixture.clear()
	await process_frame
	_finish()


func _reference(fixture: Dictionary) -> bool:
	if not _check("reference", "schema", fixture.get("schema"), 1): return false
	if not _check("reference", "completion marker", fixture.get("completed"), ["mesh_part_pose_reference"]): return false
	if not _check("reference", "case collection", fixture.get("cases") is Array, true): return false
	if not _check("reference", "nonempty cases", not fixture.cases.is_empty(), true): return false
	if not _check("reference", "original source identities", fixture.get("source_sha256") is Dictionary, true): return false
	for name: String in ["RetailMeshPartPose.cs", "RetailFloat24.cs"]:
		_check("reference", name + " unchanged", FileAccess.get_sha256("res://../OnslaughtRebuild.Core/" + name), fixture.source_sha256.get(name))
	_check("reference", "data-only fixture", _data_only(fixture), true)
	for row: Variant in fixture.cases:
		if not _check("reference", "case record", row is Dictionary, true): return false
		if not _check("reference", "known operation", row.get("operation") in OPERATIONS, true): return false
		if not _check("reference", "explicit success/refusal", row.get("ok") is bool, true): return false
	return true


func _operation(cases: Array, operation: String) -> bool:
	var seen: int = 0
	for row: Dictionary in cases:
		if row.operation != operation: continue
		seen += 1
		var before: Dictionary = row.input.duplicate(true)
		var result: Dictionary = _call(operation, row.input)
		var name: String = row.name
		_check(operation, name + " input unchanged", row.input, before)
		if not _check(operation, name + " explicit admission", result.get("ok"), row.ok): continue
		if row.ok:
			_compare_record(operation, name, result.get("value"), row.value)
			_check(operation, name + " no error on success", result.has("error_type"), false)
		else:
			_check(operation, name + " exception kind", result.get("error_type"), row.error_type)
			_check(operation, name + " exception parameter", result.get("parameter"), row.parameter)
			_check(operation, name + " no partial output", result.has("value"), false)
			if _check(operation, name + " explicit error", result.get("error") is String and not result.get("error", "").is_empty(), true):
				_check(operation, name + " unchanged source reason", row.error.begins_with(result.error), true)
	_check(operation, "operation exercised", seen > 0, true)
	return seen > 0


func _detachment(cases: Array) -> bool:
	for operation: String in OPERATIONS:
		var selected: Dictionary = {}
		for row: Dictionary in cases:
			if row.operation == operation and row.ok:
				selected = row
				break
		if not _check("detachment", operation + " admitted fixture", not selected.is_empty(), true): return false
		var input: Dictionary = selected.input.duplicate(true)
		var result: Dictionary = _call(operation, input)
		if not _check("detachment", operation + " admitted", result.get("ok"), true): return false
		var captured: Dictionary = result.value.duplicate(true)
		input.first.position_float_bits.x = 1337
		input.first.basis_float_bits.row2_z = 1338
		input.second.position_float_bits.z = 1339
		input.center.y = 1340
		input.displacement.z = 1341
		_check("detachment", operation + " input edits cannot alter result", result.value, captured)
		var untouched: Dictionary = selected.input.duplicate(true)
		for record: Dictionary in result.value.values():
			for key: String in record: record[key] = -1749
		_check("detachment", operation + " output edits cannot alter inputs", selected.input, untouched)
		var repeated: Dictionary = _call(operation, selected.input)
		_check("detachment", operation + " repeated operation admitted", repeated.get("ok"), true)
		_compare_record("detachment", operation + " repeated raw output", repeated.get("value"), selected.value)
		_check("detachment", operation + " data-only output", _data_only(repeated), true)
	return true


func _carrier_admission() -> bool:
	var valid: Dictionary = _identity()
	var invalid_poses: Array = [null, false, 0, 0.0, "pose", [], PackedInt32Array([0]), {}, {"position_float_bits": {"x": 0, "y": 0, "z": 0}}]
	var missing: Dictionary = valid.duplicate(true)
	missing.basis_float_bits.erase("row2_z")
	invalid_poses.append(missing)
	for invalid: Variant in invalid_poses:
		_reject(Pose.interpolate_single_frame(invalid), "frame")
		_reject(Pose.compose_hierarchy(invalid, valid), "parent")
		_reject(Pose.compose_hierarchy(valid, invalid), "local")
		_reject(Pose.apply_owner(invalid, valid), "owner")
		_reject(Pose.apply_owner(valid, invalid), "cached")
		_reject(Pose.to_local_sphere_query(invalid, valid.position_float_bits, valid.position_float_bits), "part")
	for value: Variant in [null, false, true, 0.0, "0", [], {}, -0x80000001, 0x80000000, 0xffffffff]:
		for group: String in ["position_float_bits", "basis_float_bits"]:
			for key: String in (Pose.VECTOR_KEYS if group == "position_float_bits" else Pose.BASIS_KEYS):
				var pose: Dictionary = valid.duplicate(true)
				pose[group][key] = value
				_reject(Pose.interpolate_single_frame(pose), "frame")
				_reject(Pose.compose_hierarchy(valid, pose), "local")
				_reject(Pose.apply_owner(pose, valid), "owner")
				_reject(Pose.to_local_sphere_query(pose, valid.position_float_bits, valid.position_float_bits), "part")
	for vector: Variant in [null, false, 0, [], PackedInt32Array([0, 0, 0]), {}, {"x": 0, "y": 0}, {"x": 0, "y": 0, "z": 0.0}, {"x": 0, "y": -0x80000001, "z": 0}]:
		_reject(Pose.to_local_sphere_query(valid, vector, valid.position_float_bits), "current_center")
		_reject(Pose.to_local_sphere_query(valid, valid.position_float_bits, vector), "displacement")
	var before: Dictionary = valid.duplicate(true)
	var rejected: Dictionary = Pose.apply_owner(null, valid)
	_check("carrier_admission", "invalid call remains refused", rejected.ok, false)
	_check("carrier_admission", "failed call cannot change valid companion input", valid, before)
	return true


func _reject(result: Dictionary, parameter: String) -> void:
	_check("carrier_admission", parameter + " rejected", result.get("ok"), false)
	_check("carrier_admission", parameter + " explicit carrier error", result.get("error_type"), "ArgumentException")
	_check("carrier_admission", parameter + " parameter", result.get("parameter"), parameter)
	_check("carrier_admission", parameter + " no partial value", result.has("value"), false)


func _compare_record(group: String, name: String, actual: Variant, expected: Dictionary) -> void:
	if not _check(group, name + " record", actual is Dictionary, true): return
	_check(group, name + " exact field count", actual.size(), expected.size())
	for key: String in expected:
		if expected[key] is Dictionary:
			_compare_record(group, name + "/" + key, actual.get(key), expected[key])
		else:
			_words += 1
			_check(group, name + "/" + key + " signed-word carrier", actual.get(key) is int, true)
			_check(group, name + "/" + key + " raw %08x" % (int(expected[key]) & 0xffffffff), actual.get(key), expected[key])


func _check(group: String, name: String, actual: Variant, expected: Variant) -> bool:
	_counts[group] = _counts.get(group, 0) + 1
	if actual == expected: return true
	var failure: Dictionary = {"group": group, "name": name, "actual": str(actual), "expected": str(expected)}
	_failures.append(failure)
	if _failures.size() <= 16: push_error(JSON.stringify(failure))
	return false


func _finish() -> void:
	if _finished: return
	_finished = true
	for group: String in REQUIRED:
		if not _completed.has(group): _failures.append({"group": "completion", "name": "missing " + group})
	var report: Dictionary = {"schema": 1, "failure_count": _failures.size(), "failures": _failures,
		"completed": _completed, "counts": _counts, "raw_words": _words, "source_sha256": _source_hashes}
	var file := FileAccess.open(_report, FileAccess.WRITE)
	if file == null: quit(2); return
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("MESH_PART_POSE_CHECKS: ", JSON.stringify({"failure_count": _failures.size(), "counts": _counts, "raw_words": _words, "completed": _completed}), "; ", _report)
	quit(0 if _failures.is_empty() else 1)


static func _call(operation: String, input: Dictionary) -> Dictionary:
	match operation:
		"interpolate_single_frame": return Pose.interpolate_single_frame(input.first)
		"compose_hierarchy": return Pose.compose_hierarchy(input.first, input.second)
		"apply_owner": return Pose.apply_owner(input.first, input.second)
		"to_local_sphere_query": return Pose.to_local_sphere_query(input.first, input.center, input.displacement)
	return {"ok": false, "error": "Unknown operation in fixture."}


static func _identity() -> Dictionary:
	return {"position_float_bits": {"x": 0, "y": 0, "z": 0}, "basis_float_bits": {
		"row0_x": 0x3f800000, "row0_y": 0, "row0_z": 0, "row1_x": 0, "row1_y": 0x3f800000,
		"row1_z": 0, "row2_x": 0, "row2_y": 0, "row2_z": 0x3f800000}}


static func _read(path: String) -> Dictionary:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null: return {}
	var value: Variant = file.get_var(false)
	file.close()
	return value if value is Dictionary else {}


static func _data_only(value: Variant) -> bool:
	if value is Dictionary:
		for key: Variant in value:
			if not _data_only(key) or not _data_only(value[key]): return false
		return true
	if value is Array:
		for item: Variant in value:
			if not _data_only(item): return false
		return true
	return value == null or value is String or value is int or value is bool


static func _owned_path(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or path.contains("\\") or not path.begins_with(owned + "/"): return false
	var directory := DirAccess.open(owned)
	if directory == null: return false
	var parts: PackedStringArray = path.trim_prefix(owned + "/").split("/", false)
	for index: int in range(parts.size()):
		if directory.is_link(parts[index]): return false
		if index < parts.size() - 1 and directory.change_dir(parts[index]) != OK: return false
	return not parts.is_empty()
