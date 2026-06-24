//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyUnwindContinuationWave747 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

        Spec(String address, String comment, String[] tags) {
            this.address = address;
            this.name = "Unwind@" + address.substring(2);
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "unwind-continuation-wave747",
            "wave747-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "compiler-unwind",
            "scope-table"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean signatureMatches(Function fn) {
        if (!"__cdecl".equals(fn.getCallingConventionName())) {
            return false;
        }
        DataType actualReturn = fn.getReturnType();
        if (actualReturn == null || !actualReturn.isEquivalent(VoidDataType.dataType)) {
            return false;
        }
        return fn.getParameterCount() == 0;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn)) {
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
        if (!signatureMatches(readBack)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
                stats.bad++;
                return;
            }

            boolean signatureNeedsUpdate = !signatureMatches(fn);
            boolean changed = needsUpdate(fn, spec);
            if (!changed) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: would update " + spec.address + " " + spec.name + " signature=void __cdecl " + spec.name + "(void)");
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                } else {
                    stats.commentOnlyUpdated++;
                }
                stats.skipped++;
                return;
            }

            fn.setCallingConvention("__cdecl");
            fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
            fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + spec.name + " signature=void __cdecl " + spec.name + "(void)");
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.updated++;
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
            stats.bad++;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        Spec[] specs = new Spec[] {
            new Spec("0x005d1cd9", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a WorldPhysicsManager/CPhysicsScript-adjacent embedded-set scope-table run. Scope-table DATA xref 0x0061ab3c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x4c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime embedded pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "sptrset", "clear", "embedded-set")),
            new Spec("0x005d1ce4", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a WorldPhysicsManager/CPhysicsScript-adjacent embedded-set scope-table run. Scope-table DATA xref 0x0061ab44 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x5c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime embedded pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "sptrset", "clear", "embedded-set")),
            new Spec("0x005d1d00", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsScript statement scope-table run. Scope-table DATA xref 0x0061ab6c points at this body; decompile/instruction evidence shows it calls CPhysicsScriptStatement__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics-script statement cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-script-statement", "destructor")),
            new Spec("0x005d1d20", "Wave747 static read-back: WorldPhysicsManager.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061ab94 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with WorldPhysicsManager.h debug path 0x00625850, line 0xe, and memtype 0x94e. Static retail Ghidra metadata/decompile/xref evidence only; runtime world-physics allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "worldphysicsmanager-h", "free-object")),
            new Spec("0x005d1d50", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsScript statement scope-table run. Scope-table DATA xref 0x0061abbc points at this body; decompile/instruction evidence shows it calls CPhysicsScriptStatement__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics-script statement cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-script-statement", "destructor")),
            new Spec("0x005d1d70", "Wave747 static read-back: WorldPhysicsManager.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061abe4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with WorldPhysicsManager.h debug path 0x00625850, line 0x3e, and memtype 0x963. Static retail Ghidra metadata/decompile/xref evidence only; runtime world-physics allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "worldphysicsmanager-h", "free-object")),
            new Spec("0x005d1da0", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsScript statement scope-table run. Scope-table DATA xref 0x0061ac0c points at this body; decompile/instruction evidence shows it calls CPhysicsScriptStatement__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics-script statement cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-script-statement", "destructor")),
            new Spec("0x005d1dc0", "Wave747 static read-back: WorldPhysicsManager.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061ac34 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with WorldPhysicsManager.h debug path 0x00625850, line 0x3f, and memtype 0x96a. Static retail Ghidra metadata/decompile/xref evidence only; runtime world-physics allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "worldphysicsmanager-h", "free-object")),
            new Spec("0x005d1df0", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsScript statement scope-table run. Scope-table DATA xref 0x0061ac5c points at this body; decompile/instruction evidence shows it calls CPhysicsScriptStatement__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics-script statement cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-script-statement", "destructor")),
            new Spec("0x005d1e10", "Wave747 static read-back: WorldPhysicsManager.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061ac84 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with WorldPhysicsManager.h debug path 0x00625850, line 0x40, and memtype 0x978. Static retail Ghidra metadata/decompile/xref evidence only; runtime world-physics allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "worldphysicsmanager-h", "free-object")),
            new Spec("0x005d1e29", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a WorldPhysicsManager/CPhysicsScript-adjacent embedded-set scope-table run. Scope-table DATA xref 0x0061ac8c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x3c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime embedded pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "sptrset", "clear", "embedded-set")),
            new Spec("0x005d1e34", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a WorldPhysicsManager/CPhysicsScript-adjacent embedded-set scope-table run. Scope-table DATA xref 0x0061ac94 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x4c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime embedded pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "sptrset", "clear", "embedded-set")),
            new Spec("0x005d1e3f", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a WorldPhysicsManager/CPhysicsScript-adjacent embedded-set scope-table run. Scope-table DATA xref 0x0061ac9c points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x5c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime embedded pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "sptrset", "clear", "embedded-set")),
            new Spec("0x005d1e4a", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a WorldPhysicsManager/CPhysicsScript-adjacent embedded-set scope-table run. Scope-table DATA xref 0x0061aca4 points at this body; decompile/instruction evidence shows it calls CSPtrSet__Clear on object field *(EBP-0x10)+0x6c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime embedded pointer-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "sptrset", "clear", "embedded-set")),
            new Spec("0x005d1e60", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsScript statement scope-table run. Scope-table DATA xref 0x0061accc points at this body; decompile/instruction evidence shows it calls CPhysicsScriptStatement__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics-script statement cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-script-statement", "destructor")),
            new Spec("0x005d1e80", "Wave747 static read-back: WorldPhysicsManager.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061acf4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with WorldPhysicsManager.h debug path 0x00625850, line 0x41, and memtype 0x97f. Static retail Ghidra metadata/decompile/xref evidence only; runtime world-physics allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "worldphysicsmanager-h", "free-object")),
            new Spec("0x005d1eb0", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsScript statement scope-table run. Scope-table DATA xref 0x0061ad1c points at this body; decompile/instruction evidence shows it calls CPhysicsScriptStatement__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics-script statement cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-script-statement", "destructor")),
            new Spec("0x005d1ed0", "Wave747 static read-back: WorldPhysicsManager.h compiler-generated SEH unwind cleanup callback. Scope-table DATA xref 0x0061ad44 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at EBP-0x10 with WorldPhysicsManager.h debug path 0x00625850, line 0x41, and memtype 0x986. Static retail Ghidra metadata/decompile/xref evidence only; runtime world-physics allocation cleanup behavior, exact source body identity, BEA patching, and rebuild parity remain unproven.", tags("worldphysicsmanager", "worldphysicsmanager-h", "free-object")),
            new Spec("0x005d1f00", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsScript statement scope-table run. Scope-table DATA xref 0x0061ad6c points at this body; decompile/instruction evidence shows it calls CPhysicsScriptStatement__dtor on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics-script statement cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-script-statement", "destructor")),
            new Spec("0x005d1f20", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsUnitValue scope-table run. Scope-table DATA xref 0x0061ad94 points at this body; decompile/instruction evidence shows it calls CPhysicsUnitValue__dtor_base on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics unit-value cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-unit-value", "destructor")),
            new Spec("0x005d1f40", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsUnitValue scope-table run. Scope-table DATA xref 0x0061adbc points at this body; decompile/instruction evidence shows it calls CPhysicsUnitValue__dtor_base on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics unit-value cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-unit-value", "destructor")),
            new Spec("0x005d1f60", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsUnitValue scope-table run. Scope-table DATA xref 0x0061ade4 points at this body; decompile/instruction evidence shows it calls CPhysicsUnitValue__dtor_base on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics unit-value cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-unit-value", "destructor")),
            new Spec("0x005d1f80", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsRoundValue scope-table run. Scope-table DATA xref 0x0061ae0c points at this body; decompile/instruction evidence shows it calls CPhysicsRoundValue__dtor_base on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics round-value cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-round-value", "destructor")),
            new Spec("0x005d1fa0", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CPhysicsRoundValue scope-table run. Scope-table DATA xref 0x0061ae34 points at this body; decompile/instruction evidence shows it calls CPhysicsRoundValue__dtor_base on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime physics round-value cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("cphysicsscript", "physics-round-value", "destructor")),
            new Spec("0x005d1fc0", "Wave747 static read-back: compiler-generated SEH unwind cleanup callback in a CComplexThing teardown scope-table run. Scope-table DATA xref 0x0061ae5c points at this body; decompile/instruction evidence shows it calls CComplexThing__dtor_base on the pointer at EBP-0x10. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source body, runtime complex-thing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("complexthing", "destructor"))
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing > 0 || stats.bad > 0) {
            throw new IllegalStateException("Wave747 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
