# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Hud/hud_draw.gd"
const Model = preload("res://Client/hud_presentation.gd")
# Decoded device diffuse bytes and the original closed form, retained exactly.
# local-lab/PORTRAIT-BATTLELINE-FIELD-2026-07-26.md; promote-gap noise band:
# local-lab/agent-notes-2026-07-27/inlevel-hud-coordinates.md section 6.
const CIRCLE_DARKENER_ALPHA: float = 127.0 / 255.0
const PORTRAIT_DRAW_COUNT: int = 6
const PORTRAIT_DRAW_ALPHA: float = 64.0 / 255.0
const PORTRAIT_COMPOSITE_ALPHA: float = 0.8234043
const MESSAGE_NOISE_ALPHA: float = 66.0 / 255.0
const MESSAGE_NOISE_ALPHA_WITHOUT_PORTRAIT: float = 112.0 / 255.0

func render(part: Part) -> void:
	begin(part)
	match int(part.part):
		0: compass_base()
		1:
			weapon_resource(false)
			weapon_icon()
		2: scanner_contacts()
		3: weapon_resource(true)
		4: weapon_selection()
		5: battle_line()
		6:
			if int(frame.mission_tick) >= int(state.message_box_allowed_tick):
				message_frame()
		7: offscreen_objectives()
		8: crosshair_target()
	end()

func compass_base() -> void:
	segmented_ring(CENTER, 98.0, 50, 6.0, 0.0, 1.0, compass_color())
	gauge_arcs(true)
	for objective: Dictionary in hud.objectives:
		var relative: float = relative_yaw(objective.position_millimeters)
		var position: Vector2 = CENTER + Vector2(f(sinf(relative) * 98.0), f(-cosf(relative) * 98.0))
		texture("compass-objective-marker", Rect2(position - Vector2(8, 8), Vector2(16, 16)), Color(1, f(0.91), f(0.08), 1))

func scanner_contacts() -> void:
	var center := Vector2(68, 417)
	var yaw: float = f(f(float(frame.facing_yaw_micro_rad)) / 1000000.0)
	var blobs: Array[String] = ["scanner-blob-small", "scanner-blob-medium", "scanner-blob-large", "scanner-blob-repair-pad"]
	for contact: Dictionary in hud.contacts:
		if not contact.on_scanner:
			continue
		var placement: Dictionary = Model.scanner_place(
			f(f(float(i32(int(contact.position.x) - int(frame.player_position.x)))) / 1000.0),
			f(f(float(i32(int(contact.position.z) - int(frame.player_position.z)))) / 1000.0), yaw)
		if not placement.drawn:
			continue
		var offset := Vector2(placement.offset_x, placement.offset_y)
		texture(blobs[clampi(int(contact.size), 0, blobs.size() - 1)], Rect2(center + offset - Vector2(8, 8), Vector2(16, 16)), contact_color(contact, placement.alpha))
	for objective: Dictionary in hud.objectives:
		var placement: Dictionary = Model.scanner_place_objective(
			f(f(float(i32(int(objective.position_millimeters.x) - int(frame.player_position.x)))) / 1000.0),
			f(f(float(i32(int(objective.position_millimeters.z) - int(frame.player_position.z)))) / 1000.0), yaw)
		texture("scanner-blob-medium", Rect2(center + Vector2(placement.offset_x, placement.offset_y) - Vector2(8, 8), Vector2(16, 16)), retail_color(0xffffff00))
	var north: Vector2 = Vector2(65, DESIGN_HEIGHT - 64.0) + Vector2(f(sinf(yaw) * 45.0), f(-cosf(yaw) * 45.0))
	rotated("radio-north", north, Vector2(32, 32), yaw, retail_color(0xff5f7fff))

func contact_color(contact: Dictionary, alpha: int) -> Color:
	return retail_color((clampi(alpha, 0, 255) << 24) | int(Model.scanner_tint_rgb(contact.allegiance)))

func resource_fraction() -> Variant:
	var weapon: Dictionary = hud.weapon
	return clampf(f(f(float(i32(1000 - int(weapon.pulse_heat_permille)))) / 1000.0), 0, 1) if weapon.selected_weapon == 1 and weapon.pulse_heat_permille != null else null

func resource_tint(measured: Color) -> Color:
	# Original TicksPerSecond/5 half-cycle; source integer division order.
	@warning_ignore("integer_division")
	var cycle: int = int(frame.tick) / (int(state.ticks_per_second) / 5)
	return Color(1, f(0.15), f(0.05), measured.a) if hud.weapon.pulse_cannon_overheated == true and cycle % 2 == 0 else measured

func weapon_resource(right: bool) -> void:
	var fraction: Variant = resource_fraction()
	if fraction == null:
		return
	var rect: Rect2 = right_weapon_rect() if right else Rect2(9, DESIGN_HEIGHT - 141.0, 128, 128)
	var width: float = f(rect.size.x * float(fraction))
	if right:
		region("weapon-fill", Rect2(f(rect.end.x - width), rect.position.y, width, rect.size.y), Rect2(width, 0, -width, 128), resource_tint(retail_color(0xcc7efe3e)))
	else:
		region("weapon-fill", Rect2(rect.position.x, rect.position.y, width, rect.size.y), Rect2(0, 0, width, 128), resource_tint(retail_color(0x7f7efe3e)))

func weapon_icon() -> void:
	var weapon: Dictionary = hud.weapon
	var icon: String = ""
	if weapon.selected_weapon == 1 and weapon.pulse_cannon_enabled:
		icon = "weapon-plasma-cannon"
	elif weapon.selected_weapon == 2 and weapon.vulcan_cannon_enabled:
		icon = "weapon-vulcan-cannon"
	if not icon.is_empty():
		texture(icon, Rect2(Vector2(9, DESIGN_HEIGHT - 141.0) + Vector2(32, 30), Vector2(64, 64)))

func weapon_selection() -> void:
	var weapon: Dictionary = hud.weapon
	if weapon.selection_panel_visible != true or weapon.selection_slot == null or weapon.selection_slot == 0:
		return
	texture("guns-darken", guns_rect(), retail_color(0x78000000))
	var selected: Dictionary = {1: "guns-side", 2: "guns-front", 3: "guns-top"}
	if selected.has(weapon.selection_slot):
		texture(selected[weapon.selection_slot], guns_rect(), Color(0.50, 0.75, 0.88, 0.80))

func battle_line() -> void:
	texture("circle-darkener", battle_line_rect(), Color(1, 1, 1, f(CIRCLE_DARKENER_ALPHA)))
	if int(state.socket) != 1:
		return
	var drawn: bool = false
	var speakers: Dictionary = {1508464: 0, 10565784: 1, 919601: 2}
	if state.speaker != null and state.portrait_pose != null and speakers.has(state.speaker):
		target.draw_texture_rect(assets.portraits[speakers[state.speaker]][state.portrait_pose], portrait_rect(), false, Color(1, 1, 1, f(PORTRAIT_COMPOSITE_ALPHA)))
		drawn = true
	target.draw_texture_rect(assets.noise_phases[int(state.noise_phase) % assets.noise_phases.size()], portrait_rect(), false,
		Color(1, 1, 1, f(MESSAGE_NOISE_ALPHA if drawn else MESSAGE_NOISE_ALPHA_WITHOUT_PORTRAIT)))

func message_frame() -> void:
	var frame_width: float = 252.0
	var piece_height: float = 120.0
	var inner_width: float = 60.0
	var tint: Color = retail_color(0x90000000)
	var center_x: float = (DESIGN_WIDTH * 0.5) + 22.0
	var center_y: float = DESIGN_HEIGHT - 41.0
	var left: float = center_x - frame_width * 0.5
	var right: float = center_x + frame_width * 0.5
	var top: float = center_y - piece_height * 0.5
	texture("objective-left", Rect2(left - piece_height * 0.5, top, piece_height, piece_height))
	texture("objective-inner-left", Rect2(left - inner_width, top, inner_width, piece_height), tint)
	texture("objective-right", Rect2(right - piece_height * 0.5, top, piece_height, piece_height))
	texture("objective-inner-right", Rect2(right, top, inner_width, piece_height), tint)
	var remaining: float = frame_width
	var x: float = left
	while remaining > 0.0:
		var width: float = minf(inner_width, remaining)
		region("objective-inner-centre", Rect2(x, top, width, piece_height), Rect2(0, 0, f(64.0 * f(width / inner_width)), 128), tint)
		x = f(x + width)
		remaining = f(remaining - width)

func offscreen_objectives() -> void:
	for objective: Dictionary in hud.objectives:
		var position: Dictionary = objective.position_millimeters
		if world_marker_x(position) != null:
			continue
		var side: float = signf(relative_yaw(position))
		rotated("offscreen-arrow", Vector2(28.0 if side < 0 else DESIGN_WIDTH - 28.0, CENTER.y), Vector2(32, 32),
			f(-PI32 * 0.5) if side < 0 else f(PI32 * 0.5), Color(1, 0.92, 0.08, 1))

func crosshair_target() -> void:
	if hud.target == null:
		return
	var target_state: Dictionary = hud.target
	var contact: Variant = null
	for candidate: Dictionary in hud.contacts:
		if candidate.id == target_state.contact_id:
			contact = candidate
			break
	var classification: String = "crosshair-friend" if contact != null and contact.allegiance == 0 else "crosshair-enemy"
	var tint: Color = Color.WHITE if contact == null else contact_color(contact, 255)
	texture(classification, Rect2(CENTER - Vector2(32, 32), Vector2(64, 64)), tint)
	texture("target-sighted", Rect2(CENTER - Vector2(32, 32), Vector2(64, 64)), Color(1, 1, 1, clampf(f(f(float(target_state.lock_permille)) / 1000.0), 0, 1)))
	var predicted: float = relative_yaw(target_state.predicted_position)
	var x: float = clampf(f(CENTER.x + f(f(predicted / f(1.05)) * f(DESIGN_WIDTH * f(0.42)))), 32.0, DESIGN_WIDTH - 32.0)
	texture("crosshair-predictor", Rect2(Vector2(x, CENTER.y) - Vector2(32, 32), Vector2(64, 64)), tint)
