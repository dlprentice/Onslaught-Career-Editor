# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual native registry against unchanged C# constructor, operations and
## ordered full snapshots. Two arguments: private reference and fresh report.
const Registry = preload("res://Core/actor_registry.gd")
const Definitions = preload("res://Core/actor_definitions.gd")
const Manifest = preload("res://Client/actor_definition_manifest.gd")
const Terrain = preload("res://Core/terrain.gd")
const REQUIRED: Array[String] = ["inputs", "definitions", "cases", "detachment", "context_refusals", "lifetime", "read_only"]
var _counts: Dictionary = {}
var _failures: Array[Dictionary] = []
var _completed: Array[String] = []
var _report: String
var _finished: bool = false
var _contexts: Dictionary = {}
var _terrains: Dictionary = {}
var _sets: Array = []
var _cases_completed: int = 0
var _steps_completed: int = 0


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if Engine.is_editor_hint() or DisplayServer.get_name() != "headless" or args.size() != 2 or not _owned_path(args[0]) or not _owned_path(args[1]) or args[0] == args[1] or FileAccess.file_exists(args[1]):
		quit(2)
		return
	_report = args[1]
	create_timer(120.0).timeout.connect(func() -> void:
		if not _finished:
			_failures.append({"group": "completion", "name": "registry harness timed out or aborted"})
			_finish())
	var file := FileAccess.open(args[0], FileAccess.READ)
	if file == null:
		quit(2)
		return
	var reference: Variant = file.get_var(false)
	file.close()
	if not reference is Dictionary or reference.get("schema") != 1 or reference.get("completed") != ["actor_registry_reference"]:
		push_error("Registry reference is incomplete.")
		quit(2)
		return
	var pointer: int = Input.mouse_mode
	for name: String in reference.source_sha256:
		_check("inputs", name + " reference source pin", _sha(FileAccess.get_file_as_bytes("res://../OnslaughtRebuild.Core/" + name)), reference.source_sha256[name])
	var manifest: PackedByteArray = FileAccess.get_file_as_bytes(reference.manifest_path)
	_check("inputs", "pinned manifest bytes", _sha(manifest), reference.manifest_sha256)
	var decoded: Dictionary = Manifest.decode(manifest)
	_check("inputs", "manifest admission", decoded.get("ok"), true)
	if not decoded.get("ok", false):
		_finish()
		return
	_check("inputs", "actual manifest complete definitions", decoded.value.snapshot(), reference.definitions[0])
	decoded.clear()
	for row: Dictionary in reference.terrains:
		var bytes: PackedByteArray = FileAccess.get_file_as_bytes(row.path)
		_check("inputs", "terrain %d source bytes" % row.world, _sha(bytes), row.sha256)
		var admitted: Dictionary = Terrain.from_bytes(bytes, row.world)
		_check("inputs", "terrain %d admission" % row.world, admitted.get("ok"), true)
		if not admitted.get("ok", false):
			_finish()
			return
		_terrains[row.world] = admitted.value
	for row: Dictionary in reference.contexts: _contexts[row.mission_program_world_number] = Definitions.Admission.copy_value(row)
	_completed.append("inputs")
	for row: Dictionary in reference.definitions:
		var admitted: Dictionary = Definitions.create(row.actors, row.spawns, row.waypoint_paths, row.motion_definitions, row.world_number)
		_check("definitions", "set admission", admitted.get("ok"), true)
		if not admitted.get("ok", false):
			_finish()
			return
		_check("definitions", "every immutable input field", admitted.value.snapshot(), row)
		_sets.append(admitted.value)
	_completed.append("definitions")
	var step_count: int = 0
	for row: Dictionary in reference.cases:
		step_count += row.steps.size()
		_run_case(row)
		_cases_completed += 1
		if _cases_completed % 16 == 0: await process_frame
	_check("cases", "all constructor cases completed", _cases_completed, reference.cases.size())
	_check("cases", "all operations completed", _steps_completed, step_count)
	_completed.append("cases")
	if _detachment(): _completed.append("detachment")
	if _context_refusals(): _completed.append("context_refusals")
	var owner_ref: WeakRef = _released_owner()
	await process_frame
	_check("lifetime", "registry owner releases after call stack unwinds", _alive(owner_ref), false)
	_completed.append("lifetime")
	_check("read_only", "manifest bytes unchanged", _sha(FileAccess.get_file_as_bytes(reference.manifest_path)), reference.manifest_sha256)
	for row: Dictionary in reference.terrains: _check("read_only", "terrain %d unchanged" % row.world, _sha(FileAccess.get_file_as_bytes(row.path)), row.sha256)
	_check("read_only", "pointer ownership unchanged", Input.mouse_mode, pointer)
	_completed.append("read_only")
	_sets.clear()
	_contexts.clear()
	_terrains.clear()
	await process_frame
	_finish()


func _context(set_value: RefCounted, terrain: int, support: bool) -> Dictionary:
	var context: Dictionary = Definitions.Admission.copy_value(_contexts[set_value.world_number()])
	context.terrain = _terrains[terrain]
	context.initialize_support = support
	return context


func _run_case(row: Dictionary) -> void:
	var set_value: RefCounted = _sets[row.definition]
	var context: Dictionary = _context(set_value, row.terrain, row.support)
	var input: Variant = Definitions.Admission.copy_value(row.input)
	var result: Dictionary = Registry.restore(set_value, input, context) if row.kind == "restore" else Registry.create(set_value, context)
	_check("construction", row.name + " admission", result.get("ok"), row.result.ok)
	if not row.result.ok:
		_refusal("construction", row.name, result, row.result)
		return
	if not result.get("ok", false):
		_failures.append({"group": "construction", "name": row.name + " unexpected refusal", "actual": str(result)})
		return
	var owner: RefCounted = result.value
	result.clear()
	_compare_result("snapshots", row.name + " initial", owner.snapshot(), row.snapshot)
	for index: int in range(row.steps.size()):
		var step: Dictionary = row.steps[index]
		var args: Array = Definitions.Admission.copy_value(step.args)
		var expected_args: Array = Definitions.Admission.copy_value(args)
		var actual: Dictionary = _operation(owner, set_value, context, step.op, args)
		_compare_result("operations", "%s/%d/%s" % [row.name, index, step.op], actual, step.expected)
		_check("detached_inputs", "%s/%d immutable arguments" % [row.name, index], args, expected_args)
		_compare_result("snapshots", "%s/%d after operation including refusal" % [row.name, index], owner.snapshot(), step.snapshot)
		_steps_completed += 1


func _operation(owner: RefCounted, set_value: RefCounted, context: Dictionary, op: String, args: Array) -> Dictionary:
	if op == "restore_snapshot":
		var snapshot: Dictionary = owner.snapshot()
		if not snapshot.ok: return snapshot
		var restored: Dictionary = Registry.restore(set_value, snapshot.value, context)
		return restored.value.snapshot() if restored.ok else restored
	if op == "construction_begin":
		var state: Dictionary = owner.get_construction_state(args[0])
		return state.value.begin_retail_initialization(args[1], args[1], args[2]) if state.ok else state
	var result: Dictionary = owner.callv(op, args)
	if result.get("ok", false) and op in ["get_construction_state", "get_plane_state"]:
		return result.value.snapshot()
	return result


func _detachment() -> bool:
	var set_value: RefCounted = _sets[0]
	var context: Dictionary = _context(set_value, 100, true)
	var created: Dictionary = Registry.create(set_value, context)
	_check("detachment", "registry admission", created.ok, true)
	if not created.ok: return false
	var owner: RefCounted = created.value
	created.clear()
	var initial: Dictionary = owner.snapshot().value
	var changed: Dictionary = owner.snapshot().value
	changed.actors[0].name[0] = 0
	changed.actors[0].pose.position_millimeters.x = -1234567
	changed.base_states[0].state.current_pose.basis_float_bits.row0_x = 0
	changed.actors.clear()
	changed.base_states.clear()
	_check("detachment", "snapshot mutations cannot affect owner", owner.snapshot().value, initial)
	var actor: Dictionary = owner.get_actor(1).value
	actor.name[0] = 0
	actor.pose.linear_velocity_millimeters_per_tick.x = int(0x7fffffff)
	_check("detachment", "actor projection is detached", owner.get_actor(1).value, initial.actors[0])
	var base: Dictionary = owner.get_base_state(1).value
	base.old_pose.position_millimeters.x += 1
	_check("detachment", "base projection is detached", owner.get_base_state(1).value, initial.base_states[0].state)
	var known: PackedInt32Array = context.mission_program_names[0].duplicate()
	context.mission_program_names.clear()
	context.contact_definitions[0].definition_name[0] = 0
	context.contact_definitions.clear()
	_check("detachment", "copied program context survives caller mutation", owner.set_actor_script(1, known).ok, true)
	var restored: Dictionary = Registry.restore(set_value, initial, _context(set_value, 100, true))
	_check("detachment", "restore admission", restored.ok, true)
	if not restored.ok: return false
	var copy: RefCounted = restored.value
	restored.clear()
	initial.actors[0].name[0] = 0
	initial.base_states[0].state.velocity.x = 88
	_check("detachment", "restore owns snapshot records", copy.get_actor(1).value, set_value_to_initial_actor(set_value))
	var trainer: Dictionary = owner.get_thing_ref("Air Trainer")
	_check("detachment", "raw Plane actor resolved", trainer.ok and trainer.value != null, true)
	if trainer.ok and trainer.value != null:
		var first: Dictionary = owner.get_plane_state(trainer.value)
		var second: Dictionary = owner.get_plane_state(trainer.value)
		_check("detachment", "Plane getter retains same mutable allocation", first.ok and second.ok and first.value == second.value, true)
	var hit: Dictionary = owner.report_hit(1, null, 4)
	_check("detachment", "hit produces a fact", hit.ok, true)
	var facts: Dictionary = owner.drain_facts()
	_check("detachment", "one detached drained fact", facts.value.size(), 1)
	facts.value[0].other_thing_type_mask = 8
	_check("detachment", "draining cleared only the internal queue", owner.drain_facts().value, [])
	return true


func set_value_to_initial_actor(set_value: RefCounted) -> Dictionary:
	# Call a fresh admitted owner rather than reverse a seated pose from a
	# definition. This also catches accidentally shared mutable base state.
	var fresh: Dictionary = Registry.create(set_value, _context(set_value, 100, true))
	return fresh.value.get_actor(1).value


func _context_refusals() -> bool:
	var set_value: RefCounted = _sets[0]
	var complete: Dictionary = _context(set_value, 100, true)
	for context: Variant in [null, {}, {"terrain": _terrains[100], "initialize_support": true}]:
		var result: Dictionary = Registry.create(set_value, context)
		_check("context_refusals", "incomplete batch refuses", result.get("ok"), false)
		_check("context_refusals", "incomplete batch has no owner", result.has("value"), false)
	for field: String in ["mission_program_names", "contact_definitions"]:
		var context: Dictionary = complete.duplicate(true)
		context[field] = []
		var result: Dictionary = Registry.create(set_value, context)
		_check("context_refusals", field + " requires admitted full batch", result.get("error_type"), "MissingDependency")
	var context: Dictionary = complete.duplicate(true)
	context.mission_program_world_number = 110
	_check("context_refusals", "program world mismatch refuses", Registry.create(set_value, context).get("error_type"), "MissingDependency")
	context = complete.duplicate(true)
	context.mission_program_names.append(context.mission_program_names[0].duplicate())
	_check("context_refusals", "duplicate names compare UTF16 contents", Registry.create(set_value, context).get("error_type"), "ArgumentException")
	_check("context_refusals", "definitions null precedes context", Registry.create(null, null).get("parameter"), "definitions")
	context = complete.duplicate(true)
	context.terrain = null
	_check("context_refusals", "terrain null precedes snapshot", Registry.restore(set_value, null, context).get("parameter"), "terrain")
	return true


func _released_owner() -> WeakRef:
	var set_value: RefCounted = _sets[0]
	var created: Dictionary = Registry.create(set_value, _context(set_value, 100, true))
	return weakref(created.value)


func _compare_result(group: String, name: String, actual: Dictionary, expected: Dictionary) -> void:
	_check(group, name + " admission", actual.get("ok"), expected.ok)
	if not expected.ok:
		_refusal(group, name, actual, expected)
	elif actual.get("ok", false):
		_check(group, name + " exact value", actual.get("value"), expected.value)


func _refusal(group: String, name: String, actual: Dictionary, expected: Dictionary) -> void:
	_check(group, name + " exception", actual.get("error_type"), expected.error_type)
	_check(group, name + " parameter", actual.get("parameter", ""), expected.parameter)
	_check(group, name + " no successful value", actual.has("value"), false)


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	_counts[group] = _counts.get(group, 0) + 1
	if actual == expected: return
	var row: Dictionary = {"group": group, "name": name, "difference": _difference(actual, expected)}
	_failures.append(row)
	if _failures.size() <= 12: push_error(JSON.stringify(row))


static func _difference(actual: Variant, expected: Variant, path: String = "") -> Dictionary:
	if actual is Dictionary and expected is Dictionary:
		for key: Variant in expected:
			if not actual.has(key): return {"path": path + "/" + str(key), "missing": true}
			if actual[key] != expected[key]: return _difference(actual[key], expected[key], path + "/" + str(key))
		return {"path": path, "actual_keys": str(actual.keys()), "expected_keys": str(expected.keys())}
	if (actual is Array or actual is PackedInt32Array) and (expected is Array or expected is PackedInt32Array):
		if actual.size() != expected.size(): return {"path": path, "actual_size": actual.size(), "expected_size": expected.size()}
		for index: int in range(actual.size()):
			if actual[index] != expected[index]: return _difference(actual[index], expected[index], path + "/" + str(index))
	return {"path": path, "actual": str(actual).substr(0, 500), "expected": str(expected).substr(0, 500)}


func _finish() -> void:
	if _finished: return
	_finished = true
	for group: String in REQUIRED:
		if group not in _completed: _failures.append({"group": "completion", "name": "missing " + group})
	var report: Dictionary = {"schema": 1, "failure_count": _failures.size(), "failures": _failures,
		"counts": _counts, "completed": _completed, "cases": _cases_completed, "operations": _steps_completed,
		"script_sha256": _sha(FileAccess.get_file_as_bytes("res://Core/actor_registry.gd"))}
	var file := FileAccess.open(_report, FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	var total: int = 0
	for value: int in _counts.values(): total += value
	print("ACTOR_REGISTRY_CHECKS: %d assertions, %d cases, %d operations, %d failures; %s" % [total, _cases_completed, _steps_completed, _failures.size(), _report])
	quit(0 if _failures.is_empty() else 1)


static func _sha(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	if not bytes.is_empty(): hash.update(bytes)
	return hash.finish().hex_encode()


static func _alive(reference: WeakRef) -> bool:
	return reference.get_ref() != null


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
