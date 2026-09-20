# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## An explicit frozen editor projection, not a campaign or gameplay outcome.
## Runtime uses the existing frontend session's settled projection instead.
const GRADE_BYTES: Array[int] = [65, 66, 67, 68, 69, 83]

@export var world_finished: int = 100:
	set(value):
		world_finished = value
		emit_changed()
@export_enum("Aborted", "Defeat", "Victory") var mission_status: int = 2:
	set(value):
		mission_status = value
		emit_changed()
@export_enum("Hidden", "Complete", "Incomplete") var primary_objectives: int = 1:
	set(value):
		primary_objectives = value
		emit_changed()
@export_enum("Hidden", "Complete", "Incomplete") var secondary_objectives: int = 2:
	set(value):
		secondary_objectives = value
		emit_changed()
## Explicit illustrative grade. This does not supply ranking or score inputs.
@export_enum("None", "A", "B", "C", "D", "E", "S") var grade: int = 1:
	set(value):
		grade = value
		emit_changed()
@export var fallback_level_name: String = "":
	set(value):
		fallback_level_name = value
		emit_changed()


func snapshot() -> Dictionary:
	return {"world_finished": world_finished, "mission_status": mission_status,
		"primary_objectives": primary_objectives, "secondary_objectives": secondary_objectives,
		"grade_byte": null if grade <= 0 or grade > GRADE_BYTES.size() else GRADE_BYTES[grade - 1],
		"new_goodie_count": 0, "first_goodie": false}
