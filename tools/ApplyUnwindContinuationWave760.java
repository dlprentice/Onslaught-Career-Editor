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

public class ApplyUnwindContinuationWave760 extends GhidraScript {
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
            "unwind-continuation-wave760",
            "wave760-readback-verified",
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
            new Spec("0x005d3d94", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c9ec points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x2e. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3daa", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c9f4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x32. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3dc0", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061c9fc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x33. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3dd6", "Wave760 static read-back: compiler-generated SEH unwind actor destructor-base callback. Scope-table DATA xref 0x0061ca04 points at this body; instruction/decompile evidence loads ECX from *(EBP+0x4) and jumps to CActor__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime actor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("actor", "destructor")),
            new Spec("0x005d3dde", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca0c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x34. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3df4", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca14 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x35. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3e0a", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca1c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x36. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3e20", "Wave760 static read-back: compiler-generated SEH unwind complex-thing destructor-base callback. Scope-table DATA xref 0x0061ca24 points at this body; instruction/decompile evidence loads ECX from *(EBP+0x4) and jumps to CComplexThing__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime complex-thing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("complex-thing", "destructor")),
            new Spec("0x005d3e28", "Wave760 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061ca2c points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on object field (*(EBP+0x4))+0x7c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d3e33", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca34 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x38. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3e49", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca3c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x3b. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3e5f", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca44 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x3c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3e75", "Wave760 static read-back: compiler-generated SEH unwind complex-thing destructor-base callback. Scope-table DATA xref 0x0061ca4c points at this body; instruction/decompile evidence loads ECX from *(EBP+0x4) and jumps to CComplexThing__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime complex-thing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("complex-thing", "destructor")),
            new Spec("0x005d3e7d", "Wave760 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061ca54 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on object field (*(EBP+0x4))+0x854. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d3e8b", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca5c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x3d. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3ea1", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca64 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x3f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3eb7", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca6c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x40. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3ecd", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca74 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x44. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3ee3", "Wave760 static read-back: compiler-generated SEH unwind complex-thing destructor-base callback. Scope-table DATA xref 0x0061ca7c points at this body; instruction/decompile evidence loads ECX from *(EBP+0x4) and jumps to CComplexThing__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime complex-thing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("complex-thing", "destructor")),
            new Spec("0x005d3eeb", "Wave760 static read-back: compiler-generated SEH unwind particle-list cleanup callback. Scope-table DATA xref 0x0061ca84 points at this body; instruction/decompile evidence jumps to CParticleManager__RemoveFromGlobalList_Thunk on object field (*(EBP+0x4))+0x7c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle/list cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-list")),
            new Spec("0x005d3ef6", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca8c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x45. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3f0c", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ca94 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x46. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3f22", "Wave760 static read-back: compiler-generated SEH unwind complex-thing destructor-base callback. Scope-table DATA xref 0x0061ca9c points at this body; instruction/decompile evidence loads ECX from *(EBP+0x4) and jumps to CComplexThing__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime complex-thing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("complex-thing", "destructor")),
            new Spec("0x005d3f2a", "Wave760 static read-back: compiler-generated SEH unwind active-reader cleanup callback. Scope-table DATA xref 0x0061caa4 points at this body; instruction/decompile evidence jumps to CGenericActiveReader__dtor on object field (*(EBP+0x4))+0x7c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime active-reader cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("active-reader")),
            new Spec("0x005d3f35", "Wave760 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061caac points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x47. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object"))
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
            throw new IllegalStateException("Wave760 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
