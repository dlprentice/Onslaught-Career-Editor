//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtSehTailWave881 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] previousNames;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String[] previousNames, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousNames = previousNames;
            this.signature = signature;
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

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "crt-seh-tail-wave881",
            "wave881-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-crt-runtime-infrastructure",
            "high-importance-low-local-evidence-density",
            "compiler-runtime",
            "crt-seh",
            "cxx-exception-runtime",
            "raw-commentless-head"
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
        if (!fn.getSignature().toString().equals(spec.signature)) {
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
        String actualSignature = readBack.getSignature().toString();
        if (!actualSignature.equals(spec.signature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature);
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
            if (!nameAllowed(fn.getName(), spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.signature);
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
            Thread.sleep(50);
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
                "0x005602d2",
                "CRT__SehDispatchWithScopeTable",
                new String[] {},
                "int CRT__SehDispatchWithScopeTable(void)",
                "Wave881 static read-back: CRT SEH/C++ exception dispatch helper. The body validates frame magic 0x19930520, checks the exception-record flags byte with mask 0x66, routes unwind cases through CRT__SehUnwindToTargetState(..., targetState=-1), and routes C++ EH code 0xe06d7363 either through a computed custom handler pointer or CRT__SehLookupAndInvokeScopeHandler. Xrefs are CRT__SehDispatchWithScopeTable_Thunk_0055d731, CRT__SehCallback_Call_005602d2, and CRT__SehFilterCppException. Static retail CRT EH evidence only; exact MSVC frame/throw-info layout, handler side effects, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("seh-dispatch", "cxx-eh-magic", "computed-handler")
            ),
            new Spec(
                "0x0056036d",
                "CRT__SehLookupAndInvokeScopeHandler",
                new String[] {},
                "int CRT__SehLookupAndInvokeScopeHandler(void)",
                "Wave881 static read-back: CRT C++ EH scope-table search and handler-dispatch helper. It validates the current state against function metadata, recognizes C++ EH records with code 0xe06d7363 and magic 0x19930520, consults TLS catch-context fields via CRT__GetOrInitThreadLocalRecord, obtains try-block ranges through CRT__GetRangeOfTryBlocksForState, scans handler descriptors with CRT__TypeMatchForCatch, and calls CRT__SehUnwindAndResumeSearch on a matched handler. No-match paths either call CRT__ValidateCatchHandlersForThrow or tail into CDXTexture__InvokeTlsCleanupCallbackAndFinalize depending on cleanup mode. Static retail CRT EH evidence only; exact MSVC scope-table/catch metadata layout, language edge-case behavior, BEA patching, and rebuild parity remain unproven.",
                tags("scope-table-search", "catch-handler-dispatch", "tls-catch-context")
            ),
            new Spec(
                "0x00560520",
                "CRT__ValidateCatchHandlersForThrow",
                new String[] {},
                "int CRT__ValidateCatchHandlersForThrow(void)",
                "Wave881 static read-back: CRT throw-side catch-handler validator. It first checks the TLS exception-translator slot at +0x68 and returns if CRT__CallExceptionTranslator handles the throw, then gets the try-block range for the current state, walks candidate handler descriptors, filters handlers whose descriptor flag byte at +0x08 is set, and invokes CRT__SehUnwindAndResumeSearch for eligible handlers. Static retail CRT EH evidence only; exact translator contract, handler descriptor schema, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("throw-validator", "exception-translator", "catch-handler-scan")
            ),
            new Spec(
                "0x005606c5",
                "CRT__SehUnwindAndResumeSearch",
                new String[] {},
                "int CRT__SehUnwindAndResumeSearch(void)",
                "Wave881 static read-back: CRT matched-handler transfer helper. When catch-object metadata is present it calls CRT__BuildCatchObject, selects the unwind target frame, calls CRT__SehRtlUnwindAndRestoreFrame, runs CRT__SehUnwindToTargetState, advances the frame state to the handler end state plus one, calls CRT__CallCatchBlock, and if a continuation target is returned calls CRT__SehPopExceptionFrameAndJump. Static retail CRT EH evidence only; exact frame layout, non-local jump behavior, catch object lifetime, BEA patching, and rebuild parity remain unproven.",
                tags("matched-handler-transfer", "catch-object", "rtl-unwind")
            ),
            new Spec(
                "0x0056080d",
                "CRT__CleanupCatchContext",
                new String[] {},
                "void CRT__CleanupCatchContext(void)",
                "Wave881 static read-back: compiler-generated CRT catch-context cleanup thunk with hidden EBP/ESI/EDI context. It restores a saved value into ESI-0x04, restores TLS catch-context fields at offsets +0x6c and +0x70 through CRT__GetOrInitThreadLocalRecord, then for C++ EH records with code 0xe06d7363, params value 3, magic 0x19930520, a clear local flag, and a non-null catch object, calls __abnormal_termination and CRT__DestroyCatchObject. Static retail CRT EH cleanup evidence only; exact parent scope, hidden-register ABI, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("catch-context-cleanup", "hidden-register-context", "abnormal-termination")
            )
        };

        Stats stats = new Stats();
        println("ApplyCrtSehTailWave881 mode=" + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave881 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }
}
