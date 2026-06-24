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

public class ApplyWaypointWave538 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final String[] allowedExistingNames;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags,
                String[] allowedExistingNames) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.allowedExistingNames = allowedExistingNames;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "waypoint-wave538",
            "retail-binary-evidence",
            "signature-corrected",
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!allowedName(spec, fn.getName())) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        boolean update = needsUpdate(fn, spec);
        if (dryRun) {
            if (needsRename) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.wouldRename++;
            } else {
                println((update ? "DRY: " : "SKIP: ") + spec.address + " " + expectedSignature(spec));
            }
            stats.skipped++;
            return;
        }
        if (!update) {
            println("SKIP: " + spec.address + " already current");
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
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + functionAtEntry(spec.address).getSignature());
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
                "0x005057b0",
                "CWaypoint__InitAndLink",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave538 Waypoint signature/name/comment hardening: vtable 0x005dd2f0 slot 9 points here and RET 0x4 proves one stack argument after ECX this. The body marks init+0x70 as -1, delegates CThing__Init(this, init), links this into global waypoint list 0x00855120, samples the static-shadow heightfield against this+0x1c and lowers this+0x24 when needed, then binds the active reader at this+0x3c from init+0xa4. Static retail evidence only; exact source method name, concrete CWaypoint/init layouts, runtime pathing behavior, and rebuild parity remain unproven.",
                tags("waypoint", "vtable-readback", "renamed", "init", "list-link"),
                new String[] {"CWaypoint__VFunc_09_005057b0"}
            ),
            new Spec(
                "0x00505810",
                "CWaypoint__ShutdownAndUnlink",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave538 Waypoint signature/name/comment hardening: vtable 0x005dd2f0 slot 2 points here. The register-only body removes this from global waypoint list 0x00855120, then delegates CThing__Shutdown. Static retail evidence only; exact source method name, complete destructor/shutdown ownership, runtime pathing behavior, and rebuild parity remain unproven.",
                tags("waypoint", "vtable-readback", "renamed", "shutdown", "list-unlink"),
                new String[] {"CWaypoint__VFunc_02_00505810"}
            ),
            new Spec(
                "0x00505960",
                "CWaypoint__Load",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem_buffer", voidPtr),
                    param("load_mode", intType),
                    param("object_table", voidPtr)
                },
                "Wave538 Waypoint owner/signature correction: CWaypointManager__LoadWaypoints calls this with the newly allocated waypoint object in ECX and RET 0x0c proves three stack arguments. The body reads a byte name length from mem_buffer, allocates and null-terminates the waypoint name at this+0x04 using WaypointManager.cpp line 0x1a provenance, then either links a global waypoint-list entry selected by a 16-bit index or reads object_table indices and links flagged objects into this+0x08. Static retail evidence only; concrete CWaypoint/list/object-table layouts, exact source identity, runtime AI navigation behavior, and rebuild parity remain unproven.",
                tags("waypoint", "renamed", "load", "mem-buffer", "object-link"),
                new String[] {"CWaypointManager__LoadWaypoint"}
            ),
            new Spec(
                "0x00505ab0",
                "CWaypointManager__ReleasePendingObjects",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave538 WaypointManager signature/comment hardening: cdecl no-argument helper drains global pending-object set 0x00854fc0, mirrors the iterator into 0x00854fc8, removes each object with CSPtrSet__Remove, and invokes its vtable slot 0 with delete flag 1. Static retail evidence only; exact pending-set ownership, object type coverage, runtime shutdown behavior, and rebuild parity remain unproven.",
                tags("waypoint", "pending-set", "shutdown", "virtual-dispatch"),
                new String[] {}
            ),
            new Spec(
                "0x00505ae0",
                "CWaypointManager__LoadWaypoints",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("mem_buffer", voidPtr),
                    param("load_mode", intType),
                    param("object_table", voidPtr)
                },
                "Wave538 WaypointManager signature/comment hardening: cdecl caller-cleanup body reads a 16-bit waypoint count from mem_buffer, allocates 0x18-byte waypoint objects with WaypointManager.cpp line 0x72 provenance, initializes the embedded CSPtrSet at item+0x08, installs the 0x005dfc8c data/vtable-adjacent pointer, calls CWaypoint__Load with the allocated waypoint as ECX, appends it to global set 0x00854fc0, and reports Loading waypoints. Static retail evidence only; 0x005dfc8c table classification, concrete object layout, runtime navigation behavior, and rebuild parity remain unproven.",
                tags("waypoint", "load", "mem-buffer", "object-allocation", "status-message"),
                new String[] {}
            ),
            new Spec(
                "0x005d5860",
                "CWaypointManager__LoadWaypoints_unwind",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave538 WaypointManager unwind signature/comment hardening: SEH data xref from 0x0061e0cc and the LoadWaypoints handler setup identify the allocation cleanup thunk. The body reads the partially constructed waypoint pointer from EBP+0x0c and forwards it to OID__FreeObject_Callback with allocation tag 0x25, source path 0x0063d1f8, and line 0x72. Static retail evidence only; exception-path runtime behavior, allocator side effects, and rebuild parity remain unproven.",
                tags("waypoint", "seh-unwind", "allocation-cleanup"),
                new String[] {}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave538 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
