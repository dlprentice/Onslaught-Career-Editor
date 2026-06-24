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

public class ApplyUnitFactionSpawnWave527 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final boolean renameAllowed;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags, boolean renameAllowed) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.renameAllowed = renameAllowed;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "unit-faction-spawn-wave527",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.name)) {
            if (!spec.renameAllowed) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }
            if (dryRun) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.wouldRename++;
                stats.skipped++;
                return;
            }
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (!needsUpdate(fn, spec)) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            stats.skipped++;
            return;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004fd830",
                "CUnit__SetFactionForHierarchy",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("faction_state", intType)},
                "Wave527 Unit faction/spawn signature/comment hardening: RET 0x4 proves one explicit faction_state argument after ECX; the prior second parameter was stale register carryover. The body writes this+0x138, recurses through child reader cells at +0x19c, removes this from global faction lists DAT_008550c0/DAT_008550b0, and re-adds unmounted units for observed state values 0, 1, and 6. Static retail evidence only; exact faction enum names, global-list semantics, runtime AI behavior, and rebuild parity remain unproven.",
                tags("unit-faction", "child-recursive", "global-unit-set"),
                true
            ),
            new Spec(
                "0x004fd8d0",
                "CUnit__FindChildReaderByField270",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("field270_value", intType)},
                "Wave527 Unit faction/spawn owner/signature hardening: renamed from a destructible-controller owner label because CDestructableSegmentsController__Init passes its owner Unit pointer at +0x10, and the body walks the Unit child-reader list at this+0x19c. RET 0x4 proves one explicit field270_value argument after ECX. The helper returns the first child reader cell whose child pointer is non-null and whose child field +0x270 matches the requested value. Static retail evidence only; exact reader-cell layout, field270 meaning, runtime destructible segment setup, and rebuild parity remain unproven.",
                tags("unit-child-list", "owner-corrected", "destructible-segment"),
                true
            ),
            new Spec(
                "0x004fd910",
                "CUnit__FindNearestFactionAnchor",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("out_position4", voidPtr)},
                "Wave527 Unit faction/spawn signature/comment hardening: RET 0x4 proves one explicit out_position4 argument after ECX; the prior second parameter was stale register carryover. The body scans global anchor list DAT_00855160, accepts entries whose vfunc +0x108 matches this+0x138, picks the closest XY position to this+0x1c/+0x20, and writes four dwords/floats to out_position4. Static retail evidence only; exact anchor type, faction enum names, output vector layout, runtime AI behavior, and rebuild parity remain unproven.",
                tags("unit-faction", "anchor-search", "position-output"),
                true
            ),
            new Spec(
                "0x004fda10",
                "CUnit__GetProfileState120",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave527 Unit faction/spawn owner/signature hardening: renamed from CUnitAI ownership because callers pass attached Unit pointers from AI objects, and the body only reads this+0x164 -> +0x120. Register-this helper returns that profile/config field directly. Static retail evidence only; exact field meaning, weapon/door-wing state semantics, runtime AI behavior, and rebuild parity remain unproven.",
                tags("unit-profile", "owner-corrected", "query"),
                true
            ),
            new Spec(
                "0x004fda20",
                "CUnit__PropagateTargetUnitToHierarchy",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("target_unit", voidPtr)},
                "Wave527 Unit faction/spawn signature/comment hardening: RET 0x4 proves one explicit target_unit argument after ECX; the prior second parameter was stale register carryover. The body forwards target_unit+0x148 through mounted target state at this+0x148, refreshes support selection through this+0x13c when present, then recursively propagates target_unit through child reader cells at +0x19c. Static retail evidence only; exact target-reader layout, script Attack semantics, runtime AI behavior, and rebuild parity remain unproven.",
                tags("unit-target", "child-recursive", "script-attack"),
                true
            ),
            new Spec(
                "0x004fdad0",
                "CUnit__TrySpawnMembersForTarget",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("target_unit", voidPtr)},
                "Wave527 Unit faction/spawn signature/comment hardening: RET 0x4 proves one explicit target_unit argument after ECX; the prior second parameter was stale register carryover. The body requires target_unit and vfunc +0x18c success, walks spawner/support entries at this+0x18c, gates each entry through CUnit__CanProvideSupportNow, mount/height/profile flag checks, target-mask compatibility, and profile range fields +0x2c/+0x30, then calls CSpawnerThng__DoSpawn. Static retail evidence only; exact spawner/support ownership, profile flag semantics, runtime spawn behavior, and rebuild parity remain unproven.",
                tags("unit-spawn", "support-selection", "target-gated"),
                true
            ),
            new Spec(
                "0x004fdc20",
                "CUnit__UpdateSpawnCountAccounting",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave527 Unit faction/spawn signature/comment hardening: register-this vtable target reads profile pointer this+0x164, adjusts global count DAT_008a9b8c by CUnit__GetTypePriorityWeight for observed faction states 0 and 1, then walks entries at this+0x18c and calls CSpawnerThng__UpdateSpawnCount. Static retail evidence only; exact global counter semantics, faction enum names, vtable-slot coverage, runtime spawn accounting, and rebuild parity remain unproven.",
                tags("unit-spawn", "vtable-target", "global-counter"),
                true
            ),
            new Spec(
                "0x004fdcb0",
                "CUnit__SetEngagementModeAndMaybeClearTargetReader",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("engagement_mode", intType)},
                "Wave527 Unit faction/spawn signature/comment hardening: RET 0x4 proves one explicit engagement_mode argument after ECX; the prior second parameter was stale register carryover. The body writes this+0x210 and, when this+0x13c exists and engagement_mode equals 1, clears the active reader at +0xc through CGenericActiveReader__SetReader and zeroes +0x10. Static retail evidence only; exact engagement enum names, reader meaning, vtable-slot coverage, runtime AI behavior, and rebuild parity remain unproven.",
                tags("unit-engagement", "active-reader", "vtable-target"),
                true
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave527 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
