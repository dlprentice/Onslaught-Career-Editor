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

public class ApplyGillMStartStateVectorWave409 extends GhidraScript {
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

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> current = tagNames(fn);
        for (String tag : tags) {
            if (!current.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private void runSpec(boolean dryRun, Stats stats) throws Exception {
        String address = "0x0047a160";
        String oldName = "CExplosionInitThing__StartState1WithStoredMotionVector";
        String expectedName = "CGillM__StartState1WithStoredMotionVector";
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        ParameterImpl[] params = new ParameterImpl[] {
            param("this", voidPtr)
        };
        String expectedSignature = "void __thiscall CGillM__StartState1WithStoredMotionVector(void * this)";
        String comment =
            "Wave409 owner/signature correction from the older CExplosionInitThing label: CGillM RTTI vtable " +
            "0x005e0b30 slot 100 points here. The body skips when state field +0x244 is already 1 or 2, " +
            "copies the stored four-dword motion vector at +0x278 into a virtual dispatch at vtable +0xf4 " +
            "with a zero flag, then sets +0x244 to 1. Static retail evidence only; exact source virtual name, " +
            "concrete CGillM layout, runtime movement behavior, and rebuild parity remain unproven.";
        String[] tags = new String[] {
            "static-reaudit",
            "gillm-start-state-vector-wave409",
            "cgillm",
            "vtable-slot",
            "state-transition",
            "motion-vector",
            "owner-corrected",
            "signature-hardened",
            "comment-hardened",
            "retail-binary-evidence"
        };

        Function fn = functionAtEntry(address);
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + address + " Function not found");
            return;
        }
        if (!fn.getName().equals(oldName) && !fn.getName().equals(expectedName)) {
            throw new IllegalStateException("Unexpected function name at " + address + ": " + fn.getName());
        }

        boolean needsRename = !fn.getName().equals(expectedName);
        boolean needsUpdate = needsRename
            || !fn.getSignature().toString().equals(expectedSignature)
            || fn.getComment() == null
            || !fn.getComment().contains("CGillM RTTI vtable 0x005e0b30 slot 100")
            || !hasAllTags(fn, tags);

        if (dryRun) {
            if (needsRename) {
                stats.wouldRename++;
            }
            println("DRY: " + address + " " + fn.getName() + " " + fn.getSignature() + " -> " + expectedSignature);
            stats.skipped++;
            return;
        }

        if (needsRename) {
            fn.setName(expectedName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsUpdate) {
            fn.setCallingConvention("__thiscall");
            fn.setReturnType(voidType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                params
            );
            fn.setComment(comment);
            for (String tag : tags) {
                fn.addTag(tag);
            }
        }

        Function readBack = functionAtEntry(address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + address);
        }
        if (!readBack.getName().equals(expectedName)) {
            throw new IllegalStateException("Read-back name mismatch at " + address + ": " + readBack.getName());
        }
        if (!readBack.getSignature().toString().equals(expectedSignature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + address + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.contains("CGillM RTTI vtable 0x005e0b30 slot 100")) {
            throw new IllegalStateException("Read-back comment mismatch at " + address);
        }
        Set<String> readTags = tagNames(readBack);
        for (String tag : tags) {
            if (!readTags.contains(tag)) {
                throw new IllegalStateException("Missing read-back tag at " + address + ": " + tag);
            }
        }

        stats.updated++;
        println("UPDATED: " + address + " " + readBack.getSignature());
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = true;
        String[] args = getScriptArgs();
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        try {
            runSpec(dryRun, stats);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + ex.getMessage());
        }
        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave409 had missing/bad targets");
        }
    }
}
