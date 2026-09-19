# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure EngineViewpointState.cs two-slot envelope. Source shape:
## references/Onslaught/engine.h:13–16,66–154 and engine.cpp:304–338.
## Retail inline ABI/layout remains unknown. Near/far are supplied explicitly;
## there is no host-window viewport or revived source-default far plane.
## Float fields are raw UInt32 words, retaining even nonfinite payloads without
## converting them through Godot float arithmetic. Camera identity is UTF-16.
const Text = preload("res://Core/canonical_json_string.gd")
const Writer = preload("res://Core/canonical_binary_writer.gd")


static func create(near_plane_bits: Variant, far_plane_bits: Variant) -> Dictionary:
	if typeof(near_plane_bits) != TYPE_INT or near_plane_bits < 0 or near_plane_bits > 0xffffffff \
			or typeof(far_plane_bits) != TYPE_INT or far_plane_bits < 0 or far_plane_bits > 0xffffffff:
		return {"ok": false, "error_type": "ArgumentException", "error": "Viewpoint depth inputs must be raw UInt32 float words."}
	return {"ok": true, "value": State.new(near_plane_bits, far_plane_bits)}


class State extends RefCounted:
	var _slots: Array[Dictionary]
	var _near_bits: int
	var _far_bits: int
	var _selected: int = 0
	var _current: Variant = null

	func _init(near_bits: int, far_bits: int) -> void:
		_near_bits = near_bits
		_far_bits = far_bits
		_slots = [_empty_slot(), _empty_slot()]

	func get_slot(slot: Variant) -> Dictionary:
		if not _slot_index(slot):
			return _bad_slot()
		return {"ok": true, "value": _slots[slot].duplicate(true)}

	func update_slot(slot: Variant, value: Variant) -> Dictionary:
		if not _slot_index(slot):
			return _bad_slot()
		var admitted: Dictionary = _admit_slot(value)
		if not admitted.ok:
			return admitted
		_slots[slot] = admitted.value
		return {"ok": true}

	func select_slot(slot: Variant) -> Dictionary:
		if not _slot_index(slot):
			return _bad_slot()
		_selected = slot
		_current = _copy_viewport(_slots[slot].viewport)
		return {"ok": true}

	func reset() -> void:
		_slots = [_empty_slot(), _empty_slot()]
		_selected = 0
		_current = null

	func selected_snapshot() -> Dictionary:
		return {"selected_slot": _selected, "selected_slot_state": _slots[_selected].duplicate(true),
			"current_viewport": _copy_viewport(_current), "near_plane_bits": _near_bits, "far_plane_bits": _far_bits}

	func snapshot() -> Dictionary:
		return {"slot_count": 2, "slots": _slots.duplicate(true), "selected": selected_snapshot()}

	func compute_hash() -> Dictionary:
		var writer := Writer.new()
		writer.write_i32(1)
		writer.write_i32(2)
		writer.write_u32(_near_bits)
		writer.write_u32(_far_bits)
		writer.write_i32(_selected)
		for slot: Dictionary in _slots:
			writer.write_bool(slot.camera_identity != null)
			if slot.camera_identity != null:
				writer.write_string(slot.camera_identity)
			writer.write_bool(slot.player_thing_identity != null)
			if slot.player_thing_identity != null:
				writer.write_i32(slot.player_thing_identity)
			_write_viewport(writer, slot.viewport)
		_write_viewport(writer, _current)
		var encoded: Dictionary = writer.finish()
		if not encoded.ok:
			return _failure(encoded.error)
		var hash := HashingContext.new()
		if hash.start(HashingContext.HASH_SHA256) != OK or hash.update(encoded.bytes) != OK:
			return _failure("Cannot hash viewpoint state.")
		return {"ok": true, "hex": hash.finish().hex_encode()}

	static func _write_viewport(writer: Writer, viewport: Variant) -> void:
		writer.write_bool(viewport != null)
		if viewport == null:
			return
		for name: String in ["width", "height", "x", "y"]:
			writer.write_i32(viewport[name])
		writer.write_u32(viewport.min_depth_bits)
		writer.write_u32(viewport.max_depth_bits)

	static func _admit_slot(value: Variant) -> Dictionary:
		if not value is Dictionary or not value.has("camera_identity") \
				or not value.has("player_thing_identity") or not value.has("viewport"):
			return _failure("Slot requires its three explicit nullable fields.")
		var camera: Dictionary = Text.units(value.camera_identity)
		if not camera.ok:
			return _failure(camera.error)
		if value.player_thing_identity != null and not _i32(value.player_thing_identity):
			return _failure("Player identity must be an Int32 or null.")
		var viewport: Variant = value.viewport
		if viewport != null:
			if not viewport is Dictionary:
				return _failure("Viewport must be a record or null.")
			for name: String in ["width", "height", "x", "y"]:
				if not _i32(viewport.get(name)):
					return _failure("Viewport requires Int32 " + name + ".")
			for name: String in ["min_depth_bits", "max_depth_bits"]:
				var word: Variant = viewport.get(name)
				if typeof(word) != TYPE_INT or word < 0 or word > 0xffffffff:
					return _failure("Viewport requires raw UInt32 " + name + ".")
			viewport = {"width": viewport.width, "height": viewport.height, "x": viewport.x, "y": viewport.y,
				"min_depth_bits": viewport.min_depth_bits, "max_depth_bits": viewport.max_depth_bits}
		return {"ok": true, "value": {"camera_identity": camera.value,
			"player_thing_identity": value.player_thing_identity, "viewport": viewport}}

	static func _empty_slot() -> Dictionary:
		return {"camera_identity": null, "player_thing_identity": null, "viewport": null}

	static func _copy_viewport(value: Variant) -> Variant:
		return null if value == null else value.duplicate(true)

	static func _i32(value: Variant) -> bool:
		return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647

	static func _slot_index(value: Variant) -> bool:
		return typeof(value) == TYPE_INT and value >= 0 and value < 2

	static func _bad_slot() -> Dictionary:
		return {"ok": false, "error_type": "ArgumentOutOfRangeException", "error": "Viewpoint slot must be 0 or 1."}

	static func _failure(message: String) -> Dictionary:
		return {"ok": false, "error_type": "ArgumentException", "error": message}
