//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyDecodeAllocatorHeadWave711 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "decode-allocator-head-wave711",
            "wave711-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "decode-allocator-head"
        }, extras);
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
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
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
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
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);

            stats.updated++;
            println("OK: " + spec.address + " " + expectedSignature(spec));
            Thread.sleep(75);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x0059bae0",
                "CDXTexture__AllocFromBank_SplitBlock",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("allocator_owner", voidPtr),
                    param("bank_index", intType),
                    param("requested_size_bytes", uintType)
                },
                "Wave711 static read-back: RET 0xc, data installation from 0x0059c548, and direct callers under the row/job allocation helpers show allocator owner, bank index, and requested-byte arguments. The helper caps oversized requests, aligns the request to 8 bytes, validates bank 0/1, searches the bank split-block list at allocator state +0x34, falls back to aligned allocation, accounts bytes at +0x4c, then returns a payload pointer after the 0x10-byte block header. Static metadata only; CDXTexture__AllocAligned16 still decompiles through extraout_EAX here, and exact allocator-state layout, failure callback semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("split-bank-allocator", "ret-0xc", "helper-return-abi-open", "tranche-head")
            ),
            new Spec(
                "0x0059bc10",
                "CDXTexture__AllocLinearBlockAndTrack",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("allocator_owner", voidPtr),
                    param("bank_index", intType),
                    param("requested_size_bytes", uintType)
                },
                "Wave711 static read-back: RET 0xc, data installation from 0x0059c54e, and calls from the row allocation helpers show allocator owner, bank index, and requested-byte arguments. The helper caps oversized requests, aligns to 8 bytes, validates bank 0/1, allocates requested+0x10 bytes, links the block into allocator state +0x3c for the selected bank, tracks total bytes at +0x4c, and returns the payload after the header. Static metadata only; CDXTexture__AllocAligned16 still decompiles through extraout_EAX here, and exact allocator-state layout, failure callback semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("linear-bank-allocator", "ret-0xc", "helper-return-abi-open")
            ),
            new Spec(
                "0x0059bcc0",
                "CDXTexture__AllocRowPointerTableAndRows",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("allocator_owner", voidPtr),
                    param("bank_index", intType),
                    param("row_stride_bytes", uintType),
                    param("row_count", uintType)
                },
                "Wave711 static read-back: RET 0x10, data installation from 0x0059c555, and no-function caller evidence at 0x0059bfc8 show allocator owner, bank index, row stride, and row count arguments. The helper guards the row-stride product against the 0x3b9ac9f0 cap, stores the batch row count at allocator state +0x50, allocates a pointer table through the split-block path, allocates row batches through the linear path, and fills the row pointer table. Static metadata only; exact row-table ownership, image component semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("row-pointer-table", "linear-row-batches", "ret-0x10")
            ),
            new Spec(
                "0x0059bd60",
                "CDXTexture__AllocMcuRowPointerTableAndRows",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("allocator_owner", voidPtr),
                    param("bank_index", intType),
                    param("mcu_units_per_row", intType),
                    param("row_count", uintType)
                },
                "Wave711 static read-back: RET 0x10, data installation from 0x0059c55c, and no-function caller evidence at 0x0059c03e show allocator owner, bank index, MCU units per row, and row count arguments. The helper uses mcu_units_per_row*0x80 as the row stride, guards the product against the 0x3b9ac9f0 cap, stores the batch row count at allocator state +0x50, allocates the pointer table through the split-block path, allocates row batches through the linear path, and fills the row pointer table. Static metadata only; exact MCU/component semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("mcu-row-pointer-table", "linear-row-batches", "ret-0x10")
            ),
            new Spec(
                "0x0059c3f0",
                "CDXTexture__ReleaseDecodeBankLists",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("allocator_owner", voidPtr),
                    param("bank_index", intType)
                },
                "Wave711 static read-back: RET 0x8, data installation from 0x0059c586, and caller evidence at 0x0059c4e2 show allocator owner and bank index arguments. The helper validates bank 0/1, runs outstanding descriptor callbacks when releasing bank 1, clears descriptor heads at allocator state +0x44/+0x48, drains the linear tracked-block list at +0x3c and split-block list at +0x34 for the selected bank, frees aligned blocks, and subtracts tracked byte totals at +0x4c. Static metadata only; exact callback contract, allocator-state layout, ownership semantics, BEA patching, and rebuild parity remain unproven.",
                tags("decode-bank-release", "tracked-list-drain", "ret-0x8")
            ),
            new Spec(
                "0x0059c510",
                "CDXTexture__InitDecodeAllocatorVtable",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("allocator_owner", voidPtr)
                },
                "Wave711 static read-back: RET 0x4 and calls from CDXTexture__InitJpegDecodeState and CTexture__ResetDecodeContextWithDefaults show one allocator-owner argument. The helper allocates a 0x54 decode allocator state, installs split/linear/row/MCU row/job/block/release slots, records the default decode budget and 1000000000-byte cap, clears the bank lists, and stores the allocator state at owner +4. Static metadata only; CDXTexture__AllocAligned16 still decompiles through extraout_EAX and a stale no-op helper label on the null path remains unproven, so exact allocator-state layout, helper ABI, runtime texture behavior, BEA patching, and rebuild parity remain open.",
                tags("allocator-vtable-init", "decode-budget", "helper-return-abi-open", "ret-0x4")
            ),
            new Spec(
                "0x0059c5d0",
                "CDXTexture__PumpDecodeAllocatorAndSetStage",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                "Wave711 static read-back: RET 0x4 and calls from the JPEG/decode state-machine helpers show one decode-state argument. When the allocator pointer at +4 is present, the helper invokes allocator vtable slot +0x24 with bank 1, then sets stage +0x14 to 200 and clears +0x134 if +0x10 is nonzero, otherwise it sets stage +0x14 to 100. Static metadata only; exact decode-state layout, stage enum semantics, allocator release callback contract, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("allocator-stage-pump", "decode-stage", "ret-0x4", "tranche-tail")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        println("ApplyDecodeAllocatorHeadWave711 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave711 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
