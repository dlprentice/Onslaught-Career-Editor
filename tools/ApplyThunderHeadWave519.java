//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
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

public class ApplyThunderHeadWave519 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final boolean createIfMissing;
        final boolean renameAllowed;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags,
                boolean createIfMissing, boolean renameAllowed) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.createIfMissing = createIfMissing;
            this.renameAllowed = renameAllowed;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int created = 0;
        int wouldCreate = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "thunderhead-wave519",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
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
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
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

    private Function createFunctionAt(Spec spec, Address address) throws Exception {
        Function containing = getFunctionContaining(address);
        if (containing != null && !containing.getEntryPoint().equals(address)) {
            throw new IllegalStateException(
                "Address " + spec.address + " is inside existing function " + containing.getName());
        }
        Function fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = getFunctionAt(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        return fn;
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function fn = functionAtEntry(spec.address);
        boolean createdNow = false;

        if (fn == null) {
            if (!spec.createIfMissing) {
                println("MISSING: " + spec.address);
                stats.missing++;
                return;
            }
            if (dryRun) {
                println("DRY: " + spec.address + " <missing> -> create " + expectedSignature(spec));
                stats.wouldCreate++;
                stats.skipped++;
                return;
            }
            fn = createFunctionAt(spec, address);
            createdNow = true;
            stats.created++;
        }

        if (!fn.getName().equals(spec.name)) {
            if (!spec.renameAllowed) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }
            if (dryRun) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.wouldRename++;
                stats.skipped++;
                return;
            }
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }

        boolean updateNeeded = createdNow || needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            stats.skipped++;
            return;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec) +
            (createdNow ? " created" : ""));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004f4730",
                "CThunderHead__CreateLegMotion",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init_context", voidPtr)},
                "Wave519 ThunderHead signature/comment hardening: CThunderHead vtable 0x005e11b0 slot 1 points here. The body looks up the LegMotion animation through this+0x30, allocates a 0xf0-byte motion-controller object from the ThunderHead.cpp line 0x20 debug path, installs the 0x005df890 CMCThunderHead/CMCMech-family vtable, stores the result at this+0x70, and seeds CMCMech parameters from init_context+0x3bc fields plus 3.4/0.99 constants. Static retail evidence only; exact source body, concrete layouts, runtime leg motion, BEA patching, and rebuild parity remain unproven.",
                tags("thunderhead", "factory", "leg-motion", "motion-controller", "vtable-slot"),
                false,
                false
            ),
            new Spec(
                "0x004f4830",
                "CThunderHead__CreateWarspite",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init_context", voidPtr)},
                "Wave519 ThunderHead signature/comment hardening: CThunderHead vtable 0x005e11b0 slot 2 points here. RET 0x4 plus ECX/stack use show this and one init_context argument. The body allocates a 0x60-byte pool-0x16 Warspite-style component from the ThunderHead.cpp line 0x2b debug path, calls CWarspite__Init with the allocated object as ECX plus owner/init_context stack arguments, and stores the returned component or NULL at this+0x13c. Static retail evidence only; exact Warspite semantics, concrete layouts, runtime combat AI behavior, BEA patching, and rebuild parity remain unproven.",
                tags("thunderhead", "factory", "warspite-style", "vtable-slot"),
                false,
                false
            ),
            new Spec(
                "0x004f48a0",
                "CThunderHead__CreateGuide",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave519 ThunderHead signature/comment hardening: CThunderHead vtable 0x005e11b0 slot 3 points here. The body allocates a 0x30-byte pool-0x17 CThunderheadGuide object from the ThunderHead.cpp line 0x31 debug path, copies four owner vector/state dwords from this+0x1c into stack arguments, calls CThunderheadGuide__Init with the owner and copied dwords, and stores the returned guide or NULL at this+0x208. Static retail evidence only; exact guide contract, concrete layouts, runtime targeting behavior, BEA patching, and rebuild parity remain unproven.",
                tags("thunderhead", "factory", "guide", "vtable-slot"),
                false,
                false
            ),
            new Spec(
                "0x004f4e00",
                "CThunderheadGuide__Init",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_unit", voidPtr),
                    param("copied_state_0", intType),
                    param("copied_state_4", intType),
                    param("copied_state_8", intType),
                    param("copied_state_c", intType)
                },
                "Wave519 Thunderhead guide signature/name/comment hardening: CThunderHead__CreateGuide calls this with the allocated guide as ECX, the owner unit, and four dwords copied from owner+0x1c. RET 0x14 confirms five stack arguments. The body calls CGuide__ctor_base(owner_unit), installs vtable 0x005df8d4, writes the four copied state dwords to this+0x20..this+0x2c, and returns this. Static retail evidence only; exact copied-state meaning, guide vtable contract, runtime targeting behavior, BEA patching, and rebuild parity remain unproven.",
                tags("thunderhead", "guide", "init", "signature-corrected", "name-corrected"),
                false,
                true
            ),
            new Spec(
                "0x004f4e40",
                "CThunderheadGuide__VFunc_03_004f4e40",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave519 recovered function boundary: CThunderheadGuide vtable 0x005df8d4 slot 3 points to 0x004f4e40, which starts a standalone ECX-based body and returns at 0x004f51b4 before the following data-initializer block. Current instruction evidence shows an owner flag gate, owner-relative vector/state updates, and a fallback owner virtual dispatch through slot +0x100. Static retail evidence only; exact virtual name, concrete guide/owner layouts, runtime targeting/fire behavior, BEA patching, and rebuild parity remain unproven.",
                tags("thunderhead", "guide", "function-boundary", "vtable-slot", "boundary-recovered"),
                true,
                false
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
