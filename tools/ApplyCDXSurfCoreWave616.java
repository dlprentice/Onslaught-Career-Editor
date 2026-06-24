//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCDXSurfCoreWave616 extends GhidraScript {
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
            "cdxsurf-wave616",
            "retail-binary-evidence",
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
        DataType floatType = FloatDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType shortType = ShortDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005563d0",
                "CDXSurf__RenderSurface",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("draw_x", floatType),
                    param("draw_y", floatType),
                    param("draw_z", floatType),
                    param("texture_or_resource", voidPtr),
                    param("draw_width", floatType),
                    param("draw_height", floatType),
                    param("draw_depth", floatType),
                    param("color_a", intType),
                    param("color_b", intType),
                    param("scale_x", floatType),
                    param("scale_y", floatType)
                },
                "Wave616 CDXSurf core hardening: heavily used cdecl frontend/HUD/game sprite wrapper with xrefs from CConsole__RenderLoadingScreen, CFrontEnd draw helpers, CGame__DrawGameStuff, CGameInterface__Render, CFEPMain__Render, and level/multiplayer frontend render paths. Body forwards to CVBufTexture__DrawSpriteEx with default UV bounds 0.0/1.0/0.0/1.0. Static retail decompile/xref evidence only; exact argument semantics, UI/runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "render-surface", "sprite-wrapper", "cdecl-helper", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x00556460",
                "CDXSurf__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave616 CDXSurf core hardening: ECX-only initializer clears the CDXSurf surface-strip array pointer at +0x00, wave texture pointer at +0x08, secondary field at +0x04, and initialized flag at +0x0c. Static retail decompile/instruction evidence only; exact CDXSurf layout, runtime water behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "init", "zero-fields", "signature-corrected")
            ),
            new Spec(
                "0x00556470",
                "CDXSurf__LoadWavesTexture",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave616 CDXSurf core hardening: CDXLandscape__Reset callsite 0x005453ac reaches this ECX-only helper. Body resolves mixers\\waves.tga through CTexture__FindTexture with type/flag arguments 5,0,-1,1,1 and stores the texture pointer at this+0x8. Static retail decompile/xref evidence only; exact texture ownership, runtime water rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "waves-texture", "texture-resource", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x00556490",
                "CDXSurf__CreateSurfaceArray",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("chunk_reader", voidPtr)
                },
                "Wave616 CDXSurf core hardening: CResourceAccumulator__ReadResourceFile callsite 0x004d77f7 passes a CDXSurf object plus a chunk reader. Body gates on a reader count above 7, reads the strip count, allocates count*0x0c+4 bytes from DXSurf.cpp line 0x38, vector-constructs 0x0c-byte strip entries with CDXSurf__DestroyBuffers as cleanup, reads each strip vertex count at entry+0x8, calls CDXSurf__CreateSurfaceStrip, then marks this+0x0c initialized. Static retail decompile/xref evidence only; exact serialized wave format, runtime water rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "surface-array", "chunk-reader", "debug-path-006525a0", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x005565b0",
                "CDXSurf__DestroyBuffers",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("surface_strip", voidPtr) },
                "Wave616 CDXSurf core hardening: vector cleanup callback used by CDXSurf__CreateSurfaceArray and CDXSurf__Destroy for each 0x0c-byte strip entry. Body calls vtable slot 0 with delete flag 1 for the two CVBuffer pointers at strip+0x00 and strip+0x04 when present. Static retail decompile/xref evidence only; exact strip layout, runtime water rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "surface-strip", "buffer-destroy", "callback", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x005565d0",
                "CDXSurf__CreateSurfaceStrip",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("chunk_reader", voidPtr)
                },
                "Wave616 CDXSurf core hardening: CDXSurf__CreateSurfaceArray callsite 0x0055655f passes each strip entry and the chunk reader. Body allocates two 0x2c-byte CVBuffer objects from DXSurf.cpp lines 0xa8 and 0xab, creates vertex buffers with count*2+2 vertices and shader 0x242, reads strip positions from the chunk reader, fills sine-offset wave vertices, handles DAT_0082b4a4 UV ordering, writes colors 0x00ffffff/0xc0ffffff/0xff000000, and unlocks both buffers. Static retail decompile/xref evidence only; exact vertex layout, runtime water rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "surface-strip", "cvbuffer", "wave-geometry", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x005569e0",
                "CDXSurf__Destroy",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave616 CDXSurf core hardening: CDXLandscape__Shutdown callsite 0x00544f8b passes the CDXSurf object. Body clears initialized flag this+0x0c, destroys the strip array through CDXLandscape__DestroyArrayWithCallback using CDXSurf__DestroyBuffers, frees the count header, clears the array pointer, releases the wave texture reference at this+0x8 through CHud__DecrementCounter9C, and returns. Static retail decompile/xref evidence only; exact resource ownership, runtime water teardown, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "destroy", "surface-array", "texture-release", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x00556a30",
                "CDXSurf__Render",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("validated_mode", byteType)
                },
                "Wave616 CDXSurf core hardening: CWaterRenderSystem__RenderMainPass callsites 0x0055bf37 and 0x0055d520 pass a CDXSurf object plus a render/validation mode byte. Body validates the shared water render state when requested, sets projection depth bias index 4, resolves the animated waves texture frame, binds render state, iterates strip entries, sets each CVBuffer stream source, draws D3D triangle strips through device vtable +0x144, marks accepted in validated mode, and resets depth bias to 0. Static retail decompile/xref evidence only; exact water-pass semantics, runtime water rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "render", "water-pass", "triangle-strip", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x00556d70",
                "CDXSurf__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                },
                "Wave616 CDXSurf core hardening: CDXSurf vtable 0x005e59a0 slot 0 points here. Body calls CDXSurf__dtor, then frees the object through CDXMemoryManager__Free when delete_flags bit 0 is set, and returns this. Static retail decompile/vtable evidence only; exact allocator ownership, runtime water teardown, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "scalar-deleting-dtor", "vtable-005e59a0", "signature-corrected", "vtable-verified")
            ),
            new Spec(
                "0x00556d90",
                "CDXSurf__dtor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave616 CDXSurf core hardening: reached from CDXSurf__ScalarDeletingDestructor at 0x00556d73 and a destructor thunk at 0x0053a140. Body installs CDXSurf vtable 0x005e59a0, unlinks from render-object lists, optionally reports nonzero texture refcounts with Texture: %s refcount %d, clears texture entries, runs base/device cleanup, and unlinks the node from the global list. Static retail decompile/xref evidence only; decompile still shows an unaff_ESI artifact, exact base-class layout, runtime teardown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "destructor", "texture-refcount", "global-list-unlink", "callsite-verified")
            ),
            new Spec(
                "0x00556f80",
                "CDXSurf__DestroyRenderTarget",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave616 CDXSurf core hardening: CFEPGoodies__FreeUpGoodyResources callsite 0x0045cd7e passes the CDXSurf-like render-target owner. Body releases the resource pointer at this+0x140 through CDXEngine__DecrementResourceRefCount, destructs the CVBufTexture when still present, frees it through CDXMemoryManager__Free, clears this+0x140, and returns. Static retail decompile/xref evidence only; exact owner layout, Goodies/render-target runtime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "render-target", "cvbuftexture", "resource-release", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x00556fc0",
                "CDXSurf__SetupSurface",
                "__thiscall",
                boolType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("setup_value", intType),
                    param("format_word", shortType),
                    param("size_x", intType),
                    param("size_y", intType),
                    param("setup_flags", byteType),
                    param("extra_config", intType)
                },
                "Wave616 CDXSurf core hardening: CDXSurf vtable 0x005e59a0 slot +0x18 and CDXBattleLine__Constructor computed-call sites reach this RET 0x18 setup helper. Body copies the default surface name from 0x00662b2c into this+0x8, stores setup fields at offsets +0xac/+0xb0/+0x13c/+0x144/+0x148/+0x14c/+0x150, increments this+0xa4, invokes vtable slot +0x04, and returns true when the result is nonnegative. Static retail decompile/vtable/xref evidence only; exact field semantics, the unbounded vtable pointers at 0x00556e90/0x00558600, runtime render-target behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxsurf", "setup-surface", "ret-0018", "vtable-slot-18", "signature-corrected", "vtable-verified")
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
