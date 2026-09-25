# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Original forwarding adapter. The separately attributed MIT implementation
## remains in the repository's tools/ support surface, outside the GPL subtree.
## Source checkouts load that explicit absolute path once. A future package may
## supply the named resource from its separately licensed dependency pack; no
## export/package path is established merely by declaring that resource name.

const SOURCE_RELATIVE_PATH: String = "../../tools/godot_compat/invariant_int32_format.gd"
const PACKAGED_RESOURCE_PATH: String = "res://RuntimeDependencies/DotNetInvariantInt32Format.gd"
static var _attempted: bool = false
static var _implementation: GDScript = null
static var _dependency_error: Dictionary = {}
static var _dependency_path: String = ""
static var _dependency_mode: String = ""


static func format_composite(template: Variant, value: Variant) -> Dictionary:
    return _invoke("format_composite", template, value, TYPE_STRING)


static func format_composite_units(template: Variant, value: Variant) -> Dictionary:
    return _invoke("format_composite_units", template, value, TYPE_PACKED_INT32_ARRAY)


static func _invoke(method: StringName, template: Variant, value: Variant, result_type: int) -> Dictionary:
    var admitted: Dictionary = _ensure_loaded()
    if not admitted.ok:
        return admitted
    var result: Variant = _implementation.call(method, template, value)
    if result is Dictionary:
        if result.get("ok") == true and typeof(result.get("value")) == result_type:
            return result
        if result.get("ok") == false and typeof(result.get("error_type")) == TYPE_STRING and typeof(result.get("error")) == TYPE_STRING and not result.has("value"):
            return result
    return {"ok": false, "error_type": "UnsupportedFormat", "error": "The invariant formatting dependency did not return its declared result contract."}


## Read-only diagnostic for the selected source/package boundary. Loading uses
## the same cached script as format_composite; this never creates a scene/node.
static func dependency_info() -> Dictionary:
    var admitted: Dictionary = _ensure_loaded()
    if not admitted.ok:
        return admitted
    return {"ok": true, "path": _dependency_path, "mode": _dependency_mode}


static func _ensure_loaded() -> Dictionary:
    if _attempted:
        return {"ok": true} if _implementation != null else _dependency_error.duplicate()
    _attempted = true
    var source_path: String = ProjectSettings.globalize_path("res://").path_join(SOURCE_RELATIVE_PATH).simplify_path()
    var located: Dictionary = _resolve_location(source_path, PACKAGED_RESOURCE_PATH)
    if not located.ok:
        _dependency_error = located
        return _dependency_error.duplicate()
    var script: GDScript = ResourceLoader.load(located.path, "GDScript") as GDScript
    if script == null or not script.can_instantiate():
        _dependency_error = _missing("The invariant formatting dependency could not be loaded: " + str(located.path))
        return _dependency_error.duplicate()
    var entry_points: Dictionary = {"format_composite": false, "format_composite_units": false}
    for method: Dictionary in script.get_script_method_list():
        var name: String = str(method.get("name", ""))
        if entry_points.has(name):
            entry_points[name] = true
    if not entry_points.format_composite or not entry_points.format_composite_units:
        _dependency_error = _missing("The invariant formatting dependency does not expose both text and UTF-16 entry points: " + str(located.path))
        return _dependency_error.duplicate()
    _implementation = script
    _dependency_path = located.path
    _dependency_mode = located.mode
    return {"ok": true}


static func _resolve_location(source_path: String, packaged_path: String) -> Dictionary:
    # A supplied package takes precedence. A failed load of the selected source
    # is explicit; it does not trigger another implementation or formatter.
    if ResourceLoader.exists(packaged_path, "GDScript"):
        return {"ok": true, "path": packaged_path, "mode": "packaged_resource"}
    if source_path.is_absolute_path() and FileAccess.file_exists(source_path):
        return {"ok": true, "path": source_path, "mode": "source_checkout"}
    return _missing("Invariant formatting requires the source-checkout utility at " + source_path + " or the separately packaged resource " + packaged_path + ".")


static func _missing(reason: String) -> Dictionary:
    return {"ok": false, "error_type": "MissingDependency", "error": reason}
