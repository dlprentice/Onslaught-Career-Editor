# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Level100ActorRegistry.cs's mutable identity/lifecycle owner. Definitions,
## Thing.Actor storage, PC24 poses and Plane arithmetic remain their existing
## native owners. This module selects no frame, AI, collision or mission policy.
##
## create(definitions, context) / restore(definitions, snapshot, context) return
## {ok,value:Registry}; every Registry method returns an explicit Result too.
## Context is one already-admitted immutable batch with fields:
## terrain: Terrain.Heightfield; initialize_support: bool;
## mission_program_world_number: Int32; mission_program_names: Array of UTF-16
## names, or null only for a world unsupported by ProgramNamesFor;
## contact_definitions: the COMPLETE admitted catalog, each row containing
## definition_name, kind and maximum_life_float_bits. Callers retain catalog
## byte/provenance admission; omission is not permission to invent a fallback.
## The batch is copied once. It neither loads files nor recreates a catalog.
## Text uses detached UTF-16, ActorId is Int32 and snapshots follow state_hasher.
const Definitions = preload("res://Core/actor_definitions.gd")
const State = preload("res://Core/thing_actor_state.gd")
const MeshPose = preload("res://Core/retail_mesh_part_pose.gd")
const PlaneMotion = preload("res://Core/retail_plane_motion.gd")
const Euler = preload("res://Core/retail_unit_euler.gd")
const Terrain = preload("res://Core/terrain.gd")
const F = preload("res://Core/retail_float24.gd")
const Values = preload("res://Core/retail_career_values.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const PROVEN_BITS: int = 12
const MARKED_OBJECTIVE: int = 0x20
const INT64_MAX: int = 9223372036854775807
const INT64_MIN: int = -9223372036854775807 - 1
enum Lifecycle { ALIVE = 0, STARTED_DYING = 1, DESTROYED = 2, DIED_AWAITING_SHUTDOWN = 3 }
enum FactKind { HIT = 1, STARTED_DYING = 2, DIED = 3, TRIGGER_DISPATCH_READY = 4 }


static func create(definitions: Variant, context: Variant) -> Dictionary:
	var admitted: Dictionary = _context(definitions, context)
	if not admitted.ok: return admitted
	var registry: Registry = admitted.value
	var result: Dictionary = registry._create_authored()
	return Values.success(registry) if result.ok else result


static func restore(definitions: Variant, snapshot: Variant, context: Variant) -> Dictionary:
	var admitted: Dictionary = _context(definitions, context)
	if not admitted.ok: return admitted
	var registry: Registry = admitted.value
	var result: Dictionary = registry._restore(snapshot)
	return Values.success(registry) if result.ok else result


static func _context(definitions: Variant, context: Variant) -> Dictionary:
	if definitions == null: return Admission.failure("ArgumentNullException", "Value cannot be null.", "definitions")
	if not definitions is Definitions.DefinitionSet: return State.Laws.transport("definitions")
	if not context is Dictionary: return Admission.failure("MissingDependency", "Registry construction requires its complete immutable context batch.", "context")
	if context.get("terrain") == null: return Admission.failure("ArgumentNullException", "Value cannot be null.", "terrain")
	if not context.terrain is Terrain.Heightfield or not context.get("initialize_support") is bool: return State.Laws.transport("context")
	if context.get("mission_program_world_number") != definitions.world_number() or not context.has("mission_program_names"):
		return Admission.failure("MissingDependency", "Mission program names must belong to the definition world's admitted program set.", "context")
	var names: Variant = context.mission_program_names
	if definitions.world_number() in [100, 110, 200, 300]:
		if not names is Array or names.is_empty(): return Admission.failure("MissingDependency", "The complete admitted mission program names are required.", "context")
	elif names != null:
		return Admission.failure("ArgumentException", "Unsupported mission worlds must retain the ProgramNamesFor refusal.", "context")
	if not context.get("contact_definitions") is Array or context.contact_definitions.is_empty():
		return Admission.failure("MissingDependency", "The complete admitted contact definition catalog is required.", "context")
	var programs: Variant = null
	if names != null:
		programs = {}
		for name: Variant in names:
			var text: Dictionary = Admission.required_text(name, "context")
			if not text.ok: return text
			var key: String = Definitions.Admission.key(text.value)
			if programs.has(key): return Admission.failure("ArgumentException", "Duplicate mission program name.", "context")
			programs[key] = true
	var contacts: Dictionary = {}
	for row: Variant in context.contact_definitions:
		if not row is Dictionary or not Values.is_int32(row.get("kind")) or row.kind not in [0, 1, 2, 3] or not State.Laws.finite_word(row.get("maximum_life_float_bits")):
			return State.Laws.transport("context")
		var text: Dictionary = Admission.required_text(row.get("definition_name"), "context")
		if not text.ok: return text
		var key: String = Definitions.Admission.key(text.value)
		if contacts.has(key): return Admission.failure("ArgumentException", "Duplicate contact definition name.", "context")
		contacts[key] = {"kind": row.kind, "maximum_life_float_bits": row.maximum_life_float_bits}
	var water: Dictionary = State.Laws.round_int32(float(Terrain.PLAYER_START_REFERENCE_ELEVATION_MILLIMETERS)
		- F.read_word(context.terrain.metadata().water_level_bits) * 1000.0)
	if not water.ok: return water
	var registry := Registry.new()
	registry._definitions = definitions
	registry._terrain = context.terrain
	registry._initialize_support = context.initialize_support
	registry._programs = programs
	registry._contacts = contacts
	registry._water_elevation = water.value
	return Values.success(registry)


class Admission extends RefCounted:
	static func required_text(value: Variant, parameter: String) -> Dictionary:
		if value == null: return failure("ArgumentNullException", "Value cannot be null.", parameter)
		var text: Dictionary = Text.units(value)
		if not text.ok: return text
		if text.value.is_empty(): return failure("ArgumentException", "The value cannot be an empty string.", parameter)
		return text


	static func text_equals(left: Variant, right: Variant) -> bool:
		var a: Dictionary = Text.units(left)
		var b: Dictionary = Text.units(right)
		return a.ok and b.ok and a.value == b.value


	static func failure(kind: String, reason: Variant, parameter: String = "") -> Dictionary:
		return Definitions.Admission.failure(kind, reason, parameter)


class Registry extends RefCounted:
	var _definitions: Definitions.DefinitionSet
	var _terrain: Terrain.Heightfield
	var _initialize_support: bool
	var _programs: Variant
	var _contacts: Dictionary
	var _water_elevation: int
	var _actors: Dictionary = {}
	var _pending_facts: Array[Dictionary] = []
	var _next_actor_id: int = 1
	var _next_fact_sequence: int = 1

	func definitions() -> Dictionary:
		return Values.success(_definitions)

	func snapshot() -> Dictionary:
		var actors: Array[Dictionary] = []
		var bases: Array[Dictionary] = []
		for id: int in _ids():
			var actor: Dictionary = _snapshot_actor(_actors[id])
			if not actor.ok: return actor
			var base: Dictionary = _actors[id].base_state.snapshot()
			if not base.ok: return base
			actors.append(actor.value)
			bases.append({"actor_id": id, "state": base.value})
		return Values.success({"definition_set_identity_sha256": _definitions.identity_sha256(), "next_actor_id": _next_actor_id,
			"next_fact_sequence": _next_fact_sequence, "actors": actors, "pending_facts": _sorted_facts(), "base_states": bases})

	func get_thing_ref(name: Variant) -> Dictionary:
		var text: Dictionary = Admission.required_text(name, "name")
		if not text.ok: return text
		var matches: Array[int] = []
		for id: int in _ids():
			if Admission.text_equals(_actors[id].name, text.value): matches.append(id)
		return Values.success(matches[0] if matches.size() == 1 else null)

	func get_actor(actor_id: Variant) -> Dictionary:
		var actor: Dictionary = _require(actor_id)
		return _snapshot_actor(actor.value) if actor.ok else actor

	func get_base_state(actor_id: Variant) -> Dictionary:
		var actor: Dictionary = _require(actor_id)
		return actor.value.base_state.snapshot() if actor.ok else actor

	## Internal native composition seam: the original guarded getter returns
	## this exact allocation, never a second state restored from a projection.
	func get_construction_state(actor_id: Variant) -> Dictionary:
		if _definitions.world_number() != 110 or _initialize_support:
			return Admission.failure("InvalidOperationException", "Retail construction state belongs to the World110 construction route.")
		var actor: Dictionary = _require(actor_id)
		return Values.success(actor.value.base_state) if actor.ok else actor

	func get_plane_state(actor_id: Variant) -> Dictionary:
		var actor: Dictionary = _require(actor_id)
		if not actor.ok: return actor
		if not _is_plane(actor.value.definition_name) or not actor.value.base_state.has_retail_plane_motion().value:
			return Admission.failure("InvalidOperationException", "The actor has no admitted Level100 Plane state.")
		return Values.success(actor.value.base_state)

	func get_pose(actor_id: Variant) -> Dictionary:
		var state: Dictionary = get_base_state(actor_id)
		return Values.success(_to_pose(state.value)) if state.ok else state

	func get_health(actor_id: Variant) -> Dictionary: return _scalar(actor_id, "health")
	func is_active(actor_id: Variant) -> Dictionary: return _scalar(actor_id, "active")
	func get_lifecycle(actor_id: Variant) -> Dictionary: return _scalar(actor_id, "lifecycle")
	func flag_word(actor_id: Variant) -> Dictionary: return _scalar(actor_id, "flag_word")
	func get_thing_type_mask(actor_id: Variant) -> Dictionary:
		var state: Dictionary = get_base_state(actor_id)
		return Values.success(state.value.thing_type_mask & PROVEN_BITS) if state.ok else state

	func activate(actor_id: Variant) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		if found.value.lifecycle == Lifecycle.DESTROYED: return Admission.failure("InvalidOperationException", "A destroyed Level 100 actor cannot be activated.")
		found.value.active = true
		return Values.success()

	func deactivate(actor_id: Variant) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var actor: Dictionary = found.value
		actor.active = false
		if actor.trigger != null and actor.trigger_entered:
			actor.trigger_event_dispatched = true
			actor.is_objective = false
		return Values.success()

	func set_objective(actor_id: Variant, objective: Variant) -> Dictionary:
		if not objective is bool: return State.Laws.transport("objective")
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var actor: Dictionary = found.value
		if objective and actor.lifecycle == Lifecycle.DESTROYED: return Admission.failure("InvalidOperationException", "A destroyed Level 100 actor cannot become an objective.")
		# RetailSetObjective.Mark/Unmark's OR/AND law. This transient word is
		# intentionally distinct from the existing compatibility snapshot bool.
		actor.flag_word = actor.flag_word | MARKED_OBJECTIVE if objective else actor.flag_word & ~MARKED_OBJECTIVE
		actor.is_objective = (actor.flag_word & MARKED_OBJECTIVE) != 0
		return Values.success()

	func set_actor_script(actor_id: Variant, script_name: Variant) -> Dictionary:
		var name: Dictionary = Admission.required_text(script_name, "scriptName")
		if not name.ok: return name
		var known: Dictionary = _known_program(name.value)
		if not known.ok: return known
		if not known.value:
			return Admission.failure("InvalidOperationException", Definitions.Admission.message(["Unknown Level ", str(_definitions.world_number()), " script '", name.value, "'."]))
		var actor: Dictionary = _mutable(actor_id)
		if not actor.ok: return actor
		actor.value.script_name = name.value
		return Values.success()

	func set_pose(actor_id: Variant, pose: Variant) -> Dictionary: return _change_pose(actor_id, pose, "reset_pose")
	func advance_pose(actor_id: Variant, pose: Variant) -> Dictionary: return _change_pose(actor_id, pose, "advance_pose")
	func update_current_pose(actor_id: Variant, pose: Variant) -> Dictionary: return _change_pose(actor_id, pose, "update_current_pose")
	func advance_low_fidelity_position(actor_id: Variant, position: Variant) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var moved: Dictionary = found.value.base_state.advance_low_fidelity_position(position)
		return found.value.base_state.set_angular_velocity(State.Laws.zero()) if moved.ok else moved

	func stop_motion(actor_id: Variant) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var stopped: Dictionary = found.value.base_state.stop()
		return found.value.base_state.set_angular_velocity(State.Laws.zero()) if stopped.ok else stopped

	func make_visible(actor_id: Variant) -> Dictionary: return _base_call(actor_id, "make_visible")
	func make_invisible(actor_id: Variant) -> Dictionary: return _base_call(actor_id, "make_invisible")
	func declare_on_ground(actor_id: Variant, bits: Variant) -> Dictionary: return _base_call(actor_id, "declare_on_ground", [bits])
	func declare_in_water(actor_id: Variant, bits: Variant) -> Dictionary: return _base_call(actor_id, "declare_in_water", [bits])
	func declare_on_object(actor_id: Variant, bits: Variant) -> Dictionary: return _base_call(actor_id, "declare_on_object", [bits])

	func set_health(actor_id: Variant, health: Variant) -> Dictionary:
		if not Values.is_int32(health): return State.Laws.transport("health")
		if health < 0: return Admission.failure("ArgumentOutOfRangeException", "Specified argument was out of range of valid values.", "health")
		var actor: Dictionary = _mutable(actor_id)
		if not actor.ok: return actor
		actor.value.health = health
		return Values.success()

	func report_hit(actor_id: Variant, other_actor_id: Variant = null, other_thing_type_mask: Variant = 0) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		if not State.Laws.is_uint32(other_thing_type_mask): return State.Laws.transport("otherThingTypeMask")
		if (other_thing_type_mask & ~PROVEN_BITS) != 0: return Admission.failure("ArgumentOutOfRangeException", "Specified argument was out of range of valid values.", "otherThingTypeMask")
		if other_actor_id != null:
			var other: Dictionary = _mutable(other_actor_id)
			if not other.ok: return other
			var mask: Dictionary = get_thing_type_mask(other_actor_id)
			if not mask.ok: return mask
			if other_thing_type_mask != 0 and other_thing_type_mask != mask.value: return Admission.failure("ArgumentException", "A hit source actor and type mask disagree.")
			other_thing_type_mask = mask.value
		_enqueue(FactKind.HIT, actor_id, other_actor_id, other_thing_type_mask)
		return Values.success()

	func report_started_dying(actor_id: Variant) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var actor: Dictionary = found.value
		if actor.lifecycle != Lifecycle.ALIVE: return Values.success(false)
		if not actor.base_state.start_die_process().value: return Admission.failure("InvalidOperationException", "Level 100 lifecycle diverged from its Thing/Actor base state.")
		actor.lifecycle = Lifecycle.STARTED_DYING
		_enqueue(FactKind.STARTED_DYING, actor_id, null, 0)
		return Values.success(true)

	func report_died(actor_id: Variant) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var actor: Dictionary = found.value
		if actor.lifecycle == Lifecycle.DESTROYED: return Values.success(false)
		actor.lifecycle = Lifecycle.DESTROYED
		actor.base_state.declare_shutdown()
		actor.active = false
		actor.is_objective = false
		_enqueue(FactKind.DIED, actor_id, null, 0)
		return Values.success(true)

	func report_plane_started_dying(actor_id: Variant) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var actor: Dictionary = found.value
		var state: Dictionary = actor.base_state.snapshot()
		if not state.ok: return state
		if state.value.retail_plane == null: return Admission.failure("InvalidOperationException", "Plane death requires an admitted raw Plane.")
		if actor.lifecycle != Lifecycle.ALIVE: return Values.success(false)
		if not actor.base_state.mark_unit_dying().value: return Admission.failure("InvalidOperationException", "Plane dying state diverged.")
		actor.lifecycle = Lifecycle.STARTED_DYING
		_enqueue(FactKind.STARTED_DYING, actor_id, null, 0)
		return Values.success(true)

	func report_ground_unit_died(actor_id: Variant) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var actor: Dictionary = found.value
		if actor.lifecycle != Lifecycle.ALIVE: return Values.success(false)
		if not actor.base_state.mark_unit_dying().value: return Admission.failure("InvalidOperationException", "Ground-unit dying state diverged.")
		actor.lifecycle = Lifecycle.DIED_AWAITING_SHUTDOWN
		_enqueue(FactKind.STARTED_DYING, actor_id, null, 0)
		_enqueue(FactKind.DIED, actor_id, null, 0)
		return Values.success(true)

	func shutdown_ground_unit(actor_id: Variant) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var actor: Dictionary = found.value
		if actor.lifecycle != Lifecycle.DIED_AWAITING_SHUTDOWN: return Admission.failure("InvalidOperationException", "Ground-unit shutdown has no pending death.")
		actor.lifecycle = Lifecycle.DESTROYED
		actor.active = false
		actor.is_objective = false
		return Values.success()

	func begin_trigger_dispatch(actor_id: Variant, entry_jet_mode_state: Variant) -> Dictionary:
		if not Values.is_int32(entry_jet_mode_state): return State.Laws.transport("entryJetModeState")
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var actor: Dictionary = found.value
		if actor.trigger == null or actor.trigger_event_dispatched: return Values.success(false)
		actor.trigger_entry_jet_mode_state = entry_jet_mode_state
		_enqueue(FactKind.TRIGGER_DISPATCH_READY, actor_id, null, 0)
		return Values.success(true)

	func mark_trigger_event_dispatched(actor_id: Variant) -> Dictionary:
		var found: Dictionary = _mutable(actor_id)
		if not found.ok: return found
		var actor: Dictionary = found.value
		if actor.trigger == null or actor.trigger_event_dispatched: return Admission.failure("InvalidOperationException", "Trigger dispatch is not ready.")
		actor.trigger_entered = true
		if actor.trigger_entry_jet_mode_state == null: actor.trigger_entry_jet_mode_state = 0
		actor.trigger_event_dispatched = true
		actor.active = false
		actor.is_objective = false
		return Values.success()

	func drain_facts() -> Dictionary:
		var result: Array[Dictionary] = _sorted_facts()
		_pending_facts.clear()
		return Values.success(result)

	func _ids() -> Array:
		var result: Array = _actors.keys()
		result.sort()
		return result

	func _require(actor_id: Variant) -> Dictionary:
		if not Values.is_int32(actor_id): return State.Laws.transport("actorId")
		if actor_id <= 0 or not _actors.has(actor_id): return Admission.failure("KeyNotFoundException", "Level 100 actor %d does not exist." % actor_id)
		return Values.success(_actors[actor_id])

	func _mutable(actor_id: Variant) -> Dictionary:
		var found: Dictionary = _require(actor_id)
		if not found.ok: return found
		var state: State.Actor = found.value.base_state
		if state.has_retail_construction().value and not state.has_retail_plane_motion().value:
			return Admission.failure("NotSupportedException", "Retail construction needs its complete world lifecycle before legacy actor mutation.")
		return found

	func _scalar(actor_id: Variant, field: String) -> Dictionary:
		var actor: Dictionary = _require(actor_id)
		return Values.success(actor.value[field]) if actor.ok else actor

	func _base_call(actor_id: Variant, method: String, args: Array = []) -> Dictionary:
		var actor: Dictionary = _mutable(actor_id)
		return actor.value.base_state.callv(method, args) if actor.ok else actor

	func _change_pose(actor_id: Variant, pose: Variant, method: String) -> Dictionary:
		var admitted: Dictionary = _pose_input(pose)
		if not admitted.ok: return admitted
		var actor: Dictionary = _mutable(actor_id)
		if not actor.ok: return actor
		var state: State.Actor = actor.value.base_state
		var result: Dictionary = state.call(method, _base_pose(admitted.value))
		if not result.ok: return result
		result = state.set_velocity(admitted.value.linear_velocity_millimeters_per_tick)
		return state.set_angular_velocity(admitted.value.angular_velocity_micro_radians_per_tick) if result.ok else result

	func _enqueue(kind: int, actor_id: int, other_id: Variant, mask: int) -> void:
		var sequence: int = _next_fact_sequence
		_next_fact_sequence = INT64_MIN if _next_fact_sequence == INT64_MAX else _next_fact_sequence + 1
		_pending_facts.append({"sequence": sequence, "kind": kind, "actor_id": actor_id, "other_actor_id": other_id, "other_thing_type_mask": mask})

	func _sorted_facts() -> Array[Dictionary]:
		# LINQ OrderBy is stable. Decorate ties explicitly; Array.sort_custom
		# alone would change the source order for an equal sequence.
		var ordered: Array[Dictionary] = []
		for index: int in range(_pending_facts.size()): ordered.append({"index": index, "fact": _pending_facts[index]})
		ordered.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
			return a.fact.sequence < b.fact.sequence if a.fact.sequence != b.fact.sequence else a.index < b.index)
		var result: Array[Dictionary] = []
		for item: Dictionary in ordered: result.append(item.fact.duplicate(true))
		return result

	func _allocate_id() -> int:
		var id: int = _next_actor_id
		_next_actor_id = Values.int32(_next_actor_id + 1)
		return id

	func _known_program(name: Variant) -> Dictionary:
		if _programs == null: return Admission.failure("ArgumentOutOfRangeException", "No admitted mission-program set for world %d." % _definitions.world_number(), "worldNumber")
		return Values.success(_programs.has(Definitions.Admission.key(name)))

	static func _pose_input(pose: Variant) -> Dictionary:
		if pose == null: return Admission.failure("ArgumentNullException", "Value cannot be null.", "pose")
		if not pose is Dictionary: return State.Laws.transport("pose")
		if not State.Laws.finite_basis(pose.get("basis_float_bits")):
			return Admission.failure("ArgumentException", "Actor pose basis must contain finite values.", "pose")
		var result: Dictionary = {"basis_float_bits": pose.basis_float_bits.duplicate()}
		for field: String in ["position_millimeters", "linear_velocity_millimeters_per_tick", "angular_velocity_micro_radians_per_tick"]:
			var vector: Dictionary = State.Laws.vector(pose.get(field), "pose")
			if not vector.ok: return vector
			result[field] = vector.value
		return Values.success(result)

	static func _base_pose(pose: Dictionary) -> Dictionary:
		return {"position_millimeters": pose.position_millimeters.duplicate(), "basis_float_bits": pose.basis_float_bits.duplicate()}

	static func _to_pose(state: Dictionary) -> Dictionary:
		return {"position_millimeters": state.current_pose.position_millimeters.duplicate(), "basis_float_bits": state.current_pose.basis_float_bits.duplicate(),
			"linear_velocity_millimeters_per_tick": state.velocity.duplicate(), "angular_velocity_micro_radians_per_tick": state.angular_velocity.duplicate()}

	func _snapshot_actor(actor: Dictionary) -> Dictionary:
		var state: Dictionary = actor.base_state.snapshot()
		if not state.ok: return state
		var result: Dictionary = {}
		for key: String in ["actor_id", "definition_identity", "name", "definition_name", "script_name", "mesh_binding", "spawn_owner_id", "spawner_name", "is_static", "active", "is_objective", "lifecycle", "health", "target_group", "target_ordinal", "trigger", "trigger_entered", "trigger_entry_jet_mode_state", "trigger_event_dispatched"]:
			result[key] = Definitions.Admission.copy_value(actor[key])
		result.thing_type_mask = state.value.thing_type_mask & PROVEN_BITS
		result.pose = _to_pose(state.value)
		return Values.success(result)

	func spawn_thing(owner_id: Variant, definition_name: Variant, spawner_name: Variant, count: Variant, script_name: Variant, event_time_float_bits: Variant = 0) -> Dictionary:
		var owner: Dictionary = _require(owner_id)
		if not owner.ok: return owner
		var texts: Array = []
		for pair: Array in [[definition_name, "definitionName"], [spawner_name, "spawnerName"], [script_name, "scriptName"]]:
			var text: Dictionary = Admission.required_text(pair[0], pair[1])
			if not text.ok: return text
			texts.append(text.value)
		if not Values.is_int32(count) or not Values.is_int32(event_time_float_bits): return State.Laws.transport("spawn")
		var found: Dictionary = _definitions.find_spawn_definition(owner.value.definition_identity, texts[0], texts[1], texts[2])
		if not found.ok: return found
		if count != 1 or found.value == null:
			return Admission.failure("InvalidOperationException", Definitions.Admission.message(["SpawnThing request is outside the supplied Level 100 definition set: ", texts[0], "/", str(count), "."]))
		var definition: Dictionary = found.value
		var seated: Dictionary = _seat_on_ground(texts[0], definition.initial_pose)
		if not seated.ok: return seated
		# Complete construction precedes ordinal and runtime identity allocation.
		var base: Dictionary = _create_spawned_plane(owner.value, definition, event_time_float_bits) if _is_plane(texts[0]) else _create_base(seated.value, definition.thing_type_mask)
		if not base.ok: return base
		var ordinal: Dictionary = _allocate_ordinal(definition)
		if not ordinal.ok: return ordinal
		var id: int = _allocate_id()
		# The C# initializer evaluates this fallback after allocating the ID.
		var health: Dictionary = _released_health(texts[0], definition.initial_health)
		if not health.ok: return health
		var actor: Dictionary = _actor_defaults(id, definition, base.value)
		actor.name = _spawn_name(texts[0], id)
		actor.definition_name = texts[0]
		actor.script_name = texts[2]
		actor.spawn_owner_id = owner_id
		actor.spawner_name = texts[1]
		actor.is_static = false
		actor.health = health.value
		actor.target_ordinal = ordinal.value
		_actors[id] = actor
		return Values.success([id])

	func get_plane_spawner_exit_point(actor_id: Variant, selector: Variant) -> Dictionary:
		var found: Dictionary = _require(actor_id)
		if not found.ok: return found
		var actor: Dictionary = found.value
		if actor.spawn_owner_id == null or not _is_plane(actor.definition_name):
			return Admission.failure("NotSupportedException", "Exit-point lookup requires an admitted spawned Plane.")
		var definition: Dictionary = _definitions.get_spawn_definition(actor.definition_identity)
		if not definition.ok: return definition
		var points: Variant = definition.value.spawner_exit_waypoints
		if points == null: return Admission.failure("NotSupportedException", "This spawn definition has no recovered exit input.")
		var owner: Dictionary = _require(actor.spawn_owner_id)
		if not owner.ok: return owner
		var parent: Dictionary = _airfield_owner_pose(owner.value, definition.value)
		if not parent.ok: return parent
		if not Values.is_int32(selector): return State.Laws.transport("selector")
		for point: Dictionary in points:
			if point.selector == selector: return MeshPose.apply_owner(parent.value, _local_pose(point.model_transform))
		return Values.success(null)

	func _create_authored() -> Dictionary:
		for definition: Dictionary in _definitions.actors():
			var id: int = _allocate_id()
			var pose: Dictionary = _seat_on_ground(definition.definition_name, definition.initial_pose)
			if not pose.ok: return pose
			var base: Dictionary = _create_authored_plane(definition) if _is_plane(definition.definition_name) else _create_base(pose.value, definition.thing_type_mask)
			if not base.ok: return base
			var actor: Dictionary = _actor_defaults(id, definition, base.value)
			actor.name = definition.name
			actor.is_static = definition.is_static
			actor.target_ordinal = definition.target_ordinal
			actor.trigger = definition.trigger
			_actors[id] = actor
		return Values.success()

	static func _actor_defaults(id: int, definition: Dictionary, base: State.Actor) -> Dictionary:
		return {"actor_id": id, "definition_identity": definition.definition_identity, "name": null,
			"definition_name": definition.definition_name, "script_name": definition.script_name, "mesh_binding": definition.mesh_binding,
			"spawn_owner_id": null, "spawner_name": null, "is_static": false, "active": definition.active,
			"is_objective": false, "flag_word": 0, "lifecycle": Lifecycle.ALIVE, "health": definition.initial_health,
			"base_state": base, "target_group": definition.target_group, "target_ordinal": 0,
			"trigger": null, "trigger_entered": false, "trigger_entry_jet_mode_state": null, "trigger_event_dispatched": false}

	func _allocate_ordinal(definition: Dictionary) -> Dictionary:
		if definition.target_group == 0: return Values.success(0)
		var ordinal: int = definition.fixed_target_ordinal
		if ordinal <= 0:
			ordinal = 1
			for actor: Dictionary in _actors.values():
				if actor.target_group == definition.target_group: ordinal = Values.int32(ordinal + 1)
		var invalid: bool = ordinal > definition.maximum_group_actors
		if not invalid:
			for actor: Dictionary in _actors.values():
				if actor.target_group == definition.target_group and actor.target_ordinal == ordinal:
					invalid = true
					break
		if invalid:
			var names: Array[String] = ["None", "StaticTargets", "TargetTrucks", "MovingTargets", "AirborneTargets1", "AirborneTargets2", "AirTrainer"]
			return Admission.failure("InvalidOperationException", "Released Level 100 spawned an invalid %s actor ordinal %d." % [names[definition.target_group], ordinal])
		return Values.success(ordinal)

	func _seat_on_ground(definition_name: Variant, pose: Dictionary) -> Dictionary:
		var result: Dictionary = pose.duplicate(true)
		if not _initialize_support: return Values.success(result)
		var motion: Dictionary = _definitions.find_motion_definition(definition_name)
		if not motion.ok: return motion
		var offset: int = motion.value.core_ground_origin_offset_millimeters if motion.value != null and motion.value.motion_class == 1 else 0
		var ground: Dictionary = _terrain.sample_ground_elevation_millimeters(pose.position_millimeters.x, pose.position_millimeters.z)
		if not ground.ok: return ground
		var sum: int = ground.value + offset
		if not Values.is_int32(sum): return State.Laws.overflow()
		# Same Level100 compatibility placement convention as SeatOnGround:
		# the GroundVehicle offset is applied to ground, never to water.
		var seated: int = maxi(sum, _water_elevation)
		if result.position_millimeters.y < seated: result.position_millimeters.y = seated
		return Values.success(result)

	func _released_health(name: Variant, fallback: int) -> Dictionary:
		var contact: Variant = _contacts.get(Definitions.Admission.key(name))
		if contact == null or contact.kind == 0: return Values.success(fallback)
		# MathF multiplication is stored before MathF.Round(AwayFromZero).
		return State.Laws.round_int32(F.store_float32(F.read_word(contact.maximum_life_float_bits) * 1000.0))

	func _is_plane(name: Variant) -> bool:
		if _definitions.world_number() != 100 or not _initialize_support or not (Admission.text_equals(name, "Air Trainer") or Admission.text_equals(name, "Target Drone")): return false
		var motion: Dictionary = _definitions.find_motion_definition(name)
		return motion.ok and motion.value != null and motion.value.motion_class == 2

	static func _create_base(pose: Dictionary, mask: int) -> Dictionary:
		return State.create(_base_pose(pose), pose.linear_velocity_millimeters_per_tick, pose.angular_velocity_micro_radians_per_tick, mask)

	func _create_authored_plane(definition: Dictionary) -> Dictionary:
		if definition.initial_pose.linear_velocity_millimeters_per_tick != State.Laws.zero() or definition.initial_pose.angular_velocity_micro_radians_per_tick != State.Laws.zero():
			return Admission.failure("NotSupportedException", "Selected Plane construction requires the admitted zero initial velocity.")
		return _create_plane(definition.authored_transform.retail_position_float_bits, definition.authored_transform.retail_euler_float_bits, definition.thing_type_mask, 0)

	func _create_spawned_plane(owner: Dictionary, definition: Dictionary, time_bits: int) -> Dictionary:
		var parent: Dictionary = _airfield_owner_pose(owner, definition)
		if not parent.ok: return parent
		var emitter: Dictionary = MeshPose.apply_owner(parent.value, _local_pose(definition.authored_emitter_transform))
		if not emitter.ok: return emitter
		var position: Dictionary = emitter.value.position_float_bits
		if F.read_word(position.x) == 0.0 and F.read_word(position.y) == 0.0 and F.read_word(position.z) == 0.0:
			return Admission.failure("NotSupportedException", "The zero-emitter owner fallback is outside the selected Airfield route.")
		var euler: Dictionary = PlaneMotion.euler_from_spawner_basis(emitter.value.basis_float_bits)
		return _create_plane(position, euler.value, definition.thing_type_mask, time_bits) if euler.ok else euler

	func _airfield_owner_pose(owner: Dictionary, definition: Dictionary) -> Dictionary:
		var source: Dictionary = _definitions.get_actor_definition(owner.definition_identity)
		if not source.ok: return source
		if owner.spawn_owner_id != null or not owner.is_static or not Admission.text_equals(owner.definition_name, "Forseti Light Fighter Airfield") or not (Admission.text_equals(definition.spawner_name, "SpawnerA") or Admission.text_equals(definition.spawner_name, "SpawnerB")):
			return Admission.failure("NotSupportedException", "Plane spawning requires the unchanged authored Airfield pose.")
		var state: Dictionary = owner.base_state.snapshot()
		if not state.ok: return state
		var seated: Dictionary = _seat_on_ground(source.value.definition_name, source.value.initial_pose)
		if not seated.ok: return seated
		if _to_pose(state.value) != seated.value: return Admission.failure("NotSupportedException", "Plane spawning requires the unchanged authored Airfield pose.")
		var position: Dictionary = _seat_retail_position(source.value.authored_transform.retail_position_float_bits)
		if not position.ok: return position
		var basis: Dictionary = _euler_basis(source.value.authored_transform.retail_euler_float_bits)
		return Values.success({"position_float_bits": position.value, "basis_float_bits": basis.value}) if basis.ok else basis

	func _seat_retail_position(position: Dictionary) -> Dictionary:
		var height: Dictionary = _sample_retail_height(position)
		if not height.ok: return height
		var result: Dictionary = position.duplicate()
		if F.read_word(result.z) > height.value: result.z = Values.int32(F.store_word(height.value))
		var water: int = Values.int32(_terrain.metadata().water_level_bits)
		if F.read_word(result.z) > F.read_word(water): result.z = water
		return Values.success(result)

	func _create_plane(position: Dictionary, euler: Dictionary, mask: int, time_bits: int) -> Dictionary:
		var basis: Dictionary = _euler_basis(euler)
		if not basis.ok: return basis
		var pose: Dictionary = {"position_float_bits": position.duplicate(), "basis_float_bits": basis.value}
		var created: Dictionary = State.create({"position_millimeters": State.Laws.zero(), "basis_float_bits": basis.value}, State.Laws.zero(), State.Laws.zero(), mask)
		if not created.ok: return created
		var motion: Dictionary = PlaneMotion.create_initial(pose, euler)
		if not motion.ok: return motion
		var state: State.Actor = created.value
		var started: Dictionary = state.begin_retail_plane(pose, motion.value, time_bits, mask)
		if not started.ok: return started
		var height: Dictionary = _sample_retail_height(position)
		if not height.ok: return height
		var current: Dictionary = position.duplicate()
		if F.read_word(current.z) > height.value:
			current.z = Values.int32(F.store_word(height.value))
			var moved: Dictionary = state.teleport_retail_position(current)
			if not moved.ok: return moved
		var water: int = Values.int32(_terrain.metadata().water_level_bits)
		if F.read_word(current.z) > F.read_word(water):
			current.z = water
			var moved: Dictionary = state.set_retail_position(current)
			if not moved.ok: return moved
		return Values.success(state)

	func _sample_retail_height(position: Dictionary) -> Dictionary:
		# Exact small RetailWorldTerrain.SampleRetailHeight coordinate wrapper.
		# Terrain retains the one actual sampler; the biased float's raw word
		# minus 0x47400000 is the fixed coordinate, not a numerical cast.
		var x: int = Values.int32(F.store_word((F.read_word(position.x) - F.read_word(0x3afffeb0)) + 49152.0) - 0x47400000)
		var y: int = Values.int32(F.store_word((F.read_word(position.y) - F.read_word(0x3afffeb0)) + 49152.0) - 0x47400000)
		var units: Dictionary = _terrain.sample_height_units_at_fixed(x, y)
		return Values.success(F.store_float32(float(units.value) * F.read_word(_terrain.metadata().height_scale_bits))) if units.ok else units

	static func _euler_basis(euler: Dictionary) -> Dictionary:
		var result: Euler.Result = Euler.build_basis(PackedInt64Array([euler.x & 0xffffffff, euler.y & 0xffffffff, euler.z & 0xffffffff]))
		if not result.ok: return Admission.failure("ArgumentOutOfRangeException", result.error, "euler")
		var basis: Dictionary = {}
		for index: int in range(Definitions.BASIS_KEYS.size()): basis[Definitions.BASIS_KEYS[index]] = Values.int32(result.words[index])
		return Values.success(basis)

	static func _local_pose(local: Dictionary) -> Dictionary:
		return {"position_float_bits": local.local_position_float_bits, "basis_float_bits": local.local_basis_float_bits}

	static func _spawn_name(name: Variant, id: int) -> PackedInt32Array:
		return Definitions.Admission.message([name, " #", str(id)])

	func _restore(supplied: Variant) -> Dictionary:
		if supplied == null: return Admission.failure("ArgumentNullException", "Value cannot be null.", "snapshot")
		if not supplied is Dictionary or not Values.is_int32(supplied.get("next_actor_id")) or not supplied.get("next_fact_sequence") is int:
			return State.Laws.transport("snapshot")
		if not Admission.text_equals(supplied.get("definition_set_identity_sha256"), _definitions.identity_sha256()) or supplied.next_actor_id <= 0 or supplied.next_fact_sequence <= 0:
			return _snapshot_failure("Actor registry snapshot does not match its immutable definition set.")
		_next_actor_id = supplied.next_actor_id
		_next_fact_sequence = supplied.next_fact_sequence
		for pair: Array in [["actors", "snapshot.Actors"], ["pending_facts", "snapshot.PendingFacts"], ["base_states", "snapshot.BaseStates"]]:
			if not supplied.has(pair[0]): return State.Laws.transport("snapshot")
			if supplied[pair[0]] == null: return Admission.failure("ArgumentNullException", "Value cannot be null.", pair[1])
			if not supplied[pair[0]] is Array: return State.Laws.transport("snapshot")
		for actor: Variant in supplied.actors:
			if actor == null: return _snapshot_failure("Actor registry snapshot contains a null record.")
		for fact: Variant in supplied.pending_facts:
			if fact == null: return _snapshot_failure("Actor registry snapshot contains a null record.")
		for base: Variant in supplied.base_states:
			if base == null or (base is Dictionary and base.get("state") == null): return _snapshot_failure("Actor registry snapshot contains a null record.")
		var bases: Dictionary = {}
		for base: Variant in supplied.base_states:
			if not base is Dictionary or not Values.is_int32(base.get("actor_id")) or not base.get("state") is Dictionary: return State.Laws.transport("snapshot")
			# ToDictionary throws here; the source's later duplicate-count branch
			# cannot override the actual framework exception or its empty parameter.
			if bases.has(base.actor_id): return Admission.failure("ArgumentException", "An item with the same key has already been added. Key: %d" % base.actor_id)
			bases[base.actor_id] = base.state
		var ordered: Array[Dictionary] = []
		for index: int in range(supplied.actors.size()):
			var admitted: Dictionary = _actor_record(supplied.actors[index])
			if not admitted.ok: return admitted
			ordered.append({"index": index, "source": admitted.value})
		ordered.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
			return a.source.actor_id < b.source.actor_id if a.source.actor_id != b.source.actor_id else a.index < b.index)
		var sources: Dictionary = {}
		for row: Dictionary in ordered:
			var actor: Dictionary = row.source
			var id: int = actor.actor_id
			if id <= 0 or id >= _next_actor_id or not bases.has(id): return _snapshot_failure("Actor registry snapshot has invalid identities.")
			# RestoreActor evaluates even when TryAdd will reject an existing ID.
			var restored: Dictionary = _restore_actor(actor, bases[id])
			if not restored.ok: return restored
			if _actors.has(id): return _snapshot_failure("Actor registry snapshot has invalid identities.")
			_actors[id] = restored.value
			sources[id] = actor
		var incomplete: bool = _actors.size() != _next_actor_id - 1 or bases.size() != _actors.size()
		if not incomplete:
			for definition: Dictionary in _definitions.actors():
				var count: int = 0
				for actor: Dictionary in _actors.values():
					if actor.spawn_owner_id == null and Admission.text_equals(actor.definition_identity, definition.definition_identity): count += 1
				if count != 1:
					incomplete = true
					break
		if incomplete: return _snapshot_failure("Actor registry snapshot does not contain each authored actor exactly once.")
		for id: int in _ids():
			var valid: Dictionary = _validate_restored(_actors[id], sources[id])
			if not valid.ok: return valid
		var ordinals: Dictionary = {}
		for id: int in _ids():
			var actor: Dictionary = _actors[id]
			if actor.target_group == 0: continue
			var key: String = "%d/%d" % [actor.target_group, actor.target_ordinal]
			if actor.target_ordinal <= 0 or ordinals.has(key): return _snapshot_failure("Actor registry snapshot has duplicate or invalid mission ordinals.")
			ordinals[key] = true
		for fact: Variant in supplied.pending_facts:
			var admitted: Dictionary = _fact_record(fact)
			if not admitted.ok: return admitted
			_pending_facts.append(admitted.value)
		_pending_facts = _sorted_facts()
		for fact: Dictionary in _pending_facts:
			if fact.sequence <= 0 or fact.sequence >= _next_fact_sequence or fact.kind not in [1, 2, 3, 4] or not _actors.has(fact.actor_id) or (fact.other_actor_id != null and not _actors.has(fact.other_actor_id)):
				return _snapshot_failure("Actor registry snapshot has invalid fact sequencing.")
		for fact: Dictionary in _pending_facts:
			if (fact.other_thing_type_mask & ~PROVEN_BITS) != 0 or (fact.kind != FactKind.HIT and (fact.other_actor_id != null or fact.other_thing_type_mask != 0)):
				return _snapshot_failure("Actor registry snapshot has invalid fact sequencing.")
			if fact.kind == FactKind.HIT and fact.other_actor_id != null:
				var mask: Dictionary = get_thing_type_mask(fact.other_actor_id)
				if not mask.ok: return mask
				if mask.value != fact.other_thing_type_mask: return _snapshot_failure("Actor registry snapshot has invalid fact sequencing.")
		var sequences: Dictionary = {}
		for fact: Dictionary in _pending_facts:
			if sequences.has(fact.sequence): return _snapshot_failure("Actor registry snapshot has invalid fact sequencing.")
			sequences[fact.sequence] = true
		return Values.success()

	static func _restore_actor(source: Dictionary, base: Dictionary) -> Dictionary:
		var state: Dictionary = State.restore(base)
		if not state.ok: return state
		var actor: Dictionary = source.duplicate(true)
		actor.erase("pose")
		actor.erase("thing_type_mask")
		actor.flag_word = MARKED_OBJECTIVE if actor.is_objective else 0
		actor.base_state = state.value
		return Values.success(actor)

	func _validate_restored(actor: Dictionary, source: Dictionary) -> Dictionary:
		var has_plane: bool = actor.base_state.has_retail_plane_motion().value
		if _is_plane(source.definition_name) and not has_plane: return _snapshot_failure("Selected Plane snapshots require their creation-owned raw state.")
		if has_plane and not _is_plane(source.definition_name): return Admission.failure("NotSupportedException", "Raw Plane motion is admitted only for the selected Level100 aircraft definitions.")
		# Preserve the source predicate's lazy order. In particular, a malformed
		# public pose rejects before projecting an otherwise overflowing base.
		if source.pose == null or not State.Laws.finite_basis(source.pose.basis_float_bits) or actor.health < 0 or actor.lifecycle not in [0, 1, 2, 3]:
			return _snapshot_failure("Actor registry snapshot contains invalid mutable actor state.")
		var projected: Dictionary = actor.base_state.snapshot()
		if not projected.ok: return projected
		var base: Dictionary = projected.value
		var dying: bool = (base.flags & State.Flags.DYING) != 0
		var shutting_down: bool = (base.flags & State.Flags.DECLARED_SHUTDOWN) != 0
		if source.pose != _to_pose(base) or base.thing_type_mask != (source.thing_type_mask | State.ACTOR_LINEAGE) \
			or (actor.lifecycle == Lifecycle.ALIVE and (dying or shutting_down)) \
			or (actor.lifecycle == Lifecycle.STARTED_DYING and not dying) \
			or (actor.lifecycle == Lifecycle.DIED_AWAITING_SHUTDOWN and (not dying or shutting_down or actor.health != 0 or not (Admission.text_equals(actor.definition_name, "Target Tank") or Admission.text_equals(actor.definition_name, "Target Truck")))) \
			or (actor.lifecycle == Lifecycle.DESTROYED and not shutting_down and not dying) \
			or (actor.lifecycle == Lifecycle.DESTROYED and (actor.active or actor.is_objective)) \
			or actor.target_group not in [0, 1, 2, 3, 4, 5, 6]:
			return _snapshot_failure("Actor registry snapshot contains invalid mutable actor state.")
		if actor.script_name != null:
			var known: Dictionary = _known_program(actor.script_name)
			if not known.ok: return known
			if not known.value: return _snapshot_failure("Actor registry snapshot contains invalid mutable actor state.")
		if (actor.trigger != null and actor.trigger not in [1, 2, 3, 4, 5]) \
			or (actor.trigger_entry_jet_mode_state != null and actor.trigger_entry_jet_mode_state not in [0, 1]) \
			or (actor.trigger == null and (actor.trigger_entered or actor.trigger_entry_jet_mode_state != null or actor.trigger_event_dispatched)) \
			or (actor.trigger != null and ((actor.trigger_event_dispatched and not actor.trigger_entered) or (actor.trigger_entered and actor.trigger_entry_jet_mode_state == null))):
			return _snapshot_failure("Actor registry snapshot contains invalid mutable actor state.")
		if actor.spawn_owner_id != null:
			var found: Dictionary = _definitions.get_spawn_definition(actor.definition_identity)
			if not found.ok: return found
			var definition: Dictionary = found.value
			if not _actors.has(actor.spawn_owner_id): return _snapshot_failure("Actor registry snapshot has a missing spawn owner.")
			var owner: Dictionary = _actors[actor.spawn_owner_id]
			if not Admission.text_equals(owner.definition_identity, definition.owner_definition_identity) \
				or not Admission.text_equals(actor.name, _spawn_name(definition.definition_name, actor.actor_id)) \
				or not Admission.text_equals(actor.definition_name, definition.definition_name) \
				or not Admission.text_equals(actor.script_name, definition.script_name) \
				or not Admission.text_equals(actor.spawner_name, definition.spawner_name) \
				or not Admission.text_equals(actor.mesh_binding, definition.mesh_binding) \
				or source.thing_type_mask != definition.thing_type_mask or actor.is_static or actor.target_group != definition.target_group \
				or (definition.target_group == 0 and actor.target_ordinal != 0) \
				or (definition.target_group != 0 and (actor.target_ordinal <= 0 or actor.target_ordinal > definition.maximum_group_actors or (definition.fixed_target_ordinal > 0 and actor.target_ordinal != definition.fixed_target_ordinal))) \
				or actor.trigger != null:
				return _snapshot_failure("Actor registry snapshot changed immutable spawn identity.")
			return Values.success()
		var found: Dictionary = _definitions.get_actor_definition(actor.definition_identity)
		if not found.ok: return found
		var definition: Dictionary = found.value
		if actor.spawner_name != null or not Admission.text_equals(actor.name, definition.name) \
			or not Admission.text_equals(actor.definition_name, definition.definition_name) or not Admission.text_equals(actor.mesh_binding, definition.mesh_binding) \
			or source.thing_type_mask != definition.thing_type_mask or actor.is_static != definition.is_static \
			or actor.target_group != definition.target_group or actor.target_ordinal != definition.target_ordinal or actor.trigger != definition.trigger:
			return _snapshot_failure("Actor registry snapshot changed immutable authored identity.")
		return Values.success()

	static func _snapshot_failure(reason: String) -> Dictionary:
		return Admission.failure("ArgumentException", reason, "snapshot")

	static func _actor_record(value: Variant) -> Dictionary:
		if not value is Dictionary: return State.Laws.transport("snapshot")
		var result: Dictionary = {}
		for key: String in ["actor_id", "lifecycle", "health", "target_group", "target_ordinal"]:
			if not Values.is_int32(value.get(key)): return State.Laws.transport("snapshot")
			result[key] = value[key]
		for key: String in ["spawn_owner_id", "trigger", "trigger_entry_jet_mode_state"]:
			if not value.has(key) or (value[key] != null and not Values.is_int32(value[key])): return State.Laws.transport("snapshot")
			result[key] = value[key]
		for key: String in ["definition_identity", "name", "definition_name", "script_name", "mesh_binding", "spawner_name"]:
			if not value.has(key): return State.Laws.transport("snapshot")
			var text: Dictionary = Text.units(value[key])
			if not text.ok: return text
			result[key] = text.value
		for key: String in ["is_static", "active", "is_objective", "trigger_entered", "trigger_event_dispatched"]:
			if not value.get(key) is bool: return State.Laws.transport("snapshot")
			result[key] = value[key]
		if not State.Laws.is_uint32(value.get("thing_type_mask")) or not value.has("pose"): return State.Laws.transport("snapshot")
		result.thing_type_mask = value.thing_type_mask
		result.pose = null
		if value.pose != null:
			if not value.pose is Dictionary: return State.Laws.transport("snapshot")
			var pose: Dictionary = {}
			var basis: Dictionary = State.Laws.basis(value.pose.get("basis_float_bits"), "snapshot")
			if not basis.ok: return basis
			pose.basis_float_bits = basis.value
			for key: String in ["position_millimeters", "linear_velocity_millimeters_per_tick", "angular_velocity_micro_radians_per_tick"]:
				var vector: Dictionary = State.Laws.vector(value.pose.get(key), "snapshot")
				if not vector.ok: return vector
				pose[key] = vector.value
			result.pose = pose
		return Values.success(result)

	static func _fact_record(value: Variant) -> Dictionary:
		if not value is Dictionary or not value.get("sequence") is int or not Values.is_int32(value.get("kind")) or not Values.is_int32(value.get("actor_id")) or not value.has("other_actor_id") or (value.other_actor_id != null and not Values.is_int32(value.other_actor_id)) or not State.Laws.is_uint32(value.get("other_thing_type_mask")):
			return State.Laws.transport("snapshot")
		return Values.success({"sequence": value.sequence, "kind": value.kind, "actor_id": value.actor_id, "other_actor_id": value.other_actor_id, "other_thing_type_mask": value.other_thing_type_mask})
