# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Streaming SHA-256 with a non-consuming current digest for replay recording.
## FIPS 180-4 sections 4.1.2, 4.2.2, 5 and 6.2 define these operations.
## Godot HashingContext.finish() consumes its context and exposes no copy;
## replay's GetCurrentHash contract must allow later appends without retaining
## an entire session's canonical state bytes. Only 8 words and <64 bytes persist.
## This is an unkeyed content hash, not an authentication or secret-handling API.

const MASK: int = 0xffffffff
const MAX_BYTES: int = 2305843009213693951 # FIPS message length is < 2^64 bits.
const INITIAL: Array[int] = [
	0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
	0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
]
const K: Array[int] = [
	0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
	0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
	0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
	0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
	0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
	0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
	0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
	0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]

var _words: Array[int] = INITIAL.duplicate()
var _tail: PackedByteArray = []
var _byte_count: int = 0
var _disposed: bool = false
var _error: String = ""


func append(data: Variant) -> Dictionary:
	if _disposed:
		return _failure("ObjectDisposedException", "The SHA-256 stream was disposed.")
	if not _error.is_empty():
		return _failure("InvalidOperationException", _error)
	if typeof(data) != TYPE_PACKED_BYTE_ARRAY:
		return _poison("SHA-256 input must be an exact byte array.")
	if data.size() > MAX_BYTES - _byte_count:
		return _poison("SHA-256 input exceeds its 64-bit bit-length field.")
	_byte_count += data.size()
	var offset: int = 0
	if not _tail.is_empty():
		var copied: int = mini(64 - _tail.size(), data.size())
		_tail.append_array(data.slice(0, copied))
		offset = copied
		if _tail.size() == 64:
			_compress(_tail, 0)
			_tail.clear()
	while offset <= data.size() - 64:
		_compress(data, offset)
		offset += 64
	if offset < data.size():
		_tail.append_array(data.slice(offset))
	return {"ok": true}


## Repeated reads and reads between appends do not reset or alter the stream.
func current_digest() -> Dictionary:
	var copied: Dictionary = fork()
	if not copied.ok:
		return copied
	var copy: RefCounted = copied.value
	return {"ok": true, "bytes": copy._final_bytes()}


func current_hex() -> Dictionary:
	var result: Dictionary = current_digest()
	if not result.ok:
		return result
	return {"ok": true, "value": result.bytes.hex_encode()}


func fork() -> Dictionary:
	if _disposed:
		return _failure("ObjectDisposedException", "The SHA-256 stream was disposed.")
	if not _error.is_empty():
		return _failure("InvalidOperationException", _error)
	var copy: RefCounted = new()
	copy._words = _words.duplicate()
	copy._tail = _tail.duplicate()
	copy._byte_count = _byte_count
	return {"ok": true, "value": copy}


func dispose() -> void:
	_disposed = true
	_tail.clear()
	_words.clear()


func _final_bytes() -> PackedByteArray:
	var ending: PackedByteArray = _tail.duplicate()
	ending.append(0x80)
	while ending.size() % 64 != 56:
		ending.append(0)
	# Two unsigned words avoid a signed-int64 overflow for large streams.
	_append_big_endian(ending, (_byte_count >> 29) & MASK)
	_append_big_endian(ending, (_byte_count & 0x1fffffff) << 3)
	for offset: int in range(0, ending.size(), 64):
		_compress(ending, offset)
	var digest: PackedByteArray = []
	for word: int in _words:
		_append_big_endian(digest, word)
	return digest


func _compress(block: PackedByteArray, offset: int) -> void:
	var schedule := PackedInt64Array()
	schedule.resize(64)
	for index: int in range(16):
		var pos: int = offset + index * 4
		schedule[index] = (int(block[pos]) << 24) | (int(block[pos + 1]) << 16) \
			| (int(block[pos + 2]) << 8) | int(block[pos + 3])
	for index: int in range(16, 64):
		var a: int = schedule[index - 15]
		var b: int = schedule[index - 2]
		# Inline fixed rotations avoid hundreds of VM calls per block.
		var small0: int = (((a >> 7) | (a << 25)) & MASK) ^ (((a >> 18) | (a << 14)) & MASK) ^ (a >> 3)
		var small1: int = (((b >> 17) | (b << 15)) & MASK) ^ (((b >> 19) | (b << 13)) & MASK) ^ (b >> 10)
		schedule[index] = (schedule[index - 16] + small0 + schedule[index - 7] + small1) & MASK
	var a: int = _words[0]
	var b: int = _words[1]
	var c: int = _words[2]
	var d: int = _words[3]
	var e: int = _words[4]
	var f: int = _words[5]
	var g: int = _words[6]
	var h: int = _words[7]
	for index: int in range(64):
		var sum1: int = (((e >> 6) | (e << 26)) & MASK) ^ (((e >> 11) | (e << 21)) & MASK) ^ (((e >> 25) | (e << 7)) & MASK)
		var choice: int = (e & f) ^ ((~e) & g)
		var t1: int = (h + sum1 + choice + K[index] + schedule[index]) & MASK
		var sum0: int = (((a >> 2) | (a << 30)) & MASK) ^ (((a >> 13) | (a << 19)) & MASK) ^ (((a >> 22) | (a << 10)) & MASK)
		var majority: int = (a & b) ^ (a & c) ^ (b & c)
		var t2: int = (sum0 + majority) & MASK
		h = g
		g = f
		f = e
		e = (d + t1) & MASK
		d = c
		c = b
		b = a
		a = (t1 + t2) & MASK
	var result: Array[int] = [a, b, c, d, e, f, g, h]
	for index: int in range(8):
		_words[index] = (_words[index] + result[index]) & MASK


static func _append_big_endian(buffer: PackedByteArray, value: int) -> void:
	buffer.append((value >> 24) & 255)
	buffer.append((value >> 16) & 255)
	buffer.append((value >> 8) & 255)
	buffer.append(value & 255)


func _poison(message: String) -> Dictionary:
	_error = message
	return _failure("InvalidOperationException", message)


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}
