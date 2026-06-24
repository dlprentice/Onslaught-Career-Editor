//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class ApplyMenuItemBaseCommentTranche extends GhidraScript {
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
            "menuitem-base-wave371",
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
            new Spec("0x00453a50", "CMenuItem__ButtonPressed_NoOp",
                "Comment hardening: zero-body CMenuItem-family button-handler slot consists of RET 0x0c and is reached through vtable data, including vtable 0x005db440 slot 1. Static retail evidence only; exact source method identity, caller class ownership, runtime input behavior, and rebuild parity remain unproven.",
                tags("menuitem", "frontend-menu", "no-op-vfunc", "comment-hardened")),

            new Spec("0x00453a60", "CMenuItem__IsEnabled",
                "Comment hardening: CMenuItem-family enabled-state virtual reads this+0x10 and returns it; vtable read-back includes 0x005db440 slot 3 and 0x005dc520 slot 3. Static retail evidence only; concrete field type, exact source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("menuitem", "frontend-menu", "vtable-slot", "comment-hardened")),

            new Spec("0x00453a70", "CMenuItem__GetRowHeight",
                "Comment hardening: CMenuItem-family row-height virtual returns 0x14 when this+0x0c is zero and 0x28 when it is nonzero; vtable read-back includes 0x005db440 slot 6 and 0x005dc520 slot 6. Static retail evidence only; concrete field semantics, exact source identity, runtime layout behavior, and rebuild parity remain unproven.",
                tags("menuitem", "frontend-menu", "layout", "comment-hardened")),

            new Spec("0x00453a80", "CMenuItem__DefaultFalseFlag",
                "Comment hardening: shared CMenuItem-family default-false virtual returns zero and is reused by flag-style slots 8, 9, and 10 in vtable 0x005db440 and sibling menu-item vtables. Static retail evidence only; per-slot semantic names, exact source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("menuitem", "frontend-menu", "shared-false-vfunc", "comment-hardened")),

            new Spec("0x00453a90", "CMenuItem__scalar_deleting_dtor",
                "Comment hardening: scalar deleting destructor wrapper installs vtable 0x005db440, conditionally frees through OID__FreeObject when flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership, exact source identity, concrete class layout, runtime lifecycle behavior, and rebuild parity remain unproven.",
                tags("menuitem", "frontend-menu", "destructor", "comment-hardened"))
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
            throw new IllegalStateException("MenuItem base comment tranche failed for " + failed + " target(s)");
        }
    }
}
