# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Standard-engine checks against the unchanged C# appearance/compositor.
## Inputs: an owned object-free reference.variant and a fresh owned report.json.
const Appearance = preload("res://Scenes/World/terrain_appearance.gd")
const Probes = preload("res://Scenes/World/terrain_probes.gd")
const PublicMaterial = preload("res://Scenes/World/TerrainMaterial.tres")
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
	if not reference is Dictionary or reference.get("schema") != 1 or reference.get("completed") != ["terrain_appearance_reference"]:
		quit(2)
		return
	for name: String in ["public-terrain.tres", "public-terrain-repeat.tres", "private-terrain.res", "private-terrain-repeat.res"]:
		if FileAccess.file_exists(_report.get_base_dir().path_join(name)):
			quit(2)
			return
	var pointer: int = Input.mouse_mode
	var before: Dictionary = _input_hashes(reference.input_hashes)
	_check("read_only", "input identity", before, reference.input_hashes)
	_probes(reference)
	_completed.append("probes")
	_resources(reference)
	_completed.append("resources")
	if Engine.is_editor_hint():
		_check("editor", "cache loader refuses before invalid input/probe", Appearance.load_paths("", "", "", "", null), {
			"ok": false, "error_type": "InvalidOperationException", "error": "Editor inspection uses saved terrain resources and cannot initialize a live cache or probe."})
		_check("editor", "resources remain production shader", _shader_code(PublicMaterial.shader.code), reference.shader)
		_completed.append("editor")
	else:
		_admission(reference)
		_completed.append("admission")
		_runtime(reference)
		_completed.append("runtime")
		_fast(reference)
		_completed.append("fast_batch")
		_supplied(reference)
		_completed.append("supplied_material")
		_private_roundtrip(reference)
		_completed.append("private_roundtrip")
		await process_frame
	_check("read_only", "source bytes unchanged", _input_hashes(before), before)
	_check("read_only", "pointer unchanged", Input.mouse_mode, pointer)
	_completed.append("read_only")
	if Engine.is_editor_hint():
		await create_timer(1.0).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame
		await create_timer(0.25).timeout
	_finish()


func _load(reference: Dictionary, material: ShaderMaterial = null) -> Dictionary:
	var p: Dictionary = reference.paths
	return Appearance.load_paths(p.root, p.hierarchy, p.detail, p.cloud, reference.facts, material)


func _probes(reference: Dictionary) -> void:
	_check("probes", "probe count", reference.probes.size(), 14)
	for row: Dictionary in reference.probes:
		var actual: Dictionary = Probes.resolve(row.input)
		if actual.ok:
			actual = {"ok": true, "code": _shader_code(actual.code)}
		_check("probes", "exact .NET trim/code " + row.input, actual, row.result)


func _resources(reference: Dictionary) -> void:
	var material: ShaderMaterial = PublicMaterial.duplicate()
	_check("resources", "external exact shader body", _shader_code(material.shader.code), reference.shader)
	_check("resources", "local to scene", material.resource_local_to_scene, true)
	var initial: Dictionary = reference.scenarios[0].initial.uniforms
	for name: String in ["detail_map", "cloud_shadow_map"]:
		var texture: Texture2D = material.get_shader_parameter(name)
		_check("resources", name + " virtual recipe", texture != null and texture.has_method("ensure_loaded"), true)
		if texture != null:
			_check("resources", name + " private input admitted", texture.ensure_loaded().ok, true)
			_check("resources", name + " exact decoded image", _image_facts(texture.get_image()), initial[name])
	for level: int in range(5):
		_check("resources", "public macro cache is not live " + str(level), material.get_shader_parameter("macro_map_" + str(level)), null)
	for round: int in range(2):
		var path: String = _report.get_base_dir().path_join("public-terrain.tres" if round == 0 else "public-terrain-repeat.tres")
		_check("resources", "save public material " + str(round), ResourceSaver.save(material, path), OK)
		var text: String = FileAccess.get_file_as_string(path)
		for marker: String in ["PackedByteArray(", "type=\"ImageTexture\"", "type=\"Image\"", "macro_map_0"]:
			_check("resources", "no public payload " + str(round) + marker, text.contains(marker), false)
		material = ResourceLoader.load(path, "ShaderMaterial", ResourceLoader.CACHE_MODE_IGNORE)
		_check("resources", "public reload shader " + str(round), _shader_code(material.shader.code), reference.shader)
		for name: String in ["detail_map", "cloud_shadow_map"]:
			var texture: Texture2D = material.get_shader_parameter(name)
			_check("resources", "public reload recipe " + str(round) + name, texture.has_method("ensure_loaded"), true)
			_check("resources", "public reload pixels " + str(round) + name, _image_facts(texture.get_image()), initial[name])


func _admission(reference: Dictionary) -> void:
	_check("admission", "fixture count", reference.admission.size(), 6)
	for row: Dictionary in reference.admission:
		var facts: Variant = null if row.null_field else reference.facts.duplicate(true)
		if facts != null:
			facts.mixer_set = row.mixer
			facts.detail_texture = row.detail
		var result: Dictionary = Appearance.load_paths(row.root, row.hierarchy, reference.paths.detail, reference.paths.cloud, facts)
		_check("admission", row.name, result, row.result)
	var unconfigured: RefCounted = Appearance.new()
	_check("admission", "unconfigured update refuses", unconfigured.update_tiles(PackedInt32Array(), 0.0).ok, false)
	var loaded: Dictionary = _load(reference)
	_check("admission", "valid retry", loaded.ok, true)
	if loaded.ok:
		var owner: RefCounted = loaded.value
		var initial: Dictionary = _snapshot(owner)
		_check("admission", "wrong packed type", owner.update_tiles([1, 2, 3], 1.0).ok, false)
		_check("admission", "incomplete record", owner.update_tiles(PackedInt32Array([1, 2]), 1.0).ok, false)
		_check("admission", "incomplete heightfield", owner.update_heightfield(PackedInt32Array([1, 2, 3]), 1.0).ok, false)
		_check("admission", "host shape refusal before mutation", _snapshot(owner), initial)


func _runtime(reference: Dictionary) -> void:
	_check("runtime", "scenario count", reference.scenarios.size(), 8)
	for scenario: Dictionary in reference.scenarios:
		var loaded: Dictionary = _load(reference)
		_check("runtime", scenario.name + " load", loaded.ok, true)
		if not loaded.ok:
			continue
		var owner: RefCounted = loaded.value
		var textures: Array = owner.get("_macro_textures").duplicate()
		_check("runtime", scenario.name + " initial", _snapshot(owner), scenario.initial)
		for index: int in range(scenario.steps.size()):
			var row: Dictionary = scenario.steps[index]
			var result: Dictionary = owner.update_tiles(row.tiles, row.delta.decode_double(0))
			_check("runtime", scenario.name + " result " + str(index), result, row.result)
			_check("cache", scenario.name + " raw phase/CPU/GPU/owner order " + str(index), _snapshot(owner), row.state)
			for level: int in range(5):
				_check("identity", scenario.name + " texture " + str(index) + ":" + str(level), owner.get("_macro_textures")[level], textures[level])


func _fast(reference: Dictionary) -> void:
	var explicit_result: Dictionary = _load(reference)
	var fast_result: Dictionary = _load(reference)
	_check("fast", "both owners admitted", explicit_result.ok and fast_result.ok, true)
	if not explicit_result.ok or not fast_result.ok:
		return
	var explicit_owner: RefCounted = explicit_result.value
	var fast_owner: RefCounted = fast_result.value
	var fixture: Dictionary = reference.fast
	_check("fast", "full record count", fixture.packed.size(), 4096 * 3)
	_check("fast", "explicit ordered admission", explicit_owner.update_tiles(fixture.explicit, fixture.delta.decode_double(0)), {"ok": true})
	_check("fast", "packed heightfield admission", fast_owner.update_heightfield(fixture.packed, fixture.delta.decode_double(0)), {"ok": true})
	_check("fast", "explicit matches old C#", _snapshot(explicit_owner), fixture.state)
	_check("fast", "packed matches old C#", _snapshot(fast_owner), fixture.state)
	_check("fast", "identical two native entry points", _snapshot(fast_owner), _snapshot(explicit_owner))
	# A failed batch checks that the fast path preserves the same y-major
	# failure and partial CPU state as the explicit list and original owner.
	explicit_result = _load(reference)
	fast_result = _load(reference)
	explicit_owner = explicit_result.value
	fast_owner = fast_result.value
	var packed := PackedInt32Array()
	packed.resize(4096 * 3)
	packed[1] = 1
	packed[32 * 3 + 1] = 1
	var expected: Dictionary = reference.scenarios[1].steps[0]
	_check("fast", "explicit alias", explicit_owner.update_tiles(expected.tiles, expected.delta.decode_double(0)), expected.result)
	_check("fast", "packed alias", fast_owner.update_heightfield(packed, expected.delta.decode_double(0)), expected.result)
	_check("fast", "packed alias mutation boundary", _snapshot(fast_owner), expected.state)
	_check("fast", "explicit alias mutation boundary", _snapshot(explicit_owner), expected.state)


func _supplied(reference: Dictionary) -> void:
	var had_probe: bool = OS.has_environment("ONSLAUGHT_TERRAIN_PROBE")
	var previous_probe: String = OS.get_environment("ONSLAUGHT_TERRAIN_PROBE")
	for row: Dictionary in reference.supplied:
		var shader := Shader.new()
		shader.code = reference.shader + "\n// supplied shader identity"
		var material := ShaderMaterial.new()
		material.shader = shader
		material.set_shader_parameter("terrain_cloud_scroll", Vector2(0.25, 0.75))
		material.set_shader_parameter("fog_density", 0.125)
		OS.set_environment("ONSLAUGHT_TERRAIN_PROBE", row.probe)
		var result: Dictionary = _load(reference, material)
		_check("supplied", "admission " + row.probe, {"ok": true} if result.ok else result, row.result)
		_check("supplied", "material identity " + row.probe, not result.ok or result.value.get_material() == material, row.same_material)
		_check("supplied", "shader identity " + row.probe, material.shader == shader, row.same_shader)
		_check("supplied", "shader code " + row.probe, _shader_code(material.shader.code), row.shader)
		_check("supplied", "existing/changed uniforms " + row.probe, _uniforms(material), row.uniforms)
	if had_probe:
		OS.set_environment("ONSLAUGHT_TERRAIN_PROBE", previous_probe)
	else:
		OS.unset_environment("ONSLAUGHT_TERRAIN_PROBE")


func _private_roundtrip(reference: Dictionary) -> void:
	var loaded: Dictionary = _load(reference)
	_check("private", "load", loaded.ok, true)
	if not loaded.ok:
		return
	var owner: RefCounted = loaded.value
	var row: Dictionary = reference.scenarios[0].steps[1]
	_check("private", "populate actual caches", owner.update_tiles(row.tiles, row.delta.decode_double(0)).ok, true)
	var material: ShaderMaterial = owner.get_material()
	var expected: Dictionary = _material_facts(material)
	for round: int in range(2):
		var path: String = _report.get_base_dir().path_join("private-terrain.res" if round == 0 else "private-terrain-repeat.res")
		_check("private", "save " + str(round), ResourceSaver.save(material, path), OK)
		material = ResourceLoader.load(path, "ShaderMaterial", ResourceLoader.CACHE_MODE_IGNORE)
		_check("private", "saved exact GPU resource " + str(round), _material_facts(material), expected)
	var saved_shader: Shader = material.shader
	loaded = _load(reference, material)
	_check("private", "rebind saved material", loaded.ok, true)
	if loaded.ok:
		_check("private", "supplied material identity retained", loaded.value.get_material(), material)
		_check("private", "supplied shader identity retained", material.shader, saved_shader)
		_check("private", "constructor resets caches and retains cloud uniform", _uniforms(material)["terrain_cloud_scroll"], expected.uniforms.terrain_cloud_scroll)
		_check("private", "runtime rebinding selects same root", _image_facts(material.get_shader_parameter("macro_map_0").get_image()), reference.scenarios[0].initial.levels[0].gpu)
		_check("private", "runtime rebinding resets CPU/GPU macro1", _image_facts(material.get_shader_parameter("macro_map_1").get_image()), reference.scenarios[0].initial.levels[1].gpu)


func _snapshot(owner: RefCounted) -> Dictionary:
	var levels: Array[Dictionary] = []
	var cpu: Array = owner.get("_cache_bytes")
	var textures: Array = owner.get("_macro_textures")
	var owners: Array = owner.get("_slot_owners")
	var occupied: Array = owner.get("_occupied_slots")
	for level: int in range(5):
		levels.append({"cpu": _hash(cpu[level]), "gpu": _image_facts(textures[level].get_image()),
			"owners": owners[level].duplicate(), "occupied": occupied[level].duplicate()})
	return {"u": _double_bytes(owner.get("_cloud_scroll_u")), "v": _double_bytes(owner.get("_cloud_scroll_v")),
		"levels": levels, "uniforms": _uniforms(owner.get_material())}


func _uniforms(material: ShaderMaterial) -> Dictionary:
	var result: Dictionary = {}
	for name: String in ["fog_color", "fog_density", "terrain_vertex_diffuse", "terrain_cloud_scroll"]:
		result[name] = var_to_bytes(material.get_shader_parameter(name))
	for name: String in ["detail_map", "cloud_shadow_map"]:
		var value: Variant = material.get_shader_parameter(name)
		if value is Texture2D:
			result[name] = _image_facts(value.get_image())
	return result


func _material_facts(material: ShaderMaterial) -> Dictionary:
	var textures: Array[Dictionary] = []
	for level: int in range(5):
		textures.append(_image_facts(material.get_shader_parameter("macro_map_" + str(level)).get_image()))
	return {"textures": textures, "uniforms": _uniforms(material), "shader": _shader_code(material.shader.code)}


func _image_facts(image: Image) -> Dictionary:
	return {"width": image.get_width(), "height": image.get_height(), "format": image.get_format(), "mips": image.has_mipmaps(), "sha256": _hash(image.get_data())}


func _double_bytes(value: float) -> PackedByteArray:
	var result := PackedByteArray()
	result.resize(8)
	result.encode_double(0, value)
	return result


func _shader_code(value: String) -> String:
	return value.trim_prefix("// SPDX-License-Identifier: GPL-3.0-or-later\n").trim_suffix("\n")


func _input_hashes(paths: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	for path: String in paths:
		result[path] = _hash(FileAccess.get_file_as_bytes(path))
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
		var failure: Dictionary = {"group": group, "label": label, "actual": str(actual), "expected": str(expected)}
		_failures.append(failure)
		printerr(group + ": " + label)


func _finish() -> void:
	var report: Dictionary = {"schema": 1, "failure_count": _failures.size(), "counts": _counts, "completed": _completed, "failures": _failures}
	var file := FileAccess.open(_report, FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(report))
	file.close()
	print("TERRAIN_APPEARANCE_CHECKS: " + JSON.stringify({"counts": _counts, "failure_count": _failures.size(), "completed": _completed}))
	quit(0 if _failures.is_empty() else 1)
