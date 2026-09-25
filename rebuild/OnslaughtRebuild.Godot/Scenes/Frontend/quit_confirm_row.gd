# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Full-width half-open choice target. The host owns all actual input/selection.
@export var source_rect: Rect2 = Rect2(110, 170, 420, 160)
@export var hit_rect: Rect2 = Rect2(120, 194, 400, 32)


func contains_design_point(point: Vector2, page: CanvasItem) -> bool:
	if size.x <= 0.0 or size.y <= 0.0 or source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0: return false
	var ratio: Vector2 = size / source_rect.size
	var source_to_design := Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio)
	# The host already converted its pointer to Stage/design space. Compose
	# only authored transforms through this page, then invert once: a second
	# Stage->canvas->Stage roundtrip moves half-open edges at fractional scales.
	var current: Node = self
	while current is CanvasItem:
		source_to_design = current.get_transform() * source_to_design
		if current == page:
			return source_to_design.determinant() != 0.0 and hit_rect.has_point(source_to_design.affine_inverse() * point)
		current = current.get_parent()
	return false
