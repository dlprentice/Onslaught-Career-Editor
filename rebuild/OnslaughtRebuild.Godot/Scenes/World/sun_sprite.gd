# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends MeshInstance3D
## Production Sun Sprite, shared by the private importer, editor and gameplay.
## Placement retains DXEngine.cpp:975,1043-1064: camera + raw sun * 0.6.
## LOS retains the current terrain-only 200 m/2 m march. It does not recover
## VisibleSun, object occlusion or unresolved particle interpolation behavior.
const Terrain = preload("res://Core/terrain.gd")
const Resolver = preload("res://Client/particle_effect_resolver.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Recipe = preload("res://Scenes/World/sun_recipe.gd")
const SCALE: float = 0.6
const LINE_OF_SIGHT: float = 200.0
const STEP: float = 2.0
const MAX_COORDINATE_BITS: int = 0x43ffffff

@export var particle_recipe: Resource
@export var base_material: StandardMaterial3D

var _terrain: RefCounted
var _layer: Dictionary = {}
var _offset: Vector3
var _direction: Vector3
var _height_scale: float
var _private_bake: bool = false
var _preview_error: String = ""


func _ready() -> void:
	set_process(false)
	if Engine.is_editor_hint() and (mesh == null or material_override == null):
		var result: Dictionary = prepare_visual(false)
		_preview_error = "" if result.ok else result.error
		update_configuration_warnings()


func _get_configuration_warnings() -> PackedStringArray:
	return PackedStringArray() if _preview_error.is_empty() else PackedStringArray([_preview_error])


func _validate_property(property: Dictionary) -> void:
	# Public editor saves retain the recipe/template, never derived material or
	# texture bytes. Only the explicit private importer enables their storage.
	if property.name in ["mesh", "material_override"] and not _private_bake \
			and not scene_file_path.begins_with("res://Assets/Level100/Scenes/"):
		property.usage = int(property.usage) & ~PROPERTY_USAGE_STORAGE


func prepare_visual(retain_saved: bool) -> Dictionary:
	if particle_recipe == null or particle_recipe.get_script() != Recipe:
		return _failure("The sun requires its authored source recipe.")
	var resolved: Dictionary = particle_recipe.read_layer()
	if not resolved.ok:
		return resolved
	var colour: Dictionary = constant_colour(resolved.value)
	if not colour.ok:
		return colour
	_layer = resolved.value
	if retain_saved:
		if mesh == null or material_override == null:
			return _failure("The imported sun has no saved mesh/material.")
		return {"ok": true}
	if base_material == null or base_material.albedo_texture == null:
		return _failure("The sun requires its production material/texture recipe.")
	var texture: Texture2D = base_material.albedo_texture
	if not texture.has_method("ensure_loaded"):
		return _failure("The sun texture must retain the private-page recipe.")
	var loaded: Dictionary = texture.ensure_loaded()
	if not loaded.ok:
		return loaded
	var side: Dictionary = Resolver.billboard_quad_side(_layer.start_radius_bits)
	if not side.ok:
		return side
	var quad := QuadMesh.new()
	var extent: float = _word(side.bits)
	quad.size = Vector2(extent, extent)
	var material: StandardMaterial3D = base_material.duplicate()
	material.albedo_color = colour.value
	mesh = quad
	material_override = material
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return {"ok": true}


## Called once by the runtime/import host with already-routed bytes. Core owns
## the sampler; no terrain callback crosses the language boundary per ray.
func configure(terrain_bytes: PackedByteArray, retain_saved: bool) -> Dictionary:
	if Engine.is_editor_hint():
		return _failure("Editor inspection cannot initialize the live sun sampler.")
	var admitted: Dictionary = Terrain.from_bytes(terrain_bytes, 100)
	if not admitted.ok:
		return admitted
	var visual: Dictionary = prepare_visual(retain_saved)
	if not visual.ok:
		return visual
	_terrain = admitted.value
	var data: Dictionary = _terrain.metadata()
	_height_scale = _word(data.height_scale_bits)
	var sun := Vector3(_word(data.sun_position_x_bits), -_word(data.sun_position_z_bits), -_word(data.sun_position_y_bits))
	_offset = sun * F.value(SCALE)
	_direction = _offset.normalized()
	_private_bake = not retain_saved
	notify_property_list_changed()
	return {"ok": true}


func update_camera(camera_position: Vector3) -> Dictionary:
	if Engine.is_editor_hint() or _terrain == null:
		return _failure("The sun has not been configured for gameplay.")
	position = camera_position + _offset
	visible = has_line_of_sight(camera_position)
	return {"ok": true}


func has_line_of_sight(camera_position: Vector3) -> bool:
	var travelled: float = STEP
	while travelled <= LINE_OF_SIGHT:
		var point: Vector3 = camera_position + _direction * travelled
		if point.y <= relative_height(point.x, point.z):
			return false
		travelled += STEP
	return true


func relative_height(relative_x: float, relative_z: float) -> float:
	var x: float = F.value(F.value(relative_x) + F.value(float(Terrain.PLAYER_START_RETAIL_X_FIXED) / 256.0))
	var z: float = F.value(F.value(relative_z) + F.value(float(Terrain.PLAYER_START_RETAIL_Y_FIXED) / 256.0))
	var fixed_x: int = int(floor(F.value(clampf(x, 0.0, _word(MAX_COORDINATE_BITS)) * 256.0)))
	var fixed_z: int = int(floor(F.value(clampf(z, 0.0, _word(MAX_COORDINATE_BITS)) * 256.0)))
	var units: int = _terrain._fixed_height_units_admitted(fixed_x, fixed_z)
	return F.value(-10.0 - F.value(float(units) * _height_scale))


func definition() -> Dictionary:
	return _layer.duplicate(true)


func offsets() -> Dictionary:
	return {"offset": _offset, "direction": _direction}


static func constant_colour(layer: Dictionary) -> Dictionary:
	if layer.colour_range == null:
		return {"ok": true, "value": Color.WHITE}
	var colour: Dictionary = layer.colour_range
	if colour.use_transition:
		return _failure("The authored colour transition law is unresolved.")
	# C# tuple equality is floating equality: +/-zero compare equal, while
	# NaN does not. Do not compare the raw words for this admission predicate.
	if colour.use_end:
		for axis: String in ["r_bits", "g_bits", "b_bits"]:
			if _word(colour.start[axis]) != _word(colour.end[axis]):
				return _failure("The authored colour ramp law is unresolved.")
	return {"ok": true, "value": Color(_word(colour.start.r_bits), _word(colour.start.g_bits), _word(colour.start.b_bits))}


static func _word(bits: int) -> float:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_u32(0, bits)
	return bytes.decode_float(0)


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
