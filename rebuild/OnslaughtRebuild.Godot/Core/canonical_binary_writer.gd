# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Little-endian BinaryWriter-compatible primitives for versioned Core hashes.
## This owns bytes only. Snapshot field order/schema stays with its serializer.
## Failure is terminal and explicit; callers cannot publish a partial result.

var _bytes: PackedByteArray = []
var _error: String = ""


func write_bool(value: bool) -> bool:
	return write_u8(1 if value else 0)


func write_u8(value: Variant) -> bool:
	if typeof(value) != TYPE_INT:
		return _fail("Byte must be an integer without coercion.")
	if value < 0 or value > 255:
		return _fail("Byte outside unsigned 8-bit range.")
	if not _error.is_empty():
		return false
	_bytes.append(value)
	return true


func write_i32(value: Variant) -> bool:
	if typeof(value) != TYPE_INT:
		return _fail("Signed 32-bit value must be an integer without coercion.")
	if value < -2147483648 or value > 2147483647:
		return _fail("Integer outside signed 32-bit range.")
	var offset: int = _reserve(4)
	if offset < 0:
		return false
	_bytes.encode_s32(offset, value)
	return true


func write_u32(value: Variant) -> bool:
	if typeof(value) != TYPE_INT:
		return _fail("Unsigned 32-bit value must be an integer without coercion.")
	if value < 0 or value > 0xffffffff:
		return _fail("Integer outside unsigned 32-bit range.")
	var offset: int = _reserve(4)
	if offset < 0:
		return false
	_bytes.encode_u32(offset, value)
	return true


func write_i64(value: Variant) -> bool:
	if typeof(value) != TYPE_INT:
		return _fail("Signed 64-bit value must be an integer without coercion.")
	var offset: int = _reserve(8)
	if offset < 0:
		return false
	_bytes.encode_s64(offset, value)
	return true


## Unsigned 64-bit values use two exact words, never a lossy float conversion.
func write_u64_words(low: Variant, high: Variant) -> bool:
	if typeof(low) != TYPE_INT or typeof(high) != TYPE_INT:
		return _fail("Unsigned 64-bit words must be integers without coercion.")
	if low < 0 or low > 0xffffffff or high < 0 or high > 0xffffffff:
		return _fail("Unsigned 64-bit value requires two unsigned 32-bit words.")
	var offset: int = _reserve(8)
	if offset < 0:
		return false
	_bytes.encode_u32(offset, low)
	_bytes.encode_u32(offset + 4, high)
	return true


func write_float32(value: float) -> bool:
	var offset: int = _reserve(4)
	if offset < 0:
		return false
	_bytes.encode_float(offset, value)
	return true


func write_float64(value: float) -> bool:
	var offset: int = _reserve(8)
	if offset < 0:
		return false
	_bytes.encode_double(offset, value)
	return true


## Like BinaryWriter.Write(byte[]), this writes no length prefix.
func write_bytes(value: PackedByteArray) -> bool:
	if not _error.is_empty():
		return false
	_bytes.append_array(value)
	return true


## BinaryWriter's UTF-8 byte count uses a 7-bit continuation length prefix.
func write_string(value: String) -> bool:
	if not _error.is_empty():
		return false
	var encoded: PackedByteArray = value.to_utf8_buffer()
	var remaining: int = encoded.size()
	if remaining > 2147483647:
		return _fail("UTF-8 length exceeds the BinaryWriter string contract.")
	while remaining >= 128:
		_bytes.append((remaining & 127) | 128)
		remaining >>= 7
	_bytes.append(remaining)
	_bytes.append_array(encoded)
	return true


func finish() -> Dictionary:
	if not _error.is_empty():
		return {"ok": false, "error": _error}
	# A caller may retain and modify this buffer without changing the writer.
	return {"ok": true, "bytes": _bytes.duplicate()}


func _reserve(count: int) -> int:
	if not _error.is_empty():
		return -1
	var offset: int = _bytes.size()
	if _bytes.resize(offset + count) != OK:
		_fail("Cannot allocate canonical byte buffer.")
		return -1
	return offset


func _fail(message: String) -> bool:
	if _error.is_empty():
		_error = message
	return false
