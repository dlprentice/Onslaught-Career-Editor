//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyThingWaypointVtableBoundaryWave1080 extends GhidraScript {
    private static final String WAVE_TAG = "thing-waypoint-vtable-boundary-wave1080";

    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String[] excludedBodyAddresses;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String[] excludedBodyAddresses, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.excludedBodyAddresses = excludedBodyAddresses;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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

    private Function functionAtEntry(Address address) {
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
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function existing = functionAtEntry(address);
        if (existing != null) {
            return existing;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null) {
            throw new IllegalStateException("Address is inside existing function "
                + containing.getName() + " at " + containing.getEntryPoint());
        }
        if (getInstructionAt(address) == null) {
            throw new IllegalStateException("No instruction at " + spec.address);
        }
        if (dryRun) {
            stats.wouldCreate++;
            println("DRY_CREATE: " + spec.address + " -> " + expectedSignature(spec));
            return null;
        }

        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, spec.name);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + spec.address + " (disassemble=" + disasmOk + ")");
        }
        stats.created++;
        return created;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = getOrCreate(spec, dryRun, stats);
        if (fn == null) {
            return;
        }

        boolean renameNeeded = !fn.getName().equals(spec.name);
        boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
        boolean commentOrTagsNeedUpdate = fn.getComment() == null
            || !fn.getComment().equals(spec.comment)
            || !hasAllTags(fn, spec);

        if (!renameNeeded && !signatureNeedsUpdate && !commentOrTagsNeedUpdate) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else if (commentOrTagsNeedUpdate) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (signatureNeedsUpdate) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        }
        fn.setComment(spec.comment);
        Set<String> existingTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                fn.addTag(tag);
            }
        }
        if (!signatureNeedsUpdate && commentOrTagsNeedUpdate) {
            stats.commentOnlyUpdated++;
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50L);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
        for (String excluded : spec.excludedBodyAddresses) {
            if (fn.getBody().contains(addr(excluded))) {
                throw new IllegalStateException("Read-back body for " + spec.address
                    + " unexpectedly absorbed " + excluded);
            }
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            WAVE_TAG,
            "wave1080-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "signature-hardened",
            "comment-hardened",
            "vtable-slot",
            "thing-family"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyThingWaypointVtableBoundaryWave1080 mode=" + (dryRun ? "dry" : "apply"));

        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004013f0",
                "SharedVFunc__ReturnColorFF000080_004013f0",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00401400" },
                "Wave1080 shared vtable-boundary recovery: broad CThing-family vtable DATA refs, including CThing/CWaypoint slot +0x10 and CInfantryAI slot +0xd4, point at this previously functionless two-instruction constant-return body. The body returns 0xff000080. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, color/flag semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "constant-return")
            ),
            new Spec(
                "0x00401400",
                "SharedVFunc__ForwardField28Slot18OrFallbackFloat_00401400",
                "__thiscall",
                floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00401420" },
                "Wave1080 shared vtable-boundary recovery: broad CThing-family vtable DATA refs, including CThing/CWaypoint slot +0x20 and CInfantryAI slot +0xe4, point at this compact field-forwarding virtual. The body loads this+0x28, jumps through that object's vtable slot +0x18 when non-null, otherwise returns the fallback float at 0x005d8568. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, field identity, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "field-forwarder", "float-return")
            ),
            new Spec(
                "0x004014d0",
                "SharedVFunc__ReturnField64Offset10OrMinusOne_004014d0",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004014e0" },
                "Wave1080 shared vtable-boundary recovery: broad CThing-family vtable DATA refs, including CThing/CWaypoint slot +0x1c and CInfantryAI slot +0xe0, point at this compact getter. The body returns *(this+0x64+0x10) when the field64 pointer is non-null and returns -1 otherwise. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, field identity, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "field-getter")
            ),
            new Spec(
                "0x004014f0",
                "SharedVFunc__ReturnField68_004014f0",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00401500" },
                "Wave1080 shared vtable-boundary recovery: broad CThing-family vtable DATA refs, including CThing/CWaypoint slot +0x70 and CInfantryAI slot +0x134, point at this two-instruction getter. The body returns the pointer/value at this+0x68. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, field identity, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "field-getter")
            ),
            new Spec(
                "0x00401500",
                "SharedVFunc__ReturnField64Offset14OrZero_00401500",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00401510" },
                "Wave1080 shared vtable-boundary recovery: broad CThing-family vtable DATA refs, including CThing/CWaypoint slot +0x58, point at this compact getter. The body returns *(this+0x64+0x14) when the field64 pointer is non-null and returns zero otherwise. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, field identity, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "field-getter")
            ),
            new Spec(
                "0x004040a0",
                "SharedVFunc__CopyVector14ToOut_004040a0",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("out_vec4", voidPtr) },
                new String[] { "0x004040d0" },
                "Wave1080 shared vtable-boundary recovery: CThing, CWaypoint, CAnimal, CActor-family, and CInfantryAI vtable DATA refs point at this previously functionless vector-output virtual. The body copies four dwords from this+0x14 into the caller output buffer and returns with RET 0x4. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, concrete vector field identity, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "vector-copy", "output-buffer")
            ),
            new Spec(
                "0x004040d0",
                "SharedVFunc__CopyBlock34ToOut_004040d0",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("out_block30", voidPtr) },
                new String[] { "0x004040f0" },
                "Wave1080 shared vtable-boundary recovery: CAnimal, CComplexThing, CWaypoint-derived, and CInfantryAI table DATA refs point at this previously functionless output-copy virtual. The body copies 0x30 bytes from this+0x34 into the caller output buffer and returns with RET 0x4. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, concrete block/matrix field identity, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "block-copy", "output-buffer")
            ),
            new Spec(
                "0x00405910",
                "SharedVFunc__ReturnMinusOne_00405910",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405920" },
                "Wave1080 shared vtable-boundary recovery: broad CThing-family and CInfantryAI table DATA refs point at this two-instruction return stub. The body returns -1. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "constant-return")
            ),
            new Spec(
                "0x00405920",
                "SharedVFunc__ReturnOneRet4_00405920",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("unused_arg", voidPtr) },
                new String[] { "0x00405930" },
                "Wave1080 shared vtable-boundary recovery: broad CThing-family and CInfantryAI table DATA refs point at this compact RET 0x4 stub. The body returns one and consumes one stack argument. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "constant-return", "ret4")
            ),
            new Spec(
                "0x004bfb50",
                "CWaypoint__GetClassNameString_004bfb50",
                "__thiscall",
                charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004bfb60" },
                "Wave1080 CWaypoint vtable-boundary recovery: CWaypoint vtable 0x005dd278 slot +0x94 points at this previously functionless constant-string getter. String read-back at 0x00630c58 is CWaypoint. Static retail Ghidra vtable/xref/listing/string evidence only; exact source virtual name, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("cwaypoint", "class-name", "constant-return")
            ),
            new Spec(
                "0x004bfb60",
                "CWaypoint__SetThingTypeMask1001_004bfb60",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("type_mask", intType) },
                new String[] { "0x004bfc60" },
                "Wave1080 CWaypoint vtable-boundary recovery: CWaypoint vtable 0x005dd278 slot +0x110 points at this compact type-mask setter. The body ORs the stack argument with 0x1001, stores it at this+0x34, and returns with RET 0x4. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, type-bit labels, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("cwaypoint", "type-mask", "ret4")
            ),
            new Spec(
                "0x004f3460",
                "CThing__GetClassNameString_004f3460",
                "__thiscall",
                charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004f3470" },
                "Wave1080 CThing vtable-boundary recovery: CThing vtable 0x005df550 slot +0x94 points at this previously functionless constant-string getter. String read-back at 0x00633174 is CThing. Static retail Ghidra vtable/xref/listing/string evidence only; exact source virtual name, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("cthing", "class-name", "constant-return")
            ),
            new Spec(
                "0x004f3470",
                "CThing__SetThingTypeMaskOr1_004f3470",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("type_mask", intType) },
                new String[] { "0x004f3480" },
                "Wave1080 CThing vtable-boundary recovery: CThing vtable 0x005df550 slot +0x110 points at this compact type-mask setter. The body ORs the low byte of the stack argument with 1, stores the result at this+0x34, and returns with RET 0x4. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, type-bit labels, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("cthing", "type-mask", "ret4")
            ),
            new Spec(
                "0x0052db60",
                "CWaypoint__GetTypeId12_0052db60",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0052db70" },
                "Wave1080 CWaypoint vtable-boundary recovery: CWaypoint vtable 0x005dd278 slot +0x98 points at this previously functionless type-id getter. The body returns constant 0x12 and stops before adjacent 0x0052db70. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, concrete type enum label, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("cwaypoint", "type-id", "constant-return")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun, stats);
            } catch (Exception ex) {
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
                stats.bad++;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1080 thing/waypoint vtable-boundary recovery encountered missing/bad rows");
        }
    }
}
