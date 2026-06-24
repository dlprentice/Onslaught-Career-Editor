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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCUnitApplyDamageWave835 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedSignature, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedSignature = expectedSignature;
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
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cunit-apply-damage-wave835",
            "wave835-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "cunit",
            "unit-damage",
            "virtual-damage-handler",
            "shield-life-damage",
            "destructible-segments",
            "message-box-text"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = voidPtr();
        DataType floatType = FloatDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x004f9a90",
                "CUnit__ApplyDamage",
                "void __thiscall CUnit__ApplyDamage(void * this, float damage_amount, void * damage_source, int apply_shields, int mesh_part_index)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("this", voidPtr, currentProgram),
                    new ParameterImpl("damage_amount", floatType, currentProgram),
                    new ParameterImpl("damage_source", voidPtr, currentProgram),
                    new ParameterImpl("apply_shields", intType, currentProgram),
                    new ParameterImpl("mesh_part_index", intType, currentProgram)
                },
                "Wave835 static read-back/signature/comment hardening: CUnit__ApplyDamage is important shared CUnit damage/lifetime infrastructure, not throwaway tail code. RET 0x10 at 0x004fa4a7 plus direct callsite pushes at 0x004037be, 0x00417a16, 0x0048006d, and 0x004898b0 prove four explicit stack arguments after ECX: damage_amount, damage_source, apply_shields, and mesh_part_index. Nineteen DATA slots at 0x005dd828/0x005dfa38/0x005dfddc/0x005e002c/0x005e027c/0x005e0724/0x005e0980/0x005e0bd0/0x005e1080/0x005e1530/0x005e1c24/0x005e232c/0x005e257c/0x005e2a1c/0x005e3114/0x005e3374/0x005e3de0/0x005e403c/0x005e4298 point at this body. Observed static behavior resets a damage cooldown helper through this+0x148, scales damage by profile/state fields, repairs health-like this+0xf8 for non-positive damage, applies nexus/weakpoint mesh-part gates using s_nexus_00633af4 and s_weakpoint_00633ae8, forwards to CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold when this+0x178 exists, otherwise applies shield-like this+0x100 before life-like this+0xf8, dispatches death/cleanup vfuncs, emits a particle effect when the profile effect pointer is present, and queues profile/Tara/Billy damage text through CMessageBox with the Unit.cpp debug allocation anchor 0x00633b6c line 0x44d. Static retail Ghidra evidence only; exact source body identity, concrete CUnit/profile/damage-source/segment layouts, exact message text semantics, runtime damage/shield/death behavior, BEA patching, and rebuild parity remain deferred.",
                tags("unit-health", "weakpoint", "nexus", "death-dispatch", "particle-effect")
            )
        };
    }

    private boolean hasTags(Function fn, String[] expected) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.expectedName)) {
            return false;
        }
        if (!fn.getSignature().toString().equals(spec.expectedSignature)) {
            return false;
        }
        if (!fn.getSignature().getReturnType().isEquivalent(spec.returnType)) {
            return false;
        }
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        return true;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.expectedName);
        boolean needsSignature = !sameSignature(fn, spec);
        boolean needsComment = fn.getComment() == null || !fn.getComment().equals(spec.comment);
        boolean needsTags = !hasTags(fn, spec.tags);

        if (!needsRename && !needsSignature && !needsComment && !needsTags) {
            println("SKIP: " + spec.address + " already matches " + spec.expectedName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.expectedName
                + " needsRename=" + needsRename
                + " needsSignature=" + needsSignature
                + " needsComment=" + needsComment
                + " needsTags=" + needsTags);
            stats.skipped++;
            if (needsRename) {
                stats.wouldRename++;
            }
            if (needsSignature) {
                stats.signatureUpdated++;
            } else if (needsComment || needsTags) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (needsRename) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsSignature) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        } else if (needsComment || needsTags) {
            stats.commentOnlyUpdated++;
        }
        if (needsComment) {
            fn.setComment(spec.comment);
        }
        for (String tagName : spec.tags) {
            fn.addTag(tagName);
        }

        Function readBack = functionAtEntry(spec.address);
        if (readBack == null || !sameSignature(readBack, spec) || readBack.getComment() == null
                || !readBack.getComment().equals(spec.comment) || !hasTags(readBack, spec.tags)) {
            println("BAD: readback mismatch at " + spec.address + " expected " + spec.expectedSignature);
            if (readBack != null) {
                println("BAD: got name=" + readBack.getName() + " signature=" + readBack.getSignature().toString());
            }
            stats.bad++;
            return;
        }

        println("READBACK_OK: " + spec.address + " " + readBack.getName() + " " + readBack.getSignature().toString());
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
            Thread.sleep(100);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
