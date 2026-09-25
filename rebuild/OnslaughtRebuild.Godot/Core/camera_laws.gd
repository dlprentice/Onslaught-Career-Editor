# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Ports RetailCameraLaws.cs and RetailMovieCameraZoom. Camera.cpp:629–672,
## 852–858; existing pristine-image contracts 0x0041a630/0x0041b070. This keeps
## the current float-stored return contract, not an unrounded x87 return value.
## The producer of movie FOV remains outside this owner. No scene/window/input.
const Float32 = preload("res://Core/retail_float24.gd")
const INVERSE_REFERENCE_FOV_BITS: int = 0x3c360b61
const DEFAULT_ZOOM_BITS: int = 0x3f800000


static func aspect_ratio(multiplayer: Variant) -> Dictionary:
	if typeof(multiplayer) != TYPE_BOOL:
		return {"ok": false, "error_type": "ArgumentException", "error": "Multiplayer must be a Boolean."}
	return {"ok": true, "bits": 0x3f000000 if multiplayer else 0x3f400000}


class MovieZoom extends RefCounted:
	var _time_bits: int = 0xc0000000
	var _zoom_bits: int = DEFAULT_ZOOM_BITS
	var _old_zoom_bits: int = DEFAULT_ZOOM_BITS

	## Raw words preserve all float32 inputs and the cache's signed zero/NaN
	## identity. Equality is numerical float equality, never word equality.
	func get_zoom(time_bits: Variant, field_of_view_bits: Variant) -> Dictionary:
		if not _word(time_bits) or (field_of_view_bits != null and not _word(field_of_view_bits)):
			return {"ok": false, "error_type": "ArgumentException", "error": "Zoom input must be raw UInt32 float words (nullable FOV)."}
		if Float32.read_word(_time_bits) == Float32.read_word(time_bits):
			return {"ok": true, "bits": _zoom_bits}
		_old_zoom_bits = _zoom_bits
		var zoom_bits: int = DEFAULT_ZOOM_BITS
		if field_of_view_bits != null:
			# Existing C# multiplies double carriers then stores once to float;
			# do not divide by 90 or introduce a store between the products.
			zoom_bits = Float32.store_word(Float32.read_word(field_of_view_bits) \
				* Float32.read_word(INVERSE_REFERENCE_FOV_BITS) * 0.5)
		_zoom_bits = zoom_bits
		_time_bits = time_bits
		return {"ok": true, "bits": zoom_bits}

	func snapshot() -> Dictionary:
		return {"time_bits": _time_bits, "zoom_bits": _zoom_bits, "old_zoom_bits": _old_zoom_bits}

	static func _word(value: Variant) -> bool:
		return typeof(value) == TYPE_INT and value >= 0 and value <= 0xffffffff
