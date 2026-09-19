# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Temporary composition boundary for the managed world renderer. These two
## native owners alone carry live camera state. One host call advances the
## supplied world pair; one later call samples and binds its selected viewpoint.
## No scene objects, elapsed clock, viewport dimensions or input are read here.
const Attached = preload("res://Client/attached_pan_camera.gd")
const Viewpoint = preload("res://Client/level100_engine_viewpoint.gd")
var _camera: RefCounted
var _viewpoint: RefCounted


func configure(duration: Variant, lead: Variant, near_bits: Variant, far_bits: Variant) -> Dictionary:
	if _camera != null:
		return _not_ready("The world camera is already configured.")
	var camera: Dictionary = Attached.create(duration, lead)
	if not camera.ok:
		return camera
	var viewpoint: Dictionary = Viewpoint.create(near_bits, far_bits)
	if not viewpoint.ok:
		return viewpoint
	_camera = camera.value
	_viewpoint = viewpoint.value
	return {"ok": true}


func advance(previous: Variant, current: Variant) -> Dictionary:
	if _camera == null:
		return _not_ready()
	return _camera.advance(previous, current)


func sample_and_bind(alpha_bits: Variant) -> Dictionary:
	if _camera == null:
		return _not_ready()
	var sampled: Dictionary = _camera.sample(alpha_bits)
	if not sampled.ok:
		return sampled
	var bound: Dictionary = _viewpoint.bind(sampled.value)
	if not bound.ok:
		return bound
	return {"ok": true, "value": {"camera": sampled.value, "viewpoint": bound.value}}


func current_snapshot() -> Dictionary:
	return _not_ready() if _camera == null else _camera.current_snapshot()


func selected_snapshot() -> Dictionary:
	return _not_ready() if _viewpoint == null else {"ok": true, "value": _viewpoint.selected_snapshot()}


func camera_hash() -> Dictionary:
	if _camera == null:
		return _not_ready()
	var current: Dictionary = _camera.current_snapshot()
	return current if not current.ok else Attached.compute_hash(current.value)


func viewpoint_hash() -> Dictionary:
	return _not_ready() if _viewpoint == null else _viewpoint.compute_hash()


static func _not_ready(reason: String = "The world camera has not been configured.") -> Dictionary:
	return {"ok": false, "error_type": "InvalidOperationException", "error": reason, "parameter": ""}
