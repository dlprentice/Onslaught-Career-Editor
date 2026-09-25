# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## PC24/RN arithmetic with a binary64 carrier and separate float32 stores.
## Ports OnslaughtRebuild.Core/RetailFloat24.cs. The admitted geometry and Unit
## contracts use 24 significand bits, ties to even, without reducing the
## intermediate exponent range to float32. See rebuild/DETERMINISM.md.
##
## Checked entry points return Result; callers must inspect ok. The *_finite
## helpers allocate no Result and require a finite unrounded operation result.
## They are for an already-admitted numerical kernel, not input validation.

const WORD_MASK: int = 0xffffffff
const _DISCARDED_MASK: int = (1 << 29) - 1
const _HALF: int = 1 << 28
const _NORMALIZE_SUBNORMAL: float = 4503599627370496.0 # 2^52, exact.


class Result extends RefCounted:
	var ok: bool
	var value: float
	var error: String

	func _init(result_value: float, result_error: String = "") -> void:
		ok = result_error.is_empty()
		value = result_value
		error = result_error


static func try_round(value: float) -> Result:
	if not is_finite(value):
		return _failure("Retail arithmetic must receive a finite rounding input.")
	# Match C# Round: admission precedes rounding. A finite binary64 value near
	# the exponent limit may round to infinity; that output is not re-admitted.
	return Result.new(round_finite(value))


static func try_add(left: float, right: float) -> Result:
	return try_round(left + right)


static func try_subtract(left: float, right: float) -> Result:
	return try_round(left - right)


static func try_multiply(left: float, right: float) -> Result:
	return try_round(left * right)


static func try_divide(left: float, right: float) -> Result:
	# Guard division by zero before invoking GDScript's operator. Otherwise the
	# C# owner admits the computed result: finite / infinity is signed zero.
	if right == 0.0:
		return _failure("Retail division requires a nonzero divisor.")
	return try_round(left / right)


static func try_sqrt(value: float) -> Result:
	if not is_finite(value) or value < 0.0:
		return _failure("Retail square root requires a finite nonnegative operand.")
	return try_round(sqrt(value))


static func try_store_float32(value: float) -> Result:
	if not is_finite(value):
		return _failure("A checked float32 store requires a finite input.")
	var stored: float = store_float32(value)
	if not is_finite(stored):
		return _failure("A checked float32 store must remain finite.")
	return Result.new(stored)


static func add_finite(left: float, right: float) -> float:
	return round_finite(left + right)


static func subtract_finite(left: float, right: float) -> float:
	return round_finite(left - right)


static func multiply_finite(left: float, right: float) -> float:
	return round_finite(left * right)


static func divide_finite(left: float, right: float) -> float:
	return round_finite(left / right)


static func sqrt_finite(value: float) -> float:
	return round_finite(sqrt(value))


static func round_finite(value: float) -> float:
	# Zero must return without arithmetic: both signs are meaningful raw words.
	if value == 0.0:
		return value
	var bytes := PackedByteArray()
	bytes.resize(8)
	bytes.encode_double(0, value)
	var high: int = bytes.decode_u32(4)
	var low: int = bytes.decode_u32(0)
	if ((high >> 20) & 0x7ff) == 0:
		# Normalize binary64 subnormals before discarding significand bits. This
		# power-of-two scale preserves their sign and retained exponent behavior.
		return round_finite(value * _NORMALIZE_SUBNORMAL) / _NORMALIZE_SUBNORMAL
	var kept: int = low >> 29
	var remainder: int = low & _DISCARDED_MASK
	if remainder > _HALF or (remainder == _HALF and (kept & 1) == 1):
		kept += 1
	var shifted: int = kept << 29
	bytes.encode_u32(0, shifted & WORD_MASK)
	bytes.encode_u32(4, high + (shifted >> 32))
	return bytes.decode_double(0)


## Raw bit casts deliberately accept all IEEE words, including infinity/NaN.
## read_word takes the low 32 bits, so signed C# words and unsigned words have
## the same meaning. Numeric owners must admit finiteness before arithmetic.
static func read_word(word: int) -> float:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_u32(0, word & WORD_MASK)
	return bytes.decode_float(0)


## Returns an unsigned 32-bit word held in GDScript's signed 64-bit int.
## This is a raw float32 store; use try_store_float32 for finite admission.
static func store_word(value: float) -> int:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	return bytes.decode_u32(0)


static func store_float32(value: float) -> float:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	return bytes.decode_float(0)


static func is_word(word: int) -> bool:
	return word >= -0x80000000 and word <= WORD_MASK


static func is_finite_word(word: int) -> bool:
	return is_word(word) and (word & 0x7f800000) != 0x7f800000


static func _failure(message: String) -> Result:
	return Result.new(0.0, message)
