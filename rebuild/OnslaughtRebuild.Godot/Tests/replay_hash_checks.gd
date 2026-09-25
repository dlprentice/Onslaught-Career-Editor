# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## C# byte/trace fixtures, native Godot SHA-256 cross-checks and lifecycle checks.
const Sha = preload("res://Core/sha256_stream.gd")
const Trace = preload("res://Core/replay_trace_hasher.gd")
const Writer = preload("res://Core/canonical_binary_writer.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var completed: Array[String] = []


func _initialize() -> void:
	call_deferred("run_checks")


func check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func check_streams(cases: Array) -> void:
	check("fixture", "hash_streams_present", not cases.is_empty(), true)
	for row: Dictionary in cases:
		var stream: RefCounted = Sha.new()
		var native := HashingContext.new()
		check("native", row.name, native.start(HashingContext.HASH_SHA256), OK)
		for index: int in range(row.chunks.size()):
			var chunk: Dictionary = row.chunks[index]
			var data: PackedByteArray = String(chunk.hex).hex_decode()
			var name: String = "%s:%d" % [row.name, index]
			check("append", name, stream.append(data).ok, true)
			check("native", name, native.update(data), OK)
			data.fill(0xaa) # Source mutation must not rewrite an admitted tail.
			var digest: Dictionary = stream.current_digest()
			check("peek", name, digest.ok, true)
			if digest.ok:
				check("sha256", name, digest.bytes.hex_encode(), chunk.hash)
				digest.bytes.fill(0xcc)
			check("detached_digest", name, stream.current_hex().value, chunk.hash)
			check("empty_append", name, stream.append(PackedByteArray()).ok, true)
		check("sha256", row.name + ":final", stream.current_hex().value, row.hash)
		check("native", row.name + ":final", native.finish().hex_encode(), row.hash)
		stream.dispose()
		check("disposed", row.name, stream.current_hex().error_type, "ObjectDisposedException")
	completed.append("streams")


func check_trace(data: Dictionary) -> void:
	check("trace_bytes", "header", Trace.header_bytes().hex_encode(), data.header)
	var stream: RefCounted = Trace.new()
	check("trace_hash", "initial", stream.get_current_hash().value, data.initial)
	check("fixture", "trace_rows_present", not data.rows.is_empty(), true)
	for index: int in range(data.rows.size()):
		var row: Dictionary = data.rows[index]
		var input: Dictionary = {}
		for field: String in Trace.INPUT_FIELDS:
			check("fixture", field, float(row.input[field]) == floor(float(row.input[field])), true)
			input[field] = int(row.input[field])
		var bytes: PackedByteArray = String(row.state).hex_decode()
		var entry: Dictionary = Trace.entry_bytes(int(row.slot), input, bytes)
		check("trace_bytes", str(index), entry.ok, true)
		if entry.ok:
			check("trace_bytes", str(index), entry.bytes.hex_encode(), row.entry)
		check("trace_append", str(index), stream.append(int(row.slot), input, bytes).ok, true)
		bytes.fill(0xdd)
		input.clear()
		check("trace_hash", str(index), stream.get_current_hash().value, row.hash)
		check("trace_peek", str(index), stream.get_current_hash().value, row.hash)
	stream.dispose()
	check("disposed", "trace", stream.get_current_hash().error_type, "ObjectDisposedException")
	completed.append("trace")


func check_lifecycle() -> void:
	var stream: RefCounted = Sha.new()
	stream.append("prefix".to_utf8_buffer())
	var fork: RefCounted = stream.fork().value
	stream.append("left".to_utf8_buffer())
	fork.append("right".to_utf8_buffer())
	check("fork", "left", stream.current_hex().value, "prefixleft".sha256_text())
	check("fork", "right", fork.current_hex().value, "prefixright".sha256_text())
	for invalid: Variant in [null, [], 1, "abc", 1.0]:
		var bad: RefCounted = Sha.new()
		check("refusal", "hash-input", bad.append(invalid).ok, false)
		check("refusal", "hash-poisoned-peek", bad.current_hex().ok, false)
		check("refusal", "hash-poisoned-append", bad.append(PackedByteArray()).ok, false)
		check("refusal", "hash-poisoned-fork", bad.fork().ok, false)
	stream.dispose()
	stream.dispose()
	check("disposed", "append", stream.append(PackedByteArray()).error_type, "ObjectDisposedException")
	check("disposed", "fork", stream.fork().error_type, "ObjectDisposedException")
	var input: Dictionary = {"move_x": 0, "move_z": 0, "look_x": 0, "look_y": 0,
		"look_x_analog_permille": 0, "look_y_analog_permille": 0, "actions": 0}
	var trace: RefCounted = Trace.new()
	var before: String = trace.get_current_hash().value
	for field: String in Trace.INPUT_FIELDS:
		for invalid: Variant in [null, true, 0.0, "0", -65536, 65536]:
			var changed: Dictionary = input.duplicate()
			changed[field] = invalid
			check("trace_refusal", field, trace.append(0, changed, PackedByteArray()).ok, false)
			check("trace_refusal", "unchanged", trace.get_current_hash().value, before)
	for invalid: Variant in [null, true, 0.0, -2147483649, 2147483648]:
		check("trace_refusal", "slot", trace.append(invalid, input, PackedByteArray()).ok, false)
		check("trace_refusal", "unchanged-slot", trace.get_current_hash().value, before)
	check("trace_refusal", "recovery", trace.append(0, input, PackedByteArray()).ok, true)
	trace.dispose()
	check("disposed", "trace-append", trace.append(0, input, PackedByteArray()).error_type, "ObjectDisposedException")
	for method: String in ["write_i8", "write_i16", "write_u16"]:
		for invalid: Variant in [null, true, 0.0, "0", -65536, 65536]:
			var writer: RefCounted = Writer.new()
			check("binary_refusal", method, writer.call(method, invalid), false)
			check("binary_refusal", "sticky", writer.write_i32(1), false)
			check("binary_refusal", "no-partial-result", writer.finish().ok, false)
	completed.append("lifecycle")


func check_strings(rows: Array) -> void:
	check("fixture", "binary_string_rows", not rows.is_empty(), true)
	for index: int in range(rows.size()):
		var row: Dictionary = rows[index]
		var writer: RefCounted = Writer.new()
		var units := PackedInt32Array(row.units)
		var original: PackedInt32Array = units.duplicate()
		check("binary_strings", str(index), writer.write_string(units), true)
		check("binary_strings", str(index) + ":source-intact", units, original)
		units.fill(1)
		check("binary_strings", str(index) + ":bytes", writer.finish().bytes.hex_encode(), row.bytes)
	for invalid: Variant in [null, true, 0, 0.0, [], {}, PackedInt32Array([-1]), PackedInt32Array([65536])]:
		var writer: RefCounted = Writer.new()
		check("binary_refusal", "string", writer.write_string(invalid), false)
		check("binary_refusal", "string-sticky", writer.write_string("later"), false)
		check("binary_refusal", "string-no-partial", writer.finish().ok, false)
	completed.append("strings")


func run_checks() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		push_error("Expected oracle JSON and owned report path.")
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if typeof(parsed) != TYPE_DICTIONARY or typeof(parsed.get("replayHash")) != TYPE_DICTIONARY:
		push_error("Missing replay-hash oracle.")
		quit(2)
		return
	check_streams(parsed.replayHash.hashes)
	check_trace(parsed.replayHash)
	check_lifecycle()
	check_strings(parsed.replayHash.strings)
	check("completion", "all-sections", completed, ["streams", "trace", "lifecycle", "strings"])
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(),
		"failures": failures, "completed": ["replay_hash"] if completed == ["streams", "trace", "lifecycle", "strings"] else []}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		push_error("Cannot write owned replay-hash report.")
		quit(2)
		return
	file.store_string(JSON.stringify(report, "\t") + "\n")
	file.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "completed": report.completed}))
	quit(0 if failures.is_empty() else 1)
