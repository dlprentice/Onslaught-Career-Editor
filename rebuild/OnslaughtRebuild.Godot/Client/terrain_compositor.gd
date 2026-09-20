# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Exact byte-processing port of Level100TerrainCompositor.cs. Its pinned LTH1
## input is locally materialized retail data, never a public scene resource.
## This owner has no files, clock, scene, material or simulation dependencies.
## The appearance owner can call render_tile natively for a whole cache update;
## this is not an API for per-tile calls across the language boundary.
const Float32 = preload("res://Core/retail_float24.gd")
const MAP_SIZE: int = 512
const TILE_COUNT_PER_AXIS: int = 64
const TILE_COUNT: int = 4096
const TILE_WIDTH: int = 8
const ROOT_TEXTURE_LENGTH: int = 524288
const LIGHT_COLOR_BYTE_SCALE: float = 1.0 / 256.0
const HIERARCHY_SOURCE_SHA256: String = "541EACD0AA75FAE8BEFB8A3E1505EA52AE6B1F6C1367C15C65D7DD23B7CFE977"
const _MATERIAL_COUNT: int = 6
const _PALETTE_ENTRIES: int = 256
const _WEIGHTS_PER_LAYER: int = 81
const _SHADOW_BYTES_PER_TILE: int = 512
const _PINE_LEVEL_OFFSETS: Array[int] = [0, 1, 5, 21, 85, 341, 1365]
const _WORD_MASK: int = 0xffffffff

var _maps: Array[Dictionary] = []
var _cells: Array[Dictionary] = []
var _shade: PackedByteArray = []
var _shadows: Array[PackedByteArray] = []
var _pine_alpha: PackedByteArray = []
var _pines: PackedInt32Array = [] # Original descriptor order, (top_x, top_y, root_level).
var _lighting: PackedInt64Array = [] # Unsigned RGB coefficient words, 64 triples.
var _admitted: bool = false


static func from_bytes(source: Variant, sun_color_rgb24: Variant, ambient_color_rgb24: Variant) -> Dictionary:
	if source == null:
		return _failure("ArgumentNullException", "Value cannot be null.", "source")
	if typeof(source) != TYPE_PACKED_BYTE_ARRAY:
		return _failure("ArgumentException", "Hierarchy source requires an exact byte array.", "source")
	if not _is_u32(sun_color_rgb24) or not _is_u32(ambient_color_rgb24):
		return _failure("ArgumentException", "Light colours require UInt32 words.")
	# Identity precedes every structural read, including the header and length.
	var hash := HashingContext.new()
	# HashingContext rejects update(empty), whereas .NET SHA256 hashes it.
	# Finishing a newly started context gives the same empty-message digest.
	if hash.start(HashingContext.HASH_SHA256) != OK or (not source.is_empty() and hash.update(source) != OK):
		return _failure("InvalidOperationException", "Cannot hash terrain hierarchy bytes.")
	if hash.finish().hex_encode().to_upper() != HIERARCHY_SOURCE_SHA256:
		return _failure("InvalidDataException", "Level 100 terrain hierarchy does not match its retail-derived identity.")
	var decoded: Dictionary = _decode_hierarchy(source)
	if not decoded.ok:
		return decoded
	var owner: RefCounted = new()
	owner._maps = decoded.maps
	owner._cells = decoded.cells
	owner._shade = decoded.shade
	owner._shadows = decoded.shadows
	owner._pine_alpha = decoded.pine_alpha
	owner._pines = decoded.pines
	owner._lighting = _build_lighting_gradient(sun_color_rgb24, ambient_color_rgb24)
	owner._admitted = true
	return {"ok": true, "value": owner}


## Exact terrain-only material response, not the compositor's Sun+Ambient
## gradient. Callers supply HFLD Sun and AntiSun here. The .8 and both products
## retain the C# binary32 stores; the stage's later MODULATE2X is not folded in.
static func terrain_vertex_diffuse(light0_color_rgb24: Variant, light1_color_rgb24: Variant) -> Dictionary:
	if not _is_u32(light0_color_rgb24) or not _is_u32(light1_color_rgb24):
		return _failure("ArgumentException", "Light colours require UInt32 words.")
	var result := PackedFloat32Array()
	var material_ambient: float = Float32.store_float32(0.8)
	for shift: int in [16, 8, 0]:
		var sum: int = ((light0_color_rgb24 >> shift) & 255) + ((light1_color_rgb24 >> shift) & 255)
		var scaled: float = Float32.store_float32(float(sum) * LIGHT_COLOR_BYTE_SCALE)
		result.append(minf(Float32.store_float32(material_ambient * scaled), 1.0))
	return {"ok": true, "value": result}


## Mutates only destination bytes; returns an explicit failure at the first
## failing C# array access. The admitted levels are 0..4. Invalid level values
## are refused before allocating a potentially enormous shifted block.
## Flat array indexing and partial destination writes deliberately match C#:
## an out-of-grid slot can alias a later row if its linear offsets are valid.
func render_tile(destination: Variant, level: Variant, tile_x: Variant, tile_y: Variant,
		slot_x: Variant, slot_y: Variant) -> Dictionary:
	if not _admitted:
		return _failure("InvalidOperationException", "Terrain compositor has no admitted hierarchy.")
	for coordinate: Variant in [level, tile_x, tile_y, slot_x, slot_y]:
		if not _is_i32(coordinate):
			return _failure("ArgumentException", "Compositor coordinates require Int32.")
	if level < 0 or level >= _maps.size():
		return _bounds_failure()
	# A null byte[] reaches its first write only after the tile is composited.
	# No externally visible state changes before then, so its explicit error can
	# be returned after the same source-index validation and before the writes.
	if destination != null and typeof(destination) != TYPE_PACKED_BYTE_ARRAY:
		return _failure("ArgumentException", "Destination requires an exact byte array.")
	var scale: int = 1 << level
	var block_size: int = TILE_WIDTH * scale
	var cell_index: int = _i32(_i32(tile_y * TILE_COUNT_PER_AXIS) + tile_x)
	if cell_index < 0 or cell_index >= _cells.size():
		return _bounds_failure()
	var map: Dictionary = _maps[level]
	var cell: Dictionary = _cells[cell_index]
	var shadow: PackedByteArray = _shadows[cell_index]
	var map_indices: PackedByteArray = map.indices
	var palette: PackedInt64Array = map.palette
	var map_width: int = map.width
	var material_stride: int = map_width * map_width
	var materials: PackedByteArray = cell.material_ids
	var weights: PackedByteArray = cell.weights
	var block := PackedInt32Array()
	block.resize(block_size * block_size)
	for control_y: int in range(TILE_WIDTH):
		var shade_y: int = _i32(_i32(tile_y * TILE_WIDTH) + control_y)
		for control_x: int in range(TILE_WIDTH):
			var shade_x: int = _i32(_i32(tile_x * TILE_WIDTH) + control_x)
			var right_x: int = mini(_i32(shade_x + 1), MAP_SIZE - 1)
			var bottom_y: int = mini(_i32(shade_y + 1), MAP_SIZE - 1)
			var shade_positions: Array[int] = [_i32(_i32(shade_y * MAP_SIZE) + shade_x),
				_i32(_i32(shade_y * MAP_SIZE) + right_x), _i32(_i32(bottom_y * MAP_SIZE) + shade_x),
				_i32(_i32(bottom_y * MAP_SIZE) + right_x)]
			for position: int in shade_positions:
				if position < 0 or position >= _shade.size(): return _bounds_failure()
			var shade_tl: int = _shade[shade_positions[0]]
			var shade_tr: int = _shade[shade_positions[1]]
			var shade_bl: int = _shade[shade_positions[2]]
			var shade_br: int = _shade[shade_positions[3]]
			var shade_horizontal: int = ((shade_tr - shade_tl) << 8) >> level
			var shade_vertical: int = ((shade_bl - shade_tl) << 8) >> level
			var shade_cross: int = (((shade_br - shade_bl) - (shade_tr - shade_tl)) << 8) >> (level * 2)
			# The coefficients do not depend on the subpixel. Hoisting preserves
			# each source-ordered Int32 operation, including wrapping before SAR.
			var coefficients := PackedInt32Array()
			for layer: int in range(materials.size()):
				var offset: int = layer * _WEIGHTS_PER_LAYER + control_y * 9 + control_x
				var tl: int = _sbyte(weights[offset])
				var tr: int = _sbyte(weights[offset + 1])
				var bl: int = _sbyte(weights[offset + 9])
				var br: int = _sbyte(weights[offset + 10])
				coefficients.append(_i32(tl << 24))
				coefficients.append(_i32((tr - tl) << 24) >> level)
				coefficients.append(_i32((bl - tl) << 24) >> level)
				coefficients.append(_i32(((br - bl) - (tr - tl)) << 24) >> (level * 2))
			for sub_y: int in range(scale):
				var pixel_y: int = control_y * scale + sub_y
				# Released lighting advances both slopes BEFORE its first texel.
				# Material weights below instead start at the unadvanced corner.
				var shade_row: int = (shade_tl << 8) + (sub_y + 1) * shade_vertical
				var shade_step: int = shade_horizontal + (sub_y + 1) * shade_cross
				for sub_x: int in range(scale):
					var pixel_x: int = control_x * scale + sub_x
					var source_x: int = (tile_x & 1) * block_size + pixel_x
					var source_y: int = (tile_y & 1) * block_size + pixel_y
					var source_texel: int = source_y * map_width + source_x
					var color: int = palette[map_indices[source_texel]]
					for layer: int in range(materials.size()):
						var offset: int = layer * 4
						var weight: int = _i32(coefficients[offset] + sub_y * coefficients[offset + 2] +
							sub_x * (coefficients[offset + 1] + sub_y * coefficients[offset + 3]))
						var material: int = materials[layer]
						var candidate: int = (palette[material * _PALETTE_ENTRIES +
							map_indices[material * material_stride + source_texel]] + (weight & 0xff000000)) & _WORD_MASK
						color = _blend_material(color, candidate)
					var shade_value: int = clampi((shade_row + (sub_x + 1) * shade_step) >> 8, 0, 63)
					if not shadow.is_empty():
						@warning_ignore("integer_division")
						var shadow_x: int = pixel_x * 8 / scale
						@warning_ignore("integer_division")
						var shadow_y: int = pixel_y * 8 / scale
						var shadow_bit: int = shadow_y * 64 + shadow_x
						if (shadow[shadow_bit >> 3] & (1 << (shadow_bit & 7))) != 0:
							shade_value >>= 1
					var light: int = shade_value * 3
					var red: int = color & 255
					var green: int = (color >> 8) & 255
					var blue: int = (color >> 16) & 255
					block[pixel_y * block_size + pixel_x] = (((green * _lighting[light + 1] & 0x07e00000) +
						(blue * _lighting[light + 2] & 0x001f0000) + (red * _lighting[light] & 0xf8000000)) >> 16) & 0xffff
	_apply_pine_shadows(block, block_size, level, tile_x, tile_y)
	if destination == null:
		return _failure("NullReferenceException", "Object reference not set to an instance of an object.")
	var destination_x: int = _i32(slot_x * block_size)
	var destination_y: int = _i32(slot_y * block_size)
	for pixel_y: int in range(block_size):
		var offset: int = _i32(_i32(_i32(_i32(destination_y + pixel_y) * MAP_SIZE) + destination_x) * 2)
		for pixel_x: int in range(block_size):
			var value: int = block[pixel_y * block_size + pixel_x]
			if offset < 0 or offset >= destination.size(): return _bounds_failure()
			destination[offset] = value & 255
			offset = _i32(offset + 1)
			if offset < 0 or offset >= destination.size(): return _bounds_failure()
			destination[offset] = value >> 8
			offset = _i32(offset + 1)
	return {"ok": true}


func _apply_pine_shadows(block: PackedInt32Array, block_size: int, logical_level: int, tile_x: int, tile_y: int) -> void:
	var scale: int = 1 << logical_level
	var origin_x: int = _i32(tile_x * TILE_WIDTH * scale)
	var origin_y: int = _i32(tile_y * TILE_WIDTH * scale)
	for descriptor: int in range(_pines.size() - 3, -1, -3):
		var alpha_level: int = _pines[descriptor + 2] + logical_level
		var dimension: int = 1 << alpha_level
		var local_x: int = _i32(_pines[descriptor] * scale - origin_x)
		var local_y: int = _i32(_pines[descriptor + 1] * scale - origin_y)
		if local_x >= block_size or local_y >= block_size or _i32(local_x + dimension) <= 0 or _i32(local_y + dimension) <= 0:
			continue
		var alpha_offset: int = _PINE_LEVEL_OFFSETS[alpha_level]
		for source_y: int in range(dimension):
			var target_y: int = _i32(local_y + source_y)
			if target_y < 0 or target_y >= block_size: continue
			for source_x: int in range(dimension):
				var target_x: int = _i32(local_x + source_x)
				if target_x < 0 or target_x >= block_size: continue
				var amount: int = _pine_alpha[alpha_offset + source_y * dimension + source_x]
				if amount >= 32: continue
				var target: int = target_y * block_size + target_x
				block[target] = _shade_pine_pixel(block[target], amount)


static func _shade_pine_pixel(destination: int, amount: int) -> int:
	var pair: int = ((destination << 16) | destination) & 0x07e0f81f
	var scaled: int = (((pair * amount) & _WORD_MASK) >> 5) & 0x07e0f81f
	return ((scaled >> 16) + scaled) & 0xffff


static func _blend_material(color: int, candidate: int) -> int:
	var difference: int = _i32(candidate - color)
	if difference > 0x1fffffff: return candidate
	if difference < 0: return color
	var blend: int = difference >> 26
	var combined: int = (((color & 0x00f8f8ff) * (7 - blend)) + ((candidate & 0x00f8f8ff) * blend)) & _WORD_MASK
	return ((combined >> 3) + (candidate & 0xff000000)) & _WORD_MASK


static func _build_lighting_gradient(sun_color: int, ambient_color: int) -> PackedInt64Array:
	@warning_ignore("integer_division")
	var red_base: int = (((ambient_color >> 16) & 255) << 8) / (((sun_color >> 16) & 0xfe) + 1)
	@warning_ignore("integer_division")
	var green_base: int = (ambient_color & 0xff00) / (((sun_color >> 8) & 0xfe) + 1)
	@warning_ignore("integer_division")
	var blue_base: int = ((ambient_color & 255) << 8) / ((sun_color & 0xfe) + 1)
	var red: int = red_base << 8
	var green: int = green_base << 8
	var blue: int = blue_base << 8
	var result := PackedInt64Array()
	for index: int in range(64):
		# Math.Min receives signed Int32 products, not arbitrary precision ints.
		result.append(mini(_i32(_i32((red >> 8) << 16) * 2), 0x00f80000) & 0x00f80000)
		result.append(mini(_i32(_i32((green >> 8) << 11) * 2), 0x0007e000) & 0x0007e000)
		result.append(mini(_i32((blue >> 3 & -32) * 2), 0x00001f00) & 0x00001f00)
		red = _i32(red + (255 - red_base) * 4)
		green = _i32(green + (255 - green_base) * 4)
		blue = _i32(blue + (255 - blue_base) * 4)
	return result


## Internal decoding is separated solely to keep byte admission readable. It
## never produces a renderable owner; from_bytes always checks the full pin.
static func _decode_hierarchy(source: PackedByteArray) -> Dictionary:
	var reader := HierarchyReader.new(source)
	if reader.exact(4) != "LTH1".to_ascii_buffer() or reader.u32() != 1 or reader.u32() != 5:
		return reader.invalid("Level 100 terrain hierarchy has an invalid header.")
	var maps: Array[Dictionary] = []
	for level: int in range(5):
		var width: int = reader.i32()
		var expected_width: int = 16 << level
		var data_length: int = reader.i32()
		if width != expected_width or data_length != _MATERIAL_COUNT * width * width:
			return reader.invalid("Level 100 MAPT level %d has invalid dimensions." % level)
		var indices: PackedByteArray = reader.exact(data_length)
		var palette_length: int = reader.i32()
		if palette_length != _MATERIAL_COUNT * _PALETTE_ENTRIES:
			return reader.invalid("Level 100 MAPT level %d has an invalid palette." % level)
		var palette := PackedInt64Array()
		for index: int in range(palette_length): palette.append(reader.u32())
		maps.append({"width": width, "indices": indices, "palette": palette})
	if reader.i32() != TILE_COUNT:
		return reader.invalid("Level 100 terrain hierarchy has an invalid cell count.")
	var cells: Array[Dictionary] = []
	for index: int in range(TILE_COUNT):
		var layer_count: int = reader.u8()
		if layer_count < 1 or layer_count > 5:
			return reader.invalid("Level 100 terrain cell %d has an invalid layer count." % index)
		var materials: PackedByteArray = reader.exact(layer_count)
		for material: int in materials:
			if material >= _MATERIAL_COUNT:
				return reader.invalid("Level 100 terrain cell %d has an invalid material." % index)
		cells.append({"material_ids": materials, "weights": reader.exact(layer_count * _WEIGHTS_PER_LAYER)})
	if reader.i32() != MAP_SIZE * MAP_SIZE:
		return reader.invalid("Level 100 terrain hierarchy has an invalid shade map.")
	var shade: PackedByteArray = reader.exact(MAP_SIZE * MAP_SIZE)
	for value: int in shade:
		if value > 63: return reader.invalid("Level 100 terrain hierarchy has an invalid shade value.")
	var shadow_count: int = reader.i32()
	if shadow_count != 211:
		return reader.invalid("Level 100 terrain hierarchy has an invalid shadow count.")
	var shadows: Array[PackedByteArray] = []
	shadows.resize(TILE_COUNT)
	for index: int in range(shadow_count):
		var tile_index: int = reader.u16()
		if tile_index >= TILE_COUNT or not shadows[tile_index].is_empty():
			return reader.invalid("Level 100 terrain hierarchy has an invalid shadow tile.")
		shadows[tile_index] = reader.exact(_SHADOW_BYTES_PER_TILE)
	if reader.i32() != 5461:
		return reader.invalid("Level 100 terrain hierarchy has invalid pine alpha.")
	var pine_alpha: PackedByteArray = reader.exact(5461)
	var pine_count: int = reader.i32()
	if pine_count != 1481:
		return reader.invalid("Level 100 terrain hierarchy has an invalid pine count.")
	var pines := PackedInt32Array()
	for index: int in range(pine_count):
		var top_x: int = reader.i16()
		var top_y: int = reader.i16()
		var root_level: int = reader.u8()
		if root_level < 1 or root_level > 2:
			return reader.invalid("Level 100 pine shadow %d has an invalid level." % index)
		pines.append_array(PackedInt32Array([top_x, top_y, root_level]))
	if not reader.error.is_empty(): return reader.error
	if reader.position != source.size():
		return reader.invalid("Level 100 terrain hierarchy has trailing data.")
	return {"ok": true, "maps": maps, "cells": cells, "shade": shade, "shadows": shadows,
		"pine_alpha": pine_alpha, "pines": pines}


class HierarchyReader extends RefCounted:
	var bytes: PackedByteArray
	var position: int = 0
	var error: Dictionary = {}

	func _init(source: PackedByteArray) -> void:
		bytes = source

	func exact(count: int) -> PackedByteArray:
		if not error.is_empty(): return PackedByteArray()
		if count < 0 or count > bytes.size() - position:
			error = {"ok": false, "error_type": "InvalidDataException", "error": "Level 100 terrain hierarchy is truncated."}
			return PackedByteArray()
		var result: PackedByteArray = bytes.slice(position, position + count)
		position += count
		return result

	func _width(count: int) -> bool:
		if not error.is_empty(): return false
		if count > bytes.size() - position:
			error = {"ok": false, "error_type": "EndOfStreamException", "error": "Unable to read beyond the end of the stream."}
			return false
		return true

	func u8() -> int:
		if not _width(1): return 0
		var result: int = bytes[position]
		position += 1
		return result

	func u16() -> int:
		if not _width(2): return 0
		var result: int = bytes.decode_u16(position)
		position += 2
		return result

	func i16() -> int:
		if not _width(2): return 0
		var result: int = bytes.decode_s16(position)
		position += 2
		return result

	func u32() -> int:
		if not _width(4): return 0
		var result: int = bytes.decode_u32(position)
		position += 4
		return result

	func i32() -> int:
		if not _width(4): return 0
		var result: int = bytes.decode_s32(position)
		position += 4
		return result

	func invalid(message: String) -> Dictionary:
		return error if not error.is_empty() else {"ok": false, "error_type": "InvalidDataException", "error": message}


static func _sbyte(value: int) -> int:
	return value if value < 128 else value - 256


static func _i32(value: int) -> int:
	return (value + 0x80000000 & _WORD_MASK) - 0x80000000


static func _is_i32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -0x80000000 and value <= 0x7fffffff


static func _is_u32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= 0 and value <= _WORD_MASK


static func _bounds_failure() -> Dictionary:
	return _failure("IndexOutOfRangeException", "Index was outside the bounds of the array.")


static func _failure(kind: String, message: String, parameter: String = "") -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message, "parameter": parameter}
