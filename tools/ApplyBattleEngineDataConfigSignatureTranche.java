//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyBattleEngineDataConfigSignatureTranche extends GhidraScript {

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
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x0040f140",
            "BattleEngineConfigurations__ShutDown",
            "__cdecl",
            voidType,
            "Signature hardening for UBattleEngineConfigurations::ShutDown retail body. Evidence: no stack arguments, clears configuration count at 0x00660250, frees/zeroes the 20-slot sConfigurationName pointer array at 0x00660200, and is called by CWorld__ShutdownAndClear. Exact source identity beyond this source-aligned static body, tags, locals, runtime behavior, and rebuild parity remain unproven.",
            dryRun);
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040f180",
            "BattleEngineConfigurations__Load",
            "__cdecl",
            voidType,
            "Signature hardening for UBattleEngineConfigurations::Load(CMEMBUFFER&) retail body. CWorld__LoadWorldHeader pushes the memBuffer argument and caller-cleans it with ADD ESP,0x4; the body clears 0x00660250/0x00660200, logs the load, reads the count and length-prefixed strings through DXMemBuffer__ReadBytes, and stores allocated names. Exact structure types, tags, locals, runtime loading behavior, and rebuild parity remain unproven.",
            dryRun,
            param("memBuffer", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040f260",
            "BattleEngineConfigurations__Skip",
            "__cdecl",
            voidType,
            "Signature hardening for UBattleEngineConfigurations::Skip(CMEMBUFFER&) retail body. CWorld__LoadWorldHeader pushes the same memBuffer argument and caller-cleans it; the body reads the configuration count and length-prefixed strings through DXMemBuffer__ReadBytes, allocates temporary string buffers, then frees them without updating the global table. Exact structure types, tags, locals, runtime loading behavior, and rebuild parity remain unproven.",
            dryRun,
            param("memBuffer", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040f520",
            "CBattleEngineData__ctor",
            "__thiscall",
            voidPtr,
            "Signature hardening for CBattleEngineData constructor. Evidence: ECX is this, the body initializes embedded CSPtrSet members at +0x40/+0x50, clears owned string/store fields, installs structured exception cleanup, and returns this. Concrete CBattleEngineData layout, tags, locals, exact source identity beyond source-aligned constructor behavior, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040f590",
            "CBattleEngineData__Initialise",
            "__fastcall",
            voidType,
            "Signature hardening for CBattleEngineData::Initialise default-data setup. Evidence: ECX is battleEngineData; the body allocates/copies Standard, Vulcan Cannon 1, Pulse Cannon Pod, Missile Pod, Animated Explosion Emitter 2, and cockpit2.msh defaults, initializes store ranges, language, and stealth zero. Concrete layout, tags, locals, runtime profile behavior, and rebuild parity remain unproven.",
            dryRun,
            param("battleEngineData", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040f890",
            "CBattleEngineData__Shutdown",
            "__fastcall",
            voidType,
            "Signature hardening for CBattleEngineData::Shutdown cleanup. Evidence: ECX is battleEngineData; the body frees mConfigurationName, drains jet/walker weapon CSPtrSet nodes through CSPtrSet__Remove plus OID__FreeObject, and frees explosion/aug/primary/cockpit string pointers. Concrete layout, tags, locals, destructor completeness, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("battleEngineData", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040f980",
            "CBattleEngineData__LoadFromMemBuffer",
            "__thiscall",
            voidType,
            "Signature hardening for CBattleEngineData::Load(CMEMBUFFER&) retail body. Evidence: ECX is this, the caller pushes memBuffer, both function exits use RET 0x4, and the body calls CBattleEngineData__Shutdown before versioned DXMemBuffer__ReadBytes fields, weapon-list string loads, store/default fallback handling, and optional aug/primary/cockpit/language fields. Concrete layout, tags, locals, runtime profile behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("memBuffer", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
