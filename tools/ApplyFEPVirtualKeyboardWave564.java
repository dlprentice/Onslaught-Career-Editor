//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyFEPVirtualKeyboardWave564 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "fep-virtual-keyboard-wave564",
            "retail-binary-evidence",
            "retail-only",
            "no-source-file",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
        if (fn.getParameterCount() != spec.params.length) {
            return false;
        }
        for (int i = 0; i < spec.params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.params[i];
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
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean updateNeeded = needsUpdate(fn, spec);
            if (dryRun) {
                if (updateNeeded) {
                    println("DRY: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
                } else {
                    println("SKIP: " + spec.address + " " + spec.name + " already matches");
                }
                stats.skipped++;
                return;
            }

            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + spec.name + " already matches");
                verifyReadBack(spec);
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("UPDATED: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = voidPtr();

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00520530",
                "CFEPVirtualKeyboard__InitKeyboardLayout",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave564 signature/comment hardening: retail-binary-first because FEPVirtualKeyboard.cpp is absent from references/Onslaught. The Init caller passes only this in ECX and the helper returns with plain RET; the body resets keyboard page/row/column fields around this+0x6e4..0x6f4, clears edit/cursor state fields, and fills virtual-keyboard key records for numeric, letter, punctuation, accented, and control-token pages. Static retail evidence only; exact class layout, frontend runtime behavior, BEA launch, and rebuild parity remain unproven.",
                tags("fep-virtual-keyboard", "keyboard-layout", "frontend-input")
            ),
            new Spec(
                "0x00520cc0",
                "CFEPVirtualKeyboard__HandleKeyToken",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("key_token", intType) },
                "Wave564 signature/comment hardening: RET 0x4 plus the ButtonPressed select callsite prove a single key_token stack argument. Control tokens 1..9 move the cursor, delete or clear the edit buffer, toggle input mode flags at this+0x4c/0x50, switch keyboard page set at this+0x6e4, or commit by copying the wide edit buffer to DAT_008a1388 and sending the frontend to page 0xb. Glyph tokens insert into the wide edit buffer at this+0x04 with a 0x1f character cap and a CDXFont__GetTextExtent width gate against _DAT_0089bcb8, including fallback ASCII mappings for rejected accented glyphs. Static retail evidence only; exact class layout, live input behavior, save-name side effects, BEA launch, and rebuild parity remain unproven.",
                tags("fep-virtual-keyboard", "key-token", "edit-buffer", "frontend-input")
            ),
            new Spec(
                "0x00520f70",
                "CFEPVirtualKeyboard__MoveSelectionToRow",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("target_row", intType) },
                "Wave564 signature/comment hardening: RET 0x4 plus four ButtonPressed row-navigation callsites prove a single target_row stack argument. The helper preserves horizontal selection using per-key widths and the weighted-column field at this+0x6f4, updates selected row/column fields at this+0x6e8/0x6ec, wraps rows through the 0..4 keyboard range, and loops through CFEPVirtualKeyboard__IsSpecialKeyBlocked to avoid unavailable special keys. Static retail evidence only; exact key-record layout, UI behavior, BEA launch, and rebuild parity remain unproven.",
                tags("fep-virtual-keyboard", "row-navigation", "selection-state", "frontend-input")
            ),
            new Spec(
                "0x00521260",
                "CFEPVirtualKeyboard__DrawPanel",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("panel_y", floatType), param("transition", floatType), param("alpha", intType) },
                "Wave564 signature/comment hardening: RET 0x0c plus CFEPVirtualKeyboard__Render proves three stack arguments: DAT_0063fd30 panel_y, transition, and the clamped alpha value. The body draws the virtual-keyboard backing panel and edit-buffer box, measures the wide edit buffer through CDXFont__GetTextExtent, highlights the selected save name when this+0x48 is set, draws the edit text with alpha-derived color, and renders the blinking cursor by measuring the prefix up to cursor offset this+0x44. Static retail evidence only; exact draw-state layout, live frontend timing, BEA launch, and rebuild parity remain unproven.",
                tags("fep-virtual-keyboard", "draw-panel", "edit-buffer", "frontend-render")
            )
        };

        println("ApplyFEPVirtualKeyboardWave564 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (stats.missing > 0 || stats.bad > 0) {
            throw new IllegalStateException("Wave564 FEP virtual keyboard apply failed: missing=" +
                stats.missing + " bad=" + stats.bad);
        }
    }
}
