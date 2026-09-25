# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Production Level 100 terrain presentation. The caller supplies the pinned
## HFLD once and, when binding an imported scene, its actual mutable ArrayMesh.
## No file access, scene tree, process/input callback, physics or simulation
## owner lives here. The retained C# reference records the original renderer.
const Terrain = preload("res://Core/terrain.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Words = preload("res://Core/retail_float24.gd")
const TILE_AXIS: int = 64
const TILE_COUNT: int = TILE_AXIS * TILE_AXIS
const TILE_WIDTH: int = 8
const PLAYER_X: float = float(Terrain.PLAYER_START_RETAIL_X_FIXED) / 256.0
const PLAYER_Z: float = float(Terrain.PLAYER_START_RETAIL_Y_FIXED) / 256.0
const PLAYER_ELEVATION: float = float(Terrain.PLAYER_START_REFERENCE_ELEVATION_MILLIMETERS) / 1000.0
const ROOT_LEVEL: int = -1
const CAMERA_SMOOTHING: float = 0.03
const STITCH_TOP: int = 1
const STITCH_RIGHT: int = 2
const STITCH_BOTTOM: int = 4
const STITCH_LEFT: int = 8
const SIGNATURE_OFFSET: int = -3750763034362895579 # FNV64 offset, same raw unsigned word.
const SIGNATURE_PRIME: int = 1099511628211


static func from_bytes(source: PackedByteArray, mesh: ArrayMesh = null) -> Dictionary:
	var admitted: Dictionary = Terrain.from_bytes(source)
	if not admitted.ok:
		return admitted
	return {"ok": true, "value": Field.new(admitted.value, mesh)}


static func tile_indices(geometry_level: int, edge_flags: int) -> PackedInt32Array:
	return Field._tile_indices(geometry_level, edge_flags)


class Field extends RefCounted:
	var _terrain: Terrain.Heightfield
	var _mesh: ArrayMesh
	var _metadata: Dictionary
	var _height_scale: float
	var _tile_complexity: PackedFloat32Array
	var _tile_mid_height := PackedFloat32Array()
	var _geometry_levels := PackedInt32Array()
	var _texture_levels := PackedInt32Array()
	var _edge_flags := PackedInt32Array()
	var _selections := PackedInt32Array()
	var _index_variants: Array[PackedInt32Array] = []
	var _root_indices: PackedInt32Array
	var _tile_vertices: Array[PackedVector3Array] = []
	var _tile_uv: Array[PackedVector2Array] = []
	var _level_uv: Array[PackedVector2Array] = []
	var _has_smoothed_camera: bool = false
	var _smoothed_camera: Vector3
	var _smoothed_forward: Vector3
	var _mesh_signature: int = 0
	var _vertex_count: int = 0
	var _triangle_count: int = 0


	func _init(terrain: Terrain.Heightfield, mesh: ArrayMesh) -> void:
		_terrain = terrain
		_mesh = ArrayMesh.new() if mesh == null else mesh
		_metadata = terrain.metadata()
		_metadata.player_start_x = PLAYER_X
		_metadata.player_start_z = PLAYER_Z
		_metadata.player_start_elevation = PLAYER_ELEVATION
		_height_scale = Words.read_word(_metadata.height_scale_bits)
		_metadata.water_level = Words.read_word(_metadata.water_level_bits)
		_metadata.water_relative_height = F.value(PLAYER_ELEVATION - _metadata.water_level)
		_metadata.fog_color = _color(_metadata.fog_color_rgb24)
		_metadata.fog_density = Words.read_word(_metadata.fog_density_bits)
		_metadata.sun_color = _color(_metadata.sun_color_rgb24)
		_metadata.anti_sun_color = _color(_metadata.anti_sun_color_rgb24)
		_metadata.ambient_color = _color(_metadata.ambient_color_rgb24)
		var sun := Vector3(Words.read_word(_metadata.sun_position_x_bits),
			Words.read_word(_metadata.sun_position_y_bits), Words.read_word(_metadata.sun_position_z_bits))
		_metadata.sun_position = sun
		var light: Vector3 = -sun.normalized()
		_metadata.sunlight_direction = Vector3(light.x, -light.z, -light.y)
		# The binary kernel returns x-major samples. Presentation traverses y/x.
		var complexity: PackedFloat32Array = terrain.tile_complexity_scores()
		_tile_complexity = PackedFloat32Array()
		_tile_complexity.resize(TILE_COUNT)
		_tile_mid_height.resize(TILE_COUNT)
		_geometry_levels.resize(TILE_COUNT)
		_texture_levels.resize(TILE_COUNT)
		_edge_flags.resize(TILE_COUNT)
		_selections.resize(TILE_COUNT * 3)
		_tile_vertices.resize(TILE_COUNT * 4)
		_tile_uv.resize(TILE_COUNT * 4)
		_level_uv.resize(4 * 5)
		for tile_y: int in range(TILE_AXIS):
			for tile_x: int in range(TILE_AXIS):
				_tile_complexity[tile_y * TILE_AXIS + tile_x] = complexity[tile_x * TILE_AXIS + tile_y]
				var minimum: int = 2147483647
				var maximum: int = -2147483648
				for local_y: int in range(TILE_WIDTH + 1):
					for local_x: int in range(TILE_WIDTH + 1):
						var sample: int = terrain._grid_height_units_admitted(tile_x * TILE_WIDTH + local_x, tile_y * TILE_WIDTH + local_y)
						minimum = mini(minimum, sample)
						maximum = maxi(maximum, sample)
				_tile_mid_height[tile_y * TILE_AXIS + tile_x] = F.value(F.value(float(minimum + maximum) * 0.5) * _height_scale)
		_root_indices = _tile_indices(ROOT_LEVEL, 0)
		for level: int in range(3):
			for flags: int in range(16):
				_index_variants.append(_tile_indices(level, flags))


	func metadata() -> Dictionary:
		return _metadata.duplicate(true)


	func get_mesh() -> ArrayMesh:
		return _mesh


	func state() -> Dictionary:
		return {"has_smoothed_camera": _has_smoothed_camera, "smoothed_camera": _smoothed_camera,
			"smoothed_forward": _smoothed_forward, "signature": _mesh_signature,
			"vertex_count": _vertex_count, "triangle_count": _triangle_count}


	func sample_relative_height(relative_x: float, relative_z: float) -> float:
		var x: float = F.value(F.value(relative_x) + PLAYER_X)
		var z: float = F.value(F.value(relative_z) + PLAYER_Z)
		var units: int = _terrain._fixed_height_units_admitted(_fixed_coordinate(x), _fixed_coordinate(z))
		return F.value(PLAYER_ELEVATION - F.value(float(units) * _height_scale))


	func update(camera_position: Vector3, camera_forward: Vector3) -> Dictionary:
		var retail_camera := Vector3(F.value(camera_position.x + PLAYER_X), F.value(PLAYER_Z - camera_position.z),
			F.value(PLAYER_ELEVATION - camera_position.y))
		var retail_forward := Vector3(camera_forward.x, -camera_forward.z, -camera_forward.y)
		if not _has_smoothed_camera:
			_smoothed_camera = retail_camera
			_smoothed_forward = retail_forward
			_has_smoothed_camera = true
		else:
			_smoothed_camera = _lerp(_smoothed_camera, retail_camera)
			_smoothed_forward = _lerp(_smoothed_forward, retail_forward)
		_select_tiles()
		var signature: int = _signature()
		if signature != _mesh_signature or _mesh.get_surface_count() == 0:
			_build_selected_mesh()
			_mesh_signature = signature
		return {"ok": true, "selections": _selections.duplicate(), "signature": _mesh_signature,
			"vertex_count": _vertex_count, "triangle_count": _triangle_count}


	func _select_tiles() -> void:
		for tile_y: int in range(TILE_AXIS):
			for tile_x: int in range(TILE_AXIS):
				var index: int = tile_y * TILE_AXIS + tile_x
				var x: float = F.value(float(tile_x * TILE_WIDTH + 4) - _smoothed_camera.x)
				var y: float = F.value(float(tile_y * TILE_WIDTH + 4) - _smoothed_camera.y)
				var height: float = F.value(_tile_mid_height[index] - _smoothed_camera.z)
				var distance: float = F.value(F.value(F.value(x * x) + F.value(y * y)) + F.value(height * height))
				var projected_size: float = 8.0
				if distance >= 1024.0:
					projected_size = F.value(F.value(256.0 + _tile_complexity[index]) / F.value(sqrt(distance)))
				var rounded_size: int = clampi(_host_int32(F.round_even(projected_size)), 0, 8)
				var level: int = ROOT_LEVEL if rounded_size <= 1 else (0 if rounded_size <= 3 else (1 if rounded_size <= 7 else 2))
				_geometry_levels[index] = level
				_texture_levels[index] = 0 if level == ROOT_LEVEL else _select_texture_level(x, y, height, distance)
		_edge_flags.fill(0)
		for tile_y: int in range(TILE_AXIS):
			for tile_x: int in range(TILE_AXIS):
				var index: int = tile_y * TILE_AXIS + tile_x
				var level: int = _geometry_levels[index]
				if level == ROOT_LEVEL:
					continue
				var flags: int = 0
				if tile_y > 0 and _geometry_levels[index - TILE_AXIS] < level:
					flags |= STITCH_TOP
				if tile_x + 1 < TILE_AXIS and _geometry_levels[index + 1] < level:
					flags |= STITCH_RIGHT
				if tile_y + 1 < TILE_AXIS and _geometry_levels[index + TILE_AXIS] < level:
					flags |= STITCH_BOTTOM
				if tile_x > 0 and _geometry_levels[index - 1] < level:
					flags |= STITCH_LEFT
				_edge_flags[index] = flags
		for index: int in range(TILE_COUNT):
			_selections[index * 3] = _geometry_levels[index]
			_selections[index * 3 + 1] = _texture_levels[index]
			_selections[index * 3 + 2] = _edge_flags[index]


	func _select_texture_level(x: float, y: float, height: float, distance: float) -> int:
		if distance > 16384.0:
			return 0
		var vertical: float = F.value(F.value(height * height) - 64.0)
		if not is_nan(vertical):
			vertical = maxf(vertical, 0.0)
		if _shifted_distance(x, y, vertical, 60.0) >= 4096.0:
			return 1
		if _shifted_distance(x, y, vertical, 28.0) >= 1024.0:
			return 2
		if _shifted_distance(x, y, vertical, 12.0) >= 256.0:
			return 3
		return 4


	func _shifted_distance(x: float, y: float, vertical: float, forward_distance: float) -> float:
		var shifted_x: float = F.value(x - F.value(_smoothed_forward.x * forward_distance))
		var shifted_y: float = F.value(y - F.value(_smoothed_forward.y * forward_distance))
		return F.value(F.value(F.value(shifted_x * shifted_x) + F.value(shifted_y * shifted_y)) + vertical)


	func _signature() -> int:
		var result: int = SIGNATURE_OFFSET
		for index: int in range(TILE_COUNT):
			result = (result ^ (_geometry_levels[index] + 1)) * SIGNATURE_PRIME
			result = (result ^ _texture_levels[index]) * SIGNATURE_PRIME
			result = (result ^ _edge_flags[index]) * SIGNATURE_PRIME
		return result


	func _build_selected_mesh() -> void:
		var vertices := PackedVector3Array()
		var texture_coordinates := PackedVector2Array()
		var texture_levels := PackedVector2Array()
		var indices := PackedInt32Array()
		for tile: int in range(TILE_COUNT):
			var level: int = _geometry_levels[tile]
			var base_vertex: int = vertices.size()
			# The admitted terrain is immutable. Cache each tile/geometry level
			# lazily, then append the same words in the original traversal order.
			var cache_index: int = tile * 4 + level + 1
			if _tile_vertices[cache_index].is_empty():
				_cache_tile(tile, level, cache_index)
			vertices.append_array(_tile_vertices[cache_index])
			texture_coordinates.append_array(_tile_uv[cache_index])
			var texture_index: int = (level + 1) * 5 + _texture_levels[tile]
			if _level_uv[texture_index].is_empty():
				var values := PackedVector2Array()
				values.resize(_tile_vertices[cache_index].size())
				values.fill(Vector2(_texture_levels[tile], 0.0))
				_level_uv[texture_index] = values
			texture_levels.append_array(_level_uv[texture_index])
			var local_indices: PackedInt32Array = _root_indices if level == ROOT_LEVEL else _index_variants[level * 16 + _edge_flags[tile]]
			for local_index: int in local_indices:
				indices.append(base_vertex + local_index)
		var arrays: Array = []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = vertices
		arrays[Mesh.ARRAY_TEX_UV] = texture_coordinates
		arrays[Mesh.ARRAY_TEX_UV2] = texture_levels
		arrays[Mesh.ARRAY_INDEX] = indices
		_mesh.clear_surfaces()
		_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		_vertex_count = vertices.size()
		_triangle_count = indices.size() / 3


	func _cache_tile(tile: int, level: int, cache_index: int) -> void:
		var step: int = TILE_WIDTH if level == ROOT_LEVEL else (4 >> level)
		var cell_count: int = TILE_WIDTH / step
		var origin_x: int = (tile % TILE_AXIS) * TILE_WIDTH
		var origin_y: int = (tile / TILE_AXIS) * TILE_WIDTH
		var vertices := PackedVector3Array()
		var uv := PackedVector2Array()
		for local_y: int in range(cell_count + 1):
			var retail_y: int = origin_y + local_y * step
			for local_x: int in range(cell_count + 1):
				var retail_x: int = origin_x + local_x * step
				var height: float = F.value(PLAYER_ELEVATION - F.value(float(_terrain._grid_height_units_admitted(retail_x, retail_y)) * _height_scale))
				vertices.append(Vector3(float(retail_x) - PLAYER_X, height, PLAYER_Z - float(retail_y)))
				uv.append(Vector2(retail_x, retail_y))
		_tile_vertices[cache_index] = vertices
		_tile_uv[cache_index] = uv


	## CLandscapeIB top/right/bottom/left stitching, with degenerate triangles
	## removed in original traversal order. This is geometry, not Godot physics.
	static func _tile_indices(geometry_level: int, edge_flags: int) -> PackedInt32Array:
		var cell_count: int = 1 if geometry_level == ROOT_LEVEL else (2 << geometry_level)
		var flags: int = 0 if geometry_level == ROOT_LEVEL else edge_flags
		var vertex_axis: int = cell_count + 1
		var working := PackedInt32Array()
		working.resize(cell_count * cell_count * 6)
		var write: int = 0
		for local_y: int in range(cell_count):
			for local_x: int in range(cell_count):
				var top_left: int = local_y * vertex_axis + local_x
				var bottom_left: int = top_left + vertex_axis
				var bottom_right: int = bottom_left + 1
				working[write] = top_left
				working[write + 1] = bottom_left
				working[write + 2] = bottom_right
				working[write + 3] = top_left
				working[write + 4] = bottom_right
				working[write + 5] = top_left + 1
				write += 6
		if flags & STITCH_TOP:
			var cursor: int = 6
			for pair: int in range(cell_count / 2):
				working[cursor - 1] += 1
				working[cursor] += 1
				_clear_triangle(working, cursor + 3)
				cursor += 12
		if flags & STITCH_RIGHT:
			var cursor: int = cell_count * 6 - 6
			for pair: int in range(cell_count / 2):
				working[cursor + 2] -= vertex_axis
				working[cursor + cell_count * 6 + 5] -= vertex_axis
				_clear_triangle(working, cursor + 3)
				cursor += cell_count * 12
			if flags & STITCH_TOP:
				_clear_triangle(working, cell_count * 6 - 6)
		if flags & STITCH_LEFT:
			var cursor: int = 0
			for pair: int in range(cell_count / 2):
				working[cursor + 1] += vertex_axis
				working[cursor + cell_count * 6 + 3] += vertex_axis
				_clear_triangle(working, cursor + cell_count * 6)
				cursor += cell_count * 12
		if flags & STITCH_BOTTOM:
			var cursor: int = (cell_count - 1) * cell_count * 6
			for pair: int in range(cell_count / 2):
				working[cursor + 4] -= 1
				working[cursor + 7] -= 1
				_clear_triangle(working, cursor)
				cursor += 12
			if flags & STITCH_LEFT:
				_clear_triangle(working, (cell_count - 1) * cell_count * 6 + 3)
		var result := PackedInt32Array()
		for index: int in range(0, working.size(), 3):
			if working[index] == 0 and working[index + 1] == 0 and working[index + 2] == 0:
				continue
			result.append(working[index])
			result.append(working[index + 1])
			result.append(working[index + 2])
		return result


	static func _clear_triangle(indices: PackedInt32Array, start: int) -> void:
		indices[start] = 0
		indices[start + 1] = 0
		indices[start + 2] = 0


	static func _fixed_coordinate(coordinate: float) -> int:
		# Preserve actual Godot-hosted C# NaN -> Int32 zero (also checked by Sun).
		if is_nan(coordinate):
			return 0
		return int(floor(F.value(clampf(coordinate, 0.0, Words.read_word(0x43ffffff)) * 256.0)))


	static func _host_int32(number: float) -> int:
		if is_nan(number):
			return 0
		if number >= 2147483648.0:
			return 2147483647
		if number <= -2147483648.0:
			return -2147483648
		return int(number)


	static func _lerp(left: Vector3, right: Vector3) -> Vector3:
		var weight: float = F.value(CAMERA_SMOOTHING)
		return Vector3(F.value(left.x + F.value(F.value(right.x - left.x) * weight)),
			F.value(left.y + F.value(F.value(right.y - left.y) * weight)),
			F.value(left.z + F.value(F.value(right.z - left.z) * weight)))


	static func _color(rgb: int) -> Color:
		return Color(F.value(float((rgb >> 16) & 255) / 255.0),
			F.value(float((rgb >> 8) & 255) / 255.0), F.value(float(rgb & 255) / 255.0))
