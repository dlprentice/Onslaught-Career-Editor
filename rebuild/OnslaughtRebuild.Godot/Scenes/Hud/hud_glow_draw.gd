# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Hud/hud_draw.gd"
const Model = preload("res://Client/hud_presentation.gd")
# Device MODULATE2X 0xFF574737, draws 1163/1167 in three independent
# in-level captures. Both weapon arc shells carry this effective RGB.
const RETAIL_ARC_SHELL_DIFFUSE: int = 0xffae8e6e
const COMPASS_GAUGE_HEALTH_ANCHOR_DEGREES: float = 149.063
const COMPASS_GAUGE_ENERGY_ANCHOR_DEGREES: float = 225.0

func render(part: Part) -> void:
	begin(part)
	match int(part.part):
		9, 10, 11, 12: instrument_outline(int(part.part))
		13: dynamic_compass()
		14: influence_map()
		15:
			var emphasis: float = highlight(3)
			texture("battleline-outline", battle_line_rect(), Color(f(f(0.44) + emphasis), f(f(0.56) + f(emphasis * f(0.35))), f(0.69), 1))
		16:
			if int(state.socket) == 3:
				texture("forseti-icon", forseti_rect())
		17: objective_reticles()
	end()

func influence_map() -> void:
	var nodes: Array = Model.influence_nodes()
	if int(state.socket) != 2 or not hud.battle_line.has_influence_values or hud.battle_line.influence_permille.size() != nodes.size():
		return
	var minimum_x: int = int(nodes[0].position.x)
	var maximum_x: int = minimum_x
	var minimum_z: int = int(nodes[0].position.z)
	var maximum_z: int = minimum_z
	for node: Dictionary in nodes:
		minimum_x = mini(minimum_x, int(node.position.x))
		maximum_x = maxi(maximum_x, int(node.position.x))
		minimum_z = mini(minimum_z, int(node.position.z))
		maximum_z = maxi(maximum_z, int(node.position.z))
	var center: Vector2 = battle_line_rect().position + Vector2(f(49.08), f(48.46))
	for index: int in range(nodes.size()):
		var node: Dictionary = nodes[index]
		var x: float = f(center.x + f(f(f(f(f(float(node.position.x)) - f(float(minimum_x))) / f(float(maximum_x - minimum_x))) - 0.5) * 55.0))
		var y: float = f(center.y + f(f(0.5 - f(f(f(float(node.position.z)) - f(float(minimum_z))) / f(float(maximum_z - minimum_z)))) * 55.0))
		var value: int = int(hud.battle_line.influence_permille[index])
		var tint: Color = retail_color(0xff5050af if value > 0 else (0xffaf0808 if value < 0 else 0xff606060))
		tint.a = f(f(0.35) + f(f(f(0.65) * absf(float(value))) / 1000.0))
		texture("battleline-marker", Rect2(Vector2(x, y) - Vector2(8, 8), Vector2(16, 16)), tint)

func objective_reticles() -> void:
	for objective: Dictionary in hud.objectives:
		var x: Variant = world_marker_x(objective.position_millimeters)
		if x != null:
			texture("screen-marker", Rect2(Vector2(float(x), CENTER.y) - Vector2(32, 32), Vector2(64, 64)), Color(1, 0.92, 0.08, 1))

func instrument_outline(part: int) -> void:
	var radar: float = highlight(4)
	var weapon: float = highlight(5)
	match part:
		9:
			texture("radar-outline", Rect2(17, DESIGN_HEIGHT - 112.0, 128, 128), Color(f(f(0.44) + radar), f(f(0.56) + f(radar * f(0.35))), f(0.69), 1))
		10:
			texture("weapon-outline", Rect2(9, DESIGN_HEIGHT - 141.0, 128, 128), Color(0.50, 1, 0.25, 1) if weapon > 0 else retail_color(RETAIL_ARC_SHELL_DIFFUSE))
		11:
			region("weapon-outline", right_weapon_rect(), Rect2(0, 0, -128, 128), retail_color(RETAIL_ARC_SHELL_DIFFUSE))
		12:
			if hud.weapon.selection_panel_visible == true and hud.weapon.selection_slot != null and hud.weapon.selection_slot != 0:
				texture("guns-outline", guns_rect(), retail_color(0xff6f8faf))

func dynamic_compass() -> void:
	var color: Color = compass_color()
	segmented_ring(CENTER, 98.0, 50, 6.0, 0.0, 1.0, color)
	var health: float = clampf(f(f(float(frame.hull)) / f(float(state.maximum_hull))), 0, 1)
	var energy: float = clampf(f(f(float(frame.energy)) / f(float(state.maximum_energy))), 0, 1)
	gauge_arcs(false)
	dial_north(color)
	for threat: Dictionary in hud.threats:
		var angle: float = f(f(float(threat.relative_yaw_micro_rad)) / 1000000.0)
		var alpha: float = clampf(f(f(float(threat.ticks_remaining)) / 600.0), 0, 1)
		rotated("threat-flash", CENTER + Vector2(sinf(angle), -cosf(angle)) * f(111.5), Vector2(32, 32), angle, Color(1, 1, 1, alpha))
	for flash: Dictionary in hud.damage_flashes:
		var angle: float = f(f(float(flash.relative_yaw_micro_rad)) / 1000000.0)
		var fade: float = clampf(f(f(float(flash.ticks_remaining)) / f(float(state.damage_flash_lifetime_ticks))), 0, 1)
		rotated("damage-flash", CENTER + Vector2(sinf(angle), -cosf(angle)) * 96.0, Vector2(128, 32), angle, Color(fade, fade, fade, 1))
	gauge_needle(degrees_to_radians(f(f(COMPASS_GAUGE_HEALTH_ANCHOR_DEGREES) - f(health * 90.0))), retail_color(0xff3e3e3e))
	gauge_needle(degrees_to_radians(f(COMPASS_GAUGE_HEALTH_ANCHOR_DEGREES)), retail_color(0xff1e1e1e))
	gauge_needle(degrees_to_radians(f(COMPASS_GAUGE_ENERGY_ANCHOR_DEGREES + f(energy * 135.0))), retail_color(0xff1e1e1e))
	gauge_needle(degrees_to_radians(COMPASS_GAUGE_ENERGY_ANCHOR_DEGREES), retail_color(0xff1e1e1e))

static func degrees_to_radians(degrees: float) -> float:
	# Godot C# Mathf.DegToRad multiplies by its float32 DegToRadConst.
	return f(degrees * f(PI32 / 180.0))

func gauge_needle(angle: float, tint: Color) -> void:
	rotated("bar-line", CENTER + Vector2(sinf(angle), -cosf(angle)) * 110.0, Vector2(16, 64), angle, tint)

func dial_north(color: Color) -> void:
	var heading: float = f(f(float(frame.facing_yaw_micro_rad)) / 1000000.0)
	var angular_step: float = f(TAU32 / 512.0)
	var radial_width: float = f(6.0 / 32.0)
	for y: int in range(16):
		var source_v: float = float(15 + y) + 0.5
		# Mathf.Lerp(from,to,weight) == from + (to-from)*weight, float32.
		var radius: float = f(101.0 + f(f(95.0 - 101.0) * f(source_v / 32.0)))
		for x: int in range(16):
			var palette: int = assets.dial[y * 16 + x]
			if palette == 0:
				continue
			var first: float = f(heading + f(f(float(x) - 8.0) * angular_step))
			var second: float = f(first + angular_step)
			var tint: Color = color
			tint.a = f(tint.a * f(float(palette) / 15.0))
			target.draw_line(CENTER + Vector2(sinf(first), -cosf(first)) * radius,
				CENTER + Vector2(sinf(second), -cosf(second)) * radius, tint, radial_width, true)
