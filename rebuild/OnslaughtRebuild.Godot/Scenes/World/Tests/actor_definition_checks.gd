# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Exact actor-definition/manifest values and identity bytes; two arguments:
## an existing private reference.variant and a fresh worktree-local report.
const Definitions = preload("res://Core/actor_definitions.gd")
const Manifest = preload("res://Client/actor_definition_manifest.gd")
const REQUIRED: Array[String] = ["manifest", "definitions", "lookups", "detachment", "refusals", "read_only"]
var _counts: Dictionary = {}
var _completed: Array[String] = []
var _failures: Array[Dictionary] = []
var _report: String
var _finished: bool = false
var _identity_bytes: int = 0
var _case_counts: Dictionary = {}


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if Engine.is_editor_hint() or DisplayServer.get_name() != "headless" or args.size() != 2 \
		or not _owned_path(args[0]) or not _owned_path(args[1]) or args[0] == args[1] or FileAccess.file_exists(args[1]):
		quit(2)
		return
	_report = args[1]
	create_timer(120.0).timeout.connect(func() -> void:
		if not _finished:
			_failures.append({"group": "completion", "name": "actor-definition harness timed out"})
			_finish())
	var file := FileAccess.open(args[0], FileAccess.READ)
	if file == null:
		quit(2)
		return
	var reference: Variant = file.get_var(false)
	file.close()
	if not reference is Dictionary or reference.get("schema") != 1 or reference.get("completed") != ["actor_definition_reference"]:
		push_error("Actor definition reference is incomplete.")
		quit(2)
		return
	var pointer: int = Input.mouse_mode
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(reference.manifest_path)
	_check("read_only", "manifest input identity", _sha(bytes), reference.manifest_sha256)
	var decoded: Dictionary = Manifest.decode(bytes)
	_check("manifest", "pinned manifest admitted", decoded.get("ok"), true)
	if not decoded.get("ok", false):
		_failures.append({"group": "manifest", "name": "decode detail", "actual": str(decoded)})
		_finish()
		return
	var set_value: RefCounted = decoded.value
	decoded.clear()
	_check("manifest", "all original definition records and exact raw words", set_value.snapshot(), reference.actual)
	_check("manifest", "unchanged identity bytes", set_value.canonical_bytes(), reference.actual_bytes)
	_identity_bytes += reference.actual_bytes.size()
	_check("manifest", "unchanged original definition hash", set_value.identity_sha256(), reference.actual.identity_sha256)
	_check("manifest", "world number retained", set_value.world_number(), reference.actual.world_number)
	var allegiance: Dictionary = Manifest.decode_authored_allegiance(bytes)
	_check("manifest", "same manifest allegiance admitted", allegiance.get("ok"), true)
	if not allegiance.get("ok", false):
		_finish()
		return
	_check("manifest", "only actual base-world allegiance records", allegiance.value, reference.allegiance)
	_check("manifest", "forty-four actor definitions", set_value.actors().size(), 44)
	_check("manifest", "ten spawn definitions", set_value.spawns().size(), 10)
	_check("manifest", "eight ordered waypoint paths", set_value.waypoint_paths().size(), 8)
	_check("manifest", "five motion definitions", set_value.motion_definitions().size(), 5)
	_completed.append("manifest")
	if _definition_cases(reference.cases, reference.case_counts): _completed.append("definitions")
	if _lookup_cases(set_value, reference.lookups): _completed.append("lookups")
	if _detachment_cases(set_value, reference.actual): _completed.append("detachment")
	if _refusal_cases(bytes, reference.manifest_refusals): _completed.append("refusals")
	var owner_ref: WeakRef = weakref(set_value)
	set_value = null
	_check("read_only", "definition owner releases without a cycle", _alive(owner_ref), false)
	_check("read_only", "retained source bytes unchanged", _sha(FileAccess.get_file_as_bytes(reference.manifest_path)), reference.manifest_sha256)
	_check("read_only", "pointer ownership unchanged", Input.mouse_mode, pointer)
	_completed.append("read_only")
	await process_frame
	_finish()


func _definition_cases(cases: Array, expected_counts: Dictionary) -> bool:
	var schemas: Dictionary = {}
	var accepted: int = 0
	var refused: int = 0
	for row: Dictionary in cases:
		var input: Dictionary = Definitions.Admission.copy_value(row.input)
		var result: Dictionary = Definitions.create(input.actors, input.spawns, input.waypoint_paths, input.motion_definitions, input.world_number)
		_check("definition", row.name + " admission", result.get("ok"), row.ok)
		if not row.ok:
			refused += 1
			_check("refusal", row.name + " exception", result.get("error_type"), row.error_type)
			_check("refusal", row.name + " parameter", result.get("parameter", ""), row.parameter)
			_check("refusal", row.name + " no partial owner", result.has("value"), false)
			continue
		if not result.get("ok", false): continue
		accepted += 1
		var owner: RefCounted = result.value
		result.clear()
		_check("identity", row.name + " complete value projection", owner.snapshot(), row.snapshot)
		var canonical: PackedByteArray = owner.canonical_bytes()
		_identity_bytes += canonical.size()
		_check("identity", row.name + " every canonical byte", canonical, row.bytes)
		_check("identity", row.name + " original C# hash", owner.identity_sha256(), row.snapshot.identity_sha256)
		_check("identity", row.name + " hash actual native bytes", _sha(canonical), row.snapshot.identity_sha256)
		if not _stored_lookup_cases(owner, row.snapshot, row.name): return false
		schemas[canonical.decode_s32("ONSLAUGHT-LEVEL100-ACTOR-DEFINITIONS".length())] = true
		canonical[0] ^= 255
		_check("detachment", row.name + " identity buffer is detached", owner.canonical_bytes(), row.bytes)
		# Mutate the supplied transport after admission, including packed UTF16
		# and nested raw-word records. Dictionary.duplicate(true) alone is not
		# relied on to detach packed arrays.
		if input.actors != null and not input.actors.is_empty():
			var actor: Dictionary = input.actors[0]
			if actor.definition_identity != null and not actor.definition_identity.is_empty(): actor.definition_identity[0] ^= 1
			actor.initial_pose.basis_float_bits.row0_x ^= 1
			input.actors.clear()
		if input.spawns != null: input.spawns.clear()
		if input.waypoint_paths != null: input.waypoint_paths.clear()
		if input.motion_definitions != null: input.motion_definitions.clear()
		_check("detachment", row.name + " caller inputs cannot change set or stored identity", owner.snapshot(), row.snapshot)
		owner = null
	_check("identity", "formats six seven and eight all exercised", schemas.size(), 3)
	_case_counts = {"accepted": accepted, "refused": refused}
	_check("definition", "every accepted fixture case completed", accepted, expected_counts.accepted)
	_check("definition", "every refused fixture case completed", refused, expected_counts.refused)
	return true


func _stored_lookup_cases(owner: RefCounted, snapshot: Dictionary, name: String) -> bool:
	# Fresh packed UTF-16 carriers must select by ordinal contents. In particular,
	# high and low lone surrogates remain distinct keys even though BinaryWriter's
	# UTF-8 identity encoding replaces either one with U+FFFD.
	for actor: Dictionary in snapshot.actors:
		var key: PackedInt32Array = actor.definition_identity.duplicate()
		var result: Dictionary = owner.get_actor_definition(key)
		_check("stored_lookup", name + " actor admission", result.get("ok"), true)
		if not result.get("ok", false): return false
		_check("stored_lookup", name + " actor exact record", result.value, actor)
		key[0] ^= 1
		result.value.definition_identity[0] ^= 1
		result.value.initial_pose.position_millimeters.x ^= 1
	for spawn: Dictionary in snapshot.spawns:
		var result: Dictionary = owner.get_spawn_definition(spawn.definition_identity.duplicate())
		_check("stored_lookup", name + " spawn exact record", result.get("value"), spawn)
		var request: Dictionary = owner.find_spawn_definition(spawn.owner_definition_identity.duplicate(),
			spawn.definition_name.duplicate(), spawn.spawner_name.duplicate(), spawn.script_name.duplicate())
		_check("stored_lookup", name + " request exact record", request.get("value"), spawn)
	for path: Dictionary in snapshot.waypoint_paths:
		var result: Dictionary = owner.get_waypoint_path(path.name.duplicate())
		_check("stored_lookup", name + " path exact record", result.get("value"), path)
	for motion: Dictionary in snapshot.motion_definitions:
		var result: Dictionary = owner.get_motion_definition(motion.definition_name.duplicate())
		_check("stored_lookup", name + " motion exact record", result.get("value"), motion)
		var found: Dictionary = owner.find_motion_definition(motion.definition_name.duplicate())
		_check("stored_lookup", name + " optional motion exact record", found.get("value"), motion)
	_check("detachment", name + " lookup inputs and returned records are detached", owner.snapshot(), snapshot)
	return true


func _lookup_cases(owner: RefCounted, cases: Array) -> bool:
	for index: int in range(cases.size()):
		var row: Dictionary = cases[index]
		var result: Dictionary
		if row.method == "chain_point":
			var path: Dictionary = owner.get_waypoint_path(row.arguments[0])
			if not path.get("ok", false): return false
			result = Definitions.chain_point(path.value, row.arguments[1])
		else:
			result = owner.callv(row.method, row.arguments)
		_check("lookup", "%d %s admission" % [index, row.method], result.get("ok"), row.ok)
		if row.ok:
			_check("lookup", "%d %s exact selected record" % [index, row.method], result.get("value"), row.value)
		else:
			_check("lookup", "%d %s exception" % [index, row.method], result.get("error_type"), row.error_type)
			_check("lookup", "%d %s parameter" % [index, row.method], result.get("parameter", ""), row.parameter)
	return true


func _detachment_cases(owner: RefCounted, original: Dictionary) -> bool:
	var snapshot: Dictionary = owner.snapshot()
	snapshot.actors[0].definition_identity[0] ^= 1
	snapshot.actors[0].authored_transform.retail_basis_float_bits.row0_x ^= 1
	snapshot.spawns[0].initial_pose.position_millimeters.x ^= 1
	snapshot.waypoint_paths[0].points.clear()
	snapshot.motion_definitions.clear()
	_check("detachment", "complete returned snapshot is detached", owner.snapshot(), original)
	for method: String in ["actors", "spawns", "waypoint_paths", "motion_definitions"]:
		var records: Array = owner.call(method)
		records.clear()
		_check("detachment", "returned " + method + " list is detached", owner.snapshot(), original)
	for row: Dictionary in original.motion_definitions:
		var fetched: Dictionary = owner.get_motion_definition(row.definition_name)
		if fetched.value.weapon_mounts != null:
			if not fetched.value.weapon_mounts.is_empty(): fetched.value.weapon_mounts[0].use.definition_name[0] ^= 1
			fetched.value.weapon_mounts.clear()
	_check("detachment", "lookup mount values are detached", owner.snapshot(), original)
	for row: Dictionary in original.spawns:
		var fetched: Dictionary = owner.get_spawn_definition(row.definition_identity)
		if fetched.value.spawner_exit_waypoints != null:
			fetched.value.spawner_exit_waypoints[0].model_transform.local_position_float_bits.x ^= 1
			fetched.value.spawner_exit_waypoints.clear()
	_check("detachment", "lookup exit values are detached", owner.snapshot(), original)
	var invalid: Dictionary = Definitions.Admission.copy_value(original)
	invalid.actors[0].authored_order = 1.0
	_check("refusal", "float is not an Int32 field", Definitions.create(invalid.actors, invalid.spawns, invalid.waypoint_paths, invalid.motion_definitions).get("ok"), false)
	invalid = Definitions.Admission.copy_value(original)
	invalid.actors[0].initial_health = 0x80000000
	_check("refusal", "wide integer is not an Int32 field", Definitions.create(invalid.actors, invalid.spawns, invalid.waypoint_paths, invalid.motion_definitions).get("ok"), false)
	invalid = Definitions.Admission.copy_value(original)
	invalid.actors[0].erase("name")
	_check("refusal", "missing name is not an implicit empty name", Definitions.create(invalid.actors, invalid.spawns, invalid.waypoint_paths, invalid.motion_definitions).get("ok"), false)
	return true


func _refusal_cases(bytes: PackedByteArray, cases: Array) -> bool:
	for row: Dictionary in cases:
		var changed: Variant
		match row.kind:
			"null": changed = null
			"prefix": changed = bytes.slice(0, row.amount)
			"oversize":
				changed = PackedByteArray()
				changed.resize(row.amount)
			"append":
				changed = bytes.duplicate()
				changed.append(0)
			"flip":
				changed = bytes.duplicate()
				changed[row.amount] ^= 1
			_: return false
		var result: Dictionary = Manifest.decode_authored_allegiance(changed) if row.allegiance else Manifest.decode(changed)
		_check("manifest_refusal", row.kind + " failure", result.get("ok"), false)
		_check("manifest_refusal", row.kind + " exact exception", result.get("error_type"), row.error_type)
		_check("manifest_refusal", row.kind + " cannot produce partial projection", result.has("value"), false)
	return true


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	_counts[group] = _counts.get(group, 0) + 1
	if actual == expected: return
	var failure: Dictionary = {"group": group, "name": name, "difference": _difference(actual, expected)}
	_failures.append(failure)
	if _failures.size() <= 10: push_error(JSON.stringify(failure))


static func _difference(actual: Variant, expected: Variant, path: String = "") -> Dictionary:
	if actual is Dictionary and expected is Dictionary:
		for key: Variant in expected:
			if not actual.has(key): return {"path": path + "/" + str(key), "missing": true}
			if actual[key] != expected[key]: return _difference(actual[key], expected[key], path + "/" + str(key))
		return {"path": path, "actual_keys": str(actual.keys()), "expected_keys": str(expected.keys())}
	if (actual is Array or actual is PackedByteArray or actual is PackedInt32Array) and (expected is Array or expected is PackedByteArray or expected is PackedInt32Array):
		if actual.size() != expected.size(): return {"path": path, "actual_size": actual.size(), "expected_size": expected.size()}
		for index: int in range(actual.size()):
			if actual[index] != expected[index]: return _difference(actual[index], expected[index], path + "/" + str(index))
	return {"path": path, "actual": str(actual).substr(0, 300), "expected": str(expected).substr(0, 300)}


func _finish() -> void:
	if _finished: return
	_finished = true
	for group: String in REQUIRED:
		if not _completed.has(group): _failures.append({"group": "completion", "name": "missing " + group})
	var report: Dictionary = {"schema": 1, "failure_count": _failures.size(), "failures": _failures,
		"counts": _counts, "completed": _completed, "case_counts": _case_counts, "identity_bytes_compared": _identity_bytes}
	var output := FileAccess.open(_report, FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "  "))
	output.close()
	var total: int = 0
	for count: int in _counts.values(): total += count
	print("ACTOR_DEFINITION_CHECKS: %d assertions, %d canonical bytes, %d failures; %s" % [total, _identity_bytes, _failures.size(), _report])
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
