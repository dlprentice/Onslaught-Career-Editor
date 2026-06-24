//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtTypeInfoWave621 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] previousNames;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String[] previousNames,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.previousNames = previousNames;
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
            "crt-typeinfo-wave621",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
          .append(" ")
          .append(spec.callingConvention)
          .append(" ")
          .append(spec.name)
          .append("(");
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

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!fn.getSignature().toString().equals(expectedSignature(spec))) {
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
        String expectedSignature = expectedSignature(spec);
        if (!actualSignature.equals(expectedSignature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature);
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
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
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
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + fn.getSignature());
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055dac5",
                "type_info__dtor",
                new String[] {"type_info__ctor_like_0055dac5"},
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("typeInfo", voidPtr)},
                "Wave621 CRT/type_info hardening: type_info destructor-like body restores type_info::vftable, locks CRT index 0x1b, frees the cached name buffer at this+0x04 when non-null through CRT__FreeBase, unlocks, and returns. Static retail C++ runtime evidence only; exact compiler CRT version, concrete type_info layout beyond observed fields, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("type-info", "type-info-dtor", "crt-lock", "name-corrected")
            ),
            new Spec(
                "0x0055daee",
                "type_info__scalar_deleting_dtor",
                new String[] {"type_info__VFunc_00_0055daee"},
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("deleteFlags", uintType)},
                "Wave621 CRT/type_info hardening: type_info vtable slot 0 calls type_info__dtor, tests deleteFlags bit 0, frees the object through OID__FreeObject_Callback when requested, returns this, and ret 0x4 confirms one stack flag argument. Static scalar-deleting-destructor evidence only; exact compiler CRT version, allocator identity, runtime RTTI behavior, BEA patching, and rebuild parity remain unproven.",
                tags("type-info", "scalar-deleting-dtor", "vtable-slot", "name-corrected")
            ),
            new Spec(
                "0x0055db0a",
                "CRT__EhVectorDestructorIterator_WithUnwind",
                new String[] {"CDXLandscape__DestroyArrayWithCallback", "CDXLandscape__Helper_0055db0a", "CFastVB__Unk_0055db0a"},
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("array", voidPtr), param("elemSize", intType), param("count", intType), param("dtor", voidPtr)},
                "Wave621 CRT/type_info hardening: owner correction from CDXLandscape naming to a generic EH vector-destructor iterator wrapper. The body computes array + elemSize*count, walks elements in reverse, calls the element destructor callback through ECX, and invokes CRT__EhVectorDestructorIterator_IfNoException on the cleanup path. Xrefs span many resource/object cleanup sites, so this is generic runtime helper evidence only; exact MSVC helper name, element layouts, runtime unwind behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "eh-vector-destructor", "owner-correction", "name-corrected")
            ),
            new Spec(
                "0x0055dccd",
                "CRT__Acos",
                new String[] {},
                "__cdecl",
                doubleType,
                new ParameterImpl[] {param("lowWord", intType), param("highWord", uintType)},
                "Wave621 CRT/type_info hardening: acos-style floating-point helper checks FPU control-word state, handles domain/special-value paths, computes atan(sqrt((1-x)*(1+x)), x) for in-range values, and dispatches CRT math error/exit handling through DAT_009d08b4. Xref evidence reaches it from OID__AcosWrapper. Static retail math helper evidence only; exact CRT version, full IEEE edge-case parity, runtime math status behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "math-helper", "fpu-control", "callsite-verified")
            ),
            new Spec(
                "0x0055dda8",
                "CRT__CExit",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("exitCode", intType)},
                "Wave621 CRT/type_info hardening: compact cexit wrapper forwards exitCode to CRT__DoExit with both control flags cleared. Xrefs include entry and CFastVB__ParserContext_Shutdown. Static retail CRT exit-helper evidence only; exact CRT API identity, process-shutdown behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "exit-helper", "callsite-verified")
            ),
            new Spec(
                "0x0055ddca",
                "CRT__DoExit",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("exitCode", uintType), param("skipOnexitCallbacks", intType), param("returnToCaller", intType)},
                "Wave621 CRT/type_info hardening: shared exit path locks CRT lock 0x0d, terminates the current process if exit is already in progress, records shutdown state, optionally walks the onexit table, invokes function-pointer ranges at 0x00622b2c-0x00622b38 and 0x00622b3c-0x00622b44, then calls ExitProcess unless returnToCaller is set. Static retail CRT exit evidence only; exact CRT global names, runtime shutdown ordering, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "exit-helper", "onexit-table", "function-pointer-range")
            ),
            new Spec(
                "0x0055de81",
                "CRT__InvokeFunctionPointerRange",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("begin", voidPtr), param("end", voidPtr)},
                "Wave621 CRT/type_info hardening: iterates 4-byte function-pointer slots from begin to end and calls each non-null entry. Xrefs include CRT__DoExit and CFastVB__RunStaticInitRangesWithOptionalCallback. Static retail CRT helper evidence only; exact table ownership, callback prototypes, runtime initialization/shutdown ordering, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "function-pointer-range", "callsite-verified")
            ),
            new Spec(
                "0x0055df28",
                "CRT__OnexitTablePush",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("callback", intType)},
                "Wave621 CRT/type_info hardening: locked onexit-table append helper checks allocation size for DAT_009d4610/DAT_009d460c, grows the table by 0x10 bytes through CRT__ReallocBase when needed, appends callback, advances the write pointer, and returns zero on allocation failure. Static retail CRT onexit evidence only; exact CRT global names, callback prototype, allocator behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "onexit-table", "crt-lock", "allocator")
            ),
            new Spec(
                "0x0055dfa6",
                "CRT__RegisterOnexitFunction",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("callback", intType)},
                "Wave621 CRT/type_info hardening: thin registration wrapper calls CRT__OnexitTablePush and maps a non-zero table entry to success 0 or failure to -1. Xrefs include CLTShell__WinMain, CDXFrontEndVideo__Render, and static initialization sites. Static retail CRT onexit evidence only; exact CRT API identity, callback prototype, initialization ordering, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "onexit-table", "callsite-verified")
            ),
            new Spec(
                "0x0055dfe7",
                "CRT__RoundDoubleWithFpuChecks",
                new String[] {},
                "__cdecl",
                doubleType,
                new ParameterImpl[] {param("value", doubleType)},
                "Wave621 CRT/type_info hardening: rounded-double helper snapshots the FPU control word, classifies NaN/infinity inputs, uses FRNDINT for finite values, and routes domain/floating-point exception cases through CRT math handlers before returning a double. Xrefs span gameplay, renderer, UI, and grade calculations. Static retail math helper evidence only; exact CRT version, full IEEE rounding-mode parity, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "math-helper", "fpu-control", "callsite-verified")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun && (stats.bad != 0 || stats.missing != 0)) {
            throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
