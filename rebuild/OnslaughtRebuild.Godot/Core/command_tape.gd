# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## CommandTape/CommandSpan codec and sequential reader from Core/CommandTape.cs.
## UTF-16 string units are the stored values; canonical JSON is ASCII with LF.
## No recorder, filesystem, clock, node, input device or simulation owner lives here.

const Strict = preload("res://Core/strict_json.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const InputValue = preload("res://Core/sim_input.gd")
const Sha = preload("res://Core/sha256_stream.gd")
const CURRENT_SCHEMA: String = "onslaught-rebuild-command-tape.v5"
const PREVIOUS_SCHEMA: String = "onslaught-rebuild-command-tape.v4"
const STRING_FIELDS: Array[String] = ["schema_version", "name", "expected_final_state_hash", "expected_trace_hash"]
const ROOT_MEMBERS: Dictionary = {
	"schemaVersion": "schema_version", "name": "name", "seed": "seed", "durationTicks": "duration_ticks",
	"expectedFinalStateHash": "expected_final_state_hash", "expectedTraceHash": "expected_trace_hash", "spans": "spans",
}
const SPAN_MEMBERS: Dictionary = {
	"startTick": "start_tick", "durationTicks": "duration_ticks", "moveX": "move_x", "moveZ": "move_z",
	"toggleMode": "toggle_mode", "fire": "fire", "reset": "reset", "lookX": "look_x", "lookY": "look_y",
	"lookXAnalogPermille": "look_x_analog_permille", "lookYAnalogPermille": "look_y_analog_permille",
	"landingJets": "landing_jets", "skipPanning": "skip_panning", "changeWeapon": "change_weapon",
	"chargeWeapon": "charge_weapon", "zoomIn": "zoom_in", "zoomOut": "zoom_out",
}
const SPAN_RANGES: Dictionary = {
	"start_tick": [-2147483648, 2147483647], "duration_ticks": [-2147483648, 2147483647],
	"move_x": [-128, 127], "move_z": [-128, 127], "look_x": [-128, 127], "look_y": [-128, 127],
	"look_x_analog_permille": [-32768, 32767], "look_y_analog_permille": [-32768, 32767],
}
const ACTIONS: Dictionary = {"toggle_mode": InputValue.Actions.TOGGLE_MODE, "fire": InputValue.Actions.FIRE,
	"reset": InputValue.Actions.RESET, "landing_jets": InputValue.Actions.LANDING_JETS,
	"skip_panning": InputValue.Actions.SKIP_PANNING, "change_weapon": InputValue.Actions.CHANGE_WEAPON,
	"charge_weapon": InputValue.Actions.CHARGE_WEAPON, "zoom_in": InputValue.Actions.ZOOM_IN,
	"zoom_out": InputValue.Actions.ZOOM_OUT}
const EDGE_FIELDS: Array[String] = ["toggle_mode", "fire", "reset", "skip_panning", "change_weapon", "zoom_in", "zoom_out"]


class Tape extends RefCounted:
	var _record: Dictionary
	var _validate: Callable
	var _serialize: Callable

	# Static operation references are injected by this module. No script cache,
	# dynamic load or mutable outer instance is needed by the detached value.
	func _init(record: Dictionary, validator: Callable, serializer: Callable) -> void:
		_record = record.duplicate(true)
		_validate = validator
		_serialize = serializer

	## Every public read detaches arrays/dictionaries, including string units.
	func snapshot() -> Dictionary:
		return _record.duplicate(true)

	func spans() -> Variant:
		return null if _record.spans == null else _record.spans.duplicate(true)

	func seed() -> int:
		return _record.seed

	func duration_ticks() -> int:
		return _record.duration_ticks

	func name_units() -> Variant:
		return null if _record.name == null else _record.name.duplicate()

	func name_utf8_bytes() -> Dictionary:
		return Text.utf8_bytes(_record.name)

	func name_text() -> Dictionary:
		return Text.native_string(_record.name)

	func validate() -> Dictionary:
		return _validate.call(_record)

	func serialize() -> Dictionary:
		return _serialize.call(_record)

	func identity() -> Dictionary:
		var encoded: Dictionary = serialize()
		if not encoded.ok:
			return encoded
		var hash: RefCounted = Sha.new()
		var appended: Dictionary = hash.append(String(encoded.value).to_ascii_buffer())
		if not appended.ok:
			return appended
		var result: Dictionary = hash.current_hex()
		hash.dispose()
		return result


class Reader extends RefCounted:
	var _record: Dictionary
	var _fail: Callable
	var _ending: Callable
	var _input: Callable
	var _span_index: int = 0
	var _next_tick: int = 0

	func _init(tape: Tape, failure: Callable, ending: Callable, input: Callable) -> void:
		_record = tape.snapshot()
		_fail = failure
		_ending = ending
		_input = input

	func next_tick() -> int:
		return _next_tick

	func span_index() -> int:
		return _span_index

	## Deliberately does not add Validate: the C# reader assumes a validated
	## tape. Its cursor changes before a later malformed-span failure remain
	## observable to the oracle and are preserved here as explicit errors.
	func read_next(tick: Variant) -> Dictionary:
		if typeof(tick) != TYPE_INT or tick < -2147483648 or tick > 2147483647:
			return _fail.call("ArgumentException", "argument", "Reader tick must fit int32.")
		if tick != _next_tick or tick < 0 or tick >= int(_record.duration_ticks):
			return _fail.call("InvalidOperationException", "reader_tick", "Command tape reader expected tick %d, not %d." % [_next_tick, tick])
		if _record.spans == null:
			return _fail.call("NullReferenceException", "null_reference", "The reader tape has null spans.")
		var spans: Array = _record.spans
		while _span_index < spans.size():
			if spans[_span_index] == null:
				return _fail.call("NullReferenceException", "null_reference", "The reader reached a null span.")
			var ending: Dictionary = _ending.call(spans[_span_index])
			if not ending.ok:
				return ending
			if int(ending.value) > tick:
				break
			_span_index += 1
		var input: Dictionary = InputValue.idle()
		if _span_index < spans.size():
			var span: Dictionary = spans[_span_index]
			if tick >= int(span.start_tick):
				var ending: Dictionary = _ending.call(span)
				if not ending.ok:
					return ending
				if tick < int(ending.value):
					input = _input.call(span)
		_next_tick += 1
		return {"ok": true, "value": input}


## Constructor-width admission only, matching the C# record constructor.
## Call validate before gameplay. Strings may be String, UTF-16 units or null.
## Missing fields retain JsonConstructor defaults, not inferred simulation values.
static func create_tape(record: Variant) -> Dictionary:
	if record == null:
		return _failure("ArgumentNullException", "null_argument", "Tape record is required.", "record")
	if typeof(record) != TYPE_DICTIONARY:
		return _failure("ArgumentException", "argument", "Tape record must be a dictionary.")
	for field: Variant in record:
		if not ROOT_MEMBERS.values().has(field):
			return _failure("ArgumentException", "argument", "Unknown tape record field.")
	var copy: Dictionary = {}
	for field: String in STRING_FIELDS:
		var text: Dictionary = Text.units(record.get(field))
		if not text.ok:
			return text
		copy[field] = text.value
	for field: String in ["seed", "duration_ticks"]:
		var number: Variant = record.get(field, 0)
		var low: int = 0 if field == "seed" else -2147483648
		var high: int = 4294967295 if field == "seed" else 2147483647
		if typeof(number) != TYPE_INT or number < low or number > high:
			return _failure("ArgumentException", "argument", "Tape numeric field exceeds its C# width: " + field)
		copy[field] = int(number)
	var spans: Variant = record.get("spans")
	if spans == null:
		copy.spans = null
	elif typeof(spans) != TYPE_ARRAY:
		return _failure("ArgumentException", "argument", "Tape spans must be an array or null.")
	else:
		var copied_spans: Array = []
		for span: Variant in spans:
			if span == null:
				copied_spans.append(null)
				continue
			var admitted: Dictionary = create_span(span)
			if not admitted.ok:
				return admitted
			copied_spans.append(admitted.value)
		copy.spans = copied_spans
	return {"ok": true, "value": Tape.new(copy, _validate_record, _serialize_record)}


static func create_span(fields: Variant) -> Dictionary:
	if typeof(fields) != TYPE_DICTIONARY:
		return _failure("ArgumentException", "argument", "Span must be a field dictionary.")
	for field: Variant in fields:
		if not SPAN_MEMBERS.values().has(field):
			return _failure("ArgumentException", "argument", "Unknown span record field.")
	var span: Dictionary = _empty_span()
	for field: String in fields:
		if SPAN_RANGES.has(field):
			if typeof(fields[field]) != TYPE_INT or fields[field] < SPAN_RANGES[field][0] or fields[field] > SPAN_RANGES[field][1]:
				return _failure("ArgumentException", "argument", "Span field exceeds its C# integer width: " + field)
		else:
			if typeof(fields[field]) != TYPE_BOOL:
				return _failure("ArgumentException", "argument", "Span action must be boolean: " + field)
		span[field] = fields[field]
	return {"ok": true, "value": span}


static func span_end_tick(span: Variant) -> Dictionary:
	var admitted: Dictionary = create_span(span)
	return _end_tick(admitted.value) if admitted.ok else admitted


static func span_to_input(span: Variant) -> Dictionary:
	var admitted: Dictionary = create_span(span)
	return {"ok": true, "value": _to_input(admitted.value)} if admitted.ok else admitted


static func validate(tape: Variant) -> Dictionary:
	var admitted: Dictionary = _require_tape(tape)
	return tape.validate() if admitted.ok else admitted


static func serialize(tape: Variant) -> Dictionary:
	var admitted: Dictionary = _require_tape(tape)
	return tape.serialize() if admitted.ok else admitted


static func serialize_bytes(tape: Variant) -> Dictionary:
	var encoded: Dictionary = serialize(tape)
	return {"ok": true, "bytes": String(encoded.value).to_ascii_buffer()} if encoded.ok else encoded


static func identity_of(tape: Variant) -> Dictionary:
	var admitted: Dictionary = _require_tape(tape)
	return tape.identity() if admitted.ok else admitted


static func new_reader(tape: Variant) -> Dictionary:
	var admitted: Dictionary = _require_tape(tape)
	return {"ok": true, "value": Reader.new(tape, _failure, _end_tick, _to_input)} if admitted.ok else admitted


## UTF-8 bytes are intentional: parsing a wire document through native Godot
## String first could lose a literal NUL before grammar admission sees it.
static func deserialize_bytes(source: Variant) -> Dictionary:
	if source == null:
		return _failure("ArgumentNullException", "null_argument", "JSON input is required.", "json")
	if typeof(source) != TYPE_PACKED_BYTE_ARRAY:
		return _failure("ArgumentException", "argument", "JSON input must be its original UTF-8 bytes.")
	if _only_dotnet_whitespace(source):
		return _failure("ArgumentException", "argument", "JSON input must not be empty or whitespace.", "json")
	# Parse the ENTIRE grammar first. Duplicate detection during parsing would
	# incorrectly win over a later syntax error, unlike JsonDocument.Parse.
	var parsed: Dictionary = Strict.parse_bytes(source, false)
	if not parsed.ok:
		return _failure("JsonReaderException", "json", parsed.error)
	var root: Strict.Value = parsed.value
	var unique: Dictionary = _validate_unique(root)
	if not unique.ok:
		return unique
	if root.kind == "null":
		return _failure("InvalidDataException", "not_document", "Command tape JSON did not contain a document.")
	var decoded: Dictionary = _decode_tape(root)
	if not decoded.ok:
		return decoded
	var record: Dictionary = decoded.value
	if Text.equals_text(record.schema_version, PREVIOUS_SCHEMA):
		var previous: Dictionary = _validate_previous_field_set(root)
		if not previous.ok:
			return previous
		record.schema_version = Text.units(CURRENT_SCHEMA).value
	var checked: Dictionary = _validate_record(record)
	if not checked.ok:
		return checked
	return {"ok": true, "value": Tape.new(record, _validate_record, _serialize_record)}


static func _decode_tape(root: Strict.Value) -> Dictionary:
	if root.kind != "object":
		return _failure("JsonException", "json", "Tape JSON must be an object.")
	var record: Dictionary = {"schema_version": null, "name": null, "seed": 0, "duration_ticks": 0,
		"expected_final_state_hash": null, "expected_trace_hash": null, "spans": null}
	# Conversion follows JSON property encounter order. Validation occurs only
	# after all fields, including every span, have been deserialized.
	for member: Dictionary in root.members:
		var field: String = _known_field(member.name, ROOT_MEMBERS)
		if field.is_empty():
			return _failure("JsonException", "json", "Unmapped command tape member.")
		var value: Strict.Value = member.value
		if STRING_FIELDS.has(field):
			var text: Dictionary = _json_string(value)
			if not text.ok:
				return text
			record[field] = text.value
		elif field == "spans":
			if value.kind == "null":
				record.spans = null
			elif value.kind != "array":
				return _failure("JsonException", "json", "Spans JSON must be an array or null.")
			else:
				var spans: Array = []
				for item: Strict.Value in value.items:
					if item.kind == "null":
						spans.append(null)
						continue
					var decoded: Dictionary = _decode_span(item)
					if not decoded.ok:
						return decoded
					spans.append(decoded.value)
				record.spans = spans
		else:
			var number: Dictionary = _json_integer(value, 0 if field == "seed" else -2147483648,
				4294967295 if field == "seed" else 2147483647, field == "seed")
			if not number.ok:
				return number
			record[field] = number.value
	return {"ok": true, "value": record}


static func _decode_span(value: Strict.Value) -> Dictionary:
	if value.kind != "object":
		return _failure("JsonException", "json", "Span JSON must be an object or null.")
	var span: Dictionary = _empty_span()
	for member: Dictionary in value.members:
		var field: String = _known_field(member.name, SPAN_MEMBERS)
		if field.is_empty():
			return _failure("JsonException", "json", "Unmapped command span member.")
		var field_value: Strict.Value = member.value
		if SPAN_RANGES.has(field):
			var number: Dictionary = _json_integer(field_value, SPAN_RANGES[field][0], SPAN_RANGES[field][1])
			if not number.ok:
				return number
			span[field] = number.value
		else:
			if field_value.kind != "boolean":
				return _failure("JsonException", "json", "Span action JSON must be boolean.")
			span[field] = field_value.boolean
	return {"ok": true, "value": span}


static func _validate_unique(value: Strict.Value) -> Dictionary:
	if value.kind == "object":
		var names: Dictionary = {}
		for member: Dictionary in value.members:
			var name: Strict.Value = member.name
			if not name.utf8_bytes().ok:
				return _failure("InvalidOperationException", "invalid_operation", "Invalid UTF-16 property name.")
			var key: String = name.string_units.to_byte_array().hex_encode()
			if names.has(key):
				return _failure("InvalidDataException", "duplicate_member", "Duplicate command tape JSON member.")
			names[key] = true
			var nested: Dictionary = _validate_unique(member.value)
			if not nested.ok:
				return nested
	elif value.kind == "array":
		for item: Strict.Value in value.items:
			var nested: Dictionary = _validate_unique(item)
			if not nested.ok:
				return nested
	return {"ok": true}


static func _validate_previous_field_set(root: Strict.Value) -> Dictionary:
	var spans: Strict.Value = root.member("spans")
	if spans == null or spans.kind != "array":
		return {"ok": true}
	for span: Strict.Value in spans.items:
		if span.kind == "object" and (span.member("chargeWeapon") != null or span.member("zoomIn") != null or span.member("zoomOut") != null):
			return _failure("InvalidDataException", "v4_fieldset", "A v4 command tape cannot contain the v5-only chargeWeapon, zoomIn or zoomOut members.")
	return {"ok": true}


static func _validate_record(record: Dictionary) -> Dictionary:
	if not Text.equals_text(record.schema_version, CURRENT_SCHEMA):
		return _failure("InvalidDataException", "schema", "Unsupported command tape schema.")
	if Text.is_null_or_white_space(record.name):
		return _failure("InvalidDataException", "name", "Command tape name is required.")
	if int(record.seed) == 0:
		return _failure("InvalidDataException", "seed", "Command tape seed must be nonzero.")
	if int(record.duration_ticks) < 1 or int(record.duration_ticks) > 1000000:
		return _failure("InvalidDataException", "duration", "Command tape duration must be between 1 and 1,000,000 ticks.")
	for field: String in ["expected_final_state_hash", "expected_trace_hash"]:
		var hash: Variant = record[field]
		if hash == null:
			continue
		var valid: bool = hash.size() == 64
		for unit: int in hash:
			if not ((unit >= 48 and unit <= 57) or (unit >= 65 and unit <= 70) or (unit >= 97 and unit <= 102)):
				valid = false
		if not valid:
			var code: String = "final_hash" if field == "expected_final_state_hash" else "trace_hash"
			return _failure("InvalidDataException", code, "Expected hash must be a 64-character SHA-256 hex value.")
	if record.spans == null:
		return _failure("InvalidDataException", "spans_required", "Command tape spans are required.")
	var previous_end: int = 0
	for span: Variant in record.spans:
		if span == null:
			return _failure("InvalidDataException", "null_span", "Command tape spans cannot contain null entries.")
		if int(span.start_tick) < previous_end or int(span.start_tick) < 0:
			return _failure("InvalidDataException", "span_order", "Command spans must be sorted and non-overlapping.")
		var ending: Dictionary = _end_tick(span)
		if not ending.ok:
			return _failure("InvalidDataException", "span_overflow", "Command span end tick exceeds the supported range.")
		if int(span.duration_ticks) <= 0 or int(ending.value) > int(record.duration_ticks):
			return _failure("InvalidDataException", "span_duration", "Command span is outside the tape duration.")
		var input_check: Dictionary = InputValue.validate(_to_input(span))
		if not input_check.ok:
			var error: Dictionary = _failure("InvalidDataException", "span_input", "Command span contains invalid input values.")
			error.inner_parameter = input_check.parameter
			return error
		for field: String in EDGE_FIELDS:
			if span[field] and int(span.duration_ticks) != 1:
				return _failure("InvalidDataException", "edge_duration", "ToggleMode, Fire, Reset, SkipPanning, ChangeWeapon, ZoomIn and ZoomOut are edge actions and require a one-tick span.")
		previous_end = ending.value
	return {"ok": true}


static func _serialize_record(record: Dictionary) -> Dictionary:
	var checked: Dictionary = _validate_record(record)
	if not checked.ok:
		return checked
	var lines: Array[String] = ["{"]
	for json_name: String in ROOT_MEMBERS:
		var field: String = ROOT_MEMBERS[json_name]
		if field == "spans":
			continue
		var value: String = Text.quote(record[field]).value if STRING_FIELDS.has(field) else str(record[field])
		lines.append('  "%s": %s,' % [json_name, value])
	var spans: Array = record.spans
	if spans.is_empty():
		lines.append('  "spans": []')
	else:
		lines.append('  "spans": [')
		for index: int in range(spans.size()):
			var span: Dictionary = spans[index]
			lines.append("    {")
			var field_index: int = 0
			for json_name: String in SPAN_MEMBERS:
				var field: String = SPAN_MEMBERS[json_name]
				var value: String = str(span[field]) if SPAN_RANGES.has(field) else "true" if span[field] else "false"
				var comma: String = "," if field_index < SPAN_MEMBERS.size() - 1 else ""
				lines.append('      "%s": %s%s' % [json_name, value, comma])
				field_index += 1
			lines.append("    }" + ("," if index < spans.size() - 1 else ""))
		lines.append("  ]")
	lines.append("}")
	return {"ok": true, "value": "\n".join(lines) + "\n"}


static func _empty_span() -> Dictionary:
	var span: Dictionary = {}
	for field: String in SPAN_MEMBERS.values():
		span[field] = 0 if SPAN_RANGES.has(field) else false
	return span


static func _to_input(span: Dictionary) -> Dictionary:
	var actions: int = 0
	for field: String in ACTIONS:
		if span[field]:
			actions |= int(ACTIONS[field])
	return {"move_x": span.move_x, "move_z": span.move_z, "actions": actions,
		"look_x": span.look_x, "look_y": span.look_y,
		"look_x_analog_permille": span.look_x_analog_permille, "look_y_analog_permille": span.look_y_analog_permille}


static func _end_tick(span: Dictionary) -> Dictionary:
	var end: int = int(span.start_tick) + int(span.duration_ticks)
	if end < -2147483648 or end > 2147483647:
		return _failure("OverflowException", "overflow", "Span end exceeds int32.")
	return {"ok": true, "value": end}


static func _json_integer(value: Strict.Value, low: int, high: int, unsigned: bool = false) -> Dictionary:
	var integer: Dictionary = value.as_int64()
	if not integer.ok or (unsigned and value.number_text.begins_with("-")):
		return _failure("JsonException", "json", "Expected a JSON integer in the declared width.")
	if int(integer.value) < low or int(integer.value) > high:
		return _failure("JsonException", "json", "JSON integer exceeds its declared width.")
	return integer


static func _json_string(value: Strict.Value) -> Dictionary:
	if value.kind == "null":
		return {"ok": true, "value": null}
	if value.kind != "string":
		return _failure("JsonException", "json", "Expected a JSON string or null.")
	if not value.utf8_bytes().ok:
		return _failure("JsonException", "json", "Invalid UTF-16 string value.")
	return {"ok": true, "value": value.string_units.duplicate()}


static func _known_field(name: Strict.Value, members: Dictionary) -> String:
	for text: String in members:
		if Text.equals_text(name.string_units, text):
			return members[text]
	return ""


static func _only_dotnet_whitespace(source: PackedByteArray) -> bool:
	var whites: Array[PackedByteArray] = []
	for unit: int in [9, 10, 11, 12, 13, 32, 0x85, 0xa0, 0x1680, 0x2000, 0x2001, 0x2002,
			0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008, 0x2009, 0x200a, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000]:
		whites.append(String.chr(unit).to_utf8_buffer())
	var offset: int = 0
	while offset < source.size():
		var found: bool = false
		for white: PackedByteArray in whites:
			if source.slice(offset, offset + white.size()) == white:
				offset += white.size()
				found = true
				break
		if not found:
			return false
	return true


static func _require_tape(tape: Variant) -> Dictionary:
	if tape == null:
		return _failure("ArgumentNullException", "null_argument", "Tape is required.", "tape")
	if not tape is Tape:
		return _failure("ArgumentException", "argument", "Expected a CommandTape value.")
	return {"ok": true}


static func _failure(kind: String, code: String, message: String, parameter: String = "") -> Dictionary:
	return {"ok": false, "error_type": kind, "error_code": code, "error": message,
		"parameter": parameter, "inner_parameter": ""}
