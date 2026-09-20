# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Original source-checkout adapter; the separately licensed Arm adaptation is
## tools/godot_compat/arm_cosf.gd, never copied into the rebuild subtree. Declaring
## a separate package resource does not establish a working export/package.
const SOURCE_RELATIVE_PATH: String = "../../tools/godot_compat/arm_cosf.gd"
const PACKAGED_RESOURCE_PATH: String = "res://RuntimeDependencies/ArmCosf.gd"
static var _attempted: bool = false
static var _implementation: GDScript = null
static var _error: Dictionary = {}
static var _path: String = ""
static var _mode: String = ""


static func cos_bits(word: Variant) -> Dictionary:
	var ready: Dictionary = _ensure_loaded()
	if not ready.ok: return ready
	return _implementation.call("cos_bits", word)


static func cosine(value: float) -> Dictionary:
	var ready: Dictionary = _ensure_loaded()
	if not ready.ok: return ready
	return _implementation.call("cosine", value)


static func dependency_info() -> Dictionary:
	var ready: Dictionary = _ensure_loaded()
	return {"ok": true, "path": _path, "mode": _mode} if ready.ok else ready


static func _ensure_loaded() -> Dictionary:
	if _attempted: return {"ok": true} if _implementation != null else _error.duplicate()
	_attempted = true
	var source: String = ProjectSettings.globalize_path("res://").path_join(SOURCE_RELATIVE_PATH).simplify_path()
	var located: Dictionary = _resolve_location(source, PACKAGED_RESOURCE_PATH)
	if not located.ok:
		_error = located
		return _error.duplicate()
	var script: GDScript = ResourceLoader.load(located.path, "GDScript") as GDScript
	if script == null or not script.can_instantiate():
		_error = _missing("Cannot load cosine dependency: " + located.path)
		return _error.duplicate()
	var entries: Dictionary = {"cos_bits": false, "cosine": false}
	for method: Dictionary in script.get_script_method_list():
		var name: String = str(method.get("name", ""))
		if entries.has(name): entries[name] = true
	if not entries.cos_bits or not entries.cosine:
		_error = _missing("Cosine dependency does not expose the required raw-word and value interfaces.")
		return _error.duplicate()
	_implementation = script
	_path = located.path
	_mode = located.mode
	return {"ok": true}


static func _resolve_location(source: String, packaged: String) -> Dictionary:
	if ResourceLoader.exists(packaged, "GDScript"): return {"ok": true, "path": packaged, "mode": "packaged_resource"}
	if source.is_absolute_path() and FileAccess.file_exists(source): return {"ok": true, "path": source, "mode": "source_checkout"}
	return _missing("Cosine requires " + source + " or its separately packaged resource " + packaged + ".")


static func _missing(reason: String) -> Dictionary:
	return {"ok": false, "error_type": "MissingDependency", "error": reason}
