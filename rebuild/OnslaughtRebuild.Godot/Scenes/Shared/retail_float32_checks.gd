# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Exact word comparison with the former portable binary32 store. No assets,
## tree content, files or simulation owner are needed by this bounded check.
const F = preload("res://Scenes/Shared/retail_float32.gd")
var _buffer := PackedByteArray()
var _count: int = 0
var _failures: int = 0


func _initialize() -> void:
	if DisplayServer.get_name() != "headless":
		quit(2)
		return
	_buffer.resize(8)
	for value: float in [0.0, -0.0, INF, -INF, NAN, 1e300, -1e300, 1e-300, -1e-300]:
		_compare(value)
	# Signed subnormals, finite extremes, infinities and NaN payloads.
	for word: int in [0, 1, 0x007fffff, 0x00800000, 0x3f000000, 0x3f800000,
		0x4b800000, 0x7f7fffff, 0x7f800000, 0x7f800001, 0x7fc00000, 0x7fffffff]:
		for sign: int in [0, 0x80000000]:
			_buffer.encode_u32(0, word | sign)
			_compare(_buffer.decode_float(0))
	# Consecutive binary32 values straddle exact binary64 halfway ties.
	for word: int in [1, 2, 0x007ffffe, 0x007fffff, 0x00800000, 0x3efffffe,
		0x3f7ffffe, 0x3f7fffff, 0x3f800000, 0x3f800001, 0x4b7ffffe, 0x7f7ffffe]:
		_buffer.encode_u32(0, word)
		_buffer.encode_u32(4, word + 1)
		var midpoint: float = (_buffer.decode_float(0) + _buffer.decode_float(4)) / 2.0
		_compare(midpoint)
		_compare(-midpoint)
	# Fixed local LCG, never the game RNG; cover all exponents and many payloads
	# together with binary64 values that actually require a binary32 rounding.
	var state: int = 0x48d60006
	for index: int in range(100000):
		state = (state * 1664525 + 1013904223) & 0xffffffff
		_buffer.encode_u32(0, state)
		var value: float = _buffer.decode_float(0)
		_compare(value)
		if is_finite(value):
			_compare(value * (1.0 + 0.000000059604644775390625))
			_compare(value * (1.0 - 0.000000059604644775390625))
	print("RETAIL_FLOAT32_CHECKS: ", _count, " comparisons; ", _failures, " failures")
	quit(0 if _failures == 0 else 1)


func _compare(value: float) -> void:
	_buffer.encode_float(0, PackedFloat32Array([value])[0])
	_buffer.encode_float(4, F.value(value))
	_count += 1
	if _buffer.decode_u32(0) != _buffer.decode_u32(4):
		if _failures < 10:
			push_error("Binary32 store mismatch: expected %08x, actual %08x" % [_buffer.decode_u32(0), _buffer.decode_u32(4)])
		_failures += 1
