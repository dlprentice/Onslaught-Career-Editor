# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends RefCounted
## Released scenery hierarchy playback, formerly the animation driver at the
## bottom of Level100StaticWorldAsset.cs. One immutable configuration batch,
## one explicit update per rendered frame; no process/input/clock owner.
## This presentation state is never read back by Core or the mission.
## Bindings preserve their order and borrow nodes, but copy all track values.
## A malformed legacy track is read at its original update stage, not eagerly
## repaired or rejected by the transport's structural admission.

const F = preload("res://Scenes/Shared/retail_float32.gd")
const LONG_MIN: int = -9223372036854775807 - 1
const LONG_LIMIT: float = 9223372036854775808.0


static func create(frames_per_second: Variant, bindings: Variant) -> Dictionary:
	if not Owner._i32(frames_per_second):
		return Owner._failure("ArgumentException", "The animation rate requires an Int32 carrier.")
	if bindings == null:
		return Owner._failure("NullReferenceException", "The animation binding list is null.")
	if not bindings is Array:
		return Owner._failure("ArgumentException", "Animation bindings require an ordered Array.")
	var copied: Array = []
	for source: Variant in bindings:
		if source == null:
			copied.append(null)
			continue
		if not source is Dictionary or not source.has_all(["mesh", "part", "node"]):
			return Owner._failure("ArgumentException", "An animation binding is incomplete.")
		var mesh: Variant = source.mesh
		if mesh != null and (not mesh is Dictionary or not mesh.has_all(["playback", "loop_frame_count"]) or not Owner._i32(mesh.playback) or not Owner._i32(mesh.loop_frame_count)):
			return Owner._failure("ArgumentException", "An animation mesh requires exact playback and loop-count carriers.")
		var part: Variant = source.part
		if part != null:
			if not part is Dictionary or not part.has("frames") or (part.frames != null and not part.frames is Array):
				return Owner._failure("ArgumentException", "An animation part requires its frame-list carrier.")
			if part.frames != null:
				for frame: Variant in part.frames:
					var admission: Dictionary = Owner._admit_frame(frame)
					if not admission.ok:
						return admission
		if source.node != null and (typeof(source.node) != TYPE_OBJECT or not is_instance_valid(source.node) or not source.node is MeshInstance3D):
			return Owner._failure("ArgumentException", "An animation binding requires a live MeshInstance3D or null.")
		copied.append({"mesh": null if mesh == null else mesh.duplicate(true),
			"part": null if part == null else part.duplicate(true),
			"node": source.node, "has_node": source.node != null})
	return {"ok": true, "value": Owner.new(frames_per_second, copied)}


static func to_obj_space_transform(frame: Variant) -> Dictionary:
	var admission: Dictionary = Owner._admit_frame(frame)
	if not admission.ok:
		return admission
	return Owner._transform_admitted(frame)



class Owner extends RefCounted:
	var _frames_per_second: int
	var _bindings: Array
	var _shown_frames := PackedInt32Array()
	var _elapsed_seconds: float = 0.0


	func _init(frames_per_second: int, bindings: Array) -> void:
		_frames_per_second = frames_per_second
		_bindings = bindings
		# Original zero-filled Int32[]: even a different authored node pose is
		# retained until the first selected frame changes away from zero.
		_shown_frames.resize(bindings.size())


	func update(frame_delta: float) -> Dictionary:
		# The caller's old argument was Single; elapsed time is double.
		var delta: float = F.value(frame_delta)
		if not is_finite(delta) or delta <= 0.0:
			return {"ok": true}
		_elapsed_seconds += delta
		var lap: Dictionary = _longest_lap_seconds()
		if not lap.ok:
			return lap
		var period: float = lap.value
		if period > 0.0 and _elapsed_seconds >= period:
			_elapsed_seconds = fmod(_elapsed_seconds, period)
		for index: int in range(_bindings.size()):
			var binding: Dictionary = _bindings[index]
			var frame: int = _select_virtual_frame(binding.mesh)
			if frame == _shown_frames[index]:
				continue
			# This write precedes every part/frame/transform/node failure.
			_shown_frames[index] = frame
			if binding.part == null:
				return _failure("NullReferenceException", "The selected animation part is null.")
			var frames: Variant = binding.part.frames
			if frames == null:
				return _failure("NullReferenceException", "The selected animation frame list is null.")
			if frame < 0 or frame >= frames.size():
				return _failure("ArgumentOutOfRangeException", "The selected animation frame is outside its list.", "index")
			var converted: Dictionary = _transform_admitted(frames[frame])
			if not converted.ok:
				return converted
			# C# evaluates the complete RHS before its null/disposed setter.
			if not binding.has_node:
				return _failure("NullReferenceException", "The animated mesh node is null.")
			if not is_instance_valid(binding.node):
				return _failure("ObjectDisposedException", "The animated mesh node has been disposed.")
			binding.node.transform = converted.value
		return {"ok": true}


	func host_snapshot() -> Dictionary:
		var bytes := PackedByteArray()
		bytes.resize(8)
		bytes.encode_double(0, _elapsed_seconds)
		return {"frames_per_second": _frames_per_second, "binding_count": _bindings.size(),
			"elapsed_seconds_bits": bytes.decode_s64(0), "shown_frames": _shown_frames.duplicate()}


	func _longest_lap_seconds() -> Dictionary:
		var lap_frames: int = 1
		for binding: Variant in _bindings:
			if binding == null or binding.mesh == null:
				return _failure("NullReferenceException", "An animation binding or mesh is null.")
			var right: int = binding.mesh.loop_frame_count
			if right <= 0:
				continue
			var a: int = lap_frames
			var b: int = right
			while b != 0:
				if a == LONG_MIN and b == -1:
					return _failure("OverflowException", "Animation LCM remainder exceeds Int64.")
				var remainder: int = a % b
				a = b
				b = remainder
			if lap_frames == LONG_MIN and a == -1:
				return _failure("OverflowException", "Animation LCM quotient exceeds Int64.")
			@warning_ignore("integer_division")
			lap_frames = _multiply_wrapped(lap_frames / a, right)
		# Preserve IEEE division for the old unvalidated zero rate, avoiding a
		# GDScript division-by-zero abort. Positive/negative rates are unchanged.
		if _frames_per_second == 0:
			return {"ok": true, "value": INF if lap_frames > 0 else (-INF if lap_frames < 0 else NAN)}
		return {"ok": true, "value": float(lap_frames) / float(_frames_per_second)}


	func _select_virtual_frame(mesh: Dictionary) -> int:
		if mesh.playback != 0 or not is_finite(_elapsed_seconds) or _elapsed_seconds <= 0.0 or mesh.loop_frame_count < 1:
			return 0
		var frames: float = floor(_elapsed_seconds * float(_frames_per_second))
		# Int64.MaxValue converts to binary64 2^63 in the C# comparison.
		if frames <= 0.0 or frames >= LONG_LIMIT:
			return 0
		return int(frames) % int(mesh.loop_frame_count)


	static func _multiply_wrapped(left: int, right: int) -> int:
		# C# unchecked Int64 LCM multiplication. A four-limb product preserves
		# exact wrapped bits without an overflowing intermediate expression.
		# right is positive Int32; each partial product is less than 2^47.
		var result: int = 0
		var carry: int = 0
		for limb: int in range(4):
			var product: int = ((left >> (limb * 16)) & 0xffff) * right + carry
			result |= (product & 0xffff) << (limb * 16)
			carry = product >> 16
		return result

	static func _admit_frame(frame: Variant) -> Dictionary:
		if not frame is Dictionary or not frame.has_all(["basis_bits", "origin_bits"]):
			return _failure("ArgumentException", "A rigid frame requires basis and origin word carriers.")
		for field: String in ["basis_bits", "origin_bits"]:
			var words: Variant = frame[field]
			if words == null:
				continue
			if not words is PackedInt64Array:
				return _failure("ArgumentException", "Rigid frame words require PackedInt64Array UInt32 carriers.")
			for word: int in words:
				if word < 0 or word > 0xffffffff:
					return _failure("ArgumentException", "A rigid frame word is outside UInt32.")
		return {"ok": true}


	static func _transform_admitted(frame: Dictionary) -> Dictionary:
		# The original C# constructor reads basis columns 0/3/6, 1/4/7,
		# 2/5/8 before origin 0/1/2. Preserve its null/short-array priority.
		var basis: Variant = frame.basis_bits
		if basis == null:
			return _failure("NullReferenceException", "The rigid frame basis is null.")
		if basis.size() < 9:
			return _failure("IndexOutOfRangeException", "The rigid frame basis is shorter than nine words.")
		var origin: Variant = frame.origin_bits
		if origin == null:
			return _failure("NullReferenceException", "The rigid frame origin is null.")
		if origin.size() < 3:
			return _failure("IndexOutOfRangeException", "The rigid frame origin is shorter than three words.")
		# cmsh_static_preview.py:1084 emits OBJ rows (convention :901-902).
		# C# Basis(column0,column1,column2) transposes those rows into columns.
		# Godot's primitive Variant wire format stores the resulting basis ROWS,
		# followed by origin. Packing the original words directly therefore gives
		# the same matrix without quieting a signaling NaN through float64.
		# Protocol, not adapted implementation: pinned engine marshalls.cpp,
		# https://github.com/godotengine/godot/blob/8898c2b3d/core/io/marshalls.cpp
		# (TRANSFORM3D decode/encode). This fixed primitive never admits objects.
		var bytes := PackedByteArray()
		bytes.resize(52)
		bytes.encode_u32(0, TYPE_TRANSFORM3D)
		for index: int in range(9):
			bytes.encode_u32(4 + index * 4, basis[index])
		for index: int in range(3):
			bytes.encode_u32(40 + index * 4, origin[index])
		var transform: Variant = bytes_to_var(bytes)
		if not transform is Transform3D:
			return _failure("InvalidOperationException", "The pinned engine did not decode the rigid transform primitive.")
		return {"ok": true, "value": transform}


	static func _i32(value: Variant) -> bool:
		return value is int and value >= -2147483648 and value <= 2147483647


	static func _failure(type: String, message: String, parameter: String = "") -> Dictionary:
		return {"ok": false, "error_type": type, "error": message, "parameter": parameter}
