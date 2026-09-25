# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Production terrain appearance: one owner for five RGB565 macro caches,
## slot ownership, cloud phase and the actual scene ShaderMaterial. No process,
## input, physics or simulation owner lives here. The host supplies one ordered
## tile batch per draw; every compositor call stays inside GDScript.
const TerrainCompositor = preload("res://Client/terrain_compositor.gd")
const Aya = preload("res://Scenes/Shared/retail_aya_texture.gd")
const Probes = preload("res://Scenes/World/terrain_probes.gd")
const MAP_SIZE: int = 512
const TILE_AXIS: int = 64
const ROOT_TEXTURE_LENGTH: int = 524288
const ROOT_TEXTURE_SHA256: String = "6EB202F450926097930BEDCA440F0163A1886572981E3C69B4EDF9289A68AE2B"
const MATERIAL_PATH: String = "res://Scenes/World/TerrainMaterial.tres"
const CLOUD_SCROLL_RATE_U: float = 0.02
const CLOUD_SCROLL_RATE_V: float = 0.01

var _compositor: RefCounted
var _macro_textures: Array[ImageTexture] = []
var _cache_bytes: Array[PackedByteArray] = []
var _slot_owners: Array[PackedInt32Array] = []
var _occupied_slots: Array[PackedInt32Array] = []
var _material: ShaderMaterial
var _cloud_scroll_u: float = 0.0
var _cloud_scroll_v: float = 0.0
var _admitted: bool = false


## Admission follows the retained Load: root identity, HFLD selectors,
## hierarchy identity, detail decode, cloud decode, constructor/probe choice.
## Assets are only read. A saved material is retained, including its shader
## identity, except for an explicitly selected runtime diagnostic probe.
static func load_paths(root_path: String, hierarchy_path: String, detail_path: String, cloud_path: String,
		facts: Variant, scene_material: ShaderMaterial = null) -> Dictionary:
	if Engine.is_editor_hint():
		return _failure("InvalidOperationException", "Editor inspection uses saved terrain resources and cannot initialize a live cache or probe.")
	var root_bytes: PackedByteArray = _read_bytes(root_path)
	if root_bytes.size() != ROOT_TEXTURE_LENGTH or _hash(root_bytes).to_upper() != ROOT_TEXTURE_SHA256:
		return _failure("InvalidDataException", "Level 100 root terrain texture does not match its retail-derived identity.")
	if facts == null:
		return _failure("NullReferenceException", "Object reference not set to an instance of an object.")
	var valid_facts: Dictionary = _admit_facts(facts)
	if not valid_facts.ok:
		return valid_facts
	if facts.mixer_set != 10 or facts.detail_texture != 0:
		return _failure("InvalidDataException", "Level 100 does not select mixer set 10 and terrain detail texture 00.")
	var composited: Dictionary = TerrainCompositor.from_bytes(_read_bytes(hierarchy_path), facts.sun_color_rgb24, facts.ambient_color_rgb24)
	if not composited.ok:
		return _relay_failure(composited)
	var loader: RefCounted = Aya.new()
	var detail_texture: Texture2D = loader.load_texture(detail_path, 512, 512, Aya.Compression.DXT1)
	if detail_texture == null:
		return _failure("InvalidDataException", loader.error_message)
	var cloud_texture: Texture2D = loader.load_texture(cloud_path, 256, 256, Aya.Compression.DXT1)
	if cloud_texture == null:
		return _failure("InvalidDataException", loader.error_message)
	return _create(composited.value, root_bytes, detail_texture, cloud_texture, facts, scene_material, OS.get_environment("ONSLAUGHT_TERRAIN_PROBE"))


static func _create(compositor: RefCounted, root_bytes: PackedByteArray, detail_texture: Texture2D,
		cloud_texture: Texture2D, facts: Dictionary, scene_material: ShaderMaterial, probe: String) -> Dictionary:
	var owner: RefCounted = new()
	owner._compositor = compositor
	owner._cache_bytes.append(root_bytes)
	owner._slot_owners.append(PackedInt32Array())
	owner._occupied_slots.append(PackedInt32Array())
	var texture: ImageTexture = _create_rgb565_texture(root_bytes)
	if texture == null:
		return _failure("InvalidDataException", "Godot could not create a Level 100 landscape texture.")
	owner._macro_textures.append(texture)
	for level: int in range(1, 5):
		var bytes := PackedByteArray()
		bytes.resize(ROOT_TEXTURE_LENGTH)
		owner._cache_bytes.append(bytes)
		texture = _create_rgb565_texture(bytes)
		if texture == null:
			return _failure("InvalidDataException", "Godot could not create a Level 100 landscape texture.")
		owner._macro_textures.append(texture)
		var tiles_per_axis: int = TILE_AXIS >> level
		var owners := PackedInt32Array()
		owners.resize(tiles_per_axis * tiles_per_axis)
		owners.fill(-1)
		owner._slot_owners.append(owners)
		var occupied := PackedInt32Array()
		occupied.resize(owners.size())
		owner._occupied_slots.append(occupied)
	var selected: Dictionary = Probes.resolve(probe)
	if not selected.ok:
		return selected
	if scene_material == null:
		var template: ShaderMaterial = load(MATERIAL_PATH)
		if template == null:
			return _failure("InvalidDataException", "The production terrain material recipe is missing.")
		owner._material = template.duplicate()
	else:
		owner._material = scene_material
	if selected.active:
		var shader := Shader.new()
		shader.code = selected.code
		owner._material.shader = shader
		print("[terrain-probe] fragment tail overridden: " + selected.mode)
	for level: int in range(5):
		owner._material.set_shader_parameter("macro_map_" + str(level), owner._macro_textures[level])
	owner._material.set_shader_parameter("detail_map", detail_texture)
	owner._material.set_shader_parameter("cloud_shadow_map", cloud_texture)
	var fog: Color = facts.fog_color
	owner._material.set_shader_parameter("fog_color", Vector3(fog.r, fog.g, fog.b))
	owner._material.set_shader_parameter("fog_density", facts.fog_density)
	# SetupLights enables HFLD Sun and AntiSun for the terrain vertex colour;
	# the compositor's separate gradient uses Sun and Ambient instead.
	var diffuse: Dictionary = TerrainCompositor.terrain_vertex_diffuse(
		facts.sun_color_rgb24, facts.anti_sun_color_rgb24)
	if not diffuse.ok:
		return _relay_failure(diffuse)
	owner._material.set_shader_parameter("terrain_vertex_diffuse", Vector3(diffuse.value[0], diffuse.value[1], diffuse.value[2]))
	owner._admitted = true
	return {"ok": true, "value": owner}


func get_material() -> ShaderMaterial:
	return _material


## Explicit ordered records (tile_x,tile_y,texture_level). Null retains the
## original null-list failure after phase/uniform/occupancy mutation. Other
## malformed host representations have no C# typed analogue and fail admission.
func update_tiles(selections: Variant, frame_delta: float) -> Dictionary:
	if not _admitted:
		return _failure("InvalidOperationException", "Terrain appearance has no admitted cache.")
	if selections != null and (typeof(selections) != TYPE_PACKED_INT32_ARRAY or selections.size() % 3 != 0):
		return _failure("ArgumentException", "Terrain selections require ordered Int32 triples.")
	_begin_update(frame_delta)
	if selections == null:
		return _failure("NullReferenceException", "Object reference not set to an instance of an object.")
	var changed: Array[bool] = [false, false, false, false, false]
	for index: int in range(0, selections.size(), 3):
		var selected: Dictionary = _select_tile(selections[index], selections[index + 1], selections[index + 2], changed)
		if not selected.ok:
			return selected
	return _upload_changed(changed)


## Fast production seam: 4096 y-major heightfield records containing
## (geometry_level,texture_level,edge_flags). The original enumeration order
## is retained without reconstructing thousands of managed objects.
func update_heightfield(selections: Variant, frame_delta: float) -> Dictionary:
	if not _admitted:
		return _failure("InvalidOperationException", "Terrain appearance has no admitted cache.")
	if typeof(selections) != TYPE_PACKED_INT32_ARRAY or selections.size() != TILE_AXIS * TILE_AXIS * 3:
		return _failure("ArgumentException", "The heightfield requires exactly 4096 Int32 selection triples.")
	_begin_update(frame_delta)
	var changed: Array[bool] = [false, false, false, false, false]
	for index: int in range(TILE_AXIS * TILE_AXIS):
		var selected: Dictionary = _select_tile(index & 63, index >> 6, selections[index * 3 + 1], changed)
		if not selected.ok:
			return selected
	return _upload_changed(changed)


func _begin_update(frame_delta: float) -> void:
	# These are intentionally binary64 accumulators/rates, then a binary32
	# Vector2 uniform store. No finite/delta clamp or engine TIME is introduced.
	# The measured per-second rates and level-entry origin remain the retained
	# behavior; the original reference/shader records the unresolved residual.
	_cloud_scroll_u = _fract(_cloud_scroll_u + (frame_delta * CLOUD_SCROLL_RATE_U))
	_cloud_scroll_v = _fract(_cloud_scroll_v + (frame_delta * CLOUD_SCROLL_RATE_V))
	_material.set_shader_parameter("terrain_cloud_scroll", Vector2(_cloud_scroll_u, _cloud_scroll_v))
	for level: int in range(1, 5):
		_occupied_slots[level].fill(-1)


func _select_tile(tile_x: int, tile_y: int, level: int, changed: Array[bool]) -> Dictionary:
	if level == 0:
		return {"ok": true}
	if level < 0 or level >= 5:
		return _bounds_failure()
	var tiles_per_axis: int = TILE_AXIS >> level
	var slot_x: int = tile_x & (tiles_per_axis - 1)
	var slot_y: int = tile_y & (tiles_per_axis - 1)
	var slot: int = slot_y * tiles_per_axis + slot_x
	var tile_index: int = _i32(tile_y * TILE_AXIS + tile_x)
	if _occupied_slots[level][slot] >= 0 and _occupied_slots[level][slot] != tile_index:
		return _failure("InvalidDataException", "Level 100 landscape cache " + str(level) + " selected aliased active tiles.")
	_occupied_slots[level][slot] = tile_index
	if _slot_owners[level][slot] == tile_index:
		return {"ok": true}
	var result: Dictionary = _compositor.render_tile(_cache_bytes[level], level, tile_x, tile_y, slot_x, slot_y)
	if not result.ok:
		return _relay_failure(result)
	_slot_owners[level][slot] = tile_index
	changed[level] = true
	return {"ok": true}


func _upload_changed(changed: Array[bool]) -> Dictionary:
	# A failed traversal never uploads. CPU bytes/slot owners from earlier
	# successful tiles deliberately remain mutated, exactly like the reference.
	for level: int in range(1, 5):
		if not changed[level]:
			continue
		var image := Image.create_from_data(MAP_SIZE, MAP_SIZE, false, Image.FORMAT_RGB565, _cache_bytes[level])
		if image.is_empty():
			return _failure("InvalidDataException", "Godot could not update Level 100 landscape cache " + str(level) + ".")
		_macro_textures[level].update(image)
	return {"ok": true}


static func _create_rgb565_texture(bytes: PackedByteArray) -> ImageTexture:
	# CLandscapeTexture's CreateTexture Levels is 1. Anisotropic sampling of
	# that one stored level does not authorize adding a generated mip chain.
	var image := Image.create_from_data(MAP_SIZE, MAP_SIZE, false, Image.FORMAT_RGB565, bytes)
	return null if image.is_empty() else ImageTexture.create_from_image(image)


static func _admit_facts(facts: Variant) -> Dictionary:
	if not facts is Dictionary:
		return _failure("ArgumentException", "Terrain appearance requires HFLD metadata.")
	for key: String in ["mixer_set", "detail_texture", "sun_color_rgb24", "anti_sun_color_rgb24", "ambient_color_rgb24"]:
		if not facts.has(key) or not facts[key] is int or facts[key] < 0 or facts[key] > 0xffffffff:
			return _failure("ArgumentException", "Terrain appearance requires exact unsigned metadata: " + key)
	if not facts.get("fog_color") is Color or not facts.get("fog_density") is float:
		return _failure("ArgumentException", "Terrain appearance requires typed fog metadata.")
	return {"ok": true}


static func _read_bytes(path: String) -> PackedByteArray:
	return FileAccess.get_file_as_bytes(path) if FileAccess.file_exists(path) else PackedByteArray()


static func _fract(value: float) -> float:
	return value - floor(value)


static func _i32(value: int) -> int:
	var word: int = value & 0xffffffff
	return word - 0x100000000 if word >= 0x80000000 else word


static func _hash(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(bytes)
	return hash.finish().hex_encode()


static func _bounds_failure() -> Dictionary:
	return _failure("IndexOutOfRangeException", "Index was outside the bounds of the array.")


static func _relay_failure(result: Dictionary) -> Dictionary:
	# The compositor also serves APIs with named ArgumentException parameters.
	# This owner omits empty metadata, retaining any actual parameter identity.
	var failure: Dictionary = _failure(result.error_type, result.error)
	if not result.get("parameter", "").is_empty():
		failure.parameter = result.parameter
	return failure


static func _failure(type: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": type, "error": message}
