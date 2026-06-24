//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyParticleTextureBundleWave612 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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
            "particle-texture-wave612",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
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
        Set<String> existing = tagNames(fn);
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
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
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
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
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType ushortType = UnsignedShortDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0054f6e0",
                "CDXEngine__ShutdownParticleSystemBundle",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("particle_bundle", voidPtr)
                },
                "Wave612 particle texture bundle hardening: callsite 0x0054f6d5 jumps here with ECX set to the engine particle bundle at 0x009c63e8. Body destroys linked particles through CParticle__Destroy, clears manager owner links through CParticleManager__ClearParticleOwnerBacklinks/PruneDeadOwnerLinks/CleanupHandles, shuts down the manager at bundle +0x0c, frees the manager storage, and returns. Static retail decompile/instruction/xref evidence only; exact bundle field layout, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "particle-bundle", "lifecycle-shutdown", "engine-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054f740",
                "CDXEngine__ResetParticleSystemBundle",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("particle_bundle", voidPtr)
                },
                "Wave612 particle texture bundle hardening: callsite 0x0054f6b5 reaches this reset helper with ECX set to the particle bundle. Body clears the bundle head/current fields at +0x00/+0x04/+0x08/+0x0c/+0x18 and returns without allocation. Static retail decompile/instruction/xref evidence only; exact bundle field names, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "particle-bundle", "lifecycle-reset", "engine-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054f760",
                "CDXEngine__SetParticleRenderStatePreset",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave612 particle texture render-state hardening: callsite 0x004c8fba invokes this no-argument helper before particle texture drawing. Body programs Direct3D render and sampler state through CDXDevice render-state wrappers, including alpha blending, cull/lighting/fog/z state, texture stage color/alpha ops, and min/mag/mip filters. Static retail decompile/instruction/xref evidence only; exact high-level render-state names, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "render-state", "cdecl-helper", "d3d-state", "callsite-verified")
            ),
            new Spec(
                "0x0054f7e0",
                "CDXEngine__RenderParticleTexturePass",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("particle_bundle", voidPtr)
                },
                "Wave612 particle texture pass hardening: CDXEngine__Render callsite 0x0053ebe3 and front-end matrix setup callsite 0x00540f55 set ECX to particle bundle 0x009c63e8. Body builds particle view/projection constants from bundle vector/matrix fields, pushes shader constants, calls DXParticleTexture__RenderAll, then restores render state and shader bindings. Static retail decompile/instruction/xref evidence only; exact bundle layout, shader constant semantics, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "particle-bundle", "render-pass", "engine-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054fbc0",
                "DXParticleTexture__GetOrCreate",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {
                    param("texture_path", charPtr),
                    param("texture_type", intType)
                },
                "Wave612 DXParticleTexture hardening: CParticleDescriptor__Load callsite 0x004c57b9 and particle descriptor callsites 0x004c0682/0x004c3185 push a texture path and type, then clean two arguments. Body scans global list DAT_009c64d0 by case-insensitive path and type, allocates a 0x1a4-byte node when absent, copies the full path and short name, resolves CTexture/CVBufTexture resources, configures vertex and index buffer formats, links the node into the global list, and returns the node pointer. Static retail decompile/instruction/xref evidence only; exact object field names, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "dxparticletexture", "global-list", "get-or-create", "cdecl-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054fd80",
                "DXParticleTexture__ReleaseAll",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave612 DXParticleTexture lifecycle hardening: device-loss/reset callsite 0x00512c1d invokes this global no-argument release pass. Body walks DAT_009c64d0, releases each texture pointer at node +0x194, releases each CVBufTexture pointer at +0x198, and releases/nulls global pixel shader DAT_009c6468. Static retail decompile/instruction/xref evidence only; exact resource ownership, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "dxparticletexture", "global-list", "resource-release", "cdecl-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054fde0",
                "DXParticleTexture__RestoreAll",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave612 DXParticleTexture lifecycle hardening: device-restore callsite 0x0051290e invokes this global no-argument restore pass. Body logs CPT::RAS start/end strings, recreates CTexture and CVBufTexture resources for each DAT_009c64d0 node, configures vertex/index buffer formats, and conditionally creates the particle vertex/pixel shaders when shader globals allow it. Static retail decompile/instruction/xref evidence only; exact shader source identity, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "dxparticletexture", "global-list", "resource-restore", "shader-restore", "cdecl-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054fee0",
                "DXParticleTexture__DestroyAll",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave612 DXParticleTexture lifecycle hardening: front-end/resource teardown callsites 0x0046923c and 0x0046c9c5 invoke this global list destructor. Body walks DAT_009c64d0, preserves the next pointer at node +0x1a0, calls DXParticleTexture__Release on each node, frees node storage through the DX memory manager, and advances until the list is empty. Static retail decompile/instruction/xref evidence only; exact global ownership, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "dxparticletexture", "global-list", "resource-destroy", "cdecl-helper", "callsite-verified")
            ),
            new Spec(
                "0x0054ff20",
                "DXParticleTexture__RenderAll",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave612 DXParticleTexture render hardening: CDXEngine__RenderParticleTexturePass callsite 0x0054f9ec and particle render path callsite 0x004c8cb3 invoke this global render walk. Body sets particle render state, binds particle shader globals DAT_009c6468/DAT_009c646c when available, calls DXParticleTexture__Render for every DAT_009c64d0 node, then restores render state and shader bindings. Static retail decompile/instruction/xref evidence only; exact shader constant semantics, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "dxparticletexture", "global-list", "render-all", "cdecl-helper", "callsite-verified")
            ),
            new Spec(
                "0x00550110",
                "DXParticleTexture__Release",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave612 DXParticleTexture method hardening: DXParticleTexture__DestroyAll callsite 0x0054fefd passes ECX as the current global-list node. Body releases the node texture pointer at +0x194 through CTexture release code, releases the CVBufTexture pointer at +0x198, clears both resource pointers, and returns. Static retail decompile/instruction/xref evidence only; exact node layout, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "dxparticletexture", "thiscall-helper", "resource-release", "callsite-verified")
            ),
            new Spec(
                "0x00550180",
                "DXParticleTexture__AddTriangleIndices",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("index0", ushortType),
                    param("index1", ushortType),
                    param("index2", ushortType)
                },
                "Wave612 DXParticleTexture index-buffer hardening: particle sprite and descriptor callsites 0x004c8bec, 0x004c8c05, 0x004ca201, 0x004ca210, 0x004caad7, and 0x004caae6 pass ECX as a DXParticleTexture node plus three triangle indices, and the callee returns with RET 0x0c. Body obtains three writable index slots from the node CVBufTexture at +0x198 and writes the three 16-bit indices. Static retail decompile/instruction/xref evidence only; exact index buffer ownership, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "dxparticletexture", "thiscall-helper", "index-buffer", "ret-000c", "callsite-verified")
            ),
            new Spec(
                "0x005501b0",
                "DXParticleTexture__GetIndexBuffer",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("index_count", intType)
                },
                "Wave612 DXParticleTexture index-buffer hardening: CPDSimpleSprite__ProcessAndRenderSpriteList callsite 0x004c782c passes ECX as a DXParticleTexture node plus an index count, then uses EAX as a writable index-buffer pointer. Body forwards to CVBufTexture__GetIndexPtr on node +0x198 and returns the buffer pointer. Static retail decompile/instruction/xref evidence only; exact index buffer ownership, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "dxparticletexture", "thiscall-helper", "index-buffer", "callsite-verified")
            ),
            new Spec(
                "0x00550220",
                "DXParticleTexture__Render",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave612 DXParticleTexture render hardening: DXParticleTexture__RenderAll callsite 0x00550082 passes ECX as each global-list node. Body early-outs when the CVBufTexture at +0x198 is absent, resolves the texture frame at +0x194, binds texture and blend state based on node type at +0x190, resets batch index +0x19c, and renders the CVBufTexture with or without validation depending on DAT_009c64d4. Static retail decompile/instruction/xref evidence only; exact blend mode semantics, runtime particle output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("particle-texture", "dxparticletexture", "thiscall-helper", "render-node", "callsite-verified")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad != 0 || stats.missing != 0) {
                throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
            }
        }
    }
}
