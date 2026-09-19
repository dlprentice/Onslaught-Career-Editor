# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Detached data projection of ParticleEffectPlan.cs; no particle simulation.
## Plan fields: effect_name (UTF-16/null), root_type (Int32), layers (authored
## order), unimplemented (UTF-16 entries), total_instances (unchecked Int32).
## Layer fields retain the source names in snake_case. Every Single is a raw
## UInt32 *_bits field. Colour triples use r_bits/g_bits/b_bits; velocity and
## random-scale triples use x_bits/y_bits/z_bits. Shape/colour_range may be null.
## Unknown Shape.Type/Axis_Aligned and blend mode 2 remain raw numbers. Selector
## expected counts and the 256-instance cap are reconstruction policy, not a
## claim that the retail RNG phase or modifier curves have been recovered.
const Text = preload("res://Core/canonical_json_string.gd")
const ANIMATION_STATIC: int = 0
const ANIMATION_PLAY_ONCE: int = 1
const ANIMATION_LOOP: int = 2


static func create(effect_name: Variant, root_type: Variant, layers: Variant, unimplemented: Variant) -> Dictionary:
	var name: Dictionary = Text.units(effect_name)
	if not name.ok: return _failure("ArgumentException", name.error)
	if not _i32(root_type): return _failure("ArgumentException", "Root type requires Int32.")
	var total: Dictionary = total_instances(layers)
	if not total.ok: return total
	if not unimplemented is Array:
		return _failure("ArgumentException", "Unimplemented entries require an ordered Array.")
	var omissions: Array = []
	for entry: Variant in unimplemented:
		var admitted: Dictionary = Text.units(entry)
		if not admitted.ok: return _failure("ArgumentException", admitted.error)
		omissions.append(admitted.value)
	return {"ok": true, "value": {"effect_name": name.value, "root_type": root_type,
		"layers": layers.duplicate(true), "unimplemented": omissions, "total_instances": total.value}}


static func total_instances(layers: Variant) -> Dictionary:
	if layers == null:
		return _failure("NullReferenceException", "Plan layers are null.")
	if not layers is Array:
		return _failure("ArgumentException", "Plan layers require an ordered Array.")
	var total: int = 0
	for layer: Variant in layers:
		if layer == null:
			return _failure("NullReferenceException", "A plan layer is null.")
		if not layer is Dictionary or not _i32(layer.get("instance_count")):
			return _failure("ArgumentException", "A plan layer requires Int32 instance_count.")
		total = int32(total + layer.instance_count)
	return {"ok": true, "value": total}


static func int32(value: int) -> int:
	var word: int = value & 0xffffffff
	return word - 0x100000000 if word >= 0x80000000 else word


static func _i32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "parameter": "", "error": message}
