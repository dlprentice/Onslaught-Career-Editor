# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## Source recipe for the existing Sun Sprite consumer. Pixels and parsed data
## are transient; a saved public recipe contains only these production routes.
const SetFile = preload("res://Client/particle_set.gd")
const Resolver = preload("res://Client/particle_effect_resolver.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const MAIN_SET: String = "res://Assets/Level100/ParticleSets/MainSet.par"
const MAIN_SET_SHA256: String = "a51fe4419b55e1af132e31c6b3cd8133c937745d8f4ab691eb5a0d81017ded06"

@export_file("*.par") var source_path: String = MAIN_SET
@export var descriptor_name: String = "Sun Sprite"


func read_layer() -> Dictionary:
	if source_path != MAIN_SET or descriptor_name != "Sun Sprite":
		return _failure("Faithful sun admission requires the original MainSet/Sun Sprite recipe; preserve deliberate overrides separately.")
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(source_path)
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(bytes)
	if hash.finish().hex_encode() != MAIN_SET_SHA256:
		return _failure("The sun particle input is missing or differs from its existing provenance pin.")
	var parsed: Dictionary = SetFile.parse_bytes(bytes)
	if not parsed.ok:
		return parsed
	var resolved: Dictionary = Resolver.resolve(parsed.value, descriptor_name)
	if not resolved.ok:
		return resolved
	var plan: Dictionary = resolved.value
	if not plan.unimplemented.is_empty() or plan.layers.size() != 1:
		return _failure("Sun Sprite must remain one resolved sprite with no unimplemented elements.")
	var layer: Dictionary = plan.layers[0]
	if not Text.equals_text(layer.texture_name, "sun3.tga") or layer.blend_mode != 0:
		return _failure("Sun Sprite must retain its one shipped additive sun3.tga texture.")
	return {"ok": true, "value": layer.duplicate(true)}


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
