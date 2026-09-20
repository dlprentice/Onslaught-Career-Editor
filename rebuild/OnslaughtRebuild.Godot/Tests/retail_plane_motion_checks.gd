# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Exact unchanged-C# comparisons. Only this harness reads the synthetic
## fixture/admitted terrain and writes a receipt; motion owns no IO or clock.
const Motion = preload("res://Core/retail_plane_motion.gd")
const State = preload("res://Core/thing_actor_state.gd")
const Terrain = preload("res://Core/terrain.gd")
const Values = preload("res://Core/retail_career_values.gd")
var _checks: int = 0
var _counts: Dictionary = {}
var _failure_count: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _group: String = "admission"
var _terrain: Terrain.Heightfield


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.size() != 2 or Engine.is_editor_hint() or DisplayServer.get_name() != "headless":
		push_error("Two fixture/report paths and headless runtime are required.")
		quit(2)
		return
	var fixture_path: String = arguments[0]
	var report_path: String = arguments[1]
	if not _owned(fixture_path, false) or not _owned(report_path, true) or fixture_path == report_path:
		push_error("Fixture/report must use existing/fresh owned local-data paths.")
		quit(2)
		return
	var before_pointer: int = Input.mouse_mode
	var fixture_hash: String = _sha256(FileAccess.get_file_as_bytes(fixture_path))
	var file: FileAccess = FileAccess.open(fixture_path, FileAccess.READ)
	if file == null:
		push_error("Cannot open Plane reference fixture.")
		quit(2)
		return
	var payload: Variant = file.get_var(false)
	file.close()
	if not payload is Dictionary or payload.get("schema") != 1 or not _object_free(payload):
		push_error("Unrecognized or object-bearing Plane fixture.")
		quit(2)
		return
	var fixture: Dictionary = payload
	_check(fixture.direct.size() > 3000 and fixture.sequences.size() >= 20, "Complete direct and repeated-motion fixtures present.")
	_verify_source_hashes(fixture.source_sha256)
	var terrain_path: String = ProjectSettings.globalize_path("res://../OnslaughtRebuild.Core/Assets/Level100/level100-heightfield.hfld.bin")
	var terrain_bytes: PackedByteArray = FileAccess.get_file_as_bytes(terrain_path)
	var terrain_hash: String = _sha256(terrain_bytes)
	_equal(terrain_hash, fixture.terrain_sha256, "Native and embedded reference terrain identity.")
	var admitted: Dictionary = Terrain.from_bytes(terrain_bytes, 100)
	_check(admitted.ok, "Existing terrain owner admits exact Level 100 input.")
	if not admitted.ok:
		push_error("Cannot admit the existing read-only terrain: " + str(admitted))
		quit(2)
		return
	_terrain = admitted.value
	_finish("admission")
	var previous_op: String = ""
	for row: Dictionary in fixture.direct:
		if row.op != previous_op:
			if not previous_op.is_empty(): _finish(previous_op)
			previous_op = row.op
			_group = row.op
		var args: Array = row.args.duplicate(true)
		var saved: Array = args.duplicate(true)
		_compare_result(_law(row.op, args), row.result, row.name)
		_equal(args, saved, row.name + "/input-detached")
	if not previous_op.is_empty(): _finish(previous_op)
	_group = "sequences"
	for row: Dictionary in fixture.sequences:
		_sequence(row)
	_finish("sequences")
	_group = "ownership"
	_ownership_checks(fixture)
	_finish("ownership")
	_group = "transport"
	_transport_checks(fixture)
	_finish("transport")
	_group = "safety"
	_check(Input.mouse_mode == before_pointer, "Pointer ownership unchanged.")
	_equal(_sha256(FileAccess.get_file_as_bytes(fixture_path)), fixture_hash, "Fixture bytes unchanged.")
	_equal(_sha256(FileAccess.get_file_as_bytes(terrain_path)), terrain_hash, "Canonical terrain bytes unchanged.")
	_finish("safety")
	var report: Dictionary = {"schema": 1, "checks": _checks, "failure_count": _failure_count,
		"failures": _failures, "completed": _completed, "counts": _counts,
		"fixture_sha256": fixture_hash, "terrain_sha256": terrain_hash,
		"engine": Engine.get_version_info().string}
	var output: FileAccess = FileAccess.open(report_path, FileAccess.WRITE)
	if output == null:
		push_error("Cannot create Plane motion report.")
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print("RETAIL_PLANE_MOTION_CHECKS: %d checks; %d failures; %s" % [_checks, _failure_count, report_path])
	for failure: String in _failures.slice(0, 8): push_error(failure)
	quit(0 if _failure_count == 0 else 1)


func _law(operation: String, args: Array) -> Dictionary:
	match operation:
		"create_initial": return Motion.create_initial(args[0], args[1])
		"euler_from_spawner_basis": return Motion.euler_from_spawner_basis(args[0])
		"integrate_velocity": return Motion.integrate_velocity(args[0], args[1], args[2], args[3])
		"update_guide": return Motion.update_guide(args[0], args[1], args[2])
		"translate": return Motion.translate(args[0], args[1])
		"align_velocity": return Motion.align_velocity(args[0], args[1])
		"compute_clearance": return Motion.compute_clearance(_terrain if args[0] else null, args[1])
		_: return Values.failure("HarnessFailure", "Unknown Plane operation: " + operation)


func _construct(row: Dictionary) -> Dictionary:
	if row.kind == "null": return Values.success(null)
	var created: Dictionary = State.create(_millimeter_pose(), _zero(), _zero(), 0)
	if not created.ok: return created
	var owner: State.Actor = created.value
	var admitted: Dictionary = Values.success()
	if row.kind == "raw": admitted = owner.begin_retail_initialization(row.pose, row.pose, 0)
	elif row.kind == "plane": admitted = owner.begin_retail_plane(row.pose, row.motion, 0, 0)
	elif row.kind != "actor": return Values.failure("HarnessFailure", "Unknown Actor construction.")
	return created if admitted.ok else admitted


func _sequence(row: Dictionary) -> void:
	var input: Dictionary = row.duplicate(true)
	var created: Dictionary = _construct(input)
	_check(created.ok, row.name + "/construction")
	if not created.ok: return
	var actor: State.Actor = created.value
	_compare_result(_snapshot(actor), row.initial, row.name + "/initial")
	var restored: State.Actor = null
	for index: int in row.steps.size():
		var step: Dictionary = input.steps[index]
		var before: Dictionary = _snapshot(actor)
		var guide_saved: Variant = step.guide.duplicate(true) if step.guide != null else null
		var result: Dictionary = Motion.advance_free_flight(actor, step.guide, step.speed, step.time)
		_compare_result(result, step.result, row.name + "/step-%d" % index)
		_compare_result(_snapshot(actor), step.snapshot, row.name + "/snapshot-%d" % index)
		_equal(step.guide, guide_saved, row.name + "/guide-detached-%d" % index)
		if not result.ok: _equal(_snapshot(actor), before, row.name + "/failed-call-atomic-%d" % index)
		if restored != null:
			_compare_result(Motion.advance_free_flight(restored, step.guide, step.speed, step.time), step.result, row.name + "/restored-step-%d" % index)
			_equal(restored.snapshot(), _snapshot(actor), row.name + "/restored-continuation-%d" % index)
		if step.restore != null:
			var restore_result: Dictionary = State.restore(actor.snapshot().value)
			var projected: Dictionary = restore_result.value.snapshot() if restore_result.ok else restore_result
			_compare_result(projected, step.restore, row.name + "/restore-%d" % index)
			if restore_result.ok: restored = restore_result.value
		if result.ok:
			_equal(actor.snapshot().value.retail_poses.old, before.value.retail_poses.current, row.name + "/old-retains-prior-current-%d" % index)
			_equal(actor.snapshot().value.retail_motion.last_move_time_float_bits, step.time, row.name + "/event-time-%d" % index)
	_equal(input, row, row.name + "/sequence-input-detached")


func _snapshot(actor: State.Actor) -> Dictionary:
	return Values.success(null) if actor == null else actor.snapshot()


func _ownership_checks(fixture: Dictionary) -> void:
	var pose: Dictionary = _raw_pose()
	var euler: Dictionary = {"x": 0, "y": -2147483648, "z": 1}
	var result: Dictionary = Motion.create_initial(pose, euler)
	_check(result.ok, "Initial motion ownership fixture.")
	if not result.ok: return
	var initial: Dictionary = result.value.duplicate(true)
	pose.position_float_bits.x = 99
	euler.y = 99
	_equal(result.value, initial, "Initial result detached from pose and Euler input.")
	result.value.current_euler.x = 99
	_equal(result.value.desired_euler, initial.desired_euler, "Current and desired Euler are independent outputs.")
	result.value.velocity.x = 99
	_equal(result.value.drive, _zero(), "Initial velocity and drive outputs independent.")
	var row: Dictionary = fixture.sequences[0].duplicate(true)
	var made: Dictionary = _construct(row)
	_check(made.ok, "Create flight ownership fixture.")
	if not made.ok: return
	var actor: State.Actor = made.value
	var step: Dictionary = row.steps[0]
	_check(Motion.advance_free_flight(actor, step.guide, step.speed, step.time).ok, "Advance ownership fixture.")
	var after: Dictionary = actor.snapshot().value
	step.guide.destination.x = 99
	row.pose.position_float_bits.y = 99
	row.motion.drive.z = 99
	_equal(actor.snapshot().value, after, "Move and creation facts remain detached.")
	var exported: Dictionary = actor.snapshot().value
	exported.retail_plane.drive.x = 99
	exported.retail_poses.old.basis_float_bits.row0_x = 99
	_equal(actor.snapshot().value, after, "Exported motion and old pose remain detached.")
	var guide: Dictionary = _guide()
	var guide_output: Dictionary = Motion.update_guide(_raw_pose(), _zero(), guide)
	_check(guide_output.ok, "Guide output ownership fixture.")
	if guide_output.ok:
		var saved: Dictionary = guide_output.value.duplicate(true)
		guide.destination.x = 99
		_equal(guide_output.value, saved, "Guide result detached from input.")


func _transport_checks(fixture: Dictionary) -> void:
	var made: Dictionary = _construct(fixture.sequences[0])
	_check(made.ok, "Create transport fixture.")
	if not made.ok: return
	var actor: State.Actor = made.value
	var before: Dictionary = actor.snapshot().value
	for invalid: Variant in [null, true, 1.0, "1", -2147483649, 2147483648]:
		var v: Dictionary = _zero()
		v.x = invalid
		_check(not Motion.integrate_velocity(v, _zero(), 0, 0).ok, "Malformed vector words explicitly refused.")
		_check(not Motion.integrate_velocity(_zero(), _zero(), invalid, 0).ok, "Malformed air-speed word explicitly refused.")
		_check(not Motion.integrate_velocity(_zero(), _zero(), 0, invalid).ok, "Malformed speed mode explicitly refused.")
		var guide: Dictionary = _guide()
		guide.controller_state = invalid
		_check(not Motion.advance_free_flight(actor, guide, 0, 0).ok, "Malformed guide explicitly refused.")
		_equal(actor.snapshot().value, before, "Malformed guide has no actor mutation.")
		_check(not Motion.advance_free_flight(actor, _guide(), 0, invalid).ok, "Malformed event word explicitly refused at commit.")
		_equal(actor.snapshot().value, before, "Malformed commit has no actor mutation.")
	for invalid: Variant in [{}, [], _zero(), true, 0, "terrain"]:
		_check(not Motion.compute_clearance(invalid, _zero()).ok, "Unadmitted terrain object explicitly refused.")
		_check(not Motion.advance_free_flight(invalid, _guide(), 0, 0).ok, "Unadmitted actor object explicitly refused.")
	_check(not State.restore(_construct({"kind": "raw", "pose": _raw_pose()}).value.snapshot().value).ok,
		"Incomplete raw construction restore remains refused.")


func _compare_result(actual: Dictionary, expected: Dictionary, label: String) -> void:
	_equal(actual.get("ok"), expected.ok, label + "/ok")
	if actual.get("ok") != expected.ok: return
	if expected.ok:
		_equal(actual.get("value"), expected.get("value"), label + "/value")
	else:
		_equal(actual.get("error_type"), expected.error_type, label + "/error-type")
		_equal(actual.get("parameter", ""), expected.parameter, label + "/parameter")


func _zero() -> Dictionary: return {"x": 0, "y": 0, "z": 0}
func _basis() -> Dictionary:
	return {"row0_x": 0x3f800000, "row0_y": 0, "row0_z": 0, "row1_x": 0, "row1_y": 0x3f800000,
		"row1_z": 0, "row2_x": 0, "row2_y": 0, "row2_z": 0x3f800000}
func _raw_pose() -> Dictionary:
	return {"position_float_bits": {"x": 0x42c80000, "y": 0x42c80000, "z": -1054867456}, "basis_float_bits": _basis()}
func _millimeter_pose() -> Dictionary:
	return {"position_millimeters": _zero(), "basis_float_bits": _basis()}
func _guide() -> Dictionary:
	return {"destination": {"x": 0x42cc0000, "y": 0x43020000, "z": -1049624576}, "mode": 1,
		"clearance_float_bits": 0x41a00000, "controller_state": 1, "speed_mode": 0, "avoidance_position": null}


func _equal(actual: Variant, expected: Variant, label: String) -> void:
	var same: bool = _same(actual, expected)
	_check(same, label if same else label + ": " + str(actual) + " != " + str(expected))


func _same(actual: Variant, expected: Variant) -> bool:
	if typeof(actual) != typeof(expected): return false
	if actual is Dictionary:
		if actual.size() != expected.size(): return false
		for key: Variant in expected:
			if not actual.has(key) or not _same(actual[key], expected[key]): return false
		return true
	if actual is Array:
		if actual.size() != expected.size(): return false
		for index: int in actual.size():
			if not _same(actual[index], expected[index]): return false
		return true
	return actual == expected


func _check(passed: bool, label: String) -> void:
	_checks += 1
	_counts[_group] = int(_counts.get(_group, 0)) + 1
	if not passed:
		_failure_count += 1
		if _failures.size() < 100: _failures.append(label)


func _finish(group: String) -> void:
	if group not in _completed:
		_completed.append(group)
		print("RETAIL_PLANE_MOTION_SECTION: " + group)


func _verify_source_hashes(expected: Dictionary) -> void:
	var allowed: Array[String] = ["RetailPlaneMotion.cs", "RetailFloat24.cs", "RetailUnitEuler.cs", "ThingActorBaseState.cs"]
	_equal(expected.size(), allowed.size(), "Reference dependency identities present.")
	for name: String in expected:
		_check(name in allowed, "Admitted source identity path.")
		if name not in allowed: continue
		var path: String = ProjectSettings.globalize_path("res://../OnslaughtRebuild.Core/" + name)
		_equal(_sha256(FileAccess.get_file_as_bytes(path)), expected[name], "Unchanged C# reference: " + name)


func _object_free(value: Variant) -> bool:
	if typeof(value) in [TYPE_NIL, TYPE_BOOL, TYPE_INT, TYPE_STRING]: return true
	if value is Array:
		for item: Variant in value:
			if not _object_free(item): return false
		return true
	if value is Dictionary:
		for key: Variant in value:
			if not key is String or not _object_free(value[key]): return false
		return true
	return false


func _sha256(bytes: PackedByteArray) -> String:
	var digest := HashingContext.new()
	digest.start(HashingContext.HASH_SHA256)
	digest.update(bytes)
	return digest.finish().hex_encode()


func _owned(path: String, fresh: bool) -> bool:
	var base: String = ProjectSettings.globalize_path("res://../..").simplify_path().path_join("local-data")
	if not path.is_absolute_path() or path != path.simplify_path() or not path.begins_with(base + "/"): return false
	if DirAccess.dir_exists_absolute(path): return false
	if FileAccess.file_exists(path) == fresh: return false
	var directory: String = path.get_base_dir()
	if not DirAccess.dir_exists_absolute(directory): return false
	var entry_directory: DirAccess = DirAccess.open(directory)
	if entry_directory == null or entry_directory.is_link(path.get_file()): return false
	while directory.length() >= base.length():
		var parent: DirAccess = DirAccess.open(directory.get_base_dir())
		if parent == null or parent.is_link(directory.get_file()): return false
		if directory == base: return true
		directory = directory.get_base_dir()
	return false
