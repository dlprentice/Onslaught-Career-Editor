//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.CharDataType;
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

public class ApplyMapTexWave427 extends GhidraScript {
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

    private Function functionAtEntry(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Function fn = getFunctionAt(toAddr(addressText));
        if (fn == null) {
            fn = getFunctionContaining(toAddr(addressText));
            if (fn != null && !fn.getEntryPoint().equals(toAddr(addressText))) {
                fn = null;
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
            "maptex-wave427",
            "terrain-texture",
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
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: missing function at " + spec.address + " for " + spec.name);
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
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00491180",
                "CMapTex__Reset",
                "__fastcall",
                voidType,
                "Wave427 signature/comment correction: RET with no stack cleanup confirms a this-only reset/lifecycle helper. The body writes -1 to +0x0c, frees owned pointers at +0x00/+0x08 through OID__FreeObject, and clears each slot after the free. Static retail evidence only; maptex.cpp is absent from the current Stuart snapshot, and concrete layout, runtime terrain texture behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("reset", "lifecycle", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004911c0",
                "CMapTex__LoadTexture",
                "__thiscall",
                intType,
                "Wave427 signature/comment correction: RET 0xc confirms texture_path, texture_width, and texture_index stack arguments. The body constructs a CTGALoader for texture_path, copies RGB-like texels into the texture buffer, derives the fourth height/alpha channel when alpha is present, and tracks per-texture min/max values at +0x1c/+0x34. Static retail evidence only; maptex.cpp is absent from the current Stuart snapshot, and concrete layout, runtime terrain texture behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("tga-loader", "height-channel", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("texture_path", charPtr),
                    param("texture_width", intType),
                    param("texture_index", intType)
                }
            ),
            new Spec(
                "0x00491340",
                "CMapTex__DownsampleTexture",
                "__thiscall",
                voidType,
                "Wave427 signature/comment correction: RET 0x8 confirms dest_buffer and src_buffer stack arguments. The body uses the CMapTex width at +0x18 to downsample 2x2 source texels into dest_buffer, with separate signed averaging for the fourth channel. Static retail evidence only; maptex.cpp is absent from the current Stuart snapshot, and concrete layout, runtime terrain texture behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("downsample", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("dest_buffer", voidPtr),
                    param("src_buffer", voidPtr)
                }
            ),
            new Spec(
                "0x004914b0",
                "CMapTex__LoadMixerTextureSet",
                "__thiscall",
                intType,
                "Wave427 signature/comment correction: RET 0xc confirms set_id, texture_count, and texture_width stack arguments. The body caches the set id, sizes texture storage as texture_width * texture_width * 4 * texture_count, formats the mixer TGA path for each slot, and calls CMapTex__LoadTexture. Static retail evidence only; maptex.cpp is absent from the current Stuart snapshot, and concrete layout, runtime terrain texture behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("mixer-texture-set", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("set_id", intType),
                    param("texture_count", intType),
                    param("texture_width", intType)
                }
            ),
            new Spec(
                "0x004915d0",
                "CMapTex__CopyFromOther",
                "__thiscall",
                voidType,
                "Wave427 signature/comment correction: RET 0x4 confirms a single source_map_tex stack argument. The body refreshes this CMapTex when the source set differs, copies set/count/min/max metadata, halves the width for the destination LOD, allocates a new buffer, and calls CMapTex__DownsampleTexture for each source texture slice. Static retail evidence only; maptex.cpp is absent from the current Stuart snapshot, and concrete layout, runtime terrain texture behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("copied-mixer-lod", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_map_tex", voidPtr)
                }
            ),
            new Spec(
                "0x004916c0",
                "CMapTex__Deserialize",
                "__thiscall",
                voidType,
                "Wave427 signature/comment correction: RET 0x8 confirms chunk_reader and texture_index stack arguments; texture_index is callsite/RET-proven but not consumed in current decompile. The body reads the 0x4c-byte CMapTex header from chunk_reader, conditionally allocates count << 0xc primary data and count << 10 secondary data, then reads each payload. Static retail evidence only; maptex.cpp is absent from the current Stuart snapshot, and concrete layout, runtime terrain texture behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("chunk-deserialize", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("chunk_reader", voidPtr),
                    param("texture_index", intType)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
