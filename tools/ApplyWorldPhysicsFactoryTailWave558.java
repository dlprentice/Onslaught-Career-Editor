//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyWorldPhysicsFactoryTailWave558 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String previousName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String previousName, String callingConvention,
                DataType returnType, ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousName = previousName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int missing = 0;
        int bad = 0;
    }

    private boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "worldphysics-factory-tail-wave558",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.params.length) {
            return false;
        }
        for (int i = 0; i < spec.params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.params[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name) && !fn.getName().equals(spec.previousName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }
            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (dryRun) {
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (updateNeeded) {
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                } else {
                    println("SKIP: " + spec.address + " already matches " + spec.name);
                }
                stats.skipped++;
                return;
            }
            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already matches " + spec.name);
                verifyReadBack(spec);
                return;
            }
            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("APPLY: " + spec.address + " -> " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        DataType voidType = VoidDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0050f610",
                "CRelaxedSquad__scalar_deleting_dtor",
                "CRelaxedSquad__VFunc_01_0050f610",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave558 owner/signature/comment hardening: CRelaxedSquad primary vtable slot 1 points here at 0x005e39d0. The wrapper calls CRelaxedSquad__Destructor(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete relaxed-squad layout, runtime squad teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("relaxed-squad", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050f630",
                "CRelaxedSquad__Destructor",
                "CRelaxedSquad__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave558 signature/comment hardening: direct xref from CRelaxedSquad__scalar_deleting_dtor proves ECX carries this. The body clears the relaxed-squad pointer set at this+0xa4, then calls CComplexThing__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set layout, runtime relaxed-squad teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("relaxed-squad", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f6d0",
                "CWorldPhysicsManager__CreateWeaponByIndex",
                "CWorldPhysicsManager__CreateWeaponByIndex",
                "__cdecl",
                voidPtr(),
                new ParameterImpl[] {
                    param("weapon_index", intType),
                    param("create_context", intType)
                },
                "Wave558 signature/comment hardening: CUnit__Init and BattleEngine reset callsites pass a weapon_index plus create_context. The body walks weapon-definition list DAT_008553e8 to the requested index, allocates a 0xb0 CWeapon object when heap space allows, calls CWeapon__ctor_base(this, weapon_data, create_context), and returns null on heap/list/allocation misses. Static retail-binary evidence only; exact weapon-definition layout, source method identity, runtime weapon behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "weapon", "factory", "signature-recovered")
            ),
            new Spec(
                "0x0050f7a0",
                "CWorldPhysicsManager__CreateProjectile",
                "CWorldPhysicsManager__CreateProjectile",
                "__cdecl",
                voidPtr(),
                new ParameterImpl[] {
                    param("round_definition", voidPtr())
                },
                "Wave558 signature/comment hardening: ProjectileBurst__SpawnFromCurrentPreset and CRound__SpawnConfiguredProjectile callsites pass one round/projectile definition pointer. The body requires heap headroom and a non-null definition, allocates a 0x134 CRound object, calls CRound__ctor(this, round_definition), and selects the alternate missile-style vtable path when round_definition+0x70 is nonzero. Static retail-binary evidence only; exact round-definition layout, source method identity, runtime projectile behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "projectile", "round", "factory", "signature-recovered")
            ),
            new Spec(
                "0x0050f8b0",
                "CMissile__scalar_deleting_dtor",
                "CMissile__VFunc_01_0050f8b0",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave558 owner/signature/comment hardening: CMissile primary vtable slot 1 points here at 0x005e3ba8. The wrapper calls CMissile__Destructor(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete missile layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("missile", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050f8d0",
                "CMissile__Destructor",
                "CMissile__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave558 signature/comment hardening: direct xref from CMissile__scalar_deleting_dtor proves ECX carries this. The body removes linked set cells at this+0xec and this+0xe8 when present, removes the this+0xe0 global-list node, then calls CActor__dtor_base(this). Static retail-binary evidence only; exact missile layout, runtime teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("missile", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f970",
                "CWorldPhysicsManager__CreateSpawner",
                "CWorldPhysicsManager__CreateSpawner",
                "__cdecl",
                voidPtr(),
                new ParameterImpl[] {
                    param("spawner_index", intType),
                    param("spawn_context", voidPtr())
                },
                "Wave558 signature/comment hardening: CUnit__Init passes a spawner index plus context. The body walks spawner-definition list DAT_008553f4, allocates a 0x3f8 CSpawnerThng object on a matching index, calls CSpawnerThng__Constructor(this, spawner_init, spawn_context), and returns null on heap/list/allocation misses. Static retail-binary evidence only; exact spawner-definition layout, source method identity, runtime spawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "spawner", "factory", "signature-recovered")
            ),
            new Spec(
                "0x0050fa40",
                "CWorldPhysicsManager__CreateCharacter",
                "CWorldPhysicsManager__CreateCharacter",
                "__cdecl",
                voidPtr(),
                new ParameterImpl[] {
                    param("component_index", intType)
                },
                "Wave558 signature/comment hardening: CUnit__Init passes one component_index, and the body walks component-definition list DAT_00855400 to that index. It selects the Gill_M_Head special case, a simple 0x2c0 CUnit path, or a 0x310 active-reader/vector path based on the definition name and field+0x12c, installs class tables, and returns null on heap/list/allocation rejects. Static retail-binary evidence only; exact component-definition layout, concrete character classes, runtime character behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "character", "component", "factory", "signature-recovered")
            ),
            new Spec(
                "0x0050fd30",
                "CGillMHead__scalar_deleting_dtor",
                "CGillMHead__VFunc_01_0050fd30",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave558 owner/signature/comment hardening: CGillMHead primary vtable slot 1 points here at 0x005e41fc. The wrapper calls CGillMHead__Destructor_VFunc01(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete GillMHead layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("gillm-head", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050fd50",
                "CTentacle__scalar_deleting_dtor",
                "CTentacle__VFunc_01_0050fd50",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave558 owner/signature/comment hardening: CTentacle primary vtable slot 1 points here at 0x005e3fa0. The wrapper calls CTentacle__Destructor(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete tentacle layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("tentacle", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050fd70",
                "CComponent__scalar_deleting_dtor",
                "CComponent__VFunc_01_0050fd70",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave558 owner/signature/comment hardening: CComponent primary vtable slot 1 points here at 0x005e3d44. The wrapper calls CComponent__Destructor(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete component layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("component", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050fd90",
                "CComponent__Destructor",
                "CComponent__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave558 signature/comment hardening: direct xref from CComponent__scalar_deleting_dtor proves ECX carries this. The body removes the linked set cell at this+0x26c when present, removes the this+0x258 global-list node, then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact component layout, runtime teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("component", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050fe10",
                "CGillMHead__Destructor_VFunc01",
                "CGillMHead__Destructor_VFunc01",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave558 signature/comment hardening: direct xref from CGillMHead__scalar_deleting_dtor proves ECX carries this. The body matches the component-style teardown path: remove linked set cell at this+0x26c when present, remove the this+0x258 global-list node, then call CUnit__dtor_base(this). Static retail-binary evidence only; exact GillMHead layout, runtime teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("gillm-head", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050fe90",
                "CTentacle__Destructor",
                "CTentacle__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave558 signature/comment hardening: direct xref from CTentacle__scalar_deleting_dtor proves ECX carries this. The body matches the component-style teardown path: remove linked set cell at this+0x26c when present, remove the this+0x258 global-list node, then call CUnit__dtor_base(this). Static retail-binary evidence only; exact tentacle layout, runtime teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("tentacle", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050ff10",
                "CWorldPhysicsManager__CreatePickup",
                "CWorldPhysicsManager__CreatePickup",
                "__cdecl",
                voidPtr(),
                new ParameterImpl[] {
                    param("pickup_type", intType)
                },
                "Wave558 signature/comment hardening: multiple unit, volume, feature, and projectile callsites pass one pickup_type/index value. The body gates out negative values, allocates a 0x94 CComplexThing-derived pickup object when heap headroom allows, seeds field+0x90 to zero, installs pickup class tables, and returns null on heap/allocation rejects. Static retail-binary evidence only; exact pickup enum names, concrete pickup layout, runtime pickup behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "pickup", "factory", "signature-recovered")
            ),
            new Spec(
                "0x0050ffd0",
                "CExplosion__scalar_deleting_dtor",
                "CExplosion__VFunc_01_0050ffd0",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave558 owner/signature/comment hardening: CExplosion primary vtable slot 1 points here at 0x005e4458. The wrapper calls CExplosion__Destructor(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete explosion layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("explosion", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050fff0",
                "CExplosion__Destructor",
                "CExplosion__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave558 signature/comment hardening: direct xref from CExplosion__scalar_deleting_dtor proves ECX carries this. The body removes the linked set cell at this+0x90 when present, then calls CComplexThing__dtor_base(this). Static retail-binary evidence only; exact explosion layout, runtime teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("explosion", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x00510060",
                "CWorldPhysicsManager__CreateEffect",
                "CWorldPhysicsManager__CreateEffect",
                "__cdecl",
                voidPtr(),
                new ParameterImpl[] {
                    param("effect_type", intType)
                },
                "Wave558 signature/comment hardening: CWorld__LoadWorld passes one effect_type/index value. The body gates out negative values, allocates a 0xf4 CComplexThing-derived effect object when heap headroom allows, installs effect class tables, and returns null on heap/allocation rejects. Static retail-binary evidence only; exact effect enum names, concrete effect layout, runtime visual effect behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "effect", "factory", "signature-recovered")
            ),
            new Spec(
                "0x00510150",
                "CWorldPhysicsManager__CreateTrigger",
                "CWorldPhysicsManager__CreateTrigger",
                "__cdecl",
                voidPtr(),
                new ParameterImpl[] {
                    param("trigger_type", intType)
                },
                "Wave558 signature/comment hardening: CWorld__LoadWorld passes one trigger_type/index value. The body gates out negative values, allocates a 0x88 CComplexThing-derived trigger object, zeroes field+0x84, links its node through CWorldPhysicsManager__PushNodeGlobalList, installs trigger class tables, and returns null on heap/allocation rejects. Static retail-binary evidence only; exact trigger enum names, concrete trigger layout, runtime trigger behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "trigger", "factory", "signature-recovered")
            ),
            new Spec(
                "0x00510230",
                "CHazard__scalar_deleting_dtor",
                "CHazard__VFunc_01_00510230",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave558 owner/signature/comment hardening: CHazard primary vtable slot 1 points here at 0x005e4780. The wrapper calls CHazard__Destructor(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete hazard layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("hazard", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x00510250",
                "CHazard__Destructor",
                "CHazard__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave558 signature/comment hardening: direct xref from CHazard__scalar_deleting_dtor and ECX use in the body prove this is a one-argument fastcall destructor. It removes the this+0x80 global-list node through CParticleManager__RemoveFromGlobalList, then calls CComplexThing__dtor_base(this). Static retail-binary evidence only; exact hazard layout, runtime teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("hazard", "destructor-body", "world-physics-manager", "signature-recovered")
            ),
            new Spec(
                "0x005102a0",
                "CWorldPhysicsManager__InitializeLists",
                "CWorldPhysicsManager__InitializeLists",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave558 signature/comment hardening: CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData calls this no-argument initializer. The body allocates nine 0x10 CSPtrSet containers, initializes them with CSPtrSet__Init, and stores them in DAT_008553e8 through DAT_00855408 for weapon, mode/round/tag, spawner, thing, component, and related definition lists. Static retail-binary evidence only; exact list ownership names, reload behavior beyond allocation, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "list-initializer", "definition-lists", "signature-recovered")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply")
            + " updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave558 apply had missing/bad rows");
        }
    }
}
