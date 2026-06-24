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

public class ApplyDecodeDispatchHeadWave710 extends GhidraScript {
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "decode-dispatch-head-wave710",
            "wave710-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "decode-dispatch-head"
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
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
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
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);

            stats.updated++;
            println("OK: " + spec.address + " " + expectedSignature(spec));
            Thread.sleep(75);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x0059aec0",
                "CTexture__CanUseCompactDecodePath",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("unused_ecx", intType),
                    param("decode_state", voidPtr)
                },
                "Wave710 static read-back: plain RET and the callers at 0x0059b10b/0x0059b1ec show EDX loaded with the decode state while ECX is unused by the observed body and retained as fastcall context. The gate checks state fields at +0x24/+0x28/+0x2c/+0x4c/+0x78/+0x130/+0x140 plus component descriptor fields under +0xdc before returning 1 for the compact path or 0 otherwise. Static metadata only; exact decode-state layout, component enum names, JPEG/texture semantics, runtime image fidelity, BEA patching, and rebuild parity remain unproven.",
                tags("compact-decode-gate", "fastcall-edx-state", "unused-ecx", "tranche-head")
            ),
            new Spec(
                "0x0059af40",
                "CTexture__ComputeDecodeBlockGeometry",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                "Wave710 static read-back: RET 0x4 and the caller at 0x0059b1d9 show one decode-state stack argument. The helper computes decode block dimensions at +0x70/+0x74 and scale at +0x140, derives per-component sampling values under +0xdc, stores output mode fields at +0x78/+0x7c, then calls CTexture__CanUseCompactDecodePath to choose the +0x80 row grouping. Static metadata only; exact decode-state layout, component enum names, runtime image fidelity, BEA patching, and rebuild parity remain unproven.",
                tags("block-geometry", "ret-0x4", "component-sampling")
            ),
            new Spec(
                "0x0059b370",
                "CTexture__RunDecodeDispatchStage",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                "Wave710 static read-back: RET 0x4, data installation from 0x0059b4e5, and the body show one decode-state stack argument. The helper drives the dispatch context at +0x1a8, calls observed decode-state slots under +0x1c4/+0x1b0/+0x1cc/+0x1c8/+0x1d0/+0x1b4/+0x1ac, and updates callback-context progress fields at +0xc/+0x10. Static metadata only; exact dispatch slot schema, callback ABI, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-stage", "ret-0x4", "callback-progress")
            ),
            new Spec(
                "0x0059b4d0",
                "CTexture__CreateDecodeDispatchContext",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                "Wave710 static read-back: RET 0x4 and the caller at 0x00590eaf show one decode-state stack argument. The helper allocates a 0x1c dispatch context through the allocator slot at +4, stores it at +0x1a8, installs CTexture__RunDecodeDispatchStage and LAB_0059b4a0, clears the state word, then calls CTexture__InitializeDecodePipelineFromHeader with ESI preserved. Static metadata only; exact dispatch-context layout, the downstream hidden-register initializer ABI, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-context", "ret-0x4", "allocator-context")
            ),
            new Spec(
                "0x0059b920",
                "CDXTexture__DecodeState_RunPostFrameCallbacks",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                "Wave710 static read-back: RET 0x4, a direct call from 0x0059ba0a, and data installation from 0x0059bab2 show one decode-state stack argument. The helper runs the component layout/scratch helpers, then invokes observed slots at +0x1c0 and +0x1b0 before copying the +0x1b0 callback result field into the callback context at +0x1b8. Static metadata only; exact callback context layout, helper hidden-register ABIs, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("post-frame-callbacks", "ret-0x4", "callback-context")
            ),
            new Spec(
                "0x0059b960",
                "CDXTexture__DecodeState_AdvanceFrame",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                "Wave710 static read-back: RET 0x4 plus calls/data xrefs from 0x0059ba0a/0x0059ba2b/0x0059baa5 show one decode-state stack argument and a status return. The helper reads callback context +0x1b8 and stage driver +0x1bc, returns 2 for the terminal flag, handles observed status 1 by validating a pending frame or running post-frame callbacks, and handles status 2 by marking terminal/clamping progress fields. Static metadata only; exact status enum meanings, JPEG frame semantics, callback ABI, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("advance-frame", "ret-0x4", "status-return")
            ),
            new Spec(
                "0x0059ba20",
                "CDXTexture__DecodeState_ResetCallbackContext",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                "Wave710 static read-back: RET 0x4 and data installation from 0x0059baab show one decode-state stack argument. The helper resets the callback context at +0x1b8 to CDXTexture__DecodeState_AdvanceFrame with zeroed state words and flag 1, invokes the decode-state vtable slot at +0x10 and the stage callback under +0x1bc, then clears +0xa4. Static metadata only; exact callback context layout, vtable semantics, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("reset-callback-context", "ret-0x4", "callback-context")
            ),
            new Spec(
                "0x0059ba90",
                "CDXTexture__DecodeState_CreateCallbackContext",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                "Wave710 static read-back: RET 0x4 and the caller at 0x00591038 show one decode-state stack argument. The helper allocates a 0x1c callback context through the allocator slot at +4, stores it at +0x1b8, installs CDXTexture__DecodeState_AdvanceFrame, CDXTexture__DecodeState_ResetCallbackContext, CDXTexture__DecodeState_RunPostFrameCallbacks, and LAB_0059ba70, then initializes the state words to 0/0/1. Static metadata only; exact callback context layout, lifecycle contract, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("create-callback-context", "ret-0x4", "callback-context", "tranche-tail")
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

        println("ApplyDecodeDispatchHeadWave710 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
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
            throw new IllegalStateException("Wave710 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
