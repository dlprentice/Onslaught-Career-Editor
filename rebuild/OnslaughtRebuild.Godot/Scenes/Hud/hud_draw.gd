# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends RefCounted
## Drawing services used by the 22 authored production Controls. Their ordinary
## transforms own layout; these laws operate only in the released 640×480 stage.
const Part = preload("res://Scenes/Hud/hud_part.gd")
const Assets = preload("res://Scenes/Hud/hud_assets.gd")
const F32 = preload("res://Scenes/Shared/retail_float32.gd")
const DESIGN_WIDTH: float = 640.0
const DESIGN_HEIGHT: float = 480.0
const CENTER := Vector2(320, 240)
const PI32: float = 3.1415927410125732
const TAU32: float = 6.2831854820251465
const GAUGE_HEALTH_BLEND_ALPHA: float = 0.178
const GAUGE_ENERGY_BLEND_ALPHA: float = 0.225
# Achromatic ring-1 texel 0x2444, CDXCompass__BuildByteSpriteOverlayTexture.
# local-lab/HUD-LANE-RECOVERED-2026-07-29.md sections 1–2. One premultiplied
# retail draw is represented by existing mix/add halves, K=P/(1+a).
const COMPASS_BASE_RING_TEXEL_ALPHA: float = 2.0 / 15.0
const COMPASS_BASE_RING_TEXEL_PREMULTIPLIED_RGB: float = 4.0 / 15.0
var target: Part
var assets: Assets
var state: Dictionary
var frame: Dictionary
var hud: Dictionary

func bind(source: Assets, snapshot: Dictionary) -> void:
	assets = source
	state = snapshot
	frame = snapshot.frame
	hud = snapshot.hud

func begin(part: Part) -> void:
	target = part
	set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

func end() -> void:
	set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	target = null

func set_transform(offset: Vector2, rotation: float, scale: Vector2) -> void:
	target.draw_set_transform_matrix(target.retail_to_local_transform() * Transform2D(rotation, offset).scaled_local(scale))

func texture(name: String, rect: Rect2, color: Color = Color.WHITE) -> void:
	target.draw_texture_rect(assets.pages[name], rect, false, color)

func region(name: String, rect: Rect2, source: Rect2, color: Color) -> void:
	target.draw_texture_rect_region(assets.pages[name], rect, source, color)

func rotated(name: String, center: Vector2, size: Vector2, angle: float, color: Color) -> void:
	set_transform(center, angle, Vector2.ONE)
	texture(name, Rect2(-size * 0.5, size), color)
	set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

func segmented_ring(center: Vector2, radius: float, segments: int, width: float,
		start_turn: float, turn_length: float, color: Color) -> void:
	var first: int = clampi(int(floor(f(start_turn * segments))), 0, segments)
	var last: int = clampi(int(ceil(f(f(start_turn + turn_length) * segments))), first, segments)
	if last <= first:
		return
	var points := PackedVector2Array()
	for index: int in range(first, last + 1):
		var turn: float = f(f(float(index) / segments) * TAU32)
		points.append(center + Vector2(sinf(turn), -cosf(turn)) * radius)
	# A joined polyline preserves the original continuous retail strip (50/40
	# segments); independent anti-aliased lines introduce interior seams.
	target.draw_polyline(points, color, width, true)

func gauge_arcs(alpha_half: bool) -> void:
	var health: float = clampf(f(f(float(frame.hull)) / f(float(state.maximum_hull))), 0, 1)
	var energy: float = clampf(f(f(float(frame.energy)) / f(float(state.maximum_energy))), 0, 1)
	var health_paint := Color(f(f(f(f(1.0 - health) * f(61.6)) / 255.0) + f(f(7.9) / 255.0)),
		f(f(health * f(61.6)) / 255.0), f(f(7.6) / 255.0))
	var energy_paint := Color(f(f(12.8) / 255.0), f(f(6.4) / 255.0), f(65.0 / 255.0))
	health_paint.a = f(GAUGE_HEALTH_BLEND_ALPHA) if alpha_half else f(1.0 + highlight(0))
	energy_paint.a = f(GAUGE_ENERGY_BLEND_ALPHA) if alpha_half else f(1.0 + highlight(1))
	segmented_ring(CENTER, 86.0, 50, 12.0, f(f(150.0 - f(health * 90.0)) / 360.0), f(health * f(90.0 / 360.0)), health_paint)
	segmented_ring(CENTER, 86.0, 40, 12.0, f(225.0 / 360.0), f(energy * f(135.0 / 360.0)), energy_paint)

func highlight(part: int) -> float:
	if not hud.emphasized_parts.has(part):
		return 0.0
	return f(f(0.22) + f(f(0.18) * f(sinf(f(f(float(frame.tick)) * f(0.45))) + 1.0)))

func compass_color() -> Color:
	var emphasis: float = highlight(2)
	var paint: float = f(f(COMPASS_BASE_RING_TEXEL_PREMULTIPLIED_RGB) / f(1.0 + f(COMPASS_BASE_RING_TEXEL_ALPHA)))
	var value: float = f(paint + emphasis)
	return Color(value, value, value, f(f(COMPASS_BASE_RING_TEXEL_ALPHA) + f(emphasis * f(0.4))))

func relative_yaw(position: Dictionary) -> float:
	# C# computes the integer delta before storing the float. Do not first
	# round large world positions independently to float32.
	var dx: float = f(float(i32(int(position.x) - int(frame.player_position.x))))
	var dz: float = f(float(i32(int(position.z) - int(frame.player_position.z))))
	var desired: float = Vector2(dz, -dx).angle()
	var angle: float = f(f(f(float(frame.facing_yaw_micro_rad)) / 1000000.0) - desired)
	while angle > PI32:
		angle = f(angle - TAU32)
	while angle <= -PI32:
		angle = f(angle + TAU32)
	return angle

func world_marker_x(position: Dictionary) -> Variant:
	var relative: float = relative_yaw(position)
	return f(320.0 + f(f(relative / f(1.05)) * f(640.0 * f(0.42)))) if absf(relative) <= f(1.05) else null

static func i32(value: int) -> int:
	return ((value + 2147483648) & 0xffffffff) - 2147483648

static func f(value: float) -> float:
	return F32.value(value)

static func sinf(value: float) -> float:
	return Vector2.from_angle(value).y

static func cosf(value: float) -> float:
	return Vector2.from_angle(value).x

static func retail_color(argb: int) -> Color:
	return Color(f(float((argb >> 16) & 255) / 255.0), f(float((argb >> 8) & 255) / 255.0),
		f(float(argb & 255) / 255.0), f(float((argb >> 24) & 255) / 255.0))

static func battle_line_rect() -> Rect2:
	return Rect2(DESIGN_WIDTH - 121.0, DESIGN_HEIGHT - 112.0, 128, 128)

static func right_weapon_rect() -> Rect2:
	return Rect2(DESIGN_WIDTH - 141.0, DESIGN_HEIGHT - 141.0, 128, 128)

static func portrait_rect() -> Rect2:
	return Rect2(DESIGN_WIDTH - 137.0, DESIGN_HEIGHT - 128.0, 128, 128)

static func forseti_rect() -> Rect2:
	return Rect2(DESIGN_WIDTH - 104.0, (DESIGN_HEIGHT - 128.0) - 32.0, 64, 64)

static func guns_rect() -> Rect2:
	return Rect2(DESIGN_WIDTH - 137.0, DESIGN_HEIGHT - 240.0, 128, 128)
