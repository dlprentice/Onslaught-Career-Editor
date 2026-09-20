# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure extraction of RetailFrontendFlow.Options.cs input handlers. The caller
## supplies the same physical-or-logical key matches and measured label width.
## It still owns the input edge, coordinates, font, audio, settings consumers and
## redraw. Ordered effects report exactly where those host operations occurred.
## `frontend_back` requests the existing frontend Back seam; the caller must
## perform its successful Back cue/navigation/redraw in the original order.

const Options = preload("res://Client/options_menu.gd")
const Laws = preload("res://Client/options_laws.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const V = preload("res://Core/retail_career_values.gd")
var _menu: Options.Menu
var _effect_handler: Callable
var _contexts: Array[Dictionary] = []


func _init(menu: Options.Menu, effect_handler: Callable = Callable()) -> void:
	_menu = menu
	_effect_handler = effect_handler


func set_effect_handler(handler: Callable) -> void:
	_effect_handler = handler


func key_matches(up: bool, down: bool, left: bool, right: bool, confirm: bool, back: bool) -> Dictionary:
	_begin()
	if _menu == null:
		return _result(V.failure("ArgumentNullException", "Options menu must not be null.", "menu"))
	# These branches retain physical/logical-key conflict precedence. Press and
	# echo admission remain with the shared platform input owner, as in the host.
	if up:
		return _notify(_menu.move_selection(-1))
	if down:
		return _notify(_menu.move_selection(1))
	if left:
		return _notify(_menu.adjust(-1))
	if right:
		return _notify(_menu.adjust(1))
	if confirm:
		return _confirm()
	if back:
		return _back()
	return _result(V.success(false))


func pointer_motion(x: float, y: float, label_width: float) -> Dictionary:
	_begin()
	if _menu == null:
		return _missing()
	if _menu.is_expanded():
		var hit: Dictionary = _expanded_hit(x, y, label_width)
		if not hit.ok or hit.value < 0:
			return _result(hit if not hit.ok else V.success(false))
		var hover: Dictionary = _menu.hover_state(hit.value)
		if not hover.ok:
			return _result(hover)
		if hover.value:
			var effect: Dictionary = _audio(0)
			if not effect.ok:
				return _result(effect)
		return _result(hover)
	var index: Dictionary = _menu.row_at(y)
	if not index.ok or index.value < 0:
		return _result(index if not index.ok else V.success(false))
	var hovered: Dictionary = _menu.hover(index.value)
	if hovered.ok and hovered.value:
		var effect: Dictionary = _audio(0)
		if not effect.ok:
			return _result(effect)
	return _result(hovered)


func pointer_confirm(x: float, y: float, label_width: float) -> Dictionary:
	_begin()
	if _menu == null:
		return _missing()
	x = F.value(x)
	y = F.value(y)
	if x >= 0.0 and x < 46.0 and y >= 430.0 and y < 478.0:
		return _back()
	if _menu.is_expanded():
		var hit: Dictionary = _expanded_hit(x, y, label_width)
		if not hit.ok:
			return _result(hit)
		if hit.value >= 0:
			var selected: Dictionary = _menu.select_state(hit.value)
			if not selected.ok:
				return _result(selected)
		# Click outside the popup still closes through Confirm, including its
		# cue and commit. It is not the right-button revert/cancel path.
		return _confirm()
	var index: Dictionary = _menu.row_at(y)
	if not index.ok or index.value < 0:
		return _result(index if not index.ok else V.success(false))
	var rows: Dictionary = _menu.get_rows()
	if not rows.ok:
		return _result(rows)
	var row: Dictionary = rows.value[index.value]
	if not row.is_selectable:
		return _result(V.success(false))
	var hover: Dictionary = _menu.hover(index.value)
	if not hover.ok:
		return _result(hover)
	if hover.value:
		var effect: Dictionary = _audio(0)
		if not effect.ok:
			return _result(effect)
	if row.kind == Options.RowKind.VALUE_BAR:
		label_width = F.value(label_width)
		var left: float = F.value(320.0 - F.value(F.value(F.value(label_width + 6.0) + 103.0) * 0.5))
		var left_arrow: float = F.value(F.value(left + label_width) + 6.0)
		var bar_x: float = F.value(left_arrow + 13.0)
		if x < bar_x:
			return _notify(_menu.adjust(-1))
		if x >= F.value(bar_x + 81.0):
			return _notify(_menu.adjust(1))
		return _result(V.success(true))
	return _confirm()


func pointer_cancel(right_down: bool) -> Dictionary:
	_begin()
	if not Laws.cancel_applies(false, right_down):
		return _result(V.success(false))
	if _menu == null:
		return _missing()
	var cancelled: Dictionary = _menu.cancel_expanded()
	if cancelled.ok and cancelled.value:
		var effect: Dictionary = _audio(2)
		if not effect.ok:
			return _result(effect)
		effect = _emit({"kind": "redraw"})
		if not effect.ok:
			return _result(effect)
	return _result(cancelled)


func _expanded_hit(x: float, y: float, label_width: float) -> Dictionary:
	var selected: Dictionary = _menu.get_selected_row()
	if not selected.ok:
		return selected
	var row: Dictionary = selected.value
	var top: Dictionary = _menu.row_top(_menu.get_selected_index())
	if not top.ok:
		return top
	var label_cx: int = Laws.int_from_float(F.value(label_width))
	if row.states == null:
		return V.failure("NullReferenceException", "Options state list is null.")
	for index: int in range(row.states.size()):
		if Laws.dropdown_contains(x, y, Laws.dropdown_list_x(319.0),
			Laws.dropdown_list_y(top.value, row.states.size(), 16, index), label_cx, 16):
			return V.success(index)
	return V.success(-1)


func _notify(changed: Dictionary) -> Dictionary:
	if not changed.ok:
		return _result(changed)
	if changed.value:
		var effect: Dictionary = _audio(0)
		if not effect.ok:
			return _result(effect)
		effect = _emit({"kind": "apply_settings"})
		if not effect.ok:
			return _result(effect)
		effect = _emit({"kind": "redraw"})
		if not effect.ok:
			return _result(effect)
	return _result(V.success(true))


func _confirm() -> Dictionary:
	var confirmed: Dictionary = _menu.confirm()
	if not confirmed.ok:
		return _result(confirmed)
	if confirmed.value == Options.OptionsSignal.NONE:
		return _result(V.success(true))
	if confirmed.value == Options.OptionsSignal.CLOSED:
		return _back()
	var effect: Dictionary = _audio(1)
	if not effect.ok:
		return _result(effect)
	effect = _emit({"kind": "apply_settings"})
	if not effect.ok:
		return _result(effect)
	effect = _emit({"kind": "redraw"})
	if not effect.ok:
		return _result(effect)
	return _result(V.success(true))


func _back() -> Dictionary:
	var backed: Dictionary = _menu.back()
	if not backed.ok:
		return _result(backed)
	var effect: Dictionary
	if backed.value in [Options.OptionsSignal.PAGE_CHANGED, Options.OptionsSignal.VALUE_CHANGED]:
		effect = _audio(2)
		if not effect.ok:
			return _result(effect)
		effect = _emit({"kind": "redraw"})
	else:
		effect = _emit({"kind": "frontend_back"})
	return _result(V.success(true) if effect.ok else effect)


func _audio(cue: int) -> Dictionary:
	return _emit({"kind": "audio", "cue": cue})


func _begin() -> void:
	# Each user action owns its result journal. A synchronous host observer may
	# reenter the same controller without erasing the outer action's effects.
	_contexts.append({"effects": [], "settings": [], "handler": _effect_handler})


func _emit(effect: Dictionary) -> Dictionary:
	var context: Dictionary = _contexts.back()
	var settings: Dictionary = {} if _menu == null else _menu.get_settings()
	context.effects.append(effect.duplicate(true))
	context.settings.append(settings.duplicate(true))
	var handler: Callable = context.handler
	if not handler.is_valid():
		return V.success()
	# The host callback runs only at an explicit input action's effect, never
	# per row/draw/frame. Returning a failure aborts before the next mutation,
	# retaining the same partial state as a thrown C# audio/settings callback.
	var result: Variant = handler.call(effect.duplicate(true), settings)
	if not result is Dictionary or not result.get("ok") is bool:
		return V.failure("InvalidOperationException", "Options effect handler must return an explicit result.")
	return result


func _result(result: Dictionary) -> Dictionary:
	var context: Dictionary = _contexts.pop_back()
	var detached: Dictionary = result.duplicate(true)
	detached.effects = context.effects.duplicate(true)
	detached.effect_settings = context.settings.duplicate(true)
	var handler: Callable = context.handler
	detached.effects_dispatched = handler.is_valid()
	return detached


func _missing() -> Dictionary:
	return _result(V.failure("ArgumentNullException", "Options menu must not be null.", "menu"))
