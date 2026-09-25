# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Terrain = preload("res://Core/terrain.gd")
const Float32 = preload("res://Core/retail_float24.gd")
var _counts: Dictionary = {}
var _failures: Array[Dictionary] = []


func _initialize() -> void:
	_run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	_counts[group] = int(_counts.get(group, 0)) + 1
	if actual != expected:
		_failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var root: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not root is Dictionary or not root.get("terrain") is Dictionary:
		push_error("Missing terrain oracle.")
		quit(2)
		return
	var data: Dictionary = root.terrain
	if not _constants(data.constants) or not _numeric_helpers(data):
		push_error("Terrain helper checks did not complete.")
		quit(2)
		return
	_check("coverage", "all retained world inputs", data.worlds.size(), 4)
	var ids: Array[int] = []
	for world: Dictionary in data.worlds:
		ids.append(int(world.id))
		if not _world(world):
			push_error("Terrain world checks did not complete.")
			quit(2)
			return
	_check("coverage", "world order", ids, [100, 110, 200, 300])
	for bad: Variant in [null, false, true, 0, 0.0, "bytes", [], {}]:
		_check("admission", "byte carrier", Terrain.from_bytes(bad).get("error_type"), "ArgumentException")
	for bad: Variant in [null, false, true, 100.0, "100", [], {}, -1, 0, 101, 2147483648]:
		_check("admission", "pinned world selection", Terrain.from_bytes(PackedByteArray(), bad).get("error_type"), "ArgumentOutOfRangeException")
	var report: Dictionary = {"schema": 1, "failure_count": _failures.size(), "counts": _counts,
		"completed": ["terrain"], "failures": _failures}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": _counts, "failure_count": _failures.size(), "first_failures": _failures.slice(0, 3)}))
	quit(0 if _failures.is_empty() else 1)


func _constants(expected: Dictionary) -> bool:
	var script: GDScript = Terrain
	var constants: Dictionary = script.get_script_constant_map()
	for key: String in expected:
		_check("constants", key, constants.get(key), _integers(expected[key]))
	return true


func _numeric_helpers(data: Dictionary) -> bool:
	_check("coverage", "scale word fixtures", data.scales.size(), 2048)
	for row: Dictionary in data.scales:
		var decoded: Dictionary = Terrain._decode_positive_float_scale(int(row.bits))
		var actual: Dictionary = decoded.duplicate()
		if decoded.ok:
			actual = {"ok": true, "value": {"significand": decoded.significand, "denominator": str(decoded.denominator)}}
		_result("scale", str(int(row.bits)), actual, row.result)
	for row: Dictionary in data.divisions:
		var value: int = int(row.value)
		var denominator: int = int(row.denominator)
		_check("integer", row.value + "/" + row.denominator + " floor", str(Terrain.Heightfield._floor_divide(value, denominator)), row.floor)
		_check("integer", row.value + "/" + row.denominator + " away", str(Terrain.Heightfield._round_divide_away(value, denominator)), row.away)
	return true


func _world(world: Dictionary) -> bool:
	var name: String = str(int(world.id))
	var source: PackedByteArray = FileAccess.get_file_as_bytes(world.path)
	var before: String = _sha(source)
	_check("read_only", name + " supplied input pin", before, world.metadata.payload_sha256)
	var loaded: Dictionary = Terrain.from_bytes(source, int(world.id))
	_check("admission", name + " actual input", loaded.get("ok"), true)
	if not loaded.get("ok", false):
		return true
	var owner: Terrain.Heightfield = loaded.value
	_check("metadata", name + " exact CHFD words", owner.metadata(), _integers(world.metadata))
	_check("coverage", name + " scalar fixtures", world.calls.size() > 4000, true)
	for index: int in range(world.calls.size()):
		var row: Dictionary = world.calls[index]
		_result("sampling", name + ":" + str(index) + ":" + row.operation, _invoke(owner, row.operation, int(row.x), int(row.y)), row.result)

	var grid: PackedInt32Array = owner.grid_height_units()
	_check("full_grid", name + " 513 squared samples", grid.size(), 513 * 513)
	_check("full_grid", name + " signed little-endian words", _hash_ints(grid), world.full_grid_sha256)
	var fixed: Dictionary = owner.fixed_height_units_grid(137, 199)
	_check("full_fixed", name + " subcell grid admission", fixed.get("ok"), true)
	if fixed.get("ok", false):
		_check("full_fixed", name + " 512 squared samples", fixed.value.size(), 512 * 512)
		_check("full_fixed", name + " two-axis interpolation words", _hash_ints(fixed.value), world.fixed_grid_sha256)
	var complexities: PackedFloat32Array = owner.tile_complexity_scores()
	_check("full_lod", name + " 64 squared patches", complexities.size(), 64 * 64)
	_check("full_lod", name + " explicit float32 words", _hash_floats(complexities), world.lod_sha256)

	var original_grid: Dictionary = owner.sample_grid_height_units(0, 0)
	grid[0] = grid[0] + 123
	_check("detachment", name + " edited grid result", owner.sample_grid_height_units(0, 0), original_grid)
	var original_score: Dictionary = owner.get_tile_complexity_score(0, 0)
	complexities[0] = 999.0
	_check("detachment", name + " edited complexity result", owner.get_tile_complexity_score(0, 0), original_score)
	var metadata: Dictionary = owner.metadata()
	metadata.height_scale_bits = 0
	metadata.world_id = -1
	metadata["added"] = ["caller"]
	_check("detachment", name + " edited metadata result", owner.metadata(), _integers(world.metadata))
	# Mutating the caller's original byte array after successful admission cannot
	# change the signed samples held by the deterministic owner.
	source[5108] ^= 255
	_check("detachment", name + " edited caller bytes", owner.sample_grid_height_units(0, 0), original_grid)
	source[5108] ^= 255
	_check("detachment", name + " restored local byte carrier", _sha(source), before)

	for index: int in range(world.admission.size()):
		var row: Dictionary = world.admission[index]
		var candidate: PackedByteArray = source.duplicate()
		var selected_world: int = int(world.id)
		match row.kind:
			"resize": candidate.resize(int(row.size))
			"flip": candidate[int(row.offset)] ^= 1
			"other_world": selected_world = int(row.world_id)
			_:
				_check("admission", name + " known corruption instruction", row.kind, "resize/flip/other_world")
				return false
		_result("admission", name + ":" + str(index) + ":" + row.kind, Terrain.from_bytes(candidate, selected_world), row.result)
	if not _host_admission(owner, name):
		return false
	_check("read_only", name + " source unchanged after all checks", _sha(FileAccess.get_file_as_bytes(world.path)), before)
	return true


func _host_admission(owner: Terrain.Heightfield, world: String) -> bool:
	for bad: Variant in [null, false, true, 0.0, "0", [], {}, -2147483649, 2147483648]:
		for operation: String in ["fixed", "grid", "air_guide", "complexity", "coordinates", "ground", "ground_fixed", "gradient"]:
			_check("host_admission", world + ":" + operation + " X carrier", _invoke(owner, operation, bad, 0).get("error_type"), "ArgumentException")
			_check("host_admission", world + ":" + operation + " Y carrier", _invoke(owner, operation, 0, bad).get("error_type"), "ArgumentException")
		_check("host_admission", world + " batch X carrier", owner.fixed_height_units_grid(bad, 0).get("error_type"), "ArgumentException")
		_check("host_admission", world + " batch Y carrier", owner.fixed_height_units_grid(0, bad).get("error_type"), "ArgumentException")
	for edge: int in [-1, 256]:
		_check("host_admission", world + " batch X range", owner.fixed_height_units_grid(edge, 0).get("parameter"), "fraction_x")
		_check("host_admission", world + " batch Y range", owner.fixed_height_units_grid(0, edge).get("parameter"), "fraction_y")
	return true


func _invoke(owner: Terrain.Heightfield, operation: String, x: Variant, y: Variant) -> Dictionary:
	match operation:
		"fixed": return owner.sample_height_units_at_fixed(x, y)
		"grid": return owner.sample_grid_height_units(x, y)
		"air_guide": return owner.sample_air_guide_height_units(x, y)
		"coordinates": return owner.get_retail_fixed_coordinates(x, y)
		"ground": return owner.sample_ground_elevation_millimeters(x, y)
		"ground_fixed": return owner.sample_ground_elevation_millimeters_at_fixed(x, y)
		"gradient": return owner.sample_ground_gradient_permille(x, y)
		"complexity":
			var result: Dictionary = owner.get_tile_complexity_score(x, y)
			return {"ok": true, "value": Float32.store_word(result.value)} if result.get("ok", false) else result
	return {"ok": false, "error_type": "UnknownOracleOperation", "parameter": ""}


func _result(group: String, name: String, actual: Dictionary, expected: Dictionary) -> void:
	_check(group, name + " admission", actual.get("ok"), expected.ok)
	if actual.get("ok", false) and expected.ok:
		_check(group, name + " value", actual.get("value"), _integers(expected.value))
	elif not actual.get("ok", false) and not expected.ok:
		_check(group, name + " failure type", actual.get("error_type"), expected.error_type)
		_check(group, name + " first parameter", actual.get("parameter", ""), expected.get("parameter", ""))
		if expected.has("error"):
			_check(group, name + " failure text", actual.get("error"), expected.error)


func _integers(value: Variant) -> Variant:
	if typeof(value) == TYPE_FLOAT:
		return int(value)
	if value is Dictionary:
		var result: Dictionary = {}
		for key: String in value:
			result[key] = _integers(value[key])
		return result
	if value is Array:
		var result: Array = []
		for item: Variant in value:
			result.append(_integers(item))
		return result
	return value


func _hash_ints(values: PackedInt32Array) -> String:
	var bytes := PackedByteArray()
	bytes.resize(values.size() * 4)
	for index: int in range(values.size()):
		bytes.encode_s32(index * 4, values[index])
	return _sha(bytes)


func _hash_floats(values: PackedFloat32Array) -> String:
	var bytes := PackedByteArray()
	bytes.resize(values.size() * 4)
	for index: int in range(values.size()):
		bytes.encode_u32(index * 4, Float32.store_word(values[index]))
	return _sha(bytes)


func _sha(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	if hash.start(HashingContext.HASH_SHA256) != OK or hash.update(bytes) != OK:
		push_error("Terrain check could not hash bytes.")
		return ""
	return hash.finish().hex_encode().to_upper()
