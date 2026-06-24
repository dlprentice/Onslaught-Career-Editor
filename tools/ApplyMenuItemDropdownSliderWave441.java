//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyMenuItemDropdownSliderWave441 extends GhidraScript {
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
        return toAddr(addressText);
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
            "menuitem-wave441",
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
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
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

            Function readBack = functionAtEntry(address);
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
        DataType floatType = FloatDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004a3b10",
                "CMenuItemDropdown__Init",
                "__thiscall",
                voidPtr,
                "Wave441 signature/comment hardening: constructor-style dropdown initializer for vtable 0x005dc578; stores text/item ids at +0x18/+0x04, clears compact base fields, writes default color 0xffd6d6d6, sets deferred-commit flag at +0x25, clears expanded state at +0x24, and returns with RET 0x0c. Static retail decompile/xref/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "init", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("text_id", intType),
                    param("item_id", intType),
                    param("defer_commit", byteType)
                }
            ),
            new Spec(
                "0x004a3b50",
                "CMenuItemDropdown__UpdateSelection",
                "__thiscall",
                voidType,
                "Wave441 signature/comment hardening: dropdown vtable slot 12 selection sync helper; calls the value/count provider at vtable+0x3c and copies the returned selection into committed/current fields at +0x1c and +0x20. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "selection", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a3b60",
                "CMenuItemDropdown__InitVariant",
                "__thiscall",
                voidPtr,
                "Wave441 signature/comment hardening: constructor-style dropdown variant initializer for vtable 0x005dc5c4; mirrors CMenuItemDropdown__Init setup while selecting the variant table whose extra slots include Return2 and Localization__GetYesNoString. Static retail decompile/xref/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "init", "variant", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("text_id", intType),
                    param("item_id", intType),
                    param("defer_commit", byteType)
                }
            ),
            new Spec(
                "0x004a3ba0",
                "CMenuItemDropdown__ClearPending",
                "__cdecl",
                voidType,
                "Wave441 signature/comment hardening: clears the deferred dropdown render global DAT_0070486c; CMenuItemRange__Render calls this before layout/render traversal. Static retail xref/decompile evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact global naming, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "deferred-render", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {}
            ),
            new Spec(
                "0x004a3bb0",
                "CMenuItemDropdown__ProcessPending",
                "__cdecl",
                voidType,
                "Wave441 signature/comment hardening: consumes DAT_0070486c as a queued dropdown item pointer, clears it, and when non-null calls CMenuItemDropdown__Render with the saved x/y globals and queued-pass flag 1; CMenuItemRange__Render calls this after traversal. Static retail xref/decompile evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact global naming, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "deferred-render", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {}
            ),
            new Spec(
                "0x004a3be0",
                "CMenuItemDropdown__RenderOrQueueDeferred",
                "__thiscall",
                voidType,
                "Wave441 comment hardening: dropdown vtable slot 4 render entry; interactive calls queue this/x/y in DAT_0070486c/DAT_00704874/DAT_00704870 when no popup is pending, otherwise it falls through to CMenuItemDropdown__Render with queued-pass flag 0. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact global naming, runtime frontend rendering/input behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "render", "deferred-render", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("interactive", intType)
                }
            ),
            new Spec(
                "0x004a3c30",
                "CMenuItemDropdown__Render",
                "__thiscall",
                voidType,
                "Wave441 signature/comment hardening: dropdown popup/body renderer (RET 0x0c); syncs committed/current selection from vtable+0x3c, measures text, draws collapsed or expanded state, handles mouse hover/click through CFrontEnd__GetCursorStateInRect/CFrontEnd__GetClickStateInRect rect helpers, commits immediately when +0x25 is clear, and accepts an observed queued-pass flag that is pushed by callers but not otherwise used in the static decompile. Static retail decompile/xref evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact coordinate/field semantics, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "render", "deferred-render", "mouse-input", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("queued_pass", intType)
                }
            ),
            new Spec(
                "0x004a40e0",
                "CMenuItemDropdown__IsExpanded",
                "__thiscall",
                byteType,
                "Wave441 comment hardening: dropdown vtable slots 8/9 state query; returns byte field +0x24, which button and mouse paths use as the expanded/open state. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field name, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "state-query", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a40f0",
                "CMenuItemDropdown__CommitSelection",
                "__thiscall",
                voidType,
                "Wave441 signature/comment hardening: dropdown vtable slot 11 commit helper; if current selection at +0x20 differs from committed selection at +0x1c, calls vtable+0x38 with the current selection and then stores it as committed. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "selection", "commit", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a4110",
                "CMenuItemDropdown__ButtonPressed",
                "__thiscall",
                voidType,
                "Wave441 comment hardening: dropdown vtable slot 1 button handler; handles up/down buttons 0x2a/0x36 and 0x2b/0x37, select 0x2c expansion/commit, and cancel 0x2e rollback to the committed selection, using vtable+0x40 for option count and vtable+0x38 for commit callbacks. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, runtime controller behavior, exact field names, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "input", "selection", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from_controller", intType),
                    param("button", intType)
                }
            ),
            new Spec(
                "0x004a42f0",
                "CMenuItemDropdown__HasPendingSelectionChange",
                "__thiscall",
                boolType,
                "Wave441 comment hardening: dropdown vtable slot 10 deferred-commit query; returns true only when +0x25 is set and committed/current selection fields at +0x1c/+0x20 differ. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemdropdown", "frontend-menu", "dropdown", "selection", "state-query", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a4250",
                "CMenuItemSlider__Init",
                "__thiscall",
                voidPtr,
                "Wave441 signature/comment hardening: constructor-style slider initializer for vtable 0x005dc610; clears compact base fields, sets text/id field +0x04 to 3, default color 0xffd6d6d6, and stores the linked range/list pointer at +0x1c for the select-button callback walk. Static retail decompile/xref/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemslider", "frontend-menu", "slider", "init", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("linked_range", voidPtr)
                }
            ),
            new Spec(
                "0x004a4290",
                "CMenuItemSlider__ButtonPressed",
                "__thiscall",
                voidType,
                "Wave441 comment hardening: slider vtable slot 1 button handler; on select button 0x2c increments DAT_00704868, walks the linked range/list stored at +0x1c, and calls each child item's vtable+0x2c callback. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, runtime controller behavior, exact linked-list ownership, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemslider", "frontend-menu", "slider", "input", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from_controller", intType),
                    param("button", intType)
                }
            ),
            new Spec(
                "0x004a4310",
                "CMenuItemSlider__Render",
                "__thiscall",
                voidType,
                "Wave441 comment hardening: slider vtable slot 4 render override; optionally computes a pulsed grayscale color when DAT_00704a88 is set, resolves text through vtable+0x8, and forwards x/y/alpha/color/text to CMenuItem__Render. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, runtime rendering behavior, exact global meaning, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemslider", "frontend-menu", "slider", "render", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("alpha", intType)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0"
            + " would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave441 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
