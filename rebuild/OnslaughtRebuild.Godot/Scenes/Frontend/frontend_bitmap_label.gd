# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## A real authored Control for the frontend atlas, including raw UTF-16 labels.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Laws = preload("res://Client/options_laws.gd")
enum Alignment { LEFT, CENTRE, INTEGER_CENTRE, RIGHT, FLOOR_CENTRE }
@export var atlas_font: AtlasFont:
	set(value):
		atlas_font = value
		queue_redraw()
@export var text: String = "":
	set(value):
		text = value
		queue_redraw()
## Deliberate enhanced text; faithful imported labels otherwise remain authoritative.
@export var override_text: bool = false:
	set(value):
		override_text = value
		queue_redraw()
@export var alignment: Alignment = Alignment.LEFT
@export var ink_color: Color = Color.WHITE
@export var shadow: bool = true
@export var body_origin: bool = true
## An authored draw origin is useful when source glyph coordinates must be
## formed before the canvas transform, rather than translated per node.
@export var content_origin: Vector2 = Vector2.ZERO:
	set(value):
		content_origin = value
		queue_redraw()
var _imported: Variant
var _font: AtlasFont
var _tint: Color = Color.WHITE
var _offset: Vector2 = Vector2.ZERO


func bind(value: Variant, font: AtlasFont) -> void:
	_imported = AtlasFont.units(value).duplicate()
	_font = font
	queue_redraw()


func set_tint(tint: Color) -> void:
	_tint = tint
	queue_redraw()


func set_content_offset(offset: Vector2) -> void:
	_offset = offset
	queue_redraw()


func displayed_units() -> PackedInt32Array:
	return AtlasFont.units(text) if override_text or _imported == null else _imported.duplicate()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		queue_redraw()


func _draw() -> void:
	var font: AtlasFont = _font if _font != null else atlas_font
	if font == null:
		return
	var value: PackedInt32Array = displayed_units()
	var width: float = font.measure(value)
	var x: float = 0.0
	match alignment:
		Alignment.CENTRE: x = F.value(F.value(size.x * 0.5) - F.value(width * 0.5))
		Alignment.INTEGER_CENTRE: x = Laws.menu_item_dest_x(F.value(size.x * 0.5), int(width))
		Alignment.RIGHT: x = Laws.dropdown_dest_x(size.x, int(width))
		Alignment.FLOOR_CENTRE: x = floor(F.value(F.value(size.x * 0.5) - F.value(width * 0.5)))
	var origin := Vector2(x, 0.0) + _offset
	if content_origin != Vector2.ZERO:
		origin += content_origin
	if body_origin and shadow:
		origin += Vector2.ONE
	font.draw_run(self, value, origin, ink_color * _tint, shadow)
