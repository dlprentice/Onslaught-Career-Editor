# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## ParticleEffectResolver.cs's current authored-plan law, including its declared
## omissions and provisional largest-remainder selector allocation. This is not
## a new retail behavior/RNG claim. Source owns the measurement/provenance for
## atlas sizes, 20 game turns/second and the radius-to-quad factor.
## No assets, clock, RNG, nodes or simulation state are read or modified here.
const Plan = preload("res://Client/particle_effect_plan.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const Float32 = preload("res://Core/retail_float24.gd")
const Number = preload("res://Core/invariant_number.gd")
const GAME_TURNS_PER_SECOND: int = 20
const BLEND_MODE_SELECTS_SHIPPED_TEXTURE_FORMAT: int = 0
const MAXIMUM_INSTANCES_PER_EFFECT: int = 256
const AUTHORED_RADIUS_IS_HALF_THE_QUAD_SIDE_BITS: int = 0x40000000
const _TYPE_NAMES: Array[String] = ["", "Sprite", "Emitter", "Modifier", "Selector", "ColourRange",
	"Timeline", "Shape", "Trail", "Mover", "Function", "Mesh", "FoR", "PMesh"]


static func billboard_quad_side(authored_radius_bits: Variant) -> Dictionary:
	if typeof(authored_radius_bits) != TYPE_INT or authored_radius_bits < 0 or authored_radius_bits > 0xffffffff:
		return ResolveState._failure("ArgumentException", "Radius requires a raw UInt32 float word.")
	return {"ok": true, "bits": Float32.store_word(Float32.read_word(authored_radius_bits) * 2.0)}


static func atlas_grid_side(texture_size: Variant) -> Dictionary:
	return ResolveState.atlas_grid_side(texture_size)


static func leaf_texture_name(authored_path: PackedInt32Array) -> PackedInt32Array:
	return ResolveState.leaf_texture_name(authored_path)


static func _lower_scalar(code: int) -> int:
	return ResolveState._lower_scalar(code)


## Accepts the parsed ParticleSet.Set object. All descriptor reads are checked;
## a failed read aborts the entire plan and never exposes partially built layers.
static func resolve(set_value: Variant, effect_name: Variant) -> Dictionary:
	if set_value == null:
		return ResolveState._failure("ArgumentNullException", "Value cannot be null.", "set")
	if effect_name == null:
		return ResolveState._failure("ArgumentNullException", "Value cannot be null.", "effectName")
	var name: Dictionary = Text.units(effect_name)
	if not name.ok: return ResolveState._failure("ArgumentException", name.error, "effectName")
	if name.value.is_empty():
		return ResolveState._failure("ArgumentException", "The value cannot be an empty string.", "effectName")
	if not set_value is RefCounted or not set_value.has_method("require") or not set_value.has_method("find"):
		return ResolveState._failure("ArgumentException", "A parsed particle set is required.", "set")
	var root: Dictionary = set_value.require(name.value)
	if not root.ok: return root
	var state := ResolveState.new(set_value)
	var visited: Dictionary = state.visit(root.value, name.value, 0, null)
	if not visited.ok: return visited
	return Plan.create(name.value, root.value.type_id, state.layers, state.unimplemented)


class ResolveState extends RefCounted:
	var _set: RefCounted
	var _active: Dictionary = {}
	var layers: Array[Dictionary] = []
	var unimplemented: Array = []
	var _instances: int = 0

	static func atlas_grid_side(texture_size: Variant) -> Dictionary:
		if not Plan._i32(texture_size):
			return _failure("ArgumentException", "Texture size requires Int32.")
		match texture_size:
			2: return {"ok": true, "value": 4}
			3: return {"ok": true, "value": 2}
			4: return {"ok": true, "value": 1}
		return _failure("InvalidDataException", _join(["Particle sprite authored an unshipped Texture_Size ", texture_size,
			"; the shipped corpus uses only 2, 3 and 4."]))



	func _init(set_value: RefCounted) -> void:
		_set = set_value

	func visit(descriptor: RefCounted, path: PackedInt32Array, start_turn: int, emitter: Variant) -> Dictionary:
		var key: String = _key(descriptor.name)
		if _active.has(key):
			unimplemented.append(_join([path, ": cyclic reference back to '", descriptor.name, "'"]))
			return {"ok": true}
		_active[key] = true
		var result: Dictionary
		match descriptor.type_id:
			1: result = _add_sprite(descriptor, path, start_turn, emitter)
			2: result = _visit_emitter(descriptor, path, start_turn, emitter)
			6: result = _visit_timeline(descriptor, path, start_turn)
			4: result = _visit_random(descriptor, path, start_turn, emitter)
			12: result = _visit_system(descriptor, path, start_turn)
			_:
				var type_name: String = _TYPE_NAMES[descriptor.type_id] if descriptor.type_id > 0 and descriptor.type_id < _TYPE_NAMES.size() else str(descriptor.type_id)
				unimplemented.append(_join([path, " > ", descriptor.name, ": type ", descriptor.type_id, " (", type_name, ") is authored but not drawn"]))
				result = {"ok": true}
		_active.erase(key)
		return result

	func _visit_timeline(timeline: RefCounted, path: PackedInt32Array, start_turn: int) -> Dictionary:
		var declared: Dictionary = timeline.int_value("Num_Entries")
		if not declared.ok: return declared
		var children: Dictionary = timeline.raw_all("Particle_Descriptor")
		if not children.ok: return children
		var times: Dictionary = timeline.raw_all("Time")
		if not times.ok: return times
		if children.value.size() != declared.value or times.value.size() != declared.value:
			return _failure("InvalidDataException", _join(["Timeline '", timeline.name, "' declares ", declared.value,
				" entries but authors ", children.value.size(), " descriptors and ", times.value.size(), " times."]))
		for index: int in range(declared.value):
			var child_name: PackedInt32Array = children.value[index]
			if _is(child_name, "NONE"): continue
			var time: Dictionary = Number.parse_int32(times.value[index])
			if not time.ok: return time
			var child: Dictionary = _set.find(child_name)
			if not child.ok: return child
			if child.value == null:
				unimplemented.append(_join([path, ": timeline entry '", child_name, "' is not in this set"]))
				continue
			var visited: Dictionary = visit(child.value, _join([path, " > ", child_name]), Plan.int32(start_turn + time.value), null)
			if not visited.ok: return visited
		return {"ok": true}

	func _visit_system(system: RefCounted, path: PackedInt32Array, start_turn: int) -> Dictionary:
		for key: String in ["Initial", "Death"]:
			var reference: Dictionary = system.reference_name(key)
			if not reference.ok: return reference
			if reference.value == null: continue
			var child: Dictionary = _set.find(reference.value)
			if not child.ok: return child
			if child.value == null:
				unimplemented.append(_join([path, ": ", key, " '", reference.value, "' is not in this set"]))
				continue
			var visited: Dictionary = visit(child.value, _join([path, " > ", reference.value]), start_turn, null)
			if not visited.ok: return visited
		var mover: Dictionary = system.reference_name("Mover")
		if not mover.ok: return mover
		if mover.value != null:
			unimplemented.append(_join([path, ": Mover '", mover.value, "' is authored but not applied"]))
		return {"ok": true}

	func _visit_random(random: RefCounted, path: PackedInt32Array, start_turn: int, emitter: Variant) -> Dictionary:
		# Preserve the current expected-count reconstruction. Retail's process-
		# global CRT RNG phase is unresolved; no random draw is invented here.
		var starts: Array = [start_turn] if emitter == null else emitter.start_turns
		var branches: Array[Dictionary] = []
		var total_weight: int = 0
		for index: int in range(4):
			var child: Dictionary = random.reference_name("Particle_Descriptor_" + str(index))
			if not child.ok: return child
			var weight: Dictionary = random.int_value("Probability_" + str(index))
			if not weight.ok: return weight
			if child.value == null or weight.value <= 0: continue
			branches.append({"name": child.value, "weight": weight.value})
			total_weight = Plan.int32(total_weight + weight.value)
		if branches.is_empty() or total_weight == 0: return {"ok": true}
		var weights: Array[int] = []
		for branch: Dictionary in branches: weights.append(branch.weight)
		var allotted: Array[int] = _largest_remainder(starts.size(), weights, total_weight)
		for index: int in range(branches.size()):
			var branch: Dictionary = branches[index]
			var branch_path: PackedInt32Array = _join([path, " > ", branch.name, " (weight ", branch.weight, "/", total_weight, ")"])
			if allotted[index] == 0:
				unimplemented.append(_join([branch_path, ": rounds to zero instances of the ", starts.size(), " this emitter starts"]))
				continue
			var child: Dictionary = _set.find(branch.name)
			if not child.ok: return child
			if child.value == null:
				unimplemented.append(_join([branch_path, ": not in this set"]))
				continue
			var next: Variant = null
			if emitter != null:
				next = emitter.duplicate(true)
				next.start_turns = starts.slice(0, maxi(0, allotted[index]))
			var visited: Dictionary = visit(child.value, branch_path, start_turn, next)
			if not visited.ok: return visited
		return {"ok": true}

	func _visit_emitter(emitter: RefCounted, path: PackedInt32Array, start_turn: int, outer: Variant) -> Dictionary:
		if outer != null and outer.start_turns.size() > 1:
			for turn: int in outer.start_turns:
				var repeated: Dictionary = _visit_emitter(emitter, path, turn, null)
				if not repeated.ok: return repeated
			return {"ok": true}
		if outer != null and outer.start_turns.size() == 1:
			start_turn = outer.start_turns[0]
		var child_name: Dictionary = emitter.reference_name("Particle_Descriptor")
		if not child_name.ok: return child_name
		if child_name.value == null: return {"ok": true}
		var child: Dictionary = _set.find(child_name.value)
		if not child.ok: return child
		if child.value == null:
			unimplemented.append(_join([path, ": emitted '", child_name.value, "' is not in this set"]))
			return {"ok": true}
		var emission: Dictionary = emitter.float_with_modifier("Emit_Per_Turn")
		if not emission.ok: return emission
		if emission.value.modifier != null:
			unimplemented.append(_join([path, ": Emit_Per_Turn modifier '", emission.value.modifier,
				"' (a ParamFunction curve) is authored but not applied, so this emitter runs at its unmodulated authored rate"]))
		var mover: Dictionary = emitter.reference_name("Mover")
		if not mover.ok: return mover
		if mover.value != null:
			unimplemented.append(_join([path, ": Mover '", mover.value, "' is authored but not applied"]))
		var shape: Variant = null
		var shape_name: Dictionary = emitter.reference_name("Shape")
		if not shape_name.ok: return shape_name
		if shape_name.value != null:
			var shape_descriptor: Dictionary = _set.find(shape_name.value)
			if not shape_descriptor.ok: return shape_descriptor
			if shape_descriptor.value == null:
				unimplemented.append(_join([path, ": Shape '", shape_name.value, "' is not in this set"]))
			else:
				var read_shape: Dictionary = _read_shape(shape_descriptor.value)
				if not read_shape.ok: return read_shape
				shape = read_shape.value
		var life: Dictionary = emitter.int_value("Life")
		if not life.ok: return life
		var last_turn: int = 0 if life.value < 0 else life.value
		if life.value < 0:
			unimplemented.append(_join([path, ": emitter Life ", life.value, " does not expire; this plan emits only its first turn"]))
		# Explicit native safety difference: the source Int32 loop counter wraps
		# at this exact bound and never terminates. Do not execute that loop or
		# disguise it as a completed plan. No smaller finite schedule is capped.
		if last_turn == 2147483647:
			return _failure("NonTerminatingInput", "The source emitter loop cannot terminate when Life is Int32.MaxValue.")
		var emit_per_turn: float = Float32.read_word(emission.value.bits)
		var accumulator: float = 0.0
		var starts: Array = []
		for turn: int in range(last_turn + 1):
			accumulator += emit_per_turn
			var this_turn: int = _float_to_int32(floor(accumulator))
			accumulator -= this_turn
			for _index: int in range(maxi(0, this_turn)):
				starts.append(Plan.int32(start_turn + turn))
		if starts.is_empty():
			var rate: Dictionary = Number.format_float32(emission.value.bits)
			if not rate.ok: return rate
			unimplemented.append(_join([path, ": Emit_Per_Turn ", rate.value, " over Life ", life.value, " emits no whole particle"]))
			return {"ok": true}
		var initial: Array[int] = []
		for key: String in ["Initial_Velocity_X", "Initial_Velocity_Y", "Initial_Velocity_Z"]:
			var component: Dictionary = emitter.float_with_modifier(key)
			if not component.ok: return component
			initial.append(component.value.bits)
		var outward: Dictionary = emitter.float_with_modifier("Outward_Velocity")
		if not outward.ok: return outward
		var randomness: Dictionary = emitter.retail_direct_float_bits("Velocity_Randomness")
		if not randomness.ok: return randomness
		var context: Dictionary = {"shape": shape, "start_turns": starts,
			"initial_velocity": {"x_bits": initial[0], "y_bits": initial[1], "z_bits": initial[2]},
			"outward_velocity_bits": outward.value.bits, "velocity_randomness_bits": randomness.bits}
		return visit(child.value, _join([path, " > ", child_name.value]), start_turn, context)

	func _add_sprite(sprite: RefCounted, path: PackedInt32Array, start_turn: int, emitter: Variant) -> Dictionary:
		var texture: Dictionary = sprite.raw("Texture")
		if not texture.ok: return texture
		if texture.value == null:
			unimplemented.append(_join([path, ": sprite '", sprite.name, "' authors no Texture"]))
			return {"ok": true}
		var starts: Array = [start_turn] if emitter == null else emitter.start_turns
		var available: int = MAXIMUM_INSTANCES_PER_EFFECT - _instances
		if available <= 0:
			unimplemented.append(_join([path, ": dropped entirely at the ", MAXIMUM_INSTANCES_PER_EFFECT, "-instance reconstruction bound"]))
			return {"ok": true}
		if starts.size() > available:
			unimplemented.append(_join([path, ": authored ", starts.size(), " instances, kept ", available,
				" at the ", MAXIMUM_INSTANCES_PER_EFFECT, "-instance reconstruction bound"]))
			starts = starts.slice(0, available)
		_instances += starts.size()
		var size: Dictionary = sprite.int_value("Texture_Size")
		if not size.ok: return size
		var side: Dictionary = atlas_grid_side(size.value)
		if not side.ok: return side
		var colour: Variant = null
		var colour_name: Dictionary = sprite.reference_name("Colour_Range")
		if not colour_name.ok: return colour_name
		if colour_name.value != null:
			var descriptor: Dictionary = _set.find(colour_name.value)
			if not descriptor.ok: return descriptor
			if descriptor.value == null:
				unimplemented.append(_join([path, ": Colour_Range '", colour_name.value, "' is not in this set"]))
			else:
				var read_colour: Dictionary = _read_colour(descriptor.value)
				if not read_colour.ok: return read_colour
				colour = read_colour.value
		var modifier: Dictionary = sprite.reference_name("Modifier")
		if not modifier.ok: return modifier
		if modifier.value != null:
			unimplemented.append(_join([path, ": sprite Modifier '", modifier.value, "' is authored but not applied"]))
		var layer: Dictionary = {"descriptor_name": sprite.name, "path": path.duplicate(),
			"texture_name": leaf_texture_name(texture.value), "atlas_columns": side.value, "atlas_rows": side.value}
		# Ordered like the source initializer, so competing malformed fields
		# expose the same first failure instead of an arbitrary dictionary order.
		for row: Array in [["blend_mode", "Blend_Mode"], ["start_cell", "Texture_Number"], ["end_cell", "End_Frame"], ["animation_mode", "Anim_Type"]]:
			var read: Dictionary = sprite.int_value(row[1])
			if not read.ok: return read
			if row[0] == "animation_mode" and read.value not in [0, 1, 2]:
				return _failure("InvalidDataException", _join(["Sprite '", sprite.name, "' authored an unshipped Anim_Type ", read.value, "."]))
			layer[row[0]] = read.value
		var animation: Dictionary = sprite.float_bits("Anim_Speed")
		if not animation.ok: return animation
		layer.animation_cells_per_turn_bits = animation.bits
		var random_start: Dictionary = sprite.int_or_default("Random_Start_Frame", 0)
		if not random_start.ok: return random_start
		layer.random_start_cell = random_start.value != 0
		var life: Dictionary = sprite.int_value("Life")
		if not life.ok: return life
		layer.life_turns = life.value
		var radius: Dictionary = sprite.float_with_modifier("Radius")
		if not radius.ok: return radius
		layer.start_radius_bits = radius.value.bits
		for row: Array in [["final_radius_bits", "Final_Radius"], ["life_fraction_bits", "Life_Pct"]]:
			var read: Dictionary = sprite.float_bits(row[1])
			if not read.ok: return read
			layer[row[0]] = read.bits
		for row: Array in [["fade_colour", "Fade_Col"], ["axis_aligned", "Axis_Aligned"], ["gravity", "Gravity"]]:
			var read: Dictionary = sprite.int_value(row[1])
			if not read.ok: return read
			layer[row[0]] = read.value if row[0] == "axis_aligned" else read.value != 0
		var damp: Dictionary = sprite.float_bits("Velocity_Damp")
		if not damp.ok: return damp
		layer.velocity_damp_bits = damp.bits
		layer.colour_range = colour
		layer.instance_count = starts.size()
		layer.start_turns = starts.duplicate()
		layer.shape = null if emitter == null else emitter.shape
		layer.initial_velocity = {"x_bits": 0, "y_bits": 0, "z_bits": 0} if emitter == null else emitter.initial_velocity
		layer.outward_velocity_bits = 0 if emitter == null else emitter.outward_velocity_bits
		layer.velocity_randomness_bits = 0 if emitter == null else emitter.velocity_randomness_bits
		layers.append(layer.duplicate(true))
		return {"ok": true}

	func _read_shape(shape: RefCounted) -> Dictionary:
		var result: Dictionary = {"name": shape.name}
		for row: Array in [["type_id", "Type"], ["ring_axis", "Ring_Axis"], ["hemisphere", "Hemisphere"], ["num_particles", "Num_Particles"]]:
			var read: Dictionary = shape.int_value(row[1])
			if not read.ok: return read
			result[row[0]] = read.value
		var radius: Dictionary = shape.float_with_modifier("Radius")
		if not radius.ok: return radius
		result.radius_bits = radius.value.bits
		var hollow: Dictionary = shape.int_or_default("Hollow", 0)
		if not hollow.ok: return hollow
		result.hollow = hollow.value != 0
		var scale: Dictionary = {}
		for row: Array in [["x_bits", "RandomSX"], ["y_bits", "RandomSY"], ["z_bits", "RandomSZ"]]:
			var read: Dictionary = shape.float_bits(row[1])
			if not read.ok: return read
			scale[row[0]] = read.bits
		result.random_scale = scale
		return {"ok": true, "value": result}

	func _read_colour(colour: RefCounted) -> Dictionary:
		var result: Dictionary = {"name": colour.name}
		for triple: Array in [["start", "Start"], ["end", "End"], ["transition", "Transition"]]:
			var values: Dictionary = {}
			for channel: Array in [["r_bits", "Red"], ["g_bits", "Green"], ["b_bits", "Blue"]]:
				var read: Dictionary = colour.float_with_modifier(triple[1] + "_" + channel[1])
				if not read.ok: return read
				values[channel[0]] = read.value.bits
			result[triple[0]] = values
		for row: Array in [["use_end", "Use_End"], ["use_transition", "Use_Transition"]]:
			var read: Dictionary = colour.int_value(row[1])
			if not read.ok: return read
			result[row[0]] = read.value != 0
		var transition: Dictionary = colour.float_bits("Transition_Point")
		if not transition.ok: return transition
		result.transition_point_bits = transition.bits
		return {"ok": true, "value": result}


	static func _largest_remainder(total: int, weights: Array[int], weight_sum: int) -> Array[int]:
		var result: Array[int] = []
		var remainder: Array[float] = []
		var assigned: int = 0
		for weight: int in weights:
			var exact: float = float(total) * float(weight) / float(weight_sum)
			var amount: int = _float_to_int32(floor(exact))
			result.append(amount)
			remainder.append(exact - float(amount))
			assigned = Plan.int32(assigned + amount)
		# Once the largest remainder is -1, assigning it -1 leaves selection
		# unchanged. Skip only that identical tail (normally it is index zero).
		# This retains unchecked Int32 outcomes for overflowed authored weight sums.
		while assigned < total:
			var best: int = 0
			for index: int in range(1, weights.size()):
				if remainder[index] > remainder[best]: best = index
			if remainder[best] == -1.0:
				result[best] = Plan.int32(result[best] + (total - assigned))
				break
			result[best] = Plan.int32(result[best] + 1)
			remainder[best] = -1.0
			assigned = Plan.int32(assigned + 1)
		return result


	static func _float_to_int32(value: float) -> int:
		# Pinned C# unchecked double-to-Int32 cast (including NaN/infinity).
		return -2147483648 if not is_finite(value) or value < -2147483648.0 or value >= 2147483648.0 else int(value)


	## Pure name projection; callers pass an admitted raw UTF-16 field. Unpaired
	## surrogates and NUL never enter Godot String. Valid scalars use native casing,
	## checked exhaustively against the pinned .NET invariant scalar map.
	static func leaf_texture_name(authored_path: PackedInt32Array) -> PackedInt32Array:
		var start: int = 0
		for index: int in range(authored_path.size()):
			if authored_path[index] in [47, 92]: start = index + 1
		var output := PackedInt32Array()
		var index: int = start
		while index < authored_path.size():
			var code: int = authored_path[index]
			index += 1
			if code >= 0xd800 and code <= 0xdbff and index < authored_path.size() and authored_path[index] >= 0xdc00 and authored_path[index] <= 0xdfff:
				code = 0x10000 + ((code - 0xd800) << 10) + authored_path[index] - 0xdc00
				index += 1
			elif code >= 0xd800 and code <= 0xdfff:
				output.append(code)
				continue
			code = _lower_scalar(code)
			if code > 0xffff:
				code -= 0x10000
				output.append(0xd800 + (code >> 10))
				output.append(0xdc00 + (code & 0x3ff))
			else:
				output.append(code)
		return output


	static func _lower_scalar(code: int) -> int:
		# .NET invariant casing preserves capital I-with-dot. Godot's simple
		# Unicode lowercase maps it to ASCII i; the complete scalar comparison
		# isolates this one difference on the pinned engines.
		if code == 0 or code == 0x0130: return code
		return String.chr(code).to_lower().unicode_at(0)


	static func _is(value: PackedInt32Array, text: String) -> bool:
		return value == Text.units(text).value


	static func _key(value: PackedInt32Array) -> String:
		var bytes := PackedByteArray()
		bytes.resize(value.size() * 2)
		for index: int in range(value.size()): bytes.encode_u16(index * 2, value[index])
		return bytes.hex_encode()


	static func _join(parts: Array) -> PackedInt32Array:
		var result := PackedInt32Array()
		for part: Variant in parts:
			if part == null: continue
			if typeof(part) == TYPE_INT:
				result.append_array(Text.units(str(part)).value)
			else:
				result.append_array(Text.units(part).value)
		return result


	static func _failure(kind: String, message: Variant, parameter: String = "") -> Dictionary:
		var units: PackedInt32Array = Text.units(message).value
		# The raw units are authoritative. Human diagnostics escape unsafe carriers.
		var display: String = ""
		for code: int in units:
			display += ("\\u%04X" % code) if code == 0 or (code >= 0xd800 and code <= 0xdfff) else String.chr(code)
		return {"ok": false, "error_type": kind, "parameter": parameter, "error": display, "error_units": units}
