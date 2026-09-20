# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure ThingBaseState.cs / ThingActorBaseState.cs port. Factories and mutations
## return {ok,value} or {ok:false,error_type,error,parameter}; inspect results.
## Raw poses are authoritative only after the original admission. This module
## owns no actor registry, Plane stepping, engine vectors, files or clock.
## Source: pinned Onslaught 5352a81c thing.h/thing.cpp and actor.h/actor.cpp;
## W2 07fca645 and ThingActorBaseState.cs retain the full evidence disposition.
const Values = preload("res://Core/retail_career_values.gd")
const ACTOR_LINEAGE: int = 0x80000003
const THING: int = 1
const ACTOR: int = 2
const COMPLEX_THING: int = 0x80000000
const INITIAL_CONTACT_TIME_FLOAT_BITS: int = -1027080192 # -100.0f, 0xc2c80000.
enum Flags { NONE = 0, DECLARED_SHUTDOWN = 1, IN_MAP_WHO = 2, DYING = 4, INVISIBLE = 16, IS_BIG_THING = 64 }
const BASIS_KEYS: Array[String] = ["row0_x", "row0_y", "row0_z", "row1_x", "row1_y", "row1_z", "row2_x", "row2_y", "row2_z"]


class Thing extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	var _lineage: int
	var _type_mask: int
	var _flags: int

	# Internal construction: callers use create_thing for checked admission.
	func _init(lineage: int, specific_type_mask: int, flags: int) -> void:
		_lineage = lineage
		_type_mask = lineage | specific_type_mask
		_flags = flags

	func snapshot() -> Dictionary:
		return Values.success({"flags": _flags, "type_mask": _type_mask})

	func get_flags() -> Dictionary:
		return Values.success(_flags)

	func get_type_mask() -> Dictionary:
		return Values.success(_type_mask)

	func set_thing_type(mask: Variant) -> Dictionary:
		if not Laws.is_uint32(mask):
			return Laws.transport("specificTypeMask")
		_type_mask = _lineage | mask
		return Values.success()

	func add_type(mask: Variant) -> Dictionary:
		if not Laws.is_uint32(mask):
			return Laws.transport("mask")
		_type_mask |= mask
		return Values.success()

	func add_flags(mask: Variant) -> Dictionary:
		if not Laws.is_uint16(mask):
			return Laws.transport("mask")
		_flags |= mask
		return Values.success()

	func make_invisible() -> Dictionary:
		_flags |= Flags.INVISIBLE
		return Values.success()

	func make_visible() -> Dictionary:
		_flags &= ~Flags.INVISIBLE
		return Values.success()

	func declare_shutdown() -> Dictionary:
		if (_flags & Flags.DECLARED_SHUTDOWN) != 0:
			return Values.success(false)
		_flags |= Flags.DECLARED_SHUTDOWN
		return Values.success(true)

	func mark_dying() -> Dictionary:
		if (_flags & Flags.DYING) != 0:
			return Values.success(false)
		_flags |= Flags.DYING
		return Values.success(true)

	func start_die_process() -> Dictionary:
		if not mark_dying().value:
			return Values.success(false)
		declare_shutdown()
		return Values.success(true)


class Actor extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	var _thing: Thing
	var _current_pose: Dictionary
	var _old_pose: Dictionary
	var _retail_poses: Variant = null
	var _retail_motion: Variant = null
	var _retail_plane: Variant = null
	var _velocity: Dictionary
	var _angular_velocity: Dictionary
	var _ground_time: int
	var _water_time: int
	var _object_time: int

	# Internal construction: create/restore supply detached admitted fields.
	func _init(data: Dictionary) -> void:
		_thing = Thing.new(ACTOR_LINEAGE, data.thing_type_mask, data.flags)
		_current_pose = data.current_pose.duplicate(true)
		_old_pose = data.old_pose.duplicate(true)
		_velocity = data.velocity.duplicate(true)
		_angular_velocity = data.angular_velocity.duplicate(true)
		_retail_poses = Laws.copy_nullable(data.get("retail_poses"))
		_retail_motion = Laws.copy_nullable(data.get("retail_motion"))
		_retail_plane = Laws.copy_nullable(data.get("retail_plane"))
		_ground_time = data.last_time_on_ground_float_bits
		_water_time = data.last_time_in_water_float_bits
		_object_time = data.last_time_on_object_float_bits

	func snapshot() -> Dictionary:
		var current: Dictionary = Values.success(_current_pose)
		var old: Dictionary = Values.success(_old_pose)
		var velocity: Dictionary = Values.success(_velocity)
		if _retail_poses != null:
			current = Laws.project_pose(_retail_poses.current)
			if not current.ok: return current
			old = Laws.project_pose(_retail_poses.old)
			if not old.ok: return old
		if _retail_plane != null:
			velocity = Laws.project_vector(_retail_plane.velocity)
			if not velocity.ok: return velocity
		return Values.success({"flags": _thing._flags, "current_pose": current.value.duplicate(true),
			"old_pose": old.value.duplicate(true), "velocity": velocity.value.duplicate(true),
			"angular_velocity": _angular_velocity.duplicate(true), "thing_type_mask": _thing._type_mask,
			"last_time_on_ground_float_bits": _ground_time, "last_time_in_water_float_bits": _water_time,
			"last_time_on_object_float_bits": _object_time, "retail_poses": Laws.copy_nullable(_retail_poses),
			"retail_motion": Laws.copy_nullable(_retail_motion), "retail_plane": Laws.copy_nullable(_retail_plane)})

	func get_retail_poses() -> Dictionary:
		return Values.failure("InvalidOperationException", "Retail actor initialization has not begun.") if _retail_poses == null else Values.success(_retail_poses.duplicate(true))

	func has_retail_construction() -> Dictionary:
		return Values.success(_retail_poses != null)

	func has_retail_plane_motion() -> Dictionary:
		return Values.success(_retail_plane != null)

	func begin_retail_plane(pose: Variant, motion: Variant, event_time_float_bits: Variant, specific_type_mask: Variant) -> Dictionary:
		var admitted: Dictionary = Laws.plane_motion(motion)
		if not admitted.ok: return admitted
		var velocity: Dictionary = Laws.project_vector(admitted.value.velocity)
		if not velocity.ok: return velocity
		var time: Dictionary = Laws.event_time(event_time_float_bits)
		if not time.ok: return time
		var started: Dictionary = begin_retail_initialization(pose, pose, specific_type_mask)
		if not started.ok: return started
		_retail_plane = admitted.value
		_retail_motion = {"last_move_time_float_bits": time.value, "move_countdown": 1}
		return Values.success()

	func commit_retail_plane_move(pose: Variant, motion: Variant, event_time_float_bits: Variant) -> Dictionary:
		if _retail_plane == null:
			return Values.failure("InvalidOperationException", "Plane motion has not been admitted.")
		var next_pose: Dictionary = Laws.retail_pose(pose)
		if not next_pose.ok: return next_pose
		var next_motion: Dictionary = Laws.plane_motion(motion)
		if not next_motion.ok: return next_motion
		var velocity: Dictionary = Laws.project_vector(next_motion.value.velocity)
		if not velocity.ok: return velocity
		var time: Dictionary = Laws.event_time(event_time_float_bits)
		if not time.ok: return time
		var angular: Dictionary = Laws.angular_delta(_retail_plane.current_euler, next_motion.value.current_euler)
		if not angular.ok: return angular
		_retail_poses = {"current": next_pose.value, "old": _retail_poses.current}
		_retail_plane = next_motion.value
		_retail_motion = {"last_move_time_float_bits": time.value, "move_countdown": _retail_motion.move_countdown}
		_angular_velocity = angular.value
		return Values.success()

	func clear_retail_plane_drive() -> Dictionary:
		if _retail_plane == null:
			return Values.failure("InvalidOperationException", "Plane motion has not been admitted.")
		_retail_plane.drive = Laws.zero()
		return Values.success()

	func begin_retail_initialization(current: Variant, old: Variant, specific_type_mask: Variant) -> Dictionary:
		if _retail_poses != null or _velocity != Laws.zero() or _angular_velocity != Laws.zero():
			return Values.failure("InvalidOperationException", "Retail initialization requires a fresh stationary Actor allocation.")
		var next_current: Dictionary = Laws.retail_pose(current)
		if not next_current.ok: return next_current
		var next_old: Dictionary = Laws.retail_pose(old)
		if not next_old.ok: return next_old
		if not Laws.is_uint32(specific_type_mask): return Laws.transport("specificTypeMask")
		_retail_poses = {"current": next_current.value, "old": next_old.value}
		_thing.set_thing_type(specific_type_mask)
		_thing.add_flags(Flags.IN_MAP_WHO)
		return Values.success()

	func set_retail_position(position: Variant) -> Dictionary:
		var admitted: Dictionary = Laws.retail_position(position)
		if not admitted.ok: return admitted
		var poses: Dictionary = get_retail_poses()
		if not poses.ok: return poses
		_retail_poses.current.position_float_bits = admitted.value
		return Values.success()

	func teleport_retail_position(position: Variant) -> Dictionary:
		var admitted: Dictionary = Laws.retail_position(position)
		if not admitted.ok: return admitted
		var poses: Dictionary = get_retail_poses()
		if not poses.ok: return poses
		_retail_poses.current.position_float_bits = admitted.value
		_retail_poses.old.position_float_bits = admitted.value.duplicate(true)
		return Values.success()

	func copy_retail_position_to_old() -> Dictionary:
		var poses: Dictionary = get_retail_poses()
		if not poses.ok: return poses
		_retail_poses.old.position_float_bits = _retail_poses.current.position_float_bits.duplicate(true)
		return Values.success()

	func add_published_type(mask: Variant) -> Dictionary:
		return _thing.add_type(mask)

	func add_publication_flags(flags: Variant) -> Dictionary:
		return _thing.add_flags(flags)

	func set_retail_motion(last_move_time_float_bits: Variant, move_countdown: Variant) -> Dictionary:
		var poses: Dictionary = get_retail_poses()
		if not poses.ok: return poses
		var time: Dictionary = Laws.event_time(last_move_time_float_bits)
		if not time.ok: return time
		if not Values.is_int32(move_countdown): return Laws.transport("moveCountdown")
		# Negative countdown is allowed here; complete Plane restore rejects it.
		_retail_motion = {"last_move_time_float_bits": time.value, "move_countdown": move_countdown}
		return Values.success()

	func make_invisible() -> Dictionary: return _thing.make_invisible()
	func make_visible() -> Dictionary: return _thing.make_visible()
	func declare_shutdown() -> Dictionary: return _thing.declare_shutdown()
	func start_die_process() -> Dictionary: return _thing.start_die_process()
	func mark_unit_dying() -> Dictionary: return _thing.mark_dying()
	func set_thing_type(mask: Variant) -> Dictionary: return _thing.set_thing_type(mask)

	func advance_pose(pose: Variant) -> Dictionary:
		var mode: Dictionary = _millimeter_mode()
		if not mode.ok: return mode
		var admitted: Dictionary = Laws.pose(pose, "pose")
		if not admitted.ok: return admitted
		_old_pose = _current_pose
		_current_pose = admitted.value
		return Values.success()

	func advance_low_fidelity_position(position: Variant) -> Dictionary:
		var mode: Dictionary = _millimeter_mode()
		if not mode.ok: return mode
		var admitted: Dictionary = Laws.vector(position, "position")
		if not admitted.ok: return admitted
		_old_pose = {"position_millimeters": _current_pose.position_millimeters.duplicate(), "basis_float_bits": _old_pose.basis_float_bits.duplicate()}
		_current_pose = {"position_millimeters": admitted.value, "basis_float_bits": _current_pose.basis_float_bits.duplicate()}
		return Values.success()

	func update_current_pose(pose: Variant) -> Dictionary:
		var mode: Dictionary = _millimeter_mode()
		if not mode.ok: return mode
		var admitted: Dictionary = Laws.pose(pose, "pose")
		if not admitted.ok: return admitted
		_current_pose = admitted.value
		return Values.success()

	func reset_pose(pose: Variant) -> Dictionary:
		var mode: Dictionary = _millimeter_mode()
		if not mode.ok: return mode
		var admitted: Dictionary = Laws.pose(pose, "pose")
		if not admitted.ok: return admitted
		_current_pose = admitted.value
		_old_pose = admitted.value.duplicate(true)
		return Values.success()

	func set_velocity(velocity: Variant) -> Dictionary:
		var mode: Dictionary = _millimeter_mode()
		if not mode.ok: return mode
		var admitted: Dictionary = Laws.vector(velocity, "velocity")
		if not admitted.ok: return admitted
		_velocity = admitted.value
		return Values.success()

	func add_velocity(velocity: Variant) -> Dictionary:
		var mode: Dictionary = _millimeter_mode()
		if not mode.ok: return mode
		var admitted: Dictionary = Laws.vector(velocity, "velocity")
		if not admitted.ok: return admitted
		var next: Dictionary = {}
		for key: String in ["x", "y", "z"]:
			var sum: int = _velocity[key] + admitted.value[key]
			if not Values.is_int32(sum): return Laws.overflow()
			next[key] = sum
		_velocity = next
		return Values.success()

	func stop() -> Dictionary:
		var mode: Dictionary = _millimeter_mode()
		if not mode.ok: return mode
		_velocity = Laws.zero()
		return Values.success()

	func set_angular_velocity(velocity: Variant) -> Dictionary:
		var mode: Dictionary = _millimeter_mode()
		if not mode.ok: return mode
		var admitted: Dictionary = Laws.vector(velocity, "angularVelocity")
		if not admitted.ok: return admitted
		_angular_velocity = admitted.value
		return Values.success()

	func declare_on_ground(bits: Variant) -> Dictionary:
		var time: Dictionary = Laws.event_time(bits)
		if time.ok: _ground_time = time.value
		return Values.success() if time.ok else time

	func declare_in_water(bits: Variant) -> Dictionary:
		var time: Dictionary = Laws.event_time(bits)
		if time.ok: _water_time = time.value
		return Values.success() if time.ok else time

	func declare_on_object(bits: Variant) -> Dictionary:
		var time: Dictionary = Laws.event_time(bits)
		if time.ok: _object_time = time.value
		return Values.success() if time.ok else time

	func _millimeter_mode() -> Dictionary:
		return Values.failure("NotSupportedException", "Millimetre motion cannot overwrite authoritative retail float poses.") if _retail_poses != null else Values.success()


class Laws extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	const Float24 = preload("res://Core/retail_float24.gd")

	static func is_uint32(value: Variant) -> bool:
		return typeof(value) == TYPE_INT and value >= 0 and value <= 0xffffffff

	static func is_uint16(value: Variant) -> bool:
		return typeof(value) == TYPE_INT and value >= 0 and value <= 0xffff

	static func zero() -> Dictionary: return {"x": 0, "y": 0, "z": 0}
	static func copy_nullable(value: Variant) -> Variant: return null if value == null else value.duplicate(true)
	static func transport(parameter: String) -> Dictionary: return Values.failure("ArgumentException", "State requires its exact integer record shape.", parameter)
	static func overflow() -> Dictionary: return Values.failure("OverflowException", "Arithmetic operation resulted in an overflow.")

	static func vector(value: Variant, parameter: String) -> Dictionary:
		if not value is Dictionary: return transport(parameter)
		for key: String in ["x", "y", "z"]:
			if not Values.is_int32(value.get(key)): return transport(parameter)
		return Values.success({"x": value.x, "y": value.y, "z": value.z})

	static func basis(value: Variant, parameter: String) -> Dictionary:
		if not value is Dictionary: return transport(parameter)
		var admitted: Dictionary = {}
		for key: String in BASIS_KEYS:
			if not Values.is_int32(value.get(key)): return transport(parameter)
			admitted[key] = value[key]
		return Values.success(admitted)

	static func finite_word(value: Variant) -> bool:
		return Values.is_int32(value) and Float24.is_finite_word(value)

	static func finite_vector(value: Dictionary) -> bool:
		return finite_word(value.x) and finite_word(value.y) and finite_word(value.z)

	static func finite_basis(value: Variant) -> bool:
		if not value is Dictionary: return false
		for key: String in BASIS_KEYS:
			if not finite_word(value.get(key)): return false
		return true

	static func pose(value: Variant, parameter: String, finite: bool = true) -> Dictionary:
		if value == null: return Values.failure("ArgumentNullException", "Value cannot be null.", parameter)
		if not value is Dictionary: return transport(parameter)
		var p: Dictionary = vector(value.get("position_millimeters"), parameter)
		if not p.ok: return p
		var b: Dictionary = basis(value.get("basis_float_bits"), parameter)
		if not b.ok: return b
		if finite and not finite_basis(b.value): return Values.failure("ArgumentException", "Thing/Actor pose basis must contain finite values.", parameter)
		return Values.success({"position_millimeters": p.value, "basis_float_bits": b.value})

	static func event_time(value: Variant) -> Dictionary:
		if not Values.is_int32(value): return transport("eventTimeFloatBits")
		if not finite_word(value): return Values.failure("ArgumentOutOfRangeException", "Specified argument was out of range.", "eventTimeFloatBits")
		return Values.success(value)

	static func round_int32(value: float) -> Dictionary:
		# Math.Round(AwayFromZero) uses binary64 here, not PC24. Separating the
		# fractional part avoids rounding an immediately-below-half value up.
		var rounded: float = floor(value) if value >= 0.0 else ceil(value)
		var fraction: float = value - rounded
		if fraction >= 0.5: rounded += 1.0
		elif fraction <= -0.5: rounded -= 1.0
		if not is_finite(rounded) or rounded < -2147483648.0 or rounded > 2147483647.0: return overflow()
		return Values.success(int(rounded))

	static func project_position(value: Dictionary) -> Dictionary:
		var result: Dictionary = {}
		# Source constructor evaluation is x, y, z, with each checked cast
		# completed before evaluating the next coordinate.
		var x: Dictionary = round_int32((Float24.read_word(value.x) - 288.6875) * 1000.0)
		if not x.ok: return x
		var y: Dictionary = round_int32((-10.0 - Float24.read_word(value.z)) * 1000.0)
		if not y.ok: return y
		var z: Dictionary = round_int32((Float24.read_word(value.y) - 243.25) * 1000.0)
		if not z.ok: return z
		result = {"x": x.value, "y": y.value, "z": z.value}
		return Values.success(result)

	static func project_vector(value: Dictionary) -> Dictionary:
		var x: Dictionary = round_int32(Float24.read_word(value.x) * 1000.0)
		if not x.ok: return x
		var y: Dictionary = round_int32(Float24.read_word(value.z) * -1.0 * 1000.0)
		if not y.ok: return y
		var z: Dictionary = round_int32(Float24.read_word(value.y) * 1000.0)
		if not z.ok: return z
		return Values.success({"x": x.value, "y": y.value, "z": z.value})

	static func retail_position(value: Variant) -> Dictionary:
		var admitted: Dictionary = vector(value, "position")
		if not admitted.ok: return admitted
		if not finite_vector(admitted.value): return Values.failure("ArgumentException", "Retail position must contain finite float words.", "position")
		var projected: Dictionary = project_position(admitted.value)
		return admitted if projected.ok else projected

	static func retail_pose(value: Variant) -> Dictionary:
		if value == null: return Values.failure("ArgumentNullException", "Value cannot be null.", "pose")
		if not value is Dictionary: return transport("pose")
		var p: Dictionary = retail_position(value.get("position_float_bits"))
		if not p.ok: return p
		var b: Dictionary = basis(value.get("basis_float_bits"), "pose")
		if not b.ok: return b
		if not finite_basis(b.value): return Values.failure("ArgumentException", "Retail basis must contain finite float words.", "pose")
		return Values.success({"position_float_bits": p.value, "basis_float_bits": b.value})

	static func project_basis(b: Dictionary) -> Dictionary:
		# Q*B*Q^-1 for Q(x,y,z)=(x,-z,y). Flip raw signs, including +/-zero.
		return {"row0_x": b.row0_x, "row0_y": Values.int32(b.row0_z ^ 0x80000000), "row0_z": b.row0_y,
			"row1_x": Values.int32(b.row2_x ^ 0x80000000), "row1_y": b.row2_z, "row1_z": Values.int32(b.row2_y ^ 0x80000000),
			"row2_x": b.row1_x, "row2_y": Values.int32(b.row1_z ^ 0x80000000), "row2_z": b.row1_y}

	static func project_pose(value: Dictionary) -> Dictionary:
		var position: Dictionary = project_position(value.position_float_bits)
		if not position.ok: return position
		return Values.success({"position_millimeters": position.value, "basis_float_bits": project_basis(value.basis_float_bits)})

	static func plane_motion(value: Variant) -> Dictionary:
		if value == null: return Values.failure("ArgumentNullException", "Value cannot be null.", "motion")
		if not value is Dictionary: return transport("motion")
		var result: Dictionary = {}
		for key: String in ["velocity", "drive", "current_euler", "desired_euler", "euler_rates"]:
			var v: Dictionary = vector(value.get(key), "motion")
			if not v.ok: return v
			if not finite_vector(v.value): return plane_failure()
			result[key] = v.value
		for key: String in ["x", "y", "z"]:
			if Float24.read_word(result.euler_rates[key]) < 0.0: return plane_failure()
		if not Values.is_int32(value.get("bank_flag_float_bits")): return transport("motion")
		if value.bank_flag_float_bits not in [0, 0x3f800000]: return plane_failure()
		result.bank_flag_float_bits = value.bank_flag_float_bits
		return Values.success(result)

	static func plane_failure() -> Dictionary:
		return Values.failure("ArgumentException", "Plane motion requires finite words, nonnegative rates and a boolean bank word.", "motion")

	static func delta(old_bits: int, new_bits: int, wrap: bool) -> Dictionary:
		var value: float = Float24.read_word(new_bits) - Float24.read_word(old_bits)
		var pi: float = Float24.read_word(0x40490fdb)
		if wrap and value > pi: value -= pi * 2.0
		elif wrap and value < -pi: value += pi * 2.0
		return round_int32(value * 1000000.0)

	static func angular_delta(before: Dictionary, after: Dictionary) -> Dictionary:
		var x: Dictionary = delta(before.y, after.y, false)
		if not x.ok: return x
		if x.value == -2147483648: return overflow()
		var y: Dictionary = delta(before.x, after.x, true)
		if not y.ok: return y
		var z: Dictionary = delta(before.z, after.z, true)
		if not z.ok: return z
		return Values.success({"x": -x.value, "y": y.value, "z": z.value})


static func create_thing(lineage: Variant, specific_type_mask: Variant, flags: Variant = 0) -> Dictionary:
	if not Laws.is_uint32(lineage): return Laws.transport("lineage")
	if not Laws.is_uint32(specific_type_mask): return Laws.transport("specificTypeMask")
	if not Laws.is_uint16(flags): return Laws.transport("flags")
	return Values.success(Thing.new(lineage, specific_type_mask, flags))


static func create(initial_pose: Variant, velocity: Variant, angular_velocity: Variant, specific_type_mask: Variant) -> Dictionary:
	var pose: Dictionary = Laws.pose(initial_pose, "initialPose")
	if not pose.ok: return pose
	var linear: Dictionary = Laws.vector(velocity, "velocity")
	if not linear.ok: return linear
	var angular: Dictionary = Laws.vector(angular_velocity, "angularVelocity")
	if not angular.ok: return angular
	if not Laws.is_uint32(specific_type_mask): return Laws.transport("specificTypeMask")
	return Values.success(Actor.new({"flags": 0, "current_pose": pose.value, "old_pose": pose.value,
		"velocity": linear.value, "angular_velocity": angular.value, "thing_type_mask": ACTOR_LINEAGE | specific_type_mask,
		"last_time_on_ground_float_bits": INITIAL_CONTACT_TIME_FLOAT_BITS,
		"last_time_in_water_float_bits": INITIAL_CONTACT_TIME_FLOAT_BITS,
		"last_time_on_object_float_bits": INITIAL_CONTACT_TIME_FLOAT_BITS}))


static func restore(snapshot: Variant) -> Dictionary:
	if snapshot == null: return Values.failure("ArgumentNullException", "Value cannot be null.", "snapshot")
	if not snapshot is Dictionary: return Laws.transport("snapshot")
	var poses: Variant = snapshot.get("retail_poses")
	var motion: Variant = snapshot.get("retail_motion")
	var plane: Variant = snapshot.get("retail_plane")
	if (poses != null or motion != null) and plane == null:
		return Values.failure("NotSupportedException", "Retail actor construction has no admitted restore contract yet.")
	var normalized: Dictionary = {}
	if plane != null:
		if poses == null or motion == null:
			return Values.failure("ArgumentException", "Plane motion requires complete Actor poses and movement state.", "snapshot")
		if not poses is Dictionary or not motion is Dictionary: return Laws.transport("snapshot")
		var current: Dictionary = Laws.retail_pose(poses.get("current"))
		if not current.ok: return current
		var old: Dictionary = Laws.retail_pose(poses.get("old"))
		if not old.ok: return old
		var admitted_plane: Dictionary = Laws.plane_motion(plane)
		if not admitted_plane.ok: return admitted_plane
		var time: Dictionary = Laws.event_time(motion.get("last_move_time_float_bits"))
		if not time.ok: return time
		if not Values.is_int32(motion.get("move_countdown")): return Laws.transport("snapshot")
		if motion.move_countdown < 0: return _compatibility_failure()
		for key: String in ["current", "old"]:
			var projected: Dictionary = Laws.project_pose(current.value if key == "current" else old.value)
			if not projected.ok: return projected
			var compatibility: Dictionary = Laws.pose(snapshot.get(key + "_pose"), "snapshot", false)
			if not compatibility.ok or projected.value != compatibility.value: return _compatibility_failure()
		var projected_velocity: Dictionary = Laws.project_vector(admitted_plane.value.velocity)
		if not projected_velocity.ok: return projected_velocity
		var compatibility_velocity: Dictionary = Laws.vector(snapshot.get("velocity"), "snapshot")
		if not compatibility_velocity.ok or projected_velocity.value != compatibility_velocity.value: return _compatibility_failure()
		normalized.retail_poses = {"current": current.value, "old": old.value}
		normalized.retail_motion = {"last_move_time_float_bits": time.value, "move_countdown": motion.move_countdown}
		normalized.retail_plane = admitted_plane.value
	var known_flags: int = Flags.DECLARED_SHUTDOWN | Flags.DYING | Flags.INVISIBLE
	if plane != null: known_flags |= Flags.IN_MAP_WHO
	if not Laws.is_uint16(snapshot.get("flags")) or (snapshot.flags & ~known_flags) != 0: return _snapshot_failure()
	for key: String in ["current_pose", "old_pose"]:
		var admitted: Dictionary = Laws.pose(snapshot.get(key), "snapshot")
		if not admitted.ok: return _snapshot_failure()
		normalized[key] = admitted.value
	if not Laws.is_uint32(snapshot.get("thing_type_mask")) or (snapshot.thing_type_mask & ACTOR_LINEAGE) != ACTOR_LINEAGE: return _snapshot_failure()
	for key: String in ["last_time_on_ground_float_bits", "last_time_in_water_float_bits", "last_time_on_object_float_bits"]:
		if not Laws.finite_word(snapshot.get(key)): return _snapshot_failure()
		normalized[key] = snapshot[key]
	for key: String in ["velocity", "angular_velocity"]:
		var admitted: Dictionary = Laws.vector(snapshot.get(key), "snapshot")
		if not admitted.ok: return admitted
		normalized[key] = admitted.value
	normalized.flags = snapshot.flags
	normalized.thing_type_mask = snapshot.thing_type_mask
	return Values.success(Actor.new(normalized))


static func snapshot_properties(snapshot: Variant, type_mask: Variant = 0) -> Dictionary:
	if not snapshot is Dictionary or not Laws.is_uint16(snapshot.get("flags")) or not Laws.is_uint32(snapshot.get("thing_type_mask")):
		return Laws.transport("snapshot")
	if not Laws.is_uint32(type_mask): return Laws.transport("typeMask")
	var current: Dictionary = Laws.pose(snapshot.get("current_pose"), "snapshot", false)
	var old: Dictionary = Laws.pose(snapshot.get("old_pose"), "snapshot", false)
	if snapshot.get("current_pose") == null or snapshot.get("old_pose") == null:
		return Values.failure("NullReferenceException", "Object reference not set to an instance of an object.")
	if not current.ok or not old.ok: return Laws.transport("snapshot")
	var delta: Dictionary = {}
	for key: String in ["x", "y", "z"]:
		delta[key] = Values.int32(current.value.position_millimeters[key] - old.value.position_millimeters[key])
	return Values.success({"is_invisible": (snapshot.flags & Flags.INVISIBLE) != 0, "is_dying": (snapshot.flags & Flags.DYING) != 0,
		"is_shutting_down": (snapshot.flags & Flags.DECLARED_SHUTDOWN) != 0,
		"local_last_frame_movement": delta, "is_a": (snapshot.thing_type_mask & type_mask) != 0})


static func _compatibility_failure() -> Dictionary:
	return Values.failure("ArgumentException", "Plane compatibility fields disagree with retained raw state.", "snapshot")


static func _snapshot_failure() -> Dictionary:
	return Values.failure("ArgumentException", "Thing/Actor base-state snapshot violates the source contract.", "snapshot")
