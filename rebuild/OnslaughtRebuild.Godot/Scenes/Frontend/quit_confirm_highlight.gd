# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/quit_confirm_surface.gd"
## Selected-row blank sprite is submitted immediately before its choice text.
## Its measured label width remains transient, never a serialized retail image.
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var highlight_padding: float = 4.0:
	set(value): highlight_padding = value; queue_redraw()
@export var row_height: float = 32.0:
	set(value): row_height = value; queue_redraw()
var _selected: bool = false


func _ready() -> void:
	super._ready()
	get_node("../Label").connect(&"content_changed", queue_redraw)


func set_selected(value: bool) -> void:
	_selected = value
	queue_redraw()


func is_selected() -> bool:
	return _selected


func draws_content() -> bool:
	return _selected


func drawing_rect() -> Rect2:
	var label: Control = get_node("../Label")
	var origin: Vector2 = label.drawing_origin()
	var padding: float = F.value(highlight_padding)
	return Rect2(F.value(origin.x - padding), origin.y,
		F.value(label.font_width() + F.value(padding * 2.0)), F.value(row_height))


func _validate_property(property: Dictionary) -> void:
	# Layout derives from the actual label plus the explicit padding/height.
	# The base surface's unrelated fixed rectangle is not an authoring input.
	if property.name == "rectangle": property.usage = PROPERTY_USAGE_NONE
