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

public class ApplyMenuItemRangeWave442 extends GhidraScript {
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
            "menuitem-wave442",
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
                "0x004a45c0",
                "CMenuItemRange__Init",
                "__thiscall",
                voidPtr,
                "Wave442 signature/comment hardening: constructor-style range initializer for four-slot vtable 0x005dc650; stores title text at +0x04, initializes the linked item set at +0x08, clears selected index +0x18 and cached blank texture +0x24, stores render origin floats at +0x1c/+0x20, and stores unresolved panel/layout arguments at +0x28/+0x2c. Static retail decompile/xref/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "init", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("title_text", shortPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("panel_flag", intType),
                    param("panel_arg", intType)
                }
            ),
            new Spec(
                "0x004a4610",
                "CMenuItemRange__ScalarDestructor",
                "__thiscall",
                voidPtr,
                "Wave442 signature/comment hardening: scalar deleting destructor for CMenuItemRange; calls CMenuItemRange__Destructor and frees this through CDXMemoryManager__Free when flags bit 0 is set. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, allocator ownership, runtime destructor ordering, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "destructor", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004a4630",
                "CMenuItemRange__ResetIterator",
                "__thiscall",
                voidType,
                "Wave442 signature/comment hardening: resets selected index +0x18 and list iterator +0x10, then walks the linked item set from +0x08 and calls each child vtable+0x30 callback. Static retail decompile/xref evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact child callback identity, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "iteration", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a4670",
                "CMenuItemRange__AddItem",
                "__thiscall",
                voidType,
                "Wave442 signature/comment hardening: range item append wrapper; forwards this+0x08 and item to CSPtrSet__AddToTail. PauseMenu__Init calls this repeatedly after constructing menu items. Static retail decompile/xref evidence only; source MenuItem.cpp body is absent from the current source snapshot, concrete child ownership, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "item-list", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("item", voidPtr)
                }
            ),
            new Spec(
                "0x004a4680",
                "CMenuItemRange__Destructor",
                "__thiscall",
                voidType,
                "Wave442 signature/comment hardening: range destructor reinstalls vtable 0x005dc650, walks child items from the linked set and invokes each child scalar destructor with delete flag 1, clears the set, releases cached blank texture state through CHud__DecrementCounter9C when +0x24 is nonzero, and clears the set again during SEH unwinding cleanup. Static retail decompile evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact resource ownership, runtime teardown behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "destructor", "resource-cleanup", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a4730",
                "CMenuItemRange__LoadTexture",
                "__thiscall",
                voidType,
                "Wave442 signature/comment hardening: loads FrontEnd_v2/FE_Blank.tga into cached field +0x24, resets iterator +0x10, and walks child items invoking vtable+0x34 texture/load callbacks. Static retail decompile/xref/string evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact texture lifetime, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "texture", "iteration", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a4790",
                "CMenuItemRange__SelectNext",
                "__thiscall",
                voidType,
                "Wave442 signature/comment hardening: advances selected index +0x18, wraps only when item count +0x14 is at least 3, skips disabled children via vtable+0x0c, calls CFrontEnd__PlaySound(0) on success, and restores the old index if no enabled item is found. Static retail decompile/xref evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact selection rules, runtime controller behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "selection", "input", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a4810",
                "CMenuItemRange__Render",
                "__thiscall",
                intType,
                "Wave442 signature/comment hardening: main range renderer; calls CMenuItemDropdown__ClearPending before traversal, computes row heights through child vtable+0x18, optionally measures/draws the title and panel frame, lazy-loads FrontEnd_v2/FE_Blank.tga, renders each child with selected-state flag, updates selected index from mouse hover/click when bindings allow it, sets DAT_00704a88 if any child reports vtable+0x28 true, then calls CMenuItemDropdown__ProcessPending after traversal. Static retail decompile/xref evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact coordinate/layout semantics, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "render", "dropdown-deferred-render", "mouse-input", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("binding_context", voidPtr)
                }
            ),
            new Spec(
                "0x004a4cd0",
                "CMenuItemRange__ProcessInput",
                "__thiscall",
                intType,
                "Wave442 signature/comment hardening: vtable slot 2 input gate for the selected child; resolves child at selected index +0x18, checks child vtable+0x20, forwards the three stack arguments to child vtable+0x04 when active, and returns 1 only after forwarding. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact argument meanings, runtime input behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "input", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from_controller", intType),
                    param("button", intType),
                    param("context", intType)
                }
            ),
            new Spec(
                "0x004a4d20",
                "CMenuItemRange__HandleKeyPress",
                "__thiscall",
                voidType,
                "Wave442 signature/comment hardening: vtable slot 1 range button handler; button 0x2a moves up with enabled-child skipping, button 0x2b calls CMenuItemRange__SelectNext, and other buttons are forwarded to the selected child vtable+0x04. Successful up/down selection plays frontend sound 0. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact controller mapping, runtime input behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "input", "selection", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from_controller", intType),
                    param("button", intType),
                    param("context", intType)
                }
            ),
            new Spec(
                "0x004a4dd0",
                "CMenuItemRange__SetItemEnabled",
                "__thiscall",
                voidType,
                "Wave442 signature/comment hardening: walks the linked item set and, for each child whose item id at +0x08 matches item_id, writes enabled to child offset +0x10. Static retail decompile/xref evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact child layout, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrange", "frontend-menu", "range", "item-list", "enabled-state", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("item_id", intType),
                    param("enabled", intType)
                }
            ),
            new Spec(
                "0x004a4e10",
                "CMenuItemRangeVariant__Init",
                "__thiscall",
                voidPtr,
                "Wave442 signature/comment hardening: constructor-style range-variant initializer for vtable 0x005dc664; mirrors CMenuItemRange__Init field setup while selecting the variant table that reuses the range input/process slots. Static retail decompile/xref/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact field names, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrangevariant", "frontend-menu", "range", "variant", "init", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("title_text", shortPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("panel_flag", intType),
                    param("panel_arg", intType)
                }
            ),
            new Spec(
                "0x004a4e60",
                "CMenuItemRangeVariant__ScalarDestructor",
                "__thiscall",
                voidPtr,
                "Wave442 signature/comment hardening: scalar deleting destructor for CMenuItemRangeVariant; calls CMenuItemRangeVariant__Destructor and frees this through CDXMemoryManager__Free when flags bit 0 is set. Static retail decompile/vtable evidence only; source MenuItem.cpp body is absent from the current source snapshot, allocator ownership, runtime destructor ordering, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrangevariant", "frontend-menu", "range", "variant", "destructor", "vtable-backed", "signature-corrected", "comment-hardened", "source-absent"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004a4e80",
                "CMenuItemRangeVariant__Destructor",
                "__thiscall",
                voidType,
                "Wave442 signature/comment hardening: range-variant destructor with the same linked-child teardown and cached texture release shape as CMenuItemRange__Destructor, but with the variant-specific SEH unwind target before restoring the base range vtable during destruction. Static retail decompile/unwind evidence only; source MenuItem.cpp body is absent from the current source snapshot, exact inheritance model, runtime teardown behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmenuitemrangevariant", "frontend-menu", "range", "variant", "destructor", "resource-cleanup", "signature-corrected", "comment-hardened", "source-absent"),
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
            + " created=0"
            + " would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave442 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
