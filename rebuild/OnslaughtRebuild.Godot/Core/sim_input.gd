# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure value-record port of SimulationTypes.cs/SimInput. Construction admits
## the C# storage widths; validate applies the separate semantic action/axis law.
## Every record returned to a caller is detached. There is no device owner here.

enum Actions {
	NONE = 0, TOGGLE_MODE = 1, FIRE = 2, RESET = 4, LANDING_JETS = 8,
	SKIP_PANNING = 16, CHARGE_WEAPON = 32, CHANGE_WEAPON = 64,
	ZOOM_IN = 128, ZOOM_OUT = 256, CLOAK = 512,
}
const DECLARED_ACTIONS: int = 1023
const IMPLEMENTED_ACTIONS: int = 511
const FIELDS: Array[String] = ["move_x", "move_z", "actions", "look_x", "look_y",
	"look_x_analog_permille", "look_y_analog_permille"]
const PARAMETERS: Dictionary = {"move_x": "MoveX", "move_z": "MoveZ", "actions": "Actions",
	"look_x": "LookX", "look_y": "LookY", "look_x_analog_permille": "LookXAnalogPermille",
	"look_y_analog_permille": "LookYAnalogPermille"}


static func idle() -> Dictionary:
	return {"move_x": 0, "move_z": 0, "actions": 0, "look_x": 0, "look_y": 0,
		"look_x_analog_permille": 0, "look_y_analog_permille": 0}


static func create(move_x: Variant, move_z: Variant, actions: Variant = 0, look_x: Variant = 0,
		look_y: Variant = 0, look_x_analog_permille: Variant = 0, look_y_analog_permille: Variant = 0) -> Dictionary:
	return admit_record({"move_x": move_x, "move_z": move_z, "actions": actions, "look_x": look_x,
		"look_y": look_y, "look_x_analog_permille": look_x_analog_permille,
		"look_y_analog_permille": look_y_analog_permille})


static func admit_record(input: Variant) -> Dictionary:
	if typeof(input) != TYPE_DICTIONARY:
		return _failure("ArgumentException", "argument", "Input must be a seven-field integer record.")
	var copy: Dictionary = {}
	for field: String in FIELDS:
		if not input.has(field) or typeof(input[field]) != TYPE_INT:
			return _failure("ArgumentException", "argument", "Input field must be an exact integer: " + field)
		var low: int = 0 if field == "actions" else -32768 if field.contains("analog") else -128
		var high: int = 65535 if field == "actions" else 32767 if field.contains("analog") else 127
		if input[field] < low or input[field] > high:
			return _failure("ArgumentOutOfRangeException", "input_range", "Input field exceeds its C# storage width.", PARAMETERS[field])
		copy[field] = int(input[field])
	return {"ok": true, "value": copy}


static func validate(input: Variant) -> Dictionary:
	var admitted: Dictionary = admit_record(input)
	if not admitted.ok:
		return admitted
	var record: Dictionary = admitted.value
	# Source order is observable when more than one field is invalid.
	for field: String in ["move_x", "move_z", "look_x", "look_y", "look_x_analog_permille", "look_y_analog_permille"]:
		var limit: int = 1000 if field.contains("analog") else 1
		if record[field] < -limit or record[field] > limit:
			return _failure("ArgumentOutOfRangeException", "input_range", "Input axis is outside its semantic range.", PARAMETERS[field])
	if (int(record.actions) & ~DECLARED_ACTIONS) != 0:
		return _failure("ArgumentOutOfRangeException", "unknown_actions", "Input contains an unknown action bit.", "Actions")
	if (int(record.actions) & ~IMPLEMENTED_ACTIONS) != 0:
		return _failure("ArgumentOutOfRangeException", "unimplemented_actions", "Input requests declared but unimplemented actions.", "Actions")
	return {"ok": true}


static func has_action(input: Variant, action: Variant) -> Dictionary:
	var admitted: Dictionary = admit_record(input)
	if not admitted.ok:
		return admitted
	if typeof(action) != TYPE_INT or action < 0 or action > 65535:
		return _failure("ArgumentOutOfRangeException", "input_range", "Action mask must fit ushort.", "action")
	return {"ok": true, "value": (int(admitted.value.actions) & int(action)) != 0}


static func _failure(kind: String, code: String, message: String, parameter: String = "") -> Dictionary:
	return {"ok": false, "error_type": kind, "error_code": code, "error": message,
		"parameter": parameter, "inner_parameter": ""}
