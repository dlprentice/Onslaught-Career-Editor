# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends AudioStreamPlayer3D
const Recipe = preload("res://Scenes/Audio/retail_audio_stream.gd")
@export var stream_recipe: Recipe

func _validate_property(property: Dictionary) -> void:
	if property.name == "stream":
		property.usage = (int(property.usage) & ~PROPERTY_USAGE_STORAGE) | PROPERTY_USAGE_EDITOR | PROPERTY_USAGE_READ_ONLY
	elif property.name in ["autoplay", "attenuation_model", "max_distance"]:
		property.usage = int(property.usage) | PROPERTY_USAGE_READ_ONLY

func _ready() -> void:
	if Engine.is_editor_hint():
		stop()
