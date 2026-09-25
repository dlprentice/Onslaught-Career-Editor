# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## One schema-4 trace format for replay and live recording, ported from
## ReplayRunner.cs/ReplayTraceHasher. Receives canonical state BYTES from the
## state serializer; it does not reconstruct state or own simulation steps.

const Writer = preload("res://Core/canonical_binary_writer.gd")
const Sha = preload("res://Core/sha256_stream.gd")
const INPUT_FIELDS: Array[String] = ["move_x", "move_z", "look_x", "look_y",
	"look_x_analog_permille", "look_y_analog_permille", "actions"]
var _hash: RefCounted = Sha.new()
var _disposed: bool = false


func _init() -> void:
	_hash.append(header_bytes())


static func header_bytes() -> PackedByteArray:
	var writer: RefCounted = Writer.new()
	writer.write_bytes("ONSLAUGHT-REBUILD-TRACE".to_ascii_buffer())
	writer.write_i32(4)
	return writer.finish().bytes


## This serialization boundary admits the full C# field widths, like the
## reference internal hasher. SimInput's semantic validation belongs to the
## input/tape owner; accepting a field here does not admit it to gameplay.
static func entry_bytes(input_slot: Variant, input: Variant, state_bytes: Variant) -> Dictionary:
	if typeof(input) != TYPE_DICTIONARY or typeof(state_bytes) != TYPE_PACKED_BYTE_ARRAY:
		return _failure("ArgumentException", "Trace entry requires an input record and canonical state bytes.")
	for field: String in INPUT_FIELDS:
		if not input.has(field) or typeof(input[field]) != TYPE_INT:
			return _failure("ArgumentException", "Trace input is missing an exact integer: " + field)
	var writer: RefCounted = Writer.new()
	writer.write_i32(input_slot)
	writer.write_i8(input.move_x)
	writer.write_i8(input.move_z)
	writer.write_i8(input.look_x)
	writer.write_i8(input.look_y)
	writer.write_i16(input.look_x_analog_permille)
	writer.write_i16(input.look_y_analog_permille)
	writer.write_u16(input.actions)
	writer.write_i32(state_bytes.size())
	writer.write_bytes(state_bytes)
	var result: Dictionary = writer.finish()
	return result if result.ok else _failure("ArgumentException", result.error)


func append(input_slot: Variant, input: Variant, state_bytes: Variant) -> Dictionary:
	# C# creates the entry before IncrementalHash checks disposal. In either
	# case an invalid entry must never partly append to the existing trace.
	var entry: Dictionary = entry_bytes(input_slot, input, state_bytes)
	if not entry.ok:
		return entry
	if _disposed:
		return _failure("ObjectDisposedException", "The replay trace was disposed.")
	return _hash.append(entry.bytes)


func get_current_hash() -> Dictionary:
	return _hash.current_hex()


func dispose() -> void:
	_disposed = true
	_hash.dispose()


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}
