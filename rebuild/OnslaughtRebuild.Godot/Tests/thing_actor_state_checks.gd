# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Standard-engine differential runner. Only this harness reads the synthetic
## unchanged-C# fixture and writes a receipt; Core remains independent of IO.
const State = preload("res://Core/thing_actor_state.gd")
const Values = preload("res://Core/retail_career_values.gd")
var _checks: int = 0
var _counts: Dictionary = {}
var _failures: Array[String] = []
var _failure_count: int = 0
var _completed: Array[String] = []
var _group: String = "admission"


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
		push_error("Fixture/report must use existing fresh owned local-data paths.")
		quit(2)
		return
	var before_pointer: int = Input.mouse_mode
	var fixture_hash: String = _sha256(FileAccess.get_file_as_bytes(fixture_path))
	var file: FileAccess = FileAccess.open(fixture_path, FileAccess.READ)
	if file == null:
		push_error("Cannot open reference fixture.")
		quit(2)
		return
	var payload: Variant = file.get_var(false)
	file.close()
	if not payload is Dictionary or payload.get("schema") != 1:
		push_error("Unrecognized Thing state fixture.")
		quit(2)
		return
	var fixture: Dictionary = payload
	_check(_object_free(fixture), "Reference transport contains only value data.")
	_check(fixture.cases.size() > 500 and fixture.laws.size() > 1000, "Complete state/projection fixtures are present.")
	_verify_source_hashes(fixture.source_sha256)
	_group = "constants"
	var constants: Dictionary = fixture.constants
	_equal(State.ACTOR_LINEAGE, constants.actor_lineage, "Actor lineage")
	_equal(State.THING, constants.thing, "Thing type bit")
	_equal(State.ACTOR, constants.actor, "Actor type bit")
	_equal(State.COMPLEX_THING, constants.complex_thing, "ComplexThing type bit")
	_equal(State.INITIAL_CONTACT_TIME_FLOAT_BITS, constants.initial_contact_time_float_bits, "Initial contact word")
	for flag: String in constants.flags:
		_equal(State.Flags.get(flag.to_upper()), constants.flags[flag], "Flag " + flag)
	_finish("constants")
	_group = "state"
	for row: Dictionary in fixture.cases:
		var input: Array = row.args.duplicate(true)
		var original_input: Array = input.duplicate(true)
		var result: Dictionary = _construct(row.kind, input)
		if result.ok:
			var owner: RefCounted = result.value
			_compare_result(owner.call("snapshot"), row.result, row.name + "/factory")
			for step: Dictionary in row.steps:
				var args: Array = step.args.duplicate(true)
				var retained: Array = args.duplicate(true)
				var actual: Dictionary
				if step.op == "restore_snapshot":
					var snapshot: Dictionary = owner.call("snapshot")
					actual = State.restore(snapshot.value) if snapshot.ok else snapshot
					if actual.ok: actual = actual.value.snapshot()
				else:
					actual = owner.callv(step.op, args)
				_compare_result(actual, step.result, row.name + "/" + step.op)
				_compare_result(owner.call("snapshot"), step.snapshot, row.name + "/after-" + step.op)
				_equal(args, retained, row.name + "/input-detached-" + step.op)
		else:
			_compare_result(result, row.result, row.name + "/factory")
		_equal(input, original_input, row.name + "/factory-input-detached")
	_finish("state")
	_group = "projection"
	for row: Dictionary in fixture.laws:
		var args: Array = row.args.duplicate(true)
		var original: Array = args.duplicate(true)
		var result: Dictionary = _law(row.op, args)
		_compare_result(result, row.result, row.name)
		_equal(args, original, row.name + "/input-detached")
	_finish("projection")
	_group = "properties"
	for row: Dictionary in fixture.properties:
		_compare_result(State.snapshot_properties(row.snapshot, row.type_mask), row.result, row.name)
	_finish("properties")
	_group = "ownership"
	_ownership_checks(fixture)
	_finish("ownership")
	_group = "transport"
	_transport_checks()
	_finish("transport")
	_group = "safety"
	_check(Input.mouse_mode == before_pointer, "Pointer ownership unchanged.")
	_check(_sha256(FileAccess.get_file_as_bytes(fixture_path)) == fixture_hash, "Reference bytes unchanged.")
	_finish("safety")
	var report: Dictionary = {"schema": 1, "checks": _checks, "failure_count": _failure_count,
		"failures": _failures, "completed": _completed, "counts": _counts, "fixture_sha256": fixture_hash}
	var output: FileAccess = FileAccess.open(report_path, FileAccess.WRITE)
	if output == null:
		push_error("Cannot create Thing state report.")
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print("THING_ACTOR_STATE_CHECKS: %d checks; %d failures; %s" % [_checks, _failure_count, report_path])
	for failure: String in _failures.slice(0, 8): push_error(failure)
	quit(0 if _failure_count == 0 else 1)


func _construct(kind: String, args: Array) -> Dictionary:
	match kind:
		"create": return State.create(args[0], args[1], args[2], args[3])
		"restore": return State.restore(args[0])
		"create_thing": return State.create_thing(args[0], args[1], args[2])
		_: return Values.failure("HarnessFailure", "Unknown construction: " + kind)


func _law(operation: String, args: Array) -> Dictionary:
	match operation:
		"project_pose": return State.Laws.project_pose(args[0])
		"project_position": return State.Laws.project_position(args[0])
		"project_vector": return State.Laws.project_vector(args[0])
		"angular_delta": return State.Laws.angular_delta(args[0], args[1])
		_: return Values.failure("HarnessFailure", "Unknown projection: " + operation)


func _compare_result(actual: Dictionary, expected: Dictionary, label: String) -> void:
	_equal(actual.get("ok"), expected.ok, label + "/ok")
	if actual.get("ok") != expected.ok: return
	if expected.ok:
		_equal(actual.get("value"), expected.get("value"), label + "/value")
	else:
		_equal(actual.get("error_type"), expected.error_type, label + "/error-type")
		_equal(actual.get("parameter", ""), expected.parameter, label + "/parameter")


func _ownership_checks(fixture: Dictionary) -> void:
	var pose: Dictionary = _pose()
	var velocity: Dictionary = {"x": 1, "y": 2, "z": 3}
	var created: Dictionary = State.create(pose, velocity, velocity, 0)
	_check(created.ok, "Create ownership fixture.")
	if not created.ok: return
	var actor: State.Actor = created.value
	var initial: Dictionary = actor.snapshot().value
	pose.position_millimeters.x = 999
	pose.basis_float_bits.row0_y = -2147483648
	velocity.x = 999
	_equal(actor.snapshot().value, initial, "Constructor inputs detached.")
	var snapshot: Dictionary = actor.snapshot().value
	snapshot.old_pose.position_millimeters.y = 99
	snapshot.current_pose.basis_float_bits.row2_z = 0
	snapshot.angular_velocity.z = 99
	_equal(actor.snapshot().value, initial, "Snapshot fields and both buffers detached.")
	var next: Dictionary = _pose(55, 66, 77)
	actor.advance_pose(next)
	var moved: Dictionary = actor.snapshot().value
	next.position_millimeters.x = 9
	next.basis_float_bits.row0_x = 1
	_equal(actor.snapshot().value, moved, "Movement input detached.")
	actor.update_current_pose(_pose(88, 99, 111))
	_equal(actor.snapshot().value.old_pose, initial.current_pose, "Current mutation leaves old pose.")
	var complete: Dictionary = {}
	for row: Dictionary in fixture.cases:
		if row.name == "restore/plane": complete = row.args[0].duplicate(true)
	_check(not complete.is_empty(), "Complete Plane fixture found.")
	if complete.is_empty(): return
	var saved: Dictionary = complete.duplicate(true)
	var restored: Dictionary = State.restore(complete)
	_check(restored.ok, "Complete Plane restore succeeds.")
	if not restored.ok: return
	var plane: State.Actor = restored.value
	complete.retail_poses.current.position_float_bits.x = 0
	complete.retail_poses.old.basis_float_bits.row0_y = 1
	complete.retail_plane.velocity.x = 1
	complete.retail_motion.move_countdown = -1
	_equal(plane.snapshot().value, saved, "Restore input and raw state detached.")
	var detached_raw: Dictionary = plane.get_retail_poses().value
	detached_raw.current.position_float_bits.z = 0
	detached_raw.old.basis_float_bits.row2_x = 1
	_equal(plane.snapshot().value, saved, "Raw getter detached.")
	var raw_input: Dictionary = _raw_pose()
	var motion_input: Dictionary = saved.retail_plane.duplicate(true)
	motion_input.drive = {"x": 0x3f800000, "y": 0x40000000, "z": 0x40400000}
	_check(plane.commit_retail_plane_move(raw_input, motion_input, 0).ok, "Commit ownership fixture.")
	var after_commit: Dictionary = plane.snapshot().value
	raw_input.position_float_bits.x = 0
	raw_input.basis_float_bits.row2_z = 0
	motion_input.current_euler.x = 1
	motion_input.drive.y = 1
	_equal(plane.snapshot().value, after_commit, "Commit inputs detached.")
	var raw_position: Dictionary = {"x": 0x43880001, "y": 0x43700001, "z": -1054867455}
	_check(plane.set_retail_position(raw_position).ok, "Set raw ownership fixture.")
	var after_position: Dictionary = plane.snapshot().value
	raw_position.x = 0
	_equal(plane.snapshot().value, after_position, "Raw position input detached.")
	_equal(plane.snapshot().value.retail_poses.old, after_commit.retail_poses.old, "Set current leaves old buffer.")
	plane.copy_retail_position_to_old()
	var old_basis: Dictionary = plane.snapshot().value.retail_poses.old.basis_float_bits.duplicate()
	plane.teleport_retail_position(_raw_pose().position_float_bits)
	plane.set_retail_position({"x": 0x43880001, "y": 0x43700001, "z": -1054867455})
	_equal(plane.snapshot().value.retail_poses.old.position_float_bits, _raw_pose().position_float_bits,
		"Teleport copies independent positions.")
	_equal(plane.snapshot().value.retail_poses.old.basis_float_bits, old_basis, "Teleport retains old basis.")
	plane.clear_retail_plane_drive()
	_equal(after_commit.retail_plane.drive, {"x": 0x3f800000, "y": 0x40000000, "z": 0x40400000}, "Clear drive leaves published snapshot.")


func _transport_checks() -> void:
	var invalid_ints: Array = [null, true, 1.0, "1", -2147483649, 2147483648]
	for invalid: Variant in invalid_ints:
		var pose: Dictionary = _pose()
		pose.position_millimeters.x = invalid
		_check(not State.create(pose, _zero(), _zero(), 0).ok, "Reject malformed signed millimeter.")
		var raw: Dictionary = _raw_pose()
		raw.basis_float_bits.row0_x = invalid
		var owner: State.Actor = State.create(_pose(), _zero(), _zero(), 0).value
		var previous: Dictionary = owner.snapshot().value
		_check(not owner.begin_retail_initialization(raw, _raw_pose(), 0).ok, "Reject malformed signed basis.")
		_equal(owner.snapshot().value, previous, "Malformed basis has no mutation.")
		_check(not owner.declare_on_ground(invalid).ok, "Reject malformed timestamp.")
		_equal(owner.snapshot().value, previous, "Malformed timestamp has no mutation.")
	for invalid: Variant in [null, true, 0.0, -1, 4294967296]:
		_check(not State.create(_pose(), _zero(), _zero(), invalid).ok, "Reject malformed uint32 type.")
		_check(not State.create_thing(invalid, 0, 0).ok, "Reject malformed uint32 lineage.")
	var thing: State.Thing = State.create_thing(0x80000003, 0x40, 0).value
	var original: Dictionary = thing.snapshot().value
	for invalid: Variant in [null, true, 0.0, -1, 65536]:
		_check(not thing.add_flags(invalid).ok, "Reject malformed ushort flags.")
		_equal(thing.snapshot().value, original, "Malformed flags have no mutation.")
	for invalid: Variant in [null, [], "pose", {}, {"position_millimeters": _zero()}]:
		var owner: State.Actor = State.create(_pose(), _zero(), _zero(), 0).value
		var original_actor: Dictionary = owner.snapshot().value
		_check(not owner.advance_pose(invalid).ok, "Reject incomplete pose.")
		_equal(owner.snapshot().value, original_actor, "Incomplete pose leaves both buffers.")
	for key: String in ["x", "y", "z"]:
		var velocity: Dictionary = _zero()
		velocity[key] = -2147483649
		var owner: State.Actor = State.create(_pose(), _zero(), _zero(), 0).value
		_check(not owner.add_velocity(velocity).ok, "Reject wide velocity.")
		_equal(owner.snapshot().value.velocity, _zero(), "Malformed add has no prefix mutation.")


func _pose(x: int = 10, y: int = 20, z: int = 30) -> Dictionary:
	return {"position_millimeters": {"x": x, "y": y, "z": z}, "basis_float_bits": _basis()}


func _raw_pose() -> Dictionary:
	return {"position_float_bits": {"x": 0x43905800, "y": 0x43734000, "z": -1054867456}, "basis_float_bits": _basis()}


func _basis() -> Dictionary:
	return {"row0_x": 0x3f800000, "row0_y": 0, "row0_z": 0, "row1_x": 0, "row1_y": 0x3f800000,
		"row1_z": 0, "row2_x": 0, "row2_y": 0, "row2_z": 0x3f800000}


func _zero() -> Dictionary: return {"x": 0, "y": 0, "z": 0}


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
	_completed.append(group)
	print("THING_ACTOR_STATE_SECTION: " + group)


func _verify_source_hashes(expected: Dictionary) -> void:
	for name: String in expected:
		_check(name in ["ThingBaseState.cs", "ThingActorBaseState.cs"], "Admitted source identity path.")
		if name not in ["ThingBaseState.cs", "ThingActorBaseState.cs"]: continue
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
