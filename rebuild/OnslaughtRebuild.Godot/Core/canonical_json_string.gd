# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## String-only System.Text.Json default-encoder compatibility. The command tape
## owns field ordering/indentation; this helper emits one quoted ASCII token.
## Behavior reference: dotnet/runtime v8.0.0 DefaultJavaScriptEncoder and
## AllowedBmpCodePointsBitmap (System.Text.Encodings.Web); the C# oracle checks
## exact bytes, including replacement of unpaired UTF-16 during serialization.

const Strict = preload("res://Core/strict_json.gd")
const SHORT_ESCAPES: Dictionary = {8: "b", 9: "t", 10: "n", 12: "f", 13: "r", 92: "\\"}
const HTML_AND_JS_ESCAPES: Array[int] = [34, 38, 39, 43, 60, 62, 96]


## Raw units preserve embedded NUL, which Godot's native String conversion does
## not. A null remains null for nullable C# string fields, never an empty name.
static func units(value: Variant) -> Dictionary:
	if value == null:
		return {"ok": true, "value": null}
	var result := PackedInt32Array()
	if typeof(value) == TYPE_STRING:
		var text: String = value
		for index: int in range(text.length()):
			var code: int = text.unicode_at(index)
			if code > 0xffff:
				code -= 0x10000
				result.append(0xd800 + (code >> 10))
				result.append(0xdc00 + (code & 0x3ff))
			else:
				result.append(code)
	elif typeof(value) == TYPE_PACKED_INT32_ARRAY:
		for code: int in value:
			if code < 0 or code > 0xffff:
				return _failure("UTF-16 units must be unsigned 16-bit integers.")
		result = value.duplicate()
	else:
		return _failure("A string field requires String, PackedInt32Array UTF-16 units, or null.")
	return {"ok": true, "value": result}


static func quote(value: Variant) -> Dictionary:
	var admitted: Dictionary = units(value)
	if not admitted.ok:
		return admitted
	if admitted.value == null:
		return {"ok": true, "value": "null"}
	var raw: PackedInt32Array = admitted.value
	var output: String = '"'
	var index: int = 0
	while index < raw.size():
		var code: int = raw[index]
		index += 1
		if code >= 0xd800 and code <= 0xdbff:
			if index < raw.size() and raw[index] >= 0xdc00 and raw[index] <= 0xdfff:
				output += "\\u%04X\\u%04X" % [code, raw[index]]
				index += 1
				continue
			code = 0xfffd
		elif code >= 0xdc00 and code <= 0xdfff:
			code = 0xfffd
		if SHORT_ESCAPES.has(code):
			output += "\\" + String(SHORT_ESCAPES[code])
		elif code >= 32 and code <= 126 and not HTML_AND_JS_ESCAPES.has(code):
			output += String.chr(code)
		else:
			output += "\\u%04X" % code
	return {"ok": true, "value": output + '"'}


static func utf8_bytes(value: Variant, replace_unpaired: bool = false) -> Dictionary:
	var admitted: Dictionary = units(value)
	if not admitted.ok:
		return admitted
	if admitted.value == null:
		return _failure("A null field has no UTF-8 string bytes.")
	var text := Strict.Value.new("string")
	text.string_units = admitted.value
	if replace_unpaired:
		# Encoding.UTF8's default replacement fallback is used by BinaryWriter.
		# JSON admission keeps the strict default and never repairs an input.
		var index: int = 0
		while index < text.string_units.size():
			var unit: int = text.string_units[index]
			if unit >= 0xd800 and unit <= 0xdbff:
				if index + 1 < text.string_units.size() and text.string_units[index + 1] >= 0xdc00 \
						and text.string_units[index + 1] <= 0xdfff:
					index += 2
					continue
				text.string_units[index] = 0xfffd
			elif unit >= 0xdc00 and unit <= 0xdfff:
				text.string_units[index] = 0xfffd
			index += 1
	return text.utf8_bytes()


static func native_string(value: Variant) -> Dictionary:
	var admitted: Dictionary = units(value)
	if not admitted.ok:
		return admitted
	if admitted.value == null:
		return {"ok": true, "value": null}
	var text := Strict.Value.new("string")
	text.string_units = admitted.value
	return text.as_string()


static func is_white_space(unit: int) -> bool:
	# Char.IsWhiteSpace's UTF-16 set, rather than Godot strip_edges()'s set.
	return (unit >= 9 and unit <= 13) or (unit >= 0x2000 and unit <= 0x200a) \
		or unit in [32, 0x85, 0xa0, 0x1680, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000]


static func is_null_or_white_space(value: Variant) -> bool:
	if value == null:
		return true
	for unit: int in value:
		if not is_white_space(unit):
			return false
	return true


static func equals_text(value: Variant, text: String) -> bool:
	return value != null and value == units(text).value


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException", "error_code": "argument", "error": message,
		"parameter": "", "inner_parameter": ""}
