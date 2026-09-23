# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends TextureRect
## Authored texture/geometry and ink remain editable. The calculated display
## tint is transient, so saving a reveal frame cannot become its next baseline.
const F = preload("res://Scenes/Shared/retail_float32.gd")
signal canvas_transform_changed
@export var ink_color: Color = Color.WHITE:
	set(value):
		ink_color = value
		_refresh()
var _fade: float = 1.0
var _replacement: Variant = null


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	_refresh()


func _notification(what: int) -> void:
	if what == NOTIFICATION_TRANSFORM_CHANGED:
		canvas_transform_changed.emit()


func set_fade(fade: float, replacement: Variant = null) -> void:
	_fade = F.value(fade)
	_replacement = replacement
	_refresh()


func _refresh() -> void:
	var tint: Color = _replacement if _replacement is Color else ink_color
	self_modulate = Color(tint, F.value(tint.a * _fade))


func _validate_property(property: Dictionary) -> void:
	if property.name == "self_modulate":
		property.usage = (property.usage & ~PROPERTY_USAGE_STORAGE) | PROPERTY_USAGE_EDITOR | PROPERTY_USAGE_READ_ONLY
