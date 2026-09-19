# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## The frontend's production atlas law, extracted from RetailFrontendFlow.
## This is deliberately distinct from pause's 96-slot font and shadow origin.
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Text = preload("res://Core/canonical_json_string.gd")

@export var page: Texture2D
@export var cell_size: Vector2i = Vector2i(16, 16)
@export var columns: int = 16
@export var system_font: bool = false
var _widths: PackedInt32Array
var _measured_page: Texture2D
var _measured_cell: Vector2i
var _measured_columns: int


func ensure_loaded() -> Dictionary:
	if page == null:
		return {"ok": false, "error": "Frontend font has no atlas recipe."}
	if page.has_method("ensure_loaded"):
		var admitted: Dictionary = page.call("ensure_loaded")
		if not admitted.ok:
			return admitted
	if cell_size.x <= 1 or cell_size.y <= 1 or columns <= 0:
		return {"ok": false, "error": "Frontend font cell geometry is invalid."}
	if _measured_page != page or _measured_cell != cell_size or _measured_columns != columns:
		_widths = measure_widths(page.get_image(), cell_size.x, columns)
		_measured_page = page
		_measured_cell = cell_size
		_measured_columns = columns
	return {"ok": true}


func glyph_widths() -> PackedInt32Array:
	if not ensure_loaded().ok:
		return PackedInt32Array()
	return _widths.duplicate()


func measure(value: Variant, scale_x: float = 1.0) -> float:
	var characters: PackedInt32Array = units(value)
	if system_font:
		return F.value(characters.size() * cell_size.x)
	if not ensure_loaded().ok:
		return 0.0
	scale_x = F.value(scale_x)
	var width: float = 0.0
	for code: int in characters:
		width = F.value(width + F.value(F.value(_widths[glyph_index(code)] + 1) * scale_x))
	return maxf(0.0, F.value(width - scale_x))


func draw_run(surface: CanvasItem, value: Variant, origin: Vector2, tint: Color,
		shadow: bool = true, glyph_scale: Vector2 = Vector2.ONE) -> void:
	if not ensure_loaded().ok:
		return
	var x: float = origin.x
	for code: int in units(value):
		var glyph: int = (code - 32 if code >= 32 and code <= 126 else 31) if system_font else glyph_index(code)
		var width: int = cell_size.x if system_font else _widths[glyph]
		var source := Rect2((glyph % columns) * cell_size.x, (glyph / columns) * cell_size.y, width, cell_size.y)
		var dest := Rect2(x, origin.y, F.value(width * glyph_scale.x), F.value(cell_size.y * glyph_scale.y))
		if shadow and not system_font:
			# Shadow is on the anchor, body at anchor-(1,1), with equal alpha.
			surface.draw_texture_rect_region(page, dest, source, Color(0.0, 0.0, 0.0, tint.a))
			surface.draw_texture_rect_region(page, Rect2(dest.position - Vector2.ONE, dest.size), source, tint)
		else:
			surface.draw_texture_rect_region(page, dest, source, tint)
		x = F.value(x + F.value(dest.size.x + (0.0 if system_font else glyph_scale.x)))


static func units(value: Variant) -> PackedInt32Array:
	if value is PackedInt32Array:
		return value
	var result: Dictionary = Text.units(value)
	return result.value if result.ok and result.value != null else PackedInt32Array()


static func glyph_index(code: int) -> int:
	return code - 32 if code >= 32 and code < 288 else 31


static func measure_widths(image: Image, cell: int, column_count: int) -> PackedInt32Array:
	var widths := PackedInt32Array()
	widths.resize(256)
	widths[0] = cell / 2
	var threshold: float = F.value(16.0 / 255.0)
	for glyph: int in range(1, 256):
		var cell_x: int = (glyph % column_count) * cell
		var cell_y: int = (glyph / column_count) * cell
		if cell_y + cell > image.get_height():
			break
		var rightmost: int = cell_x
		for x: int in range(cell_x + cell - 2, cell_x - 1, -1):
			var occupied: bool = false
			for y: int in range(cell_y, cell_y + cell - 1):
				if image.get_pixel(x, y).a > threshold:
					occupied = true
					break
			if occupied:
				rightmost = x
				break
		widths[glyph] = rightmost - cell_x + 2
	return widths
