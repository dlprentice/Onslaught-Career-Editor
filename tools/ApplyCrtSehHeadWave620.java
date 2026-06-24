//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtSehHeadWave620 extends GhidraScript {
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "crt-seh-wave620",
            "retail-binary-evidence",
            "comment-hardened"
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
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
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
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getSignature() + " comment/tag update only");
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + fn.getSignature());
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055d6a0",
                "CRT__SehPopExceptionFrameAndJump",
                "Wave620 CRT/SEH head hardening: helper pops the FS:[0] exception-list frame, restores ESP/EBP from the current frame, and jumps through EAX from the first stack argument. Xrefs include CRT__SehUnwindAndResumeSearch; Ghidra decompile warns on the indirect jump. Static retail SEH helper evidence only; exact MSVC CRT version, exception-record layout identity, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-seh", "seh-frame", "fs-exception-list", "indirect-jump", "callsite-verified")
            ),
            new Spec(
                "0x0055d6d4",
                "CRT__InvokeCallbackWithLockGuards",
                "Wave620 CRT/SEH head hardening: compact callback-transfer helper pops EAX/ECX, exchanges the stack top with EAX, and jumps indirectly through EAX after Ghidra renders LOCK/UNLOCK pseudo-operations. Xrefs include CRT__BuildCatchObject and CRT__DestroyCatchObject. Static retail CRT helper evidence only; exact CRT helper identity, callback target semantics, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-seh", "callback-wrapper", "lock-unlock-pseudo", "indirect-jump", "callsite-verified")
            ),
            new Spec(
                "0x0055d6db",
                "CRT__SehLockUnlockAndJump",
                "Wave620 CRT/SEH head hardening: sibling compact callback-transfer helper pops EAX/ECX, exchanges the stack top with EAX, and jumps indirectly through EAX after Ghidra renders LOCK/UNLOCK pseudo-operations. Xref evidence reaches it from CRT__BuildCatchObject. Static retail CRT helper evidence only; exact CRT helper identity, callback target semantics, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-seh", "callback-wrapper", "lock-unlock-pseudo", "indirect-jump", "callsite-verified")
            ),
            new Spec(
                "0x0055d6e2",
                "CRT__SehRtlUnwindAndRestoreFrame",
                "Wave620 CRT/SEH head hardening: helper builds a temporary SEH frame, calls RtlUnwind at 0x005d04e6 with landing label 0x0055d70a, clears flag bit 0x2 in the exception record, and restores FS exception-list state. Xrefs include CRT__SehUnwindAndResumeSearch and CRT__SehFilterCppException. Static retail SEH helper evidence only; exact exception-record layout identity, runtime unwind behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-seh", "seh-frame", "fs-exception-list", "rtlunwind", "callsite-verified")
            ),
            new Spec(
                "0x0055d7bb",
                "CRT__SehCallback_Call_005602d2",
                "Wave620 CRT/SEH head hardening: callback wrapper reached by a data reference from CRT__SehInvokeCallSettingFrame12; instruction evidence clears direction flag, marshals eight stack arguments from the caller/frame structure, and calls 0x005602d2 before returning. Static retail CRT/SEH callback evidence only; exact handler prototype, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-seh", "callback-wrapper", "data-xref", "callsite-verified")
            ),
            new Spec(
                "0x0055d896",
                "CRT__SehFilterCppException",
                "Wave620 CRT/SEH head hardening: filter checks exception flags at record+4 against 0x66, marks frame+0x24 on the early path, otherwise dispatches through CRT__SehDispatchWithScopeTable, optionally calls CRT__SehRtlUnwindAndRestoreFrame, and jumps through the frame callback at +0x18. Data-xref evidence reaches it from CRT__CallExceptionTranslator. Static retail C++ exception filter evidence only; exact CRT version, frame layout identity, runtime translator behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-seh", "exception-filter", "indirect-jump", "data-xref", "callsite-verified")
            ),
            new Spec(
                "0x0055d90b",
                "CRT__GetRangeOfTryBlocksForState",
                "Wave620 CRT/SEH head hardening: helper walks 0x14-byte try-block records from metadata at +0x10 using count at +0x0c, compares the current state against record bounds, writes the selected low/high range outputs, and calls CDXTexture__InvokeGlobalCleanupCallbackAndFinalize on invalid bounds. Xrefs include CRT__SehLookupAndInvokeScopeHandler and CRT__ValidateCatchHandlersForThrow. Static retail C++ EH table evidence only; exact CRT metadata layout identity, runtime catch selection behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-seh", "try-block-range", "eh-metadata", "callsite-verified")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad != 0 || stats.missing != 0) {
                throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
            }
        }
    }
}
