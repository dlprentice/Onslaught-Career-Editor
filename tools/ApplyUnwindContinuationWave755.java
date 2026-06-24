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

public class ApplyUnwindContinuationWave755 extends GhidraScript {
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
            "unwind-continuation-wave755",
            "wave755-readback-verified",
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
            new Spec("0x005d30a0", "Wave755 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bde4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x2f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d30b6", "Wave755 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bdec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x33. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d30cc", "Wave755 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bdf4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x37. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d30e2", "Wave755 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bdfc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x3b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d30f8", "Wave755 static read-back: InitThing.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061be04 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with InitThing.cpp debug path 0x0062d7b0, line token 0x09, and allocation/type value 0x3f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime factory cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("initthing", "free-object")),
            new Spec("0x005d3120", "Wave755 static read-back: compiler-generated SEH unwind destructor callback in the InitThing-to-mapwho transition run. Scope-table DATA xref 0x0061be2c points at this body; decompile/instruction evidence shows it jumps to CUMTexture__dtor_base with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime texture cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("texture", "destructor")),
            new Spec("0x005d3140", "Wave755 static read-back: compiler-generated SEH unwind monitor cleanup callback. Scope-table DATA xref 0x0061be54 points at this body; decompile/instruction evidence shows it jumps to CMonitor__Shutdown_Thunk with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown", "thunk")),
            new Spec("0x005d3160", "Wave755 static read-back: compiler-generated SEH unwind monitor cleanup callback. Scope-table DATA xref 0x0061be7c points at this body; decompile/instruction evidence shows it jumps to CMonitor__Shutdown_Thunk with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "shutdown", "thunk")),
            new Spec("0x005d3180", "Wave755 static read-back: compiler-generated SEH unwind local line-helper cleanup callback. Scope-table DATA xref 0x0061bea4 points at this body; decompile/instruction evidence shows it jumps to CLine__SetBaseVtable_00426360 with ECX loaded from stack local EBP-0x40. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("line-helper", "vtable-reset")),
            new Spec("0x005d31a0", "Wave755 static read-back: compiler-generated SEH unwind image-loader cleanup callback. Scope-table DATA xref 0x0061becc points at this body; decompile/instruction evidence shows it jumps to CTGALoader__Destructor with ECX loaded from stack local EBP-0x128. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime image-loader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("tga-loader", "destructor")),
            new Spec("0x005d31c0", "Wave755 static read-back: mapwho.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bef4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x20) with mapwho.cpp debug path 0x0062db88, line token 0x45, and allocation/type value 0x44. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime mapwho cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mapwho", "free-object")),
            new Spec("0x005d31e0", "Wave755 static read-back: compiler-generated SEH unwind motion-controller cleanup callback. Scope-table DATA xref 0x0061bf1c points at this body; decompile/instruction evidence shows it jumps to CMotionController__dtor_base with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime motion-controller cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("motion-controller", "destructor")),
            new Spec("0x005d3200", "Wave755 static read-back: MCBuggy.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bf44 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with MCBuggy.cpp debug path 0x0062dc80, line token 0x1b, and allocation/type value 0x4e. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime MCBuggy cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mcbuggy", "free-object")),
            new Spec("0x005d3216", "Wave755 static read-back: MCBuggy.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bf4c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with MCBuggy.cpp debug path 0x0062dc80, line token 0x1b, and allocation/type value 0x52. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime MCBuggy cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mcbuggy", "free-object")),
            new Spec("0x005d3240", "Wave755 static read-back: MCBuggy.cpp-adjacent compiler-generated SEH unwind profiling cleanup callback. Scope-table DATA xref 0x0061bf74 points at this body; decompile/instruction evidence shows it jumps to CMCBuggy__ProfileEnd with ECX loaded from stack local EBP-0x120. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime profiler behavior, BEA patching, and rebuild parity remain unproven.", tags("mcbuggy", "profile")),
            new Spec("0x005d3260", "Wave755 static read-back: MCBuggy.cpp-adjacent compiler-generated SEH unwind motion-controller cleanup callback. Scope-table DATA xref 0x0061bf9c points at this body; decompile/instruction evidence shows it jumps to CMotionController__dtor_base with ECX loaded from *(EBP-0x20). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime motion-controller cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mcbuggy", "motion-controller", "destructor")),
            new Spec("0x005d3280", "Wave755 static read-back: MCBuggy.cpp-adjacent compiler-generated SEH unwind motion-controller cleanup callback. Scope-table DATA xref 0x0061bfc4 points at this body; decompile/instruction evidence shows it jumps to CMotionController__dtor_base with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime motion-controller cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mcbuggy", "motion-controller", "destructor")),
            new Spec("0x005d32a0", "Wave755 static read-back: MCMech.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bfec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x160) with MCMech.cpp debug path 0x0062df60, line token 0x1b, and allocation/type value 0x131. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime MCMech cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mcmech", "free-object")),
            new Spec("0x005d32bc", "Wave755 static read-back: MCMech.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bff4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x160) with MCMech.cpp debug path 0x0062df60, line token 0x1b, and allocation/type value 0x135. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime MCMech cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mcmech", "free-object")),
            new Spec("0x005d32d8", "Wave755 static read-back: MCMech.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061bffc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x160) with MCMech.cpp debug path 0x0062df60, line token 0x1b, and allocation/type value 0x17d. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime MCMech cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mcmech", "free-object")),
            new Spec("0x005d3300", "Wave755 static read-back: MCMech.cpp-adjacent compiler-generated SEH unwind local line-helper cleanup callback. Scope-table DATA xref 0x0061c024 points at this body; decompile/instruction evidence shows it jumps to CLine__SetBaseVtable_00426360 with ECX loaded from stack local EBP-0x40. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime line-helper cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mcmech", "line-helper", "vtable-reset")),
            new Spec("0x005d3320", "Wave755 static read-back: MCMech.cpp-adjacent compiler-generated SEH unwind profiling cleanup callback. Scope-table DATA xref 0x0061c04c points at this body; decompile/instruction evidence shows it jumps to CMCBuggy__ProfileEnd with ECX loaded from stack local EBP-0x1b4. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime profiler behavior, BEA patching, and rebuild parity remain unproven.", tags("mcmech", "profile")),
            new Spec("0x005d3340", "Wave755 static read-back: MCMech.cpp-adjacent compiler-generated SEH unwind motion-controller cleanup callback. Scope-table DATA xref 0x0061c074 points at this body; decompile/instruction evidence shows it jumps to CMotionController__dtor_base with ECX loaded from *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime motion-controller cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mcmech", "motion-controller", "destructor")),
            new Spec("0x005d3360", "Wave755 static read-back: MCTentacle.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c09c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x174) with MCTentacle.cpp debug path 0x0062e06c, line token 0x1b, and allocation/type value 0x45. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime MCTentacle cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mctentacle", "free-object")),
            new Spec("0x005d3379", "Wave755 static read-back: MCTentacle.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c0a4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x174) with MCTentacle.cpp debug path 0x0062e06c, line token 0x1b, and allocation/type value 0x49. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime MCTentacle cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("mctentacle", "free-object"))
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
            throw new IllegalStateException("Wave755 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
