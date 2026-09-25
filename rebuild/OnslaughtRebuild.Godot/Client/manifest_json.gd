# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Plain values from a hash-pinned manifest: objects keep their exact keys (a
## repeated key keeps its last value), integer tokens stay Int64, every other
## number is the exactly rounded binary64 of its decimal text, strings are
## native. Godot's own JSON reader rounds some decimals differently from .NET,
## so the strict reader keeps tokens until this exact conversion. DTO property
## lookups go through field(), which matches names case-insensitively with the
## last match winning, as JsonSerializer's PropertyNameCaseInsensitive binding.

const Strict = preload("res://Core/strict_json.gd")


static func parse(bytes: PackedByteArray) -> Dictionary:
	var parsed: Dictionary = Strict.parse_bytes(bytes, false, 64)
	if not parsed.ok:
		return {"ok": false, "error_type": "JsonException", "error": parsed.error}
	return _convert(parsed.value)


static func _convert(value: Strict.Value) -> Dictionary:
	match value.kind:
		"null":
			return {"ok": true, "value": null}
		"boolean":
			return {"ok": true, "value": value.boolean}
		"string":
			var text: Dictionary = value.as_string()
			if not text.ok:
				return {"ok": false, "error_type": "JsonException", "error": text.error}
			return text
		"number":
			var integer: Dictionary = value.as_int64()
			if integer.ok:
				return integer
			var number: Dictionary = value.as_float64()
			if not number.ok:
				return {"ok": false, "error_type": "JsonException", "error": number.error}
			return number
		"array":
			var items: Array = []
			for item: Strict.Value in value.items:
				var converted: Dictionary = _convert(item)
				if not converted.ok:
					return converted
				items.append(converted.value)
			return {"ok": true, "value": items}
		"object":
			var members: Dictionary = {}
			for member: Dictionary in value.members:
				var name: Dictionary = member.name.as_string()
				if not name.ok:
					return {"ok": false, "error_type": "JsonException", "error": name.error}
				var converted: Dictionary = _convert(member.value)
				if not converted.ok:
					return converted
				# A repeated key keeps its first position and last value, like the
				# Dictionary indexer JsonSerializer writes through.
				members[String(name.value)] = converted.value
			return {"ok": true, "value": members}
	return {"ok": false, "error_type": "JsonException", "error": "Unknown JSON value kind."}


## A DTO property: the last key equal to name ignoring ASCII case, or fallback.
static func field(source: Variant, name: String, fallback: Variant = null) -> Variant:
	if not source is Dictionary:
		return fallback
	var found: Variant = fallback
	var wanted: String = name.to_lower()
	for key: String in source:
		if key.to_lower() == wanted:
			found = source[key]
	return found


static func sha256_hex(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode().to_upper()
