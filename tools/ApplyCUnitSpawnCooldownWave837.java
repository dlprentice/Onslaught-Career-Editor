//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCUnitSpawnCooldownWave837 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String expectedSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, String expectedSignature, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
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
            "cunit-spawn-cooldown-wave837",
            "wave837-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "name-corrected",
            "cunit",
            "spawn-system",
            "spawn-cooldown",
            "spawner-callsite"
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

        return new Spec[] {
            new Spec(
                "0x004fc3a0",
                "CSpawnerThng__SetCooldownState3",
                "CUnit__SetSpawnCooldownState3",
                "void __thiscall CUnit__SetSpawnCooldownState3(void * this, float cooldown_delay)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("this", voidPtr, currentProgram),
                    new ParameterImpl("cooldown_delay", floatType, currentProgram)
                },
                "Wave837 static read-back/signature/name correction: CUnit__SetSpawnCooldownState3 is called from CSpawnerThng__ProcessSpawnWave at 0x004e430f after CWorldPhysicsManager__CreateThingByType and the spawned object's vfunc +0x24 init. The caller sets ECX to the created object and pushes one value from spawner config +0x1c. RET 0x4 at 0x004fc3ba plus FADD [ESP+0x4] at 0x004fc3b0 prove one explicit float cooldown_delay argument after ECX, replacing the stale CSpawnerThng__SetCooldownState3 owner and old int cooldown_ticks/unused_scale signature. The body writes state literal 3 to this+0x168 and writes DAT_00672fd0 + cooldown_delay to this+0x16c as an absolute spawn-cooldown/ready-time value. Immediate CUnit code neighborhood and the created-object receiver support bounded CUnit helper naming. Static retail Ghidra evidence only; exact Unit.cpp source-body identity, exact state enum meaning, concrete CUnit field names/layout, runtime spawn activation/cooldown behavior, BEA patching, and rebuild parity remain deferred.",
                tags("created-object", "state3", "global-time", "ret-4", "owner-corrected")
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
        if (!fn.getName().equals(spec.newName)) {
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
            println("MISSING: " + spec.address + " " + spec.newName);
            stats.missing++;
            return;
        }

        if (!fn.getName().equals(spec.oldName) && !fn.getName().equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.newName);
        boolean needsSignature = !sameSignature(fn, spec);
        boolean needsComment = fn.getComment() == null || !fn.getComment().equals(spec.comment);
        boolean needsTags = !hasTags(fn, spec.tags);

        if (!needsRename && !needsSignature && !needsComment && !needsTags) {
            println("SKIP: " + spec.address + " already matches " + spec.newName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.newName
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
            fn.setName(spec.newName, SourceType.USER_DEFINED);
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

        if (stats.missing > 0 || stats.bad > 0) {
            throw new RuntimeException("Wave837 had missing/bad rows");
        }
    }
}
