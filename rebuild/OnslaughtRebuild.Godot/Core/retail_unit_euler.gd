# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Finite PC24/RN Unit angle update and matrix operation order at 0x004fa4b0.
## Ports OnslaughtRebuild.Core/RetailUnitEuler.cs; yaw/pitch/roll are retained
## retail float32 words, never angles reconstructed from a projected matrix.
## Provenance and bounded native oracle: the existing CComplexThing.cpp.md
## function map, pristine specimen SHA-256 74154bfa…7750. Trig matches admitted
## finite fixtures; general x87/cross-host transcendental parity is unproven.

const Float24 = preload("res://Core/retail_float24.gd")

static var _half_pi: float = Float24.read_word(0x3fc90fdb)
static var _pi: float = Float24.read_word(0x40490fdb)
static var _two_pi: float = Float24.read_word(0x40c90fdb)
static var _ease: float = Float24.read_word(0x3dcccccd)


class Result extends RefCounted:
	var ok: bool
	## Unsigned 32-bit words: three yaw/pitch/roll values, or nine row-major basis values.
	var words: PackedInt64Array
	var error: String
	## Invalid component, or -1 for a whole-input rejection.
	var axis: int

	func _init(result_words: PackedInt64Array, result_error: String = "", result_axis: int = -1) -> void:
		ok = result_error.is_empty()
		words = result_words
		error = result_error
		axis = result_axis


## Result admission is active in release builds. No input array is changed and
## no partial words are returned on failure. The multiplier is a float32 input
## in the C# contract, so its store occurs before positive/finite admission.
static func smooth(
		current: PackedInt64Array,
		desired: PackedInt64Array,
		maximum_step: PackedInt64Array,
		move_multiplier: float) -> Result:
	if current.size() != 3 or desired.size() != 3 or maximum_step.size() != 3:
		return _failure("Unit Euler vectors must each contain three words.")
	var multiplier: float = Float24.store_float32(move_multiplier)
	if not is_finite(multiplier) or multiplier <= 0.0:
		return _failure("Unit Euler move multiplier must be positive and finite as float32.")
	var output := PackedInt64Array()
	output.resize(3)
	for index: int in range(3):
		if not Float24.is_finite_word(current[index]):
			return _failure("Unit Euler current angle must be a finite float32 word.", index)
		if not Float24.is_finite_word(desired[index]):
			return _failure("Unit Euler desired angle must be a finite float32 word.", index)
		var current_value: float = Float24.read_word(current[index])
		var desired_value: float = Float24.read_word(desired[index])
		# Retail skips the complete equal axis, including its rate read, wrap
		# and stores. Equal -0/+0 therefore retains the current negative zero.
		if current_value == desired_value:
			output[index] = current[index] & Float24.WORD_MASK
			continue
		if not Float24.is_finite_word(maximum_step[index]):
			return _failure("Unit Euler active rate must be a finite float32 word.", index)
		var rate: float = Float24.read_word(maximum_step[index])
		if rate < 0.0:
			return _failure("Unit Euler active rate must be nonnegative.", index)
		var updated: float = _smooth_axis_finite(current_value, desired_value, rate, multiplier, index != 1)
		if not is_finite(updated):
			return _failure("Unit Euler output must remain finite after each float32 store.", index)
		output[index] = Float24.store_word(updated)
	return Result.new(output)


## Reconstruct nine row-major retail basis words. The caller must keep the old
## basis when all current/desired axes compare equal: Unit skips the routine.
## Yaw sine/cosine and pitch/roll cosine are float32 stores; pitch/roll sine
## retain binary64 values until the explicitly ordered PC24 operations below.
static func build_basis(euler: PackedInt64Array) -> Result:
	if euler.size() != 3:
		return _failure("Unit Euler basis input must contain three words.")
	for index: int in range(3):
		if not Float24.is_finite_word(euler[index]):
			return _failure("Unit Euler basis angle must be a finite float32 word.", index)
	var yaw: float = Float24.read_word(euler[0])
	var pitch: float = Float24.read_word(euler[1])
	var roll: float = Float24.read_word(euler[2])
	var yaw_cos: float = Float24.store_float32(cos(yaw))
	var yaw_sin: float = Float24.store_float32(sin(yaw))
	var roll_cos: float = Float24.store_float32(cos(roll))
	var roll_sin: float = sin(roll)
	var pitch_cos: float = Float24.store_float32(cos(pitch))
	var pitch_sin: float = sin(pitch)
	for value: float in [yaw_cos, yaw_sin, roll_cos, roll_sin, pitch_cos, pitch_sin]:
		if not is_finite(value):
			return _failure("Unit Euler trigonometric values must remain finite.")
	var sine_product: float = Float24.multiply_finite(pitch_sin, roll_sin)
	var mixed_product: float = Float24.multiply_finite(pitch_sin, roll_cos)
	# 0x004fa784 stores this PC24 product without popping it. Row0Z retains
	# the wider exponent while Row1Z reloads the float32 copy.
	var stored_mixed: float = Float24.store_float32(mixed_product)
	var values: Array[float] = [
		Float24.subtract_finite(Float24.multiply_finite(roll_cos, yaw_cos),
			Float24.multiply_finite(sine_product, yaw_sin)),
		-Float24.multiply_finite(pitch_cos, yaw_sin),
		Float24.add_finite(Float24.multiply_finite(mixed_product, yaw_sin),
			Float24.multiply_finite(roll_sin, yaw_cos)),
		Float24.add_finite(Float24.multiply_finite(sine_product, yaw_cos),
			Float24.multiply_finite(roll_cos, yaw_sin)),
		Float24.multiply_finite(pitch_cos, yaw_cos),
		Float24.subtract_finite(Float24.multiply_finite(roll_sin, yaw_sin),
			Float24.multiply_finite(stored_mixed, yaw_cos)),
		-Float24.multiply_finite(pitch_cos, roll_sin),
		pitch_sin,
		Float24.multiply_finite(pitch_cos, roll_cos),
	]
	var output := PackedInt64Array()
	output.resize(9)
	for index: int in range(9):
		var stored: float = Float24.store_float32(values[index])
		if not is_finite(stored):
			return _failure("Unit Euler basis output must remain finite as float32.", index)
		output[index] = Float24.store_word(stored)
	return Result.new(output)


## Admitted inputs are finite float32 angles/rate and a positive float32
## multiplier. Their products fit the binary64 carrier; no operation Result
## is needed inside this kernel. A nonfinite final store returns to the outer
## admission boundary before any wrap arithmetic can consume it.
static func _smooth_axis_finite(current: float, desired: float, rate: float, multiplier: float, wrap: bool) -> float:
	# This raw cap store may overflow to +Inf in the C# owner. A finite smaller
	# step still wins; only the updated-angle stores impose finite admission.
	var cap: float = Float24.store_float32(Float24.multiply_finite(multiplier, rate))
	var adjusted_desired: float = desired
	if wrap:
		if current < -_half_pi and desired > _half_pi:
			adjusted_desired = Float24.subtract_finite(desired, _two_pi)
		elif current > _half_pi and desired < -_half_pi:
			adjusted_desired = Float24.add_finite(desired, _two_pi)
	var step: float = Float24.multiply_finite(
		Float24.multiply_finite(absf(Float24.subtract_finite(current, adjusted_desired)), multiplier), _ease)
	if step > cap:
		step = cap
	var add: bool = current < desired
	if wrap:
		var difference: float = Float24.subtract_finite(desired, current) if add else Float24.subtract_finite(current, desired)
		if difference > _pi:
			add = not add
	var updated: float = Float24.store_float32(
		Float24.add_finite(current, step) if add else Float24.subtract_finite(current, step))
	if not is_finite(updated):
		return updated
	if wrap:
		# Exactly one correction after the first float32 store; never fposmod.
		if updated > _pi:
			updated = Float24.store_float32(Float24.subtract_finite(updated, _two_pi))
		elif updated < -_pi:
			updated = Float24.store_float32(Float24.add_finite(updated, _two_pi))
	return updated


static func _failure(message: String, index: int = -1) -> Result:
	return Result.new(PackedInt64Array(), message, index)
