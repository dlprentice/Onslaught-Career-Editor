//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtSehRuntimeHeadWave878 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "crt-seh-runtime-head-wave878",
            "wave878-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-crt-runtime-infrastructure",
            "high-importance-low-local-evidence-density",
            "compiler-runtime",
            "crt-seh",
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
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> readBackTags = tagNames(readBack);
        for (String tag : spec.tags) {
            if (!readBackTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
            }
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
                throw new IllegalStateException("Unexpected function name: " + fn.getName());
            }
            String actualSignature = fn.getSignature().toString();
            if (!actualSignature.equals(spec.signature)) {
                throw new IllegalStateException("Unexpected signature: " + actualSignature);
            }

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already " + spec.signature);
                return;
            }

            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + spec.signature);
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055d731",
                "CRT__SehDispatchWithScopeTable_Thunk_0055d731",
                "int CRT__SehDispatchWithScopeTable_Thunk_0055d731(void)",
                "Wave878 static read-back: CRT/SEH dispatch thunk at the post-Wave877 raw commentless head. The body forwards directly to CRT__SehDispatchWithScopeTable, while xref export shows 500-plus no-function callsites from compiler-generated unwind/scope-table thunks in the 0x005d0f2b-area tail. Static retail compiler-runtime evidence only; exact MSVC helper identity/version, runtime exception behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("seh-scope-dispatch-thunk", "mass-scope-table-xrefs")
            ),
            new Spec(
                "0x0055d767",
                "CRT__SehInvokeCallSettingFrame12",
                "int CRT__SehInvokeCallSettingFrame12(void)",
                "Wave878 static read-back: SEH call-setting-frame wrapper. The body installs CRT__SehCallback_Call_005602d2 in a local registration record, saves/restores ExceptionList, derives a local state from the caller stack, calls __CallSettingFrame_12 with stack-provided frame arguments, and returns the helper result. Xref is CRT__CallCatchBlock at 0x005607bb. Static retail CRT/SEH evidence only; exact hidden ABI, runtime catch/translator behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("call-setting-frame-wrapper", "exception-list", "crt-catch-runtime")
            ),
            new Spec(
                "0x0055d7e0",
                "CRT__CallExceptionTranslator",
                "int CRT__CallExceptionTranslator(void)",
                "Wave878 static read-back: CRT exception-translator wrapper. The body installs CRT__SehFilterCppException in a local exception record, saves/restores ExceptionList, obtains the thread-local record through CRT__GetOrInitThreadLocalRecord, then calls the translator-like callback at TLS/record offset +0x68 with the exception value and stack-local scratch. Xref is CRT__ValidateCatchHandlersForThrow at 0x00560547. Static retail CRT exception evidence only; exact translator prototype, TLS layout, runtime behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("exception-translator", "thread-local-record", "exception-list")
            ),
            new Spec(
                "0x0055da5e",
                "CRT__SehStoreFrameGlobals",
                "void CRT__SehStoreFrameGlobals(void)",
                "Wave878 static read-back: SEH/frame-global store helper. The body records DAT_006532d8 from caller slot EBP+0x08, DAT_006532d4 from EAX, and DAT_006532dc from EBP. Xrefs include _longjmp at 0x005d0621, __local_unwind2 at 0x0055da19, and no-function runtime code at 0x005612f4. Static retail CRT frame-global evidence only; exact NLG/global contract, runtime unwind behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("frame-globals", "longjmp-unwind", "nlg-runtime")
            ),
            new Spec(
                "0x0055da76",
                "CRT__InitRuntimeFromStoredFrameGlobals",
                "void CRT__InitRuntimeFromStoredFrameGlobals(void)",
                "Wave878 static read-back: runtime initialization stub tied to stored frame/global setup. The body calls CRT__InitFloatConversionDispatchTable, probes processor features through CDXTexture__ProbeProcessorFeaturePresentOrFallback, stores the result in DAT_009d08b8, then calls CRT__InitFpuControlWord_0x10000_0x30000. Xrefs include computed call evidence from CFastVB__RunStaticInitRangesWithOptionalCallback and DATA row 0x006532e8. Static retail runtime-init evidence only; exact startup table semantics, CPU feature policy, FPU side effects, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("runtime-init", "fpu-control", "static-init")
            ),
            new Spec(
                "0x0055da8d",
                "CRT__InitFloatConversionDispatchTable",
                "void CRT__InitFloatConversionDispatchTable(void)",
                "Wave878 static read-back: float-conversion dispatch table initializer. The body writes globals at 0x00653658 through 0x0065366c to __cfltcvt, __fassign, CRT__InsertDecimalSeparatorBeforeExponent, and local helper labels 0x00560d84/0x00560dd2. Direct caller is CRT__InitRuntimeFromStoredFrameGlobals. Static retail CRT float-format evidence only; exact table naming/layout, numeric edge behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("float-conversion-dispatch", "numeric-formatting", "runtime-init")
            ),
            new Spec(
                "0x0055db72",
                "CRT__EhVectorDestructorIterator_IfNoException",
                "void CRT__EhVectorDestructorIterator_IfNoException(void)",
                "Wave878 static read-back: EH vector-destructor cleanup helper called by CRT__EhVectorDestructorIterator_WithUnwind at 0x0055db5c. The cleanup path checks the frame-local exception flag at EBP-0x1c and, when clear, calls eh_vector_destructor_iterator with array, element size, count, and destructor callback from caller/frame slots. Static retail C++ runtime cleanup evidence only; exact frame layout, destructor callback ABI, runtime unwind behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("eh-vector-dtor-unwind", "cleanup-helper", "cxx-runtime")
            ),
            new Spec(
                "0x0055dc8a",
                "CRT__EhVectorConstructorIterator_Unwind",
                "void CRT__EhVectorConstructorIterator_Unwind(void)",
                "Wave878 static read-back: EH vector-constructor unwind cleanup helper called by eh_vector_constructor_iterator at 0x0055dc74. The cleanup path checks the frame-local exception flag at EBP-0x20 and, when clear, calls eh_vector_destructor_iterator for the partially constructed element count from EBP-0x1c using the caller array, element size, and destructor callback. Static retail C++ runtime cleanup evidence only; exact frame layout, partial-construction count semantics, runtime unwind behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("eh-vector-ctor-unwind", "cleanup-helper", "cxx-runtime")
            )
        };

        println("MODE: " + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (!dryRun) {
            println("REPORT: Save requested by headless post-script");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave878 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
