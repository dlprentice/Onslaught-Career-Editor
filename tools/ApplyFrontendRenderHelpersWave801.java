//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyFrontendRenderHelpersWave801 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, boolean updateSignature,
                String callingConvention, DataType returnType, ParameterImpl[] parameters,
                String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "frontend-render-helpers-wave801",
            "wave801-readback-verified",
            "retail-binary-evidence",
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

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.updateSignature) {
            return true;
        }
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

    private String expectedSignature(Spec spec) {
        if (!spec.updateSignature) {
            return "<unchanged signature>";
        }
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.newName)
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

    private boolean allowedName(Function fn, Spec spec) {
        return fn.getName().equals(spec.newName) || fn.getName().equals(spec.oldName);
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.newName)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        String readComment = fn.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.newName);
                return;
            }
            if (!allowedName(fn, spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName()
                    + " expected=" + spec.oldName + " or " + spec.newName);
                return;
            }

            boolean renameNeeded = !fn.getName().equals(spec.newName);
            boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
            boolean commentOrTagsNeedUpdate = fn.getComment() == null
                || !fn.getComment().equals(spec.comment)
                || !hasAllTags(fn, spec.tags);

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + spec.newName);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                }
                else if (commentOrTagsNeedUpdate) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature()
                    + " expected=" + expectedSignature(spec));
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.newName, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (signatureNeedsUpdate) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
                stats.signatureUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            if (!signatureNeedsUpdate) {
                stats.commentOnlyUpdated++;
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
            Thread.sleep(75L);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.newName + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x0044a0c0",
                "CDXMeshVB__GetGlobalZeroDouble",
                "CDXMeshVB__GetGlobalZeroDouble",
                true,
                "__cdecl",
                doubleType,
                new ParameterImpl[] {},
                "Wave801 static read-back: trivial global double getter. Body returns DAT_00672fd0 as a double value and has 14 current xrefs across HUD target overlay, mesh rendering, texture animation, AYA resource/cache code, and render queue paths. Static retail Ghidra evidence only; exact global meaning, exact source identity, runtime render/timing behavior, BEA patching, and rebuild parity remain deferred.",
                tags("dxmeshvb", "global-double-getter", "signature-corrected", "tranche-head")
            ),
            new Spec(
                "0x00456780",
                "CFEPDebriefing__Initialize",
                "CFEPDebriefing__Initialize",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave801 static read-back: CFEPDebriefing initialize vtable target from DATA xref 0x005db9c0. The body allocates 0x324 bytes for 100 eight-byte list nodes using the FEPDebriefing.cpp debug path at 0x0062913c, line 0x30, runs the vector constructor iterator with GlobalListNode__ClearField4AndPushGlobalList and CParticleManager__RemoveFromGlobalList_Thunk, stores the array at this+0x20, allocates 0x640 bytes at line 0x31 into this+0x24, clears this+0x1c/+0x10/+0x18, and returns 1. Static retail Ghidra evidence only; exact layout, runtime debriefing behavior, BEA patching, and rebuild parity remain deferred.",
                tags("fepdebriefing", "frontend-init", "allocation-init", "vtable-data-xref")
            ),
            new Spec(
                "0x0045d730",
                "CFEPLevelSelect__UpdateMouseEdgeSlide",
                "CFEPLevelSelect__UpdateMouseEdgeSlide",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave801 static read-back: level-select mouse-edge slide helper called by CFEPLevelSelect__Process. It calls CFrontEnd__IsMouseInputReady(&DAT_00675688); when mouse input is not ready and state is 0, it derives a signed edge delta from cursor globals DAT_0089bda8/DAT_0089bda4, applies cubic scaling through _DAT_00679af8 * delta^3 * _DAT_005d8bbc, adds the result into *value, and clamps the value to [0,max_value]. Static retail Ghidra evidence only; exact source identity, runtime mouse/UI feel, BEA patching, and rebuild parity remain deferred.",
                tags("feplevelselect", "mouse-edge-slide", "cubic-clamp", "frontend-process-helper")
            ),
            new Spec(
                "0x00465710",
                "CDXFont__DrawTextDynamic",
                "CDXFont__DrawTextDynamic",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave801 static read-back: dynamic text wrapper with 67 current xrefs. It copies the input wide text to a stack buffer capped at 1000 characters, computes per-character ARGB/fade arrays from transition, fade_out, color, and font constants, then draws an offset alpha shadow and foreground text through CDXFont__DrawTextScaled. Static retail Ghidra evidence only; exact font layout, stack-local names, runtime visual behavior, BEA patching, and rebuild parity remain deferred.",
                tags("dxfont", "dynamic-text", "per-character-colors", "text-shadow")
            ),
            new Spec(
                "0x004659a0",
                "CDXEngine__DrawTextScaledWithShadow",
                "CDXFont__DrawTextScaledWithShadow",
                true,
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("packed_argb", uintType),
                    param("text", shortPtr),
                    param("flags", uintType),
                    param("depth_z", floatType),
                    param("x_scale", floatType),
                    param("y_scale", floatType)
                },
                "Wave801 static read-back: corrected the stale CDXEngine owner label to CDXFont because ECX is forwarded directly as the font receiver to two CDXFont__DrawTextScaled calls. Decompile/instruction evidence shows the helper draws an alpha-only shadow at x+1/y+1, then draws the original text with the same text, flags, depth_z, x_scale, and y_scale arguments; 43 current xrefs come from frontend, game, HUD, message, and menu render paths. Static retail Ghidra evidence only; exact source identity, runtime visual behavior, BEA patching, and rebuild parity remain deferred.",
                tags("dxfont", "drawtextscaled-shadow", "name-corrected", "signature-corrected", "text-shadow")
            ),
            new Spec(
                "0x00465c10",
                "CDXBitmapFont__BuildGlyphRemapTables",
                "CDXBitmapFont__BuildGlyphRemapTables",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave801 static read-back: global glyph remap table builder called by CDXBitmapFont__ctor_base. It scans charset table DAT_005db5fc, records the fallback glyph byte in DAT_00679af4 when token 0x1f is found, fills direct byte remap table DAT_006799f4 with fallback values, clears overflow table DAT_006799d4, skips duplicate chars present in DAT_005db738, maps byte-sized chars directly, and stores wide overflow entries as character/index pairs. Static retail Ghidra evidence only; exact charset semantics, runtime localization behavior, BEA patching, and rebuild parity remain deferred.",
                tags("dxbitmapfont", "glyph-remap", "charset-table", "font-init-helper")
            ),
            new Spec(
                "0x00465dd0",
                "CFEPVirtualKeyboard__IsInputAccepted",
                "CFEPVirtualKeyboard__IsInputAccepted",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave801 static read-back: CFEPVirtualKeyboard input-acceptance predicate. If this+0x15c is nonzero it returns 1 immediately; otherwise it calls the first virtual function on this with input_ctx and returns whether that result differs from the low byte of DAT_00679af4. Static retail Ghidra evidence only; exact vtable contract, input context type, runtime save-name behavior, BEA patching, and rebuild parity remain deferred.",
                tags("fepvirtualkeyboard", "input-predicate", "vtable-dispatch", "save-name-entry")
            ),
            new Spec(
                "0x00465f00",
                "CVBufTexture__GetGlobalEnableByte",
                "CVBufTexture__GetGlobalEnableByte",
                false,
                "",
                null,
                new ParameterImpl[] {},
                "Wave801 static read-back: global enable-byte getter. The body returns the low byte from DAT_00679b40 in AL while preserving upper EAX bits as a decompiler artifact; six current xrefs come from render/texture-adjacent paths. Static retail Ghidra evidence only; exact global meaning, calling-context upper-bit semantics, runtime rendering behavior, BEA patching, and rebuild parity remain deferred.",
                tags("vbuftexture", "global-enable-byte", "render-helper", "tranche-tail")
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

        println("ApplyFrontendRenderHelpersWave801 mode=" + (dryRun ? "dry" : "apply"));
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
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave801 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
