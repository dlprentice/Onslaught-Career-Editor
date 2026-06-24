//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyFEPMixerMapWave566 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String previousName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String previousName, String callingConvention,
                DataType returnType, ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousName = previousName;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "fep-mixermap-wave566",
            "retail-binary-evidence",
            "no-source-file",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.params.length) {
            return false;
        }
        for (int i = 0; i < spec.params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.params[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
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
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
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
            if (!fn.getName().equals(spec.name) && !fn.getName().equals(spec.previousName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (dryRun) {
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (updateNeeded) {
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.name + " " + expectedSignature(spec));
                } else {
                    println("SKIP: " + spec.address + " already matches " + spec.name);
                }
                stats.skipped++;
                return;
            }

            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already matches " + spec.name);
                verifyReadBack(spec);
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("APPLY: " + spec.address + " -> " + spec.name + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = voidPtr();

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005230e0",
                "CFEPWingmen__FindCurrentLevelRecord",
                "CVBufTexture__FindListEntryByGlobalId89D94C",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave566 owner/signature/comment correction: supersedes the stale CVBufTexture owner label. Callers in the deferred CFEPWingmen no-function range pass &DAT_0089da44 in ECX; the body seeds cursor this+0x30 from list head this+0x28, follows node+0x04 links, and returns the first record whose id dword matches DAT_0089d94c or null. This aligns with Wave565 CFEPWingmen__Load appending 0x24 records to this+0x28. Static retail-binary evidence only; exact FEPWingmen boundaries, record field names, runtime wingman menu behavior, BEA patching, and rebuild parity remain unproven.",
                tags("fep-wingmen", "current-level-record", "owner-corrected", "signature-corrected", "renamed")
            ),
            new Spec(
                "0x00523190",
                "CMixerMap__InitSlot",
                "CMixerMap__InitSlot",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("chunk_reader", voidPtr) },
                "Wave566 signature/comment hardening: RET 0x4 plus prologue MOV ESI,ECX and caller 0x0052337f/0x00523381 prove a slot receiver plus one chunk_reader argument. The body consumes two chunk-reader tags, reads a 0x14-byte slot record, and when slot+0x04 is nonzero consumes another tag, allocates slot_count*0x51 bytes from mixermap.cpp line 0x86, stores it at slot+0x04, and reads that payload. Static retail evidence only; mixer slot field semantics, runtime audio behavior, exact source identity, BEA patching, and rebuild parity remain unproven.",
                tags("mixermap", "chunk-reader", "slot-init", "signature-corrected")
            ),
            new Spec(
                "0x00523210",
                "CMixerMap__DestroySlot",
                "CMixerMap__DestroySlot",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave566 signature/comment hardening: ECX-only slot cleanup used directly and as an array destructor callback. The body frees the per-slot buffer pointer at this+0x04 through CDXMemoryManager__Free and clears that pointer. Static retail evidence only; slot payload semantics, runtime audio behavior, exact source identity, BEA patching, and rebuild parity remain unproven.",
                tags("mixermap", "slot-cleanup", "destructor-callback", "signature-corrected")
            ),
            new Spec(
                "0x00523230",
                "CMixerMap__Destroy",
                "CMixerMap__Destroy",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave566 signature/comment hardening: ECX-only map cleanup called from CHeightField__ShutdownAndDestroyMixerMap. The body frees each non-null slot buffer across the 0x14000-byte slot array at 0x14-byte stride, invokes CDXLandscape__DestroyArrayWithCallback with CMixerMap__DestroySlot, frees the array header at slot_array-4, clears this+0x00, then frees and clears the secondary buffer at this+0x04. Static retail evidence only; runtime terrain/mixer/audio behavior, exact source identity, BEA patching, and rebuild parity remain unproven.",
                tags("mixermap", "cleanup", "heightfield-caller", "signature-corrected")
            ),
            new Spec(
                "0x005232b0",
                "CMixerMap__Init",
                "CMixerMap__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("chunk_reader", voidPtr) },
                "Wave566 signature/comment hardening: RET 0x4 and CHeightField__DeserializeMapAndInitResources callsite prove a chunk_reader stack argument. The body destroys an existing slot array, allocates 0x14004 bytes for 0x1000 0x14-byte slots from mixermap.cpp line 0xf6, initializes them through the vector-constructor iterator with CMixerMap__DestroySlot cleanup, allocates a 0x40000 secondary buffer from line 0xf7, consumes a chunk tag, loops through the 0x1000 slots calling CMixerMap__InitSlot(slot,chunk_reader), then consumes another tag and reads the 0x40000 payload. Static retail evidence only; runtime MAP/mixer/audio behavior, exact source identity, BEA patching, and rebuild parity remain unproven.",
                tags("mixermap", "chunk-reader", "heightfield-caller", "slot-array", "signature-corrected")
            )
        };

        Stats stats = new Stats();
        println("ApplyFEPMixerMapWave566 mode=" + (dryRun ? "dry" : "apply") + " targets=" + specs.length);
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply") +
            " updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave566 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
