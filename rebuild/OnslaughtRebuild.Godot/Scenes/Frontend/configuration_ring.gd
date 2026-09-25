# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/quit_confirm_surface.gd"
## DrawBriefingStage's measured FE_select_level_bracket02 annulus. Preserve
## size/texture-dimension division before the centered helper multiplies back.
## Its red tint above 1 is the retained measured gain, not a clamped UI color.
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var source_anchor: Vector2 = Vector2(267, 221):
	set(value): source_anchor = value; queue_redraw()
@export var source_size: Vector2 = Vector2(990, 990):
	set(value): source_size = value; queue_redraw()


func drawing_rect() -> Rect2:
	if texture == null or texture.get_width() <= 0 or texture.get_height() <= 0: return Rect2()
	var scale_x: float = F.value(source_size.x / texture.get_width())
	var scale_y: float = F.value(source_size.y / texture.get_height())
	var width: float = F.value(texture.get_width() * scale_x)
	var height: float = F.value(texture.get_height() * scale_y)
	return Rect2(F.value(source_anchor.x - F.value(width * 0.5)),
		F.value(source_anchor.y - F.value(height * 0.5)), width, height)


func _validate_property(property: Dictionary) -> void:
	if property.name == "rectangle": property.usage = PROPERTY_USAGE_NONE
