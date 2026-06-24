//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplyRenderValidationTailWave570 extends GhidraScript {
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
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

    private Function getFunctionOrReport(Spec spec, Stats stats) {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
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
            "render-validation-tail-wave570",
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
            Function fn = getFunctionOrReport(spec, stats);
            if (fn == null) {
                stats.skipped++;
                return;
            }

            String currentName = fn.getName();
            if (!allowedName(spec, currentName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
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

            Function readBack = functionAtEntry(addr(spec.address));
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
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00527cc0",
                "CWaterRenderSystem__ValidateVBufferAndMarkReady",
                "__thiscall",
                boolType,
                "Wave570 signature/comment hardening: shared render validation record helper. RET 0x4 confirms one expected_valid_so_far stack argument after this; the body compares it with this+0x0c, returns false on mismatch, logs `RM: First time attempt at %s %d` through the name/key at this+0x08 when this+0x10 is still clear, then returns true. Xrefs span CDXBattleLine, CDXLandscape, CMeshRenderer, CWaterRenderSystem, and CDXSurf render paths, so the current CWaterRenderSystem owner label is retained only as the saved entry name. Static retail evidence only; exact record class/layout, source identity, runtime D3D behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CWaterRenderSystem__ValidateVBufferAndMarkReady"},
                tags("render-validation", "vbuf-valid", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("expected_valid_so_far", intType)
                }
            ),
            new Spec(
                "0x00527d20",
                "CDXLandscape__ValidateDeviceAndUpdateValidSoFar",
                "__thiscall",
                boolType,
                "Wave570 signature/comment hardening: ECX-only render validation record/device helper. Plain RET at 0x00527d63/0x00527d98 confirms no stack arguments; when this+0x10 is clear the body calls CEngine__DeviceCall118_WithZeroOut(&DAT_00855bb0). A failure with zero this+0x0c logs `RM: Failed ValidSoFar on %s %d...` and still returns true; a failure with nonzero this+0x0c logs, decrements this+0x0c, and returns false. Xrefs span battle-line, landscape, mesh, surf, and water render paths, so the current CDXLandscape owner label is retained only as the saved entry name. Static retail evidence only; exact record class/layout, source identity, runtime D3D behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__ValidateDeviceAndUpdateValidSoFar"},
                tags("render-validation", "device-call", "valid-so-far", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00527da0",
                "CVBufTexture__MarkAccepted",
                "__thiscall",
                voidType,
                "Wave570 signature/comment hardening: ECX-only render validation record accept helper. Plain RET at 0x00527dcc confirms no stack arguments; if this+0x10 is clear the body logs `RM: Accepting %s %d` from this+0x08/this+0x0c, then sets this+0x10 to 1. Xrefs span battle-line, landscape, mesh, surf, and water render paths, so the current CVBufTexture owner label is retained only as the saved entry name. Static retail evidence only; exact record class/layout, source identity, runtime D3D behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CVBufTexture__MarkAccepted"},
                tags("render-validation", "acceptance-state", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00527dd0",
                "CDXEngine__GetRenderQueueSortKeyAt0C",
                "__thiscall",
                intType,
                "Wave570 signature/comment hardening: ECX-only getter for render queue / validation record field this+0x0c. The body is MOV EAX,[ECX+0xc]; RET, and xrefs from CDXLandscape__RenderTerrain, CRenderQueue__RenderAll, CDXEngine__RenderMultipassLayerA, and CWaterRenderSystem__RenderMainPass use the value as a sort/key reader. Static retail evidence only; exact record class/layout, source identity, runtime render-order behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__GetRenderQueueSortKeyAt0C"},
                tags("render-validation", "field-reader", "render-queue", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00527e00",
                "CWaterRenderSystem__CheckVBufValidAndHandleFailure",
                "__thiscall",
                boolType,
                "Wave570 signature/comment hardening: ECX-only render validation failure helper. If this+0x10 is already set it returns true; otherwise it checks global byte DAT_00854dd8. When that byte is set, it logs `RM: Failed CheckVBufValid on %s %d`, accepts a zero this+0x0c case by setting this+0x10 to 1 and returning true, or decrements this+0x0c, clears this+0x10, and returns false; when DAT_00854dd8 is clear it returns true. Static retail evidence only; exact record class/layout, source identity, runtime D3D behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CWaterRenderSystem__CheckVBufValidAndHandleFailure"},
                tags("render-validation", "failure-gate", "vbuf-valid", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave570 render-validation tranche failed");
        }
    }
}
