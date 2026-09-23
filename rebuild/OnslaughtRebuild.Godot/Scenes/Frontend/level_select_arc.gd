# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/quit_confirm_surface.gd"
## Measured sweep reconstruction from DrawLevelSweepArcs at 51477f62.
## The retail sprite remains unidentified; the retained alpha-blended line
## does not claim to reproduce the capture's additive composite.
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var source_center: Vector2 = Vector2(365.84, 320.38):
	set(value): source_center = value; queue_redraw()
@export var radius: float = 249.28:
	set(value): radius = value; queue_redraw()
@export var start_angle: float = 2.5423:
	set(value): start_angle = value; queue_redraw()
@export var end_angle: float = 3.7253:
	set(value): end_angle = value; queue_redraw()
@export var point_count: int = 96:
	set(value): point_count = value; queue_redraw()
@export var stroke_width: float = 1.6:
	set(value): stroke_width = value; queue_redraw()
@export var antialiased: bool = true:
	set(value): antialiased = value; queue_redraw()


func drawing_parameters() -> Dictionary:
	return {"center": source_center, "radius": F.value(radius), "start": F.value(start_angle),
		"end": F.value(end_angle), "points": point_count, "ink": ink_color,
		"width": F.value(stroke_width), "antialiased": antialiased}


func _draw() -> void:
	if source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0 or point_count < 2: return
	var parameters: Dictionary = drawing_parameters()
	draw_set_transform_matrix(source_transform())
	draw_arc(parameters.center, parameters.radius, parameters.start, parameters.end,
		parameters.points, parameters.ink, parameters.width, parameters.antialiased)


func _validate_property(property: Dictionary) -> void:
	if property.name in ["rectangle", "texture"]: property.usage = PROPERTY_USAGE_NONE
