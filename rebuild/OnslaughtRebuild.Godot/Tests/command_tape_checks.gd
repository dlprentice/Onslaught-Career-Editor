# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Differential fixtures only. The production input/tape/reader modules have
## no filesystem access; this runner reads public synthetic oracle data and
## writes its result to the explicit owned path selected by the existing gate.

const TapeCodec = preload("res://Core/command_tape.gd")
const InputValue = preload("res://Core/sim_input.gd")
const Text = preload("res://Core/canonical_json_string.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var completed: Array[String] = []


func _initialize() -> void:
	call_deferred("run_checks")


func check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func integer(value: Variant, name: String) -> int:
	check("fixture", name, typeof(value) in [TYPE_FLOAT, TYPE_INT] and is_finite(float(value))
		and float(value) == floor(float(value)) and absf(float(value)) <= 4294967295.0, true)
	return int(value)


func units(value: Variant) -> Variant:
	if value == null:
		return null
	var result := PackedInt32Array()
	for unit: Variant in value:
		var code: int = integer(unit, "UTF-16 unit")
		check("fixture", "UTF-16 unit width", code >= 0 and code <= 65535, true)
		result.append(code)
	return result


func input_record(row: Dictionary) -> Dictionary:
	var input: Dictionary = {}
	for field: String in InputValue.FIELDS:
		input[field] = integer(row[field], "input:" + field)
	return input


func tape_record(row: Dictionary) -> Dictionary:
	var record: Dictionary = {}
	for field: String in TapeCodec.STRING_FIELDS:
		record[field] = units(row[field])
	record.seed = integer(row.seed, "seed")
	record.duration_ticks = integer(row.duration_ticks, "duration")
	if row.spans == null:
		record.spans = null
	else:
		var spans: Array = []
		for source: Variant in row.spans:
			if source == null:
				spans.append(null)
				continue
			var span: Dictionary = {}
			for field: String in TapeCodec.SPAN_MEMBERS.values():
				if TapeCodec.SPAN_RANGES.has(field):
					span[field] = integer(source[field], "span:" + field)
				else:
					check("fixture", "boolean:" + field, typeof(source[field]), TYPE_BOOL)
					span[field] = source[field]
			spans.append(span)
		record.spans = spans
	return record


func compare_result(group: String, name: String, actual: Dictionary, expected: Dictionary) -> bool:
	check(group, name + ":ok", actual.get("ok"), expected.ok)
	if not expected.ok:
		for field: String in ["error_type", "error_code", "parameter", "inner_parameter"]:
			check(group, name + ":" + field, actual.get(field, ""), expected[field])
	return actual.get("ok", false) and expected.ok


func compare_tape(name: String, tape: RefCounted, expected: Dictionary) -> void:
	check("record", name, tape.snapshot(), tape_record(expected.tape))
	var encoded: Dictionary = TapeCodec.serialize_bytes(tape)
	check("serialization", name + ":ok", encoded.ok, true)
	if encoded.ok:
		check("serialization", name, encoded.bytes.hex_encode(), expected.canonical_hex)
		check("serialization", name + ":LF_only", not encoded.bytes.has(13) and encoded.bytes[-1] == 10, true)
	var identity: Dictionary = TapeCodec.identity_of(tape)
	check("identity", name + ":ok", identity.ok, true)
	if identity.ok:
		check("identity", name, identity.value, expected.identity)
	var changed: Dictionary = tape.snapshot()
	changed.seed = 0
	if changed.name != null and not changed.name.is_empty():
		changed.name[0] = 0
	if changed.spans != null:
		if not changed.spans.is_empty() and changed.spans[0] != null:
			changed.spans[0].move_x = 127
		changed.spans.clear()
	var spans: Variant = tape.spans()
	if spans != null:
		spans.clear()
	check("detached", name + ":snapshot_and_spans", tape.snapshot(), tape_record(expected.tape))
	if encoded.ok:
		check("detached", name + ":canonical", TapeCodec.serialize_bytes(tape).bytes.hex_encode(), expected.canonical_hex)
		var roundtrip: Dictionary = TapeCodec.deserialize_bytes(encoded.bytes)
		check("roundtrip", name + ":ok", roundtrip.ok, true)
		if roundtrip.ok:
			# A raw C# constructor can contain unpaired UTF-16. The encoder's
			# replacement makes canonical bytes/identity stable across reading;
			# it does not claim the original raw string units survived replacement.
			check("roundtrip", name + ":identity", TapeCodec.identity_of(roundtrip.value).value, expected.identity)


func check_json(rows: Array) -> void:
	check("fixture", "JSON cases present", rows.is_empty(), false)
	for row: Dictionary in rows:
		var source: Variant = null if row.json_hex == null else String(row.json_hex).hex_decode()
		var result: Dictionary = TapeCodec.deserialize_bytes(source)
		if compare_result("json_admission", row.name, result, row.expected):
			compare_tape(row.name, result.value, row.expected)
	completed.append("json")


func check_validation(rows: Array) -> void:
	check("fixture", "direct validation cases present", rows.is_empty(), false)
	for row: Dictionary in rows:
		var record: Dictionary = tape_record(row.tape)
		var created: Dictionary = TapeCodec.create_tape(record)
		check("construction", row.name, created.ok, true)
		if not created.ok:
			continue
		var tape: RefCounted = created.value
		record.clear()
		var result: Dictionary = TapeCodec.validate(tape)
		if compare_result("validation", row.name, result, row.expected):
			compare_tape(row.name, tape, row.expected)
		else:
			compare_result("serialization_refusal", row.name, TapeCodec.serialize(tape), row.expected)
			compare_result("identity_refusal", row.name, TapeCodec.identity_of(tape), row.expected)
	completed.append("validation")


func check_inputs(rows: Array) -> void:
	check("fixture", "input cases present", rows.is_empty(), false)
	for row: Dictionary in rows:
		var input: Dictionary = input_record(row.input)
		var created: Dictionary = InputValue.create(input.move_x, input.move_z, input.actions, input.look_x, input.look_y,
			input.look_x_analog_permille, input.look_y_analog_permille)
		check("input_widths", row.name, created.ok, true)
		if not created.ok:
			continue
		check("input_widths", row.name + ":record", created.value, input)
		compare_result("input_validation", row.name, InputValue.validate(created.value), row.validation)
		for action: Dictionary in row.actions:
			var actual: Dictionary = InputValue.has_action(created.value, integer(action.action, "requested action"))
			check("has_action", row.name + ":ok", actual.ok, true)
			if actual.ok:
				check("has_action", row.name + ":" + str(action.action), actual.value, action.value)
		created.value.move_x = 127
		check("detached", row.name + ":input", input, input_record(row.input))
	var idle: Dictionary = InputValue.idle()
	idle.actions = 65535
	check("detached", "idle", InputValue.idle().actions, 0)
	completed.append("inputs")


func check_strings(rows: Array) -> void:
	check("fixture", "string cases present", rows.is_empty(), false)
	for row: Dictionary in rows:
		var raw: PackedInt32Array = units(row.units)
		var encoded: Dictionary = Text.quote(raw)
		check("json_string", row.name + ":ok", encoded.ok, true)
		if encoded.ok:
			check("json_string", row.name, String(encoded.value).to_ascii_buffer().hex_encode(), row.canonical_hex)
	var nul := PackedInt32Array([65, 0, 0xd83d, 0xde80])
	check("string_boundary", "raw UTF8 preserves NUL and non-BMP", Text.utf8_bytes(nul).value.hex_encode(), "4100f09f9a80")
	check("string_boundary", "native String refuses NUL", Text.native_string(nul).ok, false)
	check("string_boundary", "units detached", Text.units(nul).value, nul)
	completed.append("strings")


func check_readers(rows: Array) -> void:
	check("fixture", "reader cases present", rows.is_empty(), false)
	for row: Dictionary in rows:
		var tape: RefCounted = null
		if row.tape != null:
			var record: Dictionary = tape_record(row.tape)
			var created: Dictionary = TapeCodec.create_tape(record)
			check("reader_construction", row.name + ":record", created.ok, true)
			if not created.ok:
				continue
			tape = created.value
			record.clear()
		var created: Dictionary = TapeCodec.new_reader(tape)
		if not compare_result("reader_construction", row.name, created, row.construction):
			continue
		var reader: RefCounted = created.value
		for step: Dictionary in row.steps:
			var tick: int = integer(step.tick, "reader tick")
			var name: String = row.name + ":" + str(tick)
			var result: Dictionary = reader.read_next(tick)
			if compare_result("reader", name, result, step.result):
				check("reader_input", name, result.value, input_record(step.result.input))
				result.value.move_x = 127
				result.value.clear()
			check("reader_cursor", name + ":next", reader.next_tick(), integer(step.next_tick, "next tick"))
			check("reader_cursor", name + ":span", reader.span_index(), integer(step.span_index, "span index"))
	completed.append("readers")


func check_boundary_errors() -> void:
	for source: Variant in ["{}", 0, [], {}, true]:
		check("explicit_admission", "wire requires bytes", TapeCodec.deserialize_bytes(source).ok, false)
	for source: Variant in [0, [], false, "tape"]:
		check("explicit_admission", "create requires record", TapeCodec.create_tape(source).ok, false)
	for source: Variant in [null, {}, 0, false]:
		check("explicit_admission", "identity requires tape", TapeCodec.identity_of(source).ok, false)
		check("explicit_admission", "serialize requires tape", TapeCodec.serialize(source).ok, false)
	for field: String in InputValue.FIELDS:
		var input: Dictionary = InputValue.idle()
		input.erase(field)
		check("explicit_admission", "missing input:" + field, InputValue.validate(input).ok, false)
		for invalid: Variant in [null, true, 0.0, "0", 4294967296, -4294967296]:
			input = InputValue.idle()
			input[field] = invalid
			check("explicit_admission", "input width/type:" + field, InputValue.admit_record(input).ok, false)
	for field: String in TapeCodec.SPAN_RANGES:
		for invalid: Variant in [null, false, 0.0, "0", int(TapeCodec.SPAN_RANGES[field][0]) - 1, int(TapeCodec.SPAN_RANGES[field][1]) + 1]:
			check("explicit_admission", "span width/type:" + field, TapeCodec.create_span({field: invalid}).ok, false)
	for field: String in TapeCodec.ACTIONS:
		check("explicit_admission", "span bool:" + field, TapeCodec.create_span({field: 1}).ok, false)
	check("span", "checked end overflow", TapeCodec.span_end_tick({"start_tick": 2147483647, "duration_ticks": 1}).error_type, "OverflowException")
	check("span", "input keeps held actions", TapeCodec.span_to_input({"landing_jets": true, "charge_weapon": true}).value.actions, 40)
	completed.append("boundary")


func run_checks() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if typeof(data) != TYPE_DICTIONARY or not data.has("command_tape"):
		quit(2)
		return
	var fixtures: Dictionary = data.command_tape
	check("constants", "current schema", TapeCodec.CURRENT_SCHEMA, fixtures.constants.current_schema)
	check("constants", "previous schema", TapeCodec.PREVIOUS_SCHEMA, fixtures.constants.previous_schema)
	check("constants", "declared actions", InputValue.DECLARED_ACTIONS, integer(fixtures.constants.declared_actions, "declared mask"))
	check("constants", "implemented actions", InputValue.IMPLEMENTED_ACTIONS, integer(fixtures.constants.implemented_actions, "implemented mask"))
	check_json(fixtures.json_cases)
	check_validation(fixtures.validation)
	check_inputs(fixtures.inputs)
	check_strings(fixtures.strings)
	check_readers(fixtures.readers)
	check_boundary_errors()
	for group: String in ["json", "validation", "inputs", "strings", "readers", "boundary"]:
		check("completion", group, completed.has(group), true)
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"failures": failures, "completed": completed}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify({"failure_count": failures.size(), "counts": counts, "first_failures": failures.slice(0, 4)}))
	quit(0 if failures.is_empty() else 1)
