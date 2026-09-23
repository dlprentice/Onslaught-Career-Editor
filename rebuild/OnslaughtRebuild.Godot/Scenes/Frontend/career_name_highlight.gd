# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/quit_confirm_surface.gd"
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var highlight_padding: float = 4.0:
	set(value): highlight_padding = value; queue_redraw()
@export var top_offset: float = -2.0:
	set(value): top_offset = value; queue_redraw()
@export var row_height: float = 31.0:
	set(value): row_height = value; queue_redraw()
var _fresh: bool = true


func _ready() -> void:
	super._ready()
	get_node("../Label").connect(&"content_changed", queue_redraw)


func set_fresh(value: bool) -> void:
	_fresh = value
	queue_redraw()


func draws_content() -> bool:
	return _fresh


func drawing_rect() -> Rect2:
	var label: Control = get_node("../Label")
	var origin: Vector2 = label.drawing_origin()
	var padding: float = F.value(highlight_padding)
	return Rect2(F.value(origin.x - padding), F.value(origin.y + F.value(top_offset)),
		F.value(label.font_width() + F.value(padding * 2.0)), F.value(row_height))


func _validate_property(property: Dictionary) -> void:
	if property.name == "rectangle": property.usage = PROPERTY_USAGE_NONE
