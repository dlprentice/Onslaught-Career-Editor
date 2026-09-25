# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Node3D
## The same admitted part hierarchy and materials serve private imported scenes,
## editor inspection and gameplay. This component owns presentation only. The
## caller supplies transition time/contact facts; no input, clock or simulation
## runs here. Public template previews own no serializable derived children.
const Aquila = preload("res://Client/aquila_mesh.gd")
const Factory = preload("res://Scenes/Shared/retail_fixed_function_material.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Field = preload("res://Scenes/World/height_field.gd")
const MeshGuard = preload("res://Scenes/Aquila/aquila_mesh_instance.gd")
const SOURCES: Dictionary = {"walker": "res://Assets/Aquila/Source/m_f_be1.msh.aya", "jet": "res://Assets/Aquila/Source/m_f_be2.msh.aya", "cockpit": "res://Assets/Aquila/Source/m_cockpit2.msh.aya"}
const GUN_SIGNATURE: String = "layers-00000000-ffffffff-ffffffff-ffffffff-ffffffff-ffffffff"
@export_enum("walker", "jet", "cockpit") var profile: String = "walker"
@export var cockpit_texture: Texture2D
@export var texture_a: Texture2D
@export var texture_b: Texture2D
@export var chrome_texture: Texture2D
@export var gun_light_texture: Texture2D
@export var gun_light_material: StandardMaterial3D
var _asset: RefCounted
var _parts: Array[Dictionary] = []
var _nodes: Array[Node3D] = []
var _profile: Dictionary = {}
var _leg_lengths: Array[PackedFloat32Array] = []
var _clearance: float = 0.0
var _preview_error: String = ""
var _gun_light_instance: StandardMaterial3D


func _ready() -> void:
	set_process(false)
	set_physics_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	# Saved private scenes already contain their actual hierarchy. Inspection
	# neither resets those poses nor creates an animation/sampler owner.
	if Engine.is_editor_hint() and _asset == null and get_child_count() == 0:
		var prepared: Dictionary = prepare_preview()
		if not prepared.ok: _preview_error = prepared.error
		update_configuration_warnings()


func _get_configuration_warnings() -> PackedStringArray:
	return PackedStringArray([_preview_error]) if not _preview_error.is_empty() else PackedStringArray()


func prepare_preview() -> Dictionary:
	if not Engine.is_editor_hint(): return failure("InvalidOperationException", "Aquila preview is an editor-only read-only operation.")
	if not SOURCES.has(profile): return failure("ArgumentException", "Unknown Aquila profile.")
	if not FileAccess.file_exists(SOURCES[profile]): return failure("InvalidDataException", "Prepared private Aquila source is missing: " + SOURCES[profile])
	var terrain_path: String = ProjectSettings.globalize_path("res://").path_join("../OnslaughtRebuild.Core/Assets/Level100/level100-heightfield.hfld.bin").simplify_path()
	if not FileAccess.file_exists(terrain_path): return failure("InvalidDataException", "Prepared Level 100 lighting metadata is missing.")
	var field: Dictionary = Field.from_bytes(FileAccess.get_file_as_bytes(terrain_path))
	if not field.ok: return field
	var facts: Dictionary = field.value.metadata()
	var result: Dictionary = configure_prepared(facts, false, false)
	# The admitted data survives only as these normal transient visual nodes;
	# inspection cannot advance it through the runtime methods.
	_asset = null
	_parts.clear()
	_nodes.clear()
	_profile = {}
	_leg_lengths.clear()
	return result


func texture_bindings() -> Dictionary:
	match profile:
		"walker": return {0: cockpit_texture, 1: texture_b, 3: texture_a}
		"jet": return {0: cockpit_texture, 1: chrome_texture, 2: texture_b, 3: chrome_texture, 4: texture_a}
		"cockpit": return {0: gun_light_texture, 1: cockpit_texture, 2: chrome_texture}
	return {}


func default_material_overrides() -> Variant:
	if profile != "cockpit": return null
	if _gun_light_instance == null and gun_light_material != null:
		# Keep the authored recipe external and its texture shared. The actual
		# unshaded draw material has the same built-in save boundary as the old
		# factory: Godot omits inactive emission fields when it is serialized.
		# Explicit caller-supplied overrides bypass this recipe and stay shared.
		_gun_light_instance = gun_light_material.duplicate(false)
		# Resource.duplicate applies the same inactive-property filter as save;
		# retain the original factory's fresh in-memory values before that save.
		_gun_light_instance.emission_enabled = gun_light_material.emission_enabled
		_gun_light_instance.emission = gun_light_material.emission
		_gun_light_instance.emission_energy_multiplier = gun_light_material.emission_energy_multiplier
		_gun_light_instance.emission_texture = gun_light_material.emission_texture
	return {GUN_SIGNATURE: _gun_light_instance}


func configure_prepared(facts: Variant, retain_saved: bool = true, private_bake: bool = false) -> Dictionary:
	if not SOURCES.has(profile): return failure("ArgumentException", "Unknown Aquila profile.")
	# Source data is the existing ignored materialization, read in place. A
	# saved hierarchy needs exact source admission, but no new texture, fog or
	# material preparation. Its existing resource objects remain authoritative.
	var source := PackedByteArray()
	if FileAccess.file_exists(SOURCES[profile]): source = FileAccess.get_file_as_bytes(SOURCES[profile])
	if retain_saved or source.is_empty(): return configure_bytes(source, profile, {}, null, null, retain_saved, private_bake)
	var textures: Dictionary = texture_bindings()
	for texture: Texture2D in textures.values():
		if texture != null and texture.has_method("ensure_loaded"):
			var loaded: Dictionary = texture.ensure_loaded()
			if not loaded.ok: return loaded
	return configure_bytes(source, profile, textures, facts, default_material_overrides(), false, private_bake)


func configure_bytes(source: PackedByteArray, selected_profile: String, textures: Dictionary, facts: Variant,
		material_overrides: Variant = null, retain_saved: bool = true, private_bake: bool = false) -> Dictionary:
	var admitted: Dictionary = Aquila.from_bytes(source, selected_profile)
	if not admitted.ok: return admitted
	var parsed: RefCounted = admitted.value
	var parts: Array[Dictionary] = parsed.get("_parts")
	var selected: Dictionary = parsed.get("_profile")
	var nodes: Array[Node3D] = []
	if retain_saved:
		for part: Dictionary in parts:
			var parent: Node3D = self if part.parent == null else nodes[part.parent]
			var node: Node3D = parent.get_node_or_null(part_name(part))
			if node == null: return failure("InvalidDataException", "Scene lost " + selected.display_name + " hierarchy at part " + str(part.index) + ".")
			if part.geometry != null:
				var geometry: MeshInstance3D = node.get_node_or_null("Geometry")
				if geometry == null or geometry.mesh == null: return failure("InvalidDataException", "Scene lost " + selected.display_name + " geometry at part " + str(part.index) + ".")
			nodes.append(node)
	else:
		if get_child_count() != 0: return failure("InvalidOperationException", "Aquila creation requires an empty component; bind saved parts explicitly.")
		var built: Dictionary = build_parts(parts, parsed.get("_textures"), textures, facts, selected, material_overrides, private_bake)
		if not built.ok: return built
		nodes.assign(built.nodes)
	_asset = parsed
	_parts = parts
	_nodes = nodes
	_profile = selected
	_leg_lengths = parsed.get("_leg_lengths")
	_clearance = parsed.get("_clearance")
	profile = selected_profile
	if _profile.is_walker:
		set_standing_pose()
	else:
		var result: Dictionary = set_virtual_frame(_profile.initial_frame)
		if not result.ok: return result
		position = _profile.root_offset
	return {"ok": true}


func counts() -> Dictionary:
	return {"part_count": _parts.size(), "surface_count": 0 if _asset == null else _asset.get("_surfaces"),
		"animated_count": _profile.get("animated_count", 0), "standing_clearance": _clearance}


func set_virtual_frame(virtual_frame: Variant) -> Dictionary:
	if _asset == null: return failure("InvalidOperationException", "Aquila runtime is not configured.")
	if _profile.is_walker: return failure("InvalidOperationException", "The walker hierarchy is driven by its grounded leg pose.")
	if typeof(virtual_frame) not in [TYPE_INT, TYPE_FLOAT]: return failure("ArgumentException", "Virtual frame requires a Single value.")
	for index: int in range(_parts.size()): _nodes[index].transform = Aquila.Asset.to_godot(Aquila.Asset.part_transform(_parts[index], F.value(virtual_frame)))
	return {"ok": true}


func set_ground_contact_pose(contacts: Variant) -> Dictionary:
	if _asset == null: return failure("InvalidOperationException", "Aquila runtime is not configured.")
	if contacts == null: return failure("ArgumentNullException", "Value cannot be null. (Parameter 'contactsInPlayerSpace')")
	if not contacts is PackedVector3Array and not contacts is Array: return failure("ArgumentException", "Contacts require a Vector3 sequence.")
	if contacts.size() != 4: return failure("ArgumentException", "The retained Aquila walker requires exactly four foot contacts. (Parameter 'contactsInPlayerSpace')")
	for value: Variant in contacts:
		if not value is Vector3: return failure("ArgumentException", "Contacts require a Vector3 sequence.")
	# This reset precedes the old non-walker leg-cache failure. No new IsWalker
	# or finite-value guard may move that mutation behind admission.
	set_standing_pose()
	for leg: Array in Aquila.LEGS:
		var target: Vector3 = contacts[leg[0]] - position
		var standing: Array[Transform3D] = current_globals()
		var anchor: Vector3 = standing[leg[1]].origin
		if leg[0] >= _leg_lengths.size(): return failure("IndexOutOfRangeException", "Index was outside the bounds of the array.")
		var desired_length: float = Aquila.Asset.distance(anchor, target)
		var closest_frame: int = 1
		var closest_delta: float = INF
		for frame: int in range(1, 101):
			var delta: float = absf(F.value(_leg_lengths[leg[0]][frame] - desired_length))
			if delta < closest_delta:
				closest_delta = delta
				closest_frame = frame
		for index: int in leg[3]: _nodes[index].transform = Aquila.Asset.to_godot(Aquila.Asset.part_transform(_parts[index], closest_frame))
		var posed: Array[Transform3D] = current_globals()
		var root_global: Transform3D = posed[leg[1]]
		var source: Vector3 = posed[leg[2]].origin - root_global.origin
		var desired: Vector3 = target - root_global.origin
		if Aquila.Asset.squared_length(source) <= F.value(0.000001) or Aquila.Asset.squared_length(desired) <= F.value(0.000001): continue
		var arc: Dictionary = contact_arc(Aquila.Asset.normalized(source), Aquila.Asset.normalized(desired))
		if not arc.ok: return arc
		var correction: Basis = arc.value
		root_global.basis = correction * root_global.basis
		_nodes[leg[1]].transform = root_global if _parts[leg[1]].parent == null else posed[_parts[leg[1]].parent].affine_inverse() * root_global
	return {"ok": true}


static func contact_arc(source: Vector3, desired: Vector3) -> Dictionary:
	# The pinned GodotSharp Quaternion checks zero after the caller's first
	# normalization. Native Godot additionally sanitizes nonfinite inputs, which
	# would change both the existing error order and the old NaN pose words.
	var epsilon: float = F.value(0.000001)
	if (absf(source.x) < epsilon and absf(source.y) < epsilon and absf(source.z) < epsilon) or (absf(desired.x) < epsilon and absf(desired.y) < epsilon and absf(desired.z) < epsilon):
		return failure("ArgumentException", "The vectors must not be zero.")
	if source.is_finite() and desired.is_finite(): return {"ok": true, "value": Basis(Quaternion(source, desired))}
	# Preserve the IEEE arithmetic of this nonfinite domain. A nonfinite
	# normalized operand makes the dot product and all four arc words NaN;
	# calculating them preserves the original sign/payload through the stores.
	var a: Vector3 = Aquila.Asset.normalized(source)
	var b: Vector3 = Aquila.Asset.normalized(desired)
	var dot: float = Aquila.Asset.sum3(a.x, b.x, a.y, b.y, a.z, b.z)
	var cross: Vector3 = a.cross(b)
	var scale: float = F.value(sqrt(F.value(F.value(1.0 + dot) * 2.0)))
	var reciprocal: float = F.value(1.0 / scale)
	var q := Quaternion(F.value(cross.x * reciprocal), F.value(cross.y * reciprocal), F.value(cross.z * reciprocal), F.value(scale * 0.5))
	var length: float = F.value(sqrt(F.value(Aquila.Asset.sum3(q.x, q.x, q.y, q.y, q.z, q.z) + F.value(q.w * q.w))))
	return {"ok": true, "value": Basis(Quaternion(F.value(q.x / length), F.value(q.y / length), F.value(q.z / length), F.value(q.w / length)))}


func set_standing_pose() -> void:
	for index: int in range(_parts.size()): _nodes[index].transform = Aquila.Asset.to_godot(Aquila.Asset.standing_transform(_parts[index]))
	position = Vector3(0.0, _clearance, 0.0)


func current_globals() -> Array[Transform3D]:
	var globals: Array[Transform3D] = []
	for index: int in range(_parts.size()):
		globals.append(_nodes[index].transform if _parts[index].parent == null else globals[_parts[index].parent] * _nodes[index].transform)
	return globals


func build_parts(parts: Array[Dictionary], metadata: Array[Dictionary], textures: Dictionary, facts: Variant,
		selected: Dictionary, overrides: Variant, private_bake: bool) -> Dictionary:
	var nodes: Array[Node3D] = []
	var meshes: Dictionary = {}
	var materials: Dictionary = {}
	name = selected.root_name
	for part: Dictionary in parts:
		var node := Node3D.new()
		node.name = part_name(part)
		node.transform = Aquila.Asset.to_godot(Aquila.Asset.standing_transform(part) if selected.is_walker else Aquila.Asset.part_transform(part, selected.initial_frame))
		nodes.append(node)
		var parent: Node3D = self if part.parent == null else nodes[part.parent]
		parent.add_child(node)
		if private_bake: node.owner = self
		if part.geometry != null:
			var mesh: ArrayMesh = meshes.get(part.geometry_owner)
			if mesh == null:
				var built: Dictionary = build_mesh(part.geometry, metadata, textures, facts, materials, overrides, selected.operation)
				if not built.ok: return built
				mesh = built.value
				meshes[part.geometry_owner] = mesh
			var geometry: MeshInstance3D = MeshGuard.new()
			geometry.name = "Geometry"
			geometry.mesh = mesh
			geometry.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if selected.cast_shadow else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			geometry.set("_private_bake", private_bake)
			node.add_child(geometry)
			if private_bake: geometry.owner = self
	return {"ok": true, "nodes": nodes}


static func build_mesh(geometry: Dictionary, metadata: Array[Dictionary], textures: Dictionary, facts: Variant,
		materials: Dictionary, overrides: Variant, operation: int) -> Dictionary:
	var mesh := ArrayMesh.new()
	for group: Dictionary in geometry.groups:
		var signature: Dictionary = material_signature(group.texture_indices)
		if not signature.ok: return signature
		var key: String = signature.value
		if not materials.has(key):
			if overrides != null and overrides.has(key):
				materials[key] = overrides[key]
			else:
				var layers: Array = []
				layers.resize(6)
				for layer: int in range(group.texture_indices.size()):
					var index: int = group.texture_indices[layer]
					if index == -1: continue
					if index < 0 or index >= metadata.size() or not textures.has(index):
						return failure("InvalidDataException", "The retained Aquila asset references unmapped texture " + str(index) + ".")
					layers[layer] = {"texture": textures[index], "opacity": metadata[index].opacity, "offset": metadata[index].offset, "scale": metadata[index].scale, "blend_texture_alpha": false}
				var created: Dictionary = Factory.create(layers, facts, 0.0, 0.5, operation)
				if not created.ok: return created
				materials[key] = created.value
		var arrays: Array = []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = geometry.vertices
		arrays[Mesh.ARRAY_NORMAL] = geometry.normals
		arrays[Mesh.ARRAY_TEX_UV] = geometry.uvs
		arrays[Mesh.ARRAY_COLOR] = geometry.colors
		arrays[Mesh.ARRAY_INDEX] = group.triangles
		var surface: int = mesh.get_surface_count()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		mesh.surface_set_name(surface, key)
		mesh.surface_set_material(surface, materials[key])
	return {"ok": true, "value": mesh}


static func material_signature(indices: Variant) -> Dictionary:
	if indices == null: return failure("NullReferenceException", "Object reference not set to an instance of an object.")
	if not indices is PackedInt32Array and not indices is Array: return failure("ArgumentException", "Material signature requires Int32 indices.")
	if indices.size() != 6: return failure("InvalidDataException", "The retained Aquila walker has an invalid material signature.")
	var words := PackedStringArray()
	for value: Variant in indices:
		if not value is int or value < -2147483648 or value > 2147483647: return failure("ArgumentException", "Material signature requires Int32 indices.")
		words.append("%08x" % (value & 0xffffffff))
	return {"ok": true, "value": "layers-" + "-".join(words)}


static func part_name(part: Dictionary) -> String:
	# CMSP names use .NET ASCII replacement, so this admitted character domain
	# is ASCII. char.IsLetterOrDigit therefore has no Unicode ambiguity here.
	var sanitized: String = ""
	var source_name: String = part.name
	for index: int in range(source_name.length()):
		var code: int = source_name.unicode_at(index)
		sanitized += String.chr(code) if (code >= 48 and code <= 57) or (code >= 65 and code <= 90) or (code >= 97 and code <= 122) or code == 45 or code == 95 else "-"
	return "Part%02d-%s" % [part.index, "Unnamed" if sanitized.is_empty() else sanitized]


static func failure(type: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": type, "error": message}
