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

public class ApplyUnwindContinuationWave751 extends GhidraScript {
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
            "unwind-continuation-wave751",
            "wave751-readback-verified",
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
            new Spec("0x005d2730", "Wave751 static read-back: FrontEnd.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b5a4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x24) with FrontEnd.cpp debug path 0x00629df0, line 0x27, and allocation/type value 0xb3. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime frontend cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "free-object")),
            new Spec("0x005d2760", "Wave751 static read-back: compiler-generated SEH unwind cleanup callback in the FrontEnd/game-adjacent scope-table run. Scope-table DATA xref 0x0061b5cc points at this body; decompile/instruction evidence shows it calls CDXLandscape__DestroyResourceDescriptorArray_Thunk on the stack-local descriptor array at EBP-0x434. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime landscape descriptor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("frontend", "game", "landscape", "resource-descriptor-array", "destructor")),
            new Spec("0x005d2780", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b5f4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x18) with game.cpp debug path 0x0062bba4, line 0x26, and allocation/type value 0x108. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d2799", "Wave751 static read-back: compiler-generated SEH unwind cleanup callback in the game.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b5fc points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the camera pointer at *(EBP-0x18). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "camera", "destructor")),
            new Spec("0x005d27a1", "Wave751 static read-back: compiler-generated SEH unwind cleanup callback in the game.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b604 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the active-reader pointer at *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "active-reader", "destructor")),
            new Spec("0x005d27a9", "Wave751 static read-back: monitor.h compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b60c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with monitor.h debug path 0x0062551c, line 0x5e, and allocation/type value 0x18. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor allocation cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "free-object")),
            new Spec("0x005d27d0", "Wave751 static read-back: compiler-generated SEH unwind cleanup callback in the game.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b634 points at this body; decompile/instruction evidence shows it calls CGenericCamera__dtor on the camera pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime camera cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "camera", "destructor")),
            new Spec("0x005d27f0", "Wave751 static read-back: compiler-generated SEH unwind cleanup callback in the game.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b65c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk with the object pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "monitor", "shutdown", "thunk")),
            new Spec("0x005d27f8", "Wave751 static read-back: compiler-generated SEH unwind cleanup callback in the game.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b664 points at this body; decompile/instruction evidence shows it calls CGenericActiveReader__dtor on the embedded active reader at (*(EBP-0x10))+0x9f8. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "active-reader", "destructor")),
            new Spec("0x005d2810", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b68c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with game.cpp debug path 0x0062bba4, line 0x2b, and allocation/type value 0x1f9. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d2829", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b694 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with game.cpp debug path 0x0062bba4, line 0x2b, and allocation/type value 0x1fa. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d2842", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b69c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with game.cpp debug path 0x0062bba4, line 0x29, and allocation/type value 0x1fb. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d285b", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b6a4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with game.cpp debug path 0x0062bba4, line 0x2a, and allocation/type value 0x1fc. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d2874", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b6ac points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with game.cpp debug path 0x0062bba4, line 0x2a, and allocation/type value 0x1fd. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d288d", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b6b4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with game.cpp debug path 0x0062bba4, line 0x78, and allocation/type value 0x1ff. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d28a6", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b6bc points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with game.cpp debug path 0x0062bba4, line 0x2a, and allocation/type value 0x200. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d28bf", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b6c4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x10) with game.cpp debug path 0x0062bba4, line 0x80, and allocation/type value 0x201. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d28f0", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b6ec points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with game.cpp debug path 0x0062bba4, line 0x28, and allocation/type value 0x353. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d2909", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b6f4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP+0x4) with game.cpp debug path 0x0062bba4, line 0x27, and allocation/type value 0x366. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d2930", "Wave751 static read-back: compiler-generated SEH unwind cleanup callback in the game.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b71c points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk with the stack-local monitor object at EBP-0x114. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "monitor", "shutdown", "thunk")),
            new Spec("0x005d2950", "Wave751 static read-back: compiler-generated SEH unwind cleanup callback in the game.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b744 points at this body; decompile/instruction evidence shows it calls CDXLandscape__ReleaseSurfaces on the stack-local landscape/surface context at EBP-0x44. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime landscape surface cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "landscape", "release-surfaces")),
            new Spec("0x005d2970", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b76c points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x20) with game.cpp debug path 0x0062bba4, line 0x26, and allocation/type value 0xb49. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d29a0", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b794 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x80) with game.cpp debug path 0x0062bba4, line 0x26, and allocation/type value 0xe2f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object")),
            new Spec("0x005d29d0", "Wave751 static read-back: compiler-generated SEH unwind cleanup callback in the game.cpp-adjacent scope-table run. Scope-table DATA xref 0x0061b7bc points at this body; decompile/instruction evidence shows it calls CMonitor__Shutdown_Thunk with the stack-local monitor object at EBP-0x18. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime monitor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "monitor", "shutdown", "thunk")),
            new Spec("0x005d29d8", "Wave751 static read-back: game.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061b7c4 points at this body; instruction evidence shows it calls OID__FreeObject_Callback on the pointer at *(EBP-0x1c) with game.cpp debug path 0x0062bba4, line 0x27, and allocation/type value 0x11be. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("game", "free-object"))
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
            throw new IllegalStateException("Wave751 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
