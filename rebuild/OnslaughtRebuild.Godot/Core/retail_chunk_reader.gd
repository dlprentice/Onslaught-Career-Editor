# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Resident-memory port of Core/RetailChunkReader.cs, not a chunk grammar.
## Source owners: references/Onslaught/chunker.cpp:96-200, chunker.h:33-51,
## DXMemBuffer.cpp:352-464,574-615,628-631; membuffer.h:23-26 selects DX.
## Existing carried identities: pristine 74154bfa... image, 00423870 Open,
## 00423900 Close, 00423910 GetNext, 00423960 Read, 00423990 Skip.
## No filesystem, string decoding, float conversion or streaming is introduced.
## Payload bytes (including terminators and floating-point words) remain raw.
##
## Results separate API failure (ok=false, terminal until explicit reopen) from
## retail outcomes (ok=true, value plus complete). A short read is complete=false
## and value=false/0 as appropriate; callers must check these before consuming
## a record. Retail permits further calls after EOF, so EOF is not a fatal API
## fault. Invalid host types and managed span failures are explicit and sticky.


class MemBuffer extends RefCounted:
	var _data: PackedByteArray = []
	var _length: int = 0
	var _position: int = 0
	var _end_of_file: bool = false
	var _closed: bool = false
	var _error: String = ""
	var _error_type: String = ""

	func _init(data: Variant = PackedByteArray()) -> void:
		if typeof(data) != TYPE_PACKED_BYTE_ARRAY:
			_fail("A resident buffer requires PackedByteArray input.", "ArgumentNullException" if data == null else "ArgumentException")
			return
		if data.size() > 2147483647:
			_fail("Resident buffer length exceeds the C# int32 array contract.", "ArgumentOutOfRangeException")
			return
		# Packed arrays passed to script methods retain their shared identity.
		# Like the C# byte[], this data is neither copied nor written by opening it.
		_data = data
		_length = _data.size()


	func where_am_i() -> int:
		return _position


	func end_of_file() -> bool:
		return _end_of_file


	func remaining() -> int:
		return _signed32(_length - _position)


	func error() -> Dictionary:
		return {} if _error.is_empty() else {"ok": false, "error": _error, "error_type": _error_type}


	func read(destination: Variant, size: Variant) -> Dictionary:
		if not _ready_for_call():
			return error()
		if typeof(destination) != TYPE_PACKED_BYTE_ARRAY:
			return _fail("Read destination must be a PackedByteArray.", "ArgumentException")
		if typeof(size) != TYPE_INT or size < -2147483648 or size > 2147483647:
			return _fail("Read size must be a signed int32 without coercion.", "ArgumentOutOfRangeException")
		var available: int = size
		if _signed32(_position + available) > _length:
			_end_of_file = true
			available = _signed32(_length - _position)
		if available <= 0:
			return {"ok": true, "value": 0, "complete": size == 0}
		# Preserve the C# AsSpan/CopyTo check order and mutation on failure:
		# EOF can already be raised, but neither destination nor cursor changed.
		if _position < 0 or _position > _length or available > _length - _position:
			return _fail("Read source span lies outside the resident buffer.", "ArgumentOutOfRangeException")
		if available > destination.size():
			return _fail("Read destination is shorter than the available prefix.", "ArgumentException")
		# A temporary prefix gives CopyTo's memmove behavior if destination aliases
		# the input. Uncopied destination bytes remain exactly as supplied.
		var prefix: PackedByteArray = _data.slice(_position, _position + available)
		for index: int in range(available):
			destination[index] = prefix[index]
		_position = _signed32(_position + available)
		return {"ok": true, "value": available, "complete": available == size}


	func skip(size: Variant) -> Dictionary:
		if not _ready_for_call():
			return error()
		if typeof(size) != TYPE_INT or size < -2147483648 or size > 2147483647:
			return _fail("Skip size must be a signed int32 without coercion.", "ArgumentOutOfRangeException")
		if size == 0:
			return {"ok": true, "value": 0, "complete": true}
		var available: int = size
		if _signed32(_position + available) > _length:
			_end_of_file = true
			available = _signed32(_length - _position)
		if available <= 0:
			return {"ok": true, "value": 0, "complete": false}
		_position = _signed32(_position + available)
		return {"ok": true, "value": available, "complete": available == size}


	func close() -> Dictionary:
		if not _ready_for_call():
			return error()
		if _closed:
			return {"ok": true, "value": false, "complete": true}
		_closed = true
		return {"ok": true, "value": true, "complete": true}


	func _ready_for_call() -> bool:
		if not _error.is_empty():
			return false
		# C# arrays cannot resize. Byte edits retain alias semantics, but resizing
		# a caller-owned Godot array is outside that admitted representation.
		if _data.size() != _length:
			_fail("The caller resized an adopted resident buffer.", "ArgumentException")
			return false
		return true


	func _fail(message: String, kind: String) -> Dictionary:
		if _error.is_empty():
			_error = message
			_error_type = kind
		return error()


	static func _signed32(value: int) -> int:
		var word: int = value & 0xffffffff
		return word - 0x100000000 if word >= 0x80000000 else word


var _file: MemBuffer
var _size: int = 0
var _read_since_chunk: int = 0
var _error: String = ""
var _error_type: String = ""


func open_existing_buffer(existing_buffer: Variant) -> Dictionary:
	# Open resets both counters before testing the argument, just like C#.
	_size = 0
	_read_since_chunk = 0
	if not existing_buffer is MemBuffer:
		return _fail("OpenExistingBuffer requires a resident buffer.", "ArgumentNullException" if existing_buffer == null else "ArgumentException")
	_file = existing_buffer
	# Explicitly adopting a healthy buffer starts a new parsing session. A failed
	# buffer itself cannot be revived; it must be replaced by its owner.
	_error = ""
	_error_type = ""
	if not _file.error().is_empty():
		return _from_buffer_failure(_file.error())
	return {"ok": true, "value": _file, "complete": true}


func get_size() -> int:
	return _size


func get_read_since_chunk() -> int:
	return _read_since_chunk


func where_am_i() -> Dictionary:
	if not _require_file():
		return error()
	return {"ok": true, "value": _file.where_am_i(), "complete": true}


func error() -> Dictionary:
	return {} if _error.is_empty() else {"ok": false, "error": _error, "error_type": _error_type}


func get_next() -> Dictionary:
	if not _require_file():
		return error()
	_read_since_chunk = 0
	var header := PackedByteArray([0, 0, 0, 0])
	var read_id: Dictionary = _file.read(header, 4)
	if not read_id.ok:
		return _from_buffer_failure(read_id)
	if read_id.value < 4:
		return {"ok": true, "value": 0, "complete": false, "reason": "short_chunk_id"}
	var chunk: int = _little_endian_u32(header)
	# The second read targets the live Size word: retain its high bytes on a
	# partial overwrite. An atomic eight-byte read would violate this contract.
	var size_bytes := PackedByteArray([_size & 255, (_size >> 8) & 255, (_size >> 16) & 255, (_size >> 24) & 255])
	var read_size: Dictionary = _file.read(size_bytes, 4)
	if not read_size.ok:
		return _from_buffer_failure(read_size)
	_size = _little_endian_u32(size_bytes)
	if read_size.value < 4:
		return {"ok": true, "value": 0, "complete": false, "reason": "short_chunk_size"}
	# Zero is still the released invalid/dodgy chunk name, not an invented tag.
	return {"ok": true, "value": chunk, "complete": true}


func read(destination: Variant, size: Variant, count: Variant) -> Dictionary:
	if not _require_file():
		return error()
	if not _is_u32(size) or not _is_u32(count):
		return _fail("Chunk size/count must be unsigned int32 values without coercion.", "ArgumentOutOfRangeException")
	# Only the low 32 bits of the product are required. Split into 16-bit limbs
	# so multiplying uint32 maxima never overflows GDScript's signed int64.
	var product: int = ((size & 0xffff) * (count & 0xffff) +
		((((size >> 16) * (count & 0xffff) + (count >> 16) * (size & 0xffff)) & 0xffff) << 16)) & 0xffffffff
	var requested: int = MemBuffer._signed32(product)
	_read_since_chunk = (_read_since_chunk + product) & 0xffffffff
	var result: Dictionary = _file.read(destination, requested)
	if not result.ok:
		return _from_buffer_failure(result)
	var complete: bool = result.value == requested
	return {"ok": true, "value": complete, "complete": complete, "bytes_read": result.value}


func skip() -> Dictionary:
	if not _require_file():
		return error()
	var skip_size: int = (_size - _read_since_chunk) & 0xffffffff
	_read_since_chunk = _size
	var result: Dictionary = _file.skip(MemBuffer._signed32(skip_size))
	return result if result.ok else _from_buffer_failure(result)


func close() -> Dictionary:
	if not _require_file():
		return error()
	var result: Dictionary = _file.close()
	if not result.ok:
		return _from_buffer_failure(result)
	return {"ok": true, "value": 0 if result.value else -1, "complete": true}


func _require_file() -> bool:
	if not _error.is_empty():
		return false
	if _file == null:
		_fail("The chunk reader has no buffer; call open_existing_buffer first.", "InvalidOperationException")
		return false
	if not _file.error().is_empty():
		_from_buffer_failure(_file.error())
		return false
	return true


func _from_buffer_failure(result: Dictionary) -> Dictionary:
	return _fail(result.error, result.error_type)


func _fail(message: String, kind: String) -> Dictionary:
	if _error.is_empty():
		_error = message
		_error_type = kind
	return error()


static func _is_u32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= 0 and value <= 0xffffffff


static func _little_endian_u32(bytes: PackedByteArray) -> int:
	return bytes[0] | (bytes[1] << 8) | (bytes[2] << 16) | (bytes[3] << 24)
