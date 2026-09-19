# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Released integer stream; preload this script instead of using a global class.
## Contract: OnslaughtRebuild.Core/Level100ActorWeapons.cs, Level100ReleasedRandom.
## The shipped modulus is 214783647, not MINSTD's 2147483647. All wrapped
## operations and the signed seed are intentional parts of the replay state.

const INITIAL_SEED: int = 123_456
const MULTIPLIER: int = 48_271
const MODULUS: int = 214_783_647
const QUOTIENT: int = 4_449
const REMAINDER: int = 25_968
const UNIT_MODULUS: int = 65_536
const UNIT_DIVISOR: int = 32_768
const INT32_MIN: int = -2_147_483_648
const INT32_MAX: int = 2_147_483_647

var _seed: int = INITIAL_SEED


func get_seed() -> int:
	return _seed


## Restore the exact signed snapshot word, including zero and negative seeds.
## Invalid types/ranges leave the current stream unchanged, also in release.
func restore_seed(value: Variant) -> Dictionary:
	if typeof(value) != TYPE_INT:
		return _failure("seed must be an integer, not a coerced numeric value")
	var candidate: int = value
	if candidate < INT32_MIN or candidate > INT32_MAX:
		return _failure("seed must fit signed 32 bits")
	_seed = candidate
	return {"ok": true}


## Decimal admission avoids JSON's floating-point number conversion at imports.
## Only ASCII decimal digits and an optional leading minus sign are accepted.
func restore_seed_decimal(value: Variant) -> Dictionary:
	if typeof(value) != TYPE_STRING:
		return _failure("seed text must be a string")
	var text: String = value
	if text.is_empty():
		return _failure("seed text must contain decimal digits")
	var negative: bool = text.begins_with("-")
	var first: int = 1 if negative else 0
	if first == text.length():
		return _failure("seed text must contain decimal digits")
	var limit: int = -INT32_MIN if negative else INT32_MAX
	var magnitude: int = 0
	for index: int in range(first, text.length()):
		var digit: int = text.unicode_at(index) - 48
		if digit < 0 or digit > 9:
			return _failure("seed text must contain ASCII decimal digits only")
		magnitude = magnitude * 10 + digit
		if magnitude > limit:
			return _failure("seed must fit signed 32 bits")
	return restore_seed(-magnitude if negative else magnitude)


## Advances once and returns the unchecked signed-32 absolute value. INT_MIN
## negation remains INT_MIN, matching the released body and C# unchecked code.
func next() -> int:
	_seed = _step(_seed)
	return _wrap_signed32(-_seed) if _seed < 0 else _seed


## Successful draws return {ok: true, value: int}. An invalid scale is rejected
## before a draw. A checked result overflow returns {ok: false, error: String}
## AFTER consuming its draw, matching Core's Next() then checked-cast ordering.
## In either case get_seed() exposes the exact retained stream state.
func next_signed_unit_scaled(scale: Variant) -> Dictionary:
	if typeof(scale) != TYPE_INT:
		return _failure("scale must be an integer, not a coerced numeric value")
	var admitted_scale: int = scale
	if admitted_scale < INT32_MIN or admitted_scale > INT32_MAX:
		return _failure("scale must fit signed 32 bits")
	var sample: int = next() % UNIT_MODULUS
	var product: int = (sample - UNIT_DIVISOR) * admitted_scale
	# The signed-32 scale keeps |product| <= 2^46. Positive shifts implement
	# nearest rounding with ties away from zero, with no float conversion.
	var magnitude: int = -product if product < 0 else product
	var rounded: int = (magnitude + (UNIT_DIVISOR >> 1)) >> 15
	if product < 0:
		rounded = -rounded
	if rounded < INT32_MIN or rounded > INT32_MAX:
		return _failure("scaled draw overflows signed 32 bits")
	return {"ok": true, "value": rounded}


static func _step(seed_value: int) -> int:
	# Integer / truncates toward zero, as C# and x86 idiv do. Deriving the
	# signed remainder explicitly also avoids a positive-modulo substitution.
	@warning_ignore("integer_division")
	var quotient: int = seed_value / QUOTIENT
	var remainder: int = seed_value - quotient * QUOTIENT
	var left: int = _wrap_signed32(remainder * MULTIPLIER)
	var right: int = _wrap_signed32(quotient * REMAINDER)
	var stepped: int = _wrap_signed32(left - right)
	return _wrap_signed32(MODULUS + stepped) if stepped < 1 else stepped


static func _wrap_signed32(value: int) -> int:
	var word: int = value & 4_294_967_295
	return word - 4_294_967_296 if word > INT32_MAX else word


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error": message}
