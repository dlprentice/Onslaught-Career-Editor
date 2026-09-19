# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pinned HFLD byte admission and the deterministic Level100Terrain.cs sampler.
## The caller supplies existing prepared bytes; this owner has no filesystem,
## environment, node, clock or physics dependency. Worlds 110/200/300 retain
## their existing admission pins without introducing a route or session owner.
## Steam fixed lookup 0x0047eb80 and AirGuide integer lookup 0x0047ea20 are
## distinct laws. In particular, AirGuide's X edge shifts Y by EIGHT bits.

const Float32 = preload("res://Core/retail_float24.gd")
const SOURCE_SHA256: String = "7A4C7C5B9400E2C8D2325CECB5C44701CD8A6E6F8609CBC8BC31D449C0620F5D"
const WORLD110_SOURCE_SHA256: String = "FD4D076A2926FBC473B7D364703BDBC0C8A0F7A638B0AB71B6F319374DA033C2"
const WORLD200_SOURCE_SHA256: String = "1B8EB8584BE552383F10B08C75D9F10E91708343F0E5EE085D5130D369F6B945"
const WORLD300_SOURCE_SHA256: String = "68A181F9EC3099A0BE52BF4A063350A35E43C20664F2E07572BDB44D472ACB1A"
const FIXED_POINT_UNITS_PER_RETAIL_UNIT: int = 256
const MAP_EXTENT_RETAIL_UNITS: int = 512
const PLAYER_START_RETAIL_X_FIXED: int = 73904
const PLAYER_START_RETAIL_Y_FIXED: int = 62272
const PLAYER_START_REFERENCE_ELEVATION_MILLIMETERS: int = -10000
const WALKER_CENTER_OF_GRAVITY_MILLIMETERS: int = 1900
const WATER_ELEVATION_MILLIMETERS: int = -1160
const MINIMUM_RELATIVE_X_MILLIMETERS: int = -288688
const MAXIMUM_RELATIVE_X_MILLIMETERS: int = 223313
const MINIMUM_RELATIVE_Z_MILLIMETERS: int = -243250
const MAXIMUM_RELATIVE_Z_MILLIMETERS: int = 268750
const _HFLD_PAYLOAD_SIZE: int = 668652
const _CHFD_PAYLOAD_SIZE: int = 5084
const _HFDT_PAYLOAD_SIZE: int = 663552
const _CHFD_PAYLOAD: int = 16
const _HFDT_HEADER: int = _CHFD_PAYLOAD + _CHFD_PAYLOAD_SIZE
const _HFDT_PAYLOAD: int = _HFDT_HEADER + 8
const _MAXIMUM_FIXED_COORDINATE: int = 131072


## A successful owner is created only after length, fixed provenance, envelope
## and metadata admission. There is deliberately no caller-supplied hash pin.
static func from_bytes(source: Variant, world_id: Variant = 100) -> Dictionary:
	if not source is PackedByteArray:
		return _failure("ArgumentException", "source must be PackedByteArray.", "source")
	if typeof(world_id) != TYPE_INT or world_id not in [100, 110, 200, 300]:
		return _failure("ArgumentOutOfRangeException", "Only already-admitted worlds 100, 110, 200 and 300 are available.", "world_id")
	var pin: String = {100: SOURCE_SHA256, 110: WORLD110_SOURCE_SHA256,
		200: WORLD200_SOURCE_SHA256, 300: WORLD300_SOURCE_SHA256}[world_id]
	if source.size() != _HFLD_PAYLOAD_SIZE + 8:
		return _failure("InvalidDataException", "The retained heightfield has an unexpected length.")
	var hash := HashingContext.new()
	if hash.start(HashingContext.HASH_SHA256) != OK or hash.update(source) != OK:
		return _failure("InvalidOperationException", "Cannot hash supplied heightfield bytes.")
	if hash.finish().hex_encode().to_upper() != pin:
		return _failure("InvalidDataException", "The retained heightfield hash does not match its provenance.")
	if source.decode_u32(0) != 0x444c4648 or source.decode_u32(4) != _HFLD_PAYLOAD_SIZE:
		return _failure("InvalidDataException", "The retained Level 100 HFLD has an unexpected envelope.")
	if source.decode_u32(8) != 0x44464843 or source.decode_u32(12) != _CHFD_PAYLOAD_SIZE:
		return _failure("InvalidDataException", "The retained Level 100 HFLD is missing CHFD metadata.")
	if source.decode_u32(_HFDT_HEADER) != 0x54444648 or source.decode_u32(_HFDT_HEADER + 4) != _HFDT_PAYLOAD_SIZE or _HFDT_PAYLOAD + _HFDT_PAYLOAD_SIZE != source.size():
		return _failure("InvalidDataException", "The retained Level 100 HFLD is missing its exact sample block.")
	var scale_bits: int = source.decode_u32(_CHFD_PAYLOAD + 0x102c)
	var scale: float = Float32.read_word(scale_bits)
	if not is_finite(scale) or scale <= 0.0:
		return _failure("InvalidDataException", "The retained Level 100 HFLD has an invalid height scale.")
	var density: float = source.decode_float(_CHFD_PAYLOAD + 0x1098)
	var water: float = source.decode_float(_CHFD_PAYLOAD + 0x1034)
	var sun_x: float = source.decode_float(_CHFD_PAYLOAD + 0x10a4)
	var sun_y: float = source.decode_float(_CHFD_PAYLOAD + 0x10a8)
	var sun_z: float = source.decode_float(_CHFD_PAYLOAD + 0x10ac)
	if not is_finite(density) or density < 0.0 or not is_finite(water) or not is_finite(sun_x) or not is_finite(sun_y) or not is_finite(sun_z) or (sun_x == 0.0 and sun_y == 0.0 and sun_z == 0.0):
		return _failure("InvalidDataException", "The retained Level 100 HFLD has invalid environment metadata.")
	var samples := PackedInt32Array()
	samples.resize(_HFDT_PAYLOAD_SIZE / 2)
	for index: int in range(samples.size()):
		samples[index] = source.decode_s16(_HFDT_PAYLOAD + index * 2)
	# Constructor's exact-scale admission follows the sample read, as in C#.
	var decoded: Dictionary = _decode_positive_float_scale(scale_bits)
	if not decoded.ok:
		return decoded
	var metadata: Dictionary = {"world_id": world_id, "payload_sha256": pin,
		"height_scale_bits": scale_bits, "mixer_set": source[_CHFD_PAYLOAD + 0x1030],
		"sky_cube": source[_CHFD_PAYLOAD + 0x1090], "detail_texture": source[_CHFD_PAYLOAD + 0x1094],
		"water_level_bits": source.decode_u32(_CHFD_PAYLOAD + 0x1034), "water_texture": source[_CHFD_PAYLOAD + 0x1095],
		"fog_color_rgb24": source.decode_u32(_CHFD_PAYLOAD + 0x1078), "fog_density_bits": source.decode_u32(_CHFD_PAYLOAD + 0x1098),
		"sun_color_rgb24": source.decode_u32(_CHFD_PAYLOAD + 0x107c), "anti_sun_color_rgb24": source.decode_u32(_CHFD_PAYLOAD + 0x1080),
		"ambient_color_rgb24": source.decode_u32(_CHFD_PAYLOAD + 0x108c),
		"sun_position_x_bits": source.decode_u32(_CHFD_PAYLOAD + 0x10a4),
		"sun_position_y_bits": source.decode_u32(_CHFD_PAYLOAD + 0x10a8),
		"sun_position_z_bits": source.decode_u32(_CHFD_PAYLOAD + 0x10ac)}
	return {"ok": true, "value": Heightfield.new(samples, metadata, decoded.significand, decoded.denominator)}


class Heightfield extends RefCounted:
	var _samples: PackedInt32Array
	var _metadata: Dictionary
	var _height_scale: float
	var _scale_significand: int
	var _scale_denominator: int

	# Internal constructor: callers use from_bytes, never fabricate decoded data.
	func _init(samples: PackedInt32Array, metadata_value: Dictionary, significand: int, denominator: int) -> void:
		_samples = samples.duplicate()
		_metadata = metadata_value.duplicate(true)
		_height_scale = Float32.read_word(int(_metadata.height_scale_bits))
		_scale_significand = significand
		_scale_denominator = denominator


	func metadata() -> Dictionary:
		return _metadata.duplicate(true)


	func sample_height_units_at_fixed(retail_x_fixed: Variant, retail_y_fixed: Variant) -> Dictionary:
		var admitted: Dictionary = _coordinates(retail_x_fixed, retail_y_fixed, "retailXFixed", "retailYFixed")
		return {"ok": true, "value": _fixed_height_units_admitted(retail_x_fixed, retail_y_fixed)} if admitted.ok else admitted


	func sample_grid_height_units(retail_x: Variant, retail_y: Variant) -> Dictionary:
		var admitted: Dictionary = _bounded_pair(retail_x, retail_y, 512, "retailX", "retailY", "Level 100 grid coordinates must be between 0 and 512.")
		return {"ok": true, "value": _grid_height_units_admitted(retail_x, retail_y)} if admitted.ok else admitted


	func sample_air_guide_height_units(retail_x: Variant, retail_y: Variant) -> Dictionary:
		var admitted: Dictionary = _coordinates(retail_x, retail_y, "retailX", "retailY")
		return {"ok": true, "value": _air_guide_height_units_admitted(retail_x, retail_y)} if admitted.ok else admitted


	func get_tile_complexity_score(tile_x: Variant, tile_y: Variant) -> Dictionary:
		var admitted: Dictionary = _bounded_pair(tile_x, tile_y, 63, "tileX", "tileY")
		return {"ok": true, "value": _tile_complexity_score_admitted(tile_x, tile_y)} if admitted.ok else admitted


	func get_retail_fixed_coordinates(relative_x: Variant, relative_z: Variant) -> Dictionary:
		var admitted: Dictionary = _coordinates(relative_x, relative_z, "relativePosition.X", "relativePosition.Z")
		if not admitted.ok:
			return admitted
		var x: int = PLAYER_START_RETAIL_X_FIXED + _floor_divide(relative_x * 256, 1000)
		if x < -2147483648 or x > 2147483647:
			return _fail("OverflowException", "Retail X coordinate exceeds Int32.")
		var y: int = PLAYER_START_RETAIL_Y_FIXED + _floor_divide(relative_z * 256, 1000)
		if y < -2147483648 or y > 2147483647:
			return _fail("OverflowException", "Retail Y coordinate exceeds Int32.")
		return {"ok": true, "value": {"x": x, "y": y}}


	func sample_ground_elevation_millimeters(relative_x: Variant, relative_z: Variant) -> Dictionary:
		var coordinates: Dictionary = get_retail_fixed_coordinates(relative_x, relative_z)
		if not coordinates.ok:
			return coordinates
		return _checked_height(_ground_elevation_at_fixed_admitted(coordinates.value.x, coordinates.value.y))


	func sample_ground_elevation_millimeters_at_fixed(retail_x_fixed: Variant, retail_y_fixed: Variant) -> Dictionary:
		var admitted: Dictionary = _coordinates(retail_x_fixed, retail_y_fixed, "retailXFixed", "retailYFixed")
		return _checked_height(_ground_elevation_at_fixed_admitted(retail_x_fixed, retail_y_fixed)) if admitted.ok else admitted


	func sample_ground_gradient_permille(relative_x: Variant, relative_z: Variant) -> Dictionary:
		var admitted: Dictionary = _coordinates(relative_x, relative_z, "relativePosition.X", "relativePosition.Z")
		if not admitted.ok:
			return admitted
		if relative_x < MINIMUM_RELATIVE_X_MILLIMETERS or relative_x > MAXIMUM_RELATIVE_X_MILLIMETERS or relative_z < MINIMUM_RELATIVE_Z_MILLIMETERS or relative_z > MAXIMUM_RELATIVE_Z_MILLIMETERS:
			return {"ok": true, "value": {"x": 0, "z": 0}}
		var left_x: int = maxi(MINIMUM_RELATIVE_X_MILLIMETERS, relative_x - 1000)
		var right_x: int = mini(MAXIMUM_RELATIVE_X_MILLIMETERS, relative_x + 1000)
		var back_z: int = maxi(MINIMUM_RELATIVE_Z_MILLIMETERS, relative_z - 1000)
		var forward_z: int = mini(MAXIMUM_RELATIVE_Z_MILLIMETERS, relative_z + 1000)
		var rise_x: int = _ground_elevation_admitted(right_x, relative_z) - _ground_elevation_admitted(left_x, relative_z)
		var rise_z: int = _ground_elevation_admitted(relative_x, forward_z) - _ground_elevation_admitted(relative_x, back_z)
		var x: Dictionary = _checked_height(_round_divide_away(rise_x * 1000, maxi(1, right_x - left_x)))
		if not x.ok:
			return x
		var z: Dictionary = _checked_height(_round_divide_away(rise_z * 1000, maxi(1, forward_z - back_z)))
		if not z.ok:
			return z
		return {"ok": true, "value": {"x": x.value, "z": z.value}}


	## Detached x-major arrays. These batch owners reuse the same kernels as
	## scalar calls, avoiding per-cell Dictionary allocation for mesh consumers.
	func grid_height_units() -> PackedInt32Array:
		var values := PackedInt32Array()
		values.resize(513 * 513)
		for x: int in range(513):
			for y: int in range(513):
				values[x * 513 + y] = _grid_height_units_admitted(x, y)
		return values


	func fixed_height_units_grid(fraction_x: Variant = 0, fraction_y: Variant = 0) -> Dictionary:
		var admitted: Dictionary = _bounded_pair(fraction_x, fraction_y, 255, "fraction_x", "fraction_y")
		if not admitted.ok:
			return admitted
		var values := PackedInt32Array()
		values.resize(512 * 512)
		for x: int in range(512):
			for y: int in range(512):
				values[x * 512 + y] = _fixed_height_units_admitted(x * 256 + fraction_x, y * 256 + fraction_y)
		return {"ok": true, "value": values}


	func tile_complexity_scores() -> PackedFloat32Array:
		var values := PackedFloat32Array()
		values.resize(64 * 64)
		for x: int in range(64):
			for y: int in range(64):
				values[x * 64 + y] = _tile_complexity_score_admitted(x, y)
		return values


	## Allocation-free deterministic kernels. Preconditions: this owner came
	## from successful pinned admission; coordinates are C# Int32 values. Grid
	## and tile kernels additionally require their checked API's bounds. Host
	## inputs must pass the checked API before a caller reuses these kernels.
	func _fixed_height_units_admitted(retail_x_fixed: int, retail_y_fixed: int) -> int:
		if retail_x_fixed < 0 or retail_x_fixed >= _MAXIMUM_FIXED_COORDINATE or retail_y_fixed < 0 or retail_y_fixed >= _MAXIMUM_FIXED_COORDINATE:
			return 0
		var tile_x: int = (retail_x_fixed >> 11) & 63
		var tile_y: int = (retail_y_fixed >> 11) & 63
		var local_x: int = (retail_x_fixed >> 8) & 7
		var local_y: int = (retail_y_fixed >> 8) & 7
		var index: int = ((tile_x * 64 + tile_y) * 81) + local_y * 9 + local_x
		var fraction_x: int = retail_x_fixed & 255
		var fraction_y: int = retail_y_fixed & 255
		var near_left: int = _samples[index]
		var near: int = near_left + (((_samples[index + 1] - near_left) * fraction_x) >> 8)
		var far_left: int = _samples[index + 9]
		var far: int = far_left + (((_samples[index + 10] - far_left) * fraction_x) >> 8)
		return near + (((far - near) * fraction_y) >> 8)


	func _grid_height_units_admitted(retail_x: int, retail_y: int) -> int:
		var tile_x: int = mini(retail_x / 8, 63)
		var tile_y: int = mini(retail_y / 8, 63)
		var local_x: int = 8 if retail_x == 512 else retail_x % 8
		var local_y: int = 8 if retail_y == 512 else retail_y % 8
		return _tile_sample(tile_x, tile_y, local_x, local_y)


	func _air_guide_height_units_admitted(retail_x: int, retail_y: int) -> int:
		var x_mask: int = retail_x & 0x3ffe00
		var y_mask: int = retail_y & 0x3ffe00
		var index: int
		if (x_mask | y_mask) == 0:
			index = 81 * (64 * ((retail_x >> 3) & 63) + ((retail_y >> 3) & 63)) + 9 * (retail_y & 7) + (retail_x & 7)
		elif x_mask == 512 and y_mask == 512:
			index = 331775
		elif x_mask == 512:
			index = 326600 + 81 * ((retail_y >> 8) & 63) + 9 * (retail_y & 7)
		elif y_mask == 512:
			index = 5175 + 5184 * ((retail_x >> 3) & 63) + (retail_x & 7)
		else:
			return 0
		return _samples[index]


	func _tile_complexity_score_admitted(tile_x: int, tile_y: int) -> float:
		var greatest_average: int = 0
		for step: int in [2, 4, 8]:
			var half_step: int = step >> 1
			var cell_count: int = 8 / step
			var error_sum: int = 0
			for local_y: int in range(0, 8, step):
				for local_x: int in range(0, 8, step):
					var top_left: int = _tile_sample(tile_x, tile_y, local_x, local_y)
					# C# integer division truncates toward zero even for odd negative
					# midpoint sums; arithmetic right shift is NOT interchangeable.
					error_sum += absi((top_left + _tile_sample(tile_x, tile_y, local_x + step, local_y + step)) / 2 - _tile_sample(tile_x, tile_y, local_x + half_step, local_y + half_step))
					error_sum += absi((top_left + _tile_sample(tile_x, tile_y, local_x + step, local_y)) / 2 - _tile_sample(tile_x, tile_y, local_x + half_step, local_y))
					error_sum += absi((top_left + _tile_sample(tile_x, tile_y, local_x, local_y + step)) / 2 - _tile_sample(tile_x, tile_y, local_x, local_y + half_step))
				error_sum += absi((_tile_sample(tile_x, tile_y, 8, local_y) + _tile_sample(tile_x, tile_y, 8, local_y + step)) / 2 - _tile_sample(tile_x, tile_y, 8, local_y + half_step))
			for local_x: int in range(0, 8, step):
				error_sum += absi((_tile_sample(tile_x, tile_y, local_x, 8) + _tile_sample(tile_x, tile_y, local_x + step, 8)) / 2 - _tile_sample(tile_x, tile_y, local_x + half_step, 8))
			var average: int = error_sum / ((cell_count * 3 + 2) * cell_count)
			greatest_average = maxi(greatest_average, average)
		var scaled: float = Float32.store_float32(_height_scale * Float32.store_float32(float(greatest_average)))
		return Float32.store_float32(scaled * 128.0)


	func _ground_elevation_at_fixed_admitted(retail_x_fixed: int, retail_y_fixed: int) -> int:
		var units: int = _fixed_height_units_admitted(retail_x_fixed, retail_y_fixed)
		var numerator: int = PLAYER_START_REFERENCE_ELEVATION_MILLIMETERS * _scale_denominator - units * _scale_significand * 1000
		return _round_divide_away(numerator, _scale_denominator)


	func _ground_elevation_admitted(relative_x: int, relative_z: int) -> int:
		return _ground_elevation_at_fixed_admitted(PLAYER_START_RETAIL_X_FIXED + _floor_divide(relative_x * 256, 1000), PLAYER_START_RETAIL_Y_FIXED + _floor_divide(relative_z * 256, 1000))


	func _tile_sample(tile_x: int, tile_y: int, local_x: int, local_y: int) -> int:
		return _samples[(tile_x * 64 + tile_y) * 81 + local_y * 9 + local_x]


	static func _floor_divide(value: int, denominator: int) -> int:
		var quotient: int = value / denominator
		return quotient - 1 if value % denominator < 0 else quotient


	static func _round_divide_away(value: int, denominator: int) -> int:
		if value >= 0:
			return (value + denominator / 2) / denominator
		return -((-value + denominator / 2) / denominator)


	static func _checked_height(value: int) -> Dictionary:
		return _fail("OverflowException", "Terrain result exceeds Int32.") if value < -2147483648 or value > 2147483647 else {"ok": true, "value": value}


	static func _coordinates(x: Variant, y: Variant, x_name: String, y_name: String) -> Dictionary:
		if not _is_int32(x):
			return _fail("ArgumentException", "Coordinate must be Int32.", x_name)
		if not _is_int32(y):
			return _fail("ArgumentException", "Coordinate must be Int32.", y_name)
		return {"ok": true}


	static func _bounded_pair(x: Variant, y: Variant, maximum: int, x_name: String, y_name: String, message: String = "Specified argument was out of the range of valid values.") -> Dictionary:
		if not _is_int32(x):
			return _fail("ArgumentException", "Coordinate must be Int32.", x_name)
		if x < 0 or x > maximum:
			return _fail("ArgumentOutOfRangeException", message, x_name)
		if not _is_int32(y):
			return _fail("ArgumentException", "Coordinate must be Int32.", y_name)
		if y < 0 or y > maximum:
			return _fail("ArgumentOutOfRangeException", message, y_name)
		return {"ok": true}


	static func _is_int32(value: Variant) -> bool:
		return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


	static func _fail(kind: String, message: String, parameter: String = "") -> Dictionary:
		return {"ok": false, "error_type": kind, "error": message, "parameter": parameter}


## Pure exact-scale kernel, compared with the existing private C# helper.
## This does not create a terrain or bypass byte/hash admission.
static func _decode_positive_float_scale(bits: int) -> Dictionary:
	var exponent: int = (bits >> 23) & 255
	if (bits & 0x80000000) != 0 or exponent == 0 or exponent == 255:
		return _failure("InvalidDataException", "The Level 100 height scale is not a positive normal float.")
	var binary_exponent: int = exponent - 150
	if binary_exponent > 0 or binary_exponent < -62:
		return _failure("InvalidDataException", "The Level 100 height scale is outside the exact fixed range.")
	return {"ok": true, "significand": 0x800000 | (bits & 0x7fffff), "denominator": 1 << -binary_exponent}


static func _failure(kind: String, message: String, parameter: String = "") -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message, "parameter": parameter}
