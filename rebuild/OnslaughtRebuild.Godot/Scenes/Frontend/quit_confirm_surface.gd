# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## An authored draw pass in the retained Quit.Dialog coordinate frame.
## Keeping this source transform separate from the canvas transform preserves
## the old renderer's operation grouping at fractional viewport scales.
@export var source_rect: Rect2 = Rect2(110, 170, 420, 160):
	set(value): source_rect = value; queue_redraw()
@export var rectangle: Rect2 = Rect2(120, 170, 400, 140):
	set(value): rectangle = value; queue_redraw()
@export var ink_color: Color = Color.WHITE:
	set(value): ink_color = value; queue_redraw()
@export var texture: Texture2D:
	set(value):
		if texture != null and texture.changed.is_connected(queue_redraw): texture.changed.disconnect(queue_redraw)
		texture = value
		if texture != null: texture.changed.connect(queue_redraw)
		queue_redraw()


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	resized.connect(queue_redraw)


func source_transform() -> Transform2D:
	var ratio: Vector2 = size / source_rect.size
	return Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio)


func drawing_rect() -> Rect2:
	return rectangle


func draws_content() -> bool:
	return true


func _draw() -> void:
	if not draws_content() or source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0: return
	draw_set_transform_matrix(source_transform())
	if texture == null:
		draw_rect(drawing_rect(), ink_color)
	else:
		draw_texture_rect(texture, drawing_rect(), false, ink_color)
