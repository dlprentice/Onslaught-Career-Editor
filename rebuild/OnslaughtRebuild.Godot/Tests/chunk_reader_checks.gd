# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Synthetic inputs from TestSupport/GdscriptChunkReaderOracle.cs only.
## Arguments follow the existing differential gate: oracle JSON, report JSON.

const Reader = preload("res://Core/retail_chunk_reader.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var _completed_sections: Dictionary = {}


func _initialize() -> void:
	call_deferred("run_checks")


func check(category: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[category] = int(counts.get(category, 0)) + 1
	if actual != expected:
		failures.append({"category": category, "name": name, "actual": actual, "expected": expected})


func fixture_integer(value: Variant, name: String) -> int:
	# JSON uses doubles, but every number in this fixture fits exact int32/uint32.
	var valid: bool = (typeof(value) == TYPE_FLOAT or typeof(value) == TYPE_INT) and \
		is_finite(float(value)) and float(value) == floor(float(value)) and \
		float(value) >= -2147483648.0 and float(value) <= 4294967295.0
	check("fixture_integer", name, valid, true)
	return int(value) if valid else 0


func expected_state(value: Dictionary, name: String) -> Dictionary:
	var result: Dictionary = value.duplicate(true)
	for field: String in ["size", "read_since_chunk", "position", "remaining"]:
		result[field] = fixture_integer(result[field], name + ":" + field)
	if result.reader_position != null:
		result.reader_position = fixture_integer(result.reader_position, name + ":reader_position")
	return result


func check_oracle(cases: Array) -> void:
	check("fixture", "nonempty_cases", not cases.is_empty(), true)
	for item: Dictionary in cases:
		var source: PackedByteArray = String(item.hex).hex_decode()
		var buffer := Reader.MemBuffer.new(source)
		var reader := Reader.new()
		var attached: bool = false
		check("fixture", String(item.name) + ":nonempty_operations", not item.rows.is_empty(), true)
		for index: int in range(item.rows.size()):
			var row: Dictionary = item.rows[index]
			var name: String = String(item.name) + ":" + str(index) + ":" + String(row.operation)
			var destination: PackedByteArray = source if row.operation == "buffer_read_alias" else String(row.destination).hex_decode()
			check("fixture", name + ":destination", destination.hex_encode(), row.destination)
			var result: Dictionary = {}
			match row.operation:
				"open":
					result = reader.open_existing_buffer(buffer)
					if result.ok:
						result.value = result.value == buffer
						attached = true
				"open_null": result = reader.open_existing_buffer(null)
				"new_reader":
					reader = Reader.new()
					attached = false
					result = {"ok": true, "value": null, "complete": true}
				"where": result = reader.where_am_i()
				"get_next": result = reader.get_next()
				"read": result = reader.read(destination, fixture_integer(row["size"], name + ":size"), fixture_integer(row.count, name + ":count"))
				"skip": result = reader.skip()
				"close": result = reader.close()
				"buffer_read", "buffer_read_alias": result = buffer.read(destination, fixture_integer(row.number, name + ":number"))
				"buffer_skip": result = buffer.skip(fixture_integer(row.number, name + ":number"))
				"buffer_close": result = buffer.close()
				"mutate_source":
					source[fixture_integer(row.index, name + ":index")] = fixture_integer(row.octet, name + ":octet")
					result = {"ok": true, "value": null, "complete": true}
				_:
					check("fixture", name + ":known_operation", false, true)
					result = {"ok": false, "error_type": "UnknownFixtureOperation"}
			check("exception_admission", name, result.ok, String(row.error).is_empty())
			if result.ok and String(row.error).is_empty():
				var expected: Variant = row.returned
				if typeof(expected) == TYPE_FLOAT:
					expected = fixture_integer(expected, name + ":returned")
				check("retail_return", name, result.value, expected)
				check("completion", name, result.complete, row.complete)
			elif not result.ok:
				check("exception_type", name, result.error_type, row.error)
			check("payload_bytes", name, destination.hex_encode(), row.destination_after)
			var actual_state: Dictionary = {
				"size": reader.get_size(), "read_since_chunk": reader.get_read_since_chunk(),
				"position": buffer.where_am_i(), "remaining": buffer.remaining(), "eof": buffer.end_of_file(),
				"reader_position": buffer.where_am_i() if attached else null, "source": source.hex_encode(),
			}
			check("cursor_and_accounting", name, actual_state, expected_state(row.state, name))
	_completed_sections["oracle"] = true


func check_failure_admission() -> void:
	var reader := Reader.new()
	check("wrapper_admission", "unopened_cursor", reader.where_am_i().ok, false)
	check("wrapper_admission", "unopened_failure_is_sticky", reader.read(PackedByteArray(), 0, 0).ok, false)
	var replacement := Reader.MemBuffer.new(PackedByteArray([1, 2]))
	check("wrapper_admission", "explicit_adopt_recovers_reader", reader.open_existing_buffer(replacement).ok, true)
	var destination := PackedByteArray([0xcc, 0xcc])
	check("wrapper_admission", "recovered_read", reader.read(destination, 2, 1).value, true)
	check("wrapper_admission", "recovered_payload", destination, PackedByteArray([1, 2]))
	check("wrapper_admission", "exact_end_has_no_eof", replacement.end_of_file(), false)

	var invalid_buffer := Reader.MemBuffer.new(null)
	check("wrapper_admission", "null_buffer", invalid_buffer.error().error_type, "ArgumentNullException")
	check("wrapper_admission", "invalid_buffer_read", invalid_buffer.read(PackedByteArray(), 0).ok, false)
	check("wrapper_admission", "invalid_buffer_close", invalid_buffer.close().ok, false)
	check("wrapper_admission", "cannot_adopt_failed_buffer", reader.open_existing_buffer(invalid_buffer).ok, false)
	check("wrapper_admission", "failed_buffer_cannot_report_zero_read_success", reader.read(PackedByteArray(), 0, 0).ok, false)

	for invalid: Variant in [null, true, 1.5, "1", -1, 4294967296]:
		for field: int in range(2):
			reader = Reader.new()
			var buffer := Reader.MemBuffer.new(PackedByteArray([1, 2, 3, 4]))
			reader.open_existing_buffer(buffer)
			var result: Dictionary = reader.read(PackedByteArray([0, 0, 0, 0]), invalid if field == 0 else 1, invalid if field == 1 else 1)
			check("wrapper_admission", "u32_without_coercion", result.ok, false)
			check("wrapper_admission", "argument_failure_keeps_counter", reader.get_read_since_chunk(), 0)
			check("wrapper_admission", "argument_failure_keeps_cursor", buffer.where_am_i(), 0)
			check("wrapper_admission", "argument_failure_terminal", reader.read(PackedByteArray(), 0, 0).ok, false)

	for invalid: Variant in [null, true, 1.5, "1", -2147483649, 2147483648]:
		var buffer := Reader.MemBuffer.new(PackedByteArray([1]))
		check("wrapper_admission", "signed_count_without_coercion", buffer.skip(invalid).ok, false)
		check("wrapper_admission", "signed_count_failure_terminal", buffer.read(PackedByteArray([0]), 1).ok, false)
		check("wrapper_admission", "signed_count_failure_keeps_cursor", buffer.where_am_i(), 0)

	reader = Reader.new()
	var buffer := Reader.MemBuffer.new(PackedByteArray([1, 2, 3, 4]))
	reader.open_existing_buffer(buffer)
	check("wrapper_admission", "bad_destination", reader.read(null, 4, 1).ok, false)
	check("wrapper_admission", "charge_precedes_buffer_failure", reader.get_read_since_chunk(), 4)
	check("wrapper_admission", "bad_destination_keeps_cursor", buffer.where_am_i(), 0)
	check("wrapper_admission", "buffer_failure_terminal", reader.get_next().ok, false)
	check("wrapper_admission", "terminal_call_preserves_accounting", reader.get_read_since_chunk(), 4)

	var aliased := PackedByteArray([1])
	buffer = Reader.MemBuffer.new(aliased)
	aliased.append(2)
	check("wrapper_admission", "resized_array_is_not_a_fixed_csharp_array", buffer.read(PackedByteArray([0]), 1).ok, false)
	check("wrapper_admission", "resize_failure_keeps_cursor", buffer.where_am_i(), 0)
	_completed_sections["admission"] = true


func run_checks() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or not args[1].is_absolute_path() or FileAccess.file_exists(args[1]):
		push_error("Chunk checks require oracle input and a new absolute task-owned report path.")
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if typeof(parsed) != TYPE_DICTIONARY or not parsed.has("chunkReader") or typeof(parsed.chunkReader) != TYPE_DICTIONARY or \
			not parsed.chunkReader.has("cases") or typeof(parsed.chunkReader.cases) != TYPE_ARRAY:
		push_error("Chunk-reader oracle input is missing its case collection.")
		quit(2)
		return
	check_oracle(parsed.chunkReader.cases)
	check_failure_admission()
	# GDScript can return to a caller after an aborted helper. Completion sentinels
	# prevent that path from writing a successful differential report.
	for section: String in ["oracle", "admission"]:
		check("completed_section", section, bool(_completed_sections.get(section, false)), true)
	var completed: Array[String] = []
	if _completed_sections.size() == 2:
		completed.append("chunk_reader")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"failures": failures, "completed": completed}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify({"failure_count": failures.size(), "counts": counts, "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)
