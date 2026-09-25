# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Invariant Int32/Single text boundaries used by authored-data readers.
## Raw UTF-16 avoids losing embedded NUL or surrogate units before admission.
## Decimal-to-Single rounds directly to binary32, never through binary64.
const Text = preload("res://Core/canonical_json_string.gd")
const Decimal = preload("res://Core/decimal_float64.gd")
const Wide = preload("res://Core/wide_integer.gd")


static func parse_int32(text: Variant) -> Dictionary:
	var admitted: Dictionary = _input(text)
	if not admitted.ok:
		return admitted
	var units: PackedInt32Array = admitted.value
	var cursor: int = 0
	while cursor < units.size() and _space(units[cursor]):
		cursor += 1
	var negative: bool = cursor < units.size() and units[cursor] == 45
	if cursor < units.size() and units[cursor] in [43, 45]:
		cursor += 1
	var start: int = cursor
	var magnitude: int = 0
	while _digit(units, cursor):
		magnitude = mini(2147483649, magnitude * 10 + units[cursor] - 48)
		cursor += 1
	if cursor == start or not _trailer(units, cursor):
		return _failure("FormatException", "Expected an invariant signed integer.")
	if magnitude > (2147483648 if negative else 2147483647):
		return _failure("OverflowException", "The value is outside Int32.")
	return {"ok": true, "value": -magnitude if negative else magnitude}


static func parse_float32(text: Variant) -> Dictionary:
	var admitted: Dictionary = _input(text)
	if not admitted.ok:
		return admitted
	var units: PackedInt32Array = admitted.value
	var cursor: int = 0
	while cursor < units.size() and _space(units[cursor]):
		cursor += 1
	var negative: bool = cursor < units.size() and units[cursor] == 45
	if cursor < units.size() and units[cursor] in [43, 45]:
		cursor += 1
	var integer: String = ""
	while _digit(units, cursor):
		integer += String.chr(units[cursor])
		cursor += 1
	var fraction: String = ""
	if cursor < units.size() and units[cursor] == 46:
		cursor += 1
		while _digit(units, cursor):
			fraction += String.chr(units[cursor])
			cursor += 1
	var exponent: String = ""
	var exponent_valid: bool = true
	if cursor < units.size() and units[cursor] in [69, 101]:
		cursor += 1
		exponent = "e"
		if cursor < units.size() and units[cursor] in [43, 45]:
			exponent += String.chr(units[cursor])
			cursor += 1
		var start: int = cursor
		while _digit(units, cursor):
			exponent += String.chr(units[cursor])
			cursor += 1
		exponent_valid = cursor > start
	if not (integer.is_empty() and fraction.is_empty()) and exponent_valid and _trailer(units, cursor):
		var first: int = 0
		while first < integer.length() and integer.unicode_at(first) == 48:
			first += 1
		integer = integer.substr(first)
		if integer.is_empty():
			integer = "0"
		var token: String = ("-" if negative else "") + integer
		if not fraction.is_empty():
			token += "." + fraction
		return Decimal.parse_float32(token + exponent)

	# The managed special-value fallback trims Unicode whitespace separately
	# from the numeric grammar. Its sign does not change the canonical NaN word.
	var first: int = 0
	var last: int = units.size()
	while first < last and _unicode_space(units[first]):
		first += 1
	while last > first and _unicode_space(units[last - 1]):
		last -= 1
	var special: String = ""
	for index: int in range(first, last):
		var unit: int = units[index]
		if unit >= 65 and unit <= 90:
			unit += 32
		special += String.chr(unit) if unit > 0 and unit < 128 else "?"
	if special in ["nan", "+nan", "-nan"]:
		return {"ok": true, "bits": 0xffc00000}
	if special in ["infinity", "+infinity", "-infinity"]:
		return {"ok": true, "bits": 0xff800000 if special.begins_with("-") else 0x7f800000}
	return _failure("FormatException", "Expected an invariant floating-point number.")


## Invariant default Single spelling, including shortest round-trip digits.
## Choose the nearest exact decimal at each precision and check its direct
## binary32 rounding. Nine significant digits suffice for every finite Single.
static func format_float32(bits: Variant) -> Dictionary:
	if typeof(bits) != TYPE_INT or bits < 0 or bits > 0xffffffff:
		return _failure("ArgumentOutOfRangeException", "Expected a UInt32 float word.", "bits")
	var negative: bool = (bits & 0x80000000) != 0
	var absolute: int = bits & 0x7fffffff
	if absolute > 0x7f800000:
		return {"ok": true, "value": "NaN"}
	if absolute == 0x7f800000:
		return {"ok": true, "value": "-Infinity" if negative else "Infinity"}
	if absolute == 0:
		return {"ok": true, "value": "-0" if negative else "0"}
	var exponent: int = (absolute >> 23) & 255
	var mantissa: int = absolute & 0x7fffff
	if exponent != 0:
		mantissa |= 0x800000
	var binary_scale: int = -149 if exponent == 0 else exponent - 150
	var numerator: Array[int] = Wide.from_int64(mantissa).value
	var denominator: Array[int] = [1]
	if binary_scale >= 0:
		numerator = Decimal._shift_left(numerator, binary_scale)
	else:
		denominator = Decimal._shift_left(denominator, -binary_scale)
	var order: int = 0
	var probe: Array[int]
	if Wide.compare(numerator, denominator).value >= 0:
		probe = Wide.multiply(denominator, [10]).value
		while Wide.compare(numerator, probe).value >= 0:
			order += 1
			probe = Wide.multiply(probe, [10]).value
	else:
		probe = numerator
		while Wide.compare(probe, denominator).value < 0:
			order -= 1
			probe = Wide.multiply(probe, [10]).value
	for precision: int in range(1, 10):
		var scale: int = order - precision + 1
		var top: Array[int] = numerator
		var bottom: Array[int] = denominator
		if scale < 0:
			top = Wide.multiply(top, _power10(-scale)).value
		else:
			bottom = Wide.multiply(bottom, _power10(scale)).value
		var divided: Dictionary = Wide.divmod(top, bottom)
		var decimal: int = Wide.to_int64(divided.quotient).value
		var halfway: int = Wide.compare(Wide.multiply(divided.remainder, [2]).value, bottom).value
		if halfway > 0 or (halfway == 0 and (decimal & 1) != 0):
			decimal += 1
		while decimal > 0 and decimal % 10 == 0:
			@warning_ignore("integer_division")
			decimal /= 10
			scale += 1
		var digits: String = str(decimal)
		var rounded: Dictionary = Decimal.parse_float32(digits + "e" + str(scale))
		if rounded.ok and rounded.bits == absolute:
			var shown: String
			var display_order: int = digits.length() + scale - 1
			if display_order < -4 or display_order >= 9:
				shown = digits.substr(0, 1)
				if digits.length() > 1:
					shown += "." + digits.substr(1)
				shown += "E" + ("-" if display_order < 0 else "+") + str(absi(display_order)).pad_zeros(2)
			elif scale >= 0:
				shown = digits + "0".repeat(scale)
			else:
				var point: int = digits.length() + scale
				shown = digits.substr(0, point) + "." + digits.substr(point) if point > 0 else "0." + "0".repeat(-point) + digits
			return {"ok": true, "value": ("-" if negative else "") + shown}
	return _failure("InvalidOperationException", "Could not format a finite float word.")


static func _power10(exponent: int) -> Array[int]:
	return Wide.from_decimal("1" + "0".repeat(exponent)).value


static func _input(text: Variant) -> Dictionary:
	var admitted: Dictionary = Text.units(text)
	if not admitted.ok:
		return _failure("ArgumentException", admitted.error, "text")
	if admitted.value == null:
		return _failure("ArgumentNullException", "A numeric string is required.", "s")
	return admitted


static func _digit(units: PackedInt32Array, index: int) -> bool:
	return index < units.size() and units[index] >= 48 and units[index] <= 57


static func _space(unit: int) -> bool:
	return unit == 32 or (unit >= 9 and unit <= 13)


static func _unicode_space(unit: int) -> bool:
	return _space(unit) or unit in [0x85, 0xa0, 0x1680, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000] or (unit >= 0x2000 and unit <= 0x200a)


static func _trailer(units: PackedInt32Array, position: int) -> bool:
	while position < units.size() and _space(units[position]):
		position += 1
	while position < units.size() and units[position] == 0:
		position += 1
	return position == units.size()


static func _failure(kind: String, message: String, parameter: String = "") -> Dictionary:
	return {"ok": false, "error_type": kind, "parameter": parameter, "error": message}
