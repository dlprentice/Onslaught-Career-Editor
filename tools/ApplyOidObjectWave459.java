//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyOidObjectWave459 extends GhidraScript {
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
            "oid-object-wave459",
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
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004bf090",
                "OID__CreateObject",
                "__cdecl",
                voidPtr,
                "Wave459 signature/comment hardening: main OID object factory from [maintainer-local-source-export-root]\\oids.cpp. Takes an object_id switch value, allocates matching retail object sizes through OID__AllocObject, runs constructor/init helpers including OID__InitTargetData and OID__InitBaseObject where applicable, assigns primary/secondary vtable pointers, and returns the created object or null. Runtime object construction behavior, exact concrete layouts, complete OID enum names, source-body identity, and rebuild parity remain unproven.",
                names("OID__CreateObject"),
                tags("oid", "factory", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("object_id", intType) }
            ),
            new Spec(
                "0x004bfa60",
                "OID__InitTargetData",
                "__fastcall",
                voidType,
                "Wave459 signature/comment hardening: initializes target tracking data at the ECX target_data pointer by writing dwords 0, 0xffffffff, 0, and 0xbf800000 (-1.0f). Called from OID__CreateObject during a large entity construction path. Runtime targeting behavior, field names/layout, source-body identity, and rebuild parity remain unproven.",
                names("OID__InitTargetData"),
                tags("oid", "target-data", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("target_data", voidPtr) }
            ),
            new Spec(
                "0x004bfab0",
                "OID__RenderWithState1BOverride",
                "__thiscall",
                voidType,
                "Wave459 signature/comment hardening: vtable slot render wrapper with one stack render_flags argument and RET 0x4. If the +0x48 unit/render field allows CUnit__RenderWithDistanceFade to handle the draw, it returns early; otherwise it disables render state 0x1b, calls CThing__Render(this, render_flags), then restores render state 0x1b. Runtime rendering behavior, exact owner class, render-state meaning, and rebuild parity remain unproven.",
                names("OID__RenderWithState1BOverride"),
                tags("oid", "render", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("render_flags", uintType) }
            ),
            new Spec(
                "0x004bfce0",
                "CTree__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave459 correction: CTree vtable slot 1 scalar-deleting destructor wrapper. Calls CTree__scalar_deleting_dtor_004f63c0, checks flags & 1, optionally frees this through CDXMemoryManager__Free, returns this, and ends with RET 0x4. Runtime tree cleanup behavior, exact destructor-body completeness, concrete layout, and rebuild parity remain unproven.",
                names("CTree__VFunc_01_004bfce0", "CTree__scalar_deleting_dtor"),
                tags("ctree", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("flags", byteType) }
            ),
            new Spec(
                "0x004bfd00",
                "CActorBase__shared_scalar_deleting_dtor_004bfd00",
                "__thiscall",
                voidPtr,
                "Wave459 correction: shared vtable slot 1 scalar-deleting destructor wrapper used by three vtable DATA xrefs, including actor/feature-style tables. Calls CActor__dtor_base, checks flags & 1, optionally frees this through CDXMemoryManager__Free, returns this, and ends with RET 0x4. Runtime shared cleanup behavior, exact owning classes, destructor completeness, concrete layouts, and rebuild parity remain unproven.",
                names("VFuncSlot_01_004bfd00", "CActorBase__shared_scalar_deleting_dtor_004bfd00"),
                tags("actor-base", "shared-wrapper", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("flags", byteType) }
            ),
            new Spec(
                "0x004bfd20",
                "OID__InitBaseObject",
                "__fastcall",
                voidPtr,
                "Wave459 signature/comment hardening: base object initializer at the ECX object pointer. Calls CThing__ctor_like_004f3e10, writes the CActor__HandleEvent primary vtable pointer and CActor__GetRenderPos secondary/render-position vtable pointer, then returns object. Runtime base-object behavior, exact class identity, concrete layout, and rebuild parity remain unproven.",
                names("OID__InitBaseObject"),
                tags("oid", "base-object", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("object", voidPtr) }
            ),
            new Spec(
                "0x004bfd40",
                "CRocket__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave459 correction: CRocket vtable slot 1 scalar-deleting destructor wrapper. Calls CRocket__DestroyArrayWithCallback, checks flags & 1, optionally frees this through CDXMemoryManager__Free, returns this, and ends with RET 0x4. Runtime rocket cleanup behavior, destructor completeness, concrete layout, and rebuild parity remain unproven.",
                names("CRocket__VFunc_01_004bfd40", "CRocket__scalar_deleting_dtor"),
                tags("rocket", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("flags", byteType) }
            ),
            new Spec(
                "0x004bfd60",
                "CWaypoint__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave459 correction: CWaypoint vtable slot 1 scalar-deleting destructor wrapper. Calls CWaypoint__RemoveOwnerLinkAndResetBaseThing, checks flags & 1, optionally frees this through CDXMemoryManager__Free, returns this, and ends with RET 0x4. Runtime waypoint cleanup behavior, destructor completeness, concrete layout, and rebuild parity remain unproven.",
                names("CWaypoint__VFunc_01_004bfd60", "CWaypoint__scalar_deleting_dtor"),
                tags("waypoint", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("flags", byteType) }
            ),
            new Spec(
                "0x004bfd80",
                "CSpawnerThing__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave459 correction: CSpawnerThing vtable slot 1 scalar-deleting destructor wrapper. Calls CSpawnerThing__RemoveOwnerLinkAndResetComplexThing, checks flags & 1, optionally frees this through CDXMemoryManager__Free, returns this, and ends with RET 0x4. Runtime spawner cleanup behavior, destructor completeness, concrete layout, and rebuild parity remain unproven.",
                names("CSpawnerThing__VFunc_01_004bfd80", "CSpawnerThing__scalar_deleting_dtor"),
                tags("spawner-thing", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("flags", byteType) }
            ),
            new Spec(
                "0x004bfda0",
                "CSphereTrigger__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave459 correction: CSphereTrigger vtable slot 1 scalar-deleting destructor wrapper. Calls CSphereTrigger__ClearTrackedSetRemoveGlobalAndResetBase, checks flags & 1, optionally frees this through CDXMemoryManager__Free, returns this, and ends with RET 0x4. Runtime sphere-trigger cleanup behavior, destructor completeness, concrete layout, and rebuild parity remain unproven.",
                names("CSphereTrigger__VFunc_01_004bfda0", "CSphereTrigger__scalar_deleting_dtor"),
                tags("sphere-trigger", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("flags", byteType) }
            ),
            new Spec(
                "0x004bfdc0",
                "CWingmanStart__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave459 correction: CWingmanStart vtable slot 1 scalar-deleting destructor wrapper. Calls CWingmanStart__RemoveOwnerLinkAndResetComplexThing, checks flags & 1, optionally frees this through CDXMemoryManager__Free, returns this, and ends with RET 0x4. Runtime wingman-start cleanup behavior, destructor completeness, concrete layout, and rebuild parity remain unproven.",
                names("CWingmanStart__VFunc_01_004bfdc0", "CWingmanStart__scalar_deleting_dtor"),
                tags("wingman-start", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("flags", byteType) }
            ),
            new Spec(
                "0x004bfde0",
                "CEscapePod__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave459 correction: CEscapePod vtable slot 1 scalar-deleting destructor wrapper. Calls CEscapePod__RemoveGlobalAndResetActorBase, checks flags & 1, optionally frees this through CDXMemoryManager__Free, returns this, and ends with RET 0x4. Runtime escape-pod cleanup behavior, destructor completeness, concrete layout, and rebuild parity remain unproven.",
                names("CEscapePod__VFunc_01_004bfde0", "CEscapePod__scalar_deleting_dtor"),
                tags("escape-pod", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"),
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
