# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Design-space target only. The host retains all pointer and navigation input.
@export var source_rect: Rect2 = Rect2(128, 408, 403, 44)
@export var hit_rect: Rect2 = Rect2(128, 408, 403, 44)


func source_transform() -> Transform2D:
	var ratio: Vector2 = size / source_rect.size
	return Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio)


func contains_design_point(point: Vector2, page: CanvasItem) -> bool:
	return contains(self, source_rect, hit_rect, point, page)


static func contains(control: Control, source: Rect2, target: Rect2, point: Vector2, page: CanvasItem) -> bool:
	if control.size.x <= 0.0 or control.size.y <= 0.0 or source.size.x <= 0.0 or source.size.y <= 0.0: return false
	var ratio: Vector2 = control.size / source.size
	var source_to_design := Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source.position * ratio)
	# The incoming point is already in Stage/design space. Include authored
	# page/section/pass transforms, but never introduce a second Stage roundtrip.
	var current: Node = control
	while current is CanvasItem:
		source_to_design = current.get_transform() * source_to_design
		if current == page:
			return source_to_design.determinant() != 0.0 and target.has_point(source_to_design.affine_inverse() * point)
		current = current.get_parent()
	return false
