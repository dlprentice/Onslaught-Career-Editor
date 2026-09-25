# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/quit_confirm_surface.gd"
## The measured static FE_Rock_Background pass from DrawBriefingStage.
## Its (-70,-80), scale 1.25 fit remains distinct from each Control's editable
## section frame; both editor and gameplay submit this same production quad.
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var source_anchor: Vector2 = Vector2(-70, -80):
	set(value): source_anchor = value; queue_redraw()
@export var texture_scale: Vector2 = Vector2(1.25, 1.25):
	set(value): texture_scale = value; queue_redraw()


func drawing_rect() -> Rect2:
	if texture == null: return Rect2()
	return Rect2(source_anchor, Vector2(F.value(texture.get_width() * texture_scale.x),
		F.value(texture.get_height() * texture_scale.y)))


func _validate_property(property: Dictionary) -> void:
	if property.name == "rectangle": property.usage = PROPERTY_USAGE_NONE
