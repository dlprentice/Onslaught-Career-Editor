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

public class ApplyFEPWingmenWave565 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String previousName;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String previousName, boolean updateSignature,
                String callingConvention, DataType returnType, ParameterImpl[] params,
                String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousName = previousName;
            this.updateSignature = updateSignature;
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
            "fepwingmen-wave565",
            "retail-binary-evidence",
            "retail-only",
            "no-source-file",
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
        if (!spec.updateSignature) {
            return true;
        }
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
        if (!spec.updateSignature) {
            return "<signature unchanged>";
        }
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
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.name + " " + expectedSignature(spec));
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
            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.params);
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("APPLY: " + spec.address + " -> " + spec.name + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = voidPtr();

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00521650",
                "CFEPWingmen__GetWingmenCount",
                "CFEPWingmen__GetWingmenCount",
                false,
                null,
                null,
                new ParameterImpl[] {},
                "Wave565 retail-binary-first comment hardening: CFEPBEConfig render/button callers use this helper to scan DAT_0089da6c/DAT_0089da74 for current level DAT_0089d94c, then count nonzero wingman slots at record +0x04, +0x0c, and +0x08. FEPWingmen.cpp source is absent from references/Onslaught; record layout and runtime menu behavior remain unproven.",
                tags("fep-wingmen", "wingman-count", "frontend-config", "signature-deferred")
            ),
            new Spec(
                "0x00521a60",
                "CFEPWingmen__Destroy",
                "CFEPWingmen__Destroy",
                false,
                null,
                null,
                new ParameterImpl[] {},
                "Wave565 retail-binary-first comment hardening: vtable 0x005dba10 slot 1 frees up to three frontend thing pointers at this+0x08/+0x0c/+0x10, then drains the pointer set at this+0x28 via CSPtrSet__Remove, CFEPBEConfig__CleanupSquads, and CDXMemoryManager__Free. Signature left unchanged because thiscall/fastcall storage still needs a focused convention pass; runtime owner/layout behavior remains unproven.",
                tags("fep-wingmen", "destructor", "frontend-thing-cleanup", "pointer-set", "signature-deferred")
            ),
            new Spec(
                "0x00521ae0",
                "CFEPWingmen__Load",
                "CFEPWingmen__Load",
                true,
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("stream", voidPtr) },
                "Wave565 retail-binary-first load signature correction: RET 0x4 plus the prologue storing ECX as this and moving the stack argument into EDI prove __thiscall this plus one stream argument. Allocates a 0x24 record from FEPWingmen.cpp line 0xd3, initializes record+0x14 as a CSPtrSet, reads version/count/name strings from CDXMemBuffer, applies version <2/<3 defaults for slots +0x04/+0x08/+0x0c/+0x10, and appends the record to this+0x28. FEPWingmen.cpp source is absent from references/Onslaught; runtime data-file schema remains unproven.",
                tags("fep-wingmen", "load", "cdxmembuffer", "pointer-set", "signature-corrected")
            ),
            new Spec(
                "0x00521c80",
                "CFEPWingmen__Update",
                "CFEPWingmen__Update",
                false,
                null,
                null,
                new ParameterImpl[] {},
                "Wave565 retail-binary-first comment hardening: vtable 0x005dba10 slot 2 per-frame update increments this+0x14 by _DAT_005d8574, calls the shared spinner transform/pulse helper for each live frontend thing at this+0x08/+0x0c/+0x10, decrements/clamps fade fields this+0x1c and this+0x20 by _DAT_005d85c0, and in dev mode calls vtable slot +0x0c when state==0. Missing slot +0x0c target at 0x00521d20 remains deferred; runtime UI behavior remains unproven.",
                tags("fep-wingmen", "per-frame-update", "spinner-helper", "devmode", "missing-boundary-deferred")
            ),
            new Spec(
                "0x005230c0",
                "CFEPWingmen__TransitionNotification",
                "CFEPWingmen__VFunc_06_005230c0",
                true,
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("from_page", intType) },
                "Wave565 rename/signature/comment hardening: vtable 0x005dba10 slot 6 matches the frontend TransitionNotification convention used by FEPCredits/FEPMultiplayerStart/FEPScreenPos/FEPVirtualKeyboard. RET 0x4 proves one stack from_page argument, but this implementation ignores it; it calls PLATFORM__GetSysTimeFloat through platform singleton 0x0088a0a8, stores the timestamp at this+0x04, and clears this+0x18. FEPWingmen.cpp source is absent from references/Onslaught; runtime frontend transition behavior remains unproven.",
                tags("fep-wingmen", "transition-notification", "vtable-slot", "timestamp-reset", "signature-corrected", "renamed")
            ),
            new Spec(
                "0x0046baf0",
                "CFEPWingmen__UpdateSpinnerTransformAndPulse",
                "CFEPWingmen__UpdateSpinnerTransformAndPulse",
                false,
                null,
                null,
                new ParameterImpl[] {},
                "Wave565 retail-binary-first comment hardening: shared frontend spinner helper called by CFEPWingmen__Update, CFEPMultiplayerStart__Process, and CFEPBEConfig__UpdateTransitionTimers. It writes a yaw/pulse transform from DAT_00672fd0 into matrix-like fields this+0x14..0x40, then oscillates alpha/pulse field this+0x4c using rate this+0x48*_DAT_005d8bb8, direction flag this+0x50, and countdown this+0x54. Existing owner name is retained but function is shared; runtime visual behavior remains unproven.",
                tags("shared-frontend-spinner", "transform", "pulse", "fep-wingmen", "frontend-render")
            )
        };

        Stats stats = new Stats();
        println("ApplyFEPWingmenWave565 mode=" + (dryRun ? "dry" : "apply") + " targets=" + specs.length);
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply") +
            " updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave565 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
