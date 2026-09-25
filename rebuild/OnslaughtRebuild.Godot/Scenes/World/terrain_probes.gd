# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends RefCounted
## Analysis-only replacements of the original terrain shader's PROBE_HOOK.
## The runtime appearance loader is the sole environment reader. Opening a
## material in the editor never selects a probe or mutates its saved shader.
const Text = preload("res://Core/canonical_json_string.gd")
const SHADER = preload("res://Scenes/World/terrain.gdshader")
const TAILS: Dictionary = {
	"macro": "ALBEDO = retail_output(macro_color);",
	"mask": "ALBEDO = retail_output(vec3(1.0, clamp(exp(-fog_density * max(-VERTEX.z, 0.0)), 0.0, 1.0), 0.0));",
	"chain": "ALBEDO = retail_output(0.25 * detail_primary * cloud_shadow * 2.0 * detail_secondary * 2.0);",
	"uv": "ALBEDO = retail_output(vec3(fract(retail_world_uv / 512.0), float(macro_level) / 8.0));",
	"uvfine": "ALBEDO = retail_output(vec3(fract(retail_world_uv / 2.0), 0.0));",
}


static func resolve(probe: String) -> Dictionary:
	# String.Trim uses Char.IsWhiteSpace, whose set differs from strip_edges.
	# Whitespace characters are all BMP scalars, so this also preserves .NET's
	# UTF-16 decision for any other scalar without converting or losing text.
	var first: int = 0
	var end: int = probe.length()
	while first < end and Text.is_white_space(probe.unicode_at(first)):
		first += 1
	while end > first and Text.is_white_space(probe.unicode_at(end - 1)):
		end -= 1
	if first == end:
		return {"ok": true, "active": false, "mode": "", "code": SHADER.code}
	var mode: String = probe.substr(first, end - first)
	if not TAILS.has(mode):
		return {"ok": false, "error_type": "InvalidDataException", "error": "ONSLAUGHT_TERRAIN_PROBE='" + probe + "' is not a known terrain probe mode."}
	return {"ok": true, "active": true, "mode": mode, "code": SHADER.code.replace("// PROBE_HOOK", TAILS[mode])}
