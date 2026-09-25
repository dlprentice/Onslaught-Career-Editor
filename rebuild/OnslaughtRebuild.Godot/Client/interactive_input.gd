# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## InteractiveInput.cs value contract. FireHeld is a physical level; its release
## edge belongs to InteractiveSession. This record never invents Core actions.
const SimInput = preload("res://Core/sim_input.gd")
const FIELDS: Array[String] = ["move_x", "move_z", "fire_held", "toggle_mode_held", "reset_held", "look_x", "look_y", "landing_jets_held"]
const BOOLEAN_FIELDS: Array[String] = ["fire_held", "toggle_mode_held", "reset_held", "landing_jets_held"]


static func idle() -> Dictionary:
	return {"move_x": 0, "move_z": 0, "fire_held": false, "toggle_mode_held": false,
		"reset_held": false, "look_x": 0, "look_y": 0, "landing_jets_held": false}


static func create(move_x: Variant, move_z: Variant, fire_held: Variant, toggle_mode_held: Variant,
		reset_held: Variant, look_x: Variant = 0, look_y: Variant = 0, landing_jets_held: Variant = false) -> Dictionary:
	return admit_record({"move_x": move_x, "move_z": move_z, "fire_held": fire_held,
		"toggle_mode_held": toggle_mode_held, "reset_held": reset_held,
		"look_x": look_x, "look_y": look_y, "landing_jets_held": landing_jets_held})


static func admit_record(input: Variant) -> Dictionary:
	if not input is Dictionary:
		return _argument("Interactive input must be an eight-field value record.")
	for key: String in FIELDS:
		if not input.has(key):
			return _argument("Missing interactive input field: " + key)
	var axes: Dictionary = SimInput.create(input.move_x, input.move_z, 0, input.look_x, input.look_y)
	if not axes.ok:
		return axes
	for key: String in BOOLEAN_FIELDS:
		if not input[key] is bool:
			return _argument("Interactive input Boolean required: " + key)
	var result: Dictionary = {}
	for key: String in FIELDS:
		result[key] = input[key]
	return {"ok": true, "value": result}


static func validate(input: Variant) -> Dictionary:
	var admitted: Dictionary = admit_record(input)
	if not admitted.ok:
		return admitted
	var value: Dictionary = admitted.value
	# Reuse the existing source-ordered semantic axis validation; held buttons
	# do not become repeated Fire/Toggle/Reset actions at this boundary.
	var axes: Dictionary = SimInput.create(value.move_x, value.move_z, 0, value.look_x, value.look_y)
	return SimInput.validate(axes.value)


static func _argument(reason: String) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException", "error_code": "argument", "error": reason,
		"parameter": "", "inner_parameter": ""}
