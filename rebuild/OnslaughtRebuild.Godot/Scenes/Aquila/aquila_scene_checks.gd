# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Exact three-profile old/native comparison. All imported comparison meshes
## remain private, and no source/cache/corpus file is generated or rewritten.
const Aquila = preload("res://Client/aquila_mesh.gd")
const Model = preload("res://Scenes/Aquila/aquila_model.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const VALUES: Array[String] = ["has_dot3", "has_reflection", "has_overlay", "base_blend_texture_alpha", "alpha_reference", "stage_zero_gain", "dot3_offset", "dot3_scale", "reflection_factor_alpha", "overlay_offset", "overlay_scale", "overlay_opacity", "ambient_color", "sun_color", "anti_sun_color", "sunlight_direction", "fog_color", "fog_density", "maximum_horizontal_distance_squared"]
const TEXTURES: Array[String] = ["base_texture", "dot3_texture", "reflection_texture", "overlay_texture"]
var _counts: Dictionary = {}
var _failures: Array[Dictionary] = []
var _completed: Array[String] = []
var _report: String


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or not _owned(args[0]) or not _owned(args[1]) or args[0] == args[1] or FileAccess.file_exists(args[1]):
		quit(2)
		return
	_report = args[1]
	var input := FileAccess.open(args[0], FileAccess.READ)
	if input == null:
		quit(2)
		return
	var reference: Variant = input.get_var(false)
	input.close()
	if not reference is Dictionary or reference.get("schema") != 1 or reference.get("completed") != ["aquila_reference"]:
		quit(2)
		return
	var before: Dictionary = reference.hashes.duplicate()
	before[args[0]] = _hash_file(args[0])
	_check("read_only", "read original identities", _hashes(before), before)
	var pointer: int = Input.mouse_mode
	if Engine.is_editor_hint():
		await _editor(reference)
		_completed.assign(["resources", "editor"])
	else:
		_parser(reference)
		_completed.append("parser")
		_poses(reference)
		_completed.append("poses")
		_geometry(reference)
		_completed.append("geometry")
		_resources(reference)
		_completed.append("resources")
		_serialization(reference)
		_completed.append("serialization")
	_check("read_only", "original identities remain unchanged", _hashes(before), before)
	_check("read_only", "pointer unchanged", Input.mouse_mode, pointer)
	_completed.append("read_only")
	await process_frame
	if Engine.is_editor_hint():
		await create_timer(1.0).timeout
		while EditorInterface.get_resource_filesystem().is_scanning(): await process_frame
		await create_timer(0.25).timeout
	_finish()


func _parser(reference: Dictionary) -> void:
	_check("parser", "all three profiles", reference.profiles.size(), 3)
	for row: Dictionary in reference.profiles:
		var bytes: PackedByteArray = FileAccess.get_file_as_bytes(row.source_path)
		var admitted: Dictionary = Aquila.from_bytes(bytes, row.name)
		_check("parser", row.name + " exact source admission", admitted.ok, true)
		if not admitted.ok: continue
		_check("parser", row.name + " full decoded definition", _definition(admitted.value), row.definition)
		var decoded: Dictionary = Aquila.inflate_aya(bytes)
		_check("parser", row.name + " exact decompression", _hash(decoded.value), row.decoded_sha256)
		for mutation: Dictionary in row.mutations:
			var changed: PackedByteArray = decoded.value.slice(0, mutation.truncate) if mutation.truncate >= 0 else decoded.value.duplicate()
			if mutation.offset >= 0:
				if mutation.width == 1: changed[mutation.offset] = mutation.value
				else: changed.encode_s32(mutation.offset, mutation.value)
			var result: Dictionary = Aquila.parse_decoded_for_checks(changed, row.name)
			_check("parser", row.name + " " + mutation.name, {"ok": true} if result.ok else result, mutation.result)
		var detached: Dictionary = admitted.value.definition()
		detached.parts[0].frame_map[0] = 254
		_check("parser", row.name + " public state detached", _definition(admitted.value), row.definition)
		var corrupt: PackedByteArray = bytes.duplicate()
		corrupt[corrupt.size() - 1] ^= 1
		var message: String = "The retained Aquila " + row.name + " source does not match its reviewed specimen."
		_check("parser", row.name + " pin before inflate", Aquila.from_bytes(corrupt, row.name), {"ok": false, "error_type": "InvalidDataException", "error": message})
		_check("parser", row.name + " length before decoded admission", Aquila.from_bytes(PackedByteArray(), row.name), {"ok": false, "error_type": "InvalidDataException", "error": message})
		for admission: Dictionary in row.source_admission:
			_check("parser", row.name + " public source admission " + admission.name,
				Aquila.from_bytes(FileAccess.get_file_as_bytes(admission.source_path), row.name), admission.result)
	for row: Dictionary in reference.signatures:
		_check("parser", "UInt32 six-slot signature " + str(row.input), Model.material_signature(row.input), row.result)
	# The separate private_inflater_diagnostics retain a measured difference:
	# .NET's private ZLibStream helper accepts truncated/read-ahead suffixes.
	# Every such source is refused above by both actual production entrances
	# before inflation. No live consumer bypasses that source-pin boundary.


func _definition(asset: RefCounted) -> Dictionary:
	var parts: Array = []
	for part: Dictionary in asset.get("_parts"):
		var orientations := PackedFloat32Array()
		for matrix: PackedFloat32Array in part.orientations: orientations.append_array(matrix)
		parts.append({"index": part.index, "name": part.name, "virtual_count": part.virtual_count, "horizontal_count": part.horizontal_count,
			"parent": part.parent, "reference": part.reference, "children": part.children, "frame_map": part.frame_map,
			"base_transform": part.base_transform, "orientations": orientations, "positions": part.positions,
			"geometry_owner": -1 if part.geometry_owner == null else part.geometry_owner,
			"geometry": null if part.geometry == null else _geometry_facts(part.geometry)})
	return {"parts": parts, "textures": asset.get("_textures"), "part_count": parts.size(), "surface_count": asset.get("_surfaces"), "animated_count": asset.get("_profile").animated_count,
		"standing_clearance": _word(asset.get("_clearance")), "leg_lengths": asset.get("_leg_lengths")}


func _geometry_facts(geometry: Dictionary) -> Dictionary:
	return {"vertices": _hash(var_to_bytes(geometry.vertices)), "normals": _hash(var_to_bytes(geometry.normals)), "uvs": _hash(var_to_bytes(geometry.uvs)),
		"colors": _hash(var_to_bytes(geometry.colors)), "groups": geometry.groups}


func _poses(reference: Dictionary) -> void:
	for row: Dictionary in reference.profiles:
		var admitted: Dictionary = Aquila.from_bytes(FileAccess.get_file_as_bytes(row.source_path), row.name)
		if not admitted.ok:
			_check("poses", row.name + " admission", admitted.ok, true)
			continue
		for frame: Dictionary in row.frames:
			var words := PackedFloat32Array()
			for transform: PackedFloat32Array in admitted.value.global_transforms(_single(frame.word)): words.append_array(transform)
			_check("poses", row.name + " frame result " + str(frame.word), true, frame.result.ok)
			if frame.result.ok: _check("poses", row.name + " every global transform word " + str(frame.word), words.to_byte_array(), frame.transforms.to_byte_array())
		var created: Dictionary = _create(row, reference.facts)
		_check("poses", row.name + " model created", created.ok, true)
		if not created.ok: continue
		var model: Node3D = created.value
		root.add_child(model)
		_check("poses", row.name + " original initial pose", _transforms(model), row.initial.transforms)
		for index: int in range(row.operations.size()):
			var step: Dictionary = row.operations[index]
			var result: Dictionary
			if step.kind == "root":
				model.transform = step.value
				result = {"ok": true}
			else: result = model.set_virtual_frame(_single(step.word)) if step.kind == "frame" else model.set_ground_contact_pose(step.value)
			_check("poses", row.name + " result/order " + str(index), result, step.result)
			_check("poses", row.name + " exact mutated nodes " + str(index), _transforms(model), step.state)
		model.free()


func _create(row: Dictionary, facts: Dictionary, private_bake: bool = false) -> Dictionary:
	var scene: PackedScene = load("res://Scenes/Aquila/" + row.name.capitalize() + ".tscn")
	var model: Node3D = scene.instantiate()
	var textures: Dictionary = model.texture_bindings()
	for texture: Texture2D in textures.values():
		if texture != null and texture.has_method("ensure_loaded"):
			var loaded: Dictionary = texture.ensure_loaded()
			if not loaded.ok:
				model.free()
				return loaded
	var overrides: Variant = model.default_material_overrides()
	var result: Dictionary = model.configure_bytes(FileAccess.get_file_as_bytes(row.source_path), row.name, textures, facts, overrides, false, private_bake)
	if not result.ok:
		model.free()
		return result
	return {"ok": true, "value": model}


func _geometry(reference: Dictionary) -> void:
	for row: Dictionary in reference.profiles:
		var created: Dictionary = _create(row, reference.facts)
		_check("geometry", row.name + " model created", created.ok, true)
		if not created.ok: continue
		var model: Node3D = created.value
		root.add_child(model)
		_check("geometry", row.name + " exact mesh/material/transform definitions", _scene_facts(model), row.initial)
		var identities: Dictionary = _resource_ids(model)
		var rebound: Dictionary = model.configure_bytes(FileAccess.get_file_as_bytes(row.source_path), row.name, {}, null, null, true)
		_check("geometry", row.name + " saved binding never requires new textures/fog", rebound.ok, true)
		_check("geometry", row.name + " binding retains mesh and material objects", _resource_ids(model), identities)
		_check("geometry", row.name + " binding retains exact initial scene", _scene_facts(model), row.initial)
		var bytes: PackedByteArray = FileAccess.get_file_as_bytes(row.source_path)
		bytes[bytes.size() - 1] ^= 1
		_check("geometry", row.name + " corrupt source refuses before bind", model.configure_bytes(bytes, row.name, {}, null, null, true).ok, false)
		_check("geometry", row.name + " refused bind leaves exact state", _scene_facts(model), row.initial)
		_check("geometry", row.name + " prepared bind retries without textures", model.configure_prepared(null, true).ok, true)
		_check("geometry", row.name + " prepared bind retains resources", _resource_ids(model), identities)
		var nodes: Array = model.get("_nodes")
		for part: Dictionary in model.get("_parts"):
			if part.geometry == null: continue
			var geometry: MeshInstance3D = nodes[part.index].get_node("Geometry")
			var mesh: Mesh = geometry.mesh
			geometry.mesh = null
			var before: Dictionary = _transforms(model)
			_check("geometry", row.name + " saved missing mesh refusal", model.configure_prepared(null, true),
				{"ok": false, "error_type": "InvalidDataException", "error": "Scene lost " + Aquila.PROFILES[row.name].display_name + " geometry at part " + str(part.index) + "."})
			_check("geometry", row.name + " missing mesh bind does not reset pose", _transforms(model), before)
			geometry.mesh = mesh
			_check("geometry", row.name + " restored saved mesh can rebind", model.configure_prepared(null, true).ok, true)
			_check("geometry", row.name + " retry never replaces resources", _resource_ids(model), identities)
			break
		model.free()
		var scene: PackedScene = load("res://Scenes/Aquila/" + row.name.capitalize() + ".tscn")
		var prepared: Node3D = scene.instantiate()
		_check("geometry", row.name + " production read-only prepared entry", prepared.configure_prepared(reference.facts, false).ok, true)
		_check("geometry", row.name + " prepared entry exactly equals old factory", _scene_facts(prepared), row.initial)
		var counts: Dictionary = prepared.counts()
		_check("geometry", row.name + " coarse counts batch", counts,
			{"part_count": row.definition.part_count, "surface_count": row.definition.surface_count,
				"animated_count": row.definition.animated_count, "standing_clearance": _single(row.definition.standing_clearance)})
		prepared.free()


func _resources(reference: Dictionary) -> void:
	for row: Dictionary in reference.profiles:
		var created: Dictionary = _create(row, reference.facts)
		_check("resources", row.name + " public preview uses production components", created.ok, true)
		if not created.ok: continue
		var model: Node3D = created.value
		var path: String = _fresh(row.name + "-public.tscn")
		if path.is_empty(): model.free(); continue
		var packed := PackedScene.new()
		_check("resources", row.name + " pack public source", packed.pack(model), OK)
		_check("resources", row.name + " no generated owned children", packed.get_state().get_node_count(), 1)
		_check("resources", row.name + " public save", ResourceSaver.save(packed, path), OK)
		var text: String = FileAccess.get_file_as_string(path)
		for marker: String in ["PackedByteArray(", "type=\"ImageTexture\"", "type=\"ArrayMesh\"", "Part00-"]:
			_check("resources", row.name + " no derived public payload " + marker, text.contains(marker), false)
		for texture: Texture2D in model.texture_bindings().values():
			_check("resources", row.name + " recipe remains inspectable", texture.has_method("ensure_loaded"), true)
		_check("resources", row.name + " controller has no process owner", model.is_processing() or model.is_physics_processing() or model.is_processing_input(), false)
		model.free()


func _serialization(reference: Dictionary) -> void:
	for row: Dictionary in reference.profiles:
		var created: Dictionary = _create(row, reference.facts, true)
		_check("serialization", row.name + " private creation", created.ok, true)
		if not created.ok: continue
		var model: Node3D = created.value
		root.add_child(model)
		var legacy_packed: PackedScene = ResourceLoader.load(row.scene_path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
		var legacy: Node3D = legacy_packed.instantiate()
		var expected_saved: Dictionary = _scene_facts(legacy)
		_check("serialization", row.name + " old reload keeps shader Singles", _shader_single_facts(expected_saved), _shader_single_facts(row.initial))
		# Text saves lose signed-zero Transform3D signs. Exact fresh words were
		# compared above; the private contract below compares both actual reloads.
		for path: String in expected_saved.transforms:
			_check("serialization", row.name + " old text transform values " + path,
				bytes_to_var(expected_saved.transforms[path]), bytes_to_var(row.initial.transforms[path]))
		legacy.free()
		for round: int in range(2):
			var path: String = _fresh(row.name + "-private-" + str(round) + ".tscn")
			if path.is_empty(): break
			var packed := PackedScene.new()
			_check("serialization", row.name + " pack " + str(round), packed.pack(model), OK)
			_check("serialization", row.name + " save " + str(round), ResourceSaver.save(packed, path), OK)
			model.free()
			packed = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
			model = packed.instantiate()
			root.add_child(model)
			_check("serialization", row.name + " exact old/new reloaded scene " + str(round), _scene_facts(model), expected_saved)
			var ids: Dictionary = _resource_ids(model)
			_check("serialization", row.name + " bind loaded scene " + str(round), model.configure_bytes(FileAccess.get_file_as_bytes(row.source_path), row.name, {}, null, null, true).ok, true)
			_check("serialization", row.name + " loaded resources retained " + str(round), _resource_ids(model), ids)
		model.free()


func _editor(reference: Dictionary) -> void:
	for row: Dictionary in reference.profiles:
		var scene: PackedScene = load("res://Scenes/Aquila/" + row.name.capitalize() + ".tscn")
		var model: Node3D = scene.instantiate()
		root.add_child(model)
		await process_frame
		_check("editor", row.name + " same production preview", _scene_facts(model), row.initial)
		_check("editor", row.name + " no animation/parser retained", model.get("_asset"), null)
		_check("editor", row.name + " no processing/input", model.is_processing() or model.is_physics_processing() or model.is_processing_input(), false)
		_check("editor", row.name + " virtual frames cannot start playback", model.set_virtual_frame(2.0).ok, false)
		var packed := PackedScene.new()
		_check("resources", row.name + " public pack", packed.pack(model), OK)
		_check("resources", row.name + " preview-derived nodes omitted", packed.get_state().get_node_count(), 1)
		var path: String = _fresh(row.name + "-editor-public.tscn")
		if not path.is_empty():
			_check("resources", row.name + " public editor save", ResourceSaver.save(packed, path), OK)
			var text: String = FileAccess.get_file_as_string(path)
			_check("resources", row.name + " no preview geometry payload", text.contains("PackedByteArray(") or text.contains("type=\"ArrayMesh\"") or text.contains("type=\"ImageTexture\""), false)
		model.free()
		var saved: PackedScene = ResourceLoader.load(row.scene_path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
		var retained: Node3D = saved.instantiate()
		var before: Dictionary = _scene_facts(retained)
		root.add_child(retained)
		await process_frame
		_check("editor", row.name + " saved hierarchy left intact before Play", _scene_facts(retained), before)
		retained.free()


func _transforms(model: Node3D) -> Dictionary:
	var result: Dictionary = {".": var_to_bytes(model.transform)}
	_add_transforms(model, model, result)
	return result


func _add_transforms(parent: Node, model: Node3D, result: Dictionary) -> void:
	for child: Node in parent.get_children():
		if child is Node3D: result[str(model.get_path_to(child))] = var_to_bytes(child.transform)
		_add_transforms(child, model, result)


func _scene_facts(model: Node3D) -> Dictionary:
	var meshes: Dictionary = {}
	_add_mesh_facts(model, model, meshes, {}, {})
	return {"root_name": str(model.name), "transforms": _transforms(model), "meshes": meshes}


func _add_mesh_facts(parent: Node, model: Node3D, result: Dictionary, meshes: Dictionary, materials: Dictionary) -> void:
	for child: Node in parent.get_children():
		if child is MeshInstance3D:
			var mesh: ArrayMesh = child.mesh
			if not meshes.has(mesh.get_instance_id()): meshes[mesh.get_instance_id()] = meshes.size()
			var surfaces: Array[Dictionary] = []
			for index: int in range(mesh.get_surface_count()):
				var material: Material = mesh.surface_get_material(index)
				if not materials.has(material.get_instance_id()): materials[material.get_instance_id()] = materials.size()
				surfaces.append({"name": mesh.surface_get_name(index), "primitive": mesh.surface_get_primitive_type(index), "format": mesh.surface_get_format(index), "arrays": _hash(var_to_bytes(mesh.surface_get_arrays(index))),
					"material_alias": materials[material.get_instance_id()], "material": _material_facts(material)})
			result[str(model.get_path_to(child))] = {"alias": meshes[mesh.get_instance_id()], "shadow": child.cast_shadow, "surfaces": surfaces}
		_add_mesh_facts(child, model, result, meshes, materials)


func _material_facts(material: Material) -> Dictionary:
	var result: Dictionary = {"class": material.get_class()}
	if material is ShaderMaterial:
		var values: Dictionary = {}
		for name: String in VALUES: values[name] = var_to_bytes(material.get_shader_parameter(name))
		var textures: Dictionary = {}
		for name: String in TEXTURES:
			var texture: Texture2D = material.get_shader_parameter(name)
			if texture != null: textures[name] = _hash(texture.get_image().get_data())
		result.values = values
		result.textures = textures
	else:
		result.shading = material.shading_mode
		result.cull = material.cull_mode
		result.transparency = material.transparency
		result.blend = material.blend_mode
		result.emission_enabled = material.emission_enabled
		result.emission = var_to_bytes(material.emission)
		result.energy = _word(material.emission_energy_multiplier)
		result.albedo = null if material.albedo_texture == null else _hash(material.albedo_texture.get_image().get_data())
		result.emission_texture = null if material.emission_texture == null else _hash(material.emission_texture.get_image().get_data())
		result.same_texture = material.albedo_texture == material.emission_texture
	return result


func _resource_ids(model: Node3D) -> Dictionary:
	var result: Dictionary = {}
	_add_ids(model, model, result)
	return result


func _add_ids(parent: Node, model: Node3D, result: Dictionary) -> void:
	for child: Node in parent.get_children():
		if child is MeshInstance3D:
			var ids: Array[int] = [child.mesh.get_instance_id()]
			for index: int in range(child.mesh.get_surface_count()): ids.append(child.mesh.surface_get_material(index).get_instance_id())
			result[str(model.get_path_to(child))] = ids
		_add_ids(child, model, result)


func _shader_single_facts(facts: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	for path: String in facts.meshes:
		var surfaces: Array = []
		for surface: Dictionary in facts.meshes[path].surfaces:
			if surface.material.get("class") != "ShaderMaterial": continue
			var values: Dictionary = surface.material.values.duplicate()
			for name: String in values:
				var value: Variant = bytes_to_var(values[name])
				if typeof(value) == TYPE_FLOAT: values[name] = var_to_bytes(F.value(value))
			surfaces.append(values)
		result[path] = surfaces
	return result


func _single(word: int) -> float:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_u32(0, word)
	return bytes.decode_float(0)


func _word(value: float) -> int:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	return bytes.decode_u32(0)


func _hash_file(path: String) -> String:
	return _hash(FileAccess.get_file_as_bytes(path))


func _hashes(paths: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	for path: String in paths: result[path] = _hash_file(path)
	return result


func _hash(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	if not bytes.is_empty(): hash.update(bytes)
	return hash.finish().hex_encode()


func _owned(path: String) -> bool:
	var base: String = ProjectSettings.globalize_path("res://").path_join("../../local-data").simplify_path() + "/"
	return path.is_absolute_path() and path.simplify_path().begins_with(base) and DirAccess.dir_exists_absolute(path.get_base_dir())


func _fresh(name: String) -> String:
	var path: String = _report.get_base_dir().path_join(name)
	_check("read_only", "fresh output " + name, FileAccess.file_exists(path), false)
	return "" if FileAccess.file_exists(path) else path


func _check(group: String, label: String, actual: Variant, expected: Variant) -> void:
	_counts[group] = _counts.get(group, 0) + 1
	if actual != expected:
		_failures.append({"group": group, "label": label, "difference": _difference(actual, expected)})
		printerr(group + ": " + label + " " + str(_failures.back().difference))


func _difference(actual: Variant, expected: Variant, path: String = "") -> Dictionary:
	if actual is Dictionary and expected is Dictionary:
		for key: Variant in expected:
			if not actual.has(key): return {"path": path + "/" + str(key), "actual": "missing"}
			if actual[key] != expected[key]: return _difference(actual[key], expected[key], path + "/" + str(key))
	elif (actual is Array and expected is Array) or (actual is PackedByteArray and expected is PackedByteArray) or (actual is PackedFloat32Array and expected is PackedFloat32Array):
		if actual.size() != expected.size(): return {"path": path, "actual_size": actual.size(), "expected_size": expected.size()}
		for index: int in range(actual.size()):
			if actual[index] != expected[index]: return _difference(actual[index], expected[index], path + "/" + str(index))
	return {"path": path, "actual": str(actual).left(200), "expected": str(expected).left(200)}


func _finish() -> void:
	var file := FileAccess.open(_report, FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify({"schema": 1, "failure_count": _failures.size(), "counts": _counts, "completed": _completed, "failures": _failures}))
	file.close()
	print("AQUILA_CHECKS: " + JSON.stringify({"counts": _counts, "failure_count": _failures.size(), "completed": _completed}))
	quit(0 if _failures.is_empty() else 1)
