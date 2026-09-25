# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## Admission and geometry for the existing Level 100 water presentation.
## SURF contours are private, fixed retail data. Editing this resource changes
## routing only; it never replaces the measured content identity with an override.
const Terrain = preload("res://Core/terrain.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Words = preload("res://Core/retail_float24.gd")
const SURFACE_PATH: String = "res://Assets/Level100/StaticWorld/Source/level100-water-surface.surf.bin"
const SURFACE_SHA256: String = "c3177354fed3eb5a94dc72debf2465c32ab1d931de79e5e88ac431043d3e917d"
const TERRAIN_PATH: String = "res://../OnslaughtRebuild.Core/Assets/Level100/level100-heightfield.hfld.bin"
const GRID_CELLS: int = 24
const GRID_VERTICES: int = 25
const GRID_START: float = -768.0
const GRID_STEP: float = 64.0
const RADIAL_SCALE: float = 0.0013586956774815917
const SURFACE_RECORDS: int = 515
const SURFACE_SEGMENTS: int = 514
const SURFACE_LENGTH: int = 18572
const RETAIL_DEPTH_BIAS_SCALE: float = 0.00014
const SHORELINE_DEPTH_BIAS_INDEX: int = 4
const SUN_GLINT_DEPTH_BIAS_INDEX: int = 6
const TEXTURES: Dictionary = {
	"reflection_texture": {"file": "water-reflection-00.texture.aya", "size": Vector2i(512, 512), "format": 0, "sha256": "41117238976776b114b8af4d1e4fbccd3afb90245f46f59b353e83663cac7b6e"},
	"caustic_texture": {"file": "water-caustic-00.texture.aya", "size": Vector2i(64, 64), "format": 0, "sha256": "7f34ee7d90ca483893c3ed8b0bf01bdf07b9a0b0f4a48f9df5fefd961d796f0a"},
	"waves_texture": {"file": "water-waves.texture.aya", "size": Vector2i(128, 128), "format": 0, "sha256": "6ec848d1f9801be12f3a6591d6a4f5d5ecf1fc9f21d1a4242e1d681d826ab078"},
	"sun_blob_texture": {"file": "water-sun-blob.texture.aya", "size": Vector2i(128, 128), "format": 2, "sha256": "5d97f24f514383c928c58c7f333bf489888b6a402004213ffbaaaad2ef30a53e"},
	"sun_reflection_texture": {"file": "water-sun-reflection.texture.aya", "size": Vector2i(64, 64), "format": 2, "sha256": "a65940d6cdfe93f8b8820efb883fd33166aec63863ed894673466f3f58527ab4"},
}

@export_file("*.surf.bin") var surface_source: String = SURFACE_PATH


func read_surface(path_override: String = "", expected_sha256: String = SURFACE_SHA256) -> Dictionary:
	var path: String = surface_source if path_override.is_empty() else path_override
	if not FileAccess.file_exists(path):
		return _failure("The locally materialized Level 100 shoreline is missing or changed.")
	return shoreline_from_bytes(FileAccess.get_file_as_bytes(path), expected_sha256)


static func preview_metadata() -> Dictionary:
	# Only the presentation host reads a file. The deterministic terrain owner
	# admits supplied bytes and performs no I/O; no sampler is retained here.
	var path: String = ProjectSettings.globalize_path(TERRAIN_PATH)
	if not FileAccess.file_exists(path):
		return _failure("The retained Level 100 heightfield is missing.")
	return metadata_from_bytes(FileAccess.get_file_as_bytes(path))


static func metadata_from_bytes(source: PackedByteArray) -> Dictionary:
	var admitted: Dictionary = Terrain.from_bytes(source, 100)
	if not admitted.ok:
		return admitted
	return {"ok": true, "value": admitted.value.metadata()}


static func admit_texture(texture: Texture2D, uniform: String) -> Dictionary:
	if texture == null or not TEXTURES.has(uniform):
		return _failure("The water requires all five production texture recipes.")
	var spec: Dictionary = TEXTURES[uniform]
	var path: String = "res://Assets/Level100/StaticWorld/Textures/" + spec.file
	if not FileAccess.file_exists(path) or FileAccess.get_sha256(path) != spec.sha256:
		return _failure("The locally materialized water texture is missing or changed: " + path)
	if texture.has_method("ensure_loaded"):
		if texture.get("source_path") != path or texture.get("dimensions") != spec.size or int(texture.get("compression")) != spec.format:
			return _failure("The water texture recipe differs from its admitted definition: " + uniform)
		return texture.call("ensure_loaded")
	# The temporary host may supply textures already decoded from these same
	# manifest-admitted bytes. It does not become a second geometry/phase owner.
	return {"ok": true}


static func build_grid_mesh() -> ArrayMesh:
	var vertices := PackedVector3Array()
	var colors := PackedColorArray()
	var indices := PackedInt32Array()
	vertices.resize(GRID_VERTICES * GRID_VERTICES)
	colors.resize(vertices.size())
	indices.resize(GRID_CELLS * GRID_CELLS * 6)
	var vertex: int = 0
	for z: int in range(GRID_VERTICES):
		var local_z: float = F.value(GRID_START + F.value(float(z) * GRID_STEP))
		for x: int in range(GRID_VERTICES):
			var local_x: float = F.value(GRID_START + F.value(float(x) * GRID_STEP))
			vertices[vertex] = Vector3(local_x, 0.0, local_z)
			# Vector2.length uses the pinned native float sqrt after float products,
			# matching MathF.Sqrt. MathF.Round uses ties-to-even, not roundf.
			var distance: float = Vector2(local_x, local_z).length()
			var alpha: int = clampi(500 - int(F.round_even(F.value(F.value(distance * F.value(RADIAL_SCALE)) * 500.0))), 0, 255)
			colors[vertex] = Color(1.0, 1.0, 1.0, F.value(float(alpha) / 255.0))
			vertex += 1
	var index: int = 0
	for z: int in range(GRID_CELLS):
		for x: int in range(GRID_CELLS):
			var top_left: int = z * GRID_VERTICES + x
			var bottom_left: int = top_left + GRID_VERTICES
			for item: int in [top_left, bottom_left, top_left + 1, top_left + 1, bottom_left, bottom_left + 1]:
				indices[index] = item
				index += 1
	var mesh := ArrayMesh.new()
	_add_surface(mesh, vertices, colors, PackedVector2Array(), indices)
	return mesh


static func build_sun_glint_mesh() -> ArrayMesh:
	var mesh := ArrayMesh.new()
	_add_surface(mesh, PackedVector3Array([Vector3(-1.0, 0.0, -1.0), Vector3(1.0, 0.0, -1.0), Vector3(-1.0, 0.0, 1.0), Vector3(1.0, 0.0, 1.0)]),
		PackedColorArray([Color.WHITE, Color.WHITE, Color.WHITE, Color.WHITE]),
		PackedVector2Array([Vector2(0.0, 0.0), Vector2(1.0, 0.0), Vector2(0.0, 1.0), Vector2(1.0, 1.0)]), PackedInt32Array([0, 2, 1, 1, 2, 3]))
	return mesh


static func shoreline_from_bytes(source: PackedByteArray, expected_sha256: String = SURFACE_SHA256) -> Dictionary:
	# The public production recipe never admits a caller-replaced hash. It
	# preserves the existing outer hash failure before inspecting chunk fields.
	if source.size() != SURFACE_LENGTH or expected_sha256.to_lower() != SURFACE_SHA256 or _hash(source) != SURFACE_SHA256:
		return _failure("The locally materialized Level 100 shoreline is missing or changed.")
	if not _chunk(source, 0, "SURF", SURFACE_LENGTH - 8) or not _chunk(source, 8, "SURF", SURFACE_LENGTH - 16):
		return _failure("Level 100 shoreline has invalid chunk framing.")
	if source.decode_s32(16) != 1:
		return _failure("Level 100 has an unsupported shoreline array count.")
	if not _chunk(source, 20, "OUTL", SURFACE_LENGTH - 28):
		return _failure("Level 100 shoreline has invalid chunk framing.")
	if source.decode_s32(28) != SURFACE_SEGMENTS or source.size() != 32 + SURFACE_RECORDS * 9 * 4:
		return _failure("Level 100 has an unsupported shoreline contour count.")
	var contours: Array[PackedVector3Array] = [PackedVector3Array(), PackedVector3Array(), PackedVector3Array()]
	for contour: int in range(3):
		contours[contour].resize(SURFACE_RECORDS)
	var offset: int = 32
	for point: int in range(SURFACE_RECORDS):
		for contour: int in range(3):
			var retail_x: float = source.decode_float(offset)
			var retail_y: float = source.decode_float(offset + 4)
			var retail_z: float = source.decode_float(offset + 8)
			if not is_finite(retail_x) or not is_finite(retail_y) or source.decode_u32(offset + 8) != 0xc10d70a4:
				return _failure("Level 100 shoreline contains an invalid point.")
			offset += 12
			contours[contour][point] = Vector3(F.value(retail_x - 288.6875), F.value(-10.0 - retail_z), F.value(243.25 - retail_y))
	var mesh := ArrayMesh.new()
	_add_shoreline_band(mesh, contours, 0, 1, true)
	_add_shoreline_band(mesh, contours, 1, 2, false)
	return {"ok": true, "value": mesh}


static func _add_shoreline_band(mesh: ArrayMesh, contours: Array[PackedVector3Array], first_contour: int, second_contour: int, inner_band: bool) -> void:
	var vertices := PackedVector3Array()
	var colors := PackedColorArray()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	vertices.resize(SURFACE_RECORDS * 2)
	colors.resize(vertices.size())
	uvs.resize(vertices.size())
	indices.resize(SURFACE_SEGMENTS * 6)
	for point: int in range(SURFACE_RECORDS):
		var phase: float = F.value(float(point) * 0.125)
		# Native float sin, as already gated by HUD/render interpolation. Casting
		# GDScript's double sin result afterward is observably different.
		var wave: float = F.value(Vector2.from_angle(F.value(phase * 0.5)).y * 0.5)
		var first: int = point * 2
		var second: int = first + 1
		vertices[first] = contours[first_contour][point]
		vertices[second] = contours[second_contour][point]
		if inner_band:
			colors[first] = Color(1.0, 1.0, 1.0, 0.0)
			colors[second] = Color(1.0, 1.0, 1.0, F.value(192.0 / 255.0))
			uvs[first] = Vector2(phase, F.value(F.value(wave - 0.25) - F.value(phase * 0.25)))
			uvs[second] = Vector2(phase, F.value(wave - F.value(phase * 0.25)))
		else:
			colors[first] = Color(1.0, 1.0, 1.0, F.value(192.0 / 255.0))
			colors[second] = Color(0.0, 0.0, 0.0, 1.0)
			uvs[first] = Vector2(phase, F.value(wave - F.value(phase * 0.25)))
			uvs[second] = Vector2(F.value(phase + 0.0625), F.value(F.value(wave + 2.0) - F.value(phase * 0.25)))
	var index: int = 0
	for segment: int in range(SURFACE_SEGMENTS):
		var first: int = segment * 2
		for item: int in [first, first + 1, first + 2, first + 2, first + 1, first + 3]:
			indices[index] = item
			index += 1
	_add_surface(mesh, vertices, colors, uvs, indices)


static func _add_surface(mesh: ArrayMesh, vertices: PackedVector3Array, colors: PackedColorArray, uvs: PackedVector2Array, indices: PackedInt32Array) -> void:
	var arrays: Array = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_COLOR] = colors
	if not uvs.is_empty():
		arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = indices
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)


static func _chunk(source: PackedByteArray, offset: int, tag: String, length: int) -> bool:
	return source.slice(offset, offset + 4) == tag.to_ascii_buffer() and source.decode_s32(offset + 4) == length


static func _hash(source: PackedByteArray) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(source)
	return hash.finish().hex_encode()


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
