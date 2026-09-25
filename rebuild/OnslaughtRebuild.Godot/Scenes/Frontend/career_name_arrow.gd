# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/quit_confirm_surface.gd"
## The original FE_Arrow crop and signed draw rectangle; no input owner.
const Target = preload("res://Scenes/Frontend/career_name_target.gd")
@export var region: Rect2 = Rect2(16, 12, 30, 40):
	set(value): region = value; queue_redraw()
@export var hit_rect: Rect2 = Rect2(0, 430, 46, 48)


func contains_design_point(point: Vector2, page: CanvasItem) -> bool:
	return Target.contains(self, source_rect, hit_rect, point, page)


func _draw() -> void:
	if texture == null or source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0: return
	draw_set_transform_matrix(source_transform())
	draw_texture_rect_region(texture, rectangle, region, ink_color)
