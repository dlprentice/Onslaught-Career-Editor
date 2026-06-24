//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyResourceDescriptorCleanupWave982 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String[] previousNames;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String expectedName,
                String[] previousNames,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] params,
                String comment,
                String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.previousNames = previousNames;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.expectedName).append("(");
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName()).append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean nameAllowed(String actualName, Spec spec) {
        if (actualName.equals(spec.expectedName)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (actualName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        return fn.getSignature().toString().equals(expectedSignature(spec));
    }

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            ok = false;
        }
        if (!signatureMatches(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + expectedSignature(spec) + " actual=" + fn.getSignature());
            ok = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            ok = false;
        }
        if (!hasAllTags(fn, spec)) {
            println("BADTAGS: " + spec.address);
            ok = false;
        }
        if (!ok) {
            stats.bad++;
        }
        return ok;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }
        if (!nameAllowed(fn.getName(), spec)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.expectedName);
        boolean needsSignature = !signatureMatches(fn, spec);
        boolean needsCommentOrTags = !spec.comment.equals(fn.getComment()) || !hasAllTags(fn, spec);

        if (needsRename) {
            stats.wouldRename++;
        }
        if (needsSignature) {
            stats.signatureUpdated++;
        }
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }
        if (!needsRename && !needsSignature && !needsCommentOrTags) {
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec)
                + " needsRename=" + needsRename
                + " needsSignature=" + needsSignature
                + " needsCommentOrTags=" + needsCommentOrTags);
            stats.skipped++;
            return;
        }

        if (needsRename) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsSignature) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.params);
        }
        if (needsCommentOrTags) {
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
        }
        if (readBackMatches(fn, spec, stats)) {
            println("APPLY_OK: " + spec.address + " " + spec.expectedName + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        Spec spec = new Spec(
            "0x00403ff0",
            "CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk",
            new String[] {
                "CDXLandscape__DestroyResourceDescriptorArray_Thunk"
            },
            "__thiscall",
            VoidDataType.dataType,
            new ParameterImpl[] {
                param("this", voidPtr)
            },
            "Wave982 static re-audit correction: neutral resource-descriptor cleanup thunk name replaces the older CDXLandscape owner label, which is not supported by the broad unwind/context xrefs. Static evidence: the body advances ECX by 8, passes element size 0x41c and count 1, then calls CRT__EhVectorDestructorIterator_WithUnwind with CResourceDescriptor__dtor; CResourceDescriptorTable__ctor is the inverse constructor at this+0x08. Static retail Ghidra evidence only; exact source identity, concrete descriptor-table layout, runtime unwind/cleanup behavior, BEA patching, and rebuild parity remain unproven.",
            new String[] {
                "static-reaudit",
                "resource-descriptor-cleanup-wave982",
                "wave982-readback-verified",
                "retail-binary-evidence",
                "comment-hardened",
                "signature-verified",
                "rename-corrected",
                "resource-descriptor",
                "compiler-unwind"
            }
        );

        Stats stats = new Stats();
        applySpec(spec, dryRun, stats);
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave982 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            currentProgram.flushEvents();
        }
    }
}
