//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyMenuItemWave440 extends GhidraScript {
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
            "menuitem-wave440",
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
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004a3100",
                "CMenuItem__IsMouseInBounds",
                "__cdecl",
                intType,
                "Wave440 signature/comment hardening: cdecl frontend hit-test wrapper that forwards four float rectangle coordinates to CFrontEnd__GetCursorStateInRect and returns the helper status in EAX; CMenuItemRange__Render calls it for menu mouse hover checks. Static retail xref/decompile/vtable-adjacent evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact rectangle coordinate semantics, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "mouse-hit-test", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("x0", floatType),
                    param("y0", floatType),
                    param("x1", floatType),
                    param("y1", floatType)
                }
            ),
            new Spec(
                "0x004a3120",
                "CMenuItem__IsMouseClicked",
                "__cdecl",
                intType,
                "Wave440 signature/comment hardening: cdecl frontend click-test wrapper that forwards four float rectangle coordinates to CFrontEnd__GetClickStateInRect and returns the helper status in EAX; CMenuItemRange__Render calls it for menu mouse activation checks. Static retail xref/decompile/vtable-adjacent evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact rectangle coordinate semantics, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "mouse-click-test", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("x0", floatType),
                    param("y0", floatType),
                    param("x1", floatType),
                    param("y1", floatType)
                }
            ),
            new Spec(
                "0x004a3140",
                "CMenuItem__Clone",
                "__thiscall",
                voidPtr,
                "Wave440 comment hardening: recovered sibling/base vtable 0x005db440 slot 7 clone helper; allocates a compact 0x1c-byte object, installs the 0x005db440 table, and copies display fields at +0x8, +0xc, +0x10, and +0x14. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact class name for the compact sibling object, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "clone", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a3190",
                "CMenuItem__GetText",
                "__thiscall",
                shortPtr,
                "Wave440 comment hardening: vtable slot 2 text resolver for the menu-item family; reads the primary text/id field at +0x8, handles special control/profile ids through a wide-string scratch buffer, and otherwise returns CText or Localization text. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime localization behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "text", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a3260",
                "CMenuItem__RenderCentered",
                "__thiscall",
                voidType,
                "Wave440 signature/comment hardening: recovered sibling/base vtable render slot; obtains text through vtable+0x8 and forwards x/y/alpha plus default ARGB color 0xffffffff to CMenuItem__Render (RET 0x0c). Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact coordinate semantics, runtime frontend rendering, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "render", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("alpha", intType)
                }
            ),
            new Spec(
                "0x004a3290",
                "CMenuItem__RenderWithColor",
                "__thiscall",
                voidType,
                "Wave440 signature/comment hardening: custom-color render wrapper; obtains text through vtable+0x8 and forwards x/y/alpha, caller ARGB color, and text to CMenuItem__Render (RET 0x10). Static retail decompile/xref evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact coordinate/color semantics, runtime frontend rendering, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "render", "color", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("alpha", intType),
                    param("argb_color", intType)
                }
            ),
            new Spec(
                "0x004a32c0",
                "CMenuItem__Render",
                "__thiscall",
                voidType,
                "Wave440 signature/comment hardening: shared text render body (RET 0x14); draws optional secondary text/id from +0xc, measures the supplied text through CDXFont__GetTextExtent, chooses selected/disabled colors from item state, and emits CDXEngine__DrawTextScaledWithShadow. Static retail decompile/instruction/xref evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime frontend rendering, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "render", "text", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("alpha", intType),
                    param("argb_color", intType),
                    param("text", shortPtr)
                }
            ),
            new Spec(
                "0x004a3420",
                "CMenuItem__GetTextWidth",
                "__thiscall",
                intType,
                "Wave440 comment hardening: recovered sibling/base vtable width slot; obtains text via vtable+0x8, measures it with CDXFont__GetTextExtent, and returns the x extent. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, runtime font metrics, exact field names, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "text-width", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a3450",
                "CMenuItem__Clone",
                "__thiscall",
                voidPtr,
                "Wave440 signature/comment hardening: CMenuItem vtable 0x005dc520 slot 7 clone; allocates a 0x38-byte object, initializes the recovered base table before installing 0x005dc520, copies display/value fields, and transfers the owner active-reader linkage from +0x34 through CGenericActiveReader__SetReader. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact class layout, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "clone", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a3510",
                "CMenuItem__Init",
                "__thiscall",
                voidPtr,
                "Wave440 signature/comment hardening: 0x38-byte CMenuItem initializer; writes primary/item ids, default color 0xffd6d6d6, owner monitor-list linkage at +0x34, notify flag at +0x30, max value at +0x2c, and scaled current/committed values at +0x24/+0x28 before installing vtable 0x005dc520. Static retail decompile/xref evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "init", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("text_id", intType),
                    param("item_id", intType),
                    param("value_scale", floatType),
                    param("owner", voidPtr),
                    param("max_value", intType),
                    param("notify_on_change", byteType)
                }
            ),
            new Spec(
                "0x004a3610",
                "CMenuItem__ScalarDestructor",
                "__thiscall",
                voidPtr,
                "Wave440 signature/comment hardening: scalar deleting destructor wrapper for vtable 0x005dc520; calls CMenuItem__Destructor and frees through CDXMemoryManager__Free when flags bit 0 is set. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact allocator ownership, runtime teardown behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "destructor", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004a3630",
                "CMenuItem__InitWithIcon",
                "__thiscall",
                voidPtr,
                "Wave440 signature/comment hardening: alternate CMenuItem initializer that clears +0x8, stores the first id at +0x18, applies the same default color/owner monitor-list/value setup as CMenuItem__Init, and installs vtable 0x005dc520. Static retail decompile/xref evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact first-id/icon semantics, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "init", "icon-or-localized-id", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("icon_or_text_id", intType),
                    param("item_id", intType),
                    param("value_scale", floatType),
                    param("owner", voidPtr),
                    param("max_value", intType),
                    param("notify_on_change", byteType)
                }
            ),
            new Spec(
                "0x004a3730",
                "CMenuItem__Destructor",
                "__thiscall",
                voidType,
                "Wave440 signature/comment hardening: CMenuItem destructor body; restores vtables during teardown, decrements resource counters at +0x1c/+0x20 when present, and removes this item's owner monitor-list node from +0x34 through CSPtrSet__Remove before restoring the recovered base table. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact resource types, runtime teardown behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "destructor", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a37c0",
                "CMenuItem__RenderValueBar",
                "__thiscall",
                voidType,
                "Wave440 comment hardening: CMenuItem vtable 0x005dc520 slot 4 value-bar renderer; syncs current/committed values, invokes value callbacks at vtable+0x34/+0x38, draws the segmented bar sprites, and maps left/right mouse hotspots to buttons 0x36/0x37 when interactive. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, runtime sprite/input behavior, exact field types, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "render", "value-bar", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("interactive", intType)
                }
            ),
            new Spec(
                "0x004a43a0",
                "CMenuItem__ButtonPressed",
                "__thiscall",
                voidType,
                "Wave440 comment hardening: CMenuItem vtable 0x005dc520 slot 1 button handler; handles confirm button 0x2c, decrement 0x36, increment 0x37, clamps against +0x2c, triggers vtable+0x38/value sounds, and optionally notifies the owner when +0x30 is set. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, runtime controller behavior, exact field names, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "input", "value-bar", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from_controller", intType),
                    param("button", intType)
                }
            ),
            new Spec(
                "0x004a4450",
                "CMenuItem__GetWidth",
                "__thiscall",
                intType,
                "Wave440 comment hardening: CMenuItem vtable 0x005dc520 slot 5 width helper; measures vtable+0x8 text with CDXFont__GetTextExtent and returns text width plus fixed 0x6a padding. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, runtime font metrics, exact padding meaning, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "text-width", "vtable-backed", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a44c0",
                "CMenuItem__SetUserData",
                "__thiscall",
                voidType,
                "Wave440 signature/comment hardening: one-store setter that writes the caller value to +0x20, a field also read by value-bar/resource paths. Static retail xref/decompile evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact pointer/resource type, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitem", "frontend-menu", "setter", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("user_data", voidPtr)
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
            throw new IllegalStateException("Wave440 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
