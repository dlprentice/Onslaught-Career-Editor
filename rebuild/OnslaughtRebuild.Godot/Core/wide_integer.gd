# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Unsigned exact arithmetic, loaded with an explicit preload by Core callers.
## Values are canonical Array[int] digits in little-endian base 32768: [0] is
## zero, every digit is 0..32767, and other values have no high zero digit.
## Public methods validate in release and never mutate their input arrays.
## Success has ok=true and value, except divmod which has quotient/remainder.
## Failure has ok=false and error; no sentinel numeric value is substituted.
##
## Immediate consumer: Simulation.cs's exact ground-impact incidence ratio.
## The multiply/compare/divmod primitives also fit the magnitude operations in
## Level100ActorWeaponRuntime.cs's BigInteger/Int128 fractions. Signed fractions,
## cylinder selection and square-root algorithms remain their callers' concern.

const LIMB_BITS: int = 15
const LIMB_BASE: int = 1 << LIMB_BITS
const LIMB_MASK: int = LIMB_BASE - 1


static func from_int64(value: Variant) -> Dictionary:
	if typeof(value) != TYPE_INT or value < 0:
		return _failure("value must be a nonnegative signed-64 integer")
	return _success(_from_int64(value))


## Decimal strings are parsed without float conversion or an Int64 size limit.
## Leading zeroes are accepted; signs, whitespace and non-ASCII digits are not.
static func from_decimal(value: Variant) -> Dictionary:
	if typeof(value) != TYPE_STRING:
		return _failure("decimal value must be a string")
	var text: String = value
	if text.is_empty():
		return _failure("decimal value must contain digits")
	for index: int in range(text.length()):
		var digit: int = text.unicode_at(index) - 48
		if digit < 0 or digit > 9:
			return _failure("decimal value must contain ASCII decimal digits only")
	var limbs: Array[int] = [0]
	for index: int in range(text.length()):
		var carry: int = text.unicode_at(index) - 48
		for limb_index: int in range(limbs.size()):
			var column: int = limbs[limb_index] * 10 + carry
			limbs[limb_index] = column & LIMB_MASK
			carry = column >> LIMB_BITS
		if carry != 0:
			limbs.append(carry)
	return _success(_trim(limbs))


static func to_int64(value: Variant) -> Dictionary:
	var admitted: Dictionary = _read_limbs(value)
	if not admitted["ok"]:
		return admitted
	return _to_int64(admitted["value"])


static func compare(left: Variant, right: Variant) -> Dictionary:
	var pair: Dictionary = _read_pair(left, right)
	if not pair["ok"]:
		return pair
	return _success(_compare(pair["left"], pair["right"]))


static func add(left: Variant, right: Variant) -> Dictionary:
	var pair: Dictionary = _read_pair(left, right)
	if not pair["ok"]:
		return pair
	return _success(_add(pair["left"], pair["right"]))


static func subtract(left: Variant, right: Variant) -> Dictionary:
	var pair: Dictionary = _read_pair(left, right)
	if not pair["ok"]:
		return pair
	if _compare(pair["left"], pair["right"]) < 0:
		return _failure("unsigned subtraction would be negative")
	return _success(_subtract(pair["left"], pair["right"]))


static func multiply(left: Variant, right: Variant) -> Dictionary:
	var pair: Dictionary = _read_pair(left, right)
	if not pair["ok"]:
		return pair
	return _success(_multiply(pair["left"], pair["right"]))


## Exact quotient and remainder. Unlike the original feasibility probe, neither
## the quotient nor the operands are capped at a particular gameplay scale.
static func divmod(numerator: Variant, denominator: Variant) -> Dictionary:
	var pair: Dictionary = _read_pair(numerator, denominator)
	if not pair["ok"]:
		return pair
	var divisor: Array[int] = pair["right"]
	if _is_zero(divisor):
		return _failure("division by zero")
	var divided: Dictionary = _divmod(pair["left"], divisor)
	return {"ok": true, "quotient": divided["quotient"], "remainder": divided["remainder"]}


## floor((numerator + floor(denominator / 2)) / denominator), then a checked
## nonnegative Int64 conversion. Positive halfway results round upward. Core's
## ground-impact caller supplies its own incidence clamp after this operation.
static func divide_round_nearest_to_int64(numerator: Variant, denominator: Variant) -> Dictionary:
	var pair: Dictionary = _read_pair(numerator, denominator)
	if not pair["ok"]:
		return pair
	var divisor: Array[int] = pair["right"]
	if _is_zero(divisor):
		return _failure("division by zero")
	var rounded_numerator: Array[int] = _add(pair["left"], _half(divisor))
	var divided: Dictionary = _divmod(rounded_numerator, divisor)
	return _to_int64(divided["quotient"])


static func _read_limbs(value: Variant) -> Dictionary:
	if typeof(value) != TYPE_ARRAY:
		return _failure("wide integer must be an Array of integer limbs")
	var source: Array = value
	if source.is_empty():
		return _failure("wide integer must contain at least one limb")
	var copy: Array[int] = []
	for limb: Variant in source:
		if typeof(limb) != TYPE_INT:
			return _failure("wide integer limbs must be integers")
		var digit: int = limb
		if digit < 0 or digit > LIMB_MASK:
			return _failure("wide integer limb is outside base 32768")
		copy.append(digit)
	if copy.size() > 1 and copy.back() == 0:
		return _failure("wide integer has a redundant high zero limb")
	return _success(copy)


static func _read_pair(left: Variant, right: Variant) -> Dictionary:
	var first: Dictionary = _read_limbs(left)
	if not first["ok"]:
		return _failure("left operand: " + first["error"])
	var second: Dictionary = _read_limbs(right)
	if not second["ok"]:
		return _failure("right operand: " + second["error"])
	return {"ok": true, "left": first["value"], "right": second["value"]}


static func _from_int64(value: int) -> Array[int]:
	var limbs: Array[int] = []
	while value != 0:
		limbs.append(value & LIMB_MASK)
		value >>= LIMB_BITS
	if limbs.is_empty():
		limbs.append(0)
	return limbs


static func _to_int64(limbs: Array[int]) -> Dictionary:
	# 2^63-1 has four full 15-bit digits followed by the high digit 7.
	if limbs.size() > 5 or (limbs.size() == 5 and limbs[4] > 7):
		return _failure("wide integer exceeds signed-64 maximum")
	var value: int = 0
	for index: int in range(limbs.size() - 1, -1, -1):
		value = (value << LIMB_BITS) | limbs[index]
	return _success(value)


static func _compare(left: Array[int], right: Array[int]) -> int:
	if left.size() != right.size():
		return -1 if left.size() < right.size() else 1
	for index: int in range(left.size() - 1, -1, -1):
		if left[index] != right[index]:
			return -1 if left[index] < right[index] else 1
	return 0


static func _add(left: Array[int], right: Array[int]) -> Array[int]:
	var result: Array[int] = []
	var carry: int = 0
	for index: int in range(maxi(left.size(), right.size())):
		var left_limb: int = left[index] if index < left.size() else 0
		var right_limb: int = right[index] if index < right.size() else 0
		var column: int = left_limb + right_limb + carry
		result.append(column & LIMB_MASK)
		carry = column >> LIMB_BITS
	if carry != 0:
		result.append(carry)
	return _trim(result)


## Internal precondition: both values are canonical and left >= right.
static func _subtract(left: Array[int], right: Array[int]) -> Array[int]:
	var result: Array[int] = []
	var borrow: int = 0
	for index: int in range(left.size()):
		var right_limb: int = right[index] if index < right.size() else 0
		var column: int = left[index] - right_limb - borrow
		borrow = 1 if column < 0 else 0
		result.append(column + LIMB_BASE if borrow != 0 else column)
	return _trim(result)


static func _multiply(left: Array[int], right: Array[int]) -> Array[int]:
	var product: Array[int] = []
	product.resize(left.size() + right.size())
	product.fill(0)
	for i: int in range(left.size()):
		var carry: int = 0
		for j: int in range(right.size()):
			# Each column stays below 2^30, including its incoming carry.
			var column: int = product[i + j] + left[i] * right[j] + carry
			product[i + j] = column & LIMB_MASK
			carry = column >> LIMB_BITS
		product[i + right.size()] = carry
	return _trim(product)


static func _half(limbs: Array[int]) -> Array[int]:
	var result: Array[int] = []
	result.resize(limbs.size())
	var carry: int = 0
	for index: int in range(limbs.size() - 1, -1, -1):
		result[index] = (limbs[index] >> 1) | (carry << (LIMB_BITS - 1))
		carry = limbs[index] & 1
	return _trim(result)


static func _divmod(numerator: Array[int], denominator: Array[int]) -> Dictionary:
	var quotient: Array[int] = []
	quotient.resize(numerator.size())
	quotient.fill(0)
	var remainder: Array[int] = [0]
	# Binary long division: before each input bit remainder < denominator.
	# Appending one bit gives remainder < 2*denominator, so subtract at most once.
	for digit: int in range(numerator.size() - 1, -1, -1):
		for bit: int in range(LIMB_BITS - 1, -1, -1):
			var carry: int = (numerator[digit] >> bit) & 1
			for index: int in range(remainder.size()):
				var column: int = (remainder[index] << 1) | carry
				remainder[index] = column & LIMB_MASK
				carry = column >> LIMB_BITS
			if carry != 0:
				remainder.append(carry)
			if _compare(remainder, denominator) >= 0:
				remainder = _subtract(remainder, denominator)
				quotient[digit] |= 1 << bit
	return {"quotient": _trim(quotient), "remainder": remainder}


static func _is_zero(limbs: Array[int]) -> bool:
	return limbs.size() == 1 and limbs[0] == 0


## Only used on newly owned output arrays, never on a caller's input array.
static func _trim(limbs: Array[int]) -> Array[int]:
	while limbs.size() > 1 and limbs.back() == 0:
		limbs.pop_back()
	return limbs


static func _success(value: Variant) -> Dictionary:
	return {"ok": true, "value": value}


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error": message}
