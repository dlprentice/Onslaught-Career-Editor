# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## A single visible decoration pass with real authored image bounds, texture,
## tint and source anchor. Binary32 rectangle/rotation math precedes the canvas
## transform exactly as in the retained DrawCenteredRotated operation.
## The passes share the original decoration canvas frame. Tight per-image
## Control bounds regroup floating-point transforms and change fractional-scale
## pixels; source_anchor/source_size locate the art inside these shared bounds.
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var texture: Texture2D:
	set(value):
		if texture != null and texture.changed.is_connected(queue_redraw):
			texture.changed.disconnect(queue_redraw)
		texture = value
		if texture != null: texture.changed.connect(queue_redraw)
		queue_redraw()
@export var source_rect: Rect2 = Rect2(120, 240, 440, 210):
	set(value): source_rect = value; queue_redraw()
@export var source_anchor: Vector2 = Vector2(219, 344):
	set(value): source_anchor = value; queue_redraw()
@export var source_size: Vector2 = Vector2(256, 256):
	set(value): source_size = value; queue_redraw()
@export var ink_color: Color = Color.WHITE:
	set(value): ink_color = value; queue_redraw()
var _scale: float = 1.25
var _rotation: float = 0.0
var _alpha: float = 1.0
var _motion_offset: Vector2 = Vector2.ZERO


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	resized.connect(queue_redraw)


func set_motion(image_scale: float, image_rotation: float, alpha: float, offset: Vector2) -> void:
	_scale = F.value(image_scale)
	_rotation = F.value(image_rotation)
	_alpha = F.value(alpha)
	_motion_offset = offset
	queue_redraw()


func drawing_rect() -> Rect2:
	var dimensions: Vector2 = source_size * _scale
	return Rect2(-dimensions * 0.5, dimensions)


func drawing_transform() -> Transform2D:
	var ratio: Vector2 = size / source_rect.size
	var authored := Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio)
	# Godot's native Vector2.from_angle invokes its Single sin/cos overload.
	# The retained C# four-argument Transform2D constructor adds zero skew to
	# the second-column argument, which matters for the sign of zero.
	var first: Vector2 = Vector2.from_angle(_rotation)
	var second: Vector2 = Vector2.from_angle(F.value(_rotation + 0.0))
	# Read the current authored anchor: an Inspector edit must redraw even when
	# the editor's frozen display facts never supply another motion batch.
	var offset: Vector2 = _motion_offset
	return authored * Transform2D(first, Vector2(-second.y, second.x), source_anchor + offset)


func _draw() -> void:
	if texture == null or _alpha <= 0.0 or source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0:
		return
	draw_set_transform_matrix(drawing_transform())
	draw_texture_rect(texture, drawing_rect(), false, Color(ink_color, F.value(ink_color.a * _alpha)))
