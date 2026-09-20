# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Standard-engine comparison against the unchanged former C# renderer. Args:
## existing private fixture.variant, fresh private report.json. Full arrays
## remain in ignored output; comparisons use exact stored float32 words.
const HeightField = preload("res://Scenes/World/height_field.gd")
const Float32 = preload("res://Core/retail_float24.gd")
var _counts: Dictionary = {}
var _failures: Array[Dictionary] = []
var _completed: Array[String] = []
var _report: String
var _finished: bool = false
var _mesh_words: int = 0


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if Engine.is_editor_hint() or DisplayServer.get_name() != "headless" or args.size() != 2 \
		or not _owned_path(args[0]) or not _owned_path(args[1]) or args[0] == args[1] or FileAccess.file_exists(args[1]):
		quit(2)
		return
	_report = args[1]
	create_timer(150.0).timeout.connect(func() -> void:
		if not _finished:
			_failures.append({"group": "completion", "name": "heightfield harness timed out before completion"})
			_finish())
	var input := FileAccess.open(args[0], FileAccess.READ)
	if input == null:
		quit(2)
		return
	var reference: Variant = input.get_var(false)
	input.close()
	if not reference is Dictionary or reference.get("schema") != 1 or reference.get("completed") != ["height_field_reference"]:
		push_error("Heightfield reference fixture is incomplete.")
		quit(2)
		return
	var pointer: int = Input.mouse_mode
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(reference.terrain_path)
	_check("read_only", "source matches reference bytes", _sha(bytes), reference.terrain_sha256)
	_check("admission", "empty source refuses", HeightField.from_bytes(PackedByteArray()).get("ok"), false)
	var seed: ArrayMesh = _seed_mesh()
	var before_seed: Dictionary = _mesh_words_for(seed)
	var damaged: PackedByteArray = bytes.duplicate()
	damaged[damaged.size() - 1] ^= 1
	_check("admission", "corrupt source refuses", HeightField.from_bytes(damaged, seed).get("ok"), false)
	_check("admission", "refused source leaves supplied mesh unchanged", _mesh_words_for(seed), before_seed)
	seed = null
	var admitted: Dictionary = HeightField.from_bytes(bytes)
	_check("admission", "pinned source accepted", admitted.get("ok"), true)
	if not admitted.get("ok", false):
		_finish()
		return
	var field: HeightField.Field = admitted.value
	admitted.clear()
	_check("metadata", "all existing properties and exact words", _renderer_metadata(field, reference.metadata), reference.metadata)
	_check("metadata", "initial state has no sampled camera", _normalize(field.state()), reference.initial_state)
	_check("metadata", "constructor leaves a new mesh empty", field.get_mesh().get_surface_count(), 0)
	var metadata: Dictionary = field.metadata()
	metadata.water_texture = 999
	_check("detachment", "metadata edits never alter the owner", _renderer_metadata(field, reference.metadata), reference.metadata)
	_completed.append("metadata")
	if _height_cases(field, reference.height_cases):
		_completed.append("heights")
	if _index_cases(reference.index_cases):
		_completed.append("indices")
	var observer := MeshInstance3D.new()
	root.add_child(observer)
	var mesh_result: Variant = _camera_cases(field, bytes, observer, reference.camera_cases)
	if not mesh_result is Dictionary or not mesh_result.get("ok", false):
		observer.free()
		_finish()
		return
	field = mesh_result.field
	mesh_result.clear()
	_completed.append("meshes")
	# The field owns its mutable renderer state, while a scene node may retain
	# the shared ArrayMesh after that state is released. No process is required.
	var retained_mesh: ArrayMesh = field.get_mesh()
	var field_ref: WeakRef = weakref(field)
	field = null
	_check("sharing", "field releases without a cycle", field_ref.get_ref(), null)
	_check("sharing", "scene node retains the exact shared mesh", observer.mesh, retained_mesh)
	_check("sharing", "shared mesh remains readable after owner release", _mesh_words_for(retained_mesh), reference.camera_cases[-1].mesh)
	var mesh_ref: WeakRef = weakref(retained_mesh)
	observer.mesh = null
	retained_mesh = null
	observer.free()
	_check("sharing", "last mesh owner releases its native resource", mesh_ref.get_ref(), null)
	_completed.append("sharing")
	_check("read_only", "retained source bytes unchanged", _sha(FileAccess.get_file_as_bytes(reference.terrain_path)), reference.terrain_sha256)
	_check("read_only", "pointer ownership unchanged", Input.mouse_mode, pointer)
	_completed.append("read_only")
	await process_frame
	_finish()


func _height_cases(field: HeightField.Field, cases: Array) -> bool:
	_check("height", "bounded scalar fixture count", cases.size(), 464)
	for index: int in range(cases.size()):
		var row: Dictionary = cases[index]
		_check("height", str(index), _word(field.sample_relative_height(_float(row.x_bits), _float(row.z_bits))), row.value_bits)
	return true


func _index_cases(cases: Array) -> bool:
	_check("indices", "root plus all patch stitch variants", cases.size(), 49)
	for row: Dictionary in cases:
		var actual: PackedInt32Array = HeightField.tile_indices(row.geometry_level, row.edge_flags)
		_check("indices", "%d/%d" % [row.geometry_level, row.edge_flags], actual, row.indices)
		if not actual.is_empty(): actual[0] = 999
		_check("detachment", "cached index pattern is not caller-owned", HeightField.tile_indices(row.geometry_level, row.edge_flags), row.indices)
	return true


func _camera_cases(initial: HeightField.Field, bytes: PackedByteArray, observer: MeshInstance3D, cases: Array) -> Dictionary:
	_check("camera", "bounded full mesh fixture count", cases.size(), 12)
	var field: HeightField.Field = initial
	var sentinel := StandardMaterial3D.new()
	sentinel.albedo_color = Color(0.17, 0.31, 0.59, 1.0)
	for row: Dictionary in cases:
		if row.reset:
			observer.mesh = null
			var supplied: ArrayMesh = _seed_mesh() if row.supplied_mesh else null
			var admitted: Dictionary = HeightField.from_bytes(bytes, supplied)
			_check("camera", row.name + " fresh owner admitted", admitted.get("ok"), true)
			if not admitted.get("ok", false): return {"ok": false}
			field = admitted.value
			if row.supplied_mesh:
				_check("sharing", row.name + " supplied mesh identity", field.get_mesh(), supplied)
		var mesh: ArrayMesh = field.get_mesh()
		observer.mesh = mesh
		var had_surface: bool = mesh.get_surface_count() != 0
		_check("camera", row.name + " initial surface state", had_surface, row.had_surface)
		if had_surface: mesh.surface_set_material(0, sentinel)
		if row.clear_before: mesh.clear_surfaces()
		var updated: Dictionary = field.update(_vector(row.position), _vector(row.forward))
		_check("camera", row.name + " update admitted", updated.get("ok"), true)
		if not updated.get("ok", false): return {"ok": false}
		_check("camera", row.name + " all 4096 ordered selections", updated.selections, row.selections)
		_check("camera", row.name + " current vertex count", updated.vertex_count, row.state.vertex_count)
		_check("camera", row.name + " current triangle count", updated.triangle_count, row.state.triangle_count)
		_check("camera", row.name + " exact signed 64-bit signature", updated.signature, row.state.signature)
		_check("smoothing", row.name + " stored camera/forward words", _normalize(field.state()), row.state)
		var changed_state: Dictionary = field.state()
		changed_state.signature = 0
		changed_state.smoothed_camera = Vector3(99.0, 98.0, 97.0)
		_check("detachment", row.name + " state dictionary is detached", _normalize(field.state()), row.state)
		_check("sharing", row.name + " update retains same mesh object", field.get_mesh(), mesh)
		_check("sharing", row.name + " node still sees same mesh object", observer.mesh, mesh)
		_check("mesh", row.name + " has one actual surface", mesh.get_surface_count(), 1)
		if mesh.get_surface_count() != 1: return {"ok": false}
		_check("rebuild", row.name + " unchanged signature preserves surface material", mesh.surface_get_material(0) == sentinel, row.kept_sentinel)
		var actual_mesh: Dictionary = _mesh_words_for(mesh)
		for key: String in row.mesh:
			_check("mesh", row.name + " " + key, actual_mesh[key], row.mesh[key])
			if row.mesh[key] is PackedInt32Array: _mesh_words += row.mesh[key].size()
	return {"ok": true, "field": field}


static func _mesh_words_for(mesh: ArrayMesh) -> Dictionary:
	var arrays: Array = mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var uv: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV] if arrays[Mesh.ARRAY_TEX_UV] != null else PackedVector2Array()
	var uv2: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV2] if arrays[Mesh.ARRAY_TEX_UV2] != null else PackedVector2Array()
	return {"surface_count": mesh.get_surface_count(), "primitive": mesh.surface_get_primitive_type(0),
		"vertices": vertices.to_byte_array().to_int32_array(), "uv": uv.to_byte_array().to_int32_array(),
		"uv2": uv2.to_byte_array().to_int32_array(), "indices": arrays[Mesh.ARRAY_INDEX]}


static func _seed_mesh() -> ArrayMesh:
	var arrays: Array = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = PackedVector3Array([Vector3.ZERO, Vector3.RIGHT, Vector3.FORWARD])
	arrays[Mesh.ARRAY_INDEX] = PackedInt32Array([0, 1, 2])
	var result := ArrayMesh.new()
	result.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return result


static func _renderer_metadata(field: HeightField.Field, expected: Dictionary) -> Dictionary:
	# The native API also exposes its admitted Core terrain metadata, which the
	# terrain parity gate owns. Compare every property of the former renderer;
	# no additional Core field is invented in this renderer-only reference.
	var metadata: Dictionary = field.metadata()
	var result: Dictionary = {}
	for key: String in expected: result[key] = _normalize(metadata.get(key))
	return result


static func _normalize(value: Variant) -> Variant:
	if value is Dictionary:
		var result: Dictionary = {}
		for key: Variant in value: result[key] = _normalize(value[key])
		return result
	if typeof(value) == TYPE_FLOAT: return {"float_bits": _word(value)}
	if value is Vector3: return PackedInt32Array([_word(value.x), _word(value.y), _word(value.z)])
	if value is Color: return PackedInt32Array([_word(value.r), _word(value.g), _word(value.b), _word(value.a)])
	return value


func _check(group: String, name: String, actual: Variant, expected: Variant) -> bool:
	_counts[group] = int(_counts.get(group, 0)) + 1
	if actual == expected: return true
	_failures.append({"group": group, "name": name, "difference": _difference(actual, expected)})
	return false


static func _difference(actual: Variant, expected: Variant) -> Dictionary:
	if actual is PackedInt32Array and expected is PackedInt32Array:
		var result: Dictionary = {"actual_length": actual.size(), "expected_length": expected.size()}
		for index: int in range(mini(actual.size(), expected.size())):
			if actual[index] != expected[index]:
				result.merge({"first_index": index, "actual": actual[index], "expected": expected[index]})
				break
		return result
	return {"actual": str(actual).substr(0, 1500), "expected": str(expected).substr(0, 1500)}


func _finish() -> void:
	if _finished: return
	_finished = true
	_check("completion", "every section completed", _completed, ["metadata", "heights", "indices", "meshes", "sharing", "read_only"])
	var output := FileAccess.open(_report, FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify({"schema": 1, "completed": _completed, "failure_count": _failures.size(),
		"counts": _counts, "mesh_words_compared": _mesh_words, "failures": _failures}, "\t"))
	output.close()
	print(JSON.stringify({"counts": _counts, "mesh_words_compared": _mesh_words,
		"failure_count": _failures.size(), "first_failures": _failures.slice(0, 3)}))
	quit(0 if _failures.is_empty() else 1)


static func _word(value: float) -> int:
	var word: int = Float32.store_word(value)
	return word if word < 0x80000000 else word - 0x100000000


static func _float(word: int) -> float:
	return Float32.read_word(word & 0xffffffff)


static func _vector(words: PackedInt32Array) -> Vector3:
	return Vector3(_float(words[0]), _float(words[1]), _float(words[2]))


static func _sha(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	if hash.start(HashingContext.HASH_SHA256) != OK or hash.update(bytes) != OK: return ""
	return hash.finish().hex_encode()


static func _owned_path(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or path.contains("\\") or not path.begins_with(owned + "/"):
		return false
	var directory := DirAccess.open(owned)
	if directory == null: return false
	var parts: PackedStringArray = path.trim_prefix(owned + "/").split("/", false)
	for index: int in range(parts.size()):
		if directory.is_link(parts[index]): return false
		if index < parts.size() - 1 and directory.change_dir(parts[index]) != OK: return false
	return not parts.is_empty()
