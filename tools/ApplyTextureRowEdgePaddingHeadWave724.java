//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyTextureRowEdgePaddingHeadWave724 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, boolean updateSignature, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.updateSignature = updateSignature;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] signatureTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "texture-row-edge-padding-head-wave724",
            "wave724-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "texture-row-edge-padding"
        }, extras);
    }

    private String[] commentTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "texture-row-edge-padding-head-wave724",
            "wave724-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "hidden-register-context",
            "texture-row-edge-padding"
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
        if (spec.updateSignature && !signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (spec.updateSignature && !signatureMatches(readBack, spec)) {
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

            boolean needsSignature = spec.updateSignature && !signatureMatches(fn, spec);
            boolean needsAnyUpdate = needsUpdate(fn, spec);
            String signatureText = spec.updateSignature ? expectedSignature(spec) : fn.getSignature().toString();
            if (!needsAnyUpdate) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + signatureText);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                else {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " " + signatureText);
                return;
            }
            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
            }
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            else {
                stats.commentOnlyUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + signatureText);
            Thread.sleep(75);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x005ab420",
                "CTexture__BuildComponentPlaneRowPointers",
                false,
                "__stdcall",
                voidType,
                new ParameterImpl[] {},
                "Wave724 static read-back: builds component-plane row pointer tables for the texture/decode row cache using the hidden ESI context. It allocates paired row-pointer arrays under context +0x1ac slots +0x38/+0x3c, walks the component descriptors under +0xdc using component count +0x24 and row scale +0x140, and stores base/end row pointers for each component plane. Ghidra still exposes locked hidden ESI storage, so the current void(void) signature is intentionally retained. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact texture/decode context layout, component descriptor schema, row-cache layout, allocator ABI, runtime texture/decode behavior, BEA patching, and rebuild parity remain unproven.",
                commentTags("component-plane", "row-pointer-table", "hidden-esi-context", "tranche-head")
            ),
            new Spec(
                "0x005ab4d0",
                "CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh",
                true,
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("texture_context", voidPtr) },
                "Wave724 static read-back: mirrors/copies high-side edge rows for component-plane row buffers using the ECX texture/decode context. It walks the row-cache arrays under +0x1ac slots +0x38/+0x3c, component descriptors under +0xdc, row scale +0x140, and component count +0x24, then copies/mirrors dword rows around each component plane. The existing CMeshCollisionVolume owner label is retained as current Ghidra state but static evidence here is texture row-cache/edge-padding behavior, not owner/source identity proof. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact context layout, component descriptor schema, edge-padding callback ABI, current owner/source identity, runtime texture/decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("edge-padding", "mirror-high", "fastcall-ecx-context", "current-owner-unproven")
            ),
            new Spec(
                "0x005ab620",
                "CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth",
                false,
                "__stdcall",
                voidType,
                new ParameterImpl[] {},
                "Wave724 static read-back: mirrors/copies both edge sides for component-plane row buffers using the hidden EAX texture/decode context. It uses the row-cache arrays under +0x1ac slots +0x38/+0x3c, component descriptors under +0xdc, row scale +0x140, and component count +0x24 to fill mirrored dword rows around each component plane. The existing CMeshCollisionVolume owner label is retained as current Ghidra state but static evidence here is texture row-cache/edge-padding behavior, not owner/source identity proof. Ghidra still exposes locked hidden EAX storage, so the current void(void) signature is intentionally retained. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact context layout, component descriptor schema, edge-padding callback ABI, current owner/source identity, runtime texture/decode behavior, BEA patching, and rebuild parity remain unproven.",
                commentTags("edge-padding", "mirror-both", "hidden-eax-context", "current-owner-unproven")
            ),
            new Spec(
                "0x005ab700",
                "CMeshCollisionVolume__FinalizeEdgePaddingRows",
                false,
                "__stdcall",
                voidType,
                new ParameterImpl[] {},
                "Wave724 static read-back: finalizes component-plane edge-padding rows using the hidden EAX texture/decode context. It copies/fills row-cache padding across component planes, uses the component descriptors under +0xdc and row-cache arrays under +0x1ac slots +0x38/+0x3c, and records the first-component padding height at row-cache +0x48. The existing CMeshCollisionVolume owner label is retained as current Ghidra state but static evidence here is texture row-cache/edge-padding behavior, not owner/source identity proof. Ghidra still exposes locked hidden EAX storage, so the current void(void) signature is intentionally retained. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact context layout, component descriptor schema, edge-padding callback ABI, current owner/source identity, runtime texture/decode behavior, BEA patching, and rebuild parity remain unproven.",
                commentTags("edge-padding", "finalize-padding", "hidden-eax-context", "current-owner-unproven")
            ),
            new Spec(
                "0x005ab9c0",
                "CDXTexture__InitComponentPlaneRowCache",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("texture_context", voidPtr) },
                "Wave724 static read-back: initializes the component-plane row cache for a texture/decode context. It allocates the 0x50-byte cache at context +0x1ac, installs the callback/table pointer at LAB_005ab950, optionally reports through a hidden EBX diagnostic path, conditionally builds component-plane row pointers, and allocates per-component row cache buffers from the context allocator. RET 0x4 evidence restores the single stack argument as texture_context. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact texture/decode context layout, callback table contract, component descriptor schema, row-cache layout, runtime texture/decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("row-cache", "component-plane", "allocator", "tranche-tail", "hidden-ebx-diagnostic")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        println("ApplyTextureRowEdgePaddingHeadWave724 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
