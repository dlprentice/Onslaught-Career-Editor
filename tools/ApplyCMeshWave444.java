//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCMeshWave444 extends GhidraScript {
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
        return toAddr(addressText);
    }

    private Function functionAtEntry(Address address) {
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
            "cmesh-wave444",
            "retail-binary-evidence"
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
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

            Function readBack = functionAtEntry(address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
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

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(intType);
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004aa3f0",
                "CMeshPart__CopyPrimaryAxesToOutVec3Triplet",
                "__thiscall",
                voidType,
                "Wave444 signature/comment hardening: copies the primary CMeshPart axis/position dwords at offsets +0x00, +0x10, and +0x20 into an output three-dword/vector record. RET 0x4 confirms one stack argument after this; callers include CMesh__Load, CMeshPart__ApplyRootTransformRecursive, and CSoundManager__UpdateSoundPosition. Static retail decompile/xref/instruction evidence only; exact vector type, transform semantics, runtime asset behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmeshpart", "transform", "vector-copy", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_vec3", voidPtr)
                }
            ),
            new Spec(
                "0x004aa410",
                "CMesh__FindTextureByNameSuffixHint",
                "__cdecl",
                voidPtr,
                "Wave444 signature/comment hardening: texture lookup helper for mesh texture records; validates the name at record+0x08, warns on null texture names, checks two-character suffix/prefix hints, and dispatches to CTexture__FindTexture with mode 4, mode 2, or default mode 1. Static retail decompile/xref/instruction evidence only; exact texture-record layout, mode enum names, runtime texture-cache behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "texture-lookup", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("texture_record", voidPtr)
                }
            ),
            new Spec(
                "0x004aa5a0",
                "CMesh__GetPartField40ByFlatIndex",
                "__thiscall",
                intType,
                "Wave444 signature/comment hardening: chained mesh part-table helper; subtracts each mesh node's part count at +0x1c while following the +0x08 chain, then returns field +0x40 from the selected 0x150-byte part record or 0 when the chain ends. RET 0x4 confirms one stack argument after this. Static retail decompile/xref/instruction evidence only; exact record layout, field +0x40 meaning, runtime callers, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "part-lookup", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flat_part_index", intType)
                }
            ),
            new Spec(
                "0x004aa5e0",
                "CMesh__FindEntryByInclusiveRangeTable",
                "__thiscall",
                intType,
                "Wave444 signature/comment hardening: chained mesh range-table lookup; scans count +0x0c 12-byte records at +0x10 and returns the record value when lookup_value falls inside the inclusive start/end range stored at record+0x04/+0x08, otherwise follows the +0x08 chain and returns 0 on exhaustion. RET 0x4 confirms one stack argument after this. Static retail decompile/xref/instruction evidence only; exact table owner, field names, runtime caller semantics, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "range-table", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("lookup_value", intType)
                }
            ),
            new Spec(
                "0x004aa630",
                "CMesh__FindAnimationIndexByName",
                "__thiscall",
                intType,
                "Wave444 name/signature/comment hardening: animation/state table lookup; scans count +0x14 0x24-byte records at +0x18, compares the record name against animation_name with stricmp, and returns record+0x10 or -1. RET 0x4 and broad animation callsites confirm one stack string argument after this. Static retail decompile/xref/instruction evidence only; exact animation table layout, enum semantics, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {"FindAnimationIndex"},
                tags("cmesh", "animation-lookup", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("animation_name", charPtr)
                }
            ),
            new Spec(
                "0x004aa680",
                "CMesh__FindEntryByPartId",
                "__thiscall",
                voidPtr,
                "Wave444 owner/name/signature/comment hardening: generic mesh 0x24-byte entry lookup, not CMCMech-specific; scans count +0x14 records at +0x18 and returns the first record whose +0x10 part/id field equals part_id, otherwise 0. RET 0x4 confirms one stack argument after this; callers include CMCMech, CMCBuggy, and cutscene prep paths. Static retail decompile/xref/instruction evidence only; exact table owner, id enum, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CMCMech__FindSlotByPartId"},
                tags("cmesh", "part-lookup", "owner-corrected", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("part_id", intType)
                }
            ),
            new Spec(
                "0x004aa6e0",
                "CMesh__FindOrCreate",
                "__cdecl",
                voidPtr,
                "Wave444 signature/comment hardening: global mesh cache find-or-create helper; scans DAT_00704ad8/g_pMeshList by mesh_name at +0x24, increments refcount +0x170 on hit, otherwise allocates a 0x174-byte CMesh, initializes it, loads by name with load_context, and tears down/frees the object on load failure. Static retail decompile/xref/instruction evidence only; exact load_context layout, cache lifetime, runtime IO behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "cache", "load-wrapper", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("mesh_name", charPtr),
                    param("load_context", voidPtr)
                }
            ),
            new Spec(
                "0x004aa7e0",
                "CMesh__FindEntryValueByTypeId",
                "__thiscall",
                floatType,
                "Wave444 signature/comment hardening: scans count +0x14 0x24-byte records at +0x18 for type_id at record+0x10, writes the matching record index to out_index, and returns the float at record+0x20; on miss writes -1 to out_index and returns the default float at 0x005d856c. RET 0x8 confirms two stack arguments after this. Static retail decompile/xref/instruction evidence only; exact record layout, float meaning, runtime caller semantics, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "entry-lookup", "float-return", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("type_id", intType),
                    param("out_index", intPtr)
                }
            ),
            new Spec(
                "0x004aa820",
                "CMesh__FindPartField40ByNameAndOwner",
                "__thiscall",
                intType,
                "Wave444 owner/name/signature/comment hardening: chained mesh part lookup, not CMCMech-specific; scans each mesh node's 0x150-byte part records for a case-insensitive name match at record+0x4c and owner/pointer match at record+0x14c, returning field +0x40 or 0 after following the +0x08 chain. RET 0x8 confirms two stack arguments after this. Static retail decompile/xref/instruction evidence only; exact part record layout, owner field meaning, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CMCMech__FindSlotValueByNameAndOwner"},
                tags("cmesh", "part-lookup", "owner-corrected", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("part_name", charPtr),
                    param("owner_part", voidPtr)
                }
            ),
            new Spec(
                "0x004aa900",
                "CMesh__CreatePolyBucketsForAllParts",
                "__thiscall",
                voidType,
                "Wave444 signature/comment hardening: iterates the CMesh part pointer table at +0x160 for count +0x15c and calls CMeshPart__CreatePolyBucket for each part when the table exists. ECX receiver and RET without stack cleanup indicate thiscall with no stack arguments. Static retail decompile/xref/instruction evidence only; exact part-table layout, polybucket ownership, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "polybucket", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004aa940",
                "CMesh__GetRandomVertexWeightedByPartArea",
                "__thiscall",
                voidPtr,
                "Wave444 signature/comment hardening: chooses a static mesh part and returns out_vec3 after CMesh__GetRandomVertexFromPolyBucket; for large part counts it builds up to 150 candidate parts weighted by material area field +0x24, normalizes weights, samples with Random__NextLCGAbs, and falls back to the first candidate after 100 tries, while small meshes try up to 15 random static parts. RET 0x8 confirms out_vec3 and out_part stack arguments after this. Static retail decompile/xref/instruction evidence only; exact weighting semantics, output pointer types, runtime geometry behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "random-vertex", "polybucket", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_vec3", voidPtr),
                    param("out_part", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0 would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new RuntimeException("ApplyCMeshWave444 failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
