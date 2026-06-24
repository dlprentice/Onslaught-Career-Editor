//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyObjectCleanupWave460 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "object-cleanup-wave460",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] names(String... values) {
        return values;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            if (!actualSignature.equals(expectedSignature(spec))) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature(spec));
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(250);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004bfe00",
                "CUnit__dtor_base_Thunk_004bfe00",
                "__fastcall",
                voidType,
                "Wave460 correction: jump thunk to CUnit__dtor_base at 0x004f84e0. Reached by CUnit__scalar_deleting_dtor and unwind cleanup paths; no standalone cleanup body lives here. Runtime unit cleanup behavior, exact CUnit layout, exact source identity, and rebuild parity remain unproven.",
                names("CUnit__scalar_deleting_dtor_004f84e0", "CUnit__dtor_base_Thunk_004bfe00"),
                tags("cunit", "dtor-base", "thunk", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004bfe10",
                "CRocket__dtor_base",
                "__fastcall",
                voidType,
                "Wave460 correction: CRocket destructor-base body called by CRocket__scalar_deleting_dtor. Destroys the +0xec array with CDXLandscape__DestroyArrayWithCallback using CParticleManager__RemoveFromGlobalList_Thunk, then delegates to CActor__dtor_base. Runtime rocket cleanup behavior, exact array element layout, exact source identity, and rebuild parity remain unproven.",
                names("CRocket__DestroyArrayWithCallback", "CRocket__dtor_base"),
                tags("rocket", "dtor-base", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004bfe70",
                "CWaypoint__dtor_base",
                "__fastcall",
                voidType,
                "Wave460 correction: CWaypoint destructor-base body called by CWaypoint__scalar_deleting_dtor. If the +0x3c owner/list link is populated, removes that link through CSPtrSet__Remove, then delegates to CThing__ctor_like_004f3640. Runtime waypoint cleanup behavior, exact link layout, exact source identity, and rebuild parity remain unproven.",
                names("CWaypoint__RemoveOwnerLinkAndResetBaseThing", "CWaypoint__dtor_base"),
                tags("waypoint", "dtor-base", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004bfed0",
                "CSpawnerThing__dtor_base",
                "__fastcall",
                voidType,
                "Wave460 correction: CSpawnerThing destructor-base body called by CSpawnerThing__scalar_deleting_dtor. If the +0x7c owner/list link is populated, removes that link through CSPtrSet__Remove, then delegates to CComplexThing__dtor_base. Runtime spawner cleanup behavior, exact link layout, exact source identity, and rebuild parity remain unproven.",
                names("CSpawnerThing__RemoveOwnerLinkAndResetComplexThing", "CSpawnerThing__dtor_base"),
                tags("spawner-thing", "dtor-base", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004bff30",
                "CComplexThing__dtor_base_Thunk_004bff30",
                "__fastcall",
                voidType,
                "Wave460 correction: jump thunk to the canonical CComplexThing__dtor_base body at 0x004f3f00. Reached by unwind cleanup and VFuncSlot_01_004e5e50; no standalone cleanup body lives here. Runtime complex-thing cleanup behavior, exact layout, exact source identity, and rebuild parity remain unproven.",
                names("CComplexThing__dtor_base", "CComplexThing__dtor_base_Thunk_004bff30"),
                tags("complex-thing", "dtor-base", "thunk", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004bff40",
                "CSphereTrigger__dtor_base",
                "__fastcall",
                voidType,
                "Wave460 correction: CSphereTrigger destructor-base body called by CSphereTrigger__scalar_deleting_dtor. Clears the +0x8c CSPtrSet, removes the +0x7c particle/global-list node through CParticleManager__RemoveFromGlobalList, then delegates to CComplexThing__dtor_base. Runtime sphere-trigger cleanup behavior, exact tracked-set layout, exact source identity, and rebuild parity remain unproven.",
                names("CSphereTrigger__ClearTrackedSetRemoveGlobalAndResetBase", "CSphereTrigger__dtor_base"),
                tags("sphere-trigger", "dtor-base", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004bffa0",
                "CWingmanStart__dtor_base",
                "__fastcall",
                voidType,
                "Wave460 correction: CWingmanStart destructor-base body called by CWingmanStart__scalar_deleting_dtor. If the +0x7c owner/list link is populated, removes that link through CSPtrSet__Remove, then delegates to CComplexThing__dtor_base. Runtime wingman-start cleanup behavior, exact link layout, exact source identity, and rebuild parity remain unproven.",
                names("CWingmanStart__RemoveOwnerLinkAndResetComplexThing", "CWingmanStart__dtor_base"),
                tags("wingman-start", "dtor-base", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c0000",
                "CEscapePod__dtor_base",
                "__fastcall",
                voidType,
                "Wave460 correction: CEscapePod destructor-base body called by CEscapePod__scalar_deleting_dtor. Removes the +0xe0 particle/global-list node through CParticleManager__RemoveFromGlobalList, then delegates to CActor__dtor_base. Runtime escape-pod cleanup behavior, exact node layout, exact source identity, and rebuild parity remain unproven.",
                names("CEscapePod__RemoveGlobalAndResetActorBase", "CEscapePod__dtor_base"),
                tags("escape-pod", "dtor-base", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004f84e0",
                "CUnit__dtor_base",
                "__fastcall",
                voidType,
                "Wave460 correction: CUnit destructor-base body. Resets CUnit vtable pointers, tears down observed linked unit/particle state, clears several CSPtrSet-style lists, removes owner links at observed offsets, then delegates to CActor__dtor_base. The decompile still has a non-semantic EDI artifact around CUnit__FinalizeLinkedUnitStateAndClear. Runtime unit cleanup behavior, exact CUnit layout, exact source identity, and rebuild parity remain unproven.",
                names("CUnit__scalar_deleting_dtor_004f84e0", "CUnit__dtor_base"),
                tags("cunit", "dtor-base", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x0050ee90",
                "CUnit__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave460 correction: CUnit vtable slot 1 scalar-deleting destructor wrapper. Calls CUnit__dtor_base_Thunk_004bfe00, checks flags & 1, optionally frees this through CDXMemoryManager__Free, returns this, and ends with RET 0x4. Runtime unit cleanup behavior, exact layout, exact source identity, and rebuild parity remain unproven.",
                names("VFuncSlot_01_0050ee90", "CUnit__scalar_deleting_dtor"),
                tags("cunit", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("flags", byteType) }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
