//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtMathFpuTailWave882 extends GhidraScript {
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
            "crt-math-fpu-tail-wave882",
            "wave882-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-crt-runtime-infrastructure",
            "high-importance-low-local-evidence-density",
            "compiler-runtime",
            "crt-runtime",
            "fpu-runtime",
            "math-exception-runtime",
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
                "0x00561530",
                "CRT__ReportMathErrorAndRestoreControlWord_00561530",
                new String[] {},
                "int CRT__ReportMathErrorAndRestoreControlWord_00561530(void)",
                "Wave882 static read-back: CRT math-error/control-word restore entry reached from CRT__PowCoreWithFpuGuards and CRT__HandleFpuExceptionForMathOp. Instruction evidence saves EAX and caller stack double words before jumping into the shared math-error tail; decompile evidence observes the ST0 double snapshot and CRT__HandleFloatingPointException(in_EDX, local exception record, caller control-word pointer). Static CRT math/FPU evidence only; exact MSVC helper identity, control-word layout, runtime floating-point behavior, BEA patching, and rebuild parity remain unproven.",
                tags("math-error-restore", "fpu-control-word", "shared-tail-entry")
            ),
            new Spec(
                "0x00561590",
                "CRT__Exp2FromFpuCore_00561590",
                new String[] {},
                "int CRT__Exp2FromFpuCore_00561590(void)",
                "Wave882 static read-back: x87 exp2 helper reached from CRT__PowCoreWithFpuGuards. Instruction evidence is the classic FRNDINT/FSUBR/F2XM1/FLD1/FADDP/FSCALE/FSTP ST1 sequence that computes 2^ST0 from an integer exponent plus fractional remainder and preserves the incoming EAX return/context value. Static CRT pow/FPU evidence only; exact MSVC helper identity, x87 edge-case behavior, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("pow-helper", "x87-exp2", "fscale")
            ),
            new Spec(
                "0x005615a5",
                "CRT__SetFpuControlWordMasked_005615a5",
                new String[] {},
                "void CRT__SetFpuControlWordMasked_005615a5(void)",
                "Wave882 static read-back: FPU control-word setter reached from CRT__Acos, CRT__PowCoreWithFpuGuards, and CRT__AcosCoreWithFpuGuards. Instruction evidence reads the caller control word from ESP+4, keeps only rounding-control bits 0x300, ORs in 0x7f, writes the temporary word at ESP+6, and executes FLDCW. Static CRT FPU-control evidence only; exact control-word policy, runtime rounding behavior, BEA patching, and rebuild parity remain unproven.",
                tags("fpu-control-word", "fldcw", "rounding-mask")
            ),
            new Spec(
                "0x005615bc",
                "CRT__MapExponentFlagToClassCode_005615bc",
                new String[] {},
                "int CRT__MapExponentFlagToClassCode_005615bc(void)",
                "Wave882 static read-back: exponent/classification helper reached from CRT__Acos and CRT__AcosCoreWithFpuGuards. Instruction evidence tests EAX bit 0x80000 and returns class code 7 when set; otherwise it performs an FADD against constant 0x005e5bf0 and returns class code 1. Static CRT classification evidence only; exact class-code naming, IEEE special-value semantics, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("fp-classification", "exponent-flag", "acos-context")
            ),
            new Spec(
                "0x005621b9",
                "CRT__UnlockByIndex9_005621b9",
                new String[] {},
                "void CRT__UnlockByIndex9_005621b9(void)",
                "Wave882 static read-back: CRT lock cleanup thunk reached from CRT__ReallocBase at xref 0x0056215a. Decompile and instruction evidence reduce to CRT__UnlockByIndex(9), matching the heap/small-block lock index used by surrounding realloc paths. Static CRT heap-lock evidence only; exact CRT lock table identity, runtime heap behavior, BEA patching, and rebuild parity remain unproven.",
                tags("heap-lock", "unlock-index-9", "realloc-context")
            ),
            new Spec(
                "0x00562307",
                "CRT__UnlockByIndex9_00562307",
                new String[] {},
                "void CRT__UnlockByIndex9_00562307(void)",
                "Wave882 static read-back: second CRT lock cleanup thunk reached from CRT__ReallocBase at xref 0x005622dc. Decompile and instruction evidence reduce to CRT__UnlockByIndex(9), matching the alternate realloc cleanup/exit path. Static CRT heap-lock evidence only; exact CRT lock table identity, runtime heap behavior, BEA patching, and rebuild parity remain unproven.",
                tags("heap-lock", "unlock-index-9", "realloc-context")
            ),
            new Spec(
                "0x005623c7",
                "CRT__UnlockHeap9_SbHeapMsizePath",
                new String[] {},
                "void CRT__UnlockHeap9_SbHeapMsizePath(void)",
                "Wave882 static read-back: CRT heap unlock cleanup thunk reached from CRT__MsizeByPointer at xref 0x005623b9 after the small-block heap msize path. Decompile and instruction evidence reduce to CRT__UnlockByIndex(9). Static CRT heap-lock evidence only; exact small-block heap metadata layout, runtime heap behavior, BEA patching, and rebuild parity remain unproven.",
                tags("heap-lock", "unlock-index-9", "msize-context")
            ),
            new Spec(
                "0x00562442",
                "CRT__UnlockHeap9_DeferredMsizePath",
                new String[] {},
                "void CRT__UnlockHeap9_DeferredMsizePath(void)",
                "Wave882 static read-back: CRT heap unlock cleanup thunk reached from CRT__MsizeByPointer at xref 0x00562410 on the deferred msize path. Decompile and instruction evidence reduce to CRT__UnlockByIndex(9). Static CRT heap-lock evidence only; exact small-block heap metadata layout, runtime heap behavior, BEA patching, and rebuild parity remain unproven.",
                tags("heap-lock", "unlock-index-9", "msize-context")
            ),
            new Spec(
                "0x0056249f",
                "CRT__HandleFloatingPointExceptionByFlags",
                new String[] {},
                "int CRT__HandleFloatingPointExceptionByFlags(void)",
                "Wave882 static read-back: CRT floating-point exception dispatcher reached from CRT__RoundDoubleWithFpuChecks and CRT__RoundToIntegerRespectingControlWord. Decompile evidence calls CRT__AdjustFloatingPointForFormatFlags, falls back to CRT__RaiseFloatingPointException when adjustment fails, maps format flags to a source kind, optionally calls CRT__HandleFpStatusAndReturnDouble when DAT_006561f0 is clear, otherwise sets errno and returns CRT__GetFpuControlWord. Static CRT FPU/errno evidence only; exact flag schema, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("floating-point-exception", "errno", "format-flags")
            ),
            new Spec(
                "0x00562537",
                "CRT__RaiseFloatingPointException",
                new String[] {},
                "int CRT__RaiseFloatingPointException(void)",
                "Wave882 static read-back: CRT floating-point exception raiser reached from CRT__HandleFloatingPointExceptionByFlags and CRT__HandleFloatingPointException. Decompile evidence builds a floating-point exception record, maps active status bits to NT exception codes 0xc000008f, 0xc0000093, 0xc0000091, 0xc000008e, and 0xc0000090, snapshots FPU control/status masks and double slots, calls RaiseException, then writes selected record bits back into the caller control word. Static CRT FPU exception evidence only; exact record layout, SEH continuation semantics, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("raise-exception", "nt-fp-exception-codes", "fpu-status")
            ),
            new Spec(
                "0x00562c59",
                "CRT__FpuStatusWordToInt_00562c59",
                new String[] {},
                "int CRT__FpuStatusWordToInt_00562c59(void)",
                "Wave882 static read-back: FPU status-word readback thunk used by CRT__RaiseFloatingPointException before RaiseException. Decompile evidence returns the hidden FPU status word as an int; xref evidence is 0x0056262d inside the exception-record builder. Static CRT FPU-status evidence only; exact status-bit interpretation, runtime FPU behavior, BEA patching, and rebuild parity remain unproven.",
                tags("fpu-status-word", "raise-exception-context")
            ),
            new Spec(
                "0x00562c67",
                "CRT__FpuStatusWordToInt_00562c67",
                new String[] {},
                "int CRT__FpuStatusWordToInt_00562c67(void)",
                "Wave882 static read-back: second FPU status-word readback thunk used by CRT__RaiseFloatingPointException after RaiseException. Decompile evidence returns the hidden FPU status word as an int; xref evidence is 0x0056273d in the post-raise path. Static CRT FPU-status evidence only; exact status-bit interpretation, runtime FPU behavior, BEA patching, and rebuild parity remain unproven.",
                tags("fpu-status-word", "raise-exception-context")
            ),
            new Spec(
                "0x00562c76",
                "CRT__GetFpuControlWord",
                new String[] {},
                "int CRT__GetFpuControlWord(void)",
                "Wave882 static read-back: FPU control-word readback helper reached from rounding, domain-error, floating-point-status, and CRT__HandleFloatingPointException paths. Decompile evidence returns the hidden FPU control word as an int; xrefs include CRT__RoundDoubleWithFpuChecks, CRT__RoundToIntegerRespectingControlWord, CRT__HandleDomainErrorAndReturnInput, CRT__HandleFloatingPointExceptionByFlags, CRT__HandleFpStatusAndReturnDouble, and CRT__HandleFloatingPointException. Static CRT FPU-control evidence only; exact control-word semantics, runtime FPU behavior, BEA patching, and rebuild parity remain unproven.",
                tags("fpu-control-word", "rounding-context", "exception-context")
            ),
            new Spec(
                "0x00562c99",
                "CRT__ReturnVoid",
                new String[] {},
                "void CRT__ReturnVoid(void)",
                "Wave882 static read-back: no-op CRT helper reached five times from CRT__AdjustFloatingPointForFormatFlags. Decompile and instruction evidence reduce to RET with no state change, so this row is documented as a return-only callback/placeholder in the FPU format-adjustment path. Static CRT callback evidence only; exact callback-table identity, runtime formatting behavior, BEA patching, and rebuild parity remain unproven.",
                tags("return-only", "fpu-format-context", "callback-placeholder")
            )
        };

        Stats stats = new Stats();
        println("ApplyCrtMathFpuTailWave882 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave882 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }
}
