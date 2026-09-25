# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## CFEPIntro expressions from the retained RetailClickToStart{Prompt,Splash,
## Glyphs,Slide,Title}.cs owners. Their specimen addresses/provenance remain
## authoritative. These are functions of supplied facts, never a clock owner.
## Binary32 stores follow the existing C# expressions; timer/page math stays
## binary64 where the existing owner uses double. Z values remain explicit
## metadata; the current 2-D compositor still draws in submit order.
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Numbers = preload("res://Client/options_laws.gd")
const Raw = preload("res://Core/retail_float24.gd")
const Cosine = preload("res://Scenes/Shared/retail_cosf.gd")
const SEED_BITS: int = 0x3727c5ac
const SPLASH_Z_BITS: int = 0x3f75c28f
const GLYPH_Z_BITS: int = 0x3dcccccd
const SLIDE_Z_BITS: Array[int] = [0x3dced917, 0x3dcccccd]
const SIXTH_Z_BITS: int = 0x3ca3d70a
const PROMPT: String = "Click to start" # Existing localization-0x77 literal.
const GLYPH_PASSES: Array[Dictionary] = [
	{"dx": -1.0, "y": 401.0, "color": 0xff000000},
	{"dx": 1.0, "y": 401.0, "color": 0xff000000},
	{"dx": -1.0, "y": 399.0, "color": 0xff000000},
	{"dx": 1.0, "y": 399.0, "color": 0xff000000},
	{"dx": 0.0, "y": 400.0, "color": 0xffffffff}]
const SLIDE_PASSES: Array[Dictionary] = [
	{"x": 124.0, "y": -6.0, "color": 0x3f000000},
	{"x": 120.0, "y": -10.0, "color": 0xffffffff}]
const TITLE_PASSES: Array[Dictionary] = [
	{"x": 252.0, "y": 292.0, "z_bits": 0x3d4ccccd, "outline": true},
	{"x": 248.0, "y": 292.0, "z_bits": 0x3d4ccccd, "outline": true},
	{"x": 252.0, "y": 288.0, "z_bits": 0x3d4ccccd, "outline": true},
	{"x": 248.0, "y": 288.0, "z_bits": 0x3d4ccccd, "outline": true},
	{"x": 250.0, "y": 290.0, "z_bits": 0x3d23d70a, "outline": false}]


static func advance(timer: float, page_seconds: float, delta: float) -> float:
	if timer == 0.0 and page_seconds > 1.0:
		timer = Raw.read_word(SEED_BITS)
	if timer != 0.0:
		timer += 2.0 * delta
	return timer


static func prompt_visible(timer: float) -> bool:
	if timer <= 4.0:
		return false
	# C# fmod of infinity is NaN, whose final comparison is false.
	if not is_finite(timer):
		return false
	var remainder: float = fmod(timer, 4.0)
	if remainder < 0.0:
		remainder += 4.0
	return remainder < 2.0


static func idle_result_due(page_seconds: float) -> bool:
	return page_seconds > 30.0


static func splash_argument(timer: float) -> float:
	return F.value(timer) if timer <= 1.0 else 1.0


static func splash_scale(timer: float) -> float:
	var argument: float = F.value(splash_argument(timer) * Raw.read_word(0x40490fdb))
	# MathF.Cos uses the host's single-precision cosf path. Casting Godot's
	# binary64 cos back to single changes several transition words.
	var result: Dictionary = Cosine.cosine(argument)
	if not result.ok:
		push_error(result.error)
		return NAN
	var wave: float = result.value
	return F.value(F.value(F.value(wave + 1.0) * 0.375) + 0.46875)


static func splash_x(timer: float) -> float:
	return F.value(F.value(558.0 - F.value(splash_scale(timer) * 238.0)) - 126.4375)


static func splash_y(timer: float) -> float:
	return F.value(F.value(18.0 - F.value(splash_scale(timer) * -222.0)) - -117.9375)


static func glyph_x(pass_index: int, width: int) -> float:
	return F.value(F.value(320.0 - F.value(F.value(width) * 0.5)) + GLYPH_PASSES[pass_index].dx)


static func slide_fade(timer: float) -> float:
	var delta: float = F.value(F.value(timer) - 4.0)
	if delta < 0.0:
		return 0.0
	return 1.0 if delta > 1.0 else delta


static func slide_offset(timer: float) -> float:
	var remain: float = F.value(1.0 - slide_fade(timer))
	return F.value(F.value(remain * remain) * 400.0)


static func slide_x(pass_index: int, timer: float) -> float:
	return F.value(SLIDE_PASSES[pass_index].x - slide_offset(timer))


static func title_visible(page_seconds: float) -> bool:
	return page_seconds * 1.2 > 2.0


static func title_scale(page_seconds: float) -> float:
	var v: float = _ramp(page_seconds)
	return 0.5 if v < 1.0 else F.value(0.5 * v)


static func title_outline_color(page_seconds: float) -> int:
	return ((_brightness(page_seconds) * 159) << 16) & 0xff000000


static func title_body_color(page_seconds: float) -> int:
	return _pack_body(_brightness(page_seconds))


static func sixth_scale(page_seconds: float) -> float:
	var v: float = _ramp(page_seconds)
	return F.value(1.0 - v) if v < 1.0 else -1.0


static func sixth_visible(page_seconds: float) -> bool:
	var fade: float = sixth_scale(page_seconds)
	return fade > 0.0 and fade < 3.0


static func sixth_color(page_seconds: float) -> int:
	var fade: float = sixth_scale(page_seconds)
	# GDScript refuses /0; retain the .NET unchecked conversion's result.
	var value: float = F.value(32.0 / fade) if fade != 0.0 else INF
	return _pack_body(Numbers.round_int(value, true))


static func _ramp(page_seconds: float) -> float:
	return F.value(25.0 - F.value(12.0 * F.value(page_seconds)))


static func _brightness(page_seconds: float) -> int:
	var v: float = _ramp(page_seconds)
	var u: float = 1.0 if v < 1.0 else F.value(1.0 / v)
	return Numbers.round_int(F.value(u * 255.0), true)


static func _pack_body(brightness: int) -> int:
	var packed: int = (((brightness << 8) - brightness) << 16) & 0xffffffff
	return ((~packed) & 0x00ffffff) ^ packed
