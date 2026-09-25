# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Level100EngineViewpointState.cs adapter over the same two-slot Core owner.
## Slot 0 alone is bound; slot 1 stays empty. Viewport remains explicitly null.
## Near/far are supplied raw float words, preserving the measured product
## choice (0.1/700) without assuming source defaults or a host window size.
const EngineViewpoint = preload("res://Core/engine_viewpoint.gd")
const ATTACHED_PAN_CAMERA_IDENTITY: String = "level-100.attached-pan"


static func create(near_plane_bits: Variant, far_plane_bits: Variant) -> Dictionary:
	var created: Dictionary = EngineViewpoint.create(near_plane_bits, far_plane_bits)
	if not created.ok:
		return created
	return {"ok": true, "value": State.new(created.value)}


class State extends RefCounted:
	var _state: RefCounted

	func _init(state: RefCounted) -> void:
		_state = state
		_state.update_slot(0, {"camera_identity": ATTACHED_PAN_CAMERA_IDENTITY, "player_thing_identity": null, "viewport": null})
		_state.select_slot(0)

	func slot_count() -> int:
		return 2

	func selected_snapshot() -> Dictionary:
		return _state.selected_snapshot()

	func bind(camera: Variant) -> Dictionary:
		# The C# method reads only nullable AttachedThingId. Pose, zoom and HUD
		# are not this adapter's owner and intentionally have no validation here.
		if not camera is Dictionary or not camera.has("attached_thing_id"):
			return {"ok": false, "error_type": "ArgumentException", "error": "Camera requires explicit nullable attached_thing_id."}
		var identity: Variant = camera.attached_thing_id
		if identity != null and (typeof(identity) != TYPE_INT or identity < -2147483648 or identity > 2147483647):
			return {"ok": false, "error_type": "ArgumentException", "error": "Attached identity must be Int32 or null."}
		var slot: Dictionary = _state.get_slot(0).value
		slot.camera_identity = ATTACHED_PAN_CAMERA_IDENTITY
		slot.player_thing_identity = identity
		var updated: Dictionary = _state.update_slot(0, slot)
		if not updated.ok:
			return updated
		var selected: Dictionary = _state.select_slot(0)
		if not selected.ok:
			return selected
		return {"ok": true, "value": selected_snapshot()}

	func compute_hash() -> Dictionary:
		return _state.compute_hash()
