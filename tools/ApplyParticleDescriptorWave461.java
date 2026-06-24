//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
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

public class ApplyParticleDescriptorWave461 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "particle-descriptor-wave461",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] names(String... values) {
        return values;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            if (!actualSignature.equals(expectedSignature(spec))) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature(spec));
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(250);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004c07f0",
                "CPDSimpleSprite__WriteTokenFields",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDSimpleSprite vtable slot 7 writes token fields through CTokenArchive__Write* for observed descriptor offsets, including tokens 6 through 0x1b. Static token serialization metadata only; runtime particle rendering behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDSimpleSprite__VFunc_07_004c07f0", "CPDSimpleSprite__WriteTokenFields"),
                tags("simple-sprite", "token-writer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c1970",
                "CPDEmitter__WriteTokenFields",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDEmitter vtable slot 7 writes token fields 0x1a through 0x28 through CTokenArchive__Write*. Static token serialization metadata only; runtime particle behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDEmitter__VFunc_07_004c1970", "CPDEmitter__WriteTokenFields"),
                tags("emitter", "token-writer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c2220",
                "CPDSelector__WriteTokenFields",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDSelector vtable slot 7 writes pointer/int token fields 0x29 through 0x30 through CTokenArchive__Write*. Static token serialization metadata only; runtime selector behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDSelector__VFunc_07_004c2220", "CPDSelector__WriteTokenFields"),
                tags("selector", "token-writer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c2400",
                "CPDColourRange__WriteTokenFields",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDColourRange vtable slot 7 writes float/int token fields 0x31 through 0x3c through CTokenArchive__Write*. Static token serialization metadata only; runtime colour behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDColourRange__VFunc_07_004c2400", "CPDColourRange__WriteTokenFields"),
                tags("colour-range", "token-writer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c2ca0",
                "CPDShape__WriteTokenFields",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDShape vtable slot 7 writes int/float token fields 0x3f through 0x46 plus token 6 through CTokenArchive__Write*. Static token serialization metadata only; runtime shape behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDShape__VFunc_07_004c2ca0", "CPDShape__WriteTokenFields"),
                tags("shape", "token-writer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c3440",
                "CPDTrail__WriteTokenFields",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDTrail vtable slot 7 writes trail token fields, including tokens 0x47 through 0x54, through CTokenArchive__Write*. Static token serialization metadata only; runtime trail behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDTrail__VFunc_07_004c3440", "CPDTrail__WriteTokenFields"),
                tags("trail", "token-writer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c4920",
                "CPDFunction__WriteTokenFields",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDFunction vtable slot 7 writes token fields 0x5c through 0x64 through CTokenArchive__Write*. Static token serialization metadata only; runtime function-curve behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDFunction__VFunc_07_004c4920", "CPDFunction__WriteTokenFields"),
                tags("function", "token-writer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c49b0",
                "CPDMesh__dtor_base",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDMesh destructor-base body. Sets the CPDMesh vtable during cleanup, releases the +0x5c resource pointer by decrementing its +0x170 refcount, clears +0x5c, then restores the observed base vtable. Runtime mesh cleanup behavior, exact resource layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDMesh__ctor_like_004c49b0", "CPDMesh__dtor_base"),
                tags("mesh", "dtor-base", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c4ae0",
                "CPDMesh__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave461 correction: CPDMesh vtable slot 0 scalar-deleting destructor wrapper. Calls CPDMesh__dtor_base, checks flags & 1, optionally frees this through CDXMemoryManager__Free, and returns this. Runtime mesh cleanup behavior, exact layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDMesh__VFunc_00_004c4ae0", "CPDMesh__scalar_deleting_dtor"),
                tags("mesh", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("flags", byteType) }
            ),
            new Spec(
                "0x004c4c70",
                "CPDMesh__WriteTokenFields",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDMesh vtable slot 7 writes mesh token fields, including tokens 0x65 through 0x68, through CTokenArchive__Write*. Static token serialization metadata only; runtime mesh rendering behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDMesh__VFunc_07_004c4c70", "CPDMesh__WriteTokenFields"),
                tags("mesh", "token-writer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c53b0",
                "CPDFoR__WriteTokenFields",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDFoR vtable slot 7 writes pointer token fields 0x69, 0x6a, and 0x28 through CTokenArchive__WritePointer. Static token serialization metadata only; runtime frame-of-reference behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDFoR__VFunc_07_004c53b0", "CPDFoR__WriteTokenFields"),
                tags("for", "token-writer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            ),
            new Spec(
                "0x004c5410",
                "CParticleDescriptor__Update",
                "__thiscall",
                intType,
                "Wave461 correction: CParticleDescriptor update vtable entry. Uses this plus one particle argument, copies parent visibility/transform state, creates effect/list state through CParticleManager__CreateEffect, and can allocate a fallback particle through CParticleManager__AllocateParticle. Runtime particle behavior, exact descriptor/particle layout, exact source identity, and rebuild parity remain unproven.",
                names("CParticleDescriptor__Update"),
                tags("particle-descriptor", "update", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("particle", voidPtr) }
            ),
            new Spec(
                "0x004c5730",
                "CParticleDescriptor__Load",
                "__thiscall",
                intType,
                "Wave461 correction: CParticleDescriptor load vtable entry. Uses this plus one token_archive argument, allocates a 1000-byte temp token buffer, loops CTokenArchive__ReadNextToken, handles texture/indexed-parameter/reference-fixup tokens, frees the temp buffer on terminator token 5, and returns 1. Runtime load behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CParticleDescriptor__Load"),
                tags("particle-descriptor", "load", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("token_archive", voidPtr) }
            ),
            new Spec(
                "0x004c59e0",
                "CPDPMesh__WriteTokenFields",
                "__fastcall",
                voidType,
                "Wave461 correction: CPDPMesh vtable slot 7 writes particle-mesh token fields, including tokens 0x6b through 0x7b, through CTokenArchive__Write*. Static token serialization metadata only; runtime particle-mesh behavior, exact descriptor layout, exact source identity, and rebuild parity remain unproven.",
                names("CPDPMesh__VFunc_07_004c59e0", "CPDPMesh__WriteTokenFields"),
                tags("pmesh", "token-writer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
