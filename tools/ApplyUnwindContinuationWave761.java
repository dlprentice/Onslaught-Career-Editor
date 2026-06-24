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

public class ApplyUnwindContinuationWave761 extends GhidraScript {
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
            "unwind-continuation-wave761",
            "wave761-readback-verified",
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
            new Spec("0x005d3f4b", "Wave761 static read-back: compiler-generated SEH unwind complex-thing destructor-base callback. Scope-table DATA xref 0x0061cab4 points at this body; instruction/decompile evidence loads ECX from *(EBP+0x4) and jumps to CComplexThing__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("complex-thing", "destructor")),
            new Spec("0x005d3f53", "Wave761 static read-back: oids.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cabc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with oids.cpp debug path 0x00630c20, line token 0x05, and allocation/type value 0x48. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("oids", "free-object")),
            new Spec("0x005d3f69", "Wave761 static read-back: compiler-generated SEH unwind actor destructor-base callback. Scope-table DATA xref 0x0061cac4 points at this body; instruction/decompile evidence loads ECX from *(EBP+0x4) and jumps to CActor__dtor_base at 0x004013d0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime actor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("actor", "destructor")),
            new Spec("0x005d3f80", "Wave761 static read-back: compiler-generated SEH unwind actor destructor-base callback. Scope-table DATA xref 0x0061caec points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CActor__dtor_base at 0x004013d0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime actor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("actor", "destructor")),
            new Spec("0x005d3fa0", "Wave761 static read-back: compiler-generated SEH unwind thing destructor-base callback. Scope-table DATA xref 0x0061cb14 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CThing__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime thing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("thing", "destructor")),
            new Spec("0x005d3fc0", "Wave761 static read-back: compiler-generated SEH unwind complex-thing destructor-base callback. Scope-table DATA xref 0x0061cb3c points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CComplexThing__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime complex-thing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("complex-thing", "destructor")),
            new Spec("0x005d3fe0", "Wave761 static read-back: compiler-generated SEH unwind complex-thing destructor-base callback. Scope-table DATA xref 0x0061cb64 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CComplexThing__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime complex-thing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("complex-thing", "destructor")),
            new Spec("0x005d3fe8", "Wave761 static read-back: compiler-generated SEH unwind particle-list cleanup callback. Scope-table DATA xref 0x0061cb6c points at this body; instruction/decompile evidence jumps to CParticleManager__RemoveFromGlobalList_Thunk on object field (*(EBP-0x10))+0x7c. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle/list cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-list")),
            new Spec("0x005d4000", "Wave761 static read-back: compiler-generated SEH unwind complex-thing destructor-base callback. Scope-table DATA xref 0x0061cb94 points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CComplexThing__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime complex-thing cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("complex-thing", "destructor")),
            new Spec("0x005d4020", "Wave761 static read-back: compiler-generated SEH unwind actor destructor-base callback. Scope-table DATA xref 0x0061cbbc points at this body; instruction/decompile evidence loads ECX from *(EBP-0x10) and jumps to CActor__dtor_base at 0x004013d0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime actor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("actor", "destructor")),
            new Spec("0x005d4040", "Wave761 static read-back: ParticleDescriptor.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cbe4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0xa4) with ParticleDescriptor.cpp debug path 0x00630cd8, line token 0x10, and allocation/type value 0x7e9. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle descriptor cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-descriptor", "free-object")),
            new Spec("0x005d4070", "Wave761 static read-back: ParticleManager.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cc0c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP-0x10) with ParticleManager.cpp debug path 0x00630e60, line token 0x10, and allocation/type value 0x1a6. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle manager cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-manager", "free-object")),
            new Spec("0x005d40a0", "Wave761 static read-back: ParticleManager.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cc34 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x4) with ParticleManager.cpp debug path 0x00630e60, line token 0x10, and allocation/type value 0x2c0. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle manager cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-manager", "free-object")),
            new Spec("0x005d40d0", "Wave761 static read-back: ParticleManager.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cc5c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0x8) with ParticleManager.cpp debug path 0x00630e60, line token 0x10, and allocation/type value 0x2e2. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle manager cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-manager", "free-object")),
            new Spec("0x005d4100", "Wave761 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cc84 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x5f. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d4116", "Wave761 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cc8c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x60. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d412c", "Wave761 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cc94 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x61. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d4142", "Wave761 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cc9c points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x62. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d4158", "Wave761 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cca4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x63. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d416e", "Wave761 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ccac points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x64. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d4184", "Wave761 static read-back: compiler-generated SEH unwind particle-set destructor-base callback. Scope-table DATA xref 0x0061ccb4 points at this body; instruction/decompile evidence loads ECX from *(EBP+0xc) and jumps to CParticleSet__dtor_base. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "destructor")),
            new Spec("0x005d418c", "Wave761 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ccbc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x65. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d41a2", "Wave761 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ccc4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x66. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d41b8", "Wave761 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061cccc points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x67. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object")),
            new Spec("0x005d41ce", "Wave761 static read-back: ParticleSet.cpp compiler-generated SEH unwind allocation-cleanup callback. Scope-table DATA xref 0x0061ccd4 points at this body; instruction/decompile evidence shows OID__FreeObject_Callback on *(EBP+0xc) with ParticleSet.cpp debug path 0x00630fb0, line token 0x10, and allocation/type value 0x68. Static retail Ghidra metadata/decompile/xref evidence only; exact parent source-body identity, runtime particle-set cleanup behavior, BEA patching, and rebuild parity remain unproven.", tags("particle-set", "free-object"))
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
            throw new IllegalStateException("Wave761 unwind continuation failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
