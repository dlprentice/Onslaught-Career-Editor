# SPDX-License-Identifier: GPL-3.0-or-later
@tool
class_name RetailBitmapFontResource
extends RefCounted

const F32 = preload("res://Scenes/Shared/retail_float32.gd")
const FIRST_GLYPH: int = 32
const GLYPH_COLUMNS: int = 16
const GLYPH_COUNT: int = 96

var _atlas: Texture2D
var _cell_size: int
var _widths: PackedInt32Array

func _init(atlas: Texture2D, cell_size: int) -> void:
    _atlas = atlas
    _cell_size = cell_size
    _widths = _measure_glyph_widths(atlas.get_image(), cell_size)

func measure(text: String) -> float:
    return measure_units(_utf16_units(text))

func measure_units(characters: PackedInt32Array) -> float:
    var width: int = 0
    for code: int in characters:
        width += _widths[_glyph(code)] + 1
    return float(maxi(0, width - 1))

func draw_centered(surface: Control, text: String, center_x: float, y: float, color: Color, shadow: bool) -> void:
    draw_units_centered(surface, _utf16_units(text), center_x, y, color, shadow)

func draw_units_centered(surface: Control, characters: PackedInt32Array, center_x: float, y: float, color: Color, shadow: bool) -> void:
    var x: float = center_x - measure_units(characters) * 0.5
    for code: int in characters:
        var glyph: int = _glyph(code)
        var width: int = _widths[glyph]
        if shadow:
            _draw_glyph(surface, glyph, x + 1.0, y + 1.0, width, Color.BLACK)
        _draw_glyph(surface, glyph, x, y, width, color)
        x += float(width + 1)

static func _utf16_units(text: String) -> PackedInt32Array:
    # C# iterated UTF-16 chars, so an unsupported surrogate pair is two fallback
    # glyphs. Godot's String carrier cannot preserve embedded NUL at the C#
    # boundary (8898c2b3d core/string/ustring.cpp, append_utf16). Raw code units
    # keep that information when a caller owns binary text; live menu labels
    # continue to use native String and this same measurement/drawing path.
    var encoded: PackedByteArray = text.to_utf16_buffer()
    var units := PackedInt32Array()
    units.resize(encoded.size() / 2)
    for index: int in range(units.size()):
        units[index] = encoded.decode_u16(index * 2)
    return units

static func _glyph(code: int) -> int:
    return code - FIRST_GLYPH if code >= FIRST_GLYPH and code < FIRST_GLYPH + GLYPH_COUNT else 63 - FIRST_GLYPH

func _draw_glyph(surface: Control, glyph: int, x: float, y: float, width: int, color: Color) -> void:
    var source := Rect2((glyph % GLYPH_COLUMNS) * _cell_size, (glyph / GLYPH_COLUMNS) * _cell_size, width, _cell_size)
    surface.draw_texture_rect_region(_atlas, Rect2(x, y, width, _cell_size), source, color)

static func _measure_glyph_widths(image: Image, cell_size: int) -> PackedInt32Array:
    var widths := PackedInt32Array()
    widths.resize(GLYPH_COUNT)
    widths[0] = cell_size / 2
    var alpha_cutoff: float = F32.value(16.0 / 255.0)
    for glyph: int in range(1, GLYPH_COUNT):
        var cell_x: int = (glyph % GLYPH_COLUMNS) * cell_size
        var cell_y: int = (glyph / GLYPH_COLUMNS) * cell_size
        var rightmost: int = cell_x
        for x: int in range(cell_x + cell_size - 2, cell_x - 1, -1):
            var occupied: bool = false
            for y: int in range(cell_y, cell_y + cell_size - 1):
                if image.get_pixel(x, y).a > alpha_cutoff:
                    occupied = true
                    break
            if occupied:
                rightmost = x
                break
        widths[glyph] = rightmost - cell_x + 2
    return widths
