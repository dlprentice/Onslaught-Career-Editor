# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Editor-visible image control for the source DrawSurfaceCentered operation.
## The rectangle is formed in binary32 before the containing canvas transform.
## Scaling a parent Node2D combines those operations in another order and
## changes filtered pixels at fractional viewport scales. Size, position,
## center, texture and CanvasItem tint remain ordinary authored properties.
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var texture: Texture2D:
	set(value):
		texture = value
		queue_redraw()
@export var centered: bool = true:
	set(value):
		centered = value
		queue_redraw()
@export var center: Vector2 = Vector2.ZERO:
	set(value):
		center = value
		queue_redraw()
var _center_delta: Vector2 = Vector2.ZERO
var _image_scale: float = 1.0
var _ink: Color = Color.WHITE


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	resized.connect(queue_redraw)


func set_motion(center_delta: Vector2, image_scale: float, ink: Color = Color.WHITE) -> void:
	_center_delta = center_delta
	_image_scale = image_scale
	_ink = ink
	queue_redraw()


func drawing_rect() -> Rect2:
	var width: float = F.value(size.x * _image_scale)
	var height: float = F.value(size.y * _image_scale)
	var x: float = F.value(center.x + _center_delta.x)
	var y: float = F.value(center.y + _center_delta.y)
	if centered:
		return Rect2(F.value(x - F.value(width * 0.5)), F.value(y - F.value(height * 0.5)), width, height)
	return Rect2(x, y, width, height)


func _draw() -> void:
	if texture != null:
		draw_texture_rect(texture, drawing_rect(), false, _ink)
