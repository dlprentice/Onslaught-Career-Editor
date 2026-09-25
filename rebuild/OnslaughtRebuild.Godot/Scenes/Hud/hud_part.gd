# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## An authored, editable rectangle for one production HUD drawing law.
enum Content { COMPASS_BASE, LEFT_WEAPON, SCANNER_CONTACTS, RIGHT_WEAPON,
	WEAPON_SELECTION, BATTLE_LINE, MESSAGE_FRAME, OFFSCREEN_OBJECTIVES,
	CROSSHAIR_TARGET, SCANNER_OUTLINE, LEFT_WEAPON_OUTLINE, RIGHT_WEAPON_OUTLINE,
	WEAPON_SELECTION_OUTLINE, COMPASS_GLOW, INFLUENCE_MAP, BATTLE_LINE_OUTLINE,
	FORSETI, OBJECTIVE_RETICLES, MESSAGE_TEXT, HELP_TEXT, WEAPON_AMMO, TERMINAL }
@export var part: Content = Content.COMPASS_BASE:
	set(value):
		part = value
		queue_redraw()
@export var source_rect := Rect2(0, 0, 640, 480):
	set(value):
		source_rect = value
		queue_redraw()
var _hud: Node

func _validate_property(property: Dictionary) -> void:
	if property.name in ["part", "source_rect"]:
		property.usage = int(property.usage) | PROPERTY_USAGE_READ_ONLY

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)
	var ancestor: Node = get_parent()
	while ancestor != null:
		if ancestor.has_method("draw_part"):
			_hud = ancestor
			break
		ancestor = ancestor.get_parent()

func _draw() -> void:
	if is_instance_valid(_hud):
		_hud.draw_part(self)

func retail_to_local_transform() -> Transform2D:
	var ratio := Vector2(size.x / source_rect.size.x if source_rect.size.x > 0 else 1.0,
		size.y / source_rect.size.y if source_rect.size.y > 0 else 1.0)
	return Transform2D(Vector2(ratio.x, 0), Vector2(0, ratio.y), -source_rect.position * ratio)
