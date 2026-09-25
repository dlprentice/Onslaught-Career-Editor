# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree

const Camera = preload("res://Client/attached_pan_camera.gd")
const Viewpoint = preload("res://Client/level100_engine_viewpoint.gd")
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


func _result(group: String, name: String, actual: Dictionary, expected: Dictionary) -> void:
	_check(group, name + " success", actual.get("ok"), expected.ok)
	if expected.ok:
		if expected.has("value"):
			_check(group, name + " exact value", actual.get("value"), expected.value)
		if expected.has("hex"):
			_check(group, name + " exact hash", actual.get("hex"), expected.hex)
	else:
		_check(group, name + " error class", actual.get("error_type"), expected.error_type)
		_check(group, name + " error parameter", actual.get("parameter", ""), expected.parameter)
		_check(group, name + " no usable result", actual.has("value") or actual.has("hex"), false)


func _constructor_checks(oracle: Dictionary) -> void:
	_check("constructors", "nonempty fixtures", not oracle.constructors.is_empty(), true)
	_check("constructors", "identity pose", Camera.identity_pose(), oracle.identity_pose)
	for row: Dictionary in oracle.constructors:
		_result("constructors", str(row.duration) + "/" + str(row.lead), Camera.create(row.duration, row.lead), row.expected)
	_completed.append("constructors")


func _scenario_checks(scenarios: Array) -> void:
	_check("state", "nonempty scenarios", not scenarios.is_empty(), true)
	for scenario: Dictionary in scenarios:
		var created: Dictionary = Camera.create(scenario.duration, scenario.lead)
		_check("state", scenario.name + " created", created.ok, true)
		var state: RefCounted = created.value
		var index: int = 0
		for step: Dictionary in scenario.steps:
			var name: String = scenario.name + "/" + str(index) + "/" + step.operation
			var actual: Dictionary = _step(state, step)
			_result("state", name, actual, step.expected)
			var current: Dictionary = state.current_snapshot()
			if step.snapshot == null:
				_check("state", name + " still uninitialized", current.get("ok"), false)
			else:
				_check("state", name + " exact retained snapshot", current.get("value"), step.snapshot)
				var hashed: Dictionary = Camera.compute_hash(current.get("value"))
				_check("hash", name + " hash successful", hashed.get("ok"), true)
				_check("hash", name + " retained hash", hashed.get("hex"), step.hash)
			index += 1
	_completed.append("state")


func _step(state: RefCounted, step: Dictionary) -> Dictionary:
	match step.operation:
		"frame": return state.advance_at_end_of_event_frame(step.frame)
		"sample": return state.sample(step.alpha_bits)
		"world": return state.advance(step.previous, step.current)
		"current": return state.current_snapshot()
		"seed_generation":
			# Test-only counterpart to the C# reflection seed. No restoration or
			# counter mutation method is added to either production camera API.
			var seeded: Dictionary = state.current_snapshot().value
			seeded.reset_generation = step.generation
			state.set("_snapshot", seeded)
			return state.current_snapshot()
	return {"ok": false, "error_type": "FixtureError", "error": "Unknown camera operation."}


func _hash_checks(rows: Array) -> void:
	_check("hash", "nonempty standalone fixtures", not rows.is_empty(), true)
	for row: Dictionary in rows:
		_result("hash", row.name, Camera.compute_hash(row.snapshot), row.expected)
	_completed.append("hash")


func _engine_checks(rows: Array) -> void:
	_check("engine", "nonempty adapter fixtures", not rows.is_empty(), true)
	for row: Dictionary in rows:
		var created: Dictionary = Viewpoint.create(row.near_plane_bits, row.far_plane_bits)
		_check("engine", "created adapter", created.get("ok"), true)
		var state: RefCounted = created.value
		_check("engine", "two slots", state.slot_count(), row.slot_count)
		_check("engine", "initial selection", state.selected_snapshot(), row.initial)
		_check("engine", "initial hash", state.compute_hash().get("hex"), row.initial_hash)
		var index: int = 0
		for item: Dictionary in row.rows:
			var name: String = str(row.near_plane_bits) + "/" + str(index)
			var bound: Dictionary = state.bind(item.camera)
			_check("engine", name + " bind succeeded", bound.get("ok"), true)
			_check("engine", name + " by-value selection", bound.get("value"), item.selected)
			_check("engine", name + " selected snapshot", state.selected_snapshot(), item.selected)
			_check("engine", name + " exact hash", state.compute_hash().get("hex"), item.hash)
			index += 1
	_completed.append("engine")


func _frame(tick: int, elapsed: int) -> Dictionary:
	return {"event_frame": tick, "pan_elapsed_ticks": elapsed, "zoom_permille": 1000,
		"attached_thing": {"thing_id": 7, "pose": Camera.identity_pose(),
			"pan_right": {"x_bits": 0x3f800000, "y_bits": 0, "z_bits": 0}}}


func _rejected(name: String, result: Dictionary) -> void:
	_check("admission", name + " refused", result.get("ok"), false)
	_check("admission", name + " no usable result", result.has("value") or result.has("hex"), false)
	_check("admission", name + " explicit diagnostic", str(result.get("error", "")).is_empty(), false)


func _admission_and_detachment() -> void:
	for invalid: Variant in [null, true, 120.0, "120", -2147483649, 2147483648]:
		_rejected("duration type/width", Camera.create(invalid, 1))
		_rejected("lead type/width", Camera.create(120, invalid))
	var state: RefCounted = Camera.create(120, 1).value
	var first: Dictionary = _frame(0, 0)
	var advanced: Dictionary = state.advance_at_end_of_event_frame(first)
	var before: Dictionary = state.current_snapshot().value
	first.attached_thing.pose.position.x_bits = 0x7f800001
	first.event_frame = 99
	advanced.value.current_frame.attached_thing.thing_id = -1
	advanced.value.previous_pan_pose.up.y_bits = 0
	var captured: Dictionary = state.current_snapshot().value
	captured.previous_frame.attached_thing.pose.forward.z_bits = 0
	_check("detachment", "source and returned snapshots are detached", state.current_snapshot().value, before)
	var sampled: Dictionary = state.sample(0).value
	sampled.pose.position.x_bits = 0x12345678
	_check("detachment", "sample is detached", state.current_snapshot().value, before)
	for invalid: Variant in [null, true, 0.0, -1, 4294967296, "0"]:
		_rejected("alpha carrier", state.sample(invalid))
		for axis: String in ["x_bits", "y_bits", "z_bits"]:
			var frame: Dictionary = _frame(1, 1)
			frame.attached_thing.pose.position[axis] = invalid
			_rejected("vector word " + axis, state.advance_at_end_of_event_frame(frame))
		_check("admission", "invalid raw word preserves state", state.current_snapshot().value, before)
	for key: String in ["event_frame", "pan_elapsed_ticks", "zoom_permille", "attached_thing"]:
		var missing: Dictionary = _frame(1, 1)
		missing.erase(key)
		_rejected("missing frame " + key, state.advance_at_end_of_event_frame(missing))
	for key: String in ["position", "forward", "up"]:
		var missing: Dictionary = _frame(1, 1)
		missing.attached_thing.pose.erase(key)
		_rejected("missing pose " + key, state.advance_at_end_of_event_frame(missing))
	for invalid: Variant in [null, 0, "frame", []]:
		_rejected("frame carrier", state.advance_at_end_of_event_frame(invalid))
	for key: String in ["pan_duration_ticks", "control_view_handoff_tick", "reset_generation", "update_phase", "previous_frame", "current_frame", "previous_pan_pose", "current_pan_pose", "pan_update_scheduled"]:
		var missing: Dictionary = before.duplicate(true)
		missing.erase(key)
		_rejected("missing hashed field " + key, Camera.compute_hash(missing))
	_check("admission", "all refused payloads preserve state", state.current_snapshot().value, before)
	# No Player 1 means no pose facts are read; absent angles are not replaced
	# by invented defaults. Current-only idempotence similarly skips previous.
	var no_player: Dictionary = {"tick": 10, "opening_ticks_remaining": 110, "zoom_permille": 1000, "actors": []}
	var empty: RefCounted = Camera.create(120, 1).value
	_check("world_admission", "no attachment needs no pose facts", empty.advance(no_player, no_player).get("ok"), true)
	var empty_before: Dictionary = empty.current_snapshot().value
	_check("world_admission", "current idempotence skips impossible previous", empty.advance({"opening_ticks_remaining": -2147483648}, no_player).get("value"), empty_before)
	var duplicate: Dictionary = no_player.duplicate(true)
	duplicate.tick = 11
	duplicate.actors = [{"name": "Player 1", "actor_id": 1}, {"name": PackedInt32Array([80, 108, 97, 121, 101, 114, 32, 49]), "actor_id": 2}]
	var rejected: Dictionary = empty.advance(no_player, duplicate)
	_check("world_admission", "duplicate attachment precedes absent pose facts", rejected.get("error_type"), "InvalidOperationException")
	_check("world_admission", "duplicate attachment preserves owner", empty.current_snapshot().value, empty_before)
	var engine: RefCounted = Viewpoint.create(0x3dcccccd, 0x442f0000).value
	var selected: Dictionary = engine.bind({"attached_thing_id": 7}).value
	var initial_selected: Dictionary = engine.selected_snapshot()
	selected.selected_slot_state.player_thing_identity = -1
	selected.selected_slot_state.camera_identity[0] = 0
	_check("detachment", "bound engine selection is detached", engine.selected_snapshot(), initial_selected)
	var hash_before: String = engine.compute_hash().hex
	for invalid: Variant in [-2147483649, 2147483648, 7.0, true, "7"]:
		_rejected("engine identity", engine.bind({"attached_thing_id": invalid}))
		_check("admission", "invalid engine identity preserves hash", engine.compute_hash().hex, hash_before)
	for invalid: Variant in [null, {}, [], "camera"]:
		_rejected("engine carrier", engine.bind(invalid))
	for invalid: Variant in [-1, 4294967296, 0.1, false, null]:
		_rejected("engine near word", Viewpoint.create(invalid, 0))
		_rejected("engine far word", Viewpoint.create(0, invalid))
	_check("engine", "explicit missing attachment clears identity", engine.bind({"attached_thing_id": null}).value.selected_slot_state.player_thing_identity, null)
	_completed.append("admission")


func _decode_transport(value: Variant, key_name: String = "") -> Variant:
	if value is Dictionary:
		var result: Dictionary = {}
		for key: String in value:
			result[key] = _decode_transport(value[key], key)
		return result
	if value is Array:
		if key_name in ["name", "camera_identity"]:
			var units := PackedInt32Array()
			for unit: Variant in value:
				if typeof(unit) != TYPE_FLOAT or not is_finite(unit) or unit != floor(unit) or unit < 0 or unit > 65535:
					_transport_ok = false
					return null
				units.append(int(unit))
			return units
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
		push_error("Attached camera checks require existing oracle and new absolute task-owned report paths.")
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary or not parsed.get("attachedCamera") is Dictionary:
		push_error("Missing attachedCamera oracle object.")
		quit(2)
		return
	var oracle: Dictionary = _decode_transport(parsed.attachedCamera)
	for key: String in ["constructors", "scenarios", "hashes", "engines"]:
		if not oracle.get(key) is Array: _transport_ok = false
	if not _transport_ok:
		push_error("Camera fixture transport is incomplete or loses exact words.")
		quit(2)
		return
	_constructor_checks(oracle)
	_scenario_checks(oracle.scenarios)
	_hash_checks(oracle.hashes)
	_engine_checks(oracle.engines)
	_admission_and_detachment()
	for section: String in ["constructors", "state", "hash", "engine", "admission"]:
		_check("completion", section + " returned", _completed.has(section), true)
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(), "failures": failures,
		"completed": ["attached_camera"] if _completed.size() == 5 else []}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)
