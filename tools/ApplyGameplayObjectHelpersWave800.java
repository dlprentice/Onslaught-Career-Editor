//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyGameplayObjectHelpersWave800 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, boolean updateSignature,
                String callingConvention, DataType returnType, ParameterImpl[] parameters,
                String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
            this.updateSignature = updateSignature;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "gameplay-object-helpers-wave800",
            "wave800-readback-verified",
            "retail-binary-evidence",
            "comment-hardened"
        }, extras);
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.updateSignature) {
            return true;
        }
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
        if (!spec.updateSignature) {
            return "<unchanged signature>";
        }
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.newName)
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

    private boolean allowedName(Function fn, Spec spec) {
        return fn.getName().equals(spec.newName) || fn.getName().equals(spec.oldName);
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.newName)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        String readComment = fn.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.newName);
                return;
            }
            if (!allowedName(fn, spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName()
                    + " expected=" + spec.oldName + " or " + spec.newName);
                return;
            }

            boolean renameNeeded = !fn.getName().equals(spec.newName);
            boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
            boolean commentOrTagsNeedUpdate = fn.getComment() == null
                || !fn.getComment().equals(spec.comment)
                || !hasAllTags(fn, spec.tags);

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + spec.newName);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                }
                else if (commentOrTagsNeedUpdate) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature()
                    + " expected=" + expectedSignature(spec));
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.newName, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (signatureNeedsUpdate) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
                stats.signatureUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            if (!signatureNeedsUpdate) {
                stats.commentOnlyUpdated++;
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
            Thread.sleep(75L);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.newName + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x00445010",
                "CMCBuggy__GetTargetValueOrFallback",
                "CMCBuggy__GetTargetValueOrFallback",
                true,
                "__thiscall",
                floatType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("target_id", intType)
                },
                "Wave800 static read-back: CMCBuggy/destructable-segment target value helper called by CDestructableSegmentsMotionController__ApplyRumbleTransform at 0x00494cfa. RET 0x4 proves one explicit stack argument after ECX; instruction evidence reads the target table at this+4 using target_id, checks candidate vfunc +0x14, returns candidate field +0x44 as an x87 float, or falls back to global float 0x005d856c. If target_id is nonzero and no direct entry exists, the body asks the owner/controller at this+0x10/+0x30 via vfunc +0x24 and probes that returned +0x160 target table. Static retail Ghidra evidence only; exact field names, runtime rumble/target behavior, BEA patching, and rebuild parity remain deferred.",
                tags("cmcbuggy", "target-value", "signature-corrected", "ret-0x4", "tranche-head")
            ),
            new Spec(
                "0x00445070",
                "CDiveBomber__SelectTarget",
                "CDiveBomber__SelectTarget",
                true,
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_target_position", voidPtr)
                },
                "Wave800 static read-back: CDiveBomber target-output helper reached from CCannon__SelectTarget at 0x004fd4e1. The caller and decompile show a single stack output pointer, so the older no-argument return-pointer signature was incomplete. The body walks the owner/controller target list at +0x15c/+0x160, resolves candidate target records through this+4 and each candidate's +0x88 id, filters inactive records through vfunc +0x14, chooses the highest observed priority at record +0x40 when record +0x0c is positive, and otherwise writes this unit's center position through CThing__GetCentrePos. Static retail Ghidra evidence only; exact source method identity, concrete target-record layout, runtime targeting behavior, BEA patching, and rebuild parity remain deferred.",
                tags("divebomber", "target-selection", "signature-corrected", "out-position")
            ),
            new Spec(
                "0x00449560",
                "CMine__AssignVec3AndReturnThis",
                "Vec3__AssignFromValuePointersAndReturnThis",
                true,
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x_value", floatPtr),
                    param("y_value", floatPtr),
                    param("z_value", floatPtr)
                },
                "Wave800 static read-back: owner-neutral Vec3 assignment helper. Instruction evidence uses ECX as the destination vector, dereferences the three stack arguments as 4-byte value pointers, stores those values into destination offsets +0/+4/+8, returns the destination pointer in EAX, and ends with RET 0xc. Xrefs include CMine__Init at 0x004ba41e plus one nearby unlabeled caller at 0x004494b8, but the helper body does not touch CMine fields, so the older CMine-specific owner label was too narrow. Static retail Ghidra evidence only; concrete Vec3 type recovery, exact source identity, runtime mine behavior, BEA patching, and rebuild parity remain deferred.",
                tags("vec3", "mine-context", "name-corrected", "signature-corrected", "ret-0xc")
            ),
            new Spec(
                "0x00449d40",
                "OID__FreeObject_Callback",
                "OID__FreeObject_Callback",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave800 static read-back: OID cleanup/free callback retained under the existing OID name because 657 current xrefs, mostly compiler unwind cleanup callbacks, call this row directly. Instruction evidence loads the single stack pointer argument, loads global memory manager/context 0x009c3df0 into ECX, forwards the pointer to CDXMemoryManager__Free at 0x00549220, and returns. Static retail Ghidra evidence only; exact allocator provenance, runtime exception cleanup behavior, BEA patching, and rebuild parity remain deferred.",
                tags("oid", "cleanup-callback", "memory-manager-free", "tranche-tail")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        println("ApplyGameplayObjectHelpersWave800 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave800 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
