# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Standard-engine production checks against the unchanged .NET reference.
## Args: existing owned reference.variant, fresh owned report.json, optional
## --capture on a task-owned isolated display. No desktop/input/audio ownership.
const Scene = preload("res://Scenes/World/Water.tscn")
const Water = preload("res://Scenes/World/water.gd")
const Recipe = preload("res://Scenes/World/water_recipe.gd")
const Words = preload("res://Core/retail_float24.gd")
var _counts: Dictionary = {}
var _failures: Array[Dictionary] = []
var _completed: Array[String] = []
var _report: String


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() not in [2, 3] or not _owned(args[0]) or not _owned(args[1]) or FileAccess.file_exists(args[1]) or args[0] == args[1]:
		quit(2)
		return
	_report = args[1]
	var input := FileAccess.open(args[0], FileAccess.READ)
	if input == null:
		quit(2)
		return
	var reference: Variant = input.get_var(false)
	input.close()
	if not reference is Dictionary or reference.get("schema") != 1 or reference.get("completed") != ["water_reference"]:
		quit(2)
		return
	for file: String in ["public-water.tscn", "public-water-repeat.tscn", "private-water.tscn", "private-water-repeat.tscn"]:
		if FileAccess.file_exists(_report.get_base_dir().path_join(file)):
			quit(2)
			return
	var pointer: int = Input.mouse_mode
	for row: Dictionary in reference.admission:
		reference.input_hashes[row.path] = row.sha256
	var before: Dictionary = _input_hashes(reference.input_hashes)
	_check("read_only", "reference input identities", before, reference.input_hashes)
	var water: Water = Scene.instantiate()
	root.add_child(water)
	if _scene(water, reference):
		_completed.append("scene")
		if Engine.is_editor_hint():
			_check("editor", "configure refuses before input admission", water.configure(PackedByteArray(), false).ok, false)
			_check("editor", "update refuses", water.update_camera(Vector3.ONE, 1.0).ok, false)
			_check("editor", "no live state", water.state().configured, false)
			for node: Node in [water] + water.get_children():
				_check("editor", str(node.name) + " no process", node.is_processing(), false)
				_check("editor", str(node.name) + " no physics", node.is_physics_processing(), false)
				_check("editor", str(node.name) + " no input", node.is_processing_input() or node.is_processing_unhandled_input() or node.is_processing_unhandled_key_input(), false)
			_completed.append("editor")
		elif _runtime(water, reference):
			_completed.append("runtime")
		if _public_roundtrip(reference):
			_completed.append("public_roundtrip")
		if _private_roundtrip(reference):
			_completed.append("private_roundtrip")
		if args.size() == 3:
			_check("capture", "explicit capture mode", args[2], "--capture")
			if args[2] == "--capture":
				await _capture(reference)
	water.free()
	_check("read_only", "source bytes unchanged", _input_hashes(before), before)
	_check("read_only", "pointer unchanged", Input.mouse_mode, pointer)
	_completed.append("read_only")
	await process_frame
	if Engine.is_editor_hint():
		await create_timer(1.0).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame
		await create_timer(0.25).timeout
	_finish()


func _scene(water: Water, reference: Dictionary) -> bool:
	_check("scene", "native script", water.get_script(), Water)
	_check("scene", "root name", str(water.name), "RetailLevel100Water")
	_check("scene", "three authored components", water.get_child_count(), 3)
	_check("scene", "same reported counts", water.counts(), reference.counts)
	_check("scene", "not configured", water.state().configured, false)
	var visual: Dictionary = water.prepare_visual(false)
	_check("scene", "actual production input admitted", visual.ok, true)
	if not visual.ok:
		return false
	_visual(water, reference, "scene")
	for key: String in reference.textures:
		var page: Texture2D = _texture(water, key)
		_check("texture", key + " recipe", page != null and page.has_method("ensure_loaded"), true)
		if page != null:
			_check("texture", key + " same decoded image", _image_facts(page.get_image()), reference.textures[key])
	for row: Dictionary in reference.admission:
		var result: Dictionary = Recipe.shoreline_from_bytes(FileAccess.get_file_as_bytes(row.path))
		_check("admission", "synthetic size " + str(row.length), result, {"ok": false, "error_type": row.error_type, "error": row.error})
	var source: PackedByteArray = FileAccess.get_file_as_bytes(Recipe.SURFACE_PATH)
	var damaged: PackedByteArray = source.duplicate()
	damaged[64] ^= 1
	_check("admission", "one changed byte refuses", Recipe.shoreline_from_bytes(damaged).ok, false)
	_check("admission", "caller cannot replace hash pin", Recipe.shoreline_from_bytes(source, "0".repeat(64)).ok, false)
	_check("admission", "case-insensitive exact hash", Recipe.shoreline_from_bytes(source, Recipe.SURFACE_SHA256.to_upper()).ok, true)
	return true


func _runtime(water: Water, reference: Dictionary) -> bool:
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(reference.terrain_path)
	_check("runtime", "unconfigured update refuses", water.update_camera(Vector3.ONE, 1.0).ok, false)
	_check("runtime", "empty terrain refuses", water.configure(PackedByteArray(), false).ok, false)
	_check("runtime", "failed configure stays idle", water.state().configured, false)
	var before_mesh: Mesh = water.get_child(0).mesh
	_check("runtime", "missing surface route refuses", water.configure(bytes, false, {}, "res://Assets/Level100/MissingSurface.bin").ok, false)
	_check("runtime", "failed preparation retains prior preview mesh", water.get_child(0).mesh, before_mesh)
	_check("runtime", "failed preparation does not start gameplay", water.state().configured, false)
	var configured: Dictionary = water.configure(bytes, false)
	_check("runtime", "valid retry configures", configured.ok, true)
	if not configured.ok:
		return false
	_check("runtime", "initial raw state", _snapshot(water), reference.initial)
	_check("runtime", "bounded ordered operation count", reference.steps.size(), 1173)
	for index: int in range(reference.steps.size()):
		var step: Dictionary = reference.steps[index]
		var result: Dictionary
		if step.kind == "bind":
			var saved_mesh: Mesh = water.get_child(1).mesh
			var saved_material: Material = water.get_child(1).material_override
			result = water.configure(bytes, true)
			_check("binding", str(index) + " retains mesh", water.get_child(1).mesh, saved_mesh)
			_check("binding", str(index) + " retains material", water.get_child(1).material_override, saved_material)
		else:
			result = water.update_camera(_vector(step.camera), Words.read_word(step.delta_bits))
		_check("runtime", str(index) + " admission", result.ok, true)
		_check("numeric", str(index) + " exact ordered state", _snapshot(water), step.expected)
	var copied: Dictionary = water.state()
	copied.metadata.fog_density_bits = 0
	_check("detachment", "metadata detached", water.state().metadata.fog_density_bits == 0, false)
	return true


func _visual(water: Node3D, reference: Dictionary, group: String) -> void:
	for name: String in Water.CHILD_NAMES:
		var node: MeshInstance3D = water.get_node(NodePath(name))
		var expected: Dictionary = reference.visual[name]
		_check(group, name + " actual mesh", node.mesh is ArrayMesh, true)
		_check(group, name + " actual material", node.material_override is ShaderMaterial, true)
		if node.mesh == null or not node.material_override is ShaderMaterial:
			continue
		_check(group, name + " surface count", node.mesh.get_surface_count(), expected.surfaces.size())
		for index: int in range(mini(node.mesh.get_surface_count(), expected.surfaces.size())):
			var arrays: Array = node.mesh.surface_get_arrays(index)
			_check(group, name + " all mesh bytes " + str(index), _hash(var_to_bytes(arrays)), expected.surfaces[index].sha256)
			_check(group, name + " primitive " + str(index), node.mesh.surface_get_primitive_type(index), expected.surfaces[index].primitive)
			_check(group, name + " format " + str(index), node.mesh.surface_get_format(index), expected.surfaces[index].format)
		var material: ShaderMaterial = node.material_override
		_check(group, name + " original shader body", material.shader.code.trim_prefix("// SPDX-License-Identifier: GPL-3.0-or-later\n").strip_edges(), expected.shader.strip_edges())
		_check(group, name + " priority", material.render_priority, expected.priority)
		_check(group, name + " shadows", node.cast_shadow, expected.cast_shadow)
		_check(group, name + " parameters", _parameters(material), expected.parameters)


func _public_roundtrip(reference: Dictionary) -> bool:
	var water: Water = Scene.instantiate()
	root.add_child(water)
	_check("public", "preview admission", water.prepare_visual(false).ok, true)
	for round: int in range(2):
		var scene := PackedScene.new()
		_check("public", "pack " + str(round), scene.pack(water), OK)
		var state: SceneState = scene.get_state()
		for index: int in range(state.get_node_count()):
			for property: int in range(state.get_node_property_count(index)):
				_check("public", "no derived property " + str(state.get_node_path(index)) + ":" + str(property), str(state.get_node_property_name(index, property)) in ["mesh", "material_override", "_private_bake"], false)
		var path: String = _report.get_base_dir().path_join("public-water.tscn" if round == 0 else "public-water-repeat.tscn")
		_check("public", "save " + str(round), ResourceSaver.save(scene, path), OK)
		var text: String = FileAccess.get_file_as_string(path)
		for marker: String in ["PackedByteArray(", "type=\"ImageTexture\"", "type=\"Image\"", "type=\"ArrayMesh\""]:
			_check("public", "no payload " + str(round) + marker, text.contains(marker), false)
		water.free()
		water = _reload(path)
		if water == null:
			return false
		root.add_child(water)
		_check("public", "reload production recipe " + str(round), water.prepare_visual(false).ok, true)
		_visual(water, reference, "public")
	water.free()
	return true


func _private_roundtrip(reference: Dictionary) -> bool:
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(reference.terrain_path)
	var water: Water = Scene.instantiate()
	root.add_child(water)
	# Editor cannot enable a live bake. Check its saved-resource behavior by
	# explicitly simulating the importer's derived resource storage only.
	if Engine.is_editor_hint():
		_check("private", "editor prepare", water.prepare_visual(false).ok, true)
		for child: Node in water.get_children():
			child.enable_private_bake()
	else:
		_check("private", "configure bake", water.configure(bytes, false).ok, true)
	for round: int in range(2):
		if round == 0:
			# Match the real importer's external resource/local material rules,
			# using only this check's fresh owned output directory.
			for index: int in range(water.get_child_count()):
				var child: MeshInstance3D = water.get_child(index)
				child.material_override.resource_local_to_scene = true
				for kind: String in ["mesh", "material_override"]:
					var path: String = _report.get_base_dir().path_join("water-" + str(index) + "-" + kind + ".res")
					_check("private", "fresh external resource", FileAccess.file_exists(path), false)
					var resource: Resource = child.get(kind)
					_check("private", "external resource save", ResourceSaver.save(resource, path, ResourceSaver.FLAG_CHANGE_PATH), OK)
		var scene := PackedScene.new()
		_check("private", "pack " + str(round), scene.pack(water), OK)
		var path: String = _report.get_base_dir().path_join("private-water.tscn" if round == 0 else "private-water-repeat.tscn")
		_check("private", "save " + str(round), ResourceSaver.save(scene, path), OK)
		water.free()
		water = _reload(path)
		if water == null:
			return false
		root.add_child(water)
		var mesh: Mesh = water.get_child(1).mesh
		var material: Material = water.get_child(1).material_override
		_check("private", "derived mesh survived " + str(round), mesh != null, true)
		_check("private", "derived material survived " + str(round), material != null, true)
		if Engine.is_editor_hint():
			_check("private", "editor remains idle", water.state().configured, false)
		else:
			_check("private", "saved resources bind " + str(round), water.configure(bytes, true).ok, true)
		_check("private", "no duplicate mesh on bind " + str(round), water.get_child(1).mesh, mesh)
		_check("private", "no duplicate material on bind " + str(round), water.get_child(1).material_override, material)
		_visual(water, reference, "private")
	water.free()
	return _nested_roundtrip(reference)


func _snapshot(water: Water) -> Dictionary:
	var data: Dictionary = water.state()
	var children: Dictionary = {}
	for name: String in Water.CHILD_NAMES:
		var node: MeshInstance3D = water.get_node(NodePath(name))
		var phases: Dictionary = {}
		for uniform: Dictionary in node.material_override.shader.get_shader_uniform_list():
			var key: String = uniform.name
			if key in ["caustic_phase", "main_wave_scroll", "glint_phase"]:
				phases[key] = Words.store_word(node.material_override.get_shader_parameter(key))
		children[name] = {"position": _vector_words(node.position), "rotation": _vector_words(node.rotation), "scale": _vector_words(node.scale), "phases": phases}
	return {"caustic_phase": Words.store_word(data.caustic_phase), "main_wave_scroll": Words.store_word(data.main_wave_scroll), "water_height": Words.store_word(data.water_height), "direction": _vector_words(data.direction), "children": children}


func _nested_roundtrip(reference: Dictionary) -> bool:
	# The world importer saves StaticWorld around the Water instance, then
	# embeds that component in Level100. Saving Water as the root alone does
	# not exercise Godot's nested-instance child override storage.
	var native: Water = Scene.instantiate()
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(reference.terrain_path)
	if Engine.is_editor_hint():
		_check("nested", "editor visual admission", native.prepare_visual(false).ok, true)
		for child: Node in native.get_children(): child.enable_private_bake()
	else:
		_check("nested", "runtime bake admission", native.configure(bytes, false).ok, true)
	# Nondefault transforms must survive before any runtime configure/update
	# can repair them. Use the exact old-reference pose for all three children.
	var sample: Dictionary = reference.steps[132]
	for name: String in Water.CHILD_NAMES:
		var child: Node3D = native.get_node(NodePath(name))
		var pose: Dictionary = sample.expected.children[name]
		child.position = _vector(pose.position)
		child.rotation = _vector(pose.rotation)
		child.scale = _vector(pose.scale)
	var expected: Dictionary = _child_transforms(native)
	var container := Node3D.new()
	container.name = "StaticWorld"
	container.add_child(native)
	native.owner = container
	_check("nested", "private child overrides explicitly editable", container.is_editable_instance(native), true)
	var packed := PackedScene.new()
	_check("nested", "pack enclosing static component", packed.pack(container), OK)
	var path: String = _report.get_base_dir().path_join("nested-static-water.tscn")
	_check("nested", "fresh enclosing component", FileAccess.file_exists(path), false)
	_check("nested", "save enclosing component", ResourceSaver.save(packed, path), OK)
	container.free()
	var saved: PackedScene = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	_check("nested", "reload enclosing component", saved != null, true)
	if saved == null: return false
	container = saved.instantiate()
	var water: Node3D = container.get_node("RetailLevel100Water")
	_check("nested", "frozen transforms before entering tree or binding", _child_transforms(water), expected)
	_visual(water, reference, "nested")
	var world := Node3D.new()
	world.name = "Level100"
	world.add_child(container)
	container.owner = world
	var second := PackedScene.new()
	_check("nested", "pack outer world", second.pack(world), OK)
	path = _report.get_base_dir().path_join("nested-world-water.tscn")
	_check("nested", "fresh outer world", FileAccess.file_exists(path), false)
	_check("nested", "save outer world", ResourceSaver.save(second, path), OK)
	world.free()
	saved = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	_check("nested", "reload outer world", saved != null, true)
	if saved == null: return false
	world = saved.instantiate()
	water = world.get_node("StaticWorld/RetailLevel100Water")
	_check("nested", "outer frozen transforms before binding", _child_transforms(water), expected)
	_visual(water, reference, "nested")
	world.free()
	return true


func _child_transforms(water: Node3D) -> Dictionary:
	var result: Dictionary = {}
	for name: String in Water.CHILD_NAMES:
		var node: Node3D = water.get_node(NodePath(name))
		# Godot stores Transform3D, then derives Euler angles/scale on load.
		# Compare every raw stored matrix word, not a second decomposition
		# (which changes signed-zero Euler words and can round scale by 1 ULP).
		var transform: Transform3D = node.transform
		result[name] = {"origin": _vector_words(transform.origin), "x": _vector_words(transform.basis.x), "y": _vector_words(transform.basis.y), "z": _vector_words(transform.basis.z)}
	return result


func _parameters(material: ShaderMaterial) -> Dictionary:
	var result: Dictionary = {}
	for uniform: Dictionary in material.shader.get_shader_uniform_list():
		var key: String = uniform.name
		var value: Variant = material.get_shader_parameter(key)
		if value is float:
			value = {"float_bits": Words.store_word(value)}
		elif value is Vector2:
			value = {"vector_bits": PackedInt64Array([Words.store_word(value.x), Words.store_word(value.y)])}
		elif value is Vector3:
			value = {"vector_bits": _vector_words(value)}
		elif value is Texture2D:
			value = "Texture2D"
		result[key] = value
	return result


func _texture(water: Node3D, uniform: String) -> Texture2D:
	for name: String in Water.CHILD_NAMES:
		var material: ShaderMaterial = water.get_node(NodePath(name)).material_override
		for spec: Dictionary in material.shader.get_shader_uniform_list():
			if str(spec.name) == uniform:
				return material.get_shader_parameter(uniform)
	return null


func _capture(reference: Dictionary) -> void:
	_check("capture", "isolated rendered display required", DisplayServer.get_name() != "headless", true)
	if DisplayServer.get_name() == "headless":
		return
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(reference.terrain_path)
	var native: Water = Scene.instantiate()
	_check("capture", "native configure", native.configure(bytes, false).ok, true)
	var sample: Dictionary = reference.steps[132]
	for index: int in range(133):
		var step: Dictionary = reference.steps[index]
		native.update_camera(_vector(step.camera), Words.read_word(step.delta_bits))
	var legacy := Node3D.new()
	for name: String in Water.CHILD_NAMES:
		var expected: Dictionary = reference.visual[name]
		var node := MeshInstance3D.new()
		node.name = name
		var mesh := ArrayMesh.new()
		for surface: Dictionary in expected.surfaces:
			mesh.add_surface_from_arrays(surface.primitive, surface.arrays)
		node.mesh = mesh
		var shader := Shader.new()
		shader.code = expected.shader
		var material := ShaderMaterial.new()
		material.shader = shader
		material.render_priority = expected.priority
		for key: String in expected.parameters:
			var value: Variant = expected.parameters[key]
			if value is String and value == "Texture2D": value = _texture(native, key)
			elif value is Dictionary and value.has("float_bits"): value = Words.read_word(value.float_bits)
			elif value is Dictionary and value.has("vector_bits"):
				value = _vector(value.vector_bits) if value.vector_bits.size() == 3 else Vector2(Words.read_word(value.vector_bits[0]), Words.read_word(value.vector_bits[1]))
			material.set_shader_parameter(key, value)
		var state: Dictionary = sample.expected.children[name]
		for key: String in state.phases: material.set_shader_parameter(key, Words.read_word(state.phases[key]))
		node.material_override = material
		node.cast_shadow = expected.cast_shadow
		node.position = _vector(state.position)
		node.rotation = _vector(state.rotation)
		node.scale = _vector(state.scale)
		legacy.add_child(node)
	var views: Array[SubViewport] = []
	for model: Node3D in [native, legacy]:
		var viewport := SubViewport.new()
		viewport.size = Vector2i(640, 360)
		viewport.own_world_3d = true
		viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		root.add_child(viewport)
		viewport.add_child(model)
		var camera := Camera3D.new()
		camera.position = _vector(sample.camera)
		camera.far = 1500.0
		camera.fov = 70.0
		viewport.add_child(camera)
		camera.look_at(Vector3(0.0, -1.16, 0.0))
		camera.current = true
		views.append(viewport)
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var images: Array[Image] = [views[0].get_texture().get_image(), views[1].get_texture().get_image()]
	_check("capture", "same complete RGBA bytes", _hash(images[0].get_data()), _hash(images[1].get_data()))
	var colors: Dictionary = {}
	var pixels: PackedByteArray = images[0].get_data()
	for offset: int in range(0, pixels.size(), 4):
		colors[pixels.decode_u32(offset)] = true
	_check("capture", "water produces visible varied pixels", colors.size() > 64, true)
	_check("capture", "native save", images[0].save_png(_report.get_base_dir().path_join("water-native.png")), OK)
	_check("capture", "reference save", images[1].save_png(_report.get_base_dir().path_join("water-reference.png")), OK)
	for view: SubViewport in views: view.free()
	_completed.append("capture")


func _reload(path: String) -> Water:
	var packed: PackedScene = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	_check("roundtrip", "load " + path.get_file(), packed != null, true)
	return packed.instantiate() if packed != null else null


func _image_facts(image: Image) -> Dictionary:
	return {"size": image.get_size(), "format": image.get_format(), "mipmaps": image.has_mipmaps(), "sha256": _hash(image.get_data())}


func _input_hashes(inputs: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	for path: String in inputs:
		result[path] = FileAccess.get_sha256(path)
	return result


func _owned(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or path.contains("\\") or not path.begins_with(owned + "/"):
		return false
	var directory := DirAccess.open(owned)
	if directory == null:
		return false
	var parts: PackedStringArray = path.trim_prefix(owned + "/").split("/", false)
	for index: int in range(parts.size()):
		if directory.is_link(parts[index]):
			return false
		if index < parts.size() - 1 and directory.change_dir(parts[index]) != OK:
			return false
	return not parts.is_empty()


func _vector(words: PackedInt64Array) -> Vector3:
	return Vector3(Words.read_word(words[0]), Words.read_word(words[1]), Words.read_word(words[2]))


func _vector_words(value: Vector3) -> PackedInt64Array:
	return PackedInt64Array([Words.store_word(value.x), Words.store_word(value.y), Words.store_word(value.z)])


func _hash(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(bytes)
	return hash.finish().hex_encode()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	_counts[group] = int(_counts.get(group, 0)) + 1
	if actual != expected:
		_failures.append({"group": group, "name": name, "actual": str(actual), "expected": str(expected)})


func _finish() -> void:
	var report: Dictionary = {"schema": 1, "failure_count": _failures.size(), "counts": _counts, "completed": _completed, "failures": _failures}
	var output := FileAccess.open(_report, FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print("WATER_SCENE_CHECKS: ", _counts, "; failures=", _failures.size(), "; report=", _report)
	quit(0 if _failures.is_empty() else 1)
