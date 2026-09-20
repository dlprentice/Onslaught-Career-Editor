# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Existing CFEPMain presentation, extracted from RetailFrontendFlow and its
## RetailMainMenu* expression owners. This module consumes supplied facts; it
## owns no timer, RNG, session, input, language transition or rendering loop.
## The measured underlay/reveal and shadow-rate limitations remain unchanged.
const F = preload("res://Scenes/Shared/retail_float32.gd")
const RAW = preload("res://Core/retail_float24.gd")
const PAGE_WIDTH: float = 640.0
const PAGE_HEIGHT: float = 480.0
const ROW_CENTER_X: float = 219.0
const ROW_FIRST_Y: float = 304.0 # RetailMainMenuRowY.NonzeroSlotY, not language Y268.
const ROW_PITCH: float = 20.0
const SHADOW_PHASE_RATE: float = -2.0 * PI * 141.0 / 1795.2
const ROW_NAMES: Array[String] = ["NewGame", "ContinueGame", "LoadGame", "Multiplayer", "Goodies", "Options", "Quit"]
const LABEL_KEYS: Array[String] = ["newGame", "continueGame", "loadGame", "multiplayer", "goodies", "options", "quit"]
const VERSION_TEXT: String = "V1.00" # Image-initial major/minor remain 1/0.
const UNAVAILABLE: int = 0x7d1f1f1f
const BRACKET: int = 0xfe7f7f7f
const SHADOW: int = 0x3e000000
const CHROME: int = 0x3e7f7f7f
const FLAG: int = 0xfd3f3f3f
const VERSION: int = 0xff102025


static func clamp01(value: float) -> float:
	# The source comparisons deliberately propagate NaN.
	return 0.0 if value < 0.0 else (1.0 if value > 1.0 else value)


static func range_transition(value: float, low: float, high: float) -> float:
	var denominator: float = F.value(high - low)
	var numerator: float = F.value(value - low)
	if denominator == 0.0:
		return clamp01(NAN if numerator == 0.0 else (INF if numerator > 0.0 else -INF))
	return clamp01(F.value(numerator / denominator))


static func make_alpha(value: float) -> float:
	var rounded: float = F.round_even(F.value(clamp01(value) * 255.0))
	return F.value((0.0 if rounded < 0.0 else (255.0 if rounded > 255.0 else rounded)) / 255.0)


static func page_fade(transition: float) -> float:
	return clamp01(F.value(F.value(F.value(transition) - F.value(0.75)) * 4.0))


static func icon_fade(transition: float) -> float:
	return clamp01(F.value(F.value(F.value(transition) - F.value(0.8)) * 5.0))


static func underlay_alpha(transition: float) -> float:
	# Existing measured branch uses the 0..0.5 window. The retail async-load
	# mechanism for the first ~400ms remains unestablished; do not refit it.
	return make_alpha(range_transition(F.value(transition), 0.0, 0.5))


static func left_decor(transition: float) -> Dictionary:
	transition = F.value(transition)
	var scale_value: float = 1.25
	var rotation_value: float = 0.0
	var alpha: float = 1.0
	if transition < 1.0:
		if transition < F.value(0.2):
			var t: float = clamp01(F.value(transition * 5.0))
			alpha = make_alpha(t)
			rotation_value = -F.value(F.value(1.0 - t) * F.value(0.3))
			scale_value = t
		elif transition < F.value(0.4):
			scale_value = 1.0
		elif transition < F.value(0.6):
			scale_value = F.value(F.value(clamp01(F.value(F.value(transition - F.value(0.4)) * 5.0)) * 0.25) + 1.0)
	return _decor(scale_value, rotation_value, alpha, true)


static func left_twin(transition: float) -> Dictionary:
	transition = F.value(transition)
	if transition >= 1.0:
		return _decor(0.0, 0.0, 0.0, false)
	if transition < F.value(0.2):
		var t: float = clamp01(F.value(transition * 5.0))
		return _decor(t, F.value(F.value(1.0 - t) * F.value(0.3)), make_alpha(t), true)
	if transition < F.value(0.6):
		return _decor(1.0, 0.0, 1.0, true)
	if transition < F.value(0.8):
		var t: float = F.value(1.0 - clamp01(F.value(F.value(transition - F.value(0.6)) * 5.0)))
		return _decor(t, -F.value(F.value(1.0 - t) * F.value(0.3)), make_alpha(t), true)
	return _decor(0.0, 0.0, 0.0, false)


static func right_decor(transition: float) -> Dictionary:
	transition = F.value(transition)
	var scale_value: float = 1.25
	var rotation_value: float = 0.0
	var alpha: float = 1.0
	if transition < 1.0:
		if transition < F.value(0.1):
			alpha = 0.0
		elif transition < F.value(0.3):
			var t: float = clamp01(F.value(F.value(transition - F.value(0.1)) * 5.0))
			alpha = make_alpha(t)
			rotation_value = -F.value(t * F.value(0.3))
			scale_value = t
		elif transition < F.value(0.5):
			scale_value = 1.0
		elif transition < F.value(0.7):
			scale_value = F.value(F.value(clamp01(F.value(F.value(transition - F.value(0.5)) * 5.0)) * 0.25) + 1.0)
	return _decor(scale_value, rotation_value, alpha, alpha > 0.0)


static func right_twin(transition: float) -> Dictionary:
	transition = F.value(transition)
	if transition >= 1.0 or transition < F.value(0.1):
		return _decor(0.0, 0.0, 0.0, false)
	if transition < F.value(0.3):
		var t: float = clamp01(F.value(F.value(transition - F.value(0.1)) * 5.0))
		return _decor(t, -F.value(t * F.value(0.3)), make_alpha(t), true)
	if transition < F.value(0.7):
		return _decor(1.0, 0.0, 1.0, true)
	if transition < F.value(0.9):
		var t: float = F.value(1.0 - clamp01(F.value(F.value(transition - F.value(0.7)) * 5.0)))
		return _decor(t, -F.value(t * F.value(0.3)), make_alpha(t), true)
	return _decor(0.0, 0.0, 0.0, false)


static func shadow_phase(seconds: float) -> float:
	return SHADOW_PHASE_RATE * seconds


static func shadow_offset(seconds: float) -> PackedFloat64Array:
	# RetailFrontendDecorShadow uses Math.Sin/Cos on binary64 phase; all
	# callers cast each completed coordinate to Single only afterwards.
	var phase: float = shadow_phase(seconds)
	return PackedFloat64Array([5.0 + 6.0 * cos(phase), 10.0 + 3.0 * sin(phase)])


static func reflection_scroll(seconds: float) -> float:
	var value: float = F.value(F.value(F.value(seconds) * F.value(29.95)) + F.value(86.68))
	# C# Mathf.PosMod takes Singles; the power-of-two divisor makes the
	# remainder exact for finite Single inputs before the final store.
	if is_nan(value): return value
	if is_inf(value): return RAW.read_word(0xffc00000)
	var remainder: float = F.value(fmod(value, 512.0))
	return F.value(remainder + 512.0) if remainder < 0.0 else remainder


static func retail_color(argb: int) -> Color:
	return Color(_modulate2x((argb >> 16) & 255), _modulate2x((argb >> 8) & 255),
		_modulate2x(argb & 255), F.value(float((argb >> 24) & 255) / 255.0))


static func label_base_color(selected: bool, available: bool) -> int:
	return 0xffff6f3f if selected else (0xff4f4f4f if available else 0x7f1f1f1f)


static func label_fade_mul(colour: int, fade_byte: int) -> int:
	var byte: int = clampi(fade_byte, 0, 255)
	var shifted: int = colour >> 8
	var ecx: int = ((shifted & 0x00ff0000) * byte) & 0xffffffff
	var eax: int = ((shifted & 0xffff0000) * byte) & 0xffffffff
	eax = (eax ^ colour) & 0x00ffffff
	return (eax ^ ecx) & 0xffffffff


static func label_draw_unpack(packed: int) -> int:
	var eax: int = packed >> 8
	var ecx: int = eax & 0xffff0000
	eax &= 0x00ff0000
	var ebx: int = (((ecx << 8) - ecx) & 0xffffffff) ^ packed
	var edx: int = ((eax << 8) - eax) & 0xffffffff
	return ((ebx & 0x00ffffff) ^ edx) & 0xffffffff


static func label_color(selected: bool, available: bool, fade_byte: int = 255) -> int:
	return label_draw_unpack(label_fade_mul(label_base_color(selected, available), fade_byte))


static func selector_color(fade_byte: int = 255) -> int:
	var byte: int = clampi(fade_byte, 0, 255)
	return ((((byte << 7) - byte) << 16) & 0xff000000)


static func label_dest_x(width: float) -> float:
	return F.value(ROW_CENTER_X - F.value(F.value(width) * 0.5))


static func selector_rect(index: int, width: float) -> Rect2:
	var box_width: float = F.value(F.value(width) + 31.0)
	var row_y: float = F.value(ROW_FIRST_Y + F.value(index * ROW_PITCH))
	return Rect2(F.value(ROW_CENTER_X - F.value(box_width * 0.5)), F.value(row_y - 16.0), box_width, 32.0)


static func _modulate2x(channel: int) -> float:
	return F.value(float(mini(255, (channel * 255) >> 7)) / 255.0)


static func _decor(scale_value: float, rotation_value: float, alpha: float, draw: bool) -> Dictionary:
	return {"scale": scale_value, "rotation": rotation_value, "alpha": alpha, "draw": draw}
