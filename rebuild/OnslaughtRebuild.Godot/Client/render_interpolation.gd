# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Current Level100RenderInterpolation.cs and projectile-trail history. Raw
## UInt32 words carry all float arguments/results; inputs are not clamped to
## finite values or alpha 0..1 because the C# owner does not impose those laws.
## Basis axes are matrix columns. Every numerical operation retains its source
## Single store and issue order; native slerp/physics do not replace this law.
const Float32 = preload("res://Core/retail_float24.gd")
const Target = preload("res://Client/target_presentation.gd")
const TELEPORT_METERS_BITS: int = 0x41200000
const AXES: Array[String] = ["x_bits", "y_bits", "z_bits"]
const BASIS_AXES: Array[String] = ["x_axis", "y_axis", "z_axis"]


static func lerp(previous: Variant, current: Variant, alpha_bits: Variant) -> Dictionary:
	var pair: Dictionary = _vector_pair(previous, current, alpha_bits)
	if not pair.ok: return pair
	return {"ok": true, "value": _lerp_vector(pair.previous, pair.current, Float32.read_word(alpha_bits))}


static func distance_squared(previous: Variant, current: Variant) -> Dictionary:
	var pair: Dictionary = _vector_pair(previous, current, 0)
	if not pair.ok: return pair
	return {"ok": true, "bits": Float32.store_word(_distance_squared(pair.previous, pair.current))}


static func interpolate_position(previous: Variant, current: Variant, alpha_bits: Variant, teleport_meters_bits: Variant = TELEPORT_METERS_BITS) -> Dictionary:
	var pair: Dictionary = _vector_pair(previous, current, alpha_bits)
	if not pair.ok: return pair
	if not Target.word(teleport_meters_bits):
		return Target.failure("ArgumentException", "Teleport distance requires a raw UInt32 float word.")
	var teleport: float = Float32.read_word(teleport_meters_bits)
	var result: Dictionary = pair.current if _distance_squared(pair.previous, pair.current) > _f32(teleport * teleport) \
		else _lerp_vector(pair.previous, pair.current, Float32.read_word(alpha_bits))
	return {"ok": true, "value": result}


static func interpolate_target(previous: Variant, current: Variant, alpha_bits: Variant) -> Dictionary:
	if not Target.word(alpha_bits):
		return Target.failure("ArgumentException", "Target alpha requires a raw UInt32 float word.")
	var admitted: Dictionary = Target.admit_descriptor(current)
	if not admitted.ok: return admitted
	var next: Dictionary = admitted.value
	if previous == null:
		return admitted
	var old: Dictionary = Target.admit_descriptor(previous)
	if not old.ok: return old
	var prior: Dictionary = old.value
	if prior.actor_id != next.actor_id or prior.definition_name != next.definition_name or prior.mesh_binding != next.mesh_binding \
			or not prior.visible or not next.visible or _distance_squared(prior.position, next.position) > 100.0:
		return admitted
	var alpha: float = Float32.read_word(alpha_bits)
	next.position = _lerp_vector(prior.position, next.position, alpha)
	next.basis = _interpolate_basis(prior.basis, next.basis, alpha)
	return {"ok": true, "value": next}


static func interpolate_projectile(previous: Variant, spawn: Variant, current: Variant, alpha_bits: Variant) -> Dictionary:
	if not Target.word(alpha_bits):
		return Target.failure("ArgumentException", "Projectile alpha requires a raw UInt32 float word.")
	var next: Dictionary = _admit_projectile(current)
	if not next.ok: return next
	# A previous fixed-step projectile makes the caller's spawn state unused.
	var prior: Dictionary = _admit_projectile(spawn if previous == null else previous)
	if not prior.ok: return prior
	var alpha: float = Float32.read_word(alpha_bits)
	var direction: Dictionary = _lerp_vector(prior.value.direction, next.value.direction, alpha)
	var zero: Dictionary = {"x_bits": 0, "y_bits": 0, "z_bits": 0}
	return {"ok": true, "value": {"position": _lerp_vector(prior.value.position, next.value.position, alpha),
		"direction": direction if _distance_squared(zero, direction) > 0.0 else next.value.direction}}


static func interpolate_basis(previous: Variant, current: Variant, alpha_bits: Variant) -> Dictionary:
	if not Target.word(alpha_bits):
		return Target.failure("ArgumentException", "Basis alpha requires a raw UInt32 float word.")
	var prior: Dictionary = Target.admit_basis(previous)
	if not prior.ok: return prior
	var next: Dictionary = Target.admit_basis(current)
	if not next.ok: return next
	return {"ok": true, "value": _interpolate_basis(prior.value, next.value, Float32.read_word(alpha_bits))}


static func _interpolate_basis(previous: Dictionary, current: Dictionary, alpha: float) -> Dictionary:
	if not _is_proper_rotation(previous) or not _is_proper_rotation(current):
		var linear: Dictionary = {}
		for axis: String in BASIS_AXES:
			linear[axis] = _lerp_vector(previous[axis], current[axis], alpha)
		return linear
	var p: Array[float] = _to_quaternion(previous)
	var c: Array[float] = _to_quaternion(current)
	var dot: float = _f32(_f32(_f32(_f32(p[0] * c[0]) + _f32(p[1] * c[1])) + _f32(p[2] * c[2])) + _f32(p[3] * c[3]))
	if dot < 0.0:
		for index: int in range(4): c[index] = -c[index]
		dot = -dot
	dot = clampf(dot, -1.0, 1.0)
	var previous_weight: float
	var current_weight: float
	if dot > _f32(0.9995):
		previous_weight = _f32(1.0 - alpha)
		current_weight = alpha
	else:
		var angle: float = _acos_clamped(dot)
		var inverse_sin: float = _f32(1.0 / _sin(angle))
		previous_weight = _f32(_sin(_f32(_f32(1.0 - alpha) * angle)) * inverse_sin)
		current_weight = _f32(_sin(_f32(alpha * angle)) * inverse_sin)
	var mixed: Array[float] = []
	for index: int in range(4):
		mixed.append(_f32(_f32(p[index] * previous_weight) + _f32(c[index] * current_weight)))
	var length: float = _f32(sqrt(_f32(_f32(_f32(_f32(mixed[0] * mixed[0]) + _f32(mixed[1] * mixed[1])) \
		+ _f32(mixed[2] * mixed[2])) + _f32(mixed[3] * mixed[3]))))
	if length <= 0.0 or not is_finite(length):
		return current.duplicate(true)
	return _from_quaternion(_f32(mixed[0] / length), _f32(mixed[1] / length), _f32(mixed[2] / length), _f32(mixed[3] / length))


static func _is_proper_rotation(basis: Dictionary) -> bool:
	var tolerance: float = _f32(0.001)
	for axis: String in BASIS_AXES:
		if not absf(_f32(_dot(basis[axis], basis[axis]) - 1.0)) <= _f32(2.0 * tolerance):
			return false
	if absf(_dot(basis.x_axis, basis.y_axis)) > tolerance or absf(_dot(basis.x_axis, basis.z_axis)) > tolerance \
			or absf(_dot(basis.y_axis, basis.z_axis)) > tolerance:
		return false
	var x: Array[float] = _floats(basis.x_axis)
	var y: Array[float] = _floats(basis.y_axis)
	var z: Array[float] = _floats(basis.z_axis)
	var first: float = _f32(x[0] * _f32(_f32(y[1] * z[2]) - _f32(z[1] * y[2])))
	var second: float = _f32(y[0] * _f32(_f32(x[1] * z[2]) - _f32(z[1] * x[2])))
	var third: float = _f32(z[0] * _f32(_f32(x[1] * y[2]) - _f32(y[1] * x[2])))
	return _f32(_f32(first - second) + third) > 0.0


static func _to_quaternion(basis: Dictionary) -> Array[float]:
	var x: Array[float] = _floats(basis.x_axis)
	var y: Array[float] = _floats(basis.y_axis)
	var z: Array[float] = _floats(basis.z_axis)
	var trace: float = _f32(_f32(x[0] + y[1]) + z[2])
	if trace > 0.0:
		var s: float = _f32(_f32(sqrt(_f32(trace + 1.0))) * 2.0)
		return [_f32(_f32(y[2] - z[1]) / s), _f32(_f32(z[0] - x[2]) / s), _f32(_f32(x[1] - y[0]) / s), _f32(0.25 * s)]
	if x[0] > y[1] and x[0] > z[2]:
		var s: float = _f32(_f32(sqrt(_f32(_f32(_f32(1.0 + x[0]) - y[1]) - z[2]))) * 2.0)
		return [_f32(0.25 * s), _f32(_f32(y[0] + x[1]) / s), _f32(_f32(z[0] + x[2]) / s), _f32(_f32(y[2] - z[1]) / s)]
	if y[1] > z[2]:
		var s: float = _f32(_f32(sqrt(_f32(_f32(_f32(1.0 + y[1]) - x[0]) - z[2]))) * 2.0)
		return [_f32(_f32(y[0] + x[1]) / s), _f32(0.25 * s), _f32(_f32(z[1] + y[2]) / s), _f32(_f32(z[0] - x[2]) / s)]
	var t: float = _f32(_f32(sqrt(_f32(_f32(_f32(1.0 + z[2]) - x[0]) - y[1]))) * 2.0)
	return [_f32(_f32(z[0] + x[2]) / t), _f32(_f32(z[1] + y[2]) / t), _f32(0.25 * t), _f32(_f32(x[1] - y[0]) / t)]


static func _from_quaternion(x: float, y: float, z: float, w: float) -> Dictionary:
	return {"x_axis": _vector(_f32(1.0 - _f32(2.0 * _f32(_f32(y * y) + _f32(z * z)))),
		_f32(2.0 * _f32(_f32(x * y) + _f32(w * z))), _f32(2.0 * _f32(_f32(x * z) - _f32(w * y)))),
		"y_axis": _vector(_f32(2.0 * _f32(_f32(x * y) - _f32(w * z))),
			_f32(1.0 - _f32(2.0 * _f32(_f32(x * x) + _f32(z * z)))), _f32(2.0 * _f32(_f32(y * z) + _f32(w * x)))),
		"z_axis": _vector(_f32(2.0 * _f32(_f32(x * z) + _f32(w * y))),
			_f32(2.0 * _f32(_f32(y * z) - _f32(w * x))), _f32(1.0 - _f32(2.0 * _f32(_f32(x * x) + _f32(y * y)))))}


static func _acos_clamped(value: float) -> float:
	# Native float acos, for an already clamped [-1,1] argument. get_angle uses
	# float acos and an exact factor two, without normalizing the quaternion.
	# API checked at Godot 8898c2b3d/core/math/quaternion.cpp:259–260; no upstream
	# implementation is imported. Halving is exact across this bounded range.
	return Quaternion(0.0, 0.0, 0.0, value).get_angle() * 0.5


static func _sin(value: float) -> float:
	return Vector2.from_angle(value).y


static func _dot(left: Dictionary, right: Dictionary) -> float:
	var l: Array[float] = _floats(left)
	var r: Array[float] = _floats(right)
	return _f32(_f32(_f32(l[0] * r[0]) + _f32(l[1] * r[1])) + _f32(l[2] * r[2]))


static func _distance_squared(previous: Dictionary, current: Dictionary) -> float:
	var p: Array[float] = _floats(previous)
	var c: Array[float] = _floats(current)
	var dx: float = _f32(c[0] - p[0])
	var dy: float = _f32(c[1] - p[1])
	var dz: float = _f32(c[2] - p[2])
	return _f32(_f32(_f32(dx * dx) + _f32(dy * dy)) + _f32(dz * dz))


static func _lerp_vector(previous: Dictionary, current: Dictionary, alpha: float) -> Dictionary:
	var result: Dictionary = {}
	for axis: String in AXES:
		var p: float = Float32.read_word(previous[axis])
		var c: float = Float32.read_word(current[axis])
		result[axis] = Float32.store_word(p + _f32(_f32(c - p) * alpha))
	return result


static func _floats(value: Dictionary) -> Array[float]:
	return [Float32.read_word(value.x_bits), Float32.read_word(value.y_bits), Float32.read_word(value.z_bits)]


static func _vector(x: float, y: float, z: float) -> Dictionary:
	return {"x_bits": Float32.store_word(x), "y_bits": Float32.store_word(y), "z_bits": Float32.store_word(z)}


static func _f32(value: float) -> float:
	return Float32.store_float32(value)


static func _vector_pair(previous: Variant, current: Variant, alpha_bits: Variant) -> Dictionary:
	if not Target.word(alpha_bits):
		return Target.failure("ArgumentException", "Interpolation alpha requires a raw UInt32 float word.")
	var p: Dictionary = Target.admit_vector(previous)
	if not p.ok: return p
	var c: Dictionary = Target.admit_vector(current)
	if not c.ok: return c
	return {"ok": true, "previous": p.value, "current": c.value}


static func _admit_projectile(value: Variant) -> Dictionary:
	if not value is Dictionary:
		return Target.failure("ArgumentException", "Projectile requires position and direction vectors.")
	var position: Dictionary = Target.admit_vector(value.get("position"))
	if not position.ok: return position
	var direction: Dictionary = Target.admit_vector(value.get("direction"))
	if not direction.ok: return direction
	return {"ok": true, "value": {"position": position.value, "direction": direction.value}}


static func uses_authored_trail(kind: Variant) -> Dictionary:
	if not _projectile_kind(kind):
		return Target.failure("ArgumentException", "Projectile kind must fit its unsigned byte storage.")
	return {"ok": true, "value": kind in [1, 2, 3]}


static func authored_point_count(kind: Variant) -> Dictionary:
	var supported: Dictionary = uses_authored_trail(kind)
	if not supported.ok: return supported
	if not supported.value:
		return Target.failure("ArgumentOutOfRangeException", "This kind has no authored trail.", "kind")
	return {"ok": true, "value": 5 if kind == 1 else 3}


static func authored_lifetime_ticks(kind: Variant) -> Dictionary:
	var supported: Dictionary = uses_authored_trail(kind)
	if not supported.ok: return supported
	if not supported.value:
		return Target.failure("ArgumentOutOfRangeException", "This kind has no authored trail.", "kind")
	# SimulationConstants: Pulse=6*20; MechBullet and MechAirBullet=1*20.
	return {"ok": true, "value": 120 if kind == 1 else 20}


static func _projectile_kind(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= 0 and value <= 255


static func create_trail_history(capacity: Variant, lifetime_ticks: Variant) -> Dictionary:
	if not Target.i32(capacity) or not Target.i32(lifetime_ticks):
		return Target.failure("ArgumentException", "Trail capacity and lifetime require Int32.")
	if capacity < 1:
		return Target.failure("ArgumentOutOfRangeException", "Trail capacity must be positive.", "capacity")
	if lifetime_ticks < 1:
		return Target.failure("ArgumentOutOfRangeException", "Trail lifetime must be positive.", "lifetimeTicks")
	return {"ok": true, "value": TrailHistory.new(capacity, lifetime_ticks)}


class TrailHistory extends RefCounted:
	var _capacity: int
	var _lifetime_ticks: int
	var _points: Array[Dictionary] = []
	var _last_remaining_ticks: Variant = null

	func _init(capacity: int, lifetime: int) -> void:
		_capacity = capacity
		_lifetime_ticks = lifetime

	func points() -> Array[Dictionary]:
		return _points.duplicate(true)

	func snapshot() -> Dictionary:
		return {"points": points(), "last_remaining_ticks": _last_remaining_ticks}

	func advance(current: Variant, velocity_per_tick: Variant, remaining_ticks: Variant) -> Dictionary:
		if not Target.i32(remaining_ticks):
			return Target.failure("ArgumentException", "Remaining ticks require exact Int32.")
		if remaining_ticks < 0 or remaining_ticks > _lifetime_ticks:
			return Target.failure("ArgumentOutOfRangeException", "Remaining ticks are outside the projectile lifetime.", "remainingTicks")
		var admitted: Dictionary = Target.admit_vector(current)
		if not admitted.ok: return admitted
		var velocity: Dictionary = Target.admit_vector(velocity_per_tick)
		if not velocity.ok: return velocity
		if _last_remaining_ticks == null or remaining_ticks > _last_remaining_ticks:
			_points.clear()
			var elapsed: int = _lifetime_ticks - remaining_ticks
			# C# elapsed+1 wraps at MaxValue. Its following Min(...)-1 then
			# wraps MinValue to MaxValue, issuing 2^31 samples. Add discards all
			# but the final capacity points and has no other side effects, so
			# skipping that discarded prefix has exactly the same retained tail.
			# Extreme equivalence is source-derived; only bounded original loops
			# are executed by the differential oracle, never the 2^31 loop.
			var count: int = -2147483648 if elapsed == 2147483647 else elapsed + 1
			_append_recent(admitted.value, velocity.value, count)
		elif remaining_ticks == _last_remaining_ticks:
			_points[-1] = admitted.value
		else:
			_append_recent(admitted.value, velocity.value, _last_remaining_ticks - remaining_ticks)
		_last_remaining_ticks = remaining_ticks
		return {"ok": true}

	func with_rendered_head(rendered_head: Variant) -> Dictionary:
		var admitted: Dictionary = Target.admit_vector(rendered_head)
		if not admitted.ok: return admitted
		if _points.is_empty():
			return {"ok": true, "value": [admitted.value]}
		var result: Array[Dictionary] = points()
		result[-1] = admitted.value
		return {"ok": true, "value": result}

	func _append_recent(current: Dictionary, velocity: Dictionary, sample_count: int) -> void:
		var oldest: int = 2147483647 if sample_count == -2147483648 else mini(sample_count, _capacity) - 1
		# Any larger prefix is provably overwritten by the capacity tail.
		oldest = mini(oldest, _capacity - 1)
		for offset: int in range(oldest, -1, -1):
			var point: Dictionary = {}
			var ticks: float = Float32.store_float32(offset)
			for axis: String in AXES:
				point[axis] = Float32.store_word(Float32.read_word(current[axis]) \
					- Float32.store_float32(Float32.read_word(velocity[axis]) * ticks))
			_points.append(point)
			if _points.size() > _capacity:
				_points.pop_front()
