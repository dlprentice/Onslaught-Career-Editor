//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyStringScratchWave547 extends GhidraScript {
    private static final String CALLING_CONVENTION = "__cdecl";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "string-scratch-wave547",
        "retail-binary-evidence",
        "name-corrected",
        "signature-corrected",
        "comment-hardened"
    };

    private static class Spec {
        final String address;
        final String name;
        final String counter;
        final String buffer;
        final String xrefSummary;

        Spec(String address, String name, String counter, String buffer, String xrefSummary) {
            this.address = address;
            this.name = name;
            this.counter = counter;
            this.buffer = buffer;
            this.xrefSummary = xrefSummary;
        }

        String comment() {
            return "Wave547 string-scratch signature/comment hardening: cdecl helper takes source_string " +
                "on the stack, strlen-scans for the terminating NUL, advances rotating slot counter " +
                counter + " modulo 4, copies the bytes into 4 KiB scratch bank " + buffer +
                " plus slot*0x1000, writes the NUL terminator, and returns the selected bank pointer. " +
                xrefSummary + " Static retail evidence only; exact source identity, caller lifetime " +
                "contract, overlong-string behavior, runtime formatting behavior, and rebuild parity remain unproven.";
        }
    }

    private static final Spec[] SPECS = new Spec[] {
        new Spec(
            "0x004f7c70",
            "StringScratch__CopyToRotating4KBufferA",
            "0x00854d44",
            "0x00848d40",
            "Xrefs span platform font loading, D3D device setup, game draw text, WAV open, LTShell construction, texture loading/dumping, and frontend world-file enumeration."
        ),
        new Spec(
            "0x004f7cd0",
            "StringScratch__CopyToRotating4KBufferB",
            "0x00854d48",
            "0x00844d40",
            "Observed xrefs are CDXBitmapFont named-font initialization and frontend world-file enumeration."
        )
    };

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

    private Address toAddress(Spec spec) {
        Address result = toAddr(spec.address);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + spec.address);
        }
        return result;
    }

    private Function targetFunction(Spec spec) {
        Address address = toAddress(spec);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, DataType charPtr, ParameterImpl sourceStringParam) {
        if (!CALLING_CONVENTION.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), charPtr)) {
            return false;
        }
        if (fn.getParameterCount() != 1) {
            return false;
        }
        Parameter actual = fn.getParameter(0);
        return actual.getName().equals(sourceStringParam.getName()) &&
            sameDataType(actual.getDataType(), sourceStringParam.getDataType());
    }

    private boolean hasAllTags(Function fn) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : TAGS) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec, DataType charPtr, ParameterImpl sourceStringParam) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, charPtr, sourceStringParam)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment())) {
            return true;
        }
        return !hasAllTags(fn);
    }

    private String expectedSignature(Spec spec, DataType charPtr, ParameterImpl sourceStringParam) {
        return charPtr.getDisplayName() + " " + CALLING_CONVENTION + " " + spec.name + "(" +
            sourceStringParam.getDataType().getDisplayName() + " " + sourceStringParam.getName() + ")";
    }

    private void verifyReadBack(Spec spec, DataType charPtr, ParameterImpl sourceStringParam) throws Exception {
        Function fn = targetFunction(spec);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, charPtr, sourceStringParam)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec, charPtr, sourceStringParam) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment())) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType charPtr = new PointerDataType(CharDataType.dataType);
        ParameterImpl sourceStringParam = new ParameterImpl("source_string", charPtr, currentProgram);
        Stats stats = new Stats();

        for (Spec spec : SPECS) {
            Function fn = targetFunction(spec);
            if (fn == null) {
                println("MISSING: " + spec.address);
                stats.missing++;
                continue;
            }

            boolean rename = !fn.getName().equals(spec.name);
            boolean update = needsUpdate(fn, spec, charPtr, sourceStringParam);
            if (dryRun) {
                println((update ? "DRY: " : "SKIP: ") + spec.address + " " + expectedSignature(spec, charPtr, sourceStringParam));
                stats.skipped++;
                if (rename) {
                    stats.wouldRename++;
                }
                continue;
            }

            if (!update) {
                println("SKIP: " + spec.address + " already current");
                stats.skipped++;
                continue;
            }

            if (rename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(CALLING_CONVENTION);
            fn.setReturnType(charPtr, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                sourceStringParam
            );
            fn.setComment(spec.comment());
            for (String tag : TAGS) {
                fn.addTag(tag);
            }
            verifyReadBack(spec, charPtr, sourceStringParam);
            println("OK: " + spec.address + " " + expectedSignature(spec, charPtr, sourceStringParam));
            stats.updated++;
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
