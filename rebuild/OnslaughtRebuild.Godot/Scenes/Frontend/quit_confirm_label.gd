# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Centered production atlas label with an explicit enhanced-text override.
## Glyph widths, raw UTF-16, and per-glyph shadow/body order remain shared with
## the rest of the frontend. The change signal keeps its highlight frozen-editable.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
signal content_changed
@export var atlas_font: AtlasFont:
	set(value): atlas_font = value; _refresh()
@export_multiline var text: String = "":
	set(value): text = value; _refresh()
@export var override_text: bool = false:
	set(value): override_text = value; _refresh()
@export var source_rect: Rect2 = Rect2(110, 170, 420, 160):
	set(value): source_rect = value; _refresh()
@export var source_anchor: Vector2 = Vector2(320, 178):
	set(value): source_anchor = value; _refresh()
@export var ink_color: Color = Color.WHITE:
	set(value): ink_color = value; queue_redraw()
@export var shadow: bool = true:
	set(value): shadow = value; queue_redraw()
var _imported: Variant = null


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	resized.connect(queue_redraw)


func bind(value: Variant, font: AtlasFont) -> void:
	_imported = AtlasFont.units(value).duplicate()
	atlas_font = font
	_refresh()


func displayed_units() -> PackedInt32Array:
	return AtlasFont.units(text) if override_text or _imported == null else _imported.duplicate()


func font_width() -> float:
	return atlas_font.measure(displayed_units()) if atlas_font != null else 0.0


func drawing_origin() -> Vector2:
	return Vector2(F.value(source_anchor.x - F.value(font_width() * 0.5)), source_anchor.y)


func source_transform() -> Transform2D:
	var ratio: Vector2 = size / source_rect.size
	return Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio)


func _refresh() -> void:
	queue_redraw()
	content_changed.emit()


func _draw() -> void:
	if atlas_font == null or source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0: return
	draw_set_transform_matrix(source_transform())
	atlas_font.draw_run(self, displayed_units(), drawing_origin(), ink_color, shadow)
