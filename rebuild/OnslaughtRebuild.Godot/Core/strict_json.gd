# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
const Decimal = preload("res://Core/decimal_float64.gd")

# Deterministic JSON admission for replay/manifest readers. Godot's JSON reader
# intentionally permits trailing commas/control characters and converts every
# number to double. Keep number tokens, UTF-16 units and ordered properties until
# the owning schema admits them. No filesystem, engine nodes or simulation state.
# Mirrors the strict grammar/depth and duplicate-name rule used by
# OnslaughtRebuild.Core/CommandTape.cs; not a substitute for schema validation.

class Value extends RefCounted:
    var kind: String
    var number_text: String = ""
    var string_units := PackedInt32Array()
    var boolean: bool = false
    var items: Array[Value] = []
    # Entries are {name: Value(kind=string), value: Value}. An array deliberately
    # retains duplicate names when a schema elects last-property semantics.
    var members: Array[Dictionary] = []

    func _init(value_kind: String) -> void:
        kind = value_kind

    func member(name: String) -> Value:
        if kind != "object":
            return null
        var wanted := PackedInt32Array()
        for index: int in range(name.length()):
            var code: int = name.unicode_at(index)
            if code > 0xffff:
                code -= 0x10000
                wanted.append(0xd800 + (code >> 10))
                wanted.append(0xdc00 + (code & 0x3ff))
            else:
                wanted.append(code)
        for index: int in range(members.size() - 1, -1, -1):
            if members[index].name.string_units == wanted:
                return members[index].value
        return null

    func as_int64() -> Dictionary:
        if kind != "number" or number_text.contains(".") or number_text.contains("e") or number_text.contains("E"):
            return {"ok": false, "error": "Expected an integer number token."}
        var negative: bool = number_text.begins_with("-")
        var digits: String = number_text.substr(1) if negative else number_text
        var limit: String = "9223372036854775808" if negative else "9223372036854775807"
        if digits.length() > limit.length() or (digits.length() == limit.length() and digits > limit):
            return {"ok": false, "error": "Integer is outside the signed 64-bit range."}
        # Accumulate negatively so INT64_MIN never requires an overflowing
        # positive temporary. Syntax has already been admitted by the parser.
        var value: int = 0
        for index: int in range(digits.length()):
            value = value * 10 - (digits.unicode_at(index) - 48)
        return {"ok": true, "value": value if negative else -value}

    func as_int32() -> Dictionary:
        var result: Dictionary = as_int64()
        if result.ok and (result.value < -2147483648 or result.value > 2147483647):
            return {"ok": false, "error": "Integer is outside the signed 32-bit range."}
        return result

    func as_float64() -> Dictionary:
        if kind != "number":
            return {"ok": false, "error": "Expected a number token."}
        # Conversion happens only after grammar admission and only on request.
        # Integer consumers must use as_int64/as_int32, never this path.
        return Decimal.parse(number_text)

    func utf8_bytes() -> Dictionary:
        if kind != "string":
            return {"ok": false, "error": "Expected a string token."}
        var result := PackedByteArray()
        var index: int = 0
        while index < string_units.size():
            var code: int = string_units[index]
            index += 1
            if code >= 0xd800 and code <= 0xdbff:
                if index == string_units.size() or string_units[index] < 0xdc00 or string_units[index] > 0xdfff:
                    return {"ok": false, "error": "Unpaired UTF-16 high surrogate."}
                code = 0x10000 + ((code - 0xd800) << 10) + (string_units[index] - 0xdc00)
                index += 1
            elif code >= 0xdc00 and code <= 0xdfff:
                return {"ok": false, "error": "Unpaired UTF-16 low surrogate."}
            if code < 0x80:
                result.append(code)
            elif code < 0x800:
                result.append(0xc0 | (code >> 6))
                result.append(0x80 | (code & 0x3f))
            elif code < 0x10000:
                result.append(0xe0 | (code >> 12))
                result.append(0x80 | ((code >> 6) & 0x3f))
                result.append(0x80 | (code & 0x3f))
            else:
                result.append(0xf0 | (code >> 18))
                result.append(0x80 | ((code >> 12) & 0x3f))
                result.append(0x80 | ((code >> 6) & 0x3f))
                result.append(0x80 | (code & 0x3f))
        return {"ok": true, "value": result}

    func as_string() -> Dictionary:
        var encoded: Dictionary = utf8_bytes()
        if not encoded.ok:
            return encoded
        if string_units.has(0):
            # Godot 4.8's UTF-8 conversion truncates/replaces embedded NUL.
            # Raw units/utf8_bytes preserve it; a caller requesting a native
            # String must make that limitation explicit instead of losing data.
            return {"ok": false, "error": "Embedded NUL requires string_units or utf8_bytes()."}
        return {"ok": true, "value": encoded.value.get_string_from_utf8()}


static func parse_bytes(source: PackedByteArray, reject_duplicates: bool = true, max_depth: int = 64) -> Dictionary:
    if max_depth < 1 or max_depth > 256:
        return {"ok": false, "error": "JSON maximum depth must be in [1,256].", "offset": 0}
    # A parser owns its cursor and a detached input; no state survives a call.
    var parser := Parser.new()
    parser._source = source.duplicate()
    parser._max_depth = max_depth
    parser._reject_duplicates = reject_duplicates
    var value: Value = parser._read_value(0)
    parser._skip_space()
    if parser._error.is_empty() and parser._position != source.size():
        parser._fail("Extra bytes after the JSON value.")
    if not parser._error.is_empty():
        return {"ok": false, "error": parser._error, "offset": parser._position}
    return {"ok": true, "value": value}



class Parser extends RefCounted:
    var _source: PackedByteArray
    var _position: int = 0
    var _error: String = ""
    var _max_depth: int = 64
    var _reject_duplicates: bool = true

    func _skip_space() -> void:
        while _position < _source.size() and _source[_position] in [9, 10, 13, 32]:
            _position += 1


    func _read_value(depth: int) -> Value:
        _skip_space()
        if _position == _source.size():
            return _fail("Expected a JSON value.")
        match _source[_position]:
            123:
                return _read_object(depth)
            91:
                return _read_array(depth)
            34:
                return _read_string()
            116:
                return _read_literal("true", "boolean", true)
            102:
                return _read_literal("false", "boolean", false)
            110:
                return _read_literal("null", "null", false)
            _:
                return _read_number()


    func _read_object(depth: int) -> Value:
        if depth >= _max_depth:
            return _fail("JSON nesting exceeds the admitted depth.")
        _position += 1
        var result := Value.new("object")
        var names: Dictionary = {}
        _skip_space()
        if _take(125):
            return result
        while _error.is_empty():
            _skip_space()
            if _position == _source.size() or _source[_position] != 34:
                return _fail("Expected a quoted object member name.")
            var name: Value = _read_string()
            if name == null:
                return null
            # CommandTape.ValidateUniqueMembers reads each JsonProperty.Name
            # before comparing it. Invalid surrogate names fail at that stage;
            # string values retain their later, schema-owned decoding boundary.
            if _reject_duplicates and not name.utf8_bytes().ok:
                return _fail("Invalid Unicode object member name.")
            var key: String = name.string_units.to_byte_array().hex_encode()
            if _reject_duplicates and names.has(key):
                return _fail("Duplicate JSON object member.")
            names[key] = true
            _skip_space()
            if not _take(58):
                return _fail("Expected a colon after an object member name.")
            var value: Value = _read_value(depth + 1)
            if value == null:
                return null
            result.members.append({"name": name, "value": value})
            _skip_space()
            if _take(125):
                return result
            if not _take(44):
                return _fail("Expected a comma or object end.")
        return null


    func _read_array(depth: int) -> Value:
        if depth >= _max_depth:
            return _fail("JSON nesting exceeds the admitted depth.")
        _position += 1
        var result := Value.new("array")
        _skip_space()
        if _take(93):
            return result
        while _error.is_empty():
            var value: Value = _read_value(depth + 1)
            if value == null:
                return null
            result.items.append(value)
            _skip_space()
            if _take(93):
                return result
            if not _take(44):
                return _fail("Expected a comma or array end.")
        return null


    func _read_string() -> Value:
        _position += 1
        var result := Value.new("string")
        while _position < _source.size():
            var code: int = _source[_position]
            _position += 1
            if code == 34:
                return result
            if code < 32:
                return _fail("Unescaped control byte in JSON string.")
            if code == 92:
                if _position == _source.size():
                    return _fail("Truncated JSON escape.")
                code = _source[_position]
                _position += 1
                match code:
                    34, 47, 92: pass
                    98: code = 8
                    102: code = 12
                    110: code = 10
                    114: code = 13
                    116: code = 9
                    117:
                        code = _read_hex_unit()
                        if code < 0:
                            return null
                    _: return _fail("Invalid JSON escape.")
                result.string_units.append(code)
                continue
            if code >= 128:
                var following: int
                var minimum: int
                if code >= 0xc2 and code <= 0xdf:
                    following = 1
                    minimum = 0x80
                    code &= 0x1f
                elif code >= 0xe0 and code <= 0xef:
                    following = 2
                    minimum = 0x800
                    code &= 0xf
                elif code >= 0xf0 and code <= 0xf4:
                    following = 3
                    minimum = 0x10000
                    code &= 7
                else:
                    return _fail("Invalid UTF-8 lead byte.")
                for ignored: int in range(following):
                    if _position == _source.size() or _source[_position] < 0x80 or _source[_position] > 0xbf:
                        return _fail("Invalid UTF-8 continuation byte.")
                    code = (code << 6) | (_source[_position] & 0x3f)
                    _position += 1
                if code < minimum or code > 0x10ffff or (code >= 0xd800 and code <= 0xdfff):
                    return _fail("Invalid Unicode scalar in UTF-8.")
            if code > 0xffff:
                code -= 0x10000
                result.string_units.append(0xd800 + (code >> 10))
                result.string_units.append(0xdc00 + (code & 0x3ff))
            else:
                result.string_units.append(code)
        return _fail("Unterminated JSON string.")


    func _read_hex_unit() -> int:
        var value: int = 0
        for ignored: int in range(4):
            if _position == _source.size():
                _fail("Truncated Unicode escape.")
                return -1
            var code: int = _source[_position]
            _position += 1
            var digit: int = code - 48 if code >= 48 and code <= 57 else code - 65 + 10 if code >= 65 and code <= 70 else code - 97 + 10 if code >= 97 and code <= 102 else -1
            if digit < 0:
                _fail("Invalid hexadecimal Unicode escape.")
                return -1
            value = (value << 4) | digit
        return value


    func _read_literal(text: String, kind: String, boolean: bool) -> Value:
        var bytes: PackedByteArray = text.to_ascii_buffer()
        if _source.slice(_position, _position + bytes.size()) != bytes:
            return _fail("Invalid JSON literal.")
        _position += bytes.size()
        var value := Value.new(kind)
        value.boolean = boolean
        return value


    func _read_number() -> Value:
        var start: int = _position
        _take(45)
        if not _take(48):
            if not _digit(false):
                return _fail("Expected a JSON number.")
            _position += 1
            while _digit(true):
                _position += 1
        if _take(46):
            if not _digit(true):
                return _fail("A decimal point must be followed by digits.")
            while _digit(true):
                _position += 1
        if _take(101) or _take(69):
            if not _take(43):
                _take(45)
            if not _digit(true):
                return _fail("An exponent must be followed by digits.")
            while _digit(true):
                _position += 1
        var result := Value.new("number")
        result.number_text = _source.slice(start, _position).get_string_from_ascii()
        return result


    func _digit(allow_zero: bool) -> bool:
        return _position < _source.size() and _source[_position] >= (48 if allow_zero else 49) and _source[_position] <= 57


    func _take(code: int) -> bool:
        if _position < _source.size() and _source[_position] == code:
            _position += 1
            return true
        return false


    func _fail(message: String) -> Value:
        if _error.is_empty():
            _error = message
        return null
