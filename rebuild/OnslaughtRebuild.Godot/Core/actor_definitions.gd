# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Immutable value/admission half of Level100ActorRegistry.cs. This contains no
## mutable actor registry, simulation, Godot vectors, filesystem or clock.
## Record fields follow state_hasher.gd: signed Int32 raw float words and named
## x/y/z or row0_x..row2_z fields. Text is detached UTF-16, including NUL and
## unpaired surrogates; only BinaryWriter UTF-8 encoding applies replacement.
const Text = preload("res://Core/canonical_json_string.gd")
const Writer = preload("res://Core/canonical_binary_writer.gd")
const Career = preload("res://Core/retail_career_campaign.gd")
const Float32 = preload("res://Core/retail_float24.gd")
const AMMUNITION_MASK: int = 4
const BATTLE_ENGINE_MASK: int = 8
const PROVEN_THING_BITS: int = 12
const BASIS_KEYS: Array[String] = ["row0_x", "row0_y", "row0_z", "row1_x", "row1_y", "row1_z", "row2_x", "row2_y", "row2_z"]
const VECTOR_KEYS: Array[String] = ["x", "y", "z"]


static func create(actors: Variant, spawns: Variant, waypoint_paths: Variant = null,
		motion_definitions: Variant = null, world_number: Variant = 100) -> Dictionary:
	var admission := Admission.new()
	return admission.create(actors, spawns, waypoint_paths, motion_definitions, world_number)


## The standalone value method follows the target chain, never serialized
## Points order. A bare path may be invalid; preserve explicit lookup failure.
static func chain_point(path: Variant, chain_index: Variant) -> Dictionary:
	if not path is Dictionary or not Admission.is_i32(chain_index):
		return Admission.failure("ArgumentException", "A waypoint value and Int32 chain index are required.")
	var chain: Variant = path.get("target_chain_node_indices")
	var points: Variant = path.get("points")
	if chain == null: return Admission.failure("NullReferenceException", "Object reference not set to an instance of an object.")
	if not (chain is Array or chain is PackedInt32Array):
		return Admission.failure("ArgumentException", "Waypoint collections have invalid carriers.")
	if chain_index < 0 or chain_index >= chain.size():
		return Admission.failure("ArgumentOutOfRangeException", "Index was out of range.", "index")
	var node_index: Variant = chain[chain_index]
	if points == null: return Admission.failure("NullReferenceException", "Object reference not set to an instance of an object.")
	if not points is Array: return Admission.failure("ArgumentException", "Waypoint collections have invalid carriers.")
	for point: Variant in points:
		if point == null: return Admission.failure("NullReferenceException", "Object reference not set to an instance of an object.")
		if not point is Dictionary: return Admission.failure("ArgumentException", "Waypoint point requires a value record.")
		if point.get("node_index") == node_index: return {"ok": true, "value": Admission.copy_value(point)}
	return Admission.failure("InvalidOperationException", Admission.message(["Level 100 waypoint path '", path.get("name"), "' has no node ", str(node_index), "."]))


class DefinitionSet extends RefCounted:
	var _actors: Array = []
	var _spawns: Array = []
	var _paths: Array = []
	var _motions: Array = []
	var _actor_keys: Dictionary = {}
	var _spawn_keys: Dictionary = {}
	var _request_keys: Dictionary = {}
	var _path_keys: Dictionary = {}
	var _motion_keys: Dictionary = {}
	var _world: int
	var _identity: String
	var _canonical: PackedByteArray

	func world_number() -> int: return _world
	func identity_sha256() -> String: return _identity
	func canonical_bytes() -> PackedByteArray: return _canonical.duplicate()
	func actors() -> Array: return Admission.copy_value(_actors)
	func spawns() -> Array: return Admission.copy_value(_spawns)
	func waypoint_paths() -> Array: return Admission.copy_value(_paths)
	func motion_definitions() -> Array: return Admission.copy_value(_motions)
	func snapshot() -> Dictionary:
		return {"world_number": _world, "identity_sha256": _identity, "actors": actors(), "spawns": spawns(),
			"waypoint_paths": waypoint_paths(), "motion_definitions": motion_definitions()}
	func get_actor_definition(identity: Variant) -> Dictionary:
		return _lookup(_actor_keys, identity, "Level 100 actor definition '", "' does not exist.")
	func get_spawn_definition(identity: Variant) -> Dictionary:
		return _lookup(_spawn_keys, identity, "Level 100 spawn definition '", "' does not exist.")
	func get_waypoint_path(name: Variant) -> Dictionary:
		return _lookup(_path_keys, name, "Level 100 waypoint path '", "' does not exist.")
	func get_motion_definition(name: Variant) -> Dictionary:
		return _lookup(_motion_keys, name, "Level 100 actor motion definition '", "' does not exist.")
	func find_motion_definition(name: Variant) -> Dictionary:
		var text: Dictionary = Text.units(name)
		if not text.ok: return text
		return {"ok": true, "value": Admission.copy_value(_motion_keys.get(Admission.key(text.value))) if text.value != null else null}
	func find_spawn_definition(owner: Variant, definition: Variant, spawner: Variant, script_name: Variant) -> Dictionary:
		var parts: Array = []
		for value: Variant in [owner, definition, spawner, script_name]:
			var text: Dictionary = Text.units(value)
			if not text.ok: return text
			parts.append(text.value)
		return {"ok": true, "value": Admission.copy_value(_request_keys.get(Admission.request_key(parts)))}
	func _lookup(table: Dictionary, value: Variant, prefix: String, suffix: String) -> Dictionary:
		if value == null: return Admission.failure("ArgumentNullException", "Value cannot be null.", "key")
		var text: Dictionary = Text.units(value)
		if not text.ok: return text
		var identity: String = Admission.key(text.value)
		if not table.has(identity): return Admission.failure("KeyNotFoundException", Admission.message([prefix, text.value, suffix]))
		return {"ok": true, "value": Admission.copy_value(table[identity])}


class Admission extends RefCounted:
	var error: Dictionary = {}

	func create(actors: Variant, spawns: Variant, paths: Variant, motions: Variant, world: Variant) -> Dictionary:
		if actors == null: return failure("ArgumentNullException", "Value cannot be null.", "actors")
		if spawns == null: return failure("ArgumentNullException", "Value cannot be null.", "spawns")
		if not is_i32(world): return failure("ArgumentException", "World number requires Int32.", "worldNumber")
		if Career.find_world(world) == null:
			return failure("ArgumentOutOfRangeException", "World %d is not a released career node." % world, "worldNumber")
		if not actors is Array or not spawns is Array or (paths != null and not paths is Array) or (motions != null and not motions is Array):
			return failure("ArgumentException", "Definition collections require arrays.")
		if actors.is_empty(): return failure("ArgumentException", "Level 100 requires at least one actor definition.", "actors")
		var set_value := DefinitionSet.new()
		set_value._world = world
		for index: int in range(actors.size()):
			if actors[index] == null: return failure("ArgumentException", "Level 100 actor definitions cannot contain null.", "actors")
			var actor: Dictionary = actor_value(actors[index])
			if not error.is_empty(): return error
			if not valid_actor(actor, index): return failure("ArgumentException", "Invalid Level 100 actor definition at authored order %d." % index)
			var identity: String = key(actor.definition_identity)
			if set_value._actor_keys.has(identity):
				return failure("ArgumentException", message(["Duplicate Level 100 actor definition identity '", actor.definition_identity, "'."]), "actors")
			set_value._actor_keys[identity] = actor
			set_value._actors.append(actor)
		for index: int in range(spawns.size()):
			if spawns[index] == null: return failure("ArgumentException", "Level 100 spawn definitions cannot contain null.", "spawns")
			var spawn: Dictionary = spawn_value(spawns[index])
			if not error.is_empty(): return error
			if not valid_spawn(spawn, index): return failure("ArgumentException", "Invalid Level 100 spawn definition at authored order %d." % index)
			if not valid_exits(spawn): return failure("ArgumentException", "Invalid or ambiguous spawner exit waypoint input.")
			if not set_value._actor_keys.has(key(spawn.owner_definition_identity)):
				return failure("ArgumentException", message(["Level 100 spawn owner '", spawn.owner_definition_identity, "' is undefined."]), "spawns")
			var identity: String = key(spawn.definition_identity)
			var request: String = request_key([spawn.owner_definition_identity, spawn.definition_name, spawn.spawner_name, spawn.script_name])
			if set_value._spawn_keys.has(identity) or set_value._request_keys.has(request):
				return failure("ArgumentException", message(["Duplicate Level 100 spawn definition '", spawn.definition_identity, "'."]), "spawns")
			set_value._spawn_keys[identity] = spawn
			set_value._request_keys[request] = spawn
			set_value._spawns.append(spawn)
		var supplied_paths: Array = paths if paths != null else []
		for index: int in range(supplied_paths.size()):
			if supplied_paths[index] == null: return failure("ArgumentException", "Level 100 waypoint paths cannot contain null.", "waypointPaths")
			var path: Dictionary = path_value(supplied_paths[index])
			if not error.is_empty(): return error
			if Text.is_null_or_white_space(path.name) or path.points == null or path.points.is_empty():
				return failure("ArgumentException", "Invalid Level 100 waypoint path at authored order %d." % index, "waypointPaths")
			# Enumerable.Any visits in source order and stops at the first invalid
			# point. A later null must not replace that earlier argument refusal.
			var point_values_valid: bool = true
			for point: Variant in path.points:
				if point == null: return failure("NullReferenceException", "Object reference not set to an instance of an object.")
				if point.node_index < 0 or not finite_words(point.retail_components_float_bits):
					point_values_valid = false
					break
			var identity: String = key(path.name)
			if not point_values_valid or not valid_path(path) or set_value._path_keys.has(identity):
				return failure("ArgumentException", message(["Invalid or duplicate Level 100 waypoint path '", path.name, "'."]), "waypointPaths")
			set_value._path_keys[identity] = path
			set_value._paths.append(path)
		var supplied_motions: Array = motions if motions != null else []
		for index: int in range(supplied_motions.size()):
			if supplied_motions[index] == null: return failure("ArgumentException", "Level 100 motion definitions cannot contain null.", "motionDefinitions")
			var motion: Dictionary = motion_value(supplied_motions[index])
			if not error.is_empty(): return error
			if not valid_motion(motion, index): return failure("ArgumentException", "Invalid Level 100 motion definition at authored order %d." % index)
			if not valid_mounts(motion): return failure("ArgumentException", "Invalid aircraft weapon mount input.")
			var found: bool = false
			for actor: Dictionary in set_value._actors:
				if actor.definition_name == motion.definition_name: found = true; break
			if not found:
				for spawn: Dictionary in set_value._spawns:
					if spawn.definition_name == motion.definition_name: found = true; break
			if not found:
				return failure("ArgumentException", message(["Level 100 motion definition '", motion.definition_name, "' has no actor."]), "motionDefinitions")
			var identity: String = key(motion.definition_name)
			if set_value._motion_keys.has(identity):
				return failure("ArgumentException", message(["Duplicate Level 100 motion definition '", motion.definition_name, "'."]), "motionDefinitions")
			set_value._motion_keys[identity] = motion
			set_value._motions.append(motion)
		var canonical: Dictionary = identity_bytes(set_value)
		if not canonical.ok: return failure("InvalidOperationException", canonical.error)
		set_value._canonical = canonical.bytes
		var hash := HashingContext.new()
		if hash.start(HashingContext.HASH_SHA256) != OK or hash.update(canonical.bytes) != OK:
			return failure("InvalidOperationException", "Cannot hash definition identity.")
		set_value._identity = hash.finish().hex_encode()
		return {"ok": true, "value": set_value}

	func actor_value(value: Variant) -> Dictionary:
		var r: Dictionary = record(value)
		var result: Dictionary = {"authored_order": integer(r, "authored_order"), "definition_identity": text(r, "definition_identity"),
			"name": text(r, "name"), "definition_name": text(r, "definition_name"), "script_name": text(r, "script_name"),
			"mesh_binding": text(r, "mesh_binding"), "thing_type_mask": integer(r, "thing_type_mask", true),
			"is_static": boolean(r, "is_static"), "active": boolean(r, "active"), "initial_health": integer(r, "initial_health"),
			"authored_transform": authored(field(r, "authored_transform")), "initial_pose": pose(field(r, "initial_pose")),
			"target_group": integer(r, "target_group"), "target_ordinal": integer(r, "target_ordinal"), "trigger": nullable_int(r, "trigger")}
		return result
	func spawn_value(value: Variant) -> Dictionary:
		var r: Dictionary = record(value)
		var result: Dictionary = {"authored_order": integer(r, "authored_order"), "definition_identity": text(r, "definition_identity"),
			"owner_definition_identity": text(r, "owner_definition_identity"), "definition_name": text(r, "definition_name"),
			"spawner_name": text(r, "spawner_name"), "script_name": text(r, "script_name"), "mesh_binding": text(r, "mesh_binding"),
			"thing_type_mask": integer(r, "thing_type_mask", true), "active": boolean(r, "active"), "initial_health": integer(r, "initial_health"),
			"initial_pose": pose(field(r, "initial_pose")), "authored_emitter_transform": emitter(field(r, "authored_emitter_transform")),
			"target_group": integer(r, "target_group"), "fixed_target_ordinal": integer(r, "fixed_target_ordinal"),
			"maximum_group_actors": integer(r, "maximum_group_actors"), "spawner_exit_waypoints": null}
		var supplied: Variant = r.get("spawner_exit_waypoints")
		if supplied != null:
			var points: Array = []
			for point: Variant in array_value(supplied):
				if point == null: points.append(null); continue
				var row: Dictionary = record(point)
				points.append({"selector": integer(row, "selector"), "model_transform": emitter(field(row, "model_transform"))})
			result.spawner_exit_waypoints = points
		return result
	func path_value(value: Variant) -> Dictionary:
		var r: Dictionary = record(value)
		var result: Dictionary = {"name": text(r, "name"), "points": null, "target_chain_node_indices": [], "is_closed": boolean(r, "is_closed")}
		var supplied: Variant = field(r, "points")
		if supplied != null:
			var points: Array = []
			for point: Variant in array_value(supplied):
				if point == null: points.append(null); continue
				var row: Dictionary = record(point)
				points.append({"node_index": integer(row, "node_index"), "position_millimeters": vector(field(row, "position_millimeters")),
					"retail_components_float_bits": vector(field(row, "retail_components_float_bits"), ["x", "y", "z", "w"])})
			result.points = points
		var chain: Variant = field(r, "target_chain_node_indices")
		if chain != null:
			if chain is PackedInt32Array: result.target_chain_node_indices = Array(chain)
			else: result.target_chain_node_indices = array_value(chain).duplicate()
			for node: Variant in result.target_chain_node_indices:
				if not is_i32(node): fail("Waypoint chain node requires Int32.")
		return result
	func motion_value(value: Variant) -> Dictionary:
		var r: Dictionary = record(value)
		var result: Dictionary = {"definition_name": text(r, "definition_name"), "weapon_mounts": null}
		for name: String in ["authored_order", "motion_class", "behavior_serialized_type", "behavior_internal_id", "steam_class_vtable_address", "arrival_radius_millimeters"]:
			result[name] = integer(r, name)
		for name: String in ["maximum_speed_float_bits", "maximum_turn_radians_per_base_tick_float_bits", "full_guide_base_ticks", "core_ground_origin_offset_millimeters"]:
			result[name] = nullable_int(r, name)
		var supplied: Variant = r.get("weapon_mounts")
		if supplied != null:
			var mounts: Array = []
			for mount: Variant in array_value(supplied):
				if mount == null: mounts.append(null); continue
				var row: Dictionary = record(mount)
				var use: Variant = field(row, "use")
				var use_value: Variant = null
				if use != null:
					var u: Dictionary = record(use)
					use_value = {"definition_name": text(u, "definition_name"), "tag_name": text(u, "tag_name"), "raw_creation_flags": integer(u, "raw_creation_flags", true)}
				var model: Dictionary = record(field(row, "model_pose"))
				mounts.append({"selector": integer(row, "selector"), "use": use_value, "model_pose": {
					"position_float_bits": vector(field(model, "position_float_bits")), "basis_float_bits": vector(field(model, "basis_float_bits"), BASIS_KEYS)}})
			result.weapon_mounts = mounts
		return result
	func authored(value: Variant) -> Variant:
		if value == null: return null
		var r: Dictionary = record(value)
		return {"retail_position_float_bits": vector(field(r, "retail_position_float_bits")),
			"retail_euler_float_bits": vector(field(r, "retail_euler_float_bits")), "retail_basis_float_bits": vector(field(r, "retail_basis_float_bits"), BASIS_KEYS)}
	func pose(value: Variant) -> Variant:
		if value == null: return null
		var r: Dictionary = record(value)
		return {"position_millimeters": vector(field(r, "position_millimeters")), "basis_float_bits": vector(field(r, "basis_float_bits"), BASIS_KEYS),
			"linear_velocity_millimeters_per_tick": vector(field(r, "linear_velocity_millimeters_per_tick")), "angular_velocity_micro_radians_per_tick": vector(field(r, "angular_velocity_micro_radians_per_tick"))}
	func emitter(value: Variant) -> Variant:
		if value == null: return null
		var r: Dictionary = record(value)
		return {"local_position_float_bits": vector(field(r, "local_position_float_bits")), "local_basis_float_bits": vector(field(r, "local_basis_float_bits"), BASIS_KEYS)}
	func vector(value: Variant, names: Array[String] = VECTOR_KEYS) -> Dictionary:
		var r: Dictionary = record(value)
		var result: Dictionary = {}
		for name: String in names: result[name] = integer(r, name)
		return result

	static func valid_actor(a: Dictionary, index: int) -> bool:
		return a.authored_order == index and not Text.is_null_or_white_space(a.definition_identity) and a.name != null \
			and a.authored_transform != null and a.initial_pose != null and finite_authored(a.authored_transform) \
			and finite_pose(a.initial_pose) and (a.thing_type_mask & ~PROVEN_THING_BITS) == 0 and a.initial_health >= 0 \
			and a.target_ordinal >= 0 and ((a.target_group == 0) == (a.target_ordinal == 0)) \
			and (a.trigger == null or a.target_group == 0)
	static func valid_spawn(s: Dictionary, index: int) -> bool:
		if s.authored_order != index: return false
		for name: String in ["definition_identity", "owner_definition_identity", "definition_name", "spawner_name", "script_name"]:
			if Text.is_null_or_white_space(s[name]): return false
		return s.initial_pose != null and s.authored_emitter_transform != null and finite_pose(s.initial_pose) \
			and (s.thing_type_mask & ~PROVEN_THING_BITS) == 0 and s.initial_health >= 0 and s.fixed_target_ordinal >= 0 \
			and (s.target_group != 0 or (s.fixed_target_ordinal == 0 and s.maximum_group_actors == 0)) \
			and (s.target_group == 0 or (s.maximum_group_actors > 0 and s.fixed_target_ordinal <= s.maximum_group_actors)) \
			and finite_emitter(s.authored_emitter_transform)
	static func valid_exits(s: Dictionary) -> bool:
		if s.spawner_exit_waypoints == null: return true
		if not (Text.equals_text(s.spawner_name, "SpawnerA") or Text.equals_text(s.spawner_name, "SpawnerB")) or s.spawner_exit_waypoints.is_empty(): return false
		var selectors: Dictionary = {}
		for point: Variant in s.spawner_exit_waypoints:
			if point == null or point.selector <= 0 or point.model_transform == null or not finite_emitter(point.model_transform) or selectors.has(point.selector): return false
			selectors[point.selector] = true
		return true
	static func valid_path(path: Dictionary) -> bool:
		var nodes: Dictionary = {}
		for point: Dictionary in path.points:
			if point.node_index < 0 or not finite_words(point.retail_components_float_bits): return false
			nodes[point.node_index] = true
		if path.target_chain_node_indices.size() != path.points.size(): return false
		var seen: Dictionary = {}
		for node: int in path.target_chain_node_indices:
			if seen.has(node) or not nodes.has(node): return false
			seen[node] = true
		return true
	static func valid_motion(m: Dictionary, index: int) -> bool:
		var ground_valid: bool = positive_float_word(m.maximum_speed_float_bits) and positive_float_word(m.maximum_turn_radians_per_base_tick_float_bits) \
			and m.full_guide_base_ticks != null and m.full_guide_base_ticks > 0 \
			and m.core_ground_origin_offset_millimeters != null and m.core_ground_origin_offset_millimeters > 0
		var no_ground: bool = m.maximum_speed_float_bits == null and m.maximum_turn_radians_per_base_tick_float_bits == null \
			and m.full_guide_base_ticks == null and m.core_ground_origin_offset_millimeters == null
		return m.authored_order == index and not Text.is_null_or_white_space(m.definition_name) and m.motion_class in [1, 2, 3] \
			and m.behavior_serialized_type > 0 and m.behavior_internal_id >= 0 and m.steam_class_vtable_address > 0 \
			and m.arrival_radius_millimeters > 0 and (ground_valid if m.motion_class == 1 else no_ground)
	static func valid_mounts(m: Dictionary) -> bool:
		if m.weapon_mounts == null: return true
		if m.motion_class != 2: return false
		for mount: Variant in m.weapon_mounts:
			if mount == null or mount.use == null or Text.is_null_or_white_space(mount.use.definition_name) \
				or not (Text.equals_text(mount.use.tag_name, "GunA") or Text.equals_text(mount.use.tag_name, "GunB")) \
				or mount.selector <= 0 or not finite_words(mount.model_pose.basis_float_bits) or not finite_words(mount.model_pose.position_float_bits): return false
		return true
	static func finite_words(words: Dictionary) -> bool:
		for word: int in words.values():
			if (word & 0x7f800000) == 0x7f800000: return false
		return true
	static func finite_pose(p: Dictionary) -> bool: return finite_words(p.basis_float_bits)
	static func finite_authored(t: Dictionary) -> bool:
		return finite_words(t.retail_position_float_bits) and finite_words(t.retail_euler_float_bits) and finite_words(t.retail_basis_float_bits)
	static func finite_emitter(t: Dictionary) -> bool: return finite_words(t.local_position_float_bits) and finite_words(t.local_basis_float_bits)
	static func positive_float_word(word: Variant) -> bool:
		return word != null and (word & 0x7f800000) != 0x7f800000 and Float32.read_word(word) > 0.0

	static func identity_bytes(s: DefinitionSet) -> Dictionary:
		var writer: RefCounted = Writer.new()
		writer.write_bytes("ONSLAUGHT-LEVEL100-ACTOR-DEFINITIONS".to_ascii_buffer())
		var exits: bool = false
		var mounts: bool = false
		for spawn: Dictionary in s._spawns: exits = exits or spawn.spawner_exit_waypoints != null
		for motion: Dictionary in s._motions: mounts = mounts or motion.weapon_mounts != null
		writer.write_i32(8 if mounts else (7 if exits else 6))
		# WorldNumber was never in these formats. Validate it but do not change
		# the existing identity bytes to conceal or repair that omission here.
		writer.write_i32(s._actors.size())
		for a: Dictionary in s._actors:
			writer.write_i32(a.authored_order); writer.write_string(a.definition_identity); writer.write_string(a.name)
			for name: String in ["definition_name", "script_name", "mesh_binding"]: write_nullable(writer, a[name], true)
			writer.write_u32(a.thing_type_mask); writer.write_bool(a.is_static); writer.write_bool(a.active); writer.write_i32(a.initial_health)
			write_vector(writer, a.authored_transform.retail_position_float_bits); write_vector(writer, a.authored_transform.retail_euler_float_bits)
			write_vector(writer, a.authored_transform.retail_basis_float_bits, BASIS_KEYS); write_pose(writer, a.initial_pose)
			writer.write_i32(a.target_group); writer.write_i32(a.target_ordinal); write_nullable(writer, a.trigger)
		writer.write_i32(s._spawns.size())
		for spawn: Dictionary in s._spawns:
			writer.write_i32(spawn.authored_order)
			for name: String in ["definition_identity", "owner_definition_identity", "definition_name", "spawner_name", "script_name"]: writer.write_string(spawn[name])
			write_nullable(writer, spawn.mesh_binding, true); writer.write_u32(spawn.thing_type_mask); writer.write_bool(spawn.active); writer.write_i32(spawn.initial_health)
			write_pose(writer, spawn.initial_pose); write_vector(writer, spawn.authored_emitter_transform.local_position_float_bits)
			write_vector(writer, spawn.authored_emitter_transform.local_basis_float_bits, BASIS_KEYS)
			writer.write_i32(spawn.target_group); writer.write_i32(spawn.fixed_target_ordinal); writer.write_i32(spawn.maximum_group_actors)
			if exits or mounts:
				writer.write_bool(spawn.spawner_exit_waypoints != null)
				if spawn.spawner_exit_waypoints != null:
					writer.write_i32(spawn.spawner_exit_waypoints.size())
					for point: Dictionary in spawn.spawner_exit_waypoints:
						writer.write_i32(point.selector); write_vector(writer, point.model_transform.local_position_float_bits)
						write_vector(writer, point.model_transform.local_basis_float_bits, BASIS_KEYS)
		writer.write_i32(s._paths.size())
		for path: Dictionary in s._paths:
			writer.write_string(path.name); writer.write_i32(path.points.size())
			for point: Dictionary in path.points:
				writer.write_i32(point.node_index); write_vector(writer, point.position_millimeters)
				write_vector(writer, point.retail_components_float_bits, ["x", "y", "z", "w"])
			writer.write_i32(path.target_chain_node_indices.size())
			for node: int in path.target_chain_node_indices: writer.write_i32(node)
			writer.write_bool(path.is_closed)
		writer.write_i32(s._motions.size())
		for m: Dictionary in s._motions:
			writer.write_i32(m.authored_order); writer.write_string(m.definition_name)
			for name: String in ["motion_class", "behavior_serialized_type", "behavior_internal_id", "steam_class_vtable_address", "arrival_radius_millimeters"]: writer.write_i32(m[name])
			for name: String in ["maximum_speed_float_bits", "maximum_turn_radians_per_base_tick_float_bits", "full_guide_base_ticks", "core_ground_origin_offset_millimeters"]: write_nullable(writer, m[name])
			if mounts:
				writer.write_bool(m.weapon_mounts != null)
				if m.weapon_mounts != null:
					writer.write_i32(m.weapon_mounts.size())
					for mount: Dictionary in m.weapon_mounts:
						writer.write_string(mount.use.definition_name); writer.write_string(mount.use.tag_name); writer.write_u32(mount.use.raw_creation_flags)
						writer.write_i32(mount.selector); write_vector(writer, mount.model_pose.position_float_bits); write_vector(writer, mount.model_pose.basis_float_bits, BASIS_KEYS)
		return writer.finish()
	static func write_vector(writer: RefCounted, value: Dictionary, names: Array[String] = VECTOR_KEYS) -> void:
		for name: String in names: writer.write_i32(value[name])
	static func write_pose(writer: RefCounted, p: Dictionary) -> void:
		write_vector(writer, p.position_millimeters); write_vector(writer, p.basis_float_bits, BASIS_KEYS)
		write_vector(writer, p.linear_velocity_millimeters_per_tick); write_vector(writer, p.angular_velocity_micro_radians_per_tick)
	static func write_nullable(writer: RefCounted, value: Variant, is_text: bool = false) -> void:
		writer.write_bool(value != null)
		if value != null:
			if is_text: writer.write_string(value)
			else: writer.write_i32(value)

	func record(value: Variant) -> Dictionary:
		if not value is Dictionary: fail("A definition value requires a record."); return {}
		return value
	func field(value: Dictionary, name: String) -> Variant:
		if not value.has(name): fail("Missing definition field: " + name); return null
		return value[name]
	func integer(value: Dictionary, name: String, unsigned: bool = false) -> int:
		var number: Variant = field(value, name)
		if typeof(number) != TYPE_INT or number < (0 if unsigned else -0x80000000) or number > (0xffffffff if unsigned else 0x7fffffff):
			fail("Definition field requires %s: %s" % ["UInt32" if unsigned else "Int32", name]); return 0
		return number
	func nullable_int(value: Dictionary, name: String) -> Variant:
		var number: Variant = field(value, name)
		return null if number == null else integer(value, name)
	func boolean(value: Dictionary, name: String) -> bool:
		var result: Variant = field(value, name)
		if typeof(result) != TYPE_BOOL: fail("Definition field requires Boolean: " + name); return false
		return result
	func text(value: Dictionary, name: String) -> Variant:
		var result: Dictionary = Text.units(field(value, name))
		if not result.ok: fail("Definition field requires UTF-16 text: " + name); return null
		return result.value
	func array_value(value: Variant) -> Array:
		if not value is Array: fail("Definition collection requires an array."); return []
		return value
	func fail(reason: String) -> void:
		if error.is_empty(): error = failure("ArgumentException", reason)
	static func is_i32(value: Variant) -> bool: return typeof(value) == TYPE_INT and value >= -0x80000000 and value <= 0x7fffffff
	static func key(value: Variant) -> String:
		return "N" if value == null else "S" + value.to_byte_array().hex_encode()
	static func request_key(parts: Array) -> String:
		var keys := PackedStringArray()
		for part: Variant in parts: keys.append(key(part))
		return ":".join(keys)
	static func copy_value(value: Variant) -> Variant:
		if value is PackedInt32Array or value is PackedByteArray: return value.duplicate()
		if value is Array:
			var array: Array = []
			for item: Variant in value: array.append(copy_value(item))
			return array
		if value is Dictionary:
			var result: Dictionary = {}
			for name: Variant in value: result[name] = copy_value(value[name])
			return result
		return value
	static func message(parts: Array) -> PackedInt32Array:
		var result := PackedInt32Array()
		for part: Variant in parts:
			if part != null: result.append_array(Text.units(part).value)
		return result
	static func failure(kind: String, reason: Variant, parameter: String = "") -> Dictionary:
		var units: PackedInt32Array = Text.units(reason).value
		var display: Dictionary = Text.native_string(units)
		return {"ok": false, "error_type": kind, "error": display.value if display.ok else "Definition error (see error_units).",
			"error_units": units, "parameter": parameter}
