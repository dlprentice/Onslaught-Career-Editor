//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyCliFlexArraySignatureCorrection extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
            this.parameters = parameters;
        }
    }

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
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.callingConvention).append(" ").append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            return false;
        }

        if (needsRename) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            spec.parameters
        );
        fn.setComment(spec.comment);
        println("OK: " + spec.address + " " + spec.name + " -> " + fn.getSignature().toString());
        return needsRename;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00423bc0", "CLIParams__ParseCommandLine", "__thiscall", voidType,
                "Signature/comment correction: CCLIParams-style command-line parser reached from CLTShell__WinMain. It takes the commandLine string in the lone stack argument, tokenizes into local 0x100-byte token slots, scans observed retail flags including -level/-res/-skipfmv/-nosound/-nomusic/-showdebugtrace/-traceconsole/-autoconfigtest, and keeps -forcewindowed guard-gated by DAT_00662f3e. Retail flag runtime behavior remains unproven here; exact CCLIParams layout, tags, locals, source-to-retail identity, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("commandLine", charPtr)}),
            new Spec("0x004241a0", "CFlexArray__InitWithGrowth", "__thiscall", voidPtr,
                "Signature/comment correction: CFlexArray InitWithGrowth wrapper; calls CFlexArray__Init(initialCapacity), clears count at +0x8, and stores growth at +0xc using positive scaling by DAT_005db5f8 or negative growth-1 adjustment. Runtime behavior remains unproven beyond static read-back; exact template owner types, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("initialCapacity", intType), param("growth", intType)}),
            new Spec("0x004241e0", "CFlexArray__Clear", "__fastcall", voidType,
                "Signature/comment correction: CFlexArray Clear helper; resets count at +0x8 to zero while leaving the data pointer and capacity intact. Runtime behavior remains unproven beyond static read-back; exact template owner types, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004241f0", "CFlexArray__Add", "__thiscall", voidPtr,
                "Signature/comment correction: CFlexArray Add helper for 4-byte element slots; grows according to +0xc when count reaches capacity, stores element at data[count], increments count, and returns this. Runtime behavior remains unproven beyond static read-back; exact element owner types, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("element", voidPtr)}),
            new Spec("0x00424260", "CFlexArray__InsertAt", "__thiscall", voidPtr,
                "Signature/comment correction: CFlexArray InsertAt helper for 4-byte element slots; grows when needed, appends directly when index equals count, otherwise shifts existing entries right before writing element and incrementing count. Runtime behavior remains unproven beyond static read-back; exact element owner types, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("index", intType), param("element", voidPtr)}),
            new Spec("0x00424360", "CFlexArray__RemoveRange", "__thiscall", voidType,
                "Signature/comment correction: CFlexArray RemoveRange helper; validates startIndex/endIndex, treats the end index as inclusive, truncates when removing through the tail, otherwise shifts later 4-byte entries left and adjusts count. Runtime behavior remains unproven beyond static read-back; exact element owner types, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("startIndex", intType), param("endIndex", intType)}),
            new Spec("0x00465530", "CFlexArray__Init", "__thiscall", voidPtr,
                "Signature/comment correction: CFlexArray Init helper backed by the flexarray.cpp debug string; defaults initialCapacity to 16, stores capacity at +0x4, allocates initialCapacity*4 bytes with MEMTYPE 0x12 and source line 0x22, stores the data pointer, and returns this. Runtime behavior remains unproven beyond static read-back; exact template owner types, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("initialCapacity", intType)}),
            new Spec("0x00465570", "CFlexArray__Free", "__fastcall", voidType,
                "Signature/comment correction: CFlexArray Free helper; frees the owned data pointer at +0x0 through the engine allocator and does not reset pointer, count, capacity, or growth fields in this body. Runtime behavior remains unproven beyond static read-back; exact ownership discipline, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00465580", "CFlexArray__Resize", "__thiscall", voidType,
                "Signature/comment correction: CFlexArray Resize helper; reallocates the data pointer to newCapacity*4 bytes, zero-fills newly added 4-byte slots when capacity grows, and stores newCapacity at +0x4. Runtime behavior remains unproven beyond static read-back; exact allocator semantics, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("newCapacity", uintType)}),
            new Spec("0x0044b290", "CFlexArray__Free_thunk", "__fastcall", voidType,
                "Signature/comment correction: exact jump thunk to CFlexArray__Free, kept as a distinct event-manager-adjacent entry because callers branch to 0x0044b290 directly. Runtime behavior remains unproven beyond static read-back; exact thunk provenance, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)})
        };

        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        for (Spec spec : specs) {
            boolean didRename = applySpec(spec, dryRun);
            if (dryRun) {
                skipped++;
            }
            else {
                updated++;
                if (didRename) {
                    renamed++;
                }
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " renamed=" + renamed + " missing=0 bad=0");
    }
}
