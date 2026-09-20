# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual Godot material facts are compared with the unchanged C# factory.
## All images are synthetic; existing metadata and comparison inputs stay read-only.
const Factory = preload("res://Scenes/Shared/retail_fixed_function_material.gd")
const Template = preload("res://Scenes/Shared/RetailFixedFunctionMaterial.tres")
const TEXTURES: Array[String] = ["base_texture", "dot3_texture", "reflection_texture", "overlay_texture"]
const VALUES: Array[String] = ["has_dot3", "has_reflection", "has_overlay", "base_blend_texture_alpha",
	"alpha_reference", "stage_zero_gain", "dot3_offset", "dot3_scale", "reflection_factor_alpha", "overlay_offset",
	"overlay_scale", "overlay_opacity", "ambient_color", "sun_color", "anti_sun_color", "sunlight_direction",
	"fog_color", "fog_density", "maximum_horizontal_distance_squared"]
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
	if not reference is Dictionary or reference.get("schema") != 1 or reference.get("completed") != ["fixed_function_material_reference"]:
		quit(2)
		return
	for name: String in ["public-material.tres", "public-material-repeat.tres", "native-material-scene.tscn", "native-material-scene-repeat.tscn"]:
		if FileAccess.file_exists(_report.get_base_dir().path_join(name)):
			quit(2)
			return
	var pointer: int = Input.mouse_mode
	var before: Dictionary = {args[0]: _hash_file(args[0]), reference.terrain_path: reference.input_sha256,
		reference.scene_path: reference.scene_sha256,
		ProjectSettings.globalize_path("res://Scenes/Shared/RetailFixedFunctionMaterial.tres"): _hash_file("res://Scenes/Shared/RetailFixedFunctionMaterial.tres"),
		ProjectSettings.globalize_path("res://Scenes/Shared/retail_fixed_function.gdshader"): _hash_file("res://Scenes/Shared/retail_fixed_function.gdshader")}
	_check("read_only", "input identities", _input_hashes(before), before)
	var texture_resources: Array[Texture2D] = _make_textures(reference.textures)
	if not Engine.is_editor_hint():
		_factory(reference, texture_resources)
		_completed.append("factory")
		_alpha(reference)
		_completed.append("alpha")
		_identity(reference, texture_resources)
		_completed.append("identity")
	_resources(reference)
	_completed.append("resources")
	if Engine.is_editor_hint():
		var children: Array = root.get_children().duplicate()
		var result: Dictionary = _create(reference.scene_input, texture_resources)
		_check("editor", "same production factory admitted", result.ok, true)
		if result.ok:
			_check("editor", "exact native material before Play", _material_facts(result.value, texture_resources), reference.scene_facts.Ordinary.material)
		_check("editor", "factory owns no nodes", root.get_children(), children)
		_check("editor", "factory has no process callbacks", Factory.new().has_method("_process"), false)
		_check("editor", "factory has no input callbacks", Factory.new().has_method("_input"), false)
		_completed.append("editor")
	else:
		_serialization(reference, texture_resources)
		_completed.append("serialization")
	for index: int in range(texture_resources.size()):
		_check("read_only", "supplied texture unchanged " + str(index), _image_facts(texture_resources[index].get_image()), _image_reference(reference.textures[index]))
	_check("read_only", "all input bytes unchanged", _input_hashes(before), before)
	_check("read_only", "pointer unchanged", Input.mouse_mode, pointer)
	_completed.append("read_only")
	texture_resources.clear()
	await process_frame
	if Engine.is_editor_hint():
		await create_timer(1.0).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame
		await create_timer(0.25).timeout
	_finish()


func _make_textures(rows: Array) -> Array[Texture2D]:
	var result: Array[Texture2D] = []
	_check("factory", "four distinct synthetic sources", rows.size(), 4)
	for row: Dictionary in rows:
		var image := Image.create_from_data(row.width, row.height, row.mips, row.format, row.bytes)
		_check("read_only", "synthetic source identity", _image_facts(image), _image_reference(row))
		result.append(ImageTexture.create_from_image(image))
	return result


func _create(row: Dictionary, textures: Array[Texture2D]) -> Dictionary:
	var layers: Variant = null
	if row.layers != null:
		layers = []
		for item: Variant in row.layers:
			if item == null:
				layers.append(null)
			else:
				layers.append({"texture": null if item.texture < 0 else textures[item.texture],
					"opacity": _single(item.opacity), "offset": item.offset, "scale": item.scale,
					"blend_texture_alpha": item.blend_texture_alpha})
	return Factory.create(layers, row.facts, _single(row.distance), _single(row.alpha), row.operation, row.get("rig"))


func _factory(reference: Dictionary, textures: Array[Texture2D]) -> void:
	_check("factory", "bounded complete case inventory", reference.cases.size() >= 80, true)
	for row: Dictionary in reference.cases:
		var result: Dictionary = _create(row, textures)
		_check("factory", row.name + " admission order", {"ok": true} if result.ok else result, row.result)
		if result.ok and row.result.ok:
			_check("factory", row.name + " raw uniforms/textures/defaults", _material_facts(result.value, textures), row.material)
	# Variant-only invalid types are refused explicitly rather than causing a
	# partial script abort. C# typed callers cannot supply these host values.
	_check("factory", "wrong layers type", Factory.create(7, null).error_type, "ArgumentException")
	_check("factory", "wrong operation type", Factory.create([{"texture": null}, null, null, null, null, null], null, 0.0, 0.5, "5").error_type, "ArgumentException")
	_check("factory", "wrong layer type", Factory.create([{}, null, null, null, null, null], null).error_type, "ArgumentException")
	_check("factory", "valid retry after refusal", _create(reference.scene_input, textures).ok, true)


func _alpha(reference: Dictionary) -> void:
	_check("alpha", "midpoints plus nonfinite/overflow inventory", reference.alpha_words.size() >= 1000, true)
	for row: Dictionary in reference.alpha_words:
		_check("alpha", "Single/ties-even/host-cast " + str(row.input), _word(Factory.texture_factor_alpha(_single(row.input))), row.output)


func _identity(reference: Dictionary, textures: Array[Texture2D]) -> void:
	var materials: Array[ShaderMaterial] = []
	for row: Dictionary in reference.cases:
		if not row.result.ok:
			continue
		var result: Dictionary = _create(row, textures)
		if not result.ok:
			_check("identity", row.name + " admitted", result.ok, true)
			continue
		var material: ShaderMaterial = result.value
		_check("identity", row.name + " unique material", materials.has(material), false)
		_check("identity", row.name + " one external shader", material.shader, Template.shader)
		_check("identity", row.name + " template not mutated", material != Template, true)
		for name: String in TEXTURES:
			var index: int = row.material.textures[name]
			_check("identity", row.name + name + " shares supplied texture", material.get_shader_parameter(name), null if index < 0 else textures[index])
		materials.append(material)
	for name: String in TEXTURES:
		_check("identity", "public template has no bound texture " + name, Template.get_shader_parameter(name), null)
	materials.clear()


func _resources(reference: Dictionary) -> void:
	var material: ShaderMaterial = Template.duplicate()
	_check("resources", "shader exact apart from SPDX/EOL", _shader_code(material.shader.code), _shader_code(reference.shader))
	_check("resources", "original default resource sharing", material.resource_local_to_scene, false)
	_check("resources", "original default render priority", material.render_priority, 0)
	_check("resources", "original default next pass", material.next_pass, null)
	_check("resources", "external shader is inspectable", material.shader.resource_path, "res://Scenes/Shared/retail_fixed_function.gdshader")
	for round: int in range(2):
		var path: String = _report.get_base_dir().path_join("public-material.tres" if round == 0 else "public-material-repeat.tres")
		_check("resources", "public save " + str(round), ResourceSaver.save(material, path), OK)
		var text: String = FileAccess.get_file_as_string(path)
		for marker: String in ["PackedByteArray(", "type=\"ImageTexture\"", "type=\"Image\"", "shader_parameter/base_texture"]:
			_check("resources", "no public payload " + str(round) + marker, text.contains(marker), false)
		material = ResourceLoader.load(path, "ShaderMaterial", ResourceLoader.CACHE_MODE_IGNORE)
		_check("resources", "public exact shader reload " + str(round), _shader_code(material.shader.code), _shader_code(reference.shader))
		for name: String in TEXTURES:
			_check("resources", "public reload unbound " + str(round) + name, material.get_shader_parameter(name), null)


func _serialization(reference: Dictionary, textures: Array[Texture2D]) -> void:
	var result: Dictionary = _create(reference.scene_input, textures)
	_check("serialization", "same factory builds production material", result.ok, true)
	if not result.ok:
		return
	var scene: Node3D = _build_scene(result.value)
	root.add_child(scene)
	_check("serialization", "ordinary and mirrored original scene facts", _scene_facts(scene, textures), reference.scene_facts)
	_check_scene_aliases("native", scene)
	var old_packed: PackedScene = ResourceLoader.load(reference.scene_path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	var old_scene: Node3D = old_packed.instantiate()
	var saved_reference: Dictionary = _scene_facts(old_scene, textures, true)
	# Godot text serialization writes fog_density as decimal 0.0084. Its
	# reloaded binary64 Variant differs from the fresh widened Single, in both
	# implementations, while the shader Single word stays 0x3c09a027. Compare
	# actual old/new reload carriers exactly, and original shader words below.
	_check("serialization", "old reload retains every shader Single word", _shader_single_facts(saved_reference), reference.scene_facts)
	_check_scene_aliases("legacy saved", old_scene)
	old_scene.free()
	for round: int in range(2):
		var path: String = _report.get_base_dir().path_join("native-material-scene.tscn" if round == 0 else "native-material-scene-repeat.tscn")
		var packed := PackedScene.new()
		_check("serialization", "pack " + str(round), packed.pack(scene), OK)
		_check("serialization", "save " + str(round), ResourceSaver.save(packed, path), OK)
		scene.free()
		packed = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
		scene = packed.instantiate()
		root.add_child(scene)
		var saved_actual: Dictionary = _scene_facts(scene, textures, true)
		_check("serialization", "old/new reload raw carriers/geometry " + str(round), saved_actual, saved_reference)
		_check("serialization", "native reload retains original shader Single words " + str(round), _shader_single_facts(saved_actual), reference.scene_facts)
		_check("serialization", "external shader after save " + str(round), ((scene.get_node("Ordinary") as MeshInstance3D).material_override as ShaderMaterial).shader, Template.shader)
		_check_scene_aliases("native saved " + str(round), scene)
	scene.free()


func _build_scene(material: ShaderMaterial) -> Node3D:
	var scene := Node3D.new()
	scene.name = "MaterialComparison"
	var mesh := ArrayMesh.new()
	var arrays: Array = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = PackedVector3Array([Vector3(-1, -1, 0), Vector3(1, -1, 0), Vector3(0, 1, 0)])
	arrays[Mesh.ARRAY_NORMAL] = PackedVector3Array([Vector3.BACK, Vector3.BACK, Vector3.BACK])
	arrays[Mesh.ARRAY_TEX_UV] = PackedVector2Array([Vector2.ZERO, Vector2.RIGHT, Vector2.DOWN])
	arrays[Mesh.ARRAY_COLOR] = PackedColorArray([Color.WHITE, Color(0.5, 0.5, 0.5, 1), Color.WHITE])
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	for mirrored: bool in [false, true]:
		var node := MeshInstance3D.new()
		node.name = "Mirrored" if mirrored else "Ordinary"
		node.mesh = mesh
		node.material_override = material
		node.transform = Transform3D(Basis.from_scale(Vector3(-1 if mirrored else 1, 1, 1)), Vector3(3 if mirrored else 0, 0, 0))
		scene.add_child(node)
		node.owner = scene
	return scene


func _scene_facts(scene: Node3D, textures: Array[Texture2D], match_saved_by_hash: bool = false) -> Dictionary:
	var result: Dictionary = {}
	for node: MeshInstance3D in scene.get_children():
		result[str(node.name)] = {"transform": var_to_bytes(node.transform), "mesh": _hash(var_to_bytes(node.mesh.surface_get_arrays(0))),
			"shadow": node.cast_shadow, "layers": node.layers, "material": _material_facts(node.material_override as ShaderMaterial, textures, match_saved_by_hash)}
	return result


func _check_scene_aliases(label: String, scene: Node3D) -> void:
	var ordinary: MeshInstance3D = scene.get_node("Ordinary")
	var mirrored: MeshInstance3D = scene.get_node("Mirrored")
	_check("serialization", label + " same mesh shared", ordinary.mesh, mirrored.mesh)
	_check("serialization", label + " same material shared", ordinary.material_override, mirrored.material_override)
	_check("serialization", label + " mirror retained", mirrored.transform.basis.determinant(), -1.0)
	_check("serialization", label + " ordinary retained", ordinary.transform.basis.determinant(), 1.0)
	_check("serialization", label + " no scene processing", scene.is_processing() or scene.is_physics_processing() or scene.is_processing_input(), false)


func _material_facts(material: ShaderMaterial, textures: Array[Texture2D], match_saved_by_hash: bool = false) -> Dictionary:
	var values: Dictionary = {}
	var selected: Dictionary = {}
	var pixels: Dictionary = {}
	for name: String in VALUES:
		values[name] = var_to_bytes(material.get_shader_parameter(name))
	for name: String in TEXTURES:
		var texture: Texture2D = material.get_shader_parameter(name)
		var index: int = textures.find(texture)
		if texture != null:
			pixels[name] = _hash(texture.get_image().get_data())
			if match_saved_by_hash:
				for candidate: int in range(textures.size()):
					if _hash(textures[candidate].get_image().get_data()) == pixels[name]:
						index = candidate
		selected[name] = index
	return {"values": values, "textures": selected, "pixels": pixels, "priority": material.render_priority,
		"next_pass": material.next_pass == null, "local_to_scene": material.resource_local_to_scene}


func _shader_single_facts(facts: Dictionary) -> Dictionary:
	var result: Dictionary = facts.duplicate(true)
	for node: String in result:
		for name: String in VALUES:
			var value: Variant = bytes_to_var(result[node].material.values[name])
			if typeof(value) == TYPE_FLOAT:
				result[node].material.values[name] = var_to_bytes(_single(_word(value)))
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


func _image_reference(row: Dictionary) -> Dictionary:
	return {"width": row.width, "height": row.height, "format": row.format, "mips": row.mips, "sha256": row.sha256}


func _image_facts(image: Image) -> Dictionary:
	return {"width": image.get_width(), "height": image.get_height(), "format": image.get_format(), "mips": image.has_mipmaps(), "sha256": _hash(image.get_data())}


func _shader_code(value: String) -> String:
	return value.replace("\r\n", "\n").trim_prefix("// SPDX-License-Identifier: GPL-3.0-or-later\n").trim_suffix("\n")


func _hash_file(path: String) -> String:
	return _hash(FileAccess.get_file_as_bytes(path))


func _input_hashes(paths: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	for path: String in paths:
		result[path] = _hash_file(path)
	return result


func _hash(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	if not bytes.is_empty():
		hash.update(bytes)
	return hash.finish().hex_encode()


func _owned(path: String) -> bool:
	var base: String = ProjectSettings.globalize_path("res://").path_join("../../local-data").simplify_path() + "/"
	return path.is_absolute_path() and path.simplify_path().begins_with(base) and DirAccess.dir_exists_absolute(path.get_base_dir())


func _check(group: String, label: String, actual: Variant, expected: Variant) -> void:
	_counts[group] = _counts.get(group, 0) + 1
	if actual != expected:
		_failures.append({"group": group, "label": label, "actual": str(actual), "expected": str(expected)})
		printerr(group + ": " + label)


func _finish() -> void:
	var file := FileAccess.open(_report, FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify({"schema": 1, "failure_count": _failures.size(), "counts": _counts, "completed": _completed, "failures": _failures}))
	file.close()
	print("FIXED_FUNCTION_MATERIAL_CHECKS: " + JSON.stringify({"counts": _counts, "failure_count": _failures.size(), "completed": _completed}))
	quit(0 if _failures.is_empty() else 1)
