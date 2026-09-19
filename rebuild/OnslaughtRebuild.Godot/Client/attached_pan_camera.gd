# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Current AttachedPanCameraState.cs contract, not the unfinished camera draft.
## Duration/lead are caller supplied; the source/retail duration distinction and
## unresolved constructor/ABI equality remain with that C# provenance owner.
## Frames: {event_frame,pan_elapsed_ticks,zoom_permille,attached_thing:null|{
## thing_id,pose:{position,forward,up},pan_right}}. Vectors hold exact UInt32
## x_bits/y_bits/z_bits; no normalization/admission silently rewrites a pose.
## World facts: tick,opening_ticks_remaining,zoom_permille,actors:[{name,actor_id}],
## facing_yaw_micro_rad,facing_pitch_micro_rad,body_roll_micro_rad,
## player_position:{x,z},player_elevation_millimeters. Pose facts are read only
## when Player 1 exists. Names accept native String/null or raw UTF-16 units.
## No scene, device, singleton clock or second simulation owner.

const Float32 = preload("res://Core/retail_float24.gd")
const CameraLaws = preload("res://Core/camera_laws.gd")
const Writer = preload("res://Core/canonical_binary_writer.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const END_OF_EVENT_FRAME: int = 0
const TELEPORT_METERS: float = 10.0
const ZOOM_SCALE: int = 1000


static func create(pan_duration_ticks: Variant, control_view_handoff_lead_ticks: Variant) -> Dictionary:
	if not State.i32(pan_duration_ticks) or not State.i32(control_view_handoff_lead_ticks):
		return State.failure("ArgumentException", "Camera duration and lead require exact Int32 values.")
	if pan_duration_ticks < 1:
		return State.failure("ArgumentOutOfRangeException", "Pan duration must be positive.", "panDurationTicks")
	if control_view_handoff_lead_ticks < 0 or control_view_handoff_lead_ticks >= pan_duration_ticks:
		return State.failure("ArgumentOutOfRangeException", "Handoff lead must be within the pan duration.", "controlViewHandoffLeadTicks")
	return {"ok": true, "value": State.new(pan_duration_ticks, control_view_handoff_lead_ticks)}


static func identity_pose() -> Dictionary:
	return State.identity_pose()


static func compute_hash(snapshot: Variant) -> Dictionary:
	return State.hash_snapshot(snapshot)


class State extends RefCounted:
	var _pan_duration_ticks: int
	var _control_view_handoff_tick: int
	var _snapshot: Variant = null

	func _init(duration: int, lead: int) -> void:
		_pan_duration_ticks = duration
		_control_view_handoff_tick = duration - lead

	func current_snapshot() -> Dictionary:
		if _snapshot == null:
			return failure("InvalidOperationException", "No camera event frame has been supplied.")
		return {"ok": true, "value": _snapshot.duplicate(true)}

	func advance(previous: Variant, current: Variant) -> Dictionary:
		# C# checks both null references before creating the current frame, then
		# permits render-only idempotence to bypass all previous-frame reads.
		if previous == null:
			return failure("ArgumentNullException", "Previous world is required.", "previous")
		if current == null:
			return failure("ArgumentNullException", "Current world is required.", "current")
		var current_result: Dictionary = _create_frame(current)
		if not current_result.ok:
			return current_result
		var current_frame: Dictionary = current_result.value
		if _snapshot != null and _same_frame(current_frame, _snapshot.current_frame):
			return current_snapshot()
		var previous_result: Dictionary = _create_frame(previous)
		if not previous_result.ok:
			return previous_result
		var previous_frame: Dictionary = previous_result.value
		if _snapshot == null or previous_frame.event_frame >= _snapshot.current_frame.event_frame:
			var advanced: Dictionary = advance_at_end_of_event_frame(previous_frame)
			if not advanced.ok:
				return advanced
		# The previous advance remains committed if current semantic validation
		# fails; this preserves the existing method's observable mutation order.
		return advance_at_end_of_event_frame(current_frame)

	func advance_at_end_of_event_frame(frame: Variant) -> Dictionary:
		var admitted: Dictionary = admit_frame(frame)
		if not admitted.ok:
			return admitted
		var value: Dictionary = admitted.value
		if value.event_frame < 0 or value.pan_elapsed_ticks < 0 or value.zoom_permille < 1:
			return failure("ArgumentOutOfRangeException", "Camera frame requires nonnegative ticks and positive zoom.", "frame")
		if _snapshot == null:
			return _reset_to(value, 0)
		var current: Dictionary = _snapshot
		if value.event_frame < current.current_frame.event_frame or value.pan_elapsed_ticks < current.current_frame.pan_elapsed_ticks:
			if current.reset_generation == 2147483647:
				return failure("OverflowException", "Camera reset generation exceeds Int32.")
			return _reset_to(value, current.reset_generation + 1)
		if value.event_frame == current.current_frame.event_frame:
			if _same_frame(value, current.current_frame):
				return current_snapshot()
			return failure("InvalidOperationException", "One event frame cannot carry two different camera inputs.")
		var previous_pose: Dictionary = current.current_pan_pose
		var next_pose: Dictionary = previous_pose
		if current.pan_update_scheduled and value.attached_thing != null:
			next_pose = _evaluate_pan_pose(value.attached_thing, value.pan_elapsed_ticks, previous_pose)
		_snapshot = {"pan_duration_ticks": _pan_duration_ticks, "control_view_handoff_tick": _control_view_handoff_tick,
			"reset_generation": current.reset_generation, "update_phase": END_OF_EVENT_FRAME,
			"previous_frame": current.current_frame, "current_frame": value,
			"previous_pan_pose": previous_pose, "current_pan_pose": next_pose,
			"pan_update_scheduled": value.pan_elapsed_ticks < _control_view_handoff_tick}
		return current_snapshot()

	## The alpha is a raw UInt32 word, exactly the C# Single argument. This
	## keeps negative zero and rejects NaN/infinity before the no-frame check.
	func sample(interpolation_alpha_bits: Variant) -> Dictionary:
		if not word(interpolation_alpha_bits):
			return failure("ArgumentException", "Interpolation alpha requires a raw UInt32 float word.")
		var alpha: float = Float32.read_word(interpolation_alpha_bits)
		if not is_finite(alpha) or alpha < 0.0 or alpha > 1.0:
			return failure("ArgumentOutOfRangeException", "Interpolation alpha must be finite and within 0..1.", "interpolationAlpha")
		if _snapshot == null:
			return current_snapshot()
		var value: Dictionary = _snapshot
		var elapsed: float = _lerp(value.previous_frame.pan_elapsed_ticks, value.current_frame.pan_elapsed_ticks, alpha)
		if elapsed < f32(_control_view_handoff_tick):
			return {"ok": true, "value": _view(value.current_frame.attached_thing,
				_interpolate(value.previous_pan_pose, value.current_pan_pose, alpha), CameraLaws.DEFAULT_ZOOM_BITS, false, true)}
		var attached: Variant = value.current_frame.attached_thing
		if attached == null:
			return {"ok": true, "value": _view(null, identity_pose(), CameraLaws.DEFAULT_ZOOM_BITS, false, false)}
		var pose: Dictionary = attached.pose
		var previous_attached: Variant = value.previous_frame.attached_thing
		if previous_attached != null and previous_attached.thing_id == attached.thing_id \
				and _distance_squared(previous_attached.pose.position, attached.pose.position) <= TELEPORT_METERS * TELEPORT_METERS:
			pose = _interpolate(previous_attached.pose, attached.pose, alpha)
		var zoom: float = _lerp(value.previous_frame.zoom_permille, value.current_frame.zoom_permille, alpha)
		return {"ok": true, "value": _view(attached, pose, Float32.store_word(zoom / float(ZOOM_SCALE)), true, false)}

	func _reset_to(frame: Dictionary, generation: int) -> Dictionary:
		var pose: Dictionary = identity_pose() if frame.attached_thing == null else _evaluate_pan_pose(frame.attached_thing, frame.pan_elapsed_ticks, identity_pose())
		_snapshot = {"pan_duration_ticks": _pan_duration_ticks, "control_view_handoff_tick": _control_view_handoff_tick,
			"reset_generation": generation, "update_phase": END_OF_EVENT_FRAME,
			"previous_frame": frame, "current_frame": frame, "previous_pan_pose": pose, "current_pan_pose": pose,
			"pan_update_scheduled": frame.pan_elapsed_ticks < _control_view_handoff_tick}
		return current_snapshot()

	func _create_frame(world: Variant) -> Dictionary:
		if not world is Dictionary or not i32(world.get("opening_ticks_remaining")):
			return failure("ArgumentException", "World camera facts require Int32 opening_ticks_remaining.")
		var elapsed: int = _pan_duration_ticks - world.opening_ticks_remaining
		if not i32(elapsed):
			return failure("OverflowException", "Pan elapsed subtraction exceeds Int32.")
		if elapsed < 0:
			return failure("InvalidOperationException", "Core exposed more opening-pan ticks than the caller supplied duration.")
		if not world.get("actors") is Array:
			return failure("ArgumentException", "World camera facts require explicit actors.")
		var player: Variant = null
		for actor: Variant in world.actors:
			if not actor is Dictionary or not actor.has("name"):
				return failure("ArgumentException", "Actor fact requires an explicit nullable name.")
			var name_units: Dictionary = Text.units(actor.name)
			if not name_units.ok:
				return failure("ArgumentException", name_units.error)
			if name_units.value == PackedInt32Array([80, 108, 97, 121, 101, 114, 32, 49]):
				if player != null:
					return failure("InvalidOperationException", "Sequence contains more than one matching Player 1.")
				player = actor
		var attached: Variant = null
		if player != null:
			if not i32(player.get("actor_id")):
				return failure("ArgumentException", "Player actor_id requires Int32.")
			for key: String in ["facing_yaw_micro_rad", "facing_pitch_micro_rad", "body_roll_micro_rad", "player_elevation_millimeters"]:
				if not i32(world.get(key)):
					return failure("ArgumentException", "World camera facts require Int32 " + key + ".")
			if not world.get("player_position") is Dictionary or not i32(world.player_position.get("x")) or not i32(world.player_position.get("z")):
				return failure("ArgumentException", "Player position requires Int32 x/z.")
			attached = _create_attached_thing(player.actor_id, world)
		if not i32(world.get("tick")) or not i32(world.get("zoom_permille")):
			return failure("ArgumentException", "World camera facts require Int32 tick and zoom_permille.")
		return {"ok": true, "value": {"event_frame": world.tick, "pan_elapsed_ticks": elapsed,
			"zoom_permille": world.zoom_permille, "attached_thing": attached}}

	static func _create_attached_thing(thing_id: int, world: Dictionary) -> Dictionary:
		var yaw: float = f32(f32(world.facing_yaw_micro_rad) / 1000000.0)
		var pitch: float = f32(f32(world.facing_pitch_micro_rad) / 1000000.0)
		var roll: float = f32(f32(world.body_roll_micro_rad) / 1000000.0)
		# Vector2's native real_t overload supplies the same float sin/cos as
		# MathF on the pinned engine. Double sin/cos then a float store differed
		# in the already validated scanner boundary and must not replace it.
		var yaw_trig: Vector2 = Vector2.from_angle(yaw)
		var pitch_trig: Vector2 = Vector2.from_angle(pitch)
		var roll_trig: Vector2 = Vector2.from_angle(roll)
		var forward: Dictionary = _vector(f32(-yaw_trig.y * pitch_trig.x), -pitch_trig.y, f32(-yaw_trig.x * pitch_trig.x))
		var right: Dictionary = _vector(yaw_trig.x, 0.0, -yaw_trig.y)
		var level_up: Dictionary = _normalize(_cross(right, forward), _vector(0.0, 1.0, 0.0))
		var body_up: Dictionary = _add(_scale(level_up, roll_trig.x), _scale(right, roll_trig.y))
		# C# negates the Int32 Z before conversion; MinValue wraps unchecked.
		var neg_z: int = world.player_position.z if world.player_position.z == -2147483648 else -world.player_position.z
		var unit_scale: float = f32(0.001)
		return {"thing_id": thing_id, "pose": {"position": _vector(f32(f32(world.player_position.x) * unit_scale),
			f32(f32(world.player_elevation_millimeters) * unit_scale), f32(f32(neg_z) * unit_scale)),
			"forward": forward, "up": body_up}, "pan_right": right}

	func _evaluate_pan_pose(attached: Dictionary, elapsed: int, retained: Dictionary) -> Dictionary:
		var center: Dictionary = attached.pose.position
		var forward: Dictionary = attached.pose.forward
		var right: Dictionary = attached.pan_right
		var up: Dictionary = _vector(0.0, 1.0, 0.0)
		var point0: Dictionary = _add(_add(center, _scale(forward, 10.0)), _scale(up, f32(4.3)))
		var point1: Dictionary = _add(_add(center, _scale(right, 5.0)), _scale(up, f32(-1.3)))
		var point2: Dictionary = _add(_add(center, _scale(forward, -9.0)), _scale(up, f32(1.3)))
		var point3: Dictionary = _add(center, _scale(forward, -2.5))
		var fraction: float = clampf(f32(f32(elapsed) / f32(_pan_duration_ticks)), 0.0, f32(0.999999))
		var position: Dictionary = _spline(point0, point1, point2, point3, fraction)
		return {"position": position, "forward": _normalize(_subtract(center, position), retained.forward), "up": up}

	static func _spline(p0: Dictionary, p1: Dictionary, p2: Dictionary, p3: Dictionary, fraction: float) -> Dictionary:
		# Current committed quadratic B-spline with knots [0,0,0,1,2,2,2].
		var u: float = f32(fraction * 2.0)
		if u < 1.0:
			var one_minus: float = f32(1.0 - u)
			return _add(_add(_scale(p0, f32(one_minus * one_minus)),
				_scale(p1, f32(f32(2.0 * u) - f32(f32(1.5 * u) * u)))), _scale(p2, f32(f32(0.5 * u) * u)))
		var two_minus: float = f32(2.0 - u)
		var u_minus: float = f32(u - 1.0)
		return _add(_add(_scale(p1, f32(f32(0.5 * two_minus) * two_minus)),
			_scale(p2, f32(f32(2.0 * two_minus) - f32(f32(1.5 * two_minus) * two_minus)))), _scale(p3, f32(u_minus * u_minus)))

	static func _interpolate(previous: Dictionary, current: Dictionary, alpha: float) -> Dictionary:
		if alpha == 0.0:
			return previous.duplicate(true)
		if alpha == 1.0:
			return current.duplicate(true)
		return {"position": _lerp_vector(previous.position, current.position, alpha),
			"forward": _normalize(_lerp_vector(previous.forward, current.forward, alpha), current.forward),
			"up": _normalize(_lerp_vector(previous.up, current.up, alpha), current.up)}

	static func _view(attached: Variant, pose: Dictionary, zoom: int, hud: bool, opening: bool) -> Dictionary:
		return {"attached_thing_id": null if attached == null else attached.thing_id,
			"pose": pose.duplicate(true), "zoom_bits": zoom, "hud_visible": hud, "opening_pan_active": opening}

	static func identity_pose() -> Dictionary:
		return {"position": _vector(0.0, 0.0, 0.0), "forward": _vector(0.0, 0.0, -1.0), "up": _vector(0.0, 1.0, 0.0)}

	static func _vector(x: float, y: float, z: float) -> Dictionary:
		return {"x_bits": Float32.store_word(x), "y_bits": Float32.store_word(y), "z_bits": Float32.store_word(z)}

	static func _add(left: Dictionary, right: Dictionary) -> Dictionary:
		var result: Dictionary = {}
		for axis: String in ["x_bits", "y_bits", "z_bits"]:
			result[axis] = Float32.store_word(Float32.read_word(left[axis]) + Float32.read_word(right[axis]))
		return result

	static func _subtract(left: Dictionary, right: Dictionary) -> Dictionary:
		var result: Dictionary = {}
		for axis: String in ["x_bits", "y_bits", "z_bits"]:
			result[axis] = Float32.store_word(Float32.read_word(left[axis]) - Float32.read_word(right[axis]))
		return result

	static func _scale(value: Dictionary, scale: float) -> Dictionary:
		var result: Dictionary = {}
		for axis: String in ["x_bits", "y_bits", "z_bits"]:
			result[axis] = Float32.store_word(Float32.read_word(value[axis]) * scale)
		return result

	static func _cross(left: Dictionary, right: Dictionary) -> Dictionary:
		var lx: float = Float32.read_word(left.x_bits)
		var ly: float = Float32.read_word(left.y_bits)
		var lz: float = Float32.read_word(left.z_bits)
		var rx: float = Float32.read_word(right.x_bits)
		var ry: float = Float32.read_word(right.y_bits)
		var rz: float = Float32.read_word(right.z_bits)
		return _vector(f32(f32(ly * rz) - f32(lz * ry)), f32(f32(lz * rx) - f32(lx * rz)), f32(f32(lx * ry) - f32(ly * rx)))

	static func _normalize(value: Dictionary, fallback: Dictionary) -> Dictionary:
		var x: float = Float32.read_word(value.x_bits)
		var y: float = Float32.read_word(value.y_bits)
		var z: float = Float32.read_word(value.z_bits)
		var square: float = f32(f32(f32(x * x) + f32(y * y)) + f32(z * z))
		return _scale(value, f32(1.0 / f32(sqrt(square)))) if square > 0.0 else fallback.duplicate(true)

	static func _lerp(previous: float, current: float, alpha: float) -> float:
		var p: float = f32(previous)
		var c: float = f32(current)
		return f32(p + f32(f32(c - p) * alpha))

	static func _lerp_vector(previous: Dictionary, current: Dictionary, alpha: float) -> Dictionary:
		var result: Dictionary = {}
		for axis: String in ["x_bits", "y_bits", "z_bits"]:
			result[axis] = Float32.store_word(_lerp(Float32.read_word(previous[axis]), Float32.read_word(current[axis]), alpha))
		return result

	static func _distance_squared(previous: Dictionary, current: Dictionary) -> float:
		var delta: Dictionary = _subtract(current, previous)
		var dx: float = Float32.read_word(delta.x_bits)
		var dy: float = Float32.read_word(delta.y_bits)
		var dz: float = Float32.read_word(delta.z_bits)
		return f32(f32(f32(dx * dx) + f32(dy * dy)) + f32(dz * dz))

	static func _same_frame(left: Dictionary, right: Dictionary) -> bool:
		for field: String in ["event_frame", "pan_elapsed_ticks", "zoom_permille"]:
			if left[field] != right[field]: return false
		if left.attached_thing == null or right.attached_thing == null:
			return left.attached_thing == null and right.attached_thing == null
		return left.attached_thing.thing_id == right.attached_thing.thing_id \
			and _same_pose(left.attached_thing.pose, right.attached_thing.pose) \
			and _same_vector(left.attached_thing.pan_right, right.attached_thing.pan_right)

	static func _same_pose(left: Dictionary, right: Dictionary) -> bool:
		return _same_vector(left.position, right.position) and _same_vector(left.forward, right.forward) and _same_vector(left.up, right.up)

	static func _same_vector(left: Dictionary, right: Dictionary) -> bool:
		for axis: String in ["x_bits", "y_bits", "z_bits"]:
			var l: float = Float32.read_word(left[axis])
			var r: float = Float32.read_word(right[axis])
			# Generated C# value-record equality uses Single.Equals: NaNs compare
			# equal and either zero sign compares equal; retained words stay intact.
			if l != r and not (is_nan(l) and is_nan(r)):
				return false
		return true

	static func admit_vector(value: Variant) -> Dictionary:
		if not value is Dictionary:
			return failure("ArgumentException", "Camera vector requires three raw UInt32 words.")
		var copy: Dictionary = {}
		for axis: String in ["x_bits", "y_bits", "z_bits"]:
			if not word(value.get(axis)):
				return failure("ArgumentException", "Camera vector requires UInt32 " + axis + ".")
			copy[axis] = value[axis]
		return {"ok": true, "value": copy}

	static func admit_pose(value: Variant) -> Dictionary:
		if not value is Dictionary:
			return failure("ArgumentException", "Camera pose requires position, forward and up.")
		var copy: Dictionary = {}
		for key: String in ["position", "forward", "up"]:
			var vector: Dictionary = admit_vector(value.get(key))
			if not vector.ok: return vector
			copy[key] = vector.value
		return {"ok": true, "value": copy}

	static func admit_frame(value: Variant) -> Dictionary:
		if not value is Dictionary:
			return failure("ArgumentException", "Camera frame requires explicit fields.")
		var copy: Dictionary = {}
		for key: String in ["event_frame", "pan_elapsed_ticks", "zoom_permille"]:
			if not i32(value.get(key)):
				return failure("ArgumentException", "Camera frame requires Int32 " + key + ".")
			copy[key] = value[key]
		if not value.has("attached_thing"):
			return failure("ArgumentException", "Camera frame requires explicit nullable attached_thing.")
		copy.attached_thing = null
		var attached: Variant = value.attached_thing
		if attached != null:
			if not attached is Dictionary or not i32(attached.get("thing_id")):
				return failure("ArgumentException", "Attached thing requires Int32 thing_id.")
			var pose: Dictionary = admit_pose(attached.get("pose"))
			if not pose.ok: return pose
			var right: Dictionary = admit_vector(attached.get("pan_right"))
			if not right.ok: return right
			copy.attached_thing = {"thing_id": attached.thing_id, "pose": pose.value, "pan_right": right.value}
		return {"ok": true, "value": copy}

	static func hash_snapshot(value: Variant) -> Dictionary:
		if value == null:
			return failure("ArgumentNullException", "Camera snapshot is required.", "snapshot")
		if not value is Dictionary:
			return failure("ArgumentException", "Camera snapshot must be a value record.")
		var writer := Writer.new()
		writer.write_i32(1)
		for key: String in ["pan_duration_ticks", "control_view_handoff_tick", "reset_generation", "update_phase"]:
			if not i32(value.get(key)):
				return failure("ArgumentException", "Camera snapshot requires Int32 " + key + ".")
			writer.write_i32(value[key])
		for key: String in ["previous_frame", "current_frame"]:
			var frame: Dictionary = admit_frame(value.get(key))
			if not frame.ok: return frame
			_write_frame(writer, frame.value)
		for key: String in ["previous_pan_pose", "current_pan_pose"]:
			var pose: Dictionary = admit_pose(value.get(key))
			if not pose.ok: return pose
			_write_pose(writer, pose.value)
		if typeof(value.get("pan_update_scheduled")) != TYPE_BOOL:
			return failure("ArgumentException", "Camera snapshot requires Boolean pan_update_scheduled.")
		writer.write_bool(value.pan_update_scheduled)
		var encoded: Dictionary = writer.finish()
		if not encoded.ok:
			return failure("ArgumentException", encoded.error)
		var hash := HashingContext.new()
		if hash.start(HashingContext.HASH_SHA256) != OK or hash.update(encoded.bytes) != OK:
			return failure("InvalidOperationException", "Cannot hash camera snapshot.")
		return {"ok": true, "hex": hash.finish().hex_encode()}

	static func _write_frame(writer: Writer, frame: Dictionary) -> void:
		writer.write_i32(frame.event_frame)
		writer.write_i32(frame.pan_elapsed_ticks)
		writer.write_i32(frame.zoom_permille)
		writer.write_bool(frame.attached_thing != null)
		if frame.attached_thing != null:
			writer.write_i32(frame.attached_thing.thing_id)
			_write_pose(writer, frame.attached_thing.pose)
			_write_vector(writer, frame.attached_thing.pan_right)

	static func _write_pose(writer: Writer, pose: Dictionary) -> void:
		for key: String in ["position", "forward", "up"]:
			_write_vector(writer, pose[key])

	static func _write_vector(writer: Writer, vector: Dictionary) -> void:
		for key: String in ["x_bits", "y_bits", "z_bits"]:
			writer.write_u32(vector[key])

	static func f32(value: float) -> float:
		return Float32.store_float32(value)

	static func i32(value: Variant) -> bool:
		return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647

	static func word(value: Variant) -> bool:
		return typeof(value) == TYPE_INT and value >= 0 and value <= 0xffffffff

	static func failure(kind: String, message: String, parameter: String = "") -> Dictionary:
		return {"ok": false, "error_type": kind, "error": message, "parameter": parameter}
