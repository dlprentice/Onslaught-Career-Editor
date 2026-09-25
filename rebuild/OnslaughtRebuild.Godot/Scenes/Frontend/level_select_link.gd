# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/quit_confirm_surface.gd"
## DrawLevelNodeGraph's actual trimmed segment. Endpoints use the authored
## outer rings, including local placement edits. The graph's original 640x480
## source frame stays separate from each pass's editable canvas/source pose.
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export_node_path("Control") var graph: NodePath = NodePath("../.."):
	set(value): graph = value; _refresh_connections()
@export_node_path("Control") var from_node: NodePath:
	set(value): from_node = value; _refresh_connections()
@export_node_path("Control") var to_node: NodePath:
	set(value): to_node = value; _refresh_connections()
@export var from_radius: float = 21.0:
	set(value): from_radius = value; queue_redraw()
@export var to_radius: float = 21.0:
	set(value): to_radius = value; queue_redraw()
@export var stroke_width: float = 1.6:
	set(value): stroke_width = value; queue_redraw()
@export var antialiased: bool = true:
	set(value): antialiased = value; queue_redraw()
var _watched: Array[Control] = []
var _rings: Array[Control] = []


func _ready() -> void:
	super._ready()
	_refresh_connections()


func drawing_parameters() -> Dictionary:
	var owner_frame: Control = get_node_or_null(graph) as Control
	var start: Control = get_node_or_null(from_node) as Control
	var finish: Control = get_node_or_null(to_node) as Control
	if owner_frame == null or start == null or finish == null or owner_frame.size.x <= 0.0 or owner_frame.size.y <= 0.0: return {}
	var a: Vector2 = _node_center(start, owner_frame)
	var b: Vector2 = _node_center(finish, owner_frame)
	var direction: Vector2 = (b - a).normalized()
	return {"from": a + direction * F.value(from_radius), "to": b - direction * F.value(to_radius),
		"ink": ink_color, "width": F.value(stroke_width), "antialiased": antialiased}


func _draw() -> void:
	if source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0: return
	var parameters: Dictionary = drawing_parameters()
	if parameters.is_empty(): return
	draw_set_transform_matrix(source_transform())
	draw_line(parameters.from, parameters.to, parameters.ink, parameters.width, parameters.antialiased)


static func _node_center(ring: Control, owner_frame: Control) -> Vector2:
	if ring.source_rect.size.x <= 0.0 or ring.source_rect.size.y <= 0.0: return Vector2.ZERO
	var local := Transform2D.IDENTITY
	var current: Node = ring
	while current is CanvasItem and current != owner_frame:
		local = current.get_transform() * local
		current = current.get_parent()
	if current != owner_frame: return Vector2.ZERO
	var ring_ratio: Vector2 = ring.size / ring.source_rect.size
	var graph_ratio: Vector2 = owner_frame.size / Vector2(640, 480)
	# Compose only authored local changes. Divide matching source ratios before
	# applying them to the center: an unedited ring stays exactly its binary32
	# source center under fractional page Size. A canvas/global inverse followed
	# by reapplication would introduce rounding absent from the original renderer.
	var pose := Transform2D(
		Vector2(local.x.x * (ring_ratio.x / graph_ratio.x), local.x.y * (ring_ratio.x / graph_ratio.y)),
		Vector2(local.y.x * (ring_ratio.y / graph_ratio.x), local.y.y * (ring_ratio.y / graph_ratio.y)),
		Vector2(local.origin.x / graph_ratio.x, local.origin.y / graph_ratio.y))
	return pose * (ring.source_anchor - ring.source_rect.position)


func _refresh_connections() -> void:
	queue_redraw()
	if not is_node_ready(): return
	for watched: Control in _watched:
		if is_instance_valid(watched) and watched.item_rect_changed.is_connected(queue_redraw): watched.item_rect_changed.disconnect(queue_redraw)
	for ring: Control in _rings:
		if is_instance_valid(ring) and ring.draw.is_connected(queue_redraw): ring.draw.disconnect(queue_redraw)
	_watched.clear()
	_rings.clear()
	var owner_frame: Control = get_node_or_null(graph) as Control
	for path: NodePath in [from_node, to_node]:
		var ring: Control = get_node_or_null(path) as Control
		if ring == null: continue
		if not _rings.has(ring):
			_rings.append(ring)
			ring.draw.connect(queue_redraw)
		var current: Node = ring
		while current is Control:
			if not _watched.has(current):
				_watched.append(current)
				current.item_rect_changed.connect(queue_redraw)
			if current == owner_frame: break
			current = current.get_parent()


func _validate_property(property: Dictionary) -> void:
	if property.name in ["rectangle", "texture"]: property.usage = PROPERTY_USAGE_NONE
