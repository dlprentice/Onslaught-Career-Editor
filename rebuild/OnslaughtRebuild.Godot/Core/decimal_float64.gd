# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Exact JSON decimal -> IEEE binary64, round-to-nearest/ties-to-even.
## Godot 4.8 String.to_float() is not bit-equivalent to the .NET JSON reader;
## Core/strict_json.gd retains tokens until this explicit conversion is wanted.
## The exact integer ratio is rounded once, including signed zero, subnormals
## and overflow. No floating-point arithmetic participates in the conversion.

const Wide = preload("res://Core/wide_integer.gd")
const HIDDEN_BIT: int = 1 << 52


static func parse(token: String) -> Dictionary:
    var parts: Dictionary = _parts(token)
    if not parts.ok:
        return parts
    var digits: String = parts.digits
    var negative: bool = parts.negative
    var decimal_exponent: int = parts.exponent
    if digits.is_empty():
        return _from_word(0, negative)
    var decimal_order: int = digits.length() - 1 + decimal_exponent
    if decimal_order > 308:
        return _from_word(0x7ff0000000000000, negative)
    if decimal_order < -324:
        return _from_word(0, negative)
    var numerator: Array[int] = Wide.from_decimal(digits).value
    var denominator: Array[int] = [1]
    if decimal_exponent >= 0:
        numerator = Wide.multiply(numerator, Wide.from_decimal("1" + "0".repeat(decimal_exponent)).value).value
    else:
        denominator = Wide.from_decimal("1" + "0".repeat(-decimal_exponent)).value

    var exponent: int = _bit_length(numerator) - _bit_length(denominator)
    var comparison: int
    if exponent >= 0:
        comparison = Wide.compare(numerator, _shift_left(denominator, exponent)).value
    else:
        comparison = Wide.compare(_shift_left(numerator, -exponent), denominator).value
    if comparison < 0:
        exponent -= 1
    if exponent > 1023:
        return _from_word(0x7ff0000000000000, negative)

    var quantum: int = maxi(-1074, exponent - 52)
    if quantum >= 0:
        denominator = _shift_left(denominator, quantum)
    else:
        numerator = _shift_left(numerator, -quantum)
    var divided: Dictionary = Wide.divmod(numerator, denominator)
    if not divided.ok:
        return divided
    var narrowed: Dictionary = Wide.to_int64(divided.quotient)
    if not narrowed.ok:
        return narrowed
    var significand: int = narrowed.value
    var halfway: int = Wide.compare(_shift_left(divided.remainder, 1), denominator).value
    if halfway > 0 or (halfway == 0 and (significand & 1) != 0):
        significand += 1
    if exponent < -1022:
        # A rounded subnormal may carry directly into the smallest normal.
        return _from_word(significand, negative)
    if significand == (HIDDEN_BIT << 1):
        significand >>= 1
        exponent += 1
    if exponent > 1023:
        return _from_word(0x7ff0000000000000, negative)
    return _from_word(((exponent + 1023) << 52) | (significand - HIDDEN_BIT), negative)


static func _parts(token: String) -> Dictionary:
    var length: int = token.length()
    var cursor: int = 0
    var negative: bool = length > 0 and token.unicode_at(0) == 45
    if negative:
        cursor += 1
    var integer_start: int = cursor
    if cursor < length and token.unicode_at(cursor) == 48:
        cursor += 1
    else:
        if not _digit(token, cursor) or token.unicode_at(cursor) == 48:
            return _failure()
        while _digit(token, cursor):
            cursor += 1
    var integer_end: int = cursor
    var fraction_start: int = cursor
    var fraction_end: int = cursor
    if cursor < length and token.unicode_at(cursor) == 46:
        cursor += 1
        fraction_start = cursor
        if not _digit(token, cursor):
            return _failure()
        while _digit(token, cursor):
            cursor += 1
        fraction_end = cursor
    var exponent: int = fraction_start - fraction_end
    if cursor < length and token.unicode_at(cursor) in [69, 101]:
        cursor += 1
        var exponent_negative: bool = cursor < length and token.unicode_at(cursor) == 45
        if cursor < length and token.unicode_at(cursor) in [43, 45]:
            cursor += 1
        if not _digit(token, cursor):
            return _failure()
        var magnitude: int = 0
        # Beyond this bound, no number of significand digits in this token can
        # cancel the exponent back into the binary64 range. Avoid integer wrap.
        var cap: int = length + 1024
        while _digit(token, cursor):
            magnitude = mini(cap, magnitude * 10 + token.unicode_at(cursor) - 48)
            cursor += 1
        exponent += -magnitude if exponent_negative else magnitude
    if cursor != length:
        return _failure()
    var digits: String = token.substr(integer_start, integer_end - integer_start) + token.substr(fraction_start, fraction_end - fraction_start)
    var first: int = 0
    while first < digits.length() and digits.unicode_at(first) == 48:
        first += 1
    var last: int = digits.length()
    while last > first and digits.unicode_at(last - 1) == 48:
        last -= 1
        exponent += 1
    return {"ok": true, "digits": digits.substr(first, last - first), "exponent": exponent, "negative": negative}


static func _digit(text: String, position: int) -> bool:
    return position < text.length() and text.unicode_at(position) >= 48 and text.unicode_at(position) <= 57


static func _bit_length(value: Array[int]) -> int:
    var bits: int = (value.size() - 1) * 15
    var top: int = value[-1]
    while top > 0:
        bits += 1
        top >>= 1
    return bits


static func _shift_left(value: Array[int], bits: int) -> Array[int]:
    if value.size() == 1 and value[0] == 0:
        return [0]
    @warning_ignore("integer_division")
    var words: int = bits / 15
    var shift: int = bits % 15
    var result: Array[int] = []
    result.resize(words)
    result.fill(0)
    var carry: int = 0
    for word: int in value:
        var wide: int = (word << shift) | carry
        result.append(wide & 32767)
        carry = wide >> 15
    if carry != 0:
        result.append(carry)
    return result


static func _from_word(word: int, negative: bool) -> Dictionary:
    if negative:
        word |= 1 << 63
    var bytes := PackedByteArray()
    bytes.resize(8)
    bytes.encode_s64(0, word)
    return {"ok": true, "value": bytes.decode_double(0)}


static func _failure() -> Dictionary:
    return {"ok": false, "error": "Expected one complete JSON decimal number token."}
