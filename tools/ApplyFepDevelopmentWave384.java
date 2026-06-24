//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFepDevelopmentWave384 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final String boundaryMoveFrom;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                String boundaryMoveFrom,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.boundaryMoveFrom = boundaryMoveFrom;
            this.createIfMissing = createIfMissing;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
        int boundaryMoved = 0;
        int wouldBoundaryMove = 0;
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        sb.append(")");
        return sb.toString();
    }

    private Function moveBoundaryIfNeeded(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function newFn = functionAtEntry(spec.address);
        if (newFn != null) {
            return newFn;
        }

        Function oldFn = functionAtEntry(spec.boundaryMoveFrom);
        if (oldFn == null) {
            throw new IllegalStateException("Boundary move requires old function at " + spec.boundaryMoveFrom);
        }
        if (!allowedName(spec, oldFn.getName())) {
            throw new IllegalStateException("Unexpected old boundary name at " + spec.boundaryMoveFrom + ": " + oldFn.getName());
        }

        if (dryRun) {
            println("DRY: would remove " + spec.boundaryMoveFrom + " " + oldFn.getName() + " and recreate at " + spec.address);
            stats.wouldBoundaryMove++;
            return oldFn;
        }

        FunctionManager fm = currentProgram.getFunctionManager();
        boolean removed = fm.removeFunction(addr(spec.boundaryMoveFrom));
        if (!removed) {
            throw new IllegalStateException("Failed to remove old function at " + spec.boundaryMoveFrom);
        }

        Address newEntry = addr(spec.address);
        disassemble(newEntry);
        newFn = createFunction(newEntry, null);
        if (newFn == null) {
            newFn = functionAtEntry(spec.address);
        }
        if (newFn == null) {
            throw new IllegalStateException("Function not present after create at " + spec.address);
        }
        newFn.setName(spec.name, SourceType.USER_DEFINED);
        stats.boundaryMoved++;
        println("OK: moved boundary " + spec.boundaryMoveFrom + " -> " + spec.address);
        return newFn;
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        if (spec.boundaryMoveFrom != null && !spec.boundaryMoveFrom.isEmpty()) {
            return moveBoundaryIfNeeded(spec, dryRun, stats);
        }

        Function fn = functionAtEntry(spec.address);
        if (fn != null) {
            return fn;
        }
        if (!spec.createIfMissing) {
            throw new IllegalStateException("Function not found at " + spec.address);
        }
        if (dryRun) {
            println("DRY: would create " + spec.address + " " + spec.name);
            stats.wouldCreate++;
            return null;
        }

        Address address = addr(spec.address);
        disassemble(address);
        fn = createFunction(address, null);
        if (fn == null) {
            fn = functionAtEntry(spec.address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        fn.setName(spec.name, SourceType.USER_DEFINED);
        stats.created++;
        println("OK: created " + spec.address + " " + spec.name);
        return fn;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getOrCreate(spec, dryRun, stats);
            if (fn == null) {
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
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

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (IllegalStateException ex) {
            if (ex.getMessage() != null && ex.getMessage().startsWith("Function not found")) {
                stats.missing++;
            } else {
                stats.bad++;
            }
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "fepdevelopment-wave384",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType charPtrPtr = new PointerDataType(new PointerDataType(CharDataType.dataType));

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00458050",
                "CFEPDevelopment__CompareWorldFileNamePtrs",
                "__cdecl",
                intType,
                "Wave384 boundary recovery: qsort comparator used by CFEPDevelopment__EnumerateWorldFiles. It receives two char** element pointers, compares the pointed-to ASCII filenames byte by byte, and returns strcmp-style ordering. Static retail evidence only; exact source body and runtime menu behavior remain unproven.",
                new String[] {},
                tags("fepdevelopment", "world-list", "sort-comparator", "function-boundary", "signature-hardened", "comment-hardened"),
                "",
                true,
                new ParameterImpl[] {param("left", charPtrPtr), param("right", charPtrPtr)}
            ),
            new Spec(
                "0x00458090",
                "CFEPDevelopment__EnumerateWorldFiles",
                "__fastcall",
                boolType,
                "Wave384 boundary correction: moved the saved boundary back from 0x00458100 to the true prologue at 0x00458090. The function clears CFEPDevelopment world-list fields, counts non-directory world files through FindFirstFileA/FindNextFileA, allocates the filename pointer array and 0x64-byte entries, copies filenames, closes the search handle, and sorts through CFEPDevelopment__CompareWorldFileNamePtrs. No source body is present in the Stuart source snapshot; reachability, dev-menu gating, runtime world-list behavior, and rebuild parity remain unproven.",
                new String[] {"CFEPDevelopment__EnumerateWorldFiles"},
                tags("fepdevelopment", "world-list", "function-boundary", "boundary-corrected", "signature-hardened", "comment-hardened"),
                "0x00458100",
                false,
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x004581e0",
                "CFEPDevelopment__Shutdown",
                "__fastcall",
                voidType,
                "Wave384 comment hardening: frees each allocated world-list filename entry through OID__FreeObject, frees the pointer array at this+0x04, then clears this+0x04 and this+0x08. Static retail evidence only; exact class layout, runtime shutdown behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepdevelopment", "world-list", "shutdown", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x004583c0",
                "CFEPDevelopment__RenderWorldListEntries",
                "__fastcall",
                voidType,
                "Wave384 comment hardening: iterates the world-list pointer array, converts each ASCII filename to a wide scratch string, draws entries through the platform font path, highlights the selected index at this+0x10, and wraps into a second column after 0x0f rows. Static retail evidence only; exact layout, source identity, visual runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepdevelopment", "world-list", "rendering", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x004584d0",
                "CFEPDevelopment__Render",
                "__thiscall",
                voidType,
                "Wave384 calling-convention correction: render is thiscall, not stdcall; ECX is the CFEPDevelopment object and the function retires the transition/dest stack pair with RET 0x8. It sets frontend/D3D render state flags and delegates visible world-list drawing to CFEPDevelopment__RenderWorldListEntries. Static retail evidence only; transition/dest semantics, source identity, visual runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepdevelopment", "rendering", "calling-convention-corrected", "signature-hardened", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr), param("transition", floatType), param("dest", intType)}
            ),
            new Spec(
                "0x00458710",
                "CFEPDevelopment__RefreshWorldListCore",
                "__fastcall",
                boolType,
                "Wave384 comment hardening: validates the selected storage-device state, branches on frontend save/load mode, queries storage info and save counts, opens save/delete dialogs or frontend pages, and returns a boolean-like handled result. Static retail evidence only; exact dialog semantics, runtime storage-device behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepdevelopment", "storage-device", "save-list", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x004589f0",
                "CFEPDevelopment__RefreshWorldList",
                "__fastcall",
                voidType,
                "Wave384 comment hardening: wrapper that pushes a zero refresh argument to CFEPDevelopment__ResolveActiveStorageDevice, then calls CFEPDevelopment__RefreshWorldListCore. Static retail evidence only; caller page-action semantics, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepdevelopment", "storage-device", "save-list", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00458ce0",
                "CFEPDevelopment__ResolveActiveStorageDevice",
                "__thiscall",
                voidType,
                "Wave384 calling-convention correction: this helper is thiscall with one stack argument and RET 0x4, not fastcall; all observed callsites push 0 and the current body does not read that caller argument. The function resolves/updates storage-device fields at this+0x08/+0x0c/+0x10, sets this+0x14 when HUD/dialog state is active, and clears the global dialog/message gate for selected frontend pages. Static retail evidence only; exact unused argument semantics, source identity, runtime storage behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepdevelopment", "storage-device", "calling-convention-corrected", "signature-hardened", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr), param("unused_refresh_arg", intType)}
            ),
            new Spec(
                "0x00459580",
                "CFEPDevelopment__ScheduleWorldListRefresh",
                "__thiscall",
                voidType,
                "Wave384 calling-convention correction: this vtable-referenced helper is thiscall with one ignored stack argument and RET 0x4, not fastcall. It pushes zero to CFEPDevelopment__ResolveActiveStorageDevice, then writes this+0x04 to the current platform time plus the 0x005d8ba0 delay constant. Static retail evidence only; vtable slot semantics, runtime timer behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepdevelopment", "storage-device", "timer", "calling-convention-corrected", "signature-hardened", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr), param("ignored_arg", intType)}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " boundary_moved=" + stats.boundaryMoved +
            " would_boundary_move=" + stats.wouldBoundaryMove +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave384 FEPDevelopment apply had failures");
        }
    }
}
