# SPDX-License-Identifier: GPL-3.0-or-later
extends Control
## Exercises the production font's actual draw call in an isolated SubViewport.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
var _font: AtlasFont
var _units: PackedInt32Array
var _origin: Vector2
var _tint: Color
var _shadow: bool
var _scale: Vector2

func configure(font: AtlasFont, units: PackedInt32Array, origin: Vector2, tint: Color, shadow: bool, glyph_scale: Vector2) -> void:
	_font = font
	_units = units
	_origin = origin
	_tint = tint
	_shadow = shadow
	_scale = glyph_scale
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(0, 0, 640, 96), Color(0.09, 0.09, 0.19))
	if _font != null:
		_font.draw_run(self, _units, _origin, _tint, _shadow, _scale)
