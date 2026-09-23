# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production Font13 briefing paragraph layout from WrapBriefingParagraphs at
## 51477f62. Only ASCII space separates words; empty tokens, raw UTF-16 and the
## strict >286 cutoff remain unchanged. Control Size affects drawing only.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const FALLBACK: Array[String] = [
	"Tatiana will take you through the", "basics of piloting Battle Engine",
	"Aquila. This will cover everything", "from basic movement in both",
	"Walker and Jet modes as well as", "Weapons use.", "",
	"Listen to her advice and try to", "keep Colonel Kramer happy."]
@export var atlas_font: AtlasFont:
	set(value): atlas_font = value; queue_redraw()
@export var source_rect: Rect2 = Rect2(80, 163.5, 505, 122.5):
	set(value): source_rect = value; queue_redraw()
@export var source_anchor: Vector2 = Vector2(80, 163.5):
	set(value): source_anchor = value; queue_redraw()
@export var wrap_ceiling: float = 286.0:
	set(value): wrap_ceiling = value; queue_redraw()
@export var line_pitch: float = 16.0:
	set(value): line_pitch = value; queue_redraw()
@export var paragraph_gap: float = 10.0:
	set(value): paragraph_gap = value; queue_redraw()
@export var ink_color: Color = Color(251.0 / 255.0, 221.0 / 255.0, 95.0 / 255.0):
	set(value): ink_color = value; queue_redraw()
## Deliberate enhanced text; unchecked, the admitted host/fallback data is used.
@export var override_paragraphs: bool = false:
	set(value): override_paragraphs = value; queue_redraw()
@export var paragraphs: PackedStringArray = PackedStringArray(FALLBACK):
	set(value): paragraphs = value; queue_redraw()
var _imported: Variant = null


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	resized.connect(queue_redraw)


func bind(raw_paragraphs: Array) -> void:
	_imported = raw_paragraphs.duplicate(true)
	queue_redraw()


func displayed_paragraphs() -> Array:
	if _imported != null and not override_paragraphs: return _imported.duplicate(true)
	var result: Array[PackedInt32Array] = []
	for paragraph: String in paragraphs: result.append(Text.units(paragraph).value)
	return result


func wrap_lines() -> Array[PackedInt32Array]:
	var lines: Array[PackedInt32Array] = []
	if atlas_font == null: return lines
	for paragraph: PackedInt32Array in displayed_paragraphs():
		if paragraph.is_empty():
			lines.append(PackedInt32Array())
			continue
		var current := PackedInt32Array()
		var word := PackedInt32Array()
		# Including the terminal boundary reproduces String.Split(' ') with its
		# repeated/trailing empty tokens, without a lossy native String conversion.
		for index: int in range(paragraph.size() + 1):
			if index < paragraph.size() and paragraph[index] != 32:
				word.append(paragraph[index])
				continue
			var candidate: PackedInt32Array = word.duplicate()
			if not current.is_empty():
				candidate = current.duplicate()
				candidate.append(32)
				candidate.append_array(word)
			if not current.is_empty() and atlas_font.measure(candidate, 1.0) > F.value(wrap_ceiling):
				lines.append(current.duplicate())
				current = word.duplicate()
			else:
				current = candidate
			word = PackedInt32Array()
		if not current.is_empty(): lines.append(current.duplicate())
	return lines


func layout_snapshot() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	var y: float = source_anchor.y
	for line: PackedInt32Array in wrap_lines():
		result.append({"units": line.duplicate(), "origin": Vector2(source_anchor.x, y), "draw": not line.is_empty()})
		y = F.value(y + F.value(paragraph_gap if line.is_empty() else line_pitch))
	return result


func source_transform() -> Transform2D:
	var ratio: Vector2 = size / source_rect.size
	return Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio)


func _draw() -> void:
	if atlas_font == null or source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0: return
	draw_set_transform_matrix(source_transform())
	for line: Dictionary in layout_snapshot():
		if line.draw: atlas_font.draw_run(self, line.units, line.origin, ink_color, true, Vector2.ONE)
