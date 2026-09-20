# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pinned Level100ActorDefinitionManifest.cs projection. The caller supplies
## bytes; this decoder owns no files, scenes or mutable registry. Schema v14's
## signed-basis zeros, corrected Trainer life, authored exits and weapon model
## poses remain literal data. Live muzzle/attachment cache state is not inferred.
const Definitions = preload("res://Core/actor_definitions.gd")
const Strict = preload("res://Core/strict_json.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const Number = preload("res://Core/invariant_number.gd")
const EXPECTED_MANIFEST_SHA256: String = "17D6112A96D548FB546999B79D3980D173CE5BB0A6F0DA4573EAE28FC5B62C09"
const EXPECTED_SCHEMA: String = "onslaught.level100-static-world.v14"
const EXPECTED_ARCHIVE_SHA256: String = "ED6350C0E214D00AB1BF6A7BD137FBA3E77D0AFE19A6DC4C0607F56AC037496A"
const EXPECTED_PHYSICS_SHA256: String = "E1FB3DEDBEB29B4B4151DA2C8CBBDC940B716B1A2321E1D6A9BA1542C74ADA14"
const MAXIMUM_MANIFEST_BYTES: int = 512000
const TARGET_GROUPS: Dictionary = {"None": 0, "StaticTargets": 1, "TargetTrucks": 2, "MovingTargets": 3, "AirborneTargets1": 4, "AirborneTargets2": 5, "AirTrainer": 6}
const TRIGGERS: Dictionary = {"TargetZone1": 1, "FiringRange": 2, "TargetZone2": 3, "TargetZone3": 4, "TargetZone4": 5}
const MOTION_CLASSES: Dictionary = {"GroundVehicle": 1, "Plane": 2, "Dropship": 3}


static func decode(source: Variant) -> Dictionary:
	var reader := ManifestReader.new()
	var admitted: Dictionary = reader.read_validated(source)
	if not admitted.ok: return admitted
	return reader.project(admitted.value)


## The map covers the 33 base-world identities only, exactly like C#. The
## eleven level-world actors remain absent; callers retain their existing
## fallback. Allegiance is presentation data and never enters definition hash.
static func decode_authored_allegiance(source: Variant) -> Dictionary:
	var reader := ManifestReader.new()
	var admitted: Dictionary = reader.read_validated(source)
	if not admitted.ok: return admitted
	var root: Strict.Value = admitted.value
	var result: Dictionary = {}
	for object_value: Strict.Value in reader.array(root, "Objects"):
		var ordinal: int = reader.integer(object_value, "Ordinal")
		var number: String = str(-ordinal if ordinal < 0 else ordinal).pad_zeros(4)
		var identity: String = "wres:bswd:" + ("-" if ordinal < 0 else "") + number
		result[identity] = reader.integer(object_value, "Allegiance")
	if not reader.error.is_empty(): return reader.error
	if result.size() != reader.integer(root, "VisibleObjectCount"):
		return Definitions.Admission.failure("InvalidDataException", "The Level 100 base-world object ordinals are not unique.")
	return {"ok": true, "value": result}


class ManifestReader extends RefCounted:
	var error: Dictionary = {}

	func read_validated(source: Variant) -> Dictionary:
		# A null byte[] converted to C# ReadOnlySpan<byte> is an empty span.
		if source != null and not source is PackedByteArray:
			return Definitions.Admission.failure("ArgumentException", "Manifest requires an exact byte array.")
		if source == null or source.is_empty() or source.size() > MAXIMUM_MANIFEST_BYTES:
			return changed()
		var hash := HashingContext.new()
		if hash.start(HashingContext.HASH_SHA256) != OK or hash.update(source) != OK:
			return Definitions.Admission.failure("InvalidOperationException", "Cannot hash supplied actor manifest.")
		if hash.finish().hex_encode().to_upper() != EXPECTED_MANIFEST_SHA256:
			return changed()
		# JsonSerializer's property binding uses last-property semantics. Retain
		# ordered properties, strict numbers and exact UTF-16 until this schema
		# projects them. No arbitrary unhashed manifest is publicly admitted.
		var parsed: Dictionary = Strict.parse_bytes(source, false, 64)
		if not parsed.ok: return Definitions.Admission.failure("JsonException", parsed.error)
		var root: Strict.Value = parsed.value
		if root.kind == "null": return Definitions.Admission.failure("InvalidDataException", "The Level 100 actor-definition manifest is empty.")
		if root.kind != "object": return Definitions.Admission.failure("JsonException", "Manifest requires a JSON object.")
		var schema: Variant = string_value(root, "Schema", "")
		var archive: Variant = string_value(root, "SourceArchiveSha256", "")
		var physics: Variant = string_value(root, "PhysicsSourceSha256", "")
		var actors: Array = array(root, "ActorDefinitions")
		var spawns: Array = array(root, "SpawnDefinitions")
		var paths: Array = array(root, "WaypointPaths")
		var motions: Array = array(root, "MotionDefinitions")
		var base_count: int = 0
		for actor: Strict.Value in actors:
			var identity: Variant = string_value(actor, "DefinitionIdentity", "")
			if identity != null and identity.slice(0, 10) == Text.units("wres:bswd:").value: base_count += 1
		if not error.is_empty(): return error
		if not Text.equals_text(schema, EXPECTED_SCHEMA) or not ascii_equal_ignore_case(archive, EXPECTED_ARCHIVE_SHA256) \
			or not ascii_equal_ignore_case(physics, EXPECTED_PHYSICS_SHA256) or integer(root, "UnitRecordCount") != 35 \
			or integer(root, "VisibleObjectCount") != 33 or actors.size() != 44 or spawns.size() != 10 \
			or paths.size() != 8 or motions.size() != 5 or base_count != 33:
			return Definitions.Admission.failure("InvalidDataException", "The Level 100 actor-definition identity or authored counts changed.")
		if not error.is_empty(): return error
		return {"ok": true, "value": root}

	func project(root: Strict.Value) -> Dictionary:
		var actors: Array = []
		for source: Strict.Value in array(root, "ActorDefinitions"):
			var trigger: Variant = string_value(source, "Trigger")
			actors.append({"authored_order": integer(source, "AuthoredOrder"), "definition_identity": string_value(source, "DefinitionIdentity", ""),
				"name": string_value(source, "Name", ""), "definition_name": empty_to_null(string_value(source, "DefinitionName")),
				"script_name": empty_to_null(string_value(source, "ScriptName")), "mesh_binding": empty_to_null(string_value(source, "MeshBinding")),
				"thing_type_mask": integer(source, "ThingTypeMask", true), "is_static": boolean(source, "IsStatic"), "active": boolean(source, "Active"),
				"initial_health": integer(source, "InitialHealth"), "authored_transform": authored(object_field(source, "AuthoredTransform")),
				"initial_pose": pose(object_field(source, "InitialPose")), "target_group": enumeration(string_value(source, "TargetGroup", ""), TARGET_GROUPS, "target group"),
				"target_ordinal": integer(source, "TargetOrdinal"), "trigger": null if trigger == null else enumeration(trigger, TRIGGERS, "trigger")})
			if not error.is_empty(): return error
		var spawns: Array = []
		for source: Strict.Value in array(root, "SpawnDefinitions"):
			var exits: Variant = null
			var authored_exits: Variant = nullable_array(source, "SpawnerExitWaypoints")
			if authored_exits != null:
				exits = []
				for point: Strict.Value in authored_exits:
					exits.append({"selector": integer(point, "Selector"), "model_transform": emitter(object_field(point, "ModelTransform"))})
			spawns.append({"authored_order": integer(source, "AuthoredOrder"), "definition_identity": string_value(source, "DefinitionIdentity", ""),
				"owner_definition_identity": string_value(source, "OwnerDefinitionIdentity", ""), "definition_name": string_value(source, "DefinitionName", ""),
				"spawner_name": string_value(source, "SpawnerName", ""), "script_name": string_value(source, "ScriptName", ""),
				"mesh_binding": empty_to_null(string_value(source, "MeshBinding")), "thing_type_mask": integer(source, "ThingTypeMask", true),
				"active": boolean(source, "Active"), "initial_health": integer(source, "InitialHealth"), "initial_pose": pose(object_field(source, "InitialPose")),
				"authored_emitter_transform": emitter(object_field(source, "AuthoredEmitterTransform")),
				"target_group": enumeration(string_value(source, "TargetGroup", ""), TARGET_GROUPS, "target group"),
				"fixed_target_ordinal": integer(source, "FixedTargetOrdinal"), "maximum_group_actors": integer(source, "MaximumGroupActors"),
				"spawner_exit_waypoints": exits})
			if not error.is_empty(): return error
		var paths: Array = []
		for source: Strict.Value in array(root, "WaypointPaths"):
			var points: Array = []
			for point: Strict.Value in array(source, "Points"):
				points.append({"node_index": integer(point, "NodeIndex"),
					"position_millimeters": vector(point, "PositionMillimeters", ["x", "y", "z"], "A Level 100 waypoint point changed shape."),
					"retail_components_float_bits": vector(point, "RetailComponentsFloatBits", ["x", "y", "z", "w"], "A Level 100 waypoint point changed shape.")})
			var chain: Array = int_array(source, "TargetChainNodeIndices")
			if not error.is_empty(): return error
			var name: Variant = string_value(source, "Name", "")
			if chain.size() != points.size():
				return Definitions.Admission.failure("InvalidDataException", Definitions.Admission.message(["Level 100 waypoint path '", name,
					"' has ", str(chain.size()), " chain entries for ", str(points.size()), " nodes."]))
			paths.append({"name": name, "points": points, "target_chain_node_indices": chain, "is_closed": boolean(source, "IsClosed")})
		var motions: Array = []
		for source: Strict.Value in array(root, "MotionDefinitions"):
			var mounts: Variant = null
			var supplied_mounts: Variant = nullable_array(source, "WeaponMounts")
			if supplied_mounts != null:
				mounts = []
				for mount: Strict.Value in supplied_mounts:
					var use: Strict.Value = member(mount, "Use")
					if use == null or use.kind == "null": return Definitions.Admission.failure("InvalidDataException", "An aircraft weapon use is missing.")
					var model: Strict.Value = object_field(mount, "ModelTransform")
					mounts.append({"use": {"definition_name": string_value(use, "DefinitionName"), "tag_name": string_value(use, "TagName"),
						"raw_creation_flags": integer(use, "RawCreationFlags", true)}, "selector": integer(mount, "Selector"),
						"model_pose": {"position_float_bits": vector(model, "LocalPositionFloatBits", ["x", "y", "z"], "A Level 100 actor weapon model position changed shape."),
						"basis_float_bits": vector(model, "LocalBasisFloatBits", Definitions.BASIS_KEYS, "A Level 100 actor weapon model basis changed shape.")}})
			motions.append({"authored_order": integer(source, "AuthoredOrder"), "definition_name": string_value(source, "DefinitionName", ""),
				"motion_class": enumeration(string_value(source, "MotionClass", ""), MOTION_CLASSES, "motion class"),
				"behavior_serialized_type": integer(source, "BehaviorSerializedType"), "behavior_internal_id": integer(source, "BehaviorInternalId"),
				"steam_class_vtable_address": integer(source, "SteamClassVtableAddress"), "arrival_radius_millimeters": integer(source, "ArrivalRadiusMillimeters"),
				"maximum_speed_float_bits": nullable_int(source, "MaximumSpeedFloatBits"),
				"maximum_turn_radians_per_base_tick_float_bits": nullable_int(source, "MaximumTurnRadiansPerBaseTickFloatBits"),
				"full_guide_base_ticks": nullable_int(source, "FullGuideBaseTicks"),
				"core_ground_origin_offset_millimeters": nullable_int(source, "CoreGroundOriginOffsetMillimeters"), "weapon_mounts": mounts})
			if not error.is_empty(): return error
		return Definitions.create(actors, spawns, paths, motions)

	func authored(source: Strict.Value) -> Variant:
		if source == null or source.kind == "null": fail("ArgumentNullException", "Value cannot be null.", "source"); return null
		return {"retail_position_float_bits": vector(source, "RetailPositionFloatBits", ["x", "y", "z"], "A Level 100 actor authored position changed shape."),
			"retail_euler_float_bits": vector(source, "RetailEulerFloatBits", ["x", "y", "z"], "A Level 100 actor authored Euler changed shape."),
			"retail_basis_float_bits": vector(source, "RetailBasisFloatBits", Definitions.BASIS_KEYS, "A Level 100 actor authored basis changed shape.")}
	func pose(source: Strict.Value) -> Variant:
		if source == null or source.kind == "null": fail("ArgumentNullException", "Value cannot be null.", "source"); return null
		return {"position_millimeters": vector(source, "PositionMillimeters", ["x", "y", "z"], "A Level 100 actor position changed shape."),
			"basis_float_bits": vector(source, "BasisFloatBits", Definitions.BASIS_KEYS, "A Level 100 actor basis changed shape."),
			"linear_velocity_millimeters_per_tick": vector(source, "LinearVelocityMillimetersPerTick", ["x", "y", "z"], "A Level 100 actor linear velocity changed shape."),
			"angular_velocity_micro_radians_per_tick": vector(source, "AngularVelocityMicroRadiansPerTick", ["x", "y", "z"], "A Level 100 actor angular velocity changed shape.")}
	func emitter(source: Strict.Value) -> Variant:
		if source == null or source.kind == "null": fail("ArgumentNullException", "Value cannot be null.", "source"); return null
		return {"local_position_float_bits": vector(source, "LocalPositionFloatBits", ["x", "y", "z"], "A Level 100 authored emitter transform changed shape."),
			"local_basis_float_bits": vector(source, "LocalBasisFloatBits", Definitions.BASIS_KEYS, "A Level 100 authored emitter transform changed shape.")}
	func vector(source: Strict.Value, name: String, fields: Array[String], reason: String) -> Dictionary:
		var values: Array = int_array(source, name)
		if values.size() != fields.size(): fail("InvalidDataException", reason); return {}
		var result: Dictionary = {}
		for index: int in range(fields.size()): result[fields[index]] = values[index]
		return result
	func int_array(source: Strict.Value, name: String) -> Array:
		var result: Array = []
		for value: Strict.Value in array(source, name): result.append(read_int(value))
		return result
	func integer(source: Strict.Value, name: String, unsigned: bool = false) -> int:
		var value: Strict.Value = member(source, name)
		return 0 if value == null else read_int(value, unsigned)
	func nullable_int(source: Strict.Value, name: String) -> Variant:
		var value: Strict.Value = member(source, name)
		return null if value == null or value.kind == "null" else read_int(value)
	func read_int(value: Strict.Value, unsigned: bool = false) -> int:
		var result: Dictionary = value.as_int64()
		if not result.ok or result.value < (0 if unsigned else -0x80000000) or result.value > (0xffffffff if unsigned else 0x7fffffff):
			fail("JsonException", "Manifest integer is outside its declared type."); return 0
		return result.value
	func boolean(source: Strict.Value, name: String) -> bool:
		var value: Strict.Value = member(source, name)
		if value == null: return false
		if value.kind != "boolean": fail("JsonException", "Manifest Boolean has an invalid token."); return false
		return value.boolean
	func string_value(source: Strict.Value, name: String, fallback: Variant = null) -> Variant:
		var value: Strict.Value = member(source, name)
		if value == null: return Text.units(fallback).value
		if value.kind == "null": return null
		if value.kind != "string": fail("JsonException", "Manifest text has an invalid token."); return null
		var unicode: Dictionary = value.utf8_bytes()
		if not unicode.ok: fail("JsonException", unicode.error); return null
		return value.string_units.duplicate()
	func array(source: Strict.Value, name: String) -> Array:
		var value: Strict.Value = member(source, name)
		if value == null: return []
		if value.kind != "array": fail("JsonException", "Manifest collection has an invalid token."); return []
		return value.items
	func nullable_array(source: Strict.Value, name: String) -> Variant:
		var value: Strict.Value = member(source, name)
		return null if value == null or value.kind == "null" else array(source, name)
	func object_field(source: Strict.Value, name: String) -> Strict.Value:
		var value: Strict.Value = member(source, name)
		return Strict.Value.new("object") if value == null else value
	func member(source: Strict.Value, name: String) -> Strict.Value:
		if source == null or source.kind == "null": fail("NullReferenceException", "Object reference not set to an instance of an object."); return null
		if source.kind != "object": fail("JsonException", "Manifest record has an invalid token."); return null
		# All admitted schema property names are ASCII. Their binding is case
		# insensitive and last-match wins, as in this pinned JsonSerializer DTO.
		for index: int in range(source.members.size() - 1, -1, -1):
			if ascii_equal_ignore_case(source.members[index].name.string_units, name): return source.members[index].value
		return null
	func enumeration(value: Variant, names: Dictionary, role: String) -> int:
		var units: PackedInt32Array = value if value != null else PackedInt32Array()
		var start: int = 0
		var end: int = units.size()
		while start < end and Text.is_white_space(units[start]): start += 1
		while end > start and Text.is_white_space(units[end - 1]): end -= 1
		units = units.slice(start, end)
		var parsed: Dictionary = Text.native_string(units)
		if parsed.ok:
			var native: String = parsed.value
			if names.has(native): return names[native]
			var numeric: Dictionary = Number.parse_int32(units)
			if numeric.ok and numeric.value in names.values(): return numeric.value
			# Enum.TryParse also permits comma-separated names on a non-flags
			# enum; IsDefined is still the final gate on their combined value.
			var combined: int = 0
			var valid: bool = true
			for part: String in native.split(","):
				var trimmed: String = part.strip_edges()
				if not names.has(trimmed): valid = false; break
				combined |= names[trimmed]
			if valid and combined in names.values(): return combined
		fail("InvalidDataException", Definitions.Admission.message(["A Level 100 actor ", role, " is invalid: ", value, "."]))
		return 0
	func fail(kind: String, reason: Variant, parameter: String = "") -> void:
		if error.is_empty(): error = Definitions.Admission.failure(kind, reason, parameter)
	static func empty_to_null(value: Variant) -> Variant: return null if value == null or value.is_empty() else value
	static func ascii_equal_ignore_case(value: Variant, expected: String) -> bool:
		if value == null or value.size() != expected.length(): return false
		for index: int in range(value.size()):
			var left: int = value[index]
			var right: int = expected.unicode_at(index)
			if left >= 65 and left <= 90: left += 32
			if right >= 65 and right <= 90: right += 32
			if left != right: return false
		return true
	static func changed() -> Dictionary:
		return Definitions.Admission.failure("InvalidDataException", "The locally materialized Level 100 actor-definition manifest is missing or changed.")
