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

public class ApplyAirUnitLifecycleWave557 extends GhidraScript {
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
            "air-unit-lifecycle-wave557",
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
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0050ed60",
                "CBomber__scalar_deleting_dtor",
                "CBomber__VFunc_01_0050ed60",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CBomber primary vtable slot 1 points here at 0x005e2e24. The wrapper calls CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct(this), conditionally frees this through CDXMemoryManager__Free when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete class layout, allocator ownership, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("bomber", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050ed80",
                "CBigAirUnit__ctor_base",
                "CBigAirUnit__ctor_like_0050ed80",
                "__fastcall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 name/signature/comment hardening: CWorldPhysicsManager__CreateThingByType calls this after allocating big-air-unit variants and passing the allocation in ECX. The body calls CUnit__ctor_base, zeroes the global-list node state at this+0x254, links this+0x250 through CWorldPhysicsManager__PushNodeGlobalList, initializes pointer sets at this+0x25c and this+0x26c, installs base CBigAirUnit vtables, and returns this. Static retail-binary evidence only; exact source constructor identity, concrete layout, runtime spawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("big-air-unit", "constructor", "world-physics-manager", "factory", "owner-corrected")
            ),
            new Spec(
                "0x0050ee10",
                "CGroundAttackAircraft__scalar_deleting_dtor",
                "CGroundAttackAircraft__VFunc_01_0050ee10",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CGroundAttackAircraft primary vtable slot 1 points here at 0x005e2bd0. The wrapper calls CGroundAttackAircraft__Destructor_VFunc01(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete class layout, runtime aircraft destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("ground-attack-aircraft", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050ee30",
                "CInfantryUnit__scalar_deleting_dtor",
                "CInfantryUnit__VFunc_01_0050ee30",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CInfantryUnit primary vtable slot 1 points here at 0x005e2730. The wrapper calls CInfantryUnit__Destructor_VFunc01(this), optionally frees this through CDXMemoryManager__Free when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete infantry-unit layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("infantry-unit", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050ee50",
                "CCarrier__scalar_deleting_dtor",
                "CCarrier__VFunc_01_0050ee50",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CCarrier primary vtable slot 1 points here at 0x005e203c. The wrapper calls CCarrier__Destructor(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete carrier layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("carrier", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050ee70",
                "CDropship__scalar_deleting_dtor",
                "CDropship__VFunc_01_0050ee70",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CDropship primary vtable slot 1 points here at 0x005e1ddc. The wrapper calls CDropship__Destructor_VFunc01(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete dropship layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("dropship", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050eeb0",
                "CPlane__scalar_deleting_dtor",
                "CPlane__VFunc_01_0050eeb0",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CPlane primary vtable slot 1 points here at 0x005e1934. The wrapper calls CPlane__Destructor_VFunc01(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete CPlane layout, runtime flight-unit destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("plane", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050eed0",
                "CDiveBomber__scalar_deleting_dtor",
                "CDiveBomber__VFunc_01_0050eed0",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CDiveBomber primary vtable slot 1 points here at 0x005e1240. The wrapper calls CDiveBomber__Destructor_VFunc01(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete dive-bomber layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("dive-bomber", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050eef0",
                "CCarver__scalar_deleting_dtor",
                "CCarver__VFunc_01_0050eef0",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CCarver primary vtable slot 1 points here at 0x005e0d90. The wrapper calls CCarver__Destructor_VFunc01(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete Carver layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("carver", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050ef10",
                "CFenrir__scalar_deleting_dtor",
                "CFenrir__VFunc_01_0050ef10",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CFenrir primary vtable slot 1 points here at 0x005e0434. The wrapper calls CFenrir__Destructor_VFunc01(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete Fenrir layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("fenrir", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050ef30",
                "CCarrier__Destructor",
                "CCarrier__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CCarrier__scalar_deleting_dtor proves ECX carries this. The body clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node through CParticleManager__RemoveFromGlobalList, and then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set/list layout, runtime carrier teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("carrier", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050efa0",
                "CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct",
                "CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CBomber__scalar_deleting_dtor proves ECX carries this. The body clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, and then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set/list layout, runtime bomber teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("bomber", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f010",
                "CBigAirUnit__scalar_deleting_dtor",
                "CBigAirUnit__VFunc_01_0050f010",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CBigAirUnit primary vtable slot 1 points here at 0x005e3528. The wrapper calls CBigAirUnit__Destructor(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete big-air-unit layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("big-air-unit", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050f030",
                "CBigAirUnit__Destructor",
                "CBigAirUnit__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CBigAirUnit__scalar_deleting_dtor proves ECX carries this. The body clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node through CParticleManager__RemoveFromGlobalList, and then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set/list layout, runtime big-air-unit teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("big-air-unit", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f0a0",
                "CAirUnit__ctor_base",
                "CAirUnit__ctor_like_0050f0a0",
                "__fastcall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 name/signature/comment hardening: CWorldPhysicsManager__CreateThingByType calls this for multiple aircraft variants after OID__AllocObject and ECX=this setup. The body calls CUnit__ctor_base, zeroes this+0x254, links this+0x250 through CWorldPhysicsManager__PushNodeGlobalList, initializes pointer sets at this+0x25c and this+0x26c, installs base CAirUnit vtables, and returns this. Static retail-binary evidence only; exact source constructor identity, concrete aircraft layout, runtime spawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("air-unit", "constructor", "world-physics-manager", "factory", "owner-corrected")
            ),
            new Spec(
                "0x0050f130",
                "CGroundAttackAircraft__Destructor_VFunc01",
                "CGroundAttackAircraft__Destructor_VFunc01",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CGroundAttackAircraft__scalar_deleting_dtor proves ECX carries this. The body clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, and then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set/list layout, runtime ground-attack-aircraft teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("ground-attack-aircraft", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f1a0",
                "CInfantryUnit__Destructor_VFunc01",
                "CInfantryUnit__Destructor_VFunc01",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CInfantryUnit__scalar_deleting_dtor proves ECX carries this, replacing the locked no-parameter signature. The body removes the this+0x270 global-list node through CParticleManager__RemoveFromGlobalList, then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete list layout, runtime infantry teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("infantry-unit", "destructor-body", "world-physics-manager", "signature-recovered")
            ),
            new Spec(
                "0x0050f1f0",
                "CDropship__Destructor_VFunc01",
                "CDropship__Destructor_VFunc01",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CDropship__scalar_deleting_dtor proves ECX carries this. The body clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, and then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set/list layout, runtime dropship teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("dropship", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f260",
                "CPlane__Destructor_VFunc01",
                "CPlane__Destructor_VFunc01",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CPlane__scalar_deleting_dtor proves ECX carries this. The body clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, and then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set/list layout, runtime plane teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("plane", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f2d0",
                "CDiveBomber__Destructor_VFunc01",
                "CDiveBomber__Destructor_VFunc01",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CDiveBomber__scalar_deleting_dtor proves ECX carries this. The body clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, and then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set/list layout, runtime dive-bomber teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("dive-bomber", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f340",
                "CCarver__Destructor_VFunc01",
                "CCarver__Destructor_VFunc01",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CCarver__scalar_deleting_dtor proves ECX carries this. The body clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, and then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set/list layout, runtime Carver teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("carver", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f3b0",
                "CFenrir__Destructor_VFunc01",
                "CFenrir__Destructor_VFunc01",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CFenrir__scalar_deleting_dtor proves ECX carries this. The body clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, and then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set/list layout, runtime Fenrir teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("fenrir", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f420",
                "CAirUnit__scalar_deleting_dtor",
                "CAirUnit__VFunc_01_0050f420",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("delete_flags", byteType)
                },
                "Wave557 owner/signature/comment hardening: CAirUnit base vtable slot 1 points here at 0x005e377c. The wrapper calls CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct(this), optionally frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail-binary evidence only; exact source virtual name, concrete aircraft layout, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("air-unit", "scalar-deleting-dtor", "vtable-slot-1", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050f440",
                "CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct",
                "CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave557 signature/comment hardening: direct xref from CAirUnit__scalar_deleting_dtor proves ECX carries this. The body clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, and then calls CUnit__dtor_base(this). Static retail-binary evidence only; exact source destructor identity, concrete set/list layout, runtime aircraft teardown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("air-unit", "destructor-body", "world-physics-manager")
            ),
            new Spec(
                "0x0050f4b0",
                "CWorldPhysicsManager__CreateSquad",
                "CWorldPhysicsManager__CreateSquad",
                "__cdecl",
                voidPtr(),
                new ParameterImpl[] {
                    param("squad_type", intType)
                },
                "Wave557 signature/comment hardening: CWorld__LoadWorld and CSpawnerThng callsites pass one squad_type value, and the body switches on that value. It allocates a 0xb4 CSquad-style object for observed types 0 and 3, initializes the base CSquad path plus one pointer set, otherwise allocates a 0x144 CSquadNormal through CSquadNormal__Constructor for supported normal-squad types, and returns null for heap/type rejects. Static retail-binary evidence only; exact squad-type enum names, concrete squad layouts, runtime squad behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "squad", "factory", "signature-recovered")
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
            throw new IllegalStateException("Wave557 apply had missing/bad rows");
        }
    }
}
