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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyUnitAttachedNodeForwardersWave838 extends GhidraScript {
    private static class Spec {
        final String address;
        final String[] acceptedNames;
        final String newName;
        final String expectedSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String[] acceptedNames, String newName, String expectedSignature,
                String callingConvention, DataType returnType, ParameterImpl[] parameters,
                String comment, String[] tags) {
            this.address = address;
            this.acceptedNames = acceptedNames;
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

    private boolean acceptedName(Function fn, Spec spec) {
        for (String name : spec.acceptedNames) {
            if (fn.getName().equals(name)) {
                return true;
            }
        }
        return fn.getName().equals(spec.newName);
    }

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private String[] tags(String slotTag, String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "unit-attached-node-forwarders-wave838",
            "wave838-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "name-corrected",
            "cunit",
            "attached-node",
            "controller-forwarder",
            "ret-10",
            slotTag
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private ParameterImpl[] fourWordParams(DataType voidPtr, DataType intType) throws Exception {
        return new ParameterImpl[] {
            new ParameterImpl("this", voidPtr, currentProgram),
            new ParameterImpl("node_arg0", intType, currentProgram),
            new ParameterImpl("node_arg1", intType, currentProgram),
            new ParameterImpl("node_arg2", intType, currentProgram),
            new ParameterImpl("node_arg3", intType, currentProgram)
        };
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = voidPtr();

        return new Spec[] {
            new Spec(
                "0x004fce40",
                new String[] { "CUnitAI__CallAttachedNodeVFunc14IfPresent" },
                "CUnit__ForwardAttachedNodeVFunc14IfPresent",
                "int __thiscall CUnit__ForwardAttachedNodeVFunc14IfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)",
                "__thiscall",
                intType,
                fourWordParams(voidPtr, intType),
                "Wave838 static read-back/name/signature correction: this CUnit-tail attached-node forwarder loads the attached controller/node pointer from this+0x208, null-gates it, copies four explicit stack dwords into a 16-byte call frame, dispatches attached-node vfunc +0x14, returns the callee EAX value when present, and ends with RET 0x10 at 0x004fce71. The saved name corrects stale CUnitAI__CallAttachedNodeVFunc14IfPresent owner wording; adjacent CUnit helpers, shared this+0x208 usage, and xrefs including 0x0044610a CUnitAI__UpdateDoorWingEngagement_MidRange support bounded CUnit helper ownership. Static retail Ghidra evidence only; exact attached-node/controller type, argument layout, return semantics, runtime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("vfunc-14", "owner-corrected")
            ),
            new Spec(
                "0x004fce80",
                new String[] { "CUnit__ForwardControllerQuery18" },
                "CUnit__ForwardAttachedNodeVFunc18IfPresent",
                "int __thiscall CUnit__ForwardAttachedNodeVFunc18IfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)",
                "__thiscall",
                intType,
                fourWordParams(voidPtr, intType),
                "Wave838 static read-back/name/signature correction: this CUnit-tail attached-node forwarder loads the attached controller/node pointer from this+0x208, null-gates it, copies four explicit stack dwords into a 16-byte call frame, dispatches attached-node vfunc +0x18, returns the callee EAX value when present, and ends with RET 0x10 at 0x004fceb1. The saved name replaces the older broad CUnit__ForwardControllerQuery18 label with the observed vfunc-slot forwarding shape. Static callers include 0x0047a38a, 0x0048a113, 0x004ef404, 0x004fecda, and 0x004feda1. Static retail Ghidra evidence only; exact attached-node/controller type, argument layout, return semantics, runtime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("vfunc-18", "name-refined")
            ),
            new Spec(
                "0x004fcec0",
                new String[] { "CUnitAI__GetAttachedNodeReadyState" },
                "CUnit__ForwardAttachedNodeVFunc1CIfPresent",
                "int __thiscall CUnit__ForwardAttachedNodeVFunc1CIfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)",
                "__thiscall",
                intType,
                fourWordParams(voidPtr, intType),
                "Wave838 static read-back/name/signature correction: this CUnit-tail attached-node forwarder loads the attached controller/node pointer from this+0x208, null-gates it, copies four explicit stack dwords into a 16-byte call frame, dispatches attached-node vfunc +0x1c, returns the callee EAX value when present, and ends with RET 0x10 at 0x004fcef1. The saved name corrects stale CUnitAI__GetAttachedNodeReadyState owner/semantic wording; adjacent CUnit helpers, shared this+0x208 usage, CSquadNormal__BuildAttackFormation xrefs at 0x004e8ba9/0x004e8c06, and CUnitAI door-wing xrefs at 0x00445db5/0x0044626e/0x00446472 support bounded CUnit helper ownership. Static retail Ghidra evidence only; exact attached-node/controller type, argument layout, return semantics, runtime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("vfunc-1c", "owner-corrected")
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

        if (!acceptedName(fn, spec)) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected accepted old name or " + spec.newName);
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
            throw new RuntimeException("Wave838 had missing/bad rows");
        }
    }
}
