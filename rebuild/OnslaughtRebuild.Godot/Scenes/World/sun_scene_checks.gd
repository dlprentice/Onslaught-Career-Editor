# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual production scene check. Args: existing owned reference.variant and
## fresh owned report.json; .NET SunSceneChecks.tscn creates the reference.
## Runs on standard Godot, headless, and also under the actual --editor hint.
const Sun = preload("res://Scenes/World/sun_sprite.gd")
const Scene = preload("res://Scenes/World/SunSprite.tscn")
const Float32 = preload("res://Core/retail_float24.gd")
const WORLD_PATH: String = "res://Assets/Level100/Scenes/Level100.tscn"
var _counts: Dictionary = {}
var _failures: Array[Dictionary] = []
var _completed: Array[String] = []
var _report: String


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or not _owned_path(args[0]) or not _owned_path(args[1]) or args[0] == args[1] or FileAccess.file_exists(args[1]):
		quit(2)
		return
	_report = args[1]
	var input := FileAccess.open(args[0], FileAccess.READ)
	if input == null:
		quit(2)
		return
	var reference: Variant = input.get_var(false)
	input.close()
	if not reference is Dictionary or reference.get("schema") != 1 or reference.get("completed") != ["sun_reference"]:
		push_error("The Sun reference fixture is incomplete.")
		quit(2)
		return
	for file: String in ["public-sun.tscn", "baked-sun.tscn", "external-sun.tscn", "external-sun-repeat.tscn"]:
		if FileAccess.file_exists(_report.get_base_dir().path_join(file)):
			push_error("Sun round-trip output already exists.")
			quit(2)
			return
	var pointer: int = Input.mouse_mode
	var before: Dictionary = _input_hashes(reference.input_hashes)
	_check("read_only", "reference input identities", before, reference.input_hashes)
	var sun: Sun = Scene.instantiate()
	root.add_child(sun)
	if not _scene(sun, reference):
		sun.free()
		_finish()
		return
	_completed.append("scene")
	if Engine.is_editor_hint():
		_check("editor", "no sampler before configure", sun.get("_terrain"), null)
		_check("editor", "configure refuses before inspecting supplied bytes", sun.configure(PackedByteArray(), false).ok, false)
		_check("editor", "camera update refuses", sun.update_camera(Vector3.ONE).ok, false)
		_check("editor", "still no sampler", sun.get("_terrain"), null)
		_check("editor", "no processing", sun.is_processing(), false)
		_check("editor", "no physics", sun.is_physics_processing(), false)
		_check("editor", "no input", sun.is_processing_input(), false)
		_check("editor", "no unhandled input", sun.is_processing_unhandled_input(), false)
		_check("editor", "no unhandled key input", sun.is_processing_unhandled_key_input(), false)
		_check("editor", "preview is visible geometry", sun.mesh is QuadMesh and sun.material_override is StandardMaterial3D, true)
		_completed.append("editor")
	else:
		if _runtime(sun, reference):
			_completed.append("runtime")
	if _public_roundtrip(reference):
		_completed.append("public_roundtrip")
	if _external_roundtrip(reference):
		_completed.append("external_roundtrip")
	_check("read_only", "all source inputs unchanged", _input_hashes(before), before)
	_check("safety", "pointer unchanged", Input.mouse_mode, pointer)
	_completed.append("read_only")
	sun.free()
	await process_frame
	if Engine.is_editor_hint():
		# A probe quit during scan reports unrelated editor shutdown resources.
		# Let this actual editor process finish its own scan before final drain.
		await create_timer(1.0).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame
		await create_timer(0.25).timeout
	_finish()


func _scene(sun: Sun, reference: Dictionary) -> bool:
	_check("scene", "production script", sun.get_script(), Sun)
	_check("scene", "original node name", str(sun.name), "RetailLevel100SunSprite")
	_check("scene", "no autonomous children", sun.get_child_count(), 0)
	_check("scene", "starts without sampler", sun.get("_terrain"), null)
	_check("scene", "starts without processing", sun.is_processing(), false)
	_check("scene", "authored material", sun.base_material is StandardMaterial3D, true)
	_check("scene", "authored source recipe", sun.particle_recipe is Resource, true)
	var layer: Variant = sun.particle_recipe.call("read_layer")
	_check("scene", "recipe resolves in current editor/runtime context", layer is Dictionary and layer.get("ok", false), true)
	if not layer is Dictionary or not layer.get("ok", false):
		return false
	_check("scene", "all shipped layer values", layer.value, reference.definition)
	var visual: Dictionary = sun.prepare_visual(false)
	_check("scene", "production visual admission", visual.ok, true)
	if not visual.ok:
		return false
	_visual(sun, reference, "scene")
	var recipe: Resource = sun.particle_recipe.duplicate(true)
	recipe.set("source_path", "res://Assets/Level100/ParticleSets/Unadmitted.par")
	_check("admission", "changed particle input route refused", recipe.call("read_layer").ok, false)
	recipe.set("source_path", sun.particle_recipe.get("source_path"))
	recipe.set("descriptor_name", "Another Sprite")
	_check("admission", "changed descriptor refused", recipe.call("read_layer").ok, false)
	return true


func _runtime(sun: Sun, reference: Dictionary) -> bool:
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(reference.terrain_path)
	_check("runtime", "unconfigured camera refuses", sun.update_camera(Vector3.ONE).ok, false)
	_check("runtime", "invalid terrain refuses", sun.configure(PackedByteArray(), false).ok, false)
	_check("runtime", "invalid terrain starts no sampler", sun.get("_terrain"), null)
	var admitted: Dictionary = sun.configure(bytes, false)
	_check("runtime", "explicit pinned configuration", admitted.ok, true)
	if not admitted.ok:
		return false
	var offsets: Dictionary = sun.offsets()
	_check("numeric", "offset raw words", _vector_words(offsets.offset), reference.offset)
	_check("numeric", "normalized direction raw words", _vector_words(offsets.direction), reference.direction)
	_check("numeric", "defined height count", reference.height_cases.size(), 848)
	_check("numeric", "defined camera count", reference.camera_cases.size(), 2348)
	for index: int in range(reference.height_cases.size()):
		var row: Dictionary = reference.height_cases[index]
		_check("height", str(index), Float32.store_word(sun.relative_height(Float32.read_word(row.x_bits), Float32.read_word(row.z_bits))), row.value_bits)
	var visible: int = 0
	var hidden: int = 0
	for index: int in range(reference.camera_cases.size()):
		var row: Dictionary = reference.camera_cases[index]
		var camera: Vector3 = _vector(row.camera)
		var updated: Dictionary = sun.update_camera(camera)
		_check("camera", str(index) + " update", updated.ok, true)
		_check("camera", str(index) + " position words", _vector_words(sun.position), row.position)
		_check("camera", str(index) + " LOS gate", sun.visible, row.visible)
		if row.visible: visible += 1
		else: hidden += 1
	_check("camera", "both visible and occluded fixtures", visible > 0 and hidden > 0, true)
	for row: Dictionary in reference.constant_colours:
		var result: Dictionary = Sun.constant_colour({"colour_range": row.range})
		var expected: Dictionary = row.expected
		_check("colour", row.name + " admission", result.ok, expected.ok)
		if result.ok and expected.ok:
			_check("colour", row.name + " raw words", _colour_words(result.value), expected.value)
		elif not result.ok and not expected.ok:
			_check("colour", row.name + " failure type", result.error_type, expected.error_type)
	var layer: Dictionary = sun.definition()
	layer.colour_range.start.r_bits = 0
	layer.start_turns[0] = 99
	_check("detachment", "caller edits cannot change admitted definition", sun.definition(), reference.definition)
	offsets.offset = Vector3(99.0, 98.0, 97.0)
	_check("detachment", "caller edits cannot change vector offset", _vector_words(sun.offsets().offset), reference.offset)
	var pack := PackedScene.new()
	_check("private_bake", "explicit bake packs", pack.pack(sun), OK)
	var stored: Dictionary = _stored_root(pack)
	_check("private_bake", "derived mesh is saved", stored.get("mesh") is QuadMesh, true)
	_check("private_bake", "derived material is saved", stored.get("material_override") is StandardMaterial3D, true)
	var baked_path: String = _report.get_base_dir().path_join("baked-sun.tscn")
	_check("private_bake", "save owned derived scene", ResourceSaver.save(pack, baked_path), OK)
	var baked: Sun = _reload(baked_path)
	if baked == null:
		return false
	root.add_child(baked)
	var baked_mesh: Mesh = baked.mesh
	var baked_material: Material = baked.material_override
	_check("private_bake", "saved visual binds to native sampler", baked.configure(bytes, true).ok, true)
	_check("private_bake", "saved mesh identity retained", baked.mesh, baked_mesh)
	_check("private_bake", "saved material identity retained", baked.material_override, baked_material)
	_visual(baked, reference, "private_bake")
	baked.free()
	return true


func _public_roundtrip(reference: Dictionary) -> bool:
	var sun: Sun = Scene.instantiate()
	root.add_child(sun)
	var visual: Dictionary = sun.prepare_visual(false)
	_check("public_roundtrip", "load public visual recipe", visual.ok, true)
	if not visual.ok:
		sun.free()
		return false
	var packed := PackedScene.new()
	_check("public_roundtrip", "pack public preview", packed.pack(sun), OK)
	var properties: Dictionary = _stored_root(packed)
	_check("public_roundtrip", "derived mesh excluded", properties.has("mesh"), false)
	_check("public_roundtrip", "derived material excluded", properties.has("material_override"), false)
	_check("public_roundtrip", "source recipe retained", properties.get("particle_recipe") is Resource, true)
	_check("public_roundtrip", "authored material retained", properties.get("base_material") is StandardMaterial3D, true)
	var path: String = _report.get_base_dir().path_join("public-sun.tscn")
	_check("public_roundtrip", "save public recipe", ResourceSaver.save(packed, path), OK)
	var text: String = FileAccess.get_file_as_string(path)
	for prohibited: String in ["PackedByteArray(", "ImageTexture", "_decoded", "_terrain", "ArrayMesh", "surface_0", "image ="]:
		_check("public_roundtrip", "no private payload " + prohibited, text.contains(prohibited), false)
	var copy: Sun = _reload(path)
	sun.free()
	if copy == null:
		return false
	root.add_child(copy)
	_check("public_roundtrip", "reloaded scene has no sampler", copy.get("_terrain"), null)
	_check("public_roundtrip", "reloaded same recipe decodes production presentation", copy.prepare_visual(false).ok, true)
	_visual(copy, reference, "public_roundtrip")
	copy.free()
	return true


func _external_roundtrip(reference: Dictionary) -> bool:
	# Read just the two Sun resource routes from the private generated scene.
	# Loading the whole world would unnecessarily instantiate retained C# owners.
	var paths: Dictionary = _external_paths()
	_check("external_roundtrip", "existing imported resource routes", paths.size(), 2)
	if paths.size() != 2:
		return false
	var hashes: Dictionary = _input_hashes(paths)
	var sun: Sun = Scene.instantiate()
	sun.mesh = ResourceLoader.load(paths.mesh, "Mesh", ResourceLoader.CACHE_MODE_IGNORE)
	sun.material_override = ResourceLoader.load(paths.material_override, "Material", ResourceLoader.CACHE_MODE_IGNORE)
	root.add_child(sun)
	_check("external_roundtrip", "loading private resources does not create sampler", sun.get("_terrain"), null)
	_check("external_roundtrip", "loading private resources does not process", sun.is_processing(), false)
	_visual(sun, reference, "external_roundtrip")
	var packed := PackedScene.new()
	_check("external_roundtrip", "pack unchanged imported external refs", packed.pack(sun), OK)
	var stored: Dictionary = _stored_root(packed)
	for name: String in ["mesh", "material_override"]:
		_check("external_roundtrip", name + " storage retained", stored.get(name) is Resource, true)
		if stored.get(name) is Resource:
			_check("external_roundtrip", name + " exact imported path", stored[name].resource_path, paths[name])
	var path: String = _report.get_base_dir().path_join("external-sun.tscn")
	_check("external_roundtrip", "save owned external-ref scene", ResourceSaver.save(packed, path), OK)
	var copy: Sun = _reload(path)
	sun.free()
	if copy == null:
		return false
	root.add_child(copy)
	_check("external_roundtrip", "saved refs remain inspector-visible", copy.mesh != null and copy.material_override != null, true)
	_check("external_roundtrip", "saved refs remain inactive", copy.get("_terrain"), null)
	_visual(copy, reference, "external_roundtrip")
	if not Engine.is_editor_hint():
		var mesh_before: Mesh = copy.mesh
		var material_before: Material = copy.material_override
		_check("external_roundtrip", "bind existing private resources", copy.configure(FileAccess.get_file_as_bytes(reference.terrain_path), true).ok, true)
		_check("external_roundtrip", "bind retains exact mesh object", copy.mesh, mesh_before)
		_check("external_roundtrip", "bind retains exact material object", copy.material_override, material_before)
	var repeat := PackedScene.new()
	_check("external_roundtrip", "pack second save", repeat.pack(copy), OK)
	var second: Dictionary = _stored_root(repeat)
	_check("external_roundtrip", "second save retains mesh", second.has("mesh"), true)
	_check("external_roundtrip", "second save retains material", second.has("material_override"), true)
	_check("external_roundtrip", "save again only to owned output", ResourceSaver.save(repeat, _report.get_base_dir().path_join("external-sun-repeat.tscn")), OK)
	copy.free()
	_check("external_roundtrip", "imported resources unchanged", _input_hashes(paths), hashes)
	return true


func _external_paths() -> Dictionary:
	var source: String = FileAccess.get_file_as_string(WORLD_PATH)
	var node_start: int = source.find("[node name=\"RetailLevel100SunSprite\"")
	if node_start < 0:
		return {}
	var end: int = source.find("\n[node ", node_start + 1)
	var block: String = source.substr(node_start, -1 if end < 0 else end - node_start)
	var result: Dictionary = {}
	for property: String in ["mesh", "material_override"]:
		var binding := RegEx.new()
		binding.compile("(?m)^" + property + " = ExtResource\\(\"([^\"]+)\"\\)")
		var value: RegExMatch = binding.search(block)
		if value == null:
			return {}
		var route := RegEx.new()
		route.compile("(?m)^\\[ext_resource [^\\n]*path=\"([^\"]+)\"[^\\n]*id=\"" + value.get_string(1) + "\"\\]")
		var match_value: RegExMatch = route.search(source)
		if match_value == null or not match_value.get_string(1).begins_with("res://Assets/Level100/Scenes/"):
			return {}
		result[property] = match_value.get_string(1)
	return result


func _visual(sun: Sun, reference: Dictionary, group: String) -> void:
	_check(group, "real quad mesh", sun.mesh is QuadMesh, true)
	_check(group, "real material", sun.material_override is StandardMaterial3D, true)
	if not sun.mesh is QuadMesh or not sun.material_override is StandardMaterial3D:
		return
	_check(group, "all mesh properties", _properties(sun.mesh), reference.mesh)
	_check(group, "all material properties", _properties(sun.material_override), reference.material)
	_check(group, "shadow policy", sun.cast_shadow, reference.cast_shadow)
	var texture: Texture2D = sun.material_override.albedo_texture
	_check(group, "production texture present", texture != null, true)
	if texture == null:
		return
	var image: Image = texture.get_image()
	_check(group, "texture pixels available", image != null, true)
	if image != null:
		_check(group, "exact texture size", image.get_size(), reference.texture.size)
		_check(group, "exact texture format", image.get_format(), reference.texture.format)
		_check(group, "mipmap policy", image.has_mipmaps(), reference.texture.mipmaps)
		_check(group, "exact production texture bytes", _sha(image.get_data()), reference.texture.sha256)


func _properties(resource: Resource) -> Dictionary:
	var result: Dictionary = {}
	for property: Dictionary in resource.get_property_list():
		if (int(property.usage) & PROPERTY_USAGE_STORAGE) == 0:
			continue
		var name: String = property.name
		if name in ["resource_local_to_scene", "resource_name", "script"]:
			continue
		var value: Variant = resource.get(name)
		match typeof(value):
			TYPE_OBJECT: result[name] = "Texture2D" if value is Texture2D else null
			TYPE_FLOAT: result[name] = {"float_bits": Float32.store_word(value)}
			TYPE_COLOR: result[name] = {"colour_bits": _colour_words(value)}
			TYPE_VECTOR2: result[name] = {"vector_bits": PackedInt64Array([Float32.store_word(value.x), Float32.store_word(value.y)])}
			TYPE_VECTOR3: result[name] = {"vector_bits": _vector_words(value)}
			_: result[name] = value
	return result


func _stored_root(packed: PackedScene) -> Dictionary:
	var state: SceneState = packed.get_state()
	var result: Dictionary = {}
	for index: int in range(state.get_node_property_count(0)):
		result[str(state.get_node_property_name(0, index))] = state.get_node_property_value(0, index)
	return result


func _reload(path: String) -> Sun:
	var resource: Resource = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	_check("roundtrip", "reload " + path.get_file(), resource is PackedScene, true)
	return resource.instantiate() as Sun if resource is PackedScene else null


func _input_hashes(paths: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	for key: String in paths:
		var path: String = paths[key] if not key.begins_with("res://") and not key.is_absolute_path() else key
		result[key] = _sha(FileAccess.get_file_as_bytes(path))
	return result


func _check(group: String, name: String, actual: Variant, expected: Variant) -> bool:
	_counts[group] = int(_counts.get(group, 0)) + 1
	if actual == expected:
		return true
	_failures.append({"group": group, "name": name, "actual": str(actual), "expected": str(expected)})
	return false


func _finish() -> void:
	var expected: Array[String] = ["scene", "editor" if Engine.is_editor_hint() else "runtime", "public_roundtrip", "external_roundtrip", "read_only"]
	_check("completion", "all sections completed", _completed, expected)
	var output := FileAccess.open(_report, FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify({"schema": 1, "completed": _completed, "failure_count": _failures.size(),
		"counts": _counts, "failures": _failures}, "\t"))
	output.close()
	print(JSON.stringify({"counts": _counts, "failure_count": _failures.size(), "first_failures": _failures.slice(0, 3)}))
	quit(0 if _failures.is_empty() else 1)


static func _vector(words: PackedInt64Array) -> Vector3:
	return Vector3(Float32.read_word(words[0]), Float32.read_word(words[1]), Float32.read_word(words[2]))


static func _vector_words(value: Vector3) -> PackedInt64Array:
	return PackedInt64Array([Float32.store_word(value.x), Float32.store_word(value.y), Float32.store_word(value.z)])


static func _colour_words(value: Color) -> PackedInt64Array:
	return PackedInt64Array([Float32.store_word(value.r), Float32.store_word(value.g), Float32.store_word(value.b), Float32.store_word(value.a)])


static func _sha(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	if hash.start(HashingContext.HASH_SHA256) != OK or hash.update(bytes) != OK:
		push_error("Sun check could not hash bytes.")
		return ""
	return hash.finish().hex_encode()


static func _owned_path(path: String) -> bool:
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
