# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## One native letterbox transform for all three production HUD layers.
const F32 = preload("res://Scenes/Shared/retail_float32.gd")
var _surface: Control


func _ready() -> void:
	_surface = get_parent() as Control
	if _surface == null:
		push_error("The HUD design stage requires its authored parent Control.")
		return
	_surface.resized.connect(_fit)
	_fit()


func _fit() -> void:
	if _surface == null or _surface.size.x <= 0.0 or _surface.size.y <= 0.0:
		return
	var factor: float = minf(F32.value(_surface.size.x / 640.0), F32.value(_surface.size.y / 480.0))
	scale = Vector2(factor, factor)
	position = Vector2(
		F32.value(F32.value(_surface.size.x - F32.value(640.0 * factor)) * 0.5),
		F32.value(F32.value(_surface.size.y - F32.value(480.0 * factor)) * 0.5))
