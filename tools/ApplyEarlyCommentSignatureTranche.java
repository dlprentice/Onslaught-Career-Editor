//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyEarlyCommentSignatureTranche extends GhidraScript {
    private static boolean isDryRun(String mode) {
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

    private Function getFunctionOrThrow(String addrText) throws Exception {
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String expectedSignature(String name, String callingConvention, DataType returnType, ParameterImpl... params) {
        StringBuilder sb = new StringBuilder();
        sb.append(returnType.getDisplayName()).append(" ").append(callingConvention).append(" ").append(name).append("(");
        for (int i = 0; i < params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(params[i].getDataType().getDisplayName()).append(" ").append(params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void applySignature(
            String addr,
            String expectedName,
            String callingConvention,
            DataType returnType,
            String comment,
            boolean dryRun,
            ParameterImpl... params) throws Exception {
        Function fn = getFunctionOrThrow(addr);
        if (!fn.getName().equals(expectedName)) {
            throw new IllegalStateException("Unexpected function name at " + addr + ": " + fn.getName() + " != " + expectedName);
        }

        if (dryRun) {
            println("DRY: " + addr + " " + expectedName + " -> " + expectedSignature(expectedName, callingConvention, returnType, params));
            return;
        }

        fn.setCallingConvention(callingConvention);
        fn.setReturnType(returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            params
        );
        fn.setComment(comment);
        println("OK: " + addr + " " + expectedName + " -> " + fn.getSignature().toString());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x00401000",
            "CGenericActiveReader__SetReader",
            "__thiscall",
            voidType,
            "Signature/comment hardening: rebinds this reader cell from its old target to readerCell, removes the old target through CSPtrSet__Remove when present, then registers the new target through CMonitor__AddDeletionEvent. Exact reader-cell layout, source identity, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("readerCell", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00401040",
            "CMonitor__AddDeletionEvent",
            "__thiscall",
            voidType,
            "Signature/comment hardening: ensures the deletion-event set at +0x4 exists via OID__AllocObject/CSPtrSet__Init, then adds readerCell with CSPtrSet__AddToHead. Exact monitor/event-set layout, source identity, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("readerCell", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004011b0",
            "vector_constructor_iterator_nothrow",
            "__stdcall",
            voidType,
            "Signature/comment hardening: CRT vector-constructor iterator walks count elements from base, advances by elemSize, performs a computed call to ctorFn for each element, and returns with ret 0x10. Exact caller object types, allocation semantics, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("base", voidPtr),
            param("elemSize", intType),
            param("count", intType),
            param("ctorFn", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004014c0",
            "CFrontEndPage__ActiveNotification_NoOp",
            "__thiscall",
            voidType,
            "Signature/comment hardening: frontend page active-notification no-op is a ret 0x4 thiscall-style vtable target with one stack argument fromPage. Exact frontend page owner/table coverage, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("fromPage", intType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00403650",
            "CMeshRenderer__CopyBasisAndRefreshTime",
            "__thiscall",
            voidType,
            "Signature/comment hardening: copies the four-word basis from srcBasis into this as destination and refreshes +0xac from DAT_00672fd0 unless the existing sentinel value is present. The old extra destination parameter was removed; exact renderer layout, source identity, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("srcBasis", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00403f40",
            "CResourceDescriptor__ctor",
            "__fastcall",
            voidType,
            "Signature/comment hardening: initializes the resource descriptor and zeros byte slots at +0x0/+0x100/+0x200/+0x300 plus descriptor fields including +0x400, +0x40c, +0x410, +0x414, and +0x418. Exact descriptor layout, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00403f80",
            "CResourceDescriptor__dtor",
            "__fastcall",
            voidType,
            "Signature/comment hardening: frees child descriptor objects referenced through +0x414/+0x418 with OID__FreeObject, clears released slots, then frees and clears the descriptor pointer array. Exact descriptor layout, ownership semantics, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004048f0",
            "CMesh__IsValidProfileIndex_1to10",
            "__cdecl",
            intType,
            "Signature/comment hardening: returns true only when profileIndex is in the inclusive 1..10 range; current xrefs are from CMesh__Load. Exact source identity, profile table semantics, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("profileIndex", intType));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
