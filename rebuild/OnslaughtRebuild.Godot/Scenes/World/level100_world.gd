# SPDX-License-Identifier: GPL-3.0-or-later
extends Node3D
## The Level 100 world view: root of the imported private Level100.tscn. The
## offline import runs build_imported_scene() on a fresh node; gameplay
## instantiates the saved scene and initialize() binds its existing nodes.
## Only immutable Core facts arrive per frame through the simulation bridge;
## transforms, clocks, camera state, feet and actor/projectile lifecycles belong
## to the native presentation owners (world_presentation.gd, world_entities.gd).

const HeightField = preload("res://Scenes/World/height_field.gd")
const TerrainAppearance = preload("res://Scenes/World/terrain_appearance.gd")
const StaticWorld = preload("res://Scenes/World/level100_static_world.gd")
const SkyBox = preload("res://Scenes/World/level100_sky.gd")
const ObjMesh = preload("res://Scenes/World/curated_obj_mesh.gd")
const AyaTexture = preload("res://Scenes/Shared/retail_aya_texture.gd")
const FixedFunction = preload("res://Scenes/Shared/retail_fixed_function_material.gd")
const Targets = preload("res://Client/target_presentation.gd")
const WorldPresentationScript = preload("res://Scenes/World/world_presentation.gd")
const PulseImpact = preload("res://Scenes/World/pulse_impact.gd")
const VulcanImpact = preload("res://Scenes/World/vulcan_impact.gd")
const DestructionEffect = preload("res://Scenes/World/destruction_effect.gd")
const Words = preload("res://Core/retail_float24.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")

const ENTITY_SCENE_PATH: String = "res://Scenes/World/EntityPresentation.tscn"
const WORLD_PRESENTATION_SCENE_PATH: String = "res://Scenes/World/WorldPresentation.tscn"
const SUN_SCENE_PATH: String = "res://Scenes/World/SunSprite.tscn"
const PULSE_IMPACT_SCENE_PATH: String = "res://Scenes/World/PulseImpact.tscn"
const VULCAN_IMPACT_SCENE_PATH: String = "res://Scenes/World/VulcanImpact.tscn"
const TARGET_TANK_DESTRUCTION_SCENE_PATH: String = "res://Scenes/World/TargetTankDestruction.tscn"
const TARGET_DRONE_DESTRUCTION_SCENE_PATH: String = "res://Scenes/World/TargetDroneDestruction.tscn"
const FACILITY_DESTRUCTION_SCENE_PATH: String = "res://Scenes/World/FacilityDestruction.tscn"
const ROOT_TEXTURE_PATH: String = "res://Assets/Level100/Source/level100-root-terrain.rgb565.bin"
const HIERARCHY_PATH: String = "res://Assets/Level100/Source/level100-terrain-hierarchy.bin"
const DETAIL_TEXTURE_PATH: String = "res://Assets/Level100/Textures/terrain-detail-00.texture.aya"
const CLOUD_SHADOW_PATH: String = "res://Assets/Level100/Textures/terrain-cloud-shadow.texture.aya"
## 0.001f: Core positions are millimetres; BEA X/Y are horizontal and Z is down.
const UNITS_TO_METERS: float = 0.0010000000474974513
## 2*atan(0.75), from the released binary rather than fitted:
## CDXEngine__SetProjectionMatrix (0x00550b10) builds proj[0][0] = near/viewport_w
## and proj[1][1] = near/viewport_h, CDXEngine__Render (0x0053e670) passes
## viewport_w = near*zoom and viewport_h = near*zoom*aspect, and
## CCamera__GetAspectRatio (0x0041b070) returns the constant 0.75 outside
## multiplayer. Unzoomed play is 90 degrees horizontal and 73.739795 vertical
## (player-camera-attach-and-mesh-hfov-2026-07-26.md).
const RETAIL_VERTICAL_FOV_DEGREES: float = 73.739795
## The same 0.75, as the tangent the frustum projection is built from.
const RETAIL_TAN_VERTICAL_HALF_FOV: float = 0.75
const RETAIL_NEAR_PLANE: float = 0.1
const RETAIL_FAR_PLANE: float = 700.0
## Retail's cockpit render thing composes CCockpit+0x2c (its orientation-offset
## "shake" matrix) onto the battle engine's orientation (virtual at 0x004254f0),
## so the drawn cockpit basis is the camera basis pre-multiplied by it. Read from
## a running copy (local-lab/safe-copy-bea-pristine/BEA.exe, sha256 E1436EF7...
## FADF4) at the Level 100 cockpit draw (0x0053bb50..0x0053ec6f window, dumped at
## 0x0053bb56, three identical windows, memory reads only): a proper rotation of
## 2.877224 degrees. It closes the captured SetTransform values to 3.080e-07.
## Measured and identified, not derived: the shake updater (0x00424ca0) reads
## an identity CCockpit+0xb0 with every shake input zero, and whether +0x2c is a
## latched state, a second updater's write (0x004250f0) or level-entry residue is
## open. It is not the Camera01 node and not the terrain normal. Correct for
## Level 100's single frozen pose only (local-lab/COMPOSITION-RESIDUAL-2026-07-26.md).
const RETAIL_LEVEL100_COCKPIT_ORIENTATION_OFFSET: Basis = Basis(
	Vector3(0.99880058, 0.03836670, 0.03041990),
	Vector3(-0.03870098, 0.99919593, 0.01047720),
	Vector3(-0.02999347, -0.01164191, 0.99948227))
## "Not modelled": a cockpit without an observed offset keeps the camera basis.
const RETAIL_NO_COCKPIT_ORIENTATION_OFFSET: Basis = Basis.IDENTITY
## Chrome3 reflection strength 0x3E4CCCCC, measured in the MSHT/TEXB records.
const CHROME_REFLECTION_OPACITY: float = 0.199999988079071
const TARGET_TANK_GROUP: String = "layers-00000000-ffffffff-00000001-ffffffff-ffffffff-ffffffff"
const TRANSPORTER_LIFTER01_GROUP: String = "layers-00000002-ffffffff-00000001-ffffffff-ffffffff-ffffffff"
const WAREHOUSE_BASE_GROUP: String = "layers-00000000-ffffffff-ffffffff-ffffffff-ffffffff-ffffffff"
const WAREHOUSE_M001_OVERLAY_GROUP: String = "layers-00000001-ffffffff-ffffffff-ffffffff-00000005-ffffffff"
const WAREHOUSE_M002_OVERLAY_GROUP: String = "layers-00000003-ffffffff-ffffffff-ffffffff-00000005-ffffffff"
const DXT2: int = 1
enum Effect { NONE = 0, PULSE_IMPACT = 1, VULCAN_IMPACT = 2, TARGET_DESTROYED = 3, DRONE_DESTROYED = 4, FACILITY_DESTROYED = 5 }

var _bridge: RefCounted
var _terrain_bytes := PackedByteArray()
var _terrain: RefCounted
var _terrain_appearance: RefCounted
var _terrain_mesh_instance: MeshInstance3D
var _sky: MeshInstance3D
var _sun: MeshInstance3D
var _static_world: Dictionary = {}
var _player_root: Node3D
var _player_body_pivot: Node3D
var _walker: Node3D
var _jet: Node3D
var _cockpit: Node3D
var _walker_counts: Dictionary = {}
var _jet_counts: Dictionary = {}
var _cockpit_counts: Dictionary = {}
var _camera: Camera3D
var _entity_presentation: Node
var _world_presentation: Node
## [{definition_name, mesh_binding, mesh}] in the original catalogue order.
var _target_assets: Array[Dictionary] = []
var _chrome3_texture: Texture2D
var _warehouse_overlay_texture: Texture2D
var _particle_presentation_seconds: float = 0.0
var _target_visual_count: int = 0
var _projectile_visual_count: int = 0
var _target_surface_count: int = 0
var _terrain_vertex_count: int = 0
var _terrain_triangle_count: int = 0
var show_hud: bool = false
var opening_pan_active: bool = false


## The offline import entry. Runtime instantiates the saved scene instead, and
## editor inspection executes none of this.
func build_imported_scene(bridge: RefCounted) -> Dictionary:
	_bridge = bridge
	name = "WorldView"
	var steps: Array[Callable] = [_build_terrain, _build_environment, _build_static_world, _load_shared_textures,
		_build_targets, _build_player, _build_camera, _create_entity_presentation, _admit_effect_artwork,
		_configure_entity_presentation, _create_world_presentation, _configure_world_presentation]
	for step: Callable in steps:
		var result: Dictionary = step.call()
		if not result.ok:
			return result
	return render(0.0, 0.0)


## Adds the production target meshes the entity presentation spawns from, as
## hidden resources on this scene rather than additional actors.
func add_imported_actor_resources() -> void:
	var meshes := Node3D.new()
	meshes.name = "ActorMeshes"
	meshes.visible = false
	meshes.set_meta("purpose", "Production meshes for later script-spawned actors; not additional actors")
	add_child(meshes)
	for ordinal: int in range(_target_assets.size()):
		var node := MeshInstance3D.new()
		node.name = "Mesh%d" % ordinal
		node.mesh = _target_assets[ordinal].mesh
		node.set_meta("definition", _target_assets[ordinal].definition_name)
		node.set_meta("mesh_binding", _target_assets[ordinal].mesh_binding)
		meshes.add_child(node)


## Binds the saved production scene's nodes to fresh native owners and draws
## the first frame from the bridge's current snapshot.
func initialize(bridge: RefCounted) -> Dictionary:
	_bridge = bridge
	var terrain_bytes: Dictionary = _bridge.GetHeightFieldBytes()
	if not terrain_bytes.ok:
		return terrain_bytes
	_terrain_bytes = terrain_bytes.value
	_terrain_mesh_instance = get_node("RetailLevel100HeightField")
	var terrain: Dictionary = HeightField.from_bytes(_terrain_bytes, _terrain_mesh_instance.mesh)
	if not terrain.ok:
		return _invalid(terrain.error)
	_terrain = terrain.value
	var appearance: Dictionary = _load_terrain_appearance(_terrain_mesh_instance.material_override)
	if not appearance.ok:
		return appearance
	_sky = get_node("RetailLevel100KempyCube25")
	var sun: Dictionary = _configure_sun(get_node("RetailLevel100SunSprite"), true)
	if not sun.ok:
		return sun
	var static_world: Dictionary = StaticWorld.bind_scene(get_node("RetailLevel100StaticWorld"), _terrain, _terrain_bytes)
	if not static_world.ok:
		return static_world
	_static_world = static_world.value
	_player_root = get_node("PlayerVisual")
	_player_body_pivot = _player_root.get_node("BodyPivot")
	for pair: Array in [["walker", "RetailAquilaWalker"], ["jet", "RetailAquilaJet"]]:
		var bound: Dictionary = _configure_aquila(_player_body_pivot.get_node(pair[1]), pair[0], true)
		if not bound.ok:
			return bound
	_camera = get_node("RetailOpeningAndFirstPersonCamera")
	var cockpit: Dictionary = _configure_aquila(_camera.get_node("RetailAquilaCockpit"), "cockpit", true)
	if not cockpit.ok:
		return cockpit
	_target_assets.clear()
	for child: Node in get_node("ActorMeshes").get_children():
		var source := child as MeshInstance3D
		_target_assets.append({"definition_name": String(source.get_meta("definition")),
			"mesh_binding": String(source.get_meta("mesh_binding")), "mesh": source.mesh})
	_entity_presentation = get_node("EntityPresentation")
	for step: Callable in [_admit_effect_artwork, _configure_entity_presentation]:
		var result: Dictionary = step.call()
		if not result.ok:
			return result
	_world_presentation = get_node("WorldPresentation")
	var configured: Dictionary = _configure_world_presentation()
	if not configured.ok:
		return configured
	var offset: Dictionary = WorldPresentationScript.apply_pixel_centre_offset(self, _camera)
	if not offset.ok:
		return offset
	return render(0.0, 0.0)


func render(interpolation_alpha: float, frame_delta: float) -> Dictionary:
	var facts: Dictionary = _bridge.WorldFrameFacts(interpolation_alpha, frame_delta)
	if not facts.ok:
		return facts
	var result: Variant = _world_presentation.render_frame(facts.value)
	return _presentation_result(result, facts.value)


func consume_weapon_fire_facts(weapons: Array) -> Dictionary:
	return _presentation_result(_world_presentation.queue_weapon_events(weapons), {})


func consume_destruction_facts(events: Array, tick: int) -> Dictionary:
	for event: Dictionary in events:
		var position := Vector3(_meters(event.x), _meters(-int(event.z)), _meters(-int(event.y)))
		match int(event.effect_kind):
			Effect.NONE:
				pass
			Effect.PULSE_IMPACT:
				var started: Dictionary = _spawn(PULSE_IMPACT_SCENE_PATH, "PulseImpact%d-%d" % [event.actor_id, tick],
					position, [_particle_presentation_seconds])
				if not started.ok:
					return started
			Effect.VULCAN_IMPACT:
				# Mech Bullet Hit Unit Effect schedules Spark Anim Sprite at Time 0:
				# alparticle2.tga, additive, Radius 0.3 -> 1.0, Life 5 turns, cells
				# 11..15 PlayOnce at 0.8 cells/turn. Two sibling emitters stay open.
				var started: Dictionary = _spawn(VULCAN_IMPACT_SCENE_PATH, "VulcanImpact%d-%d" % [event.actor_id, tick], position, [])
				if not started.ok:
					return started
			Effect.TARGET_DESTROYED:
				var started: Dictionary = _spawn(TARGET_TANK_DESTRUCTION_SCENE_PATH, "TargetTankDestruction%d" % event.actor_id, position, [])
				if not started.ok:
					return started
			Effect.DRONE_DESTROYED:
				var started: Dictionary = _spawn(TARGET_DRONE_DESTRUCTION_SCENE_PATH, "TargetDroneDestruction%d" % event.actor_id, position, [])
				if not started.ok:
					return started
			Effect.FACILITY_DESTROYED:
				var started: Dictionary = _spawn(FACILITY_DESTRUCTION_SCENE_PATH, "FacilityDestruction%d" % event.actor_id, position, [])
				if not started.ok:
					return started
			_:
				return _invalid("Core exposed unknown Level 100 destruction effect %d." % event.effect_kind)
	return {"ok": true}


## The world half of the smoke report.
func presentation_facts() -> Dictionary:
	var water_counts: Dictionary = _static_world.get("water_counts", {})
	return {"show_hud": show_hud, "opening_pan_active": opening_pan_active,
		"player_visual_present": is_instance_valid(_player_root),
		"retail_aquila_meshes_present": is_instance_valid(_walker) and is_instance_valid(_jet)
			and int(_walker_counts.get("surface_count", 0)) > 0 and int(_jet_counts.get("surface_count", 0)) > 0,
		"retail_aquila_surface_count": int(_walker_counts.get("surface_count", 0)) + int(_jet_counts.get("surface_count", 0)),
		"retail_aquila_part_count": int(_walker_counts.get("part_count", 0)),
		"retail_aquila_animated_part_count": int(_walker_counts.get("animated_count", 0)),
		"retail_aquila_standing_clearance": F.value(_walker_counts.get("standing_clearance", 0.0)),
		"retail_cockpit_surface_count": int(_cockpit_counts.get("surface_count", 0)),
		"level100_player_start_relative_height": StaticWorld.sample(_terrain, 0.0, 0.0),
		"retail_level100_static_object_count": _static_world.objects.size(),
		"retail_level100_static_object_surface_count": _static_world.surface_count,
		"retail_level100_pine_count": _static_world.pine_count,
		"retail_level100_water_present": is_instance_valid(_static_world.water),
		"retail_level100_water_grid_vertex_count": int(water_counts.get("grid_vertices", 0)),
		"retail_level100_water_grid_triangle_count": int(water_counts.get("grid_triangles", 0)),
		"retail_level100_shoreline_triangle_count": int(water_counts.get("shoreline_triangles", 0)),
		"retail_level100_target_surface_count": _target_surface_count,
		"retail_level100_terrain_vertex_count": _terrain_vertex_count,
		"retail_level100_terrain_triangle_count": _terrain_triangle_count,
		"retail_level100_sky_surface_count": 0 if _sky == null or _sky.mesh == null else _sky.mesh.get_surface_count(),
		"target_visual_count": _target_visual_count}


static func cockpit_orientation_offset() -> Basis:
	return RETAIL_LEVEL100_COCKPIT_ORIENTATION_OFFSET


func _build_terrain() -> Dictionary:
	var bytes: Dictionary = _bridge.GetHeightFieldBytes()
	if not bytes.ok:
		return bytes
	_terrain_bytes = bytes.value
	var terrain: Dictionary = HeightField.from_bytes(_terrain_bytes, null)
	if not terrain.ok:
		return _invalid(terrain.error)
	_terrain = terrain.value
	var appearance: Dictionary = _load_terrain_appearance(null)
	if not appearance.ok:
		return appearance
	_terrain_mesh_instance = MeshInstance3D.new()
	_terrain_mesh_instance.name = "RetailLevel100HeightField"
	_terrain_mesh_instance.mesh = _terrain.get_mesh()
	_terrain_mesh_instance.material_override = _terrain_appearance.get_material()
	add_child(_terrain_mesh_instance)
	return {"ok": true}


func _load_terrain_appearance(scene_material: Variant) -> Dictionary:
	var metadata: Dictionary = _terrain.metadata()
	var facts: Dictionary = {"mixer_set": metadata.mixer_set, "detail_texture": metadata.detail_texture,
		"sun_color_rgb24": metadata.sun_color_rgb24, "anti_sun_color_rgb24": metadata.anti_sun_color_rgb24,
		"ambient_color_rgb24": metadata.ambient_color_rgb24, "fog_color": metadata.fog_color,
		"fog_density": metadata.fog_density}
	var loaded: Dictionary = TerrainAppearance.load_paths(ROOT_TEXTURE_PATH, HIERARCHY_PATH, DETAIL_TEXTURE_PATH,
		CLOUD_SHADOW_PATH, facts, scene_material)
	if not loaded.ok:
		return loaded
	_terrain_appearance = loaded.value
	return {"ok": true}


func _build_environment() -> Dictionary:
	var metadata: Dictionary = _terrain.metadata()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = metadata.fog_color
	environment.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	var world_environment := WorldEnvironment.new()
	world_environment.name = "WorldEnvironment"
	world_environment.environment = environment
	add_child(world_environment)
	var sky: Dictionary = SkyBox.create(metadata.sky_cube)
	if not sky.ok:
		return sky
	_sky = sky.value
	add_child(_sky)
	# The cube paints its own soft sun disc; the flare is a separate particle the
	# engine adds every frame (references/Onslaught/DXEngine.cpp:968-1066), so it
	# is its own node here too, following the camera rather than the world.
	var sun: MeshInstance3D = (load(SUN_SCENE_PATH) as PackedScene).instantiate()
	var configured: Dictionary = _configure_sun(sun, false)
	if not configured.ok:
		sun.free()
		return configured
	add_child(sun)
	return {"ok": true}


func _configure_sun(root: MeshInstance3D, retain_saved: bool) -> Dictionary:
	if not root.has_method("configure"):
		return _invalid("The imported sun is stale. Rebuild the private production scene.")
	var result: Dictionary = root.configure(_terrain_bytes, retain_saved)
	if not result.ok:
		return _invalid(result.error)
	_sun = root
	return {"ok": true}


func _build_static_world() -> Dictionary:
	var built: Dictionary = StaticWorld.build(_terrain, _terrain_bytes)
	if not built.ok:
		return built
	_static_world = built.value
	add_child(_static_world.root)
	return {"ok": true}


func _load_shared_textures() -> Dictionary:
	var chrome: Dictionary = _load_texture("res://Assets/Level100/StaticWorld/Textures/meshtex-chrome3.texture.aya", 128, 128)
	if not chrome.ok:
		return chrome
	_chrome3_texture = chrome.value
	var overlay: Dictionary = _load_texture("res://Assets/Level100/Textures/material-overlay-a8trust5.texture.aya", 128, 128)
	if not overlay.ok:
		return overlay
	_warehouse_overlay_texture = overlay.value
	return {"ok": true}


func _build_targets() -> Dictionary:
	var chrome: Dictionary = _layer(_chrome3_texture, CHROME_REFLECTION_OPACITY)
	var tank_texture: Dictionary = _load_texture("res://Assets/Level100/Textures/target-tank.texture.aya", 512, 512)
	if not tank_texture.ok:
		return tank_texture
	var tank_material: Dictionary = _retail_material(tank_texture.value, null, chrome, null)
	if not tank_material.ok:
		return tank_material
	var tank_mesh: Dictionary = ObjMesh.load_mesh("res://Assets/Level100/level100-target-tank.obj",
		{TARGET_TANK_GROUP: tank_material.value})
	if not tank_mesh.ok:
		return tank_mesh
	var truck_texture: Dictionary = _load_texture("res://Assets/Level100/Textures/target-truck.texture.aya", 512, 512)
	if not truck_texture.ok:
		return truck_texture
	var truck_material: Dictionary = _retail_material(truck_texture.value, null, chrome, null)
	if not truck_material.ok:
		return truck_material
	var truck_mesh: Dictionary = ObjMesh.load_mesh("res://Assets/Level100/level100-target-truck.obj",
		{TARGET_TANK_GROUP: truck_material.value})
	if not truck_mesh.ok:
		return truck_mesh
	var m001_texture: Dictionary = _load_texture("res://Assets/Level100/Textures/target-warehouse-m001.texture.aya", 512, 512)
	if not m001_texture.ok:
		return m001_texture
	var m002_texture: Dictionary = _load_texture("res://Assets/Level100/Textures/target-warehouse-m002.texture.aya", 512, 512)
	if not m002_texture.ok:
		return m002_texture
	var overlay: Dictionary = _layer(_warehouse_overlay_texture, 1.0, Vector2.ZERO, Vector2(20.0, 20.0))
	var m001: Dictionary = _retail_material(m001_texture.value, null, null, null)
	var m001_overlay: Dictionary = _retail_material(m001_texture.value, null, null, overlay)
	var m002_overlay: Dictionary = _retail_material(m002_texture.value, null, null, overlay)
	for material: Dictionary in [m001, m001_overlay, m002_overlay]:
		if not material.ok:
			return material
	var warehouse_mesh: Dictionary = ObjMesh.load_mesh("res://Assets/Level100/level100-target-warehouse.obj",
		{WAREHOUSE_BASE_GROUP: m001.value, WAREHOUSE_M001_OVERLAY_GROUP: m001_overlay.value,
		WAREHOUSE_M002_OVERLAY_GROUP: m002_overlay.value})
	if not warehouse_mesh.ok:
		return warehouse_mesh
	# Task #114: m_FA_F24_training.msh.aya serves the Air Trainer and all nine
	# Target Drones, and its material table is the Target Tank's verbatim (both
	# name f_pulsetank_training and Chrome3 at strength 0x3E4CCCCC, one group).
	var air_trainer_mesh: Dictionary = ObjMesh.load_mesh("res://Assets/Level100/level100-air-trainer.obj",
		{TARGET_TANK_GROUP: tank_material.value})
	if not air_trainer_mesh.ok:
		return air_trainer_mesh
	# The U-17 Highside Transporter's table is (f_lifter02, Chrome3, f_lifter01,
	# Chrome3). Watch the inversion: group ...-00000000-... is f_lifter02 and
	# group ...-00000002-... is f_lifter01.
	var lifter01: Dictionary = _load_texture("res://Assets/Level100/Textures/transporter-lifter01.texture.aya", 512, 512)
	if not lifter01.ok:
		return lifter01
	var lifter02: Dictionary = _load_texture("res://Assets/Level100/Textures/transporter-lifter02.texture.aya", 512, 512)
	if not lifter02.ok:
		return lifter02
	var lifter02_material: Dictionary = _retail_material(lifter02.value, null, _layer(_chrome3_texture, CHROME_REFLECTION_OPACITY), null)
	if not lifter02_material.ok:
		return lifter02_material
	var lifter01_material: Dictionary = _retail_material(lifter01.value, null, _layer(_chrome3_texture, CHROME_REFLECTION_OPACITY), null)
	if not lifter01_material.ok:
		return lifter01_material
	var transporter_mesh: Dictionary = ObjMesh.load_mesh("res://Assets/Level100/level100-transporter.obj",
		{TARGET_TANK_GROUP: lifter02_material.value, TRANSPORTER_LIFTER01_GROUP: lifter01_material.value})
	if not transporter_mesh.ok:
		return transporter_mesh
	var bindings: Array[Dictionary] = Targets.rendered_bindings()
	var by_name: Dictionary = {}
	for binding: Dictionary in bindings:
		by_name[_native(binding.definition_name)] = _native(binding.mesh_binding)
	_target_assets.clear()
	for row: Array in [["Target Tank", tank_mesh], ["Target Truck", truck_mesh], ["Warehouse", warehouse_mesh],
			["Air Trainer", air_trainer_mesh], ["Target Drone", air_trainer_mesh],
			["U-17 Highside Transporter", transporter_mesh]]:
		_target_assets.append({"definition_name": row[0], "mesh_binding": by_name[row[0]], "mesh": row[1].value})
	return {"ok": true}


func _build_player() -> Dictionary:
	_player_root = Node3D.new()
	_player_root.name = "PlayerVisual"
	add_child(_player_root)
	_player_body_pivot = Node3D.new()
	_player_body_pivot.name = "BodyPivot"
	_player_root.add_child(_player_body_pivot)
	for pair: Array in [["walker", "Walker"], ["jet", "Jet"]]:
		var root: Node3D = (load("res://Scenes/Aquila/%s.tscn" % pair[1]) as PackedScene).instantiate()
		var created: Dictionary = _configure_aquila(root, pair[0], false)
		if not created.ok:
			root.free()
			return created
		_player_body_pivot.add_child(root)
	return {"ok": true}


func _build_camera() -> Dictionary:
	_camera = Camera3D.new()
	_camera.name = "RetailOpeningAndFirstPersonCamera"
	_camera.fov = RETAIL_VERTICAL_FOV_DEGREES
	_camera.near = RETAIL_NEAR_PLANE
	_camera.far = RETAIL_FAR_PLANE
	_camera.current = true
	# Frustum rather than perspective only so the half-pixel translation has a
	# home: KEEP_HEIGHT frustum size is the full vertical near-plane extent, so
	# 2 * near * tan(vfov/2) reproduces the perspective projection exactly.
	_camera.projection = Camera3D.PROJECTION_FRUSTUM
	_camera.size = F.value(F.value(2.0 * _camera.near) * RETAIL_TAN_VERTICAL_HALF_FOV)
	add_child(_camera)
	var offset: Dictionary = WorldPresentationScript.apply_pixel_centre_offset(self, _camera)
	if not offset.ok:
		return offset
	var cockpit: Node3D = (load("res://Scenes/Aquila/Cockpit.tscn") as PackedScene).instantiate()
	var created: Dictionary = _configure_aquila(cockpit, "cockpit", false)
	if not created.ok:
		cockpit.free()
		return created
	_camera.add_child(cockpit)
	# Retail composes CCockpit+0x2c onto the camera orientation before drawing.
	cockpit.basis = cockpit_orientation_offset()
	return {"ok": true}


func _configure_aquila(root: Node3D, profile: String, retain_saved: bool) -> Dictionary:
	if not root.has_method("configure_prepared") or root.get("profile") != profile:
		return _invalid("The imported Aquila is stale. Rebuild the private production scene.")
	var metadata: Dictionary = _terrain.metadata()
	var facts: Dictionary = {"ambient_color_rgb24": metadata.ambient_color_rgb24, "sun_color_rgb24": metadata.sun_color_rgb24,
		"anti_sun_color_rgb24": metadata.anti_sun_color_rgb24, "sunlight_direction": metadata.sunlight_direction,
		"fog_color": metadata.fog_color, "fog_density": metadata.fog_density}
	var result: Dictionary = root.configure_prepared(facts, retain_saved, not retain_saved)
	if not result.ok:
		return {"ok": false, "error_type": result.get("error_type", "InvalidDataException"), "error": result.error}
	var counts: Dictionary = root.counts()
	match profile:
		"walker":
			_walker = root
			_walker_counts = counts
		"jet":
			_jet = root
			_jet_counts = counts
		"cockpit":
			_cockpit = root
			_cockpit_counts = counts
	return {"ok": true}


func _create_entity_presentation() -> Dictionary:
	_entity_presentation = (load(ENTITY_SCENE_PATH) as PackedScene).instantiate()
	add_child(_entity_presentation)
	set_editable_instance(_entity_presentation, true)
	return {"ok": true}


## Admits the production effect recipes in the original six-load order; the
## effect and editor share each native texture recipe.
func _admit_effect_artwork() -> Dictionary:
	for admitted: Dictionary in [DestructionEffect.admit_artwork("animated_blob"), PulseImpact.admit_artwork(),
			VulcanImpact.admit_artwork(), DestructionEffect.admit_artwork("flash_medium"),
			DestructionEffect.admit_artwork("explosion_animated"), DestructionEffect.admit_artwork("fireball")]:
		if not admitted.ok:
			return admitted
	return {"ok": true}


func _configure_entity_presentation() -> Dictionary:
	var assets: Array = []
	for asset: Dictionary in _target_assets:
		assets.append({"definition_name": _units(asset.definition_name), "mesh_binding": _units(asset.mesh_binding),
			"mesh": asset.mesh})
	var targets: Dictionary = _bridge.TargetFacts()
	if not targets.ok:
		return targets
	var result: Variant = _entity_presentation.configure(self, _camera, assets, targets.value)
	if not result is Dictionary:
		return _failure("InvalidOperationException", "Native entity presentation aborted without a completion result.")
	if not result.get("ok", false):
		return {"ok": false, "error_type": result.get("error_type", "InvalidOperationException"),
			"error": result.get("error", "Native entity presentation failed.")}
	_store_entity_counts(result)
	return {"ok": true}


func _create_world_presentation() -> Dictionary:
	_world_presentation = (load(WORLD_PRESENTATION_SCENE_PATH) as PackedScene).instantiate()
	add_child(_world_presentation)
	set_editable_instance(_world_presentation, true)
	return {"ok": true}


func _configure_world_presentation() -> Dictionary:
	var config: Dictionary = _bridge.WorldConfigFacts()
	if not config.ok:
		return config
	var bindings: Dictionary = {"world": self, "player": _player_root, "body": _player_body_pivot, "walker": _walker,
		"jet": _jet, "cockpit": _cockpit, "camera": _camera, "sky": _sky, "sun": _sun, "terrain": _terrain,
		"appearance": _terrain_appearance, "entities": _entity_presentation, "water": _static_world.water,
		"scenery": _static_world.animation}
	var settings: Dictionary = {"pan_duration_ticks": config.value.pan_duration_ticks,
		"control_view_handoff_lead_ticks": config.value.control_view_handoff_lead_ticks,
		"near_bits": Words.store_word(RETAIL_NEAR_PLANE), "far_bits": Words.store_word(RETAIL_FAR_PLANE),
		"walker_height_mm": config.value.walker_height_mm, "target_count": _target_visual_count,
		"projectile_count": _projectile_visual_count, "target_surface_count": _target_surface_count,
		"terrain_vertex_count": _terrain_vertex_count, "terrain_triangle_count": _terrain_triangle_count}
	return _presentation_result(_world_presentation.configure(bindings, settings), {})


## Detached facts survive a later stage failure: a failed frame does not roll
## back the native writes before it.
func _presentation_result(returned: Variant, facts: Dictionary) -> Dictionary:
	if not returned is Dictionary:
		return _failure("InvalidOperationException", "Native world presentation aborted without a completion result.")
	var result: Dictionary = returned
	if result.has("particle_seconds_bits"):
		_particle_presentation_seconds = Words.read_word(result.particle_seconds_bits)
		show_hud = result.show_hud
		opening_pan_active = result.opening_pan
		_store_entity_counts(result)
		_terrain_vertex_count = result.terrain_vertex_count
		_terrain_triangle_count = result.terrain_triangle_count
	if result.has("host_exception_id"):
		# Core's target projection failed; report its own error at the native
		# frame's projection stage, never as an empty actor list.
		for key: String in ["previous", "current"]:
			var targets: Variant = facts.get(key, {}).get("targets") if facts.get(key) is Dictionary else null
			if targets is Dictionary and targets.get("host_exception_id") == result.host_exception_id:
				return {"ok": false, "error_type": targets.error_type, "error": targets.error}
		return _failure("InvalidOperationException", "Unknown world projection failure token.")
	if typeof(result.get("ok")) != TYPE_BOOL:
		return _failure("InvalidOperationException", "Native world presentation returned no completion flag.")
	if result.ok:
		return {"ok": true, "show_hud": show_hud, "opening_pan_active": opening_pan_active}
	return {"ok": false, "error_type": result.get("error_type", "InvalidOperationException"),
		"error": result.get("error", "Native world presentation failed.")}


func _store_entity_counts(result: Dictionary) -> void:
	_target_visual_count = result.target_count
	_projectile_visual_count = result.projectile_count
	_target_surface_count = result.target_surface_count


func _spawn(path: String, node_name: String, position_value: Vector3, arguments: Array) -> Dictionary:
	var root: Node3D = (load(path) as PackedScene).instantiate()
	root.name = node_name
	root.position = position_value
	add_child(root)
	return _presentation_result(root.callv("start", arguments), {})


func _load_texture(path: String, width: int, height: int) -> Dictionary:
	var loaded: Dictionary = AyaTexture.new().load_texture_checked(path, width, height, DXT2, null, null)
	return loaded if loaded.ok else _invalid(loaded.error)


func _retail_material(texture: Texture2D, dot3: Variant, reflection: Variant, overlay: Variant) -> Dictionary:
	var layers: Array = [_layer(texture), dot3, reflection, null, overlay, null]
	var created: Dictionary = FixedFunction.create(layers, StaticWorld.terrain_facts(_terrain.metadata()))
	return created if created.ok else {"ok": false, "error_type": created.get("error_type", "InvalidDataException"),
		"error": created.get("error", "Native fixed-function material failed.")}


static func _layer(texture: Texture2D, opacity: float = 1.0, offset: Vector2 = Vector2.ZERO, scale: Vector2 = Vector2.ONE) -> Dictionary:
	return {"texture": texture, "opacity": F.value(opacity), "offset": offset, "scale": scale, "blend_texture_alpha": false}


static func _meters(millimeters: int) -> float:
	return F.value(F.value(float(millimeters)) * UNITS_TO_METERS)


static func _units(text: String) -> PackedInt32Array:
	var result := PackedInt32Array()
	for index: int in range(text.length()):
		var code: int = text.unicode_at(index)
		if code > 0xffff:
			code -= 0x10000
			result.append(0xd800 + (code >> 10))
			result.append(0xdc00 + (code & 0x3ff))
		else:
			result.append(code)
	return result


static func _native(units: PackedInt32Array) -> String:
	var text: String = ""
	for unit: int in units:
		text += String.chr(unit)
	return text


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}


static func _invalid(message: String) -> Dictionary:
	return _failure("InvalidDataException", message)
