//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class ApplyTerrainGuideCallerCommentWave544 extends GhidraScript {
    private static final String ADDRESS = "0x00479cb0";
    private static final String NAME = "CGillM__InitTerrainGuideComponent";
    private static final String OLD_COMMENT =
        "Wave389 owner/name/signature correction: CGillM vtable 0x005e0b30 slot 119 points here. " +
        "The body allocates a 0x20-byte object with GillM.cpp line 0x3e evidence, initializes it " +
        "through CTerrainGuide__ctor_like_004f1ec0, and stores the result at this+0x208. Static " +
        "retail evidence only; exact guide layout, source method name, runtime behavior, and " +
        "rebuild parity remain unproven.";
    private static final String NEW_COMMENT =
        "Wave389 owner/name/signature correction, refreshed by Wave544: CGillM vtable 0x005e0b30 " +
        "slot 119 points here. The body allocates a 0x20-byte object with GillM.cpp line 0x3e " +
        "evidence, initializes it through CTerrainGuide__ctor, and stores the result at this+0x208. " +
        "Static retail evidence only; exact guide layout, source method name, runtime behavior, " +
        "and rebuild parity remain unproven.";

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

    private Function targetFunction() {
        Address address = toAddr(ADDRESS);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + ADDRESS);
        }
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private boolean needsUpdate(Function fn) {
        String comment = fn.getComment();
        return comment == null || !comment.equals(NEW_COMMENT);
    }

    private void verifyReadBack() {
        Function fn = targetFunction();
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + ADDRESS);
        }
        if (!fn.getName().equals(NAME)) {
            throw new IllegalStateException("Readback name mismatch: " + fn.getName());
        }
        String comment = fn.getComment();
        if (comment == null || !comment.equals(NEW_COMMENT)) {
            throw new IllegalStateException("Readback comment mismatch");
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        Function fn = targetFunction();
        if (fn == null) {
            println("MISSING: " + ADDRESS);
            stats.missing++;
        } else if (!fn.getName().equals(NAME)) {
            println("BADNAME: " + ADDRESS + " " + fn.getName() + " expected " + NAME);
            stats.bad++;
        } else {
            String comment = fn.getComment();
            boolean recognized = NEW_COMMENT.equals(comment) || OLD_COMMENT.equals(comment);
            if (!recognized) {
                println("BADCOMMENT: " + ADDRESS + " unrecognized existing comment");
                stats.bad++;
            } else if (dryRun) {
                println((needsUpdate(fn) ? "DRY: " : "SKIP: ") + ADDRESS + " " + NAME);
                stats.skipped++;
            } else if (!needsUpdate(fn)) {
                println("SKIP: " + ADDRESS + " already current");
                stats.skipped++;
            } else {
                fn.setComment(NEW_COMMENT);
                verifyReadBack();
                println("OK: " + ADDRESS + " " + NAME);
                stats.updated++;
            }
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
