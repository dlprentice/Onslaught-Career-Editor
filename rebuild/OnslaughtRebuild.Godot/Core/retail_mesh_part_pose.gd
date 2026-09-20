# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Ports RetailMeshPartPose.cs, without selecting frames, refreshing caches,
## running controllers or introducing a mutable pose owner. The existing
## source/evidence pins remain authoritative; PC24 is the bounded geometry
## precision contract, not a new claim about every retail calling context.
##
## A pose is {position_float_bits:{x,y,z}, basis_float_bits:{row0_x..row2_z}}.
## Every component is a signed Int32 IEEE word. Results are detached dictionaries:
## {ok:true,value:pose}, or sphere {ok:true,value:{position:vector,displacement:vector}}.
## Failure has error_type/parameter/error and no value. Shape validation has no
## C# value-type equivalent; finite admission then follows the source read order.
## Final float stores may produce infinity. A later PC24 operation consuming an
## overflowed intermediate store is refused, exactly as the retained C# owner.
const Float24 = preload("res://Core/retail_float24.gd")
const VECTOR_KEYS: Array[String] = ["x", "y", "z"]
const BASIS_KEYS: Array[String] = ["row0_x", "row0_y", "row0_z", "row1_x", "row1_y", "row1_z", "row2_x", "row2_y", "row2_z"]
const HIERARCHY_ORDERS: Array[Array] = [[0, 2, 1], [2, 1, 0], [2, 1, 0], [1, 2, 0], [1, 0, 2], [1, 0, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2]]
const OWNER_ORDERS: Array[Array] = [[0, 1, 2], [1, 0, 2], [2, 1, 0], [0, 1, 2], [0, 1, 2], [2, 0, 1], [0, 1, 2], [0, 1, 2], [2, 0, 1]]


static func interpolate_single_frame(frame: Variant) -> Dictionary:
	if not _pose_shape(frame): return _shape_failure("frame")
	var kernel := Kernel.new()
	return kernel.finish(kernel.interpolate(frame))


static func compose_hierarchy(parent: Variant, local: Variant) -> Dictionary:
	if not _pose_shape(parent): return _shape_failure("parent")
	if not _pose_shape(local): return _shape_failure("local")
	var kernel := Kernel.new()
	return kernel.finish(kernel.compose(parent, local, false))


static func apply_owner(owner: Variant, cached: Variant) -> Dictionary:
	if not _pose_shape(owner): return _shape_failure("owner")
	if not _pose_shape(cached): return _shape_failure("cached")
	var kernel := Kernel.new()
	return kernel.finish(kernel.compose(owner, cached, true))


static func to_local_sphere_query(part: Variant, current_center: Variant, displacement: Variant) -> Dictionary:
	if not _pose_shape(part): return _shape_failure("part")
	if not _word_record(current_center, VECTOR_KEYS): return _shape_failure("current_center")
	if not _word_record(displacement, VECTOR_KEYS): return _shape_failure("displacement")
	var kernel := Kernel.new()
	return kernel.finish(kernel.sphere(part, current_center, displacement))


static func _pose_shape(value: Variant) -> bool:
	return value is Dictionary and _word_record(value.get("position_float_bits"), VECTOR_KEYS) \
		and _word_record(value.get("basis_float_bits"), BASIS_KEYS)


static func _word_record(value: Variant, keys: Array[String]) -> bool:
	if not value is Dictionary: return false
	for key: String in keys:
		var word: Variant = value.get(key)
		if not word is int or word < -0x80000000 or word > 0x7fffffff: return false
	return true


static func _shape_failure(parameter: String) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException", "parameter": parameter,
		"error": "Pose/vector records require every named component as a signed Int32 float word."}


## One transient call frame. It keeps the first numerical refusal and never
## exposes partial results. No input dictionary is retained or mutated.
class Kernel extends RefCounted:
	var _error: Dictionary = {}

	func finish(value: Dictionary) -> Dictionary:
		return {"ok": true, "value": value} if _error.is_empty() else _error.duplicate()

	func interpolate(frame: Dictionary) -> Dictionary:
		var position: Dictionary = {}
		var basis: Dictionary = {}
		for key: String in VECTOR_KEYS:
			position[key] = _store(_add(_read(frame.position_float_bits[key]), 0.0))
		for key: String in BASIS_KEYS:
			basis[key] = _store(_add(_read(frame.basis_float_bits[key]), 0.0))
		return {"position_float_bits": position, "basis_float_bits": basis}

	func compose(parent: Dictionary, local: Dictionary, owner: bool) -> Dictionary:
		var a: Array[float] = _components(parent.basis_float_bits)
		var b: Array[float] = _components(local.basis_float_bits)
		if not _error.is_empty(): return {}
		var position: Dictionary = _position(parent.position_float_bits, local.position_float_bits, a, owner)
		if not _error.is_empty(): return {}
		var basis: Dictionary = {}
		var orders: Array[Array] = OWNER_ORDERS if owner else HIERARCHY_ORDERS
		for index: int in range(9):
			@warning_ignore("integer_division")
			var row: int = index / 3
			basis[BASIS_KEYS[index]] = _product(a, b, row, index % 3, orders[index])
		return {"position_float_bits": position, "basis_float_bits": basis}

	func sphere(part: Dictionary, center: Dictionary, displacement: Dictionary) -> Dictionary:
		# Centre-minus-displacement is stored before subtracting the part. The
		# Z subtraction is stored for two columns but retained wide for column 2.
		var dx: float = _read(displacement.x)
		var dy: float = _read(displacement.y)
		var dz: float = _read(displacement.z)
		var bx: float = Float24.store_float32(_subtract(_read(center.x), dx))
		var by: float = Float24.store_float32(_subtract(_read(center.y), dy))
		var bz: float = Float24.store_float32(_subtract(_read(center.z), dz))
		var x: float = Float24.store_float32(_subtract(bx, _read(part.position_float_bits.x)))
		var y: float = Float24.store_float32(_subtract(by, _read(part.position_float_bits.y)))
		var wide_z: float = _subtract(bz, _read(part.position_float_bits.z))
		var z: float = Float24.store_float32(wide_z)
		var a: Array[float] = _components(part.basis_float_bits)
		if not _error.is_empty(): return {}
		var position: Dictionary = {"x": _transpose_dot(a, 0, x, y, z), "y": _transpose_dot(a, 1, x, y, z),
			"z": _transpose_dot(a, 2, x, y, wide_z)}
		var motion: Dictionary = {"x": _transpose_dot(a, 0, dx, dy, dz), "y": _transpose_dot(a, 1, dx, dy, dz),
			"z": _transpose_dot(a, 2, dx, dy, dz)}
		return {"position": position, "displacement": motion}

	func _position(parent: Dictionary, local: Dictionary, a: Array[float], owner: bool) -> Dictionary:
		var p: Array[float] = [_read(local.x), _read(local.y), _read(local.z)]
		var x: float = _dot(a, p, 0, [1, 0, 2] if owner else [0, 2, 1])
		var y: float = _dot(a, p, 1, [0, 1, 2] if owner else [1, 2, 0])
		var z: float = _dot(a, p, 2, [0, 1, 2])
		# These reads must not be pre-admitted with the basis: a Y store can
		# overflow before a later bad Z input would have been read by C#.
		return {"x": _store(_add(x, _read(parent.x))),
			"y": _store(_add(Float24.store_float32(y), _read(parent.y))),
			"z": _store(_add(Float24.store_float32(z), _read(parent.z)))}

	func _dot(a: Array[float], p: Array[float], row: int, order: Array) -> float:
		return _add(_add(_multiply(a[row * 3 + order[0]], p[order[0]]),
			_multiply(a[row * 3 + order[1]], p[order[1]])),
			_multiply(a[row * 3 + order[2]], p[order[2]]))

	func _product(a: Array[float], b: Array[float], row: int, column: int, order: Array) -> int:
		return _store(_add(_add(_multiply(a[row * 3 + order[0]], b[order[0] * 3 + column]),
			_multiply(a[row * 3 + order[1]], b[order[1] * 3 + column])),
			_multiply(a[row * 3 + order[2]], b[order[2] * 3 + column])))

	func _transpose_dot(a: Array[float], column: int, x: float, y: float, z: float) -> int:
		return _store(_add(_add(_multiply(z, a[6 + column]), _multiply(y, a[3 + column])), _multiply(x, a[column])))

	func _components(basis: Dictionary) -> Array[float]:
		var result: Array[float] = []
		for key: String in BASIS_KEYS: result.append(_read(basis[key]))
		return result

	func _read(word: int) -> float:
		if not _error.is_empty(): return 0.0
		if (word & 0x7f800000) == 0x7f800000:
			_error = {"ok": false, "error_type": "ArgumentOutOfRangeException", "parameter": "bits", "error": "Pose input must be finite."}
			return 0.0
		return Float24.read_word(word)

	func _round(value: float) -> float:
		if not _error.is_empty(): return 0.0
		if not is_finite(value):
			_error = {"ok": false, "error_type": "ArgumentOutOfRangeException", "parameter": "value", "error": "Retail arithmetic must remain finite."}
			return 0.0
		return Float24.round_finite(value)

	func _add(left: float, right: float) -> float: return _round(left + right)
	func _subtract(left: float, right: float) -> float: return _round(left - right)
	func _multiply(left: float, right: float) -> float: return _round(left * right)
	func _store(value: float) -> int:
		var word: int = Float24.store_word(value)
		return word if word < 0x80000000 else word - 0x100000000
