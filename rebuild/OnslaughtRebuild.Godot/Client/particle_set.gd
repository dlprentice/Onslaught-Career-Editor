# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Lossless authored .par reader from Client/ParticleSetFile.cs. No IO or scene
## owner: callers supply bytes, and re-emission returns bytes without writing.
## Repeated fields and the first exact descriptor name retain authored order.
const Text = preload("res://Core/canonical_json_string.gd")
const Numbers = preload("res://Core/invariant_number.gd")
const Latin1 = preload("res://Core/latin1_encoding.gd")
const RECORD_SEPARATOR: String = "*****************************************************************"
const HEADER_PREFIX: String = "ParticleSystemEd_File_"
const VERSION_PREFIX: String = "File_Version "
const COUNT_PREFIX: String = "Num_Particle_Descriptors "
const TYPE_PREFIX: String = "Particle_Descriptor_Type "
const NAME_PREFIX: String = "Particle_Descriptor_Name "
enum DescriptorType { SPRITE = 1, EMITTER, MODIFIER, SELECTOR, COLOUR_RANGE,
	TIMELINE, SHAPE, TRAIL, MOVER, FUNCTION, MESH, FOR, PMESH }
enum ParseKind { UNRECOGNIZED = -1, INVALID_OR_UNKNOWN = 0, MARKER_NO_VALUE,
	DIRECT_FLOAT, DIRECT_INT, RAW_REMAINDER_STRING, FLOAT_WITH_OPTIONAL_REFERENCE, REFERENCE_NAME }
const CLASS_NAMES: Array[String] = ["", "CPDSimpleSprite", "CPDEmitter", "CPDModifier", "CPDSelector",
	"CPDColourRange", "CPDTimeline", "CPDShape", "CPDTrail", "CPDMover", "CPDFunction", "CPDMesh", "CPDFoR", "CPDPMesh"]
const LOADER_ADDRESSES: Array[int] = [0, 0x004c05c0, 0x004c1810, 0x004c20c0, 0x004c2130,
	0x004c2300, 0x004c24c0, 0x004c2b70, 0x004c3120, 0x004c4420, 0x004c4840, 0x004c4b00, 0x004c5330, 0x004c5730]
# TOKEN_KINDS is the exact public token-name table below, not a permissiveness
# switch in the lossless file decoder. Unknown authored fields remain intact.
const TOKEN_KINDS: Dictionary = {
	"ParticleSystemEd_File_(C)2000_Lost_Toys_Ltd": ParseKind.MARKER_NO_VALUE,
	"*****************************************************************": ParseKind.MARKER_NO_VALUE,
	"File_Version": ParseKind.DIRECT_FLOAT,
	"Final_Radius": ParseKind.DIRECT_FLOAT,
	"Anim_Speed": ParseKind.DIRECT_FLOAT,
	"Velocity_Damp": ParseKind.DIRECT_FLOAT,
	"Life_Pct": ParseKind.DIRECT_FLOAT,
	"Velocity_Randomness": ParseKind.DIRECT_FLOAT,
	"Transition_Point": ParseKind.DIRECT_FLOAT,
	"RandomSX": ParseKind.DIRECT_FLOAT,
	"RandomSY": ParseKind.DIRECT_FLOAT,
	"RandomSZ": ParseKind.DIRECT_FLOAT,
	"Width": ParseKind.DIRECT_FLOAT,
	"Start_Width": ParseKind.DIRECT_FLOAT,
	"Wiggle_Factor": ParseKind.DIRECT_FLOAT,
	"Disperse_Rate": ParseKind.DIRECT_FLOAT,
	"SegmentLength": ParseKind.DIRECT_FLOAT,
	"Yaw": ParseKind.DIRECT_FLOAT,
	"Pitch": ParseKind.DIRECT_FLOAT,
	"Roll": ParseKind.DIRECT_FLOAT,
	"Angular_Momentum": ParseKind.DIRECT_FLOAT,
	"Num_Particle_Descriptors": ParseKind.DIRECT_INT,
	"Particle_Descriptor_Type": ParseKind.DIRECT_INT,
	"Gravity": ParseKind.DIRECT_INT,
	"Bounce": ParseKind.DIRECT_INT,
	"Fade_Col": ParseKind.DIRECT_INT,
	"Blend_Mode": ParseKind.DIRECT_INT,
	"Texture_Number": ParseKind.DIRECT_INT,
	"Axis_Aligned": ParseKind.DIRECT_INT,
	"Anim_Type": ParseKind.DIRECT_INT,
	"End_Frame": ParseKind.DIRECT_INT,
	"Texture_Size": ParseKind.DIRECT_INT,
	"Random_Start_Frame": ParseKind.DIRECT_INT,
	"2D": ParseKind.DIRECT_INT,
	"Life": ParseKind.DIRECT_INT,
	"Transmit_Life": ParseKind.DIRECT_INT,
	"Transmit_FoR": ParseKind.DIRECT_INT,
	"Interpolated_Emission": ParseKind.DIRECT_INT,
	"Pass_Num_Particles": ParseKind.DIRECT_INT,
	"Probability_0": ParseKind.DIRECT_INT,
	"Probability_1": ParseKind.DIRECT_INT,
	"Probability_2": ParseKind.DIRECT_INT,
	"Probability_3": ParseKind.DIRECT_INT,
	"Use_End": ParseKind.DIRECT_INT,
	"Use_Transition": ParseKind.DIRECT_INT,
	"Num_Entries": ParseKind.DIRECT_INT,
	"Time": ParseKind.DIRECT_INT,
	"Type": ParseKind.DIRECT_INT,
	"Ring_Axis": ParseKind.DIRECT_INT,
	"Hemisphere": ParseKind.DIRECT_INT,
	"Num_Particles": ParseKind.DIRECT_INT,
	"Hollow": ParseKind.DIRECT_INT,
	"Num_Points": ParseKind.DIRECT_INT,
	"Taper_Start": ParseKind.DIRECT_INT,
	"Width_With_Life": ParseKind.DIRECT_INT,
	"Fade_Point": ParseKind.DIRECT_INT,
	"Use_Segment_Length": ParseKind.DIRECT_INT,
	"Manual_Wiggle_Enabled": ParseKind.DIRECT_INT,
	"Flat": ParseKind.DIRECT_INT,
	"Param_Function": ParseKind.DIRECT_INT,
	"Clip": ParseKind.DIRECT_INT,
	"Value_Type": ParseKind.DIRECT_INT,
	"Offset_Gameturn": ParseKind.DIRECT_INT,
	"Auto_Centre": ParseKind.DIRECT_INT,
	"Cylinder_NumPtsAxial": ParseKind.DIRECT_INT,
	"Cylinder_NumPtsRadial": ParseKind.DIRECT_INT,
	"Sphere_NumPtsAx": ParseKind.DIRECT_INT,
	"Sphere_NumPtsRad": ParseKind.DIRECT_INT,
	"Particle_Descriptor_Name": ParseKind.RAW_REMAINDER_STRING,
	"Texture": ParseKind.RAW_REMAINDER_STRING,
	"Mesh": ParseKind.RAW_REMAINDER_STRING,
	"Radius": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Length": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Emit_Per_Turn": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Initial_Velocity_X": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Initial_Velocity_Y": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Initial_Velocity_Z": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Transmit_Velocity": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Outward_Velocity": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Start_Red": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Start_Green": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Start_Blue": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"End_Red": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"End_Green": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"End_Blue": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Transition_Red": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Transition_Green": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Transition_Blue": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Wiggle_Length": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Yaw_Length": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"GravityPC": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Param_A": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Param_B": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Param_C": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Param_D": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Gameturn_Scale": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Tile_U": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Tile_V": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Scroll_U": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Scroll_V": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Cylinder_Radius": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Cylinder_Radius2": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Cylinder_Length": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Sphere_RadiusTime": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Sphere_Latitude_Start": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Sphere_Latitude_End": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Sphere_Longitude_Start": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Sphere_Longitude_End": ParseKind.FLOAT_WITH_OPTIONAL_REFERENCE,
	"Modifier": ParseKind.REFERENCE_NAME,
	"Colour_Range": ParseKind.REFERENCE_NAME,
	"Particle_Descriptor": ParseKind.REFERENCE_NAME,
	"Shape": ParseKind.REFERENCE_NAME,
	"Mover": ParseKind.REFERENCE_NAME,
	"Particle_Descriptor_0": ParseKind.REFERENCE_NAME,
	"Particle_Descriptor_1": ParseKind.REFERENCE_NAME,
	"Particle_Descriptor_2": ParseKind.REFERENCE_NAME,
	"Particle_Descriptor_3": ParseKind.REFERENCE_NAME,
	"Yaw_Function": ParseKind.REFERENCE_NAME,
	"Pitch_Function": ParseKind.REFERENCE_NAME,
	"Roll_Function": ParseKind.REFERENCE_NAME,
	"Impact_Spawnee": ParseKind.REFERENCE_NAME,
	"Initial": ParseKind.REFERENCE_NAME,
	"Death": ParseKind.REFERENCE_NAME,
	"Colour_Range2": ParseKind.REFERENCE_NAME,
}


class Descriptor extends RefCounted:
	const Text = preload("res://Core/canonical_json_string.gd")
	const Numbers = preload("res://Core/invariant_number.gd")
	var _type_id: int
	var _name: PackedInt32Array
	var _fields: Array[Dictionary] = []
	var type_id: int:
		get: return _type_id
	var name: PackedInt32Array:
		get: return _name.duplicate()
	var fields: Array[Dictionary]:
		get: return _fields.duplicate(true)

	func raw(key: Variant) -> Dictionary:
		var admitted: Dictionary = Text.units(key)
		if not admitted.ok:
			return admitted
		for field: Dictionary in _fields:
			if field.key == admitted.value:
				return {"ok": true, "value": null if field.value == null else field.value.duplicate()}
		return {"ok": true, "value": null}


	func raw_all(key: Variant) -> Dictionary:
		var admitted: Dictionary = Text.units(key)
		if not admitted.ok:
			return admitted
		var values: Array[PackedInt32Array] = []
		for field: Dictionary in _fields:
			if field.key == admitted.value and field.value != null:
				values.append(field.value.duplicate())
		return {"ok": true, "value": values}


	func int_value(key: Variant) -> Dictionary:
		var value: Dictionary = _require(key)
		return Numbers.parse_int32(value.value) if value.ok else value


	func int_or_default(key: Variant, fallback: Variant) -> Dictionary:
		if typeof(fallback) != TYPE_INT or fallback < -2147483648 or fallback > 2147483647:
			return Numbers._failure("ArgumentException", "Fallback must be Int32.", "fallback")
		var value: Dictionary = raw(key)
		if not value.ok:
			return value
		return {"ok": true, "value": fallback} if value.value == null else Numbers.parse_int32(value.value)


	func float_bits(key: Variant) -> Dictionary:
		var value: Dictionary = _require(key)
		return Numbers.parse_float32(value.value) if value.ok else value


	func retail_direct_float_bits(key: Variant) -> Dictionary:
		var value: Dictionary = _require(key)
		if not value.ok:
			return value
		var units: PackedInt32Array = value.value
		var space: int = units.find(32)
		return Numbers.parse_float32(units if space < 0 else units.slice(0, space))


	func float_with_modifier(key: Variant) -> Dictionary:
		var value: Dictionary = _require(key)
		if not value.ok:
			return value
		var units: PackedInt32Array = value.value
		var space: int = units.find(32)
		var scalar: Dictionary = Numbers.parse_float32(units if space < 0 else units.slice(0, space))
		if not scalar.ok:
			return scalar
		var modifier: Variant = null if space < 0 else units.slice(space + 1)
		return {"ok": true, "value": {"bits": scalar.bits, "modifier": null if Text.equals_text(modifier, "NONE") else modifier}}


	func reference_name(key: Variant) -> Dictionary:
		var result: Dictionary = raw(key)
		if result.ok and Text.equals_text(result.value, "NONE"):
			result.value = null
		return result


	func _require(key: Variant) -> Dictionary:
		var value: Dictionary = raw(key)
		if value.ok and value.value == null:
			return Numbers._failure("InvalidDataException", "Particle descriptor has no requested field.")
		return value


class Set extends RefCounted:
	const Text = preload("res://Core/canonical_json_string.gd")
	const Numbers = preload("res://Core/invariant_number.gd")
	const Latin1 = preload("res://Core/latin1_encoding.gd")
	var _header: PackedInt32Array
	var _version_line: PackedInt32Array
	var _declared_count: int
	var _descriptors: Array[Descriptor] = []
	var _by_name: Dictionary = {}
	var header: PackedInt32Array:
		get: return _header.duplicate()
	var version_line: PackedInt32Array:
		get: return _version_line.duplicate()
	var declared_count: int:
		get: return _declared_count
	var descriptors: Array[Descriptor]:
		get: return _descriptors.duplicate()


	func find(name: Variant) -> Dictionary:
		var admitted: Dictionary = Text.units(name)
		if not admitted.ok:
			return admitted
		if admitted.value == null:
			return Numbers._failure("ArgumentNullException", "A descriptor name is required.", "key")
		return {"ok": true, "value": _by_name.get(admitted.value)}


	func require(name: Variant) -> Dictionary:
		var result: Dictionary = find(name)
		if result.ok and result.value == null:
			return Numbers._failure("InvalidDataException", "Particle set has no descriptor with the requested name.")
		return result


	func to_units() -> PackedInt32Array:
		var lines: Array[PackedInt32Array] = [_header, _version_line,
			Text.units("Num_Particle_Descriptors " + str(_declared_count)).value]
		for descriptor: Descriptor in _descriptors:
			lines.append(Text.units("Particle_Descriptor_Type " + str(descriptor.type_id)).value)
			var name_line: PackedInt32Array = Text.units("Particle_Descriptor_Name ").value
			name_line.append_array(descriptor._name)
			lines.append(name_line)
			for field: Dictionary in descriptor._fields:
				var line: PackedInt32Array = field.key.duplicate()
				if field.value != null:
					line.append(32)
					line.append_array(field.value)
				lines.append(line)
			lines.append(Text.units("*****************************************************************").value)
		var result := PackedInt32Array()
		for line: PackedInt32Array in lines:
			result.append_array(line)
			result.append(13)
			result.append(10)
		return result


	func to_bytes() -> PackedByteArray:
		return Latin1.encode(to_units()).value


static func parse_bytes(bytes: PackedByteArray) -> Dictionary:
	return parse_units(Latin1.decode(bytes))


static func parse_units(text: Variant) -> Dictionary:
	var admitted: Dictionary = Text.units(text)
	if not admitted.ok:
		return admitted
	if admitted.value == null:
		return Numbers._failure("ArgumentNullException", "Particle text is required.", "text")
	var lines: Array[PackedInt32Array] = _split_lines(admitted.value)
	if not lines.is_empty() and lines[-1].is_empty():
		lines.remove_at(lines.size() - 1)
	if lines.size() < 3:
		return _invalid("Particle set file is truncated.")
	for row: Array in [[0, HEADER_PREFIX], [1, VERSION_PREFIX], [2, COUNT_PREFIX]]:
		if not _starts_with(lines[row[0]], row[1]):
			return _invalid("Particle set file is missing an ordered header line.")
	var count: Dictionary = Numbers.parse_int32(lines[2].slice(COUNT_PREFIX.length()))
	if not count.ok:
		return count
	var value := Set.new()
	value._header = lines[0]
	value._version_line = lines[1]
	value._declared_count = count.value
	var current: Array[PackedInt32Array] = []
	for index: int in range(3, lines.size()):
		var line: PackedInt32Array = lines[index]
		if not Text.equals_text(line, RECORD_SEPARATOR):
			current.append(line)
			continue
		var built: Dictionary = _build_descriptor(current)
		if not built.ok:
			return built
		var descriptor: Descriptor = built.value
		value._descriptors.append(descriptor)
		if not value._by_name.has(descriptor._name):
			value._by_name[descriptor._name] = descriptor
		current.clear()
	if not current.is_empty():
		return _invalid("Particle set file has trailing lines after its last record separator.")
	return {"ok": true, "value": value}


static func try_get_parse_kind(name: Variant) -> Dictionary:
	var native: Dictionary = Text.native_string(name)
	var kind: int = TOKEN_KINDS.get(native.value, ParseKind.UNRECOGNIZED) if native.ok and native.value != null else ParseKind.UNRECOGNIZED
	return {"recognized": kind != ParseKind.UNRECOGNIZED, "kind": kind}


static func descriptor_class_name(type_id: int) -> Dictionary:
	return _invalid("Retail has no such particle descriptor type.") if type_id < 1 or type_id > 13 else {"ok": true, "value": CLASS_NAMES[type_id]}


static func descriptor_loader_address(type_id: int) -> Dictionary:
	return _invalid("Retail has no such particle descriptor type.") if type_id < 1 or type_id > 13 else {"ok": true, "value": LOADER_ADDRESSES[type_id]}


static func _build_descriptor(lines: Array[PackedInt32Array]) -> Dictionary:
	if lines.size() < 2:
		return _invalid("Particle descriptor record is missing its type or name line.")
	if not _starts_with(lines[0], TYPE_PREFIX) or not _starts_with(lines[1], NAME_PREFIX):
		return _invalid("Particle descriptor record is missing its ordered type/name prefix.")
	var type_result: Dictionary = Numbers.parse_int32(lines[0].slice(TYPE_PREFIX.length()))
	if not type_result.ok:
		return type_result
	var descriptor := Descriptor.new()
	descriptor._type_id = type_result.value
	descriptor._name = lines[1].slice(NAME_PREFIX.length())
	for index: int in range(2, lines.size()):
		var line: PackedInt32Array = lines[index]
		var space: int = line.find(32)
		descriptor._fields.append({"key": line if space < 0 else line.slice(0, space),
			"value": null if space < 0 else line.slice(space + 1)})
	return {"ok": true, "value": descriptor}


static func _split_lines(units: PackedInt32Array) -> Array[PackedInt32Array]:
	var lines: Array[PackedInt32Array] = []
	var start: int = 0
	var cursor: int = 0
	while cursor < units.size() - 1:
		if units[cursor] == 13 and units[cursor + 1] == 10:
			lines.append(units.slice(start, cursor))
			cursor += 2
			start = cursor
		else:
			cursor += 1
	lines.append(units.slice(start))
	return lines


static func _starts_with(units: PackedInt32Array, prefix: String) -> bool:
	return units.size() >= prefix.length() and units.slice(0, prefix.length()) == Text.units(prefix).value


static func _invalid(message: String) -> Dictionary:
	return Numbers._failure("InvalidDataException", message)
