# SPDX-License-Identifier: MIT
extends RefCounted
## Standalone one-Int32 invariant composite formatting compatibility utility.
## No locale, floating-point conversion, filesystem or engine state participates.
## Accepted formats exceeding the bounded text carrier return UnsupportedFormat;
## malformed composite/number formats return FormatException. Raw UTF-16 callers
## use format_composite_units to retain NUL and unpaired code units. This utility has no
## project, retail-data, application-core or simulation dependencies.
##
## Numeric section/scaling/rounding and composite grammar adapted from:
## https://github.com/dotnet/runtime/blob/v8.0.0/src/libraries/System.Private.CoreLib/src/System/Number.Formatting.cs
## https://github.com/dotnet/runtime/blob/v10.0.0/src/libraries/System.Private.CoreLib/src/System/Text/ValueStringBuilder.AppendFormat.cs
## Those portions are Copyright (c) .NET Foundation and Contributors, MIT:
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
## of the Software, and to permit persons to whom the Software is furnished to do
## so, subject to the following conditions: The above copyright notice and this
## permission notice shall be included in all copies or substantial portions of
## the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
## EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
## OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
## ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
## DEALINGS IN THE SOFTWARE.

const MAX_TEXT_UNITS: int = 65536
const COMPOSITE_DIGIT_LIMIT: int = 1000000


static func format_composite(template: Variant, value: Variant) -> Dictionary:
    if typeof(template) != TYPE_STRING:
        return _error("ArgumentException", "The composite template must be a String.")
    var units: PackedInt32Array = _text_units(template)
    if units.has(0):
        return _error("UnsupportedFormat", "An embedded NUL requires format_composite_units, not a Godot String.")
    var result: Dictionary = format_composite_units(units, value)
    if not result.ok:
        return result
    var decoded: Dictionary = _numeric_pattern(result.value)
    if not decoded.replacements.is_empty():
        return _error("UnsupportedFormat", "Unpaired UTF-16 requires format_composite_units, not a Godot String.")
    return {"ok": true, "value": decoded.value}


## One composite parser for both APIs. Literal UTF-16 units are never converted
## through Godot String; braces/index/alignment are ASCII grammar. Numeric
## patterns alone use a reversible carrier for any unpaired literal surrogates.
static func format_composite_units(template: Variant, value: Variant) -> Dictionary:
    if typeof(template) != TYPE_PACKED_INT32_ARRAY:
        return _error("ArgumentException", "The composite template must be PackedInt32Array UTF-16 units.")
    if typeof(value) != TYPE_INT or value < -2147483648 or value > 2147483647:
        return _error("ArgumentException", "The formatting argument must be an exact signed Int32.")
    var text: PackedInt32Array = template
    if text.size() > MAX_TEXT_UNITS:
        return _unsupported()
    for unit: int in text:
        if unit < 0 or unit > 65535:
            return _error("ArgumentException", "UTF-16 units must be integers in [0,65535].")
    var output := PackedInt32Array()
    var cursor: int = 0
    while cursor < text.size():
        var character: int = text[cursor]
        cursor += 1
        if character != 123 and character != 125:
            output.append(character)
            continue
        if cursor < text.size() and text[cursor] == character:
            output.append(character)
            cursor += 1
            continue
        if character != 123 or not _unit_digit(text, cursor):
            return _malformed()
        var argument_index: int = text[cursor] - 48
        cursor += 1
        while _unit_digit(text, cursor) and argument_index < COMPOSITE_DIGIT_LIMIT:
            argument_index = argument_index * 10 + text[cursor] - 48
            cursor += 1
        while cursor < text.size() and text[cursor] == 32:
            cursor += 1
        var width: int = 0
        var left_justify: bool = false
        if cursor < text.size() and text[cursor] == 44:
            cursor += 1
            while cursor < text.size() and text[cursor] == 32:
                cursor += 1
            if cursor < text.size() and text[cursor] == 45:
                left_justify = true
                cursor += 1
            if not _unit_digit(text, cursor):
                return _malformed()
            width = text[cursor] - 48
            cursor += 1
            while _unit_digit(text, cursor) and width < COMPOSITE_DIGIT_LIMIT:
                width = width * 10 + text[cursor] - 48
                cursor += 1
            while cursor < text.size() and text[cursor] == 32:
                cursor += 1
        var numeric_units := PackedInt32Array()
        if cursor < text.size() and text[cursor] == 58:
            cursor += 1
            var start: int = cursor
            while cursor < text.size() and text[cursor] != 125:
                if text[cursor] == 123:
                    return _malformed()
                cursor += 1
            numeric_units = text.slice(start, cursor)
        if cursor == text.size() or text[cursor] != 125 or argument_index != 0:
            return _malformed()
        cursor += 1
        var numeric: Dictionary = _numeric_pattern(numeric_units)
        var formatted: Dictionary = _format_number(numeric.value, value)
        if not formatted.ok:
            return formatted
        var rendered: PackedInt32Array = _text_units(formatted.value, numeric.replacements)
        if output.size() + maxi(width, rendered.size()) > MAX_TEXT_UNITS:
            return _unsupported()
        var padding := PackedInt32Array()
        padding.resize(maxi(0, width - rendered.size()))
        padding.fill(32)
        output.append_array(rendered if left_justify else padding)
        output.append_array(padding if left_justify else rendered)
    if output.size() > MAX_TEXT_UNITS:
        return _unsupported()
    return {"ok": true, "value": output}


static func _numeric_pattern(units: PackedInt32Array) -> Dictionary:
    var end: int = units.find(0)
    var terminated: bool = end >= 0
    if not terminated:
        end = units.size()
    var characters: Array[int] = []
    var occupied: Dictionary = {}
    var cursor: int = 0
    while cursor < end:
        var code: int = units[cursor]
        cursor += 1
        if code >= 0xd800 and code <= 0xdbff and cursor < end and units[cursor] >= 0xdc00 and units[cursor] <= 0xdfff:
            code = 0x10000 + ((code - 0xd800) << 10) + units[cursor] - 0xdc00
            cursor += 1
        occupied[code] = true
        characters.append(code)
    # Numeric punctuation is ASCII except per-mille. Unpaired surrogate units
    # are therefore literal text. Move only those units into unused supplementary
    # private-use scalars, then reverse the mapping before alignment or admission.
    # At most 32768 supplementary scalars and 2048 distinct surrogate units fit
    # in a bounded input, so this range always has enough unused carriers.
    var replacements: Dictionary = {}
    var assigned: Dictionary = {}
    var candidate: int = 0xf0000
    var pieces := PackedStringArray()
    for original: int in characters:
        var code: int = original
        if code >= 0xd800 and code <= 0xdfff:
            if not assigned.has(code):
                while occupied.has(candidate):
                    candidate += 1
                assigned[code] = candidate
                replacements[candidate] = code
                occupied[candidate] = true
                candidate += 1
            code = assigned[code]
        pieces.append(String.chr(code))
    var output: String = "".join(pieces)
    # .NET's compatibility NUL terminator reaches its multi-character standard
    # parser: "E\0ignored" has precision 0, unlike bare "E" (default 6).
    if terminated and end == 1 and ((units[0] >= 65 and units[0] <= 90) or (units[0] >= 97 and units[0] <= 122)):
        output += "0"
    return {"value": output, "replacements": replacements}


static func _text_units(text: String, replacements: Dictionary = {}) -> PackedInt32Array:
    var units := PackedInt32Array()
    for index: int in range(text.length()):
        var code: int = text.unicode_at(index)
        if replacements.has(code):
            units.append(replacements[code])
        elif code > 0xffff:
            code -= 0x10000
            units.append(0xd800 + (code >> 10))
            units.append(0xdc00 + (code & 0x3ff))
        else:
            units.append(code)
    return units


static func _unit_digit(text: PackedInt32Array, position: int) -> bool:
    return position < text.size() and text[position] >= 48 and text[position] <= 57


static func _format_number(pattern: String, value: int) -> Dictionary:
    var specifier: String = "G"
    var precision: int = -1
    var standard: bool = pattern.is_empty()
    if not pattern.is_empty():
        var code: int = pattern.unicode_at(0)
        if (code >= 65 and code <= 90) or (code >= 97 and code <= 122):
            specifier = pattern[0]
            if pattern.length() == 1:
                standard = true
            else:
                precision = 0
                var cursor: int = 1
                while _digit(pattern, cursor):
                    # The actual runtime refuses overflow before checking if a
                    # following non-digit would otherwise make this custom.
                    if precision >= 100000000:
                        return _malformed()
                    precision = precision * 10 + pattern.unicode_at(cursor) - 48
                    cursor += 1
                standard = cursor == pattern.length()
    if not standard:
        return _format_custom(pattern, value)
    var upper: String = specifier.to_upper()
    if not upper in ["B", "C", "D", "E", "F", "G", "N", "P", "R", "X"]:
        return _malformed()
    if precision > MAX_TEXT_UNITS and upper != "G" and upper != "R":
        return _unsupported()
    var magnitude: String = str(absi(value))
    var sign: String = "-" if value < 0 else ""
    if upper == "D" or (upper == "G" and precision < 1):
        return _success(sign + "0".repeat(maxi(0, precision - magnitude.length())) + magnitude)
    if upper == "X" or upper == "B":
        var unsigned: int = value & 0xffffffff
        var radix_bits: int = 4 if upper == "X" else 1
        var alphabet: String = "0123456789ABCDEF" if specifier == "X" else "0123456789abcdef"
        var digits: String = ""
        while unsigned != 0 or digits.is_empty():
            digits = alphabet[unsigned & ((1 << radix_bits) - 1)] + digits
            unsigned >>= radix_bits
        return _success("0".repeat(maxi(0, precision - digits.length())) + digits)
    if upper in ["C", "F", "N", "P"]:
        var decimals: int = precision if precision >= 0 else 2
        if upper == "P":
            magnitude = str(absi(value) * 100)
        if upper != "F":
            magnitude = _group(magnitude)
        var number: String = magnitude + ("." + "0".repeat(decimals) if decimals > 0 else "")
        if upper == "C":
            return _success("(¤" + number + ")" if value < 0 else "¤" + number)
        if upper == "P":
            return _success(sign + number + " %")
        return _success(sign + number)
    var state: Dictionary = _number(value)
    if upper == "E":
        var decimals: int = precision if precision >= 0 else 6
        _round_number(state, decimals + 1)
        var digits: String = state.digits
        var mantissa: String = digits[0] if not digits.is_empty() else "0"
        if decimals > 0:
            var tail: String = digits.substr(1) if digits.length() > 1 else ""
            mantissa += "." + tail + "0".repeat(decimals - tail.length())
        return _success(sign + mantissa + _exponent(specifier, state.scale - 1 if not digits.is_empty() else 0, 3, true))
    # Integral R/r follows G/g, including an explicit significant precision.
    var significant: int = precision if precision > 0 else magnitude.length()
    _round_number(state, significant)
    var digits: String = state.digits
    if state.scale > significant or state.scale < -3:
        var tail: String = digits.substr(1)
        var result: String = sign + digits[0] + ("." + tail if not tail.is_empty() else "")
        return _success(result + _exponent("E" if specifier == upper else "e", state.scale - 1, 2, true))
    return _success(sign + (digits + "0".repeat(maxi(0, state.scale - digits.length())) if not digits.is_empty() else "0"))


static func _number(value: int) -> Dictionary:
    var digits: String = str(absi(value)) if value != 0 else ""
    return {"digits": digits, "scale": digits.length(), "negative": value < 0}


static func _round_number(number: Dictionary, position: int) -> void:
    # Int32/custom NumberBuffer formatting rounds a discarded 5 upward. This is
    # the integer formatter's law, separate from binary64's ties-to-even codec.
    var digits: String = number.digits
    var cursor: int = mini(maxi(0, position), digits.length())
    if cursor == position and cursor < digits.length() and digits.unicode_at(cursor) >= 53:
        while cursor > 0 and digits[cursor - 1] == "9":
            cursor -= 1
        if cursor > 0:
            digits = digits.substr(0, cursor - 1) + String.chr(digits.unicode_at(cursor - 1) + 1)
        else:
            number.scale += 1
            digits = "1"
            cursor = 1
    else:
        while cursor > 0 and digits[cursor - 1] == "0":
            cursor -= 1
        digits = digits.substr(0, cursor)
    if cursor == 0:
        number.negative = false
        number.scale = 0
    number.digits = digits


static func _format_custom(pattern: String, value: int) -> Dictionary:
    var state: Dictionary = _number(value)
    var section: int = _find_section(pattern, 2 if value == 0 else 1 if value < 0 else 0)
    var picture: Dictionary
    while true:
        picture = _scan_section(pattern, section)
        if not state.digits.is_empty():
            state.scale += picture.scale_adjust
            var position: int = picture.digit_count if picture.scientific else state.scale + picture.digit_count - picture.decimal_pos
            _round_number(state, position)
            if state.digits.is_empty():
                var zero_section: int = _find_section(pattern, 2)
                if zero_section != section:
                    section = zero_section
                    continue
        else:
            state.negative = false
            state.scale = 0
        break
    var first_required: int = picture.decimal_pos - picture.first_digit if picture.first_digit < picture.decimal_pos else 0
    var last_required: int = picture.decimal_pos - picture.last_digit if picture.last_digit > picture.decimal_pos else 0
    var scientific: bool = picture.scientific
    var digit_position: int = picture.decimal_pos if scientific else maxi(state.scale, picture.decimal_pos)
    var adjust: int = 0 if scientific else state.scale - picture.decimal_pos
    var total_digits: int = maxi(first_required, digit_position + mini(adjust, 0))
    var output: String = "-" if state.negative and section == 0 and state.scale != 0 else ""
    var digits: String = state.digits
    var digit_cursor: int = 0
    var cursor: int = section
    var decimal_written: bool = false
    while cursor < pattern.length() and pattern[cursor] != ";":
        var character: String = pattern[cursor]
        cursor += 1
        if adjust > 0 and character in ["#", "0", "."]:
            if output.length() + adjust > MAX_TEXT_UNITS:
                return _unsupported()
            while adjust > 0:
                output += digits[digit_cursor] if digit_cursor < digits.length() else "0"
                if digit_cursor < digits.length():
                    digit_cursor += 1
                if picture.thousand_seps and _separator_at(digit_position, total_digits):
                    output += ","
                digit_position -= 1
                adjust -= 1
        match character:
            "#", "0":
                var digit: String = ""
                if adjust < 0:
                    adjust += 1
                    if digit_position <= first_required:
                        digit = "0"
                elif digit_cursor < digits.length():
                    digit = digits[digit_cursor]
                    digit_cursor += 1
                elif digit_position > last_required:
                    digit = "0"
                if not digit.is_empty():
                    output += digit
                    if picture.thousand_seps and _separator_at(digit_position, total_digits):
                        output += ","
                digit_position -= 1
            ".":
                if digit_position == 0 and not decimal_written and (last_required < 0 or (picture.decimal_pos < picture.digit_count and digit_cursor < digits.length())):
                    output += "."
                    decimal_written = true
            ",":
                pass
            "'", '"':
                var literal_start: int = cursor
                while cursor < pattern.length() and pattern[cursor] != character:
                    cursor += 1
                output += pattern.substr(literal_start, cursor - literal_start)
                if cursor < pattern.length():
                    cursor += 1
            "\\":
                if cursor < pattern.length():
                    output += pattern[cursor]
                    cursor += 1
            "E", "e":
                var exponent_end: int = _exponent_end(pattern, cursor)
                if scientific and exponent_end != cursor:
                    var positive_sign: bool = pattern[cursor] == "+"
                    var zeros: int = exponent_end - cursor - (1 if pattern[cursor] in ["+", "-"] else 0)
                    output += _exponent(character, 0 if digits.is_empty() else state.scale - picture.decimal_pos, mini(zeros, 10), positive_sign)
                    cursor = exponent_end
                    scientific = false
                elif not scientific:
                    output += character
                    if cursor < pattern.length() and pattern[cursor] in ["+", "-"]:
                        output += pattern[cursor]
                        cursor += 1
                    while cursor < pattern.length() and pattern[cursor] == "0":
                        output += "0"
                        cursor += 1
                else:
                    output += character
            _:
                output += character
        if output.length() > MAX_TEXT_UNITS:
            return _unsupported()
    if state.negative and section == 0 and state.scale == 0 and not output.is_empty():
        output = "-" + output
    return _success(output)


static func _scan_section(pattern: String, section: int) -> Dictionary:
    var result: Dictionary = {"digit_count": 0, "decimal_pos": -1, "first_digit": 2147483647,
        "last_digit": 0, "scientific": false, "thousand_seps": false, "scale_adjust": 0}
    var thousand_position: int = -1
    var thousand_count: int = 0
    var cursor: int = section
    while cursor < pattern.length() and pattern[cursor] != ";":
        var character: String = pattern[cursor]
        cursor += 1
        match character:
            "#":
                result.digit_count += 1
            "0":
                if result.first_digit == 2147483647:
                    result.first_digit = result.digit_count
                result.digit_count += 1
                result.last_digit = result.digit_count
            ".":
                if result.decimal_pos < 0:
                    result.decimal_pos = result.digit_count
            ",":
                if result.digit_count > 0 and result.decimal_pos < 0:
                    if thousand_position == result.digit_count:
                        thousand_count += 1
                    else:
                        if thousand_position >= 0:
                            result.thousand_seps = true
                        thousand_position = result.digit_count
                        thousand_count = 1
            "%":
                result.scale_adjust += 2
            "‰":
                result.scale_adjust += 3
            "'", '"':
                while cursor < pattern.length() and pattern[cursor] != character:
                    cursor += 1
                if cursor < pattern.length():
                    cursor += 1
            "\\":
                cursor += 1 if cursor < pattern.length() else 0
            "E", "e":
                var end: int = _exponent_end(pattern, cursor)
                if end != cursor:
                    result.scientific = true
                    cursor = end
    if result.decimal_pos < 0:
        result.decimal_pos = result.digit_count
    if thousand_position >= 0:
        if thousand_position == result.decimal_pos:
            result.scale_adjust -= thousand_count * 3
        else:
            result.thousand_seps = true
    return result


static func _find_section(pattern: String, requested: int) -> int:
    if requested == 0:
        return 0
    var cursor: int = 0
    while cursor < pattern.length():
        var character: String = pattern[cursor]
        cursor += 1
        if character in ["'", '"']:
            while cursor < pattern.length() and pattern[cursor] != character:
                cursor += 1
            if cursor < pattern.length():
                cursor += 1
        elif character == "\\":
            cursor += 1 if cursor < pattern.length() else 0
        elif character == ";":
            requested -= 1
            if requested == 0:
                return cursor if cursor < pattern.length() and pattern[cursor] != ";" else 0
    return 0


static func _exponent_end(pattern: String, start: int) -> int:
    var cursor: int = start
    if cursor < pattern.length() and pattern[cursor] in ["+", "-"]:
        cursor += 1
    if cursor == pattern.length() or pattern[cursor] != "0":
        return start
    while cursor < pattern.length() and pattern[cursor] == "0":
        cursor += 1
    return cursor


static func _exponent(marker: String, exponent: int, precision: int, positive_sign: bool) -> String:
    var magnitude: String = str(absi(exponent))
    return marker + ("-" if exponent < 0 else "+" if positive_sign else "") + "0".repeat(maxi(0, precision - magnitude.length())) + magnitude


static func _group(digits: String) -> String:
    var output: String = ""
    for cursor: int in range(digits.length()):
        if cursor > 0 and (digits.length() - cursor) % 3 == 0:
            output += ","
        output += digits[cursor]
    return output


static func _separator_at(position: int, total: int) -> bool:
    return position > 1 and (position - 1) % 3 == 0 and position - 1 < total


static func _utf16_length(text: String) -> int:
    var units: int = text.length()
    for index: int in range(text.length()):
        if text.unicode_at(index) > 0xffff:
            units += 1
    return units


static func _digit(text: String, position: int) -> bool:
    return position < text.length() and text.unicode_at(position) >= 48 and text.unicode_at(position) <= 57


static func _success(value: String) -> Dictionary:
    # An internal supplementary carrier can use two UTF-16 units for one raw
    # surrogate literal. The public parser enforces MAX_TEXT_UNITS after recovery.
    if _utf16_length(value) > MAX_TEXT_UNITS * 2:
        return _unsupported()
    return {"ok": true, "value": value}


static func _error(kind: String, reason: String) -> Dictionary:
    return {"ok": false, "error_type": kind, "error": reason}


static func _malformed() -> Dictionary:
    return _error("FormatException", "Invalid invariant Int32 composite format.")


static func _unsupported() -> Dictionary:
    return _error("UnsupportedFormat", "Formatting exceeds the supported 65536 UTF-16 code-unit text carrier.")
