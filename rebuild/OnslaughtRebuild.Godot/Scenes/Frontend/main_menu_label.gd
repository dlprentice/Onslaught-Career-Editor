# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/frontend_bitmap_label.gd"
## One production menu label. The native bounds scale the same authored source
## rectangle as the former C# row, including its real half-open hit rectangle.
## Font decoding, raw UTF-16, glyph measurements and shadow/body order are shared.
@export var source_rect: Rect2 = Rect2(99, 294, 240, 20):
	set(value):
		source_rect = value
		queue_redraw()
@export var source_anchor: Vector2 = Vector2(219, 296):
	set(value):
		source_anchor = value
		queue_redraw()
@export var centered: bool = true:
	set(value):
		centered = value
		queue_redraw()


func source_transform() -> Transform2D:
	var ratio: Vector2 = size / source_rect.size
	return Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio)


func drawing_origin() -> Vector2:
	var active_font: AtlasFont = _font if _font != null else atlas_font
	var width: float = active_font.measure(displayed_units()) if active_font != null else 0.0
	return Vector2(F.value(source_anchor.x - F.value(width * 0.5)), source_anchor.y) if centered else source_anchor


func _draw() -> void:
	var active_font: AtlasFont = _font if _font != null else atlas_font
	if active_font == null or source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0:
		return
	draw_set_transform_matrix(source_transform())
	active_font.draw_run(self, displayed_units(), drawing_origin(), ink_color * _tint, shadow)
