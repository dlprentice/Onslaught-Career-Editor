# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Runtime expressions from Client/RetailOptions*.cs. Source addresses and their
## provenance remain in those admitted owners; this consolidates their executable
## laws without adding device recommendations or a new input owner. Float32
## stores and unchecked Int32 intermediates follow the C# reference expression.

const F = preload("res://Scenes/Shared/retail_float32.gd")
const V = preload("res://Core/retail_career_values.gd")
const IDENTITY_SCALE: float = 1.0
const PAD: float = 2.0
const LEFTOVER_MIN_X: float = 5.0
const PANEL_CLAMP_MAX: float = 480.0
const ICON_LABEL_PITCH: float = 20.0
const DROPDOWN_CLICK_CUE: int = 1


static func int_from_float(value: float) -> int:
	# The pinned .NET x64 unchecked conversion yields the integer-indefinite
	# word outside the signed range, including NaN and either infinity.
	return V.INT_MIN if not is_finite(value) or value < -2147483648.0 or value >= 2147483648.0 else int(value)


static func round_int(value: float, even: bool) -> int:
	if not is_finite(value) or absf(value) > 2147483649.0:
		return V.INT_MIN
	return int_from_float(F.round_even(value) if even else signf(value) * floor(absf(value) + 0.5))


static func mouse_sensitivity_index(sensitivity: float) -> int:
	var divided: float = F.value(F.value(sensitivity) / 3.0)
	return clampi(V.int32(round_int(F.value(divided + 0.5), true) - 1), 0, 20)


static func mouse_sensitivity_value(index: int) -> float:
	return F.value((clampi(index, 0, 20) + 1) * 3.0)


static func volume_index(scale: float) -> int:
	return clampi(round_int(F.value(F.value(10.0 * F.value(scale)) + F.value(0.48)), false), 0, 10)


static func volume_value(index: int) -> float:
	return F.value(clampi(index, 0, 10) / 10.0)


@warning_ignore("integer_division")
static func integer_half(value: int) -> int:
	return value / 2


static func menu_item_dest_x(center_x: float, cx: int) -> float:
	return F.value(F.value(center_x) - F.value(integer_half(cx)))


static func menu_item_scale(center_x: float, cx: int) -> float:
	var half: int = integer_half(cx)
	if half != 0 and menu_item_dest_x(center_x, cx) < 5.0:
		return F.value(F.value(F.value(center_x) - 5.0) / F.value(half))
	return 1.0


static func menu_icon_dest_x(incoming_x: float, cx: int) -> float:
	return menu_item_dest_x(incoming_x, cx)


static func menu_icon_scale(_incoming_x: float, _cx: int) -> float:
	return 1.0


static func dropdown_width(cx: int) -> int:
	return cx


static func dropdown_dest_x(incoming_x: float, cx: int) -> float:
	return F.value(F.value(incoming_x) - F.value(cx))


static func dropdown_scale(incoming_x: float, cx: int) -> float:
	if cx != 0 and dropdown_dest_x(incoming_x, cx) < 5.0:
		return F.value(F.value(F.value(incoming_x) - 5.0) / F.value(cx))
	return 1.0


static func dropdown_value_x(incoming_x: float) -> float:
	return F.value(F.value(incoming_x) + 2.0)


static func dropdown_list_x(incoming_x: float) -> float:
	return F.value(dropdown_value_x(incoming_x) + 2.0)


static func dropdown_panel_y(incoming_y: float, count: int, pitch: int) -> float:
	var span: int = V.int32(V.int32(count - 1) * pitch)
	var result: float = F.value(F.value(incoming_y) - F.value(integer_half(span)))
	var height: int = V.int32(count * pitch)
	if result < 0.0:
		result = 0.0
	if F.value(result + F.value(height)) > 480.0:
		return 0.0 if F.value(height) > 480.0 else F.value(480.0 - F.value(height))
	return result


static func dropdown_panel_width(max_cx: int) -> float:
	return F.value(V.int32(max_cx + 3))


static func dropdown_list_scale(count: int, pitch: int) -> float:
	var height: int = V.int32(count * pitch)
	return F.value(480.0 / F.value(height)) if F.value(height) > 480.0 else 1.0


static func dropdown_list_y(incoming_y: float, count: int, pitch: int, index: int) -> float:
	var offset: float = F.value(F.value(V.int32(index * pitch)) * dropdown_list_scale(count, pitch))
	return F.value(dropdown_panel_y(incoming_y, count, pitch) + offset)


static func dropdown_contains(x: float, y: float, dest_x: float, dest_y: float, label_cx: int, pitch: int) -> bool:
	x = F.value(x)
	y = F.value(y)
	dest_x = F.value(dest_x)
	dest_y = F.value(dest_y)
	return x >= dest_x and x < F.value(dest_x + F.value(label_cx)) \
		and y >= dest_y and y < F.value(dest_y + F.value(pitch))


static func dropdown_hit_right(incoming_x: float, label_cx: int) -> float:
	return F.value(dropdown_list_x(incoming_x) + F.value(label_cx))


static func dropdown_hit_bottom(incoming_y: float, count: int, pitch: int, index: int) -> float:
	return F.value(dropdown_list_y(incoming_y, count, pitch, index) + F.value(pitch))


static func dropdown_index_after_hit(current: int, index: int, hit: bool) -> int:
	return index if hit else current


static func dropdown_expand_after_click(expanded: bool, hit: bool) -> bool:
	return false if hit else expanded


static func dropdown_applies_live(pending_byte: int, committed: int, index: int) -> bool:
	return pending_byte == 0 and committed != index


static func dropdown_click_sound_applies(hit: bool) -> bool:
	return hit


static func cancel_helper_nonzero(first: int, second: int) -> bool:
	return first != 0 and second != 0


static func cancel_applies(helper_nonzero: bool, latch: bool) -> bool:
	return not helper_nonzero and latch


static func index_after_cancel(current: int, committed: int, apply: bool) -> int:
	return committed if apply else current


static func expand_after_cancel(expanded: bool, apply: bool) -> bool:
	return false if apply else expanded


static func menu_base_color(selected: bool, enabled: bool) -> int:
	return 0x50505050 if not enabled else (0xffffcc00 if selected else 0xffd6d6d6)


static func menu_packed_color(selected: bool, enabled: bool, incoming: int) -> int:
	return menu_base_color(selected, enabled) & incoming


static func dropdown_list_color(index: int, current: int) -> int:
	return 0xffffffff if index == current else 0xff404040


static func should_pulse(pending: bool) -> bool:
	return pending


static func dropdown_row_is_pending(committed: int, current: int) -> bool:
	return committed != current


static func pulse_channel(seconds: float) -> int:
	var source: float = F.value(seconds)
	var wrapped: float = source - 2.0 * floor(source / 2.0)
	var pulse: float = ((cos(wrapped * F.value(TAU)) + 1.0) * 0.5) * 255.0
	return 255 - clampi(round_int(pulse, true), 0, 255)


static func pulse_packed_color(pending: bool, seconds: float) -> int:
	if not pending:
		return 0xffffffff
	var channel: int = pulse_channel(seconds)
	return 0xff000000 | (channel << 16) | (channel << 8) | channel
