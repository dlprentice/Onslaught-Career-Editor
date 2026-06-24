//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCMeshWave445 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;
        final boolean updateSignature;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters,
                boolean updateSignature) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
            this.updateSignature = updateSignature;
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
        if (!spec.updateSignature) {
            return "<comment-tags-only; signature deferred>";
        }
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
            "cmesh-wave445",
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
            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
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
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004aab90",
                "CMesh__Deserialize",
                "__cdecl",
                voidPtr,
                "Wave445 signature/comment hardening: deserializes a CMesh from chunk-reader streams, allocating a 0x174-byte CMesh, preserving the prior material pointer/ref field, reading mesh metadata/materials/emitters/parts, recursively loading chained meshes, and optionally opening data\\resources\\meshes\\m_%s.aya when the global mesh archive flag is clear. RET without stack cleanup confirms cdecl two-argument shape. Static retail decompile/xref/instruction evidence only; exact CChunkReader layout, serialized field names, runtime asset behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "deserialize", "aya-resource", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("primary_reader", voidPtr),
                    param("resource_reader", voidPtr)
                },
                true
            ),
            new Spec(
                "0x004ab330",
                "CMesh__FindByRuntimeId",
                "__cdecl",
                voidPtr,
                "Wave445 signature/comment hardening: scans DAT_00704ad8/g_pMeshList until a mesh entry whose field +0x154 matches runtime_id is found, returning that CMesh pointer or 0. RET without stack cleanup confirms cdecl one-argument shape. Static retail decompile/xref/instruction evidence only; exact runtime id semantics, mesh-list ownership, caller expectations, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "global-list", "runtime-id", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("runtime_id", intType)
                },
                true
            ),
            new Spec(
                "0x004ab360",
                "CMesh__OptimizeParts",
                "__thiscall",
                voidType,
                "Wave445 signature/comment hardening: mesh-part optimization pass; adds the current part count to DAT_00704af0, attempts to merge compatible static parts while excluding Nexus/protected dependencies, transforms child geometry into parent space during removal, rewrites part/material child lists, decrements the part count, and increments DAT_00704af4 for removed parts. Static retail decompile/xref/instruction evidence only; exact CMesh/CMeshPart layouts, source-body identity, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "optimize-parts", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                true
            ),
            new Spec(
                "0x004ac0e0",
                "CMeshCollisionVolume__dtor_base",
                "__thiscall",
                voidType,
                "Wave445 owner/name/signature/comment hardening: CMeshCollisionVolume destructor body called by the saved scalar-deleting wrapper at 0x00426300; installs the CMeshCollisionVolume vtable during cleanup, frees the per-part collision data at +0x24 when present, clears that pointer, then restores the base vtable. Static retail decompile/xref/instruction evidence only; exact helper subtype layout, destructor chain semantics, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {"CMeshCollisionVolume__scalar_deleting_dtor_004ac0e0"},
                tags("mesh-collision-volume", "destructor", "owner-corrected", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                true
            ),
            new Spec(
                "0x004acde0",
                "CMeshCollisionVolume__InitContactOutputRecord",
                null,
                null,
                "Wave445 comment/tag hardening only: shared MeshCollisionVolume contact-output tail block reached from local collision-test control flow, not a clean source-level callable boundary. The block uses EBX as the output record, copies stack float/vector fields into record +0x10/+0x14/+0x18/+0x1c, clears the first vector fields, copies stack +0x20 into record +0x0c, sets record +0x20 to 1, restores saved registers, and returns with RET 0x10. Signature intentionally deferred because EBX/register state is part of the observed calling convention. Static retail instruction/decompile evidence only; exact contact-record layout, caller boundary, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("mesh-collision-volume", "contact-output", "signature-deferred", "comment-hardened"),
                new ParameterImpl[] {},
                false
            ),
            new Spec(
                "0x004ad600",
                "CMeshCollisionVolume__SetPartBounds",
                "__thiscall",
                voidType,
                "Wave445 signature/comment hardening: lazily allocates a per-part collision-data array at this+0x24 sized mesh->+0x15c * 0x74 with allocation tag 0x6c, initializes each entry status to -1.0f, validates the selected mesh part pointer from mesh->+0x160[part_index], computes either standard mesh-part pose bounds or interpolated mech pose bounds depending on this+0x1c, writes two 4x3 matrices plus a vec4 bounds record, and stores bounds_status at entry +0x70. RET 0x0c confirms three stack arguments after this. Static retail decompile/xref/instruction evidence only; exact matrix/vector types, mode flag meaning, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("mesh-collision-volume", "part-bounds", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh", voidPtr),
                    param("part_index", intType),
                    param("bounds_status", floatType)
                },
                true
            ),
            new Spec(
                "0x004adf90",
                "CMesh__ReleaseEmbeddedResources",
                "__thiscall",
                voidType,
                "Wave445 signature/comment hardening: releases a 0x24-byte mesh material/texture resource record; when record+0x08 count is nonzero it frees the buffer at +0x0c and clears +0x10/+0x14/+0x18/+0x1c/+0x08, then decrements the HUD/resource counter for the pointer at +0x00 and the CDXEngine resource refcount for the pointer at +0x04. Static retail decompile/xref/instruction evidence only; exact record layout, counter ownership, runtime texture/resource behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "resource-release", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                true
            ),
            new Spec(
                "0x004ae080",
                "CMesh__InitSingleVertexPartDefaults",
                "__thiscall",
                voidType,
                "Wave445 signature/comment hardening: initializes a single-vertex mesh material/part record, zeroes the first field, calls CMeshPart__SetVertexCount(1), writes default position/UV-like float values of 1.0f through the allocated vertex arrays, sets record +0x20 to 1.0f, and clears record +0x04. Static retail decompile/xref/instruction evidence only; exact record layout, vertex buffer ownership, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "single-vertex-defaults", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                true
            ),
            new Spec(
                "0x004ae0d0",
                "CMesh__InitPartVBufTextureFormats",
                "__thiscall",
                voidType,
                "Wave445 signature/comment hardening: initializes the VBuf texture resources for a mesh material/part record by resolving CVBufTexture__GetOrCreate(record+0x00, 0), storing it at record+0x04, then applying the observed VB format 0x152/8/0x24/4/1 and IB format 0x65/8/2/1. Static retail decompile/xref/instruction evidence only; exact format enum names, record layout, GPU/resource behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "vbuf-texture", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                true
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
            throw new RuntimeException("ApplyCMeshWave445 failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
