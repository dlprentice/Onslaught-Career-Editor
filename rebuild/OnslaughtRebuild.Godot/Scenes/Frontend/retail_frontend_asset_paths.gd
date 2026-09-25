# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## Public routing recipe, ported from RetailFrontendAssetPaths.TexturePath.
## No path normalization, filesystem access or asset loading belongs here.
## PascalCase exports retain existing authored .tres property names. Godot's
## typed String exports cannot store a forced C# null directory; the checked
## raw resolver preserves that legacy failure for callers with nullable data.
const Text = preload("res://Core/canonical_json_string.gd")
@export_dir var FrontendDirectory: String = "res://Assets/Frontend"
@export_dir var HudDirectory: String = "res://Assets/Hud"
@export_dir var PauseDirectory: String = "res://Assets/PauseMenu"
@export var TextureOverrides: Dictionary[String, String] = {}


func texture_path(folder: Variant, name: Variant) -> Dictionary:
	var resolved: Dictionary = texture_path_units(folder, name)
	if not resolved.ok: return resolved
	var converted: Dictionary = Text.native_string(resolved.value)
	if not converted.ok:
		return _failure("UnsupportedString", "This path requires texture_path_units to preserve its UTF-16 units.")
	return converted


## The temporary C# bridge transports units both ways, preserving embedded NUL,
## lone surrogates and null interpolation without an intermediate native String.
func texture_path_units(folder: Variant, name: Variant) -> Dictionary:
	return resolve_texture_path_units(folder, name, FrontendDirectory, HudDirectory, PauseDirectory, TextureOverrides)


static func resolve_texture_path_units(folder: Variant, name: Variant, frontend_directory: Variant,
		hud_directory: Variant, pause_directory: Variant, overrides: Dictionary) -> Dictionary:
	var folder_value: Dictionary = Text.units(folder)
	if not folder_value.ok: return _failure("ArgumentException", folder_value.error, "folder")
	var name_value: Dictionary = Text.units(name)
	if not name_value.ok: return _failure("ArgumentException", name_value.error, "name")
	# C# interpolation substitutes empty text for either null argument.
	var folder_units: PackedInt32Array = PackedInt32Array() if folder_value.value == null else folder_value.value
	var name_units: PackedInt32Array = PackedInt32Array() if name_value.value == null else name_value.value
	var key: PackedInt32Array = folder_units + PackedInt32Array([47]) + name_units
	for candidate: Variant in overrides:
		if not candidate is String:
			return _failure("ArgumentException", "Texture override keys require strings.", "overrides")
		if Text.units(candidate).value != key: continue
		var path: Dictionary = Text.units(overrides[candidate])
		if not path.ok: return _failure("ArgumentException", path.error, "overrides")
		# Preserve the exact override, including all surrounding whitespace. Only
		# the null/all-Char.IsWhiteSpace predicate selects the default route.
		if not Text.is_null_or_white_space(path.value): return {"ok": true, "value": path.value}
		break
	var directory: Variant
	if Text.equals_text(folder_value.value, "Frontend"):
		directory = frontend_directory
	elif Text.equals_text(folder_value.value, "Hud"):
		directory = hud_directory
	elif Text.equals_text(folder_value.value, "PauseMenu"):
		directory = pause_directory
	else:
		return _failure("ArgumentOutOfRangeException", "Specified argument was out of the range of valid values.", "folder")
	# A valid override above bypasses this dereference in the original C#.
	if directory == null:
		return _failure("NullReferenceException", "Object reference not set to an instance of an object.")
	var admitted: Dictionary = Text.units(directory)
	if not admitted.ok: return _failure("ArgumentException", admitted.error, "directory")
	var directory_units: PackedInt32Array = admitted.value
	var length: int = directory_units.size()
	while length > 0 and directory_units[length - 1] == 47: length -= 1
	return {"ok": true, "value": directory_units.slice(0, length) + PackedInt32Array([47]) + name_units + Text.units(".texture.aya").value}


static func _failure(kind: String, message: String, parameter: String = "") -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message, "parameter": parameter}
