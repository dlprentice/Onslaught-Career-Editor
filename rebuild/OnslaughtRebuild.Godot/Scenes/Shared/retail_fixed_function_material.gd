# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends RefCounted
## One production owner for the released six-slot material recipe. Textures are
## supplied shared resources; this factory never reads assets, copies pixels,
## owns nodes, advances time, processes input or changes mirrored transforms.
## The exact shader and per-draw provenance remain in the external shader and
## retained C# light-rig/enumerant definitions. No lighting model is added here.
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Template = preload("res://Scenes/Shared/RetailFixedFunctionMaterial.tres")
const MODULATE: int = 4
const MODULATE_2X: int = 5


## layers: six null/Dictionary entries with texture, opacity, offset, scale,
## blend_texture_alpha. Only slots 0,1,2,4 are consumed. facts: immutable HFLD
## RGB words, sunlight_direction, fog_color and fog_density. Optional light_rig
## carries ambient_color,key_light_color,fill_light_color,key_light_direction.
## All Single arguments are stored before their original admission checks.
static func create(layers: Variant, facts: Variant, maximum_horizontal_distance: Variant = 0.0,
		alpha_reference: Variant = 0.5, operation: Variant = MODULATE_2X, light_rig: Variant = null) -> Dictionary:
	if layers == null:
		return _null_reference()
	if not layers is Array:
		return _host_type("layers", "an array")
	if layers.size() != 6 or layers[0] == null:
		return _failure("InvalidDataException", "Retail material requires one base layer and six exact slots.")
	if not _number(maximum_horizontal_distance):
		return _host_type("maximumHorizontalDistance", "a Single")
	var distance: float = F.value(maximum_horizontal_distance)
	if not is_finite(distance) or distance < 0.0:
		return _range("maximumHorizontalDistance")
	if not _number(alpha_reference):
		return _host_type("alphaReference", "a Single")
	var alpha: float = F.value(alpha_reference)
	if not is_finite(alpha) or alpha < 0.0 or alpha > 1.0:
		return _range("alphaReference")
	if not operation is int or operation < -2147483648 or operation > 2147483647:
		return _host_type("operation", "an Int32")
	var gain: float
	match operation:
		MODULATE: gain = 1.0
		MODULATE_2X: gain = 2.0
		_: return _range("operation")
	for index: int in [0, 1, 2, 4]:
		if layers[index] != null:
			var admitted: Dictionary = _layer(layers[index])
			if not admitted.ok:
				return admitted
	var base: Dictionary = layers[0]
	var dot3: Variant = layers[1]
	var reflection: Variant = layers[2]
	var overlay: Variant = layers[4]
	var material: ShaderMaterial = Template.duplicate()
	material.set_shader_parameter("base_texture", base.texture)
	material.set_shader_parameter("dot3_texture", _texture_or_base(dot3, base))
	material.set_shader_parameter("reflection_texture", _texture_or_base(reflection, base))
	material.set_shader_parameter("overlay_texture", _texture_or_base(overlay, base))
	material.set_shader_parameter("has_dot3", 0.0 if dot3 == null else 1.0)
	material.set_shader_parameter("has_reflection", 0.0 if reflection == null else 1.0)
	material.set_shader_parameter("has_overlay", 0.0 if overlay == null else 1.0)
	material.set_shader_parameter("base_blend_texture_alpha", 1.0 if base.blend_texture_alpha else 0.0)
	material.set_shader_parameter("alpha_reference", alpha)
	material.set_shader_parameter("stage_zero_gain", gain)
	material.set_shader_parameter("dot3_offset", Vector2.ZERO if dot3 == null else dot3.offset)
	material.set_shader_parameter("dot3_scale", Vector2.ONE if dot3 == null else dot3.scale)
	material.set_shader_parameter("reflection_factor_alpha", texture_factor_alpha(0.0 if reflection == null else reflection.opacity))
	material.set_shader_parameter("overlay_offset", Vector2.ZERO if overlay == null else overlay.offset)
	material.set_shader_parameter("overlay_scale", Vector2.ONE if overlay == null else overlay.scale)
	material.set_shader_parameter("overlay_opacity", 0.0 if overlay == null else F.value(overlay.opacity))
	var rig: Dictionary
	if light_rig == null:
		var selected: Dictionary = static_world_rig(facts)
		if not selected.ok:
			return selected
		rig = selected.value
	else:
		var admitted: Dictionary = _rig(light_rig)
		if not admitted.ok:
			return admitted
		rig = light_rig
	material.set_shader_parameter("ambient_color", rig.ambient_color)
	material.set_shader_parameter("sun_color", rig.key_light_color)
	material.set_shader_parameter("anti_sun_color", rig.fill_light_color)
	material.set_shader_parameter("sunlight_direction", rig.key_light_direction)
	if facts == null:
		return _null_reference()
	if not facts is Dictionary or not facts.get("fog_color") is Color or not _number(facts.get("fog_density")):
		return _host_type("facts", "typed fog metadata")
	var fog: Color = facts.fog_color
	material.set_shader_parameter("fog_color", Vector3(fog.r, fog.g, fog.b))
	material.set_shader_parameter("fog_density", F.value(facts.fog_density))
	material.set_shader_parameter("maximum_horizontal_distance_squared", F.value(distance * distance) if distance > 0.0 else -1.0)
	return {"ok": true, "value": material}


## The default rig is HFLD ambient/255, Sun/256, AntiSun/256, and the supplied
## mapped sunlight axis. Explicit per-draw rigs remain caller-owned facts.
static func static_world_rig(facts: Variant) -> Dictionary:
	if facts == null:
		return _null_reference()
	if not facts is Dictionary or not facts.get("sunlight_direction") is Vector3:
		return _host_type("facts", "typed light metadata")
	for key: String in ["ambient_color_rgb24", "sun_color_rgb24", "anti_sun_color_rgb24"]:
		var word: Variant = facts.get(key)
		if not word is int or word < 0 or word > 0xffffffff:
			return _host_type("facts", "UInt32 light words")
	return {"ok": true, "value": {"ambient_color": _color_vector(facts.ambient_color_rgb24, 255.0),
		"key_light_color": _color_vector(facts.sun_color_rgb24, 256.0),
		"fill_light_color": _color_vector(facts.anti_sun_color_rgb24, 256.0), "key_light_direction": facts.sunlight_direction}}


## MathF.Round(ToEven) follows a Single product. The subsequent unchecked cast
## is the Godot-hosted .NET conversion, compared against the actual C# oracle
## including nonfinite, overflow and every byte midpoint; it is not GDScript's
## ties-away round() or a clamp on the original opacity.
static func texture_factor_alpha(strength: float) -> float:
	var scaled: float = F.value(F.value(strength) * 255.0)
	if is_nan(scaled):
		return 0.0
	if scaled >= 2147483648.0:
		return 1.0
	if scaled <= -2147483648.0:
		return 0.0
	var lower: float = floor(scaled)
	var remainder: float = scaled - lower
	var rounded: int = int(lower)
	if remainder > 0.5 or (remainder == 0.5 and (rounded & 1) != 0):
		rounded += 1
	return F.value(float(clampi(rounded, 0, 255)) / 255.0)


static func _texture_or_base(layer: Variant, base: Dictionary) -> Texture2D:
	return base.texture if layer == null or layer.texture == null else layer.texture


static func _color_vector(rgb: int, divisor: float) -> Vector3:
	return Vector3(F.value(float((rgb >> 16) & 255) / divisor),
		F.value(float((rgb >> 8) & 255) / divisor), F.value(float(rgb & 255) / divisor))


static func _layer(layer: Variant) -> Dictionary:
	if not layer is Dictionary or not layer.has("texture") or (layer.texture != null and not layer.texture is Texture2D) \
			or not _number(layer.get("opacity")) or not layer.get("offset") is Vector2 or not layer.get("scale") is Vector2 \
			or not layer.get("blend_texture_alpha") is bool:
		return _host_type("layers", "typed texture-layer records")
	return {"ok": true}


static func _rig(rig: Variant) -> Dictionary:
	if not rig is Dictionary:
		return _host_type("lightRig", "typed light vectors")
	for key: String in ["ambient_color", "key_light_color", "fill_light_color", "key_light_direction"]:
		if not rig.get(key) is Vector3:
			return _host_type("lightRig", "typed light vectors")
	return {"ok": true}


static func _number(value: Variant) -> bool:
	return typeof(value) in [TYPE_INT, TYPE_FLOAT]


static func _range(parameter: String) -> Dictionary:
	return _failure("ArgumentOutOfRangeException", "Specified argument was out of the range of valid values. (Parameter '" + parameter + "')", parameter)


static func _host_type(parameter: String, expected: String) -> Dictionary:
	return _failure("ArgumentException", parameter + " requires " + expected + ".", parameter)


static func _null_reference() -> Dictionary:
	return _failure("NullReferenceException", "Object reference not set to an instance of an object.")


static func _failure(type: String, message: String, parameter: String = "") -> Dictionary:
	return {"ok": false, "error_type": type, "error": message, "parameter": parameter}
