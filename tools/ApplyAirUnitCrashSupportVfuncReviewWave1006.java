//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyAirUnitCrashSupportVfuncReviewWave1006 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
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
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            Function containing = getFunctionContaining(entry);
            if (containing != null && containing.getEntryPoint().equals(entry)) {
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.name);
            stats.missing++;
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
        Function fn = functionAtEntry(spec.address);
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
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "air-unit-crash-support-vfunc-review-wave1006",
            "wave1006-readback-verified",
            "retail-binary-evidence",
            "comment-normalized",
            "tag-normalized",
            "vtable-slot-evidence"
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
        println("ApplyAirUnitCrashSupportVfuncReviewWave1006 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        ParameterImpl[] thisOnly = new ParameterImpl[] {
            param("this", voidPtr)
        };

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00402fa0",
                "CUnit__UpdateMotionAndTrailEffects",
                "__thiscall",
                voidType,
                thisOnly,
                "Wave1006 static re-audit metadata normalization: air-unit vtable slot 66 refs at 0x005e362c (CBigAirUnit) and 0x005e3880 (CAirUnit) point at this existing CUnit motion/effects pass. The body updates velocity/friction state, clamps motion, advances attachment/trail particle and mesh renderer state, and includes a low-altitude crash path. Static retail Ghidra metadata/xref/decompile/vtable evidence only; no runtime flight proof, concrete CUnit layout, exact source-body identity, BEA patching, or rebuild parity is implied.",
                tags("cunit", "air-unit", "vtable-slot-66", "motion-effects")
            ),
            new Spec(
                "0x00403730",
                "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
                "__thiscall",
                voidType,
                thisOnly,
                "Wave1006 static re-audit metadata normalization: CFenrir, CCarver, CCarrier, CBigAirUnit, and CAirUnit vtable slot 68 rows point here. The body sets a state timestamp, then triggers the explosion/death path when flag bit 4 is set and unit-data +0x11c is zero. This remains a CAirUnit-family virtual helper, not a CExplosionInitThing method. Static retail Ghidra metadata/xref/decompile/vtable evidence only; exact source virtual name, support-field semantics, concrete layout, runtime crash behavior, BEA patching, and rebuild parity remain unproven.",
                tags("air-unit", "vtable-slot-68", "support-gate", "crash-death-path")
            ),
            new Spec(
                "0x00403760",
                "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes",
                "__thiscall",
                voidType,
                thisOnly,
                "Wave1006 static re-audit metadata normalization: CFenrir, CCarver, CCarrier, CBigAirUnit, and CAirUnit vtable slot 69 rows point here. The body resets the D0 threshold helper, then triggers the explosion/death path when flag bit 4 is set and unit-data +0x11c/+0x124 are both zero. This remains a CAirUnit-family virtual helper, not the older duplicate CUnitAI wrapper label. Static retail Ghidra metadata/xref/decompile/vtable evidence only; exact source virtual name, support-field semantics, concrete layout, runtime crash behavior, BEA patching, and rebuild parity remain unproven.",
                tags("air-unit", "vtable-slot-69", "support-gate", "crash-death-path")
            ),
            new Spec(
                "0x00403a50",
                "CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear",
                "__thiscall",
                intType,
                thisOnly,
                "Wave1006 static re-audit metadata normalization: CFenrir, CCarver, CDiveBomber, CPlane, CCarrier, CGroundAttackAircraft, CBomber, CBigAirUnit, and CAirUnit vtable slot 117 rows point here. The body compares current and prior/target position components and returns true when any component differs while flag bit 4 is clear. This remains an air/plane-family virtual predicate, not a CFrontEndPage method. Static retail Ghidra metadata/xref/decompile/vtable evidence only; exact source virtual name, concrete position/flag layout, runtime caller behavior, BEA patching, and rebuild parity remain unproven.",
                tags("air-unit", "plane-family", "vtable-slot-117", "position-delta-predicate")
            ),
            new Spec(
                "0x0047bf60",
                "CPlane__VFunc_69_CrashIfNoSupportModes",
                "__thiscall",
                voidType,
                thisOnly,
                "Wave1006 static re-audit metadata normalization: CDiveBomber, CPlane, CGroundAttackAircraft, and CBomber vtable slot 69 rows point here. The body calls CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes, then triggers the explosion/death path when unit-data +0x11c/+0x124 are both zero. This remains a plane-family override, not a generic CUnitAI owner label. Static retail Ghidra metadata/xref/decompile/vtable evidence only; exact source virtual name, support-field semantics, concrete layout, runtime crash behavior, BEA patching, and rebuild parity remain unproven.",
                tags("plane-family", "vtable-slot-69", "support-gate", "crash-death-path")
            ),
            new Spec(
                "0x004d20a0",
                "CPlane__VFunc_68_CrashIfNoAirSupport",
                "__thiscall",
                voidType,
                thisOnly,
                "Wave1006 static re-audit metadata normalization: CDiveBomber, CPlane, CGroundAttackAircraft, and CBomber vtable slot 68 rows point here. The body calls CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport, then triggers the explosion/death path when unit-data +0x11c is zero. This remains a plane-family override, not a CExplosionInitThing method. Static retail Ghidra metadata/xref/decompile/vtable evidence only; exact source virtual name, support-field semantics, concrete layout, runtime crash behavior, BEA patching, and rebuild parity remain unproven.",
                tags("plane-family", "vtable-slot-68", "support-gate", "crash-death-path")
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
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1006 air-unit crash/support vfunc review encountered missing/bad rows");
        }
    }
}
