# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## The selector is one genuine image control, submitted before every text row.
## Its width follows the imported label's ink+31, independent of text overrides.
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var texture: Texture2D:
	set(value):
		if texture != null and texture.changed.is_connected(queue_redraw):
			texture.changed.disconnect(queue_redraw)
		texture = value
		if texture != null: texture.changed.connect(queue_redraw)
		queue_redraw()
@export var source_rect: Rect2 = Rect2(99, 288, 240, 152):
	set(value): source_rect = value; queue_redraw()
@export var ink_color: Color = Color(0.0, 0.0, 0.0, 0.49411764705882355):
	set(value): ink_color = value; queue_redraw()
var _rectangle: Rect2 = Rect2(160.5, 288, 117, 32)
var _alpha: float = 1.0


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	resized.connect(queue_redraw)


func set_selection(rectangle: Rect2, alpha: float) -> void:
	_rectangle = rectangle
	_alpha = F.value(alpha)
	queue_redraw()


func drawing_rect() -> Rect2:
	return _rectangle


func _draw() -> void:
	if texture == null or _alpha <= 0.0 or source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0:
		return
	var ratio: Vector2 = size / source_rect.size
	draw_set_transform_matrix(Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio))
	draw_texture_rect(texture, _rectangle, false, Color(ink_color, F.value(ink_color.a * _alpha)))
