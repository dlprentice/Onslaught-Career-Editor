//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCDXTextureMappedGdiWave677 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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
        int signatureUpdated = 0;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] baseTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cdxtexture-mapped-gdi-wave677",
            "wave677-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened"
        }, extras);
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
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
                return;
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
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        }
        catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private ParameterImpl[] onePointer(String name, DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param(name, voidPtr)
        };
    }

    private ParameterImpl[] openParams(DataType voidPtr, DataType intType) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("path_or_wide_path", voidPtr),
            param("path_is_wide", intType),
            param("unused_context", intType)
        };
    }

    private Spec spec(String address, String name, String callingConvention, DataType returnType,
            ParameterImpl[] params, String comment, String... tags) {
        return new Spec(address, name, callingConvention, returnType, params, comment, baseTags(tags));
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            spec(
                "0x0058864a",
                "CDXTexture__InitMappedFileContext",
                "__fastcall",
                voidType,
                onePointer("mapped_file_context", voidPtr),
                "Wave677 static read-back: initializes the mapped-file context handles to INVALID_HANDLE_VALUE and clears the mapped view pointer plus byte count. Static metadata only; exact context layout and runtime decode/export behavior remain unproven.",
                "cdxtexture", "mapped-file-context", "context-init", "file-backed-texture-io"
            ),
            spec(
                "0x0058865c",
                "CDXTexture__OpenMappedFileReadOnly",
                "__thiscall",
                intType,
                openParams(voidPtr, intType),
                "Wave677 static read-back: opens a path read-only through CreateFileA/W, creates a read-only mapping, records file size, and maps a view when the file is non-empty. Static metadata only; exact path encoding policy, context layout, and runtime decode behavior remain unproven.",
                "cdxtexture", "mapped-file-context", "file-open-readonly", "map-view-of-file", "path-encoding-branch"
            ),
            spec(
                "0x0058877d",
                "CDXTexture__OpenOutputFileHandle",
                "__thiscall",
                intType,
                openParams(voidPtr, intType),
                "Wave677 static read-back: opens a path for write output through CreateFileA/W after the same observed path-encoding branch and stores the resulting handle in the context. Static metadata only; exact path encoding policy, output mode contract, and runtime export behavior remain unproven.",
                "cdxtexture", "mapped-file-context", "file-open-output", "texture-export", "path-encoding-branch"
            ),
            spec(
                "0x00588855",
                "CDXTexture__CloseMappedFileContext",
                "__fastcall",
                intType,
                onePointer("mapped_file_context", voidPtr),
                "Wave677 static read-back: unmaps the mapped view when present, clears the size field, closes mapping and file handles when valid, restores INVALID_HANDLE_VALUE sentinels, and returns zero. Static metadata only; exact context layout and runtime ownership contract remain unproven.",
                "cdxtexture", "mapped-file-context", "close-handles", "unmap-view-of-file", "cleanup-helper"
            ),
            spec(
                "0x00588896",
                "CDXTexture__CloseHandleIfValid",
                "__fastcall",
                voidType,
                onePointer("mapped_file_context", voidPtr),
                "Wave677 static read-back: checks the first handle sentinel and delegates to CDXTexture__CloseMappedFileContext when the mapped-file context is open. Static metadata only; exact caller ownership contract remains unproven.",
                "cdxtexture", "mapped-file-context", "close-if-valid", "cleanup-helper"
            ),
            spec(
                "0x005888a1",
                "CDXTexture__ZeroGdiBitmapRecord",
                "__fastcall",
                voidType,
                onePointer("gdi_bitmap_record", voidPtr),
                "Wave677 static read-back: clears three dwords in a small GDI bitmap-style record used by texture preprocessor include context setup. Static metadata only; exact record layout and runtime GDI ownership remain unproven.",
                "cdxtexture", "gdi-record", "bitmap-record-init", "preprocessor-context"
            ),
            spec(
                "0x005888ae",
                "CDXTexture__DeleteGdiObjectIfSet",
                "__fastcall",
                voidType,
                onePointer("gdi_object_slot", voidPtr),
                "Wave677 static read-back: deletes the GDI object stored in the first slot when non-null. Static metadata only; exact record layout, object type, and runtime GDI ownership remain unproven.",
                "cdxtexture", "gdi-record", "delete-object-if-set", "cleanup-helper"
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave677 apply encountered missing/bad rows");
        }
    }
}
