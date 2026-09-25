# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Current Level100TargetPresentation.cs conversion and six explicit mesh pairs.
## Measurement/provenance remains with that source owner; this adds no bindings.
## Project preserves an unknown pair exactly: rejection of a missing mesh is
## the renderer's responsibility, not a new filter at this pure projection seam.
## Render vectors use camera-compatible UInt32 x_bits/y_bits/z_bits. Bases have
## x_axis/y_axis/z_axis columns; Core input rows retain their signed Int32 words.
## Names use detached UTF-16 carriers (native String inputs are admitted too).
const Float32 = preload("res://Core/retail_float24.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const BASIS_KEYS: Array[String] = ["row0_x", "row0_y", "row0_z", "row1_x", "row1_y", "row1_z", "row2_x", "row2_y", "row2_z"]
const _BINDINGS: Array = [
	["Target Tank", "m_f_pulsetank_training.msh.aya"],
	["Target Truck", "m_f_truck_training.msh.aya"],
	["Warehouse", "m_m_warehouse.msh.aya"],
	["U-17 Highside Transporter", "m_f_lifter.msh.aya"],
	["Air Trainer", "m_FA_F24_training.msh.aya"],
	["Target Drone", "m_FA_F24_training.msh.aya"],
]


static func rendered_bindings() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for row: Array in _BINDINGS:
		result.append({"definition_name": Text.units(row[0]).value, "mesh_binding": Text.units(row[1]).value})
	return result


## Required target facts: actor_id,definition_name,mesh_binding,is_active,pose:
## {position_millimeters:{x,y,z},basis_float_bits:{row0_x,...,row2_z}}.
## Other TargetSnapshot fields are not read by the original projection.
static func project(target: Variant) -> Dictionary:
	if target == null:
		return failure("ArgumentNullException", "Target is required.", "target")
	if not target is Dictionary or not target.has("pose"):
		return failure("ArgumentException", "Target requires an explicit pose.")
	if target.pose == null:
		return failure("NullReferenceException", "Target pose is null.")
	if not target.pose is Dictionary or not target.pose.get("basis_float_bits") is Dictionary:
		return failure("ArgumentException", "Target pose requires Core basis_float_bits.")
	var core: Dictionary = target.pose.basis_float_bits
	for key: String in BASIS_KEYS:
		if not i32(core.get(key)):
			return failure("ArgumentException", "Core basis requires signed Int32 " + key + ".")
	if not target.pose.get("position_millimeters") is Dictionary:
		return failure("ArgumentException", "Target pose requires position_millimeters.")
	var position: Dictionary = target.pose.position_millimeters
	for key: String in ["x", "y", "z"]:
		if not i32(position.get(key)):
			return failure("ArgumentException", "Core position requires Int32 " + key + ".")
	if not i32(target.get("actor_id")) or typeof(target.get("is_active")) != TYPE_BOOL:
		return failure("ArgumentException", "Target requires Int32 actor_id and Boolean is_active.")
	var admitted_binding: Dictionary = binding(target)
	if not admitted_binding.ok:
		return admitted_binding
	var scale: float = Float32.store_float32(0.001)
	# The source negates Int32 Z before conversion, including unchecked MinValue.
	var z: int = position.z if position.z == -2147483648 else -position.z
	return {"ok": true, "value": {"actor_id": target.actor_id, "definition_name": admitted_binding.value.definition_name,
		"mesh_binding": admitted_binding.value.mesh_binding, "visible": target.is_active,
		"position": {"x_bits": Float32.store_word(Float32.store_float32(position.x) * scale),
			"y_bits": Float32.store_word(Float32.store_float32(position.y) * scale),
			"z_bits": Float32.store_word(Float32.store_float32(z) * scale)},
		"basis": {"x_axis": {"x_bits": core.row0_x & 0xffffffff, "y_bits": core.row1_x & 0xffffffff, "z_bits": (core.row2_x ^ 0x80000000) & 0xffffffff},
			"y_axis": {"x_bits": core.row0_y & 0xffffffff, "y_bits": core.row1_y & 0xffffffff, "z_bits": (core.row2_y ^ 0x80000000) & 0xffffffff},
			"z_axis": {"x_bits": (core.row0_z ^ 0x80000000) & 0xffffffff, "y_bits": (core.row1_z ^ 0x80000000) & 0xffffffff, "z_bits": core.row2_z & 0xffffffff}}}}


static func binding(value: Variant) -> Dictionary:
	if not value is Dictionary or not value.has("definition_name") or not value.has("mesh_binding"):
		return failure("ArgumentException", "Binding requires both explicit nullable names.")
	var definition: Dictionary = Text.units(value.definition_name)
	if not definition.ok:
		return failure("ArgumentException", definition.error)
	var mesh: Dictionary = Text.units(value.mesh_binding)
	if not mesh.ok:
		return failure("ArgumentException", mesh.error)
	return {"ok": true, "value": {"definition_name": definition.value, "mesh_binding": mesh.value}}


static func admit_descriptor(value: Variant) -> Dictionary:
	var names: Dictionary = binding(value)
	if not names.ok:
		return names
	if not i32(value.get("actor_id")) or typeof(value.get("visible")) != TYPE_BOOL:
		return failure("ArgumentException", "Visual descriptor requires Int32 identity and Boolean visible.")
	var position: Dictionary = admit_vector(value.get("position"))
	if not position.ok: return position
	var basis: Dictionary = admit_basis(value.get("basis"))
	if not basis.ok: return basis
	return {"ok": true, "value": {"actor_id": value.actor_id, "definition_name": names.value.definition_name,
		"mesh_binding": names.value.mesh_binding, "visible": value.visible, "position": position.value, "basis": basis.value}}


static func admit_basis(value: Variant) -> Dictionary:
	if not value is Dictionary:
		return failure("ArgumentException", "Render basis requires three column vectors.")
	var result: Dictionary = {}
	for axis: String in ["x_axis", "y_axis", "z_axis"]:
		var vector: Dictionary = admit_vector(value.get(axis))
		if not vector.ok: return vector
		result[axis] = vector.value
	return {"ok": true, "value": result}


static func admit_vector(value: Variant) -> Dictionary:
	if not value is Dictionary:
		return failure("ArgumentException", "Render vector requires three raw UInt32 words.")
	var result: Dictionary = {}
	for axis: String in ["x_bits", "y_bits", "z_bits"]:
		if not word(value.get(axis)):
			return failure("ArgumentException", "Render vector requires UInt32 " + axis + ".")
		result[axis] = value[axis]
	return {"ok": true, "value": result}


static func word(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= 0 and value <= 0xffffffff


static func i32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


static func failure(kind: String, message: String, parameter: String = "") -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message, "parameter": parameter}
