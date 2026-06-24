//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyParticleTokenLandscapeWave420 extends GhidraScript {
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
            "particle-token-landscape-wave420",
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
            Thread.sleep(50);
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0048ddd0",
                "CDXMemBuffer__OpenReadMode11",
                "__thiscall",
                intType,
                "Wave420 owner/signature correction: ECX is the CDXMemBuffer receiver and the single stack argument is the filename. The helper calls CDXMemBuffer__InitFromFile(filename, 0x11, 1, 0) and returns that status; the only observed caller in this tranche is CParticleSet__LoadParticleSetFile. Static binary evidence only; runtime particle archive loading remains unproven.",
                new String[] {"CParticleSet__OpenRead"},
                tags("dx-mem-buffer", "particle-file-context", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("filename", charPtr)}),
            new Spec(
                "0x0048de00",
                "CTokenArchive__ReadLine",
                "__stdcall",
                voidType,
                "Wave420 signature/comment hardening: reads a line into the caller-provided buffer with max_len via DXMemBuffer__ReadLine, then strips one trailing LF byte when present. CTokenArchive__ReadNextToken passes the 0x0083e288 scratch line buffer with max length 999 before token scanning. Static binary evidence only; archive parser runtime coverage remains unproven.",
                new String[] {},
                tags("token-archive", "line-reader", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("line_buffer", charPtr), param("max_len", intType)}),
            new Spec(
                "0x0048de30",
                "CDXEngine__FormatCubeTextureFilename",
                "__cdecl",
                voidType,
                "Wave420 signature/comment hardening: formats one Kempy cube texture path into out_path using the cube_%02d_%s.tga format string, masks cube_index to one byte, and selects one of five suffix strings by suffix_index. CDXEngine__InitKempyCubeTexturesAndVertexBuffer calls this in a five-iteration loop. Static binary evidence only; texture load/runtime render behavior remains unproven.",
                new String[] {},
                tags("dx-engine", "kempy-cube", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("out_path", charPtr), param("cube_index", intType), param("suffix_index", intType)}),
            new Spec(
                "0x0048de90",
                "CDXLandscape__ClearPendingHudMarkerHandle",
                "__thiscall",
                voidPtr,
                "Wave420 signature/comment hardening: constructor passes the CDXLandscape +0x8 marker-owner subobject in ECX; the helper clears global pending marker handle 0x0067a7d0 and returns the same subobject pointer. Static binary evidence only; HUD marker lifetime behavior remains unproven.",
                new String[] {},
                tags("dx-landscape", "hud-marker", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048df20",
                "CLandscapeIB__CreateIndexBuffer",
                "__thiscall",
                voidType,
                "Wave420 signature/comment hardening: ECX is the CLandscapeIB receiver. The cached path copies index data from DAT_009c64e4/e8/ec using fields +0x24/+0x28 and creates a D3D index buffer at +0x8; the generated path builds grid triangles from +0x2c, applies edge-stitch flags from +0x28, emits strip batches through CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer, stores index count at +0x30, and frees temporary index storage. Static binary evidence only; landscape render behavior remains unproven.",
                new String[] {},
                tags("landscape-ib", "index-buffer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)})
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                break;
            }
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
