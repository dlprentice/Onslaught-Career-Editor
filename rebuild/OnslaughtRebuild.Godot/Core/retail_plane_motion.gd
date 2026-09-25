# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure RetailPlaneMotion.cs port: retained Plane words, ordered PC24/RN
## arithmetic and explicit float32 stores. The existing Actor owns mutation;
## this module owns no registry, clock, event scheduling, input or filesystem.
## Pristine 74154bfa…7750 / CComplexThing.cpp.md remain the source evidence.
## Managed-trig comparisons are bounded; general x87 parity is not established.
const Float24 = preload("res://Core/retail_float24.gd")
const Euler = preload("res://Core/retail_unit_euler.gd")
const State = preload("res://Core/thing_actor_state.gd")
const Terrain = preload("res://Core/terrain.gd")
const Values = preload("res://Core/retail_career_values.gd")
static var _pi: float = Float24.read_word(0x40490fdb)
static var _half_pi: float = Float24.read_word(0x3fc90fdb)
static var _two_pi: float = Float24.read_word(0x40c90fdb)
static var _tick: float = Float24.read_word(0x3d4ccccd)


## Operations latch the first source arithmetic refusal. Expressions following
## it produce only inert numeric placeholders; no partial result is published.
## All mutable Actor/terrain boundaries inspect this result before proceeding.
class Arithmetic extends RefCounted:
	const Float24 = preload("res://Core/retail_float24.gd")
	const Values = preload("res://Core/retail_career_values.gd")
	var error: Dictionary = {}

	func reject(parameter: String = "value") -> void:
		if error.is_empty():
			error = Values.failure("ArgumentOutOfRangeException", "Plane arithmetic requires finite admitted values.", parameter)

	func read(word: int) -> float:
		if not error.is_empty(): return 0.0
		if not Float24.is_finite_word(word):
			reject("bits")
			return 0.0
		return Float24.read_word(word)

	func store(value: float) -> float:
		if not error.is_empty(): return 0.0
		var stored: float = Float24.store_float32(value)
		if not is_finite(stored):
			reject()
			return 0.0
		return stored

	func bits(value: float) -> int:
		var stored: float = store(value)
		return Values.int32(Float24.store_word(stored)) if error.is_empty() else 0

	func _result(result: Float24.Result) -> float:
		if not result.ok: reject()
		return result.value if error.is_empty() else 0.0

	func add(a: float, b: float) -> float:
		return _result(Float24.try_add(a, b)) if error.is_empty() else 0.0

	func sub(a: float, b: float) -> float:
		return _result(Float24.try_subtract(a, b)) if error.is_empty() else 0.0

	func mul(a: float, b: float) -> float:
		return _result(Float24.try_multiply(a, b)) if error.is_empty() else 0.0

	func div(a: float, b: float) -> float:
		return _result(Float24.try_divide(a, b)) if error.is_empty() else 0.0

	func sqrt24(value: float) -> float:
		return _result(Float24.try_sqrt(value)) if error.is_empty() else 0.0

	func magnitude(x: float, y: float, z: float) -> float:
		return sqrt24(add(add(mul(x, x), mul(y, y)), mul(z, z)))

	func wrap(value: float, pi: float, two_pi: float) -> float:
		if value > pi: value = sub(value, two_pi)
		if value < -pi: value = add(value, two_pi)
		return value

	func even_int32(value: float) -> int:
		if not error.is_empty(): return 0
		var integral: float = floor(value) if value >= 0.0 else ceil(value)
		var fraction: float = value - integral
		if absf(fraction) > 0.5 or (absf(fraction) == 0.5 and fmod(integral, 2.0) != 0.0):
			integral += 1.0 if value > 0.0 else -1.0
		if not is_finite(integral) or integral < -2147483648.0 or integral > 2147483647.0:
			error = Values.failure("OverflowException", "Arithmetic operation resulted in an overflow.")
			return 0
		return int(integral)

	func finish(value: Variant = null) -> Dictionary:
		return Values.success(value) if error.is_empty() else error.duplicate(true)


static func create_initial(pose: Variant, euler: Variant) -> Dictionary:
	var p: Dictionary = _pose_carrier(pose)
	if not p.ok: return p
	var e: Dictionary = State.Laws.vector(euler, "euler")
	if not e.ok: return e
	# The source does not read the pose's float fields here. It checks only
	# non-null pose and the three Euler words; no orientation is inferred.
	var c := Arithmetic.new()
	c.read(e.value.x)
	c.read(e.value.y)
	c.read(e.value.z)
	return c.finish({"velocity": _zero(), "drive": _zero(), "current_euler": e.value.duplicate(),
		"desired_euler": e.value.duplicate(), "euler_rates": {"x": 0x3d32b8c2, "y": 0x3d32b8c2, "z": 0x3d32b8c2},
		"bank_flag_float_bits": 0})


static func euler_from_spawner_basis(basis: Variant) -> Dictionary:
	var admitted: Dictionary = State.Laws.basis(basis, "basis")
	if not admitted.ok: return admitted
	var b: Dictionary = admitted.value
	var c := Arithmetic.new()
	var x: float = c.mul(c.read(b.row0_y), 100.0)
	var y: float = c.mul(c.read(b.row1_y), 100.0)
	var z: float = c.store(c.mul(c.read(b.row2_y), 100.0))
	var yaw: int = c.bits(-atan2(x, y))
	var norm: float = c.magnitude(c.store(x), c.store(y), z)
	var pitch: int = 0
	if norm > 0.0:
		var ratio: float = c.div(z, c.store(norm))
		# Math.Asin returns NaN outside its domain; the following Bits/Store
		# owns that refusal. Avoid an engine diagnostic for an invalid asin.
		pitch = c.bits(asin(ratio) if absf(ratio) <= 1.0 else NAN)
	return c.finish({"x": yaw, "y": pitch, "z": 0})


static func integrate_velocity(velocity: Variant, drive: Variant, air_speed_float_bits: Variant, speed_mode: Variant) -> Dictionary:
	var v: Dictionary = State.Laws.vector(velocity, "velocity")
	if not v.ok: return v
	var d: Dictionary = State.Laws.vector(drive, "drive")
	if not d.ok: return d
	if not Values.is_int32(air_speed_float_bits): return State.Laws.transport("airSpeedFloatBits")
	if not Values.is_int32(speed_mode): return State.Laws.transport("speedMode")
	var c := Arithmetic.new()
	var x: float = c.store(c.add(c.read(v.value.x), c.read(d.value.x)))
	var y: float = c.store(c.add(c.read(v.value.y), c.read(d.value.y)))
	var z: float = c.store(c.add(c.read(v.value.z), c.read(d.value.z)))
	z = c.store(c.add(z, 0.0))
	var friction: float = c.read(0x3f7ae148)
	x = c.store(c.mul(x, friction))
	y = c.store(c.mul(y, friction))
	z = c.store(c.mul(z, friction))
	var norm: float = c.magnitude(x, y, z)
	var stored_norm: float = c.store(norm)
	var speed: float = c.read(air_speed_float_bits)
	if speed < 0.0: c.reject("airSpeedFloatBits")
	if speed_mode in [1, 2]: speed = c.mul(speed, 1.5)
	var limit: float = c.mul(speed, _tick)
	if norm > 0.0 and stored_norm > limit:
		var ratio: float = c.div(limit, stored_norm)
		x = c.mul(x, ratio)
		y = c.mul(y, ratio)
		z = c.mul(z, ratio)
	return c.finish({"x": c.bits(x), "y": c.bits(y), "z": c.bits(z)})


static func update_guide(pose: Variant, integrated_velocity: Variant, guide: Variant) -> Dictionary:
	if pose == null: return _null("pose")
	if guide == null: return _null("guide")
	var p: Dictionary = _pose_carrier(pose)
	if not p.ok: return p
	var v: Dictionary = State.Laws.vector(integrated_velocity, "integratedVelocity")
	if not v.ok: return v
	var g: Dictionary = _guide_carrier(guide)
	if not g.ok: return g
	var c := Arithmetic.new()
	var x: float = c.read(p.value.position_float_bits.x)
	var y: float = c.read(p.value.position_float_bits.y)
	var z: float = c.read(p.value.position_float_bits.z)
	var dx: float = c.store(c.sub(c.read(g.value.destination.x), x))
	var dy: float = c.store(c.sub(c.read(g.value.destination.y), y))
	var dz: float = c.store(c.sub(c.read(g.value.destination.z), z))
	var heading: float = c.store(-atan2(dx, dy))
	var horizontal: float = c.sqrt24(c.add(c.mul(dy, dy), c.mul(dx, dx)))
	var pitch: float = c.store(atan2(dz, horizontal))
	var velocity_heading: float = c.store(-atan2(c.read(v.value.x), c.read(v.value.y)))
	if g.value.mode == 0:
		heading = c.add(velocity_heading, _half_pi)
		pitch = 0.0
	elif g.value.mode == 2:
		heading = c.sub(heading, _pi)
	heading = c.wrap(heading, _pi, _two_pi)
	pitch = c.store(c.wrap(pitch, _pi, _two_pi))
	if g.value.controller_state != 2:
		if g.value.avoidance_position != null:
			pitch = -c.read(0x3f860a92) if c.sub(c.read(g.value.avoidance_position.z), z) > 0.0 else c.read(0x3f860a92)
		var clearance: float = c.read(g.value.clearance_float_bits)
		if clearance < 5.0: pitch = -c.read(0x3f490fdb)
		elif clearance < 15.0 and pitch > 0.0: pitch = 0.0
		elif clearance > 50.0: pitch = c.read(0x3f490fdb)
		if g.value.speed_mode not in [1, 2]:
			if x < 10.0: heading = -_half_pi
			elif x > 502.0: heading = _half_pi
			elif y < 10.0: heading = 0.0
			elif y > 502.0: heading = _pi
	var adjusted_heading: float = heading
	if velocity_heading < -_half_pi and heading > _half_pi:
		adjusted_heading = c.sub(heading, _two_pi)
	elif velocity_heading > _half_pi and heading < -_half_pi:
		adjusted_heading = c.add(heading, _two_pi)
	var bank: float = minf(absf(c.sub(velocity_heading, adjusted_heading)), _half_pi)
	var b: Dictionary = p.value.basis_float_bits
	var side: float = c.add(c.add(c.mul(c.read(b.row2_x), dz), c.mul(c.read(b.row1_x), dy)), c.mul(c.read(b.row0_x), dx))
	bank = c.store(bank if side < 0.0 else -bank)
	var scale: float = c.mul(c.mul(15.0, _tick), 4.0)
	return c.finish({"desired_euler": {"x": c.bits(heading), "y": c.bits(pitch), "z": c.bits(bank)},
		"drive": {"x": c.bits(c.mul(c.read(b.row0_y), scale)), "y": c.bits(c.mul(c.read(b.row1_y), scale)),
			"z": c.bits(c.mul(c.read(b.row2_y), scale))},
		"bank_flag_float_bits": 0x3f800000 if absf(bank) > c.read(0x3dcccccd) else 0})


static func translate(position: Variant, velocity: Variant) -> Dictionary:
	var p: Dictionary = State.Laws.vector(position, "position")
	if not p.ok: return p
	var v: Dictionary = State.Laws.vector(velocity, "velocity")
	if not v.ok: return v
	var c := Arithmetic.new()
	var output: Dictionary = {}
	for key: String in ["x", "y", "z"]:
		output[key] = c.bits(c.add(c.read(p.value[key]), c.read(v.value[key])))
	return c.finish(output)


static func align_velocity(velocity: Variant, basis: Variant) -> Dictionary:
	var v: Dictionary = State.Laws.vector(velocity, "velocity")
	if not v.ok: return v
	var b: Dictionary = State.Laws.basis(basis, "basis")
	if not b.ok: return b
	var c := Arithmetic.new()
	var magnitude: float = c.magnitude(c.read(v.value.x), c.read(v.value.y), c.read(v.value.z))
	return c.finish({"x": c.bits(c.mul(magnitude, c.read(b.value.row0_y))),
		"y": c.bits(c.mul(magnitude, c.read(b.value.row1_y))), "z": c.bits(c.mul(magnitude, c.read(b.value.row2_y)))})


static func compute_clearance(terrain: Variant, position: Variant) -> Dictionary:
	if terrain == null: return _null("terrain")
	if not terrain is Terrain.Heightfield: return State.Laws.transport("terrain")
	var p: Dictionary = State.Laws.vector(position, "position")
	if not p.ok: return p
	var c := Arithmetic.new()
	var x: int = c.even_int32(c.read(p.value.x))
	if not c.error.is_empty(): return c.finish()
	var y: int = c.even_int32(c.read(p.value.y))
	if not c.error.is_empty(): return c.finish()
	var height: float = -c.read(p.value.z)
	if not c.error.is_empty(): return c.finish()
	var minimum: float = c.read(0x497423f0)
	var metadata: Dictionary = terrain.metadata()
	var height_scale: float = Float24.read_word(metadata.height_scale_bits)
	var water: float = Float24.read_word(metadata.water_level_bits)
	for offset_y: int in range(-20, 21, 5):
		for offset_x: int in range(-20, 21, 5):
			var sample_x: int = x + offset_x
			if not Values.is_int32(sample_x): return State.Laws.overflow()
			var sample_y: int = y + offset_y
			if not Values.is_int32(sample_y): return State.Laws.overflow()
			var sampled: Dictionary = terrain.sample_air_guide_height_units(sample_x, sample_y)
			if not sampled.ok: return sampled
			var ground: float = -c.mul(sampled.value, height_scale)
			var candidate: float = c.sub(height, maxf(ground, -water))
			if candidate < minimum: minimum = c.store(candidate)
			if not c.error.is_empty(): return c.finish()
	return c.finish(c.bits(minimum))


## One transactional free-flight step. Contact/lifecycle/event owners are
## deliberately absent. Invalid final commit leaves the existing Actor intact.
static func advance_free_flight(actor: Variant, guide: Variant, air_speed_float_bits: Variant, event_time_float_bits: Variant) -> Dictionary:
	if actor == null: return _null("actor")
	if not actor is State.Actor: return State.Laws.transport("actor")
	var before: Dictionary = actor.snapshot()
	if not before.ok: return before
	var motion: Variant = before.value.retail_plane
	if motion == null:
		return Values.failure("InvalidOperationException", "Plane creation inputs were not admitted.")
	# C# dereferences guide.SpeedMode before IntegrateVelocity is entered.
	if guide == null:
		return Values.failure("NullReferenceException", "Object reference not set to an instance of an object.")
	var g: Dictionary = _guide_carrier(guide)
	if not g.ok: return g
	var pose: Dictionary = before.value.retail_poses.current
	var velocity: Dictionary = integrate_velocity(motion.velocity, motion.drive, air_speed_float_bits, g.value.speed_mode)
	if not velocity.ok: return velocity
	var next: Dictionary = update_guide(pose, velocity.value, g.value)
	if not next.ok: return next
	var position: Dictionary = translate(pose.position_float_bits, velocity.value)
	if not position.ok: return position
	var euler: Euler.Result = Euler.smooth(_words(motion.current_euler), _words(next.value.desired_euler), _words(motion.euler_rates), 1.0)
	if not euler.ok: return _euler_failure(euler.error)
	var skips_euler: bool = true
	for key: String in ["x", "y", "z"]:
		if Float24.read_word(motion.current_euler[key]) != Float24.read_word(next.value.desired_euler[key]):
			skips_euler = false
			break
	var basis: Dictionary = pose.basis_float_bits.duplicate()
	if not skips_euler:
		var built: Euler.Result = Euler.build_basis(euler.words)
		if not built.ok: return _euler_failure(built.error)
		for index: int in range(9): basis[State.BASIS_KEYS[index]] = Values.int32(built.words[index])
	var aligned: Dictionary = align_velocity(velocity.value, basis)
	if not aligned.ok: return aligned
	var next_motion: Dictionary = motion.duplicate(true)
	next_motion.velocity = aligned.value
	next_motion.drive = next.value.drive
	next_motion.current_euler = _vector_words(euler.words)
	next_motion.desired_euler = next.value.desired_euler
	next_motion.bank_flag_float_bits = next.value.bank_flag_float_bits
	return actor.commit_retail_plane_move({"position_float_bits": position.value, "basis_float_bits": basis}, next_motion, event_time_float_bits)


static func _pose_carrier(pose: Variant) -> Dictionary:
	if pose == null: return _null("pose")
	if not pose is Dictionary: return State.Laws.transport("pose")
	var position: Dictionary = State.Laws.vector(pose.get("position_float_bits"), "pose")
	if not position.ok: return position
	var basis: Dictionary = State.Laws.basis(pose.get("basis_float_bits"), "pose")
	if not basis.ok: return basis
	return Values.success({"position_float_bits": position.value, "basis_float_bits": basis.value})


static func _guide_carrier(guide: Variant) -> Dictionary:
	if guide == null: return _null("guide")
	if not guide is Dictionary: return State.Laws.transport("guide")
	var destination: Dictionary = State.Laws.vector(guide.get("destination"), "guide")
	if not destination.ok: return destination
	for key: String in ["mode", "clearance_float_bits", "controller_state", "speed_mode"]:
		if not Values.is_int32(guide.get(key)): return State.Laws.transport("guide")
	var avoidance: Variant = guide.get("avoidance_position")
	if avoidance != null:
		var result: Dictionary = State.Laws.vector(avoidance, "guide")
		if not result.ok: return result
		avoidance = result.value
	return Values.success({"destination": destination.value, "mode": guide.mode, "clearance_float_bits": guide.clearance_float_bits,
		"controller_state": guide.controller_state, "speed_mode": guide.speed_mode, "avoidance_position": avoidance})


static func _words(vector: Dictionary) -> PackedInt64Array:
	return PackedInt64Array([vector.x, vector.y, vector.z])


static func _vector_words(words: PackedInt64Array) -> Dictionary:
	return {"x": Values.int32(words[0]), "y": Values.int32(words[1]), "z": Values.int32(words[2])}


static func _zero() -> Dictionary: return {"x": 0, "y": 0, "z": 0}
static func _null(parameter: String) -> Dictionary:
	return Values.failure("ArgumentNullException", "Value cannot be null.", parameter)


static func _euler_failure(message: String) -> Dictionary:
	var parameter: String = "value"
	if "rate must be nonnegative" in message: parameter = "rateBits"
	elif "angle must be a finite" in message or "rate must be a finite" in message: parameter = "bits"
	return Values.failure("ArgumentOutOfRangeException", message, parameter)
