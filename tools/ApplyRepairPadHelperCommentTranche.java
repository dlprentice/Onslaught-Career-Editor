//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class ApplyRepairPadHelperCommentTranche extends GhidraScript {
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

    private static boolean isDryRun(String mode) {
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

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private void applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " comment/tags");
            return;
        }
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        println("OK: " + spec.address + " " + spec.name + " comment/tags");
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        String[] commonTags = new String[] {"static-reaudit", "repairpad-wave328", "repairpad-ai", "comment-hardened"};
        Spec[] specs = new Spec[] {
            new Spec("0x0040c5b0", "CRepairPadAI__IsWithinRepairBounds",
                "Comment/tag correction: leaf helper called by CRepairPadAI__IsCompatibleDockCandidate; compares two candidate-unit float thresholds at +0xf8/+0xfc against the referenced bounds record at *(this+0x4b0)+0x1c/+0x20. Exact field names, runtime docking behavior, and rebuild parity remain unproven.",
                commonTags),
            new Spec("0x0040c5e0", "CRepairPadAI__HasAnySlotBelowThreshold",
                "Comment/tag correction: leaf helper called by CRepairPadAI__IsCompatibleDockCandidate; scans six float slots starting at +0x52c and returns true when an enabled/zero-gated slot is still below its referenced threshold. Exact slot semantics, concrete layout, runtime repair behavior, and rebuild parity remain unproven.",
                commonTags),
            new Spec("0x004d6e00", "CRepairPadAI__IsCompatibleDockCandidate",
                "Comment/tag correction: compatibility gate calls the repair-bounds and slot-threshold helpers, then compares candidate and owner state fields at +0x138 before accepting a dock candidate. Exact state enum labels, runtime repair-pad behavior, concrete layouts, and rebuild parity remain unproven.",
                commonTags)
        };

        int updated = 0;
        int skipped = 0;
        for (Spec spec : specs) {
            applySpec(spec, dryRun);
            if (dryRun) {
                skipped++;
            }
            else {
                updated++;
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " renamed=0 missing=0 bad=0");
    }
}
