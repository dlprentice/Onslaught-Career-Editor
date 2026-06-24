//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyUnwindContinuationWave764 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

        Spec(String address, String comment, String[] tags) {
            this(address, "Unwind@" + address.substring(2), comment, tags);
        }

        Spec(String address, String name, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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
            "unwind-continuation-wave764",
            "wave764-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "compiler-unwind",
            "scope-table"
        };
        String[] out = new String[common.length + extras.length];
        System.arraycopy(common, 0, out, 0, common.length);
        System.arraycopy(extras, 0, out, common.length, extras.length);
        return out;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private String expectedSignature(Spec spec) {
        return "void __cdecl " + spec.name + "(void)";
    }

    private void verifyReadBack(Spec spec) {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        String signature = fn.getSignature().toString();
        if (!signature.equals(expectedSignature(spec))) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + signature);
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> actualTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actualTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
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

            String signature = fn.getSignature().toString();
            boolean signatureNeedsUpdate = !signature.equals(expectedSignature(spec));
            boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(spec.comment);
            Set<String> actualTags = tagNames(fn);
            boolean tagsNeedUpdate = false;
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    tagsNeedUpdate = true;
                    break;
                }
            }

            if (!signatureNeedsUpdate && !commentNeedsUpdate && !tagsNeedUpdate) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name + " signature=" + signature + " -> " + expectedSignature(spec));
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
            new Spec("0x005d46c8", "Wave764 static read-back: Player.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061cf4c points at this body; instruction/decompile evidence shows CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "active-reader")),
            new Spec("0x005d46d3", "Wave764 static read-back: Player.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061cf54 points at this body; instruction/decompile evidence shows CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x24. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "active-reader")),
            new Spec("0x005d46f0", "Wave764 static read-back: Player.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061cf7c points at this body; instruction/decompile evidence shows CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "monitor", "shutdown")),
            new Spec("0x005d46f8", "Wave764 static read-back: Player.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061cf84 points at this body; instruction/decompile evidence shows CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x10))+0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "active-reader")),
            new Spec("0x005d4710", "Wave764 static read-back: Player.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061cfac points at this body; instruction/decompile evidence shows CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "monitor", "shutdown")),
            new Spec("0x005d4730", "Wave764 static read-back: Player.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cfd4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x14) with Player.cpp debug path 0x00631690, line token 0x3a, and allocation/type value 0x26. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "free-object")),
            new Spec("0x005d4746", "Wave764 static read-back: Player.cpp-adjacent compiler-generated SEH unwind camera cleanup callback. Scope-table DATA xref 0x0061cfdc points at this body; instruction/decompile evidence shows CGenericCamera__dtor on the camera pointer at *(EBP-0x14). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "camera", "destructor")),
            new Spec("0x005d474e", "Wave764 static read-back: Player.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061cfe4 points at this body; instruction/decompile evidence shows CGenericActiveReader__dtor on the active-reader pointer at *(EBP-0x18). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "active-reader")),
            new Spec("0x005d4756", "Wave764 static read-back: monitor.h compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cfec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with monitor.h debug path 0x0062551c, line token 0x18, and allocation/type value 0x5e. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("monitor", "free-object")),
            new Spec("0x005d4780", "Wave764 static read-back: Player.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d014 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with Player.cpp debug path 0x00631690, line token 0x43, and allocation/type value 0x26. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "free-object")),
            new Spec("0x005d47a0", "Wave764 static read-back: Player.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d03c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x40) with Player.cpp debug path 0x00631690, line token 0xa0, and allocation/type value 0x28. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "free-object")),
            new Spec("0x005d47b9", "Wave764 static read-back: Player.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d044 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x40) with Player.cpp debug path 0x00631690, line token 0xbc, and allocation/type value 0x28. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "free-object")),
            new Spec("0x005d47d2", "Wave764 static read-back: Player.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d04c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x40) with Player.cpp debug path 0x00631690, line token 0xbe, and allocation/type value 0x26. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("player", "free-object")),
            new Spec("0x005d4800", "Wave764 static read-back: PolyBucket.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d074 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on the stack pointer at EBP-0xec with PolyBucket.cpp debug path 0x006316bc, line token 0x14c, and allocation/type value 0x46. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("polybucket", "free-object")),
            new Spec("0x005d481c", "Wave764 static read-back: array.h compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d07c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on the stack pointer at EBP-0xe4 with array.h debug path 0x0062d590, line token 0x12, and allocation/type value 0x54. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("array", "free-object")),
            new Spec("0x005d4840", "Wave764 static read-back: PolyBucket.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d0a4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x18) with PolyBucket.cpp debug path 0x006316bc, line token 0x499, and allocation/type value 0x46. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("polybucket", "free-object")),
            new Spec("0x005d4859", "Wave764 static read-back: PolyBucket.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d0ac points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x18) with PolyBucket.cpp debug path 0x006316bc, line token 0x4da, and allocation/type value 0x46. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("polybucket", "free-object")),
            new Spec("0x005d4880", "Wave764 static read-back: RadarWarningReceiver.cpp-adjacent compiler-generated SEH unwind monitor shutdown callback. Scope-table DATA xref 0x0061d0d4 points at this body; instruction/decompile evidence shows CMonitor__Shutdown_Thunk on the monitor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("radar-warning-receiver", "monitor", "shutdown")),
            new Spec("0x005d4888", "Wave764 static read-back: RadarWarningReceiver.cpp-adjacent compiler-generated SEH unwind pointer-set cleanup callback. Scope-table DATA xref 0x0061d0dc points at this body; instruction/decompile evidence shows CSPtrSet__Clear on the embedded pointer set at (*(EBP-0x10))+0x1c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("radar-warning-receiver", "pointer-set")),
            new Spec("0x005d48a0", "Wave764 static read-back: RadarWarningReceiver.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d104 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x44) with RadarWarningReceiver.cpp debug path 0x00631784, line token 0x41, and allocation/type value 0x49. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("radar-warning-receiver", "free-object")),
            new Spec("0x005d48b6", "Wave764 static read-back: RadarWarningReceiver.cpp-adjacent compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061d10c points at this body; instruction/decompile evidence shows CGenericActiveReader__dtor on the active-reader subobject at (*(EBP-0x44))+0x0c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("radar-warning-receiver", "active-reader")),
            new Spec("0x005d48d0", "Wave764 static read-back: ResourceAccumulator.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061d134 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on the stack pointer at EBP-0x5cc with ResourceAccumulator.cpp debug path 0x00631b7c, line token 0x330, and allocation/type value 0x80. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("resource-accumulator", "free-object")),
            new Spec("0x005d4900", "Wave764 static read-back: ResourceAccumulator.cpp-adjacent compiler-generated SEH unwind resource-descriptor array cleanup callback. Scope-table DATA xref 0x0061d15c points at this body; instruction/decompile evidence shows CDXLandscape__DestroyResourceDescriptorArray_Thunk on the stack-local descriptor array at EBP-0x434. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("resource-accumulator", "resource-descriptor", "destructor")),
            new Spec("0x005d4920", "Wave764 static read-back: compiler-generated SEH unwind actor destructor-base cleanup callback. Scope-table DATA xref 0x0061d184 points at this body; instruction/decompile evidence shows CActor__dtor_base on the actor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("actor", "destructor")),
            new Spec("0x005d4940", "Wave764 static read-back: compiler-generated SEH unwind actor destructor-base cleanup callback. Scope-table DATA xref 0x0061d1ac points at this body; instruction/decompile evidence shows CActor__dtor_base on the actor pointer at *(EBP-0x10). Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("actor", "destructor"))
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
            throw new IllegalStateException("Wave764 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
