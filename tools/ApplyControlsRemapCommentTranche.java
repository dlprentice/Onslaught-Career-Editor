//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class ApplyControlsRemapCommentTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.comment = comment;
            this.tags = tags;
        }
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

    private Function getFunctionOrThrow(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addressText);
        }
        return fn;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "controls-remap-wave372",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " comment/tag update");
            return true;
        }

        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = getFunctionOrThrow(spec.address);
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        println("OK: " + spec.address + " " + spec.name);
        Thread.sleep(50);
        return true;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec("0x00453f50", "Controls__DispatchRemap",
                "Comment hardening: remap dispatch switch normalizes action_code 0x3b..0x4c into persisted options entry id / binding-type pairs, then invokes callback(key_or_value, entryId, bindingType). Xrefs include CControllerDefinition__RenderBindingsAndPollRemapInput, Controls__RemapKey, and ControlsUI__RenderBindingsList. Static retail evidence only; exact source contract, raw callback boundary ownership, runtime remap behavior, and rebuild parity remain unproven.",
                tags("controls", "frontend-controls", "remap", "dispatch-helper", "comment-hardened")),

            new Spec("0x004541e0", "Controls__RemapKey",
                "Comment hardening: high-level remap handler uses g_ControlRemapVkScanPacked and g_ControlRemapBindingType state, calls Controls__ClearDuplicateBinding, Controls__DispatchRemap, and Controls__ApplyPreset, and scans the active options table for related slot conflicts. Static retail evidence only; exact source contract, runtime input behavior, and rebuild parity remain unproven.",
                tags("controls", "frontend-controls", "remap", "input-binding", "comment-hardened")),

            new Spec("0x00454e00", "Controls__GetDeviceCategory",
                "Comment hardening: device-code category switch maps raw keyboard/mouse/controller-style identifiers to category values 1..7 and is called by remap conflict logic. Static retail evidence only; exact device taxonomy, runtime input behavior, and rebuild parity remain unproven.",
                tags("controls", "frontend-controls", "remap", "device-category", "comment-hardened")),

            new Spec("0x00454e90", "Controls__ClearDuplicateBinding",
                "Comment hardening: duplicate-binding cleanup scans the active 0x20-byte options entry table at DAT_008892d8, checks both 12-byte binding slots, compares key/scan plus device category, and clears matching slot key_code to -1. Static retail evidence only; concrete options-entry type, runtime remap behavior, and rebuild parity remain unproven.",
                tags("controls", "frontend-controls", "remap", "duplicate-binding", "options-table", "comment-hardened")),

            new Spec("0x00456650", "Controls__FindFirstFreeBindingSlot",
                "Comment hardening: free-slot scan walks the active 0x20-byte options entry table at DAT_008892d8, checks the selected 12-byte binding slot at entry+0x08+0x0c*slot_index for -1, and returns a pointer-tagged entry result. Static retail evidence only; concrete options-entry type, caller semantics, runtime remap behavior, and rebuild parity remain unproven.",
                tags("controls", "frontend-controls", "remap", "free-binding-slot", "options-table", "comment-hardened"))
        };

        int changedOrWouldChange = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                if (applySpec(spec, dryRun)) {
                    changedOrWouldChange++;
                }
            } catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println("targets=" + specs.length + " changed_or_would_change=" + changedOrWouldChange + " failed=" + failed + " dry=" + dryRun);
        if (failed > 0) {
            throw new IllegalStateException("Controls remap comment tranche failed for " + failed + " target(s)");
        }
    }
}
