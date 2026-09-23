# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/quit_confirm_surface.gd"
## FrontEnd.cpp:891-892 center plus the already measured DevSelect scale 1.4.
## The retained 2026-07-26 alpha-mask fit corrects this page's earlier 1.39/336
## fit; it does not identify the still-missing header endcaps or Forseti emblem.
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var source_anchor: Vector2 = Vector2(328, 343):
	set(value): source_anchor = value; queue_redraw()
@export var texture_scale: Vector2 = Vector2(1.4, 1.4):
	set(value): texture_scale = value; queue_redraw()
@export var shadow_scale_boost: float = 1.0:
	set(value): shadow_scale_boost = value; queue_redraw()


func drawing_rect() -> Rect2:
	if texture == null: return Rect2()
	var sx: float = F.value(texture_scale.x * F.value(shadow_scale_boost))
	var sy: float = F.value(texture_scale.y * F.value(shadow_scale_boost))
	var width: float = F.value(texture.get_width() * sx)
	var height: float = F.value(texture.get_height() * sy)
	return Rect2(F.value(source_anchor.x - F.value(width * 0.5)),
		F.value(source_anchor.y - F.value(height * 0.5)), width, height)


func _validate_property(property: Dictionary) -> void:
	if property.name == "rectangle": property.usage = PROPERTY_USAGE_NONE
