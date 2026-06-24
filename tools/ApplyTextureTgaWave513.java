//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyTextureTgaWave513 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "texture-tga-wave513",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.newName).append("(");
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }

        String currentName = fn.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + currentName + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }

        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName + " :: " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.newName)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }

        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType boolType = BooleanDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004f27f0",
                "CTexture__FindTexture",
                "CTexture__FindTexture",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {
                    param("name", charPtr),
                    param("texture_type", intType),
                    param("load_arg", intType),
                    param("required_mip_count", intType),
                    param("allow_fallback", intType),
                    param("load_flags", intType)
                },
                "Wave513 signature/comment hardening: global CTexture cache lookup/load helper. The cdecl body walks DAT_0083d9b0 by case-insensitive name, texture_type or wildcard 0, and required_mip_count or -1; on miss it allocates a 0x158-byte CTexture from texture.cpp line 0x98, calls the constructor, forwards name/type/load_arg/required_mip_count/load_flags to vtable slot +0x14, and returns the default texture DAT_0083d9b4 when loading fails and allow_fallback is set. Static retail evidence only; exact CTexture layout beyond observed fields, forwarded loader argument semantics, runtime rendering behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("texture", "cache", "fallback", "asset-loading")
            ),
            new Spec(
                "0x004f29c0",
                "CTexture__InitDefaultTextureResourcesAndStatus",
                "CTexture__InitDefaultTextureResourcesAndStatus",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave513 signature/comment hardening: default texture bootstrap/status helper. The no-argument body lazily resolves meshtex/default.tga into DAT_0083d9b4 through CTexture__FindTexture, then emits Loading texture resources status/done messages on the global console. Static retail evidence only; exact texture resource lifecycle, runtime rendering behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("texture", "default-texture", "resource-bootstrap", "console-status")
            ),
            new Spec(
                "0x004f2a30",
                "CTexture__ClearOut",
                "CTexture__ClearOut",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave513 signature/comment hardening: texture shutdown clear-out helper. The no-argument body drops the default texture reference DAT_0083d9b4, releases zero-ref entries from the global DAT_0083d9b0 texture list, logs any remaining leaked textures by name/refcount, then zeroes refcounts and releases the remaining list. Static retail evidence only; exact CTexture layout beyond observed fields, runtime shutdown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("texture", "resource-lifecycle", "leak-report", "shutdown")
            ),
            new Spec(
                "0x004f2b40",
                "CTexture__FreeLevelResources",
                "CTexture__FreeLevelResources",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave513 signature/comment hardening: end-of-level texture resource free helper. The no-argument body clears texture debug flag DAT_0083d9b8, drops DAT_0083d9b4, releases zero-ref entries from DAT_0083d9b0, and logs any end-of-level texture leaks by name/refcount. Static retail evidence only; exact CTexture layout beyond observed fields, runtime level-unload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("texture", "resource-lifecycle", "level-unload", "leak-report")
            ),
            new Spec(
                "0x004f2c60",
                "CTGALoader__CTGALoader",
                "CTGALoader__CTGALoader",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("filename", charPtr),
                    param("status_out", voidPtr)
                },
                "Wave513 signature/comment hardening: CTGALoader constructor. RET 0x8 proves filename and status_out stack arguments after ECX; the body calls CImageLoader__Constructor with filename, installs vtable 0x005df518, stores status_out at this+0x118 for later Load status writes, and returns this. Static retail evidence only; exact CTGALoader layout, status_out semantics, runtime image loading, BEA launch, patching, and rebuild parity remain unproven.",
                tags("tgaloader", "constructor", "vtable", "imageloader")
            ),
            new Spec(
                "0x004f2c90",
                "CTGALoader__scalar_deleting_destructor",
                "CTGALoader__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave513 stale-destructor/signature correction: CTGALoader scalar-deleting destructor wrapper. RET 0x4 proves one flags argument; the body calls CTGALoader__Destructor, frees this through CDXMemoryManager__Free when flags&1 is set, and returns this. Static retail evidence only; exact CTGALoader layout, runtime lifetime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("tgaloader", "destructor", "scalar-deleting", "stale-name-corrected")
            ),
            new Spec(
                "0x004f2cb0",
                "CTGALoader__destructor",
                "CTGALoader__Destructor",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave513 stale-destructor/signature correction: CTGALoader destructor body. The ECX-only body restores the CTGALoader vtable pointer 0x005df518 before chaining into CImageLoader__Destructor. Static retail evidence only; exact CTGALoader layout, runtime lifetime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("tgaloader", "destructor", "imageloader", "stale-name-corrected")
            ),
            new Spec(
                "0x004f2ce0",
                "CTGALoader__Load",
                "CTGALoader__Load",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave513 signature/comment hardening: CTGALoader TGA decode body. The ECX-only body reads the inherited filename, initializes a CDXMemBuffer, parses an 18-byte TGA header, accepts image types 2 and 10 with 24-bit or 32-bit pixels, supports raw and RLE packet data, fills the inherited RGB buffer, and for 32-bit images splits alpha into the inherited +0x14 buffer while honoring the orientation flag. Static retail evidence only; exact CTGALoader/CImageLoader layout beyond observed fields, complete malformed-file behavior, runtime image loading, BEA launch, patching, and rebuild parity remain unproven.",
                tags("tgaloader", "tga", "image-loader", "rle", "alpha")
            ),
            new Spec(
                "0x004f3110",
                "ImageIO__WriteTGA24",
                "ImageIO__WriteTGA24",
                "__cdecl",
                boolType,
                new ParameterImpl[] {
                    param("path", charPtr),
                    param("pixels32", voidPtr),
                    param("width", intType),
                    param("height", intType),
                    param("pitch_bytes", intType)
                },
                "Wave513 signature/comment hardening: 24-bit TGA writer used by screenshot and texture-dump paths. The cdecl body writes an uncompressed 18-byte TGA header for width/height, walks the 32-bit source buffer bottom-up using pitch_bytes, emits three bytes per pixel, closes the file, and returns success. Source ltshell.cpp calls the analogous Save24BitWithPitch(path, pixels, width, height, pitch). Static retail evidence only; exact source body identity, runtime screenshot behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("tgaloader", "image-io", "screenshot", "tga-writer")
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
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave513 texture/TGA apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
