# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Production type-on panel model, ported from Level100MessagePlaybackState.cs.
## The 25-column/three-line/40-character law is the existing measured model;
## see that file and rebuild/PROVENANCE.md for its bounded retail evidence.
## Columns and reveal cursors count UTF-16 units, as the C# owner did. Raw units
## retain NULs and split surrogate pairs without lossy Godot String conversion.

const Text = preload("res://Core/canonical_json_string.gd")
const WRAP_COLUMNS: int = 25
const VISIBLE_LINES: int = 3
const LINE_HEIGHT_PIXELS: float = 15.0
const TEXT_PEN_LEFT: float = 206.0
const FIRST_LINE_PEN_TOP: float = 413.0
const CHARACTERS_PER_SECOND: float = 40.0
const PANEL_BODY_LEFT: float = 186.5
const PANEL_BODY_TOP: float = 405.5
const PANEL_BODY_RIGHT: float = 496.5
const PANEL_BODY_BOTTOM: float = 464.5


## {ok,value:Array[{text:PackedInt32Array,source_length:int}]}
static func wrap(text: Variant) -> Dictionary:
	if text == null:
		return _failure("ArgumentNullException", "text", "A message string is required.")
	var admitted: Dictionary = Text.units(text)
	if not admitted.ok:
		return admitted
	var raw: PackedInt32Array = admitted.value
	var normalized := PackedInt32Array()
	var index: int = 0
	while index < raw.size():
		var unit: int = raw[index]
		index += 1
		if unit == 13:
			if index < raw.size() and raw[index] == 10:
				index += 1
			unit = 10
		normalized.append(unit)
	var paragraphs: Array[PackedInt32Array] = []
	var start: int = 0
	for position: int in range(normalized.size()):
		if normalized[position] == 10:
			paragraphs.append(normalized.slice(start, position))
			start = position + 1
	paragraphs.append(normalized.slice(start))
	var lines: Array[Dictionary] = []
	for paragraph_index: int in range(paragraphs.size()):
		var paragraph: PackedInt32Array = paragraphs[paragraph_index]
		var terminator: int = 1 if paragraph_index < paragraphs.size() - 1 else 0
		var current := PackedInt32Array()
		var pending_separator: int = 0
		var position: int = 0
		while position < paragraph.size():
			var separator_start: int = position
			while position < paragraph.size() and Text.is_white_space(paragraph[position]):
				position += 1
			var separator: PackedInt32Array = paragraph.slice(separator_start, position)
			var word_start: int = position
			while position < paragraph.size() and not Text.is_white_space(paragraph[position]):
				position += 1
			if word_start == position:
				pending_separator = _i32(pending_separator + separator.size())
				break
			var word: PackedInt32Array = paragraph.slice(word_start, position)
			if current.is_empty():
				pending_separator = _i32(pending_separator + separator.size())
			elif _i32(current.size() + separator.size() + word.size()) <= WRAP_COLUMNS:
				current.append_array(separator)
				current.append_array(word)
				continue
			else:
				# Preserve the old wrap's handling of an earlier leading separator;
				# changing its accounting would move subsequent reveal boundaries.
				lines.append({"text": current, "source_length": _i32(current.size() + separator.size())})
				current = PackedInt32Array()
				pending_separator = 0
			var remaining: PackedInt32Array = word
			while remaining.size() > WRAP_COLUMNS:
				lines.append({"text": remaining.slice(0, WRAP_COLUMNS),
					"source_length": _i32(WRAP_COLUMNS + pending_separator)})
				pending_separator = 0
				remaining = remaining.slice(WRAP_COLUMNS)
			current = remaining
		if not current.is_empty():
			lines.append({"text": current, "source_length": _i32(current.size() + pending_separator + terminator)})
		elif paragraph.is_empty() or pending_separator > 0:
			lines.append({"text": PackedInt32Array(), "source_length": _i32(pending_separator + terminator)})
	return _ok(lines)


static func source_length(lines: Variant) -> Dictionary:
	var admitted: Dictionary = _line_list(lines)
	if not admitted.ok:
		return admitted
	var total: int = 0
	for line: Variant in lines:
		var length: Dictionary = _source_length(line)
		if not length.ok:
			return length
		total = _i32(total + int(length.value))
	return _ok(total)


static func revealed_characters(elapsed_seconds: Variant) -> Dictionary:
	if typeof(elapsed_seconds) not in [TYPE_FLOAT, TYPE_INT]:
		return _failure("ArgumentException", "elapsed_seconds", "Elapsed time must be a number.")
	var seconds: float = float(elapsed_seconds)
	if is_nan(seconds) or seconds <= 0.0:
		return _ok(0)
	var revealed: float = seconds * CHARACTERS_PER_SECOND
	return _ok(2147483647 if revealed >= 2147483647.0 else int(revealed))


## {ok,value:Array[PackedInt32Array|null]} in top-to-bottom draw order. This never
## converts a partially revealed surrogate pair into a replacement character.
static func window(lines: Variant, revealed_characters: Variant) -> Dictionary:
	var admitted: Dictionary = _line_list(lines)
	if not admitted.ok:
		return admitted
	if not _int32(revealed_characters):
		return _failure("ArgumentException", "revealed_characters", "Reveal cursor must be an exact Int32.")
	var visible: Array = []
	if lines.is_empty():
		return _ok(visible)
	var cursor: int = maxi(revealed_characters, 0)
	var active_line: int = lines.size() - 1
	var text: Dictionary = _line_text(lines[active_line])
	if not text.ok:
		return text
	var revealed_in_line: int = text.value.size()
	var consumed: int = 0
	for index: int in range(lines.size()):
		var length: Dictionary = _source_length(lines[index])
		if not length.ok:
			return length
		var next: int = _i32(consumed + int(length.value))
		if cursor < next or index == lines.size() - 1:
			active_line = index
			text = _line_text(lines[index])
			if not text.ok:
				return text
			revealed_in_line = clampi(_i32(cursor - consumed), 0, text.value.size())
			break
		consumed = next
	var first: int = maxi(0, active_line - VISIBLE_LINES + 1)
	for index: int in range(first, active_line):
		text = _line_text(lines[index], true)
		if not text.ok:
			return text
		visible.append(text.value)
	text = _line_text(lines[active_line])
	if not text.ok:
		return text
	visible.append(text.value.slice(0, revealed_in_line))
	return _ok(visible)


static func _line_list(lines: Variant) -> Dictionary:
	if lines == null:
		return _failure("ArgumentNullException", "lines", "A line list is required.")
	if typeof(lines) != TYPE_ARRAY:
		return _failure("ArgumentException", "lines", "A line list must be an Array.")
	return _ok(null)


static func _source_length(line: Variant) -> Dictionary:
	if typeof(line) != TYPE_DICTIONARY or not _int32(line.get("source_length")):
		return _failure("ArgumentException", "lines", "A line source_length must be an exact Int32.")
	return _ok(line.source_length)


static func _line_text(line: Variant, allow_null: bool = false) -> Dictionary:
	if typeof(line) != TYPE_DICTIONARY or not line.has("text"):
		return _failure("ArgumentException", "lines", "A line text field is required.")
	if line.text == null:
		if allow_null:
			return _ok(null)
		return _failure("NullReferenceException", "", "A line's null text has no length.")
	return Text.units(line.text)


static func _int32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


static func _i32(value: int) -> int:
	return ((value + 2147483648) & 0xffffffff) - 2147483648


static func _ok(value: Variant) -> Dictionary:
	return {"ok": true, "value": value}


static func _failure(kind: String, parameter: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "parameter": parameter, "error": message}
