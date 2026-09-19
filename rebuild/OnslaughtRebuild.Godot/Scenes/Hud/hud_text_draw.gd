# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Hud/hud_draw.gd"
const Text = preload("res://Core/canonical_json_string.gd")
const MessagePanel = preload("res://Client/message_panel.gd")
const BitmapFont = preload("res://Scenes/Shared/retail_bitmap_font.gd")

func render(part: Part) -> void:
	begin(part)
	match int(part.part):
		18: message_window()
		19: help_prompts()
		20: weapon_ammo()
		21: terminal_overlay()
	end()

func message_window() -> void:
	var clip := Rect2(MessagePanel.PANEL_BODY_LEFT, MessagePanel.PANEL_BODY_TOP,
		MessagePanel.PANEL_BODY_RIGHT - MessagePanel.PANEL_BODY_LEFT, MessagePanel.PANEL_BODY_BOTTOM - MessagePanel.PANEL_BODY_TOP)
	for index: int in range(state.message_window.size()):
		text_line(state.message_window[index], MessagePanel.TEXT_PEN_LEFT, f(MessagePanel.FIRST_LINE_PEN_TOP + f(float(index) * MessagePanel.LINE_HEIGHT_PIXELS)), false, true, clip)

func help_prompts() -> void:
	var y: float = 28.0
	for prompt: Variant in state.help_texts:
		var lines: Array[PackedInt32Array] = wrap_lines(prompt, 360.0)
		for line: PackedInt32Array in lines.slice(0, 2):
			text_line(line, f(f(DESIGN_WIDTH - measure(line, false)) * 0.5), y)
			y = f(y + MessagePanel.LINE_HEIGHT_PIXELS)
		y = f(y + 4.0)

func weapon_ammo() -> void:
	var weapon: Dictionary = hud.weapon
	if weapon.selected_weapon != 2 or not weapon.vulcan_cannon_enabled or weapon.vulcan_ammo == null:
		return
	var text: PackedInt32Array = BitmapFont._utf16_units(str(int(weapon.vulcan_ammo)))
	var bounds := Rect2(9, DESIGN_HEIGHT - 141.0, 128, 32)
	var left: float = f(f(bounds.end.x - measure(text, true)) - 8.0)
	text_line(text, left, bounds.position.y, true, false, bounds)

func terminal_overlay() -> void:
	if not hud.terminal.visible:
		return
	target.draw_rect(Rect2(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT), Color(0, 0, 0, f(float(state.terminal_darkener_alpha) / 255.0)))
	var title: Variant = state.terminal_title
	text_line(title, f(f(DESIGN_WIDTH - measure(title, true)) * 0.5), 50.0, true)
	if int(hud.terminal.outcome) != 2:
		return
	var top: float = 90.0
	for line: PackedInt32Array in wrap_lines(state.terminal_reason, 500.0):
		text_line(line, 65.0, top)
		top = f(top + 16.0)

func text_line(text: Variant, left: float, top: float, large: bool = false,
		shadow: bool = true, clip: Variant = null) -> void:
	var atlas: Texture2D = assets.pages["font-22" if large else "font-13ps"]
	var widths: PackedInt32Array = assets.large_widths if large else assets.small_widths
	var cell: int = 32 if large else 16
	var x: float = left
	for code: int in text_units(text):
		var glyph: int = BitmapFont._glyph(code)
		var width: int = widths[glyph]
		@warning_ignore("integer_division")
		var source := Rect2((glyph % 16) * cell, (glyph / 16) * cell, width, cell)
		# HUD shadow is at the pen, body is pen−(1,1). This differs from the
		# pause label law, so only atlas indexing/measurement is shared.
		if shadow:
			clipped_region(atlas, Rect2(x, top, width, cell), source, Color.BLACK, clip)
		clipped_region(atlas, Rect2(f(x - 1.0) if shadow else x, f(top - 1.0) if shadow else top, width, cell), source, Color.WHITE, clip)
		x = f(x + float(width + 1))

func clipped_region(atlas: Texture2D, destination: Rect2, source: Rect2, color: Color, clip: Variant) -> void:
	if clip == null:
		target.draw_texture_rect_region(atlas, destination, source, color)
		return
	var bounds: Rect2 = clip
	var left: float = maxf(destination.position.x, bounds.position.x)
	var top: float = maxf(destination.position.y, bounds.position.y)
	var right: float = minf(destination.end.x, bounds.end.x)
	var bottom: float = minf(destination.end.y, bounds.end.y)
	if right <= left or bottom <= top:
		return
	var clipped := Rect2(left, top, f(right - left), f(bottom - top))
	var clipped_source := Rect2(source.position + clipped.position - destination.position, clipped.size)
	target.draw_texture_rect_region(atlas, clipped, clipped_source, color)

func measure(text: Variant, large: bool = false) -> float:
	var width: float = 0.0
	var widths: PackedInt32Array = assets.large_widths if large else assets.small_widths
	for code: int in text_units(text):
		width = f(width + float(widths[BitmapFont._glyph(code)] + 1))
	return width

static func text_units(text: Variant) -> PackedInt32Array:
	return text if typeof(text) == TYPE_PACKED_INT32_ARRAY else BitmapFont._utf16_units(String(text))

func wrap_lines(text: Variant, maximum_width: float) -> Array[PackedInt32Array]:
	var raw: PackedInt32Array = text_units(text)
	var normalized := PackedInt32Array()
	var index: int = 0
	while index < raw.size():
		var code: int = raw[index]
		index += 1
		if code == 13:
			if index < raw.size() and raw[index] == 10:
				index += 1
			code = 10
		normalized.append(code)
	var paragraphs: Array[PackedInt32Array] = []
	var start: int = 0
	for position: int in range(normalized.size()):
		if normalized[position] == 10:
			paragraphs.append(normalized.slice(start, position))
			start = position + 1
	paragraphs.append(normalized.slice(start))
	var lines: Array[PackedInt32Array] = []
	for paragraph: PackedInt32Array in paragraphs:
		var current := PackedInt32Array()
		var position: int = 0
		while position < paragraph.size():
			var separator_start: int = position
			while position < paragraph.size() and Text.is_white_space(paragraph[position]):
				position += 1
			var separator: PackedInt32Array = paragraph.slice(separator_start, position)
			var word_start: int = position
			while position < paragraph.size() and not Text.is_white_space(paragraph[position]):
				position += 1
			if word_start == position:
				break
			var word: PackedInt32Array = paragraph.slice(word_start, position)
			var candidate: PackedInt32Array = word if current.is_empty() else current + separator + word
			if measure(candidate) <= maximum_width:
				current = candidate
				continue
			if not current.is_empty():
				lines.append(current)
				current = PackedInt32Array()
			var remaining: PackedInt32Array = word
			while not remaining.is_empty() and measure(remaining) > maximum_width:
				var split: int = 1
				while split < remaining.size() and measure(remaining.slice(0, split + 1)) <= maximum_width:
					split += 1
				lines.append(remaining.slice(0, split))
				remaining = remaining.slice(split)
			current = remaining
		if not current.is_empty():
			lines.append(current)
		elif paragraph.is_empty():
			lines.append(PackedInt32Array())
	return lines
